# tests/test_core_logic.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the core functions
from julie_julie_app import handle_time_command, handle_weather_command, process_command_from_user

class TestTimeHandler(unittest.TestCase):
    """Test time-related functionality."""
    
    def test_time_command_structure(self):
        """Test that time command returns proper structure."""
        result = handle_time_command()
        
        # Check that result has the expected structure
        self.assertIsInstance(result, dict)
        self.assertIn("spoken_response", result)
        self.assertIn("opened_url", result)
        self.assertIn("additional_context", result)
        
        # Check that spoken_response contains time information
        self.assertIsInstance(result["spoken_response"], str)
        self.assertIn("time", result["spoken_response"].lower())
        
        # opened_url should be None for time commands
        self.assertIsNone(result["opened_url"])
    
    def test_time_command_format(self):
        """Test that time is formatted correctly."""
        result = handle_time_command()
        spoken_response = result["spoken_response"]
        
        # Should contain "AM" or "PM"
        self.assertTrue("AM" in spoken_response or "PM" in spoken_response)
        
        # Should contain "current time"
        self.assertIn("current time", spoken_response.lower())

class TestWeatherHandler(unittest.TestCase):
    """Test weather functionality."""
    
    @patch('requests.get')
    def test_weather_with_valid_response(self, mock_get):
        """Test weather handler with mocked valid API responses."""
        # Mock the geocoding response
        mock_geo_response = MagicMock()
        mock_geo_response.status_code = 200
        mock_geo_response.json.return_value = [{
            'lat': '39.0997',
            'lon': '-94.5786',
            'display_name': 'Kansas City, Jackson County, Missouri, United States'
        }]
        
        # Mock the NWS points response
        mock_nws_response = MagicMock()
        mock_nws_response.status_code = 200
        mock_nws_response.json.return_value = {
            'properties': {
                'forecast': 'https://api.weather.gov/gridpoints/EAX/34,70/forecast'
            }
        }
        
        # Mock the forecast response
        mock_forecast_response = MagicMock()
        mock_forecast_response.status_code = 200
        mock_forecast_response.json.return_value = {
            'properties': {
                'periods': [{
                    'temperature': 75,
                    'temperatureUnit': 'F',
                    'shortForecast': 'Sunny',
                    'detailedForecast': 'Sunny with clear skies'
                }]
            }
        }
        
        # Configure the mock to return different responses for different URLs
        def mock_get_side_effect(url, **kwargs):
            if 'nominatim.openstreetmap.org' in url:
                return mock_geo_response
            elif 'api.weather.gov/points' in url:
                return mock_nws_response
            elif 'forecast' in url:
                return mock_forecast_response
            return MagicMock(status_code=404)
        
        mock_get.side_effect = mock_get_side_effect
        
        result = handle_weather_command("Kansas City")
        
        self.assertIsNotNone(result)
        self.assertIn("spoken_response", result)
        self.assertIn("75", result["spoken_response"])
        self.assertIn("Sunny", result["spoken_response"])
    
    @patch('requests.get')
    def test_weather_with_api_failure(self, mock_get):
        """Test weather handler when API calls fail."""
        mock_get.side_effect = Exception("Network error")
        
        result = handle_weather_command("Invalid Location")
        
        self.assertIsNotNone(result)
        self.assertIn("spoken_response", result)
        self.assertIn("couldn't", result["spoken_response"].lower())
    
    def test_weather_default_location(self):
        """Test weather handler with no location specified."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")  # Force failure for testing
            
            result = handle_weather_command()  # No location specified
            
            self.assertIsNotNone(result)
            self.assertIn("spoken_response", result)

class TestCommandProcessing(unittest.TestCase):
    """Test the main command processing logic."""
    
    @patch('subprocess.run')  # Mock the 'say' command
    def test_time_command_processing(self, mock_subprocess):
        """Test that time commands are processed correctly."""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        result = process_command_from_user("what time is it")
        
        self.assertIsNotNone(result)
        self.assertIn("spoken_response", result)
        self.assertIn("time", result["spoken_response"].lower())
        
        # Verify that the 'say' command was called
        mock_subprocess.assert_called()
    
    @patch('subprocess.run')
    def test_empty_command(self, mock_subprocess):
        """Test handling of empty commands."""
        result = process_command_from_user("")
        
        self.assertIsNotNone(result)
        self.assertIn("didn't receive", result["spoken_response"])
    
    @patch('subprocess.run')
    def test_none_command(self, mock_subprocess):
        """Test handling of None commands."""
        result = process_command_from_user(None)
        
        self.assertIsNotNone(result)
        self.assertIn("didn't receive", result["spoken_response"])
    
    @patch('subprocess.run')
    @patch('julie_julie_app.handle_ollama_query')
    def test_fallback_to_ollama(self, mock_ollama, mock_subprocess):
        """Test that unrecognized commands fall back to Ollama."""
        mock_ollama.return_value = {
            "spoken_response": "I understand you're asking about something.",
            "opened_url": None,
            "additional_context": "Processed by Ollama"
        }
        
        result = process_command_from_user("tell me a random fact")
        
        self.assertIsNotNone(result)
        mock_ollama.assert_called_once()

if __name__ == '__main__':
    unittest.main()
