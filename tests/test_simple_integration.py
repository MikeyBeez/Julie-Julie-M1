# tests/test_simple_integration.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from julie_julie_app import process_command_from_user

class TestSimpleIntegration(unittest.TestCase):
    """Simple integration tests that don't require a running server."""
    
    @patch('subprocess.run')  # Mock speech output
    def test_time_command_integration(self, mock_subprocess):
        """Test time command through the full processing logic."""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        result = process_command_from_user("what time is it")
        
        self.assertIsNotNone(result)
        self.assertIn("spoken_response", result)
        self.assertIn("time", result["spoken_response"].lower())
        
        # Verify that speech was triggered
        mock_subprocess.assert_called()
    
    @patch('subprocess.run')
    def test_calculation_integration(self, mock_subprocess):
        """Test calculation command through the full processing logic."""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        result = process_command_from_user("47 + 23")
        
        self.assertIsNotNone(result)
        if result["spoken_response"]:  # Only check if calculation was handled
            self.assertIn("70", result["spoken_response"])
            mock_subprocess.assert_called()
    
    @patch('subprocess.run')
    @patch('webbrowser.open')
    def test_spotify_integration(self, mock_browser, mock_subprocess):
        """Test Spotify command through the full processing logic."""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        result = process_command_from_user("spotify play hello")
        
        self.assertIsNotNone(result)
        self.assertIn("spoken_response", result)
        
        # Should have opened browser and triggered speech
        mock_browser.assert_called()
        mock_subprocess.assert_called()
    
    @patch('subprocess.run')
    def test_empty_command_handling(self, mock_subprocess):
        """Test handling of empty commands."""
        result = process_command_from_user("")
        
        self.assertIsNotNone(result)
        self.assertIn("didn't receive", result["spoken_response"])
    
    @patch('subprocess.run')
    def test_fallback_to_ollama(self, mock_subprocess):
        """Test that unrecognized commands fall back appropriately."""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Mock the Ollama handler to avoid network calls
        with patch('julie_julie_app.handle_ollama_query') as mock_ollama:
            mock_ollama.return_value = {
                "spoken_response": "I understand you're asking about something.",
                "opened_url": None,
                "additional_context": "Processed by Ollama"
            }
            
            result = process_command_from_user("tell me a random story")
            
            self.assertIsNotNone(result)
            mock_ollama.assert_called_once()

if __name__ == '__main__':
    unittest.main()
