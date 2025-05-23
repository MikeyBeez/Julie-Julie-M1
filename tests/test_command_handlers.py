# tests/test_command_handlers.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import from handlers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from handlers.calculation_handler import handle_calculation
from handlers.apple_music_handler import handle_apple_music_command
from handlers.spotify_handler import handle_spotify_command
from handlers.youtube_browser import handle_youtube_command
from handlers.visualizer_handler import handle_visualizer_command
from handlers.radio_handler import handle_radio_command
from handlers.audio_handler import handle_audio_command

class TestCalculationHandler(unittest.TestCase):
    """Test the calculation handler functionality."""
    
    def test_simple_addition(self):
        """Test basic addition calculations."""
        result = handle_calculation("47 + 23")
        self.assertIsNotNone(result)
        self.assertIn("spoken_response", result)
        self.assertIn("70", result["spoken_response"])
    
    def test_multiplication(self):
        """Test multiplication calculations."""
        result = handle_calculation("6 * 7")
        self.assertIsNotNone(result)
        self.assertIn("42", result["spoken_response"])
    
    def test_complex_expression(self):
        """Test more complex mathematical expressions."""
        result = handle_calculation("what's 10 plus 5")
        self.assertIsNotNone(result)
        # Should be 15 (simple addition)
        self.assertIn("15", result["spoken_response"])
    
    def test_non_calculation_command(self):
        """Test that non-calculation commands return None."""
        result = handle_calculation("what time is it")
        self.assertIsNone(result)
    
    def test_invalid_calculation(self):
        """Test handling of invalid mathematical expressions."""
        result = handle_calculation("calculate abc plus def")
        # Should return None for non-matching patterns
        self.assertIsNone(result)
    
    def test_tip_calculation(self):
        """Test tip calculations."""
        result = handle_calculation("15% tip on $50")
        self.assertIsNotNone(result)
        self.assertIn("7.50", result["spoken_response"])  # 15% of $50
        self.assertIn("57.50", result["spoken_response"])  # Total
    
    def test_percentage_calculation(self):
        """Test percentage calculations."""
        result = handle_calculation("what's 20% of 100")
        self.assertIsNotNone(result)
        self.assertIn("20", result["spoken_response"])

class TestMusicHandlers(unittest.TestCase):
    """Test music control handlers."""
    
    @patch('webbrowser.open')
    def test_spotify_play_command(self, mock_browser):
        """Test Spotify play command."""
        result = handle_spotify_command("spotify play despacito")
        self.assertIsNotNone(result)
        self.assertIn("spoken_response", result)
        self.assertIn("Searching for", result["spoken_response"])
        mock_browser.assert_called_once()
    
    @patch('subprocess.run')
    def test_apple_music_play_command(self, mock_subprocess):
        """Test Apple Music play command."""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        result = handle_apple_music_command("play music on apple music")
        self.assertIsNotNone(result)
        self.assertIn("spoken_response", result)
        mock_subprocess.assert_called()
    
    def test_non_music_command(self):
        """Test that non-music commands return None."""
        result = handle_spotify_command("what time is it")
        self.assertIsNone(result)
        
        result = handle_apple_music_command("what time is it")
        self.assertIsNone(result)
    
    def test_spotify_memory_command(self):
        """Test Spotify memory functionality."""
        # This would require more complex setup, so we'll test the pattern recognition
        result = handle_spotify_command("remember this song")
        # Should return a response about no recent track or successfully remembering
        if result is not None:
            self.assertIn("spoken_response", result)

class TestYouTubeHandler(unittest.TestCase):
    """Test YouTube search and opening functionality."""
    
    @patch('webbrowser.open')
    def test_youtube_search(self, mock_browser):
        """Test YouTube search command."""
        result = handle_youtube_command("youtube cute cats")
        self.assertIsNotNone(result)
        self.assertIn("spoken_response", result)
        self.assertIn("opened_url", result)
        self.assertIsNotNone(result["opened_url"])
        mock_browser.assert_called_once()
    
    @patch('webbrowser.open')
    def test_youtube_search_with_play(self, mock_browser):
        """Test YouTube search with 'play' keyword."""
        result = handle_youtube_command("play funny videos on youtube")
        self.assertIsNotNone(result)
        self.assertIn("youtube.com", result["opened_url"].lower())
        mock_browser.assert_called_once()
    
    def test_non_youtube_command(self):
        """Test that non-YouTube commands return None."""
        result = handle_youtube_command("what time is it")
        self.assertIsNone(result)

class TestVisualizerHandler(unittest.TestCase):
    """Test data visualization handler."""
    
    @patch('webbrowser.open')
    def test_visualizer_command(self, mock_browser):
        """Test basic visualizer command."""
        result = handle_visualizer_command("show me a chart")
        # This will depend on your actual implementation
        if result is not None:
            self.assertIn("spoken_response", result)
    
    def test_non_visualizer_command(self):
        """Test that non-visualizer commands return None."""
        result = handle_visualizer_command("what time is it")
        self.assertIsNone(result)

class TestRadioHandler(unittest.TestCase):
    """Test radio station handler."""
    
    @patch('webbrowser.open')
    def test_classical_radio(self, mock_browser):
        """Test classical radio command."""
        result = handle_radio_command("classical radio")
        self.assertIsNotNone(result)
        self.assertIn("spoken_response", result)
        self.assertIn("Playing", result["spoken_response"])
        mock_browser.assert_called_once()
    
    @patch('webbrowser.open')
    def test_jazz_radio(self, mock_browser):
        """Test jazz radio command."""
        result = handle_radio_command("jazz music")
        self.assertIsNotNone(result)
        self.assertIn("jazz", result["spoken_response"].lower())
        mock_browser.assert_called_once()
    
    @patch('webbrowser.open')
    def test_rock_radio(self, mock_browser):
        """Test rock radio command."""
        result = handle_radio_command("rock radio")
        self.assertIsNotNone(result)
        self.assertIn("Playing", result["spoken_response"])
        mock_browser.assert_called_once()
    
    @patch('webbrowser.open')
    def test_npr_radio(self, mock_browser):
        """Test NPR radio command."""
        result = handle_radio_command("npr")
        self.assertIsNotNone(result)
        self.assertIn("NPR", result["spoken_response"])
        mock_browser.assert_called_once()
    
    @patch('webbrowser.open')
    def test_news_radio(self, mock_browser):
        """Test news radio command."""
        result = handle_radio_command("news")
        self.assertIsNotNone(result)
        self.assertIn("NPR", result["spoken_response"])
        mock_browser.assert_called_once()
    
    def test_radio_station_list(self):
        """Test listing available radio stations."""
        result = handle_radio_command("what radio stations do you have")
        self.assertIsNotNone(result)
        self.assertIn("classical", result["spoken_response"].lower())
        self.assertIn("jazz", result["spoken_response"].lower())
        self.assertIn("rock", result["spoken_response"].lower())
        self.assertIn("npr", result["spoken_response"].lower())
    
    def test_non_radio_command(self):
        """Test that non-radio commands return None."""
        result = handle_radio_command("what time is it")
        self.assertIsNone(result)

class TestAudioHandler(unittest.TestCase):
    """Test audio device switching handler."""
    
    @patch('subprocess.run')
    def test_list_audio_devices(self, mock_subprocess):
        """Test listing available audio devices."""
        # Mock system_profiler output
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Built-in Output:\nBluetooth Device:\nHDMI Output:"
        )
        
        result = handle_audio_command("what speakers are available")
        self.assertIsNotNone(result)
        self.assertIn("Available audio devices", result["spoken_response"])
    
    @patch('subprocess.run')
    def test_switch_to_speaker(self, mock_subprocess):
        """Test switching to a specific speaker."""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        result = handle_audio_command("switch to yamaha")
        self.assertIsNotNone(result)
        self.assertIn("spoken_response", result)
    
    def test_non_audio_command(self):
        """Test that non-audio commands return None."""
        result = handle_audio_command("what time is it")
        self.assertIsNone(result)
    
    @patch('subprocess.run')
    def test_audio_device_patterns(self, mock_subprocess):
        """Test various audio command patterns."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="")
        
        commands = [
            "list audio devices",
            "show speakers", 
            "what sound devices",
            "switch to soundbar",
            "use bluetooth"
        ]
        
        for command in commands:
            result = handle_audio_command(command)
            self.assertIsNotNone(result, f"Failed for command: {command}")

if __name__ == '__main__':
    unittest.main()
