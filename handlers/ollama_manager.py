"""
Ollama service manager for Julie Julie.
Handles starting, stopping, and monitoring the Ollama service.
"""

import subprocess
import logging
import time
import requests
import threading
import os
from typing import Dict, Any, Optional

logger = logging.getLogger('julie_julie')

class OllamaManager:
    """Manages the Ollama service lifecycle."""
    
    def __init__(self):
        self.ollama_process = None
        self.is_running = False
        self.auto_start_enabled = True
        self.model_name = "llama3.2"  # Default to a more commonly available model
        self.ollama_url = "http://localhost:11434"
        self.startup_timeout = 30  # seconds
        
    def check_ollama_running(self) -> bool:
        """Check if Ollama is running and responsive."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            self.is_running = response.status_code == 200
            return self.is_running
        except Exception:
            self.is_running = False
            return False
    
    def check_model_available(self) -> bool:
        """Check if the required model is available."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                return any(self.model_name in model for model in models)
        except Exception:
            pass
        return False
    
    def list_available_models(self) -> list:
        """Get list of all downloaded models."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get('models', []):
                    name = model['name']
                    size = model.get('size', 0)
                    # Convert size to human readable format
                    size_str = self._format_size(size)
                    models.append({
                        'name': name,
                        'size': size_str,
                        'modified': model.get('modified_at', '')
                    })
                return models
        except Exception as e:
            logger.error(f"Error listing models: {e}")
        return []
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable string."""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different model."""
        # Check if model exists
        available_models = self.list_available_models()
        model_names = [model['name'] for model in available_models]
        
        # Try exact match first
        if model_name in model_names:
            self.model_name = model_name
            logger.info(f"Switched to model: {model_name}")
            return True
        
        # Try partial match
        matches = [name for name in model_names if model_name.lower() in name.lower()]
        if len(matches) == 1:
            self.model_name = matches[0]
            logger.info(f"Switched to model: {matches[0]} (matched '{model_name}')")
            return True
        elif len(matches) > 1:
            logger.warning(f"Multiple models match '{model_name}': {matches}")
            return False
        else:
            logger.warning(f"Model '{model_name}' not found")
            return False
    
    def start_ollama_service(self) -> bool:
        """Start the Ollama service."""
        try:
            logger.info("Starting Ollama service...")
            
            # Check if ollama command is available
            try:
                subprocess.run(['ollama', '--version'], 
                             capture_output=True, check=True, timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                logger.error("Ollama command not found. Please install Ollama first.")
                return False
            
            # Start ollama serve in background
            self.ollama_process = subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for service to start
            for attempt in range(self.startup_timeout):
                time.sleep(1)
                if self.check_ollama_running():
                    logger.info("Ollama service started successfully")
                    
                    # Check if model is available
                    if not self.check_model_available():
                        logger.info(f"Model {self.model_name} not found, attempting to pull...")
                        self.pull_model()
                    
                    return True
                
            logger.error("Ollama service failed to start within timeout")
            return False
            
        except Exception as e:
            logger.error(f"Error starting Ollama service: {e}")
            return False
    
    def pull_model(self) -> bool:
        """Pull the required model if it's not available."""
        try:
            logger.info(f"Pulling model {self.model_name}...")
            result = subprocess.run(
                ['ollama', 'pull', self.model_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout for model download
            )
            
            if result.returncode == 0:
                logger.info(f"Model {self.model_name} pulled successfully")
                return True
            else:
                logger.error(f"Failed to pull model {self.model_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Model pull timed out for {self.model_name}")
            return False
        except Exception as e:
            logger.error(f"Error pulling model {self.model_name}: {e}")
            return False
    
    def stop_ollama_service(self):
        """Stop the Ollama service if we started it."""
        if self.ollama_process:
            try:
                logger.info("Stopping Ollama service...")
                self.ollama_process.terminate()
                self.ollama_process.wait(timeout=10)
                logger.info("Ollama service stopped")
            except subprocess.TimeoutExpired:
                logger.warning("Ollama service didn't stop gracefully, killing...")
                self.ollama_process.kill()
            except Exception as e:
                logger.error(f"Error stopping Ollama service: {e}")
            finally:
                self.ollama_process = None
                self.is_running = False
    
    def ensure_ollama_available(self) -> bool:
        """Ensure Ollama is running and the model is available."""
        # First check if it's already running
        if self.check_ollama_running():
            if self.check_model_available():
                return True
            else:
                # Service running but model missing
                logger.info("Ollama running but model missing, pulling model...")
                return self.pull_model()
        
        # Service not running, try to start it if auto-start is enabled
        if self.auto_start_enabled:
            logger.info("Ollama not running, attempting to start...")
            return self.start_ollama_service()
        else:
            logger.warning("Ollama not running and auto-start disabled")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current Ollama manager status."""
        return {
            "ollama_running": self.check_ollama_running(),
            "model_available": self.check_model_available(),
            "auto_start_enabled": self.auto_start_enabled,
            "model_name": self.model_name,
            "ollama_url": self.ollama_url,
            "managed_process": self.ollama_process is not None
        }

# Global Ollama manager instance
ollama_manager = OllamaManager()

def ensure_ollama_available() -> bool:
    """Convenience function to ensure Ollama is available."""
    return ollama_manager.ensure_ollama_available()

def get_ollama_status() -> Dict[str, Any]:
    """Get Ollama status."""
    return ollama_manager.get_status()

def set_auto_start(enabled: bool):
    """Enable or disable auto-start."""
    ollama_manager.auto_start_enabled = enabled
    logger.info(f"Ollama auto-start set to: {enabled}")

def handle_ollama_command(text_command: str) -> Optional[Dict[str, Any]]:
    """Handle Ollama-related voice commands."""
    command_lower = text_command.lower().strip()
    
    # Start Ollama
    if any(phrase in command_lower for phrase in ["start ollama", "launch ollama", "start ai"]):
        success = ollama_manager.start_ollama_service()
        if success:
            return {
                "spoken_response": "Ollama service started successfully.",
                "opened_url": None,
                "additional_context": "Ollama is now running"
            }
        else:
            return {
                "spoken_response": "Failed to start Ollama service.",
                "opened_url": None,
                "additional_context": "Check logs for details"
            }
    
    # Stop Ollama
    if any(phrase in command_lower for phrase in ["stop ollama", "shutdown ollama", "stop ai"]):
        ollama_manager.stop_ollama_service()
        return {
            "spoken_response": "Ollama service stopped.",
            "opened_url": None,
            "additional_context": "Ollama has been shut down"
        }
    
    # Ollama status
    if any(phrase in command_lower for phrase in ["ollama status", "ai status", "is ollama running"]):
        status = get_ollama_status()
        if status["ollama_running"] and status["model_available"]:
            response = f"Ollama is running with model {status['model_name']}."
        elif status["ollama_running"]:
            response = f"Ollama is running but model {status['model_name']} is not available."
        else:
            response = "Ollama is not running."
        
        if status["auto_start_enabled"]:
            response += " Auto-start is enabled."
        else:
            response += " Auto-start is disabled."
        
        return {
            "spoken_response": response,
            "opened_url": None,
            "additional_context": f"Ollama Status: {status}"
        }
    
    # Enable/disable auto-start
    if any(phrase in command_lower for phrase in ["enable ollama auto start", "turn on auto start"]):
        set_auto_start(True)
        return {
            "spoken_response": "Ollama auto-start enabled.",
            "opened_url": None,
            "additional_context": "Ollama will start automatically when needed"
        }
    
    if any(phrase in command_lower for phrase in ["disable ollama auto start", "turn off auto start"]):
        set_auto_start(False)
        return {
            "spoken_response": "Ollama auto-start disabled.",
            "opened_url": None,
            "additional_context": "Ollama will not start automatically"
        }
    
    # Pull model
    if any(phrase in command_lower for phrase in ["pull model", "download model", "update model"]):
        success = ollama_manager.pull_model()
        if success:
            return {
                "spoken_response": f"Model {ollama_manager.model_name} downloaded successfully.",
                "opened_url": None,
                "additional_context": "Model is now available"
            }
        else:
            return {
                "spoken_response": f"Failed to download model {ollama_manager.model_name}.",
                "opened_url": None,
                "additional_context": "Check internet connection and try again"
            }
    
    # List models
    if any(phrase in command_lower for phrase in ["list models", "show models", "available models"]):
        if not ollama_manager.check_ollama_running():
            return {
                "spoken_response": "Ollama is not running. Please start it first.",
                "opened_url": None,
                "additional_context": "Ollama service needed"
            }
        
        models = ollama_manager.list_available_models()
        if models:
            model_names = [model['name'] for model in models]
            if len(model_names) == 1:
                response = f"Available model: {model_names[0]}"
            else:
                response = f"Available models: {', '.join(model_names)}"
            
            current_model = ollama_manager.model_name
            response += f" Currently using: {current_model}"
            
            return {
                "spoken_response": response,
                "opened_url": None,
                "additional_context": f"Models: {models}"
            }
        else:
            return {
                "spoken_response": "No models found. You may need to download some first.",
                "opened_url": None,
                "additional_context": "No models available"
            }
    
    # Switch model (e.g., "use llama3" or "switch to codellama")
    if any(phrase in command_lower for phrase in ["use model", "switch to", "use "]):
        # Extract model name
        model_name = None
        if "use model" in command_lower:
            parts = command_lower.split("use model", 1)
            if len(parts) > 1:
                model_name = parts[1].strip()
        elif "switch to" in command_lower:
            parts = command_lower.split("switch to", 1)
            if len(parts) > 1:
                model_name = parts[1].strip().replace("model", "").strip()
        elif "use " in command_lower:
            # Handle "use llama3" format
            parts = command_lower.split("use ", 1)
            if len(parts) > 1:
                potential_model = parts[1].strip()
                # Only treat as model if it doesn't match other commands
                if not any(cmd in potential_model for cmd in ["google", "local", "voice", "tts"]):
                    model_name = potential_model
        
        if model_name:
            if not ollama_manager.check_ollama_running():
                return {
                    "spoken_response": "Ollama is not running. Please start it first.",
                    "opened_url": None,
                    "additional_context": "Ollama service needed"
                }
            
            success = ollama_manager.switch_model(model_name)
            if success:
                return {
                    "spoken_response": f"Switched to model {ollama_manager.model_name}.",
                    "opened_url": None,
                    "additional_context": f"Now using model: {ollama_manager.model_name}"
                }
            else:
                available_models = ollama_manager.list_available_models()
                model_names = [model['name'] for model in available_models]
                if model_names:
                    return {
                        "spoken_response": f"Model {model_name} not found. Available models: {', '.join(model_names[:3])}",
                        "opened_url": None,
                        "additional_context": f"Available: {model_names}"
                    }
                else:
                    return {
                        "spoken_response": "No models available. You may need to download some first.",
                        "opened_url": None,
                        "additional_context": "No models found"
                    }
    
    return None

def cleanup_ollama():
    """Cleanup function to call on app shutdown."""
    ollama_manager.stop_ollama_service()
