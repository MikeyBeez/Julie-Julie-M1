# tests/test_flask_api.py
import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from julie_julie_app import flask_app

class TestFlaskAPI(unittest.TestCase):
    """Test the Flask API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        self.app = flask_app.test_client()
        self.app.testing = True
    
    def test_home_endpoint(self):
        """Test the home endpoint returns status information."""
        response = self.app.get('/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn("status", data)
        self.assertIn("app", data)
        self.assertIn("version", data)
        self.assertEqual(data["status"], "online")
        self.assertEqual(data["app"], "Julie Julie")
    
    @patch('julie_julie_app.process_command_from_user')
    def test_command_endpoint_with_json(self, mock_process):
        """Test the command endpoint with JSON data."""
        mock_process.return_value = {
            "spoken_response": "Test response",
            "opened_url": None,
            "additional_context": None
        }
        
        response = self.app.post('/command',
                                json={"text_command": "what time is it"},
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("details", data)
        
        mock_process.assert_called_once_with("what time is it")
    
    @patch('julie_julie_app.process_command_from_user')
    def test_command_endpoint_with_form_data(self, mock_process):
        """Test the command endpoint with form data."""
        mock_process.return_value = {
            "spoken_response": "Test response",
            "opened_url": None,
            "additional_context": None
        }
        
        response = self.app.post('/command',
                                data={"text_command": "what time is it"})
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        
        mock_process.assert_called_once_with("what time is it")
    
    def test_command_endpoint_without_command(self):
        """Test the command endpoint without a text_command parameter."""
        response = self.app.post('/command', json={})
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertIn("No text_command provided", data["message"])
    
    @patch('julie_julie_app.process_command_from_user')
    def test_command_endpoint_with_exception(self, mock_process):
        """Test the command endpoint when processing raises an exception."""
        mock_process.side_effect = Exception("Test error")
        
        response = self.app.post('/command',
                                json={"text_command": "test command"})
        
        self.assertEqual(response.status_code, 500)
        
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertIn("Test error", data["message"])

if __name__ == '__main__':
    unittest.main()
