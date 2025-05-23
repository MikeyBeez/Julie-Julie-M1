# tests/test_integration.py
import unittest
from unittest.mock import patch, MagicMock
import requests
import time
import threading
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from julie_julie_app import run_flask_server

class TestIntegration(unittest.TestCase):
    """Integration tests that test the full application flow."""
    
    @classmethod
    def setUpClass(cls):
        """Start the Flask server in a separate thread for integration testing."""
        cls.server_thread = threading.Thread(target=run_flask_server, daemon=True)
        cls.server_thread.start()
        time.sleep(2)  # Give the server time to start
        cls.base_url = "http://127.0.0.1:58586"
    
    def test_server_is_running(self):
        """Test that the server is accessible."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["status"], "online")
        except requests.exceptions.RequestException as e:
            self.fail(f"Server is not running: {e}")
    
    @patch('subprocess.run')  # Mock the 'say' command to avoid actual speech
    def test_full_command_flow(self, mock_subprocess):
        """Test the complete flow from HTTP request to response."""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        try:
            response = requests.post(
                f"{self.base_url}/command",
                data={"text_command": "what time is it"},
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["status"], "success")
            self.assertIn("details", data)
            self.assertIn("spoken_response", data["details"])
            self.assertIn("time", data["details"]["spoken_response"].lower())
            
            # Verify that speech was triggered
            mock_subprocess.assert_called()
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Integration test failed: {e}")
    
    @patch('subprocess.run')
    def test_calculation_integration(self, mock_subprocess):
        """Test calculation command through the full stack."""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        try:
            response = requests.post(
                f"{self.base_url}/command",
                json={"text_command": "what is 5 plus 3"},
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["status"], "success")
            
            # Check that the calculation was performed
            spoken_response = data["details"]["spoken_response"]
            self.assertIn("8", spoken_response)
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Calculation integration test failed: {e}")
    
    def test_invalid_command_handling(self):
        """Test how the system handles invalid or malformed requests."""
        try:
            # Test with missing command
            response = requests.post(
                f"{self.base_url}/command",
                json={},
                timeout=5
            )
            
            self.assertEqual(response.status_code, 400)
            
            data = response.json()
            self.assertEqual(data["status"], "error")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Invalid command test failed: {e}")

class TestCommandRecognition(unittest.TestCase):
    """Test that different command variations are recognized correctly."""
    
    def setUp(self):
        """Import the command processing function."""
        from julie_julie_app import process_command_from_user
        self.process_command = process_command_from_user
    
    @patch('subprocess.run')  # Mock speech to avoid actual audio output
    def test_time_command_variations(self, mock_subprocess):
        """Test various ways of asking for time."""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        time_variations = [
            "what time is it",
            "What's the time?",
            "tell me the time",
            "current time",
            "what's the clock say"
        ]
        
        for command in time_variations:
            with self.subTest(command=command):
                result = self.process_command(command)
                self.assertIsNotNone(result)
                self.assertIn("spoken_response", result)
                self.assertIn("time", result["spoken_response"].lower())
    
    @patch('subprocess.run')
    def test_calculation_variations(self, mock_subprocess):
        """Test various ways of asking for calculations."""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        calc_variations = [
            "what is 2 plus 2",
            "calculate 5 times 3",
            "2 + 2",
            "5 * 3",
            "what's 10 minus 4"
        ]
        
        for command in calc_variations:
            with self.subTest(command=command):
                result = self.process_command(command)
                if result is not None:  # Some variations might not be recognized
                    self.assertIn("spoken_response", result)

if __name__ == '__main__':
    unittest.main()
