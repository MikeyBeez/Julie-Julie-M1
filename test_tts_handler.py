"""
Unit tests for TTS handler.
Tests Google TTS, say fallback, command handling, and error conditions.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
import json
import subprocess

# Import the handler
import sys
sys.path.append('/Users/bard/Code/Julie-Julie-M1')
from handlers.tts_handler import TTSManager, speak_text, set_tts_preference, get_tts_status, handle_tts_command

class TestTTSManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.tts_manager = TTSManager()
    
    def test_init_without_credentials(self):
        """Test TTSManager initialization without Google credentials."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 1  # gcloud auth fails
                
                manager = TTSManager()
                self.assertFalse(manager.google_available)
                self.assertTrue(manager.use_google_tts)  # Default preference
                self.assertEqual(manager.fallback_count, 0)
    
    def test_init_with_env_credentials(self):
        """Test TTSManager initialization with environment credentials."""
        fake_creds_path = '/fake/path/to/creds.json'
        with patch.dict(os.environ, {'GOOGLE_APPLICATION_CREDENTIALS': fake_creds_path}):
            with patch('os.path.exists', return_value=True):
                manager = TTSManager()
                self.assertTrue(manager.google_available)
    
    def test_init_with_gcloud_credentials(self):
        """Test TTSManager initialization with gcloud credentials."""
        with patch.dict(os.environ, {}, clear=True):
            mock_accounts = [{"account": "test@example.com", "status": "ACTIVE"}]
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = json.dumps(mock_accounts)
                
                manager = TTSManager()
                self.assertTrue(manager.google_available)
    
    @patch('subprocess.run')
    def test_say_fallback_success(self, mock_run):
        """Test successful say command fallback."""
        mock_run.return_value = None  # say command succeeds
        
        result = self.tts_manager._say_fallback("Hello world")
        self.assertTrue(result)
        mock_run.assert_called_once_with(['say', '-v', 'Alex', 'Hello world'], check=True)
    
    @patch('subprocess.run')
    def test_say_fallback_failure(self, mock_run):
        """Test say command failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'say')
        
        result = self.tts_manager._say_fallback("Hello world")
        self.assertFalse(result)
    
    @patch('handlers.tts_handler.texttospeech')
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_google_tts_success(self, mock_unlink, mock_tempfile, mock_subprocess, mock_tts):
        """Test successful Google TTS."""
        # Mock the Google TTS client and response
        mock_client = MagicMock()
        mock_tts.TextToSpeechClient.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.audio_content = b'fake audio data'
        mock_client.synthesize_speech.return_value = mock_response
        
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = '/tmp/fake_audio.mp3'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        # Mock afplay
        mock_subprocess.return_value = None
        
        result = self.tts_manager._google_tts("Hello world")
        self.assertTrue(result)
        
        # Verify calls
        mock_client.synthesize_speech.assert_called_once()
        mock_subprocess.assert_called_once_with(['afplay', '/tmp/fake_audio.mp3'], check=True)
        mock_unlink.assert_called_once_with('/tmp/fake_audio.mp3')
    
    def test_google_tts_import_error(self):
        """Test Google TTS when library is not installed."""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'google.cloud'")):
            result = self.tts_manager._google_tts("Hello world")
            self.assertFalse(result)
    
    @patch.object(TTSManager, '_google_tts')
    @patch.object(TTSManager, '_say_fallback')
    def test_speak_google_success(self, mock_say, mock_google):
        """Test speak method with successful Google TTS."""
        self.tts_manager.google_available = True
        self.tts_manager.use_google_tts = True
        mock_google.return_value = True
        
        result = self.tts_manager.speak("Hello world")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["method"], "google_tts")
        mock_google.assert_called_once_with("Hello world")
        mock_say.assert_not_called()
    
    @patch.object(TTSManager, '_google_tts')
    @patch.object(TTSManager, '_say_fallback')
    def test_speak_google_failure_fallback(self, mock_say, mock_google):
        """Test speak method falling back to say when Google fails."""
        self.tts_manager.google_available = True
        self.tts_manager.use_google_tts = True
        mock_google.return_value = False
        mock_say.return_value = True
        
        result = self.tts_manager.speak("Hello world")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["method"], "say_fallback")
        self.assertEqual(result["fallback_count"], 1)
        mock_google.assert_called_once()
        mock_say.assert_called_once()
    
    @patch.object(TTSManager, '_say_fallback')
    def test_speak_force_fallback(self, mock_say):
        """Test speak method with forced fallback."""
        mock_say.return_value = True
        
        result = self.tts_manager.speak("Hello world", force_fallback=True)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["method"], "say_direct")
        mock_say.assert_called_once_with("Hello world")
    
    @patch.object(TTSManager, '_google_tts')
    @patch.object(TTSManager, '_say_fallback')
    def test_speak_both_fail(self, mock_say, mock_google):
        """Test speak method when both TTS methods fail."""
        self.tts_manager.google_available = True
        self.tts_manager.use_google_tts = True
        mock_google.return_value = False
        mock_say.return_value = False
        
        result = self.tts_manager.speak("Hello world")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["method"], "none")
        self.assertIn("Both TTS methods failed", result["error"])
    
    def test_speak_empty_text(self):
        """Test speak method with empty text."""
        result = self.tts_manager.speak("")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["method"], "none")
        self.assertIn("No text provided", result["error"])
    
    def test_set_google_preference(self):
        """Test setting Google TTS preference."""
        self.tts_manager.set_google_preference(False)
        self.assertFalse(self.tts_manager.use_google_tts)
        
        self.tts_manager.set_google_preference(True)
        self.assertTrue(self.tts_manager.use_google_tts)
    
    def test_get_status(self):
        """Test getting TTS manager status."""
        self.tts_manager.google_available = True
        self.tts_manager.use_google_tts = False
        self.tts_manager.fallback_count = 3
        
        status = self.tts_manager.get_status()
        
        self.assertTrue(status["google_available"])
        self.assertFalse(status["google_preferred"])
        self.assertEqual(status["fallback_count"], 3)

class TestTTSCommands(unittest.TestCase):
    """Test TTS command handling."""
    
    @patch('handlers.tts_handler.set_tts_preference')
    def test_use_google_voice_command(self, mock_set_pref):
        """Test 'use google voice' command."""
        result = handle_tts_command("Use google voice")
        
        self.assertIsNotNone(result)
        self.assertIn("Google text to speech", result["spoken_response"])
        mock_set_pref.assert_called_once_with(True)
    
    @patch('handlers.tts_handler.set_tts_preference')
    def test_use_local_voice_command(self, mock_set_pref):
        """Test 'use local voice' command."""
        result = handle_tts_command("switch to say")
        
        self.assertIsNotNone(result)
        self.assertIn("local say command", result["spoken_response"])
        mock_set_pref.assert_called_once_with(False)
    
    @patch('handlers.tts_handler.get_tts_status')
    def test_tts_status_command(self, mock_status):
        """Test TTS status command."""
        mock_status.return_value = {
            "google_available": True,
            "google_preferred": True,
            "fallback_count": 2
        }
        
        result = handle_tts_command("tts status")
        
        self.assertIsNotNone(result)
        self.assertIn("Google text to speech", result["spoken_response"])
        self.assertIn("2 times", result["spoken_response"])
    
    @patch('handlers.tts_handler.speak_text')
    def test_voice_test_command(self, mock_speak):
        """Test voice test command."""
        mock_speak.return_value = {"success": True, "method": "google_tts"}
        
        result = handle_tts_command("test voice")
        
        self.assertIsNotNone(result)
        self.assertIn("Voice test completed", result["spoken_response"])
        mock_speak.assert_called_once_with("This is a test of the text to speech system.")
    
    def test_unrecognized_command(self):
        """Test unrecognized command returns None."""
        result = handle_tts_command("random unrelated command")
        self.assertIsNone(result)

class TestConvenienceFunctions(unittest.TestCase):
    """Test module-level convenience functions."""
    
    @patch('handlers.tts_handler.tts_manager')
    def test_speak_text(self, mock_manager):
        """Test speak_text convenience function."""
        mock_manager.speak.return_value = {"success": True}
        
        result = speak_text("Hello")
        
        self.assertEqual(result, {"success": True})
        mock_manager.speak.assert_called_once_with("Hello", False)
    
    @patch('handlers.tts_handler.tts_manager')
    def test_set_tts_preference(self, mock_manager):
        """Test set_tts_preference convenience function."""
        set_tts_preference(False)
        mock_manager.set_google_preference.assert_called_once_with(False)
    
    @patch('handlers.tts_handler.tts_manager')
    def test_get_tts_status(self, mock_manager):
        """Test get_tts_status convenience function."""
        mock_manager.get_status.return_value = {"test": "data"}
        
        result = get_tts_status()
        
        self.assertEqual(result, {"test": "data"})
        mock_manager.get_status.assert_called_once()

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
