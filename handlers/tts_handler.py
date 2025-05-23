"""
Text-to-Speech handler with Google Cloud TTS and macOS say fallback.
Provides configurable TTS with automatic fallback when needed.
"""

import subprocess
import logging
import os
import json
from typing import Optional, Dict, Any
import tempfile

logger = logging.getLogger('julie_julie')

class TTSManager:
    """Manages text-to-speech with Google TTS primary and say fallback."""
    
    def __init__(self):
        self.google_available = self._check_google_credentials()
        self.use_google_tts = True  # Default preference
        self.fallback_count = 0
        
    def _check_google_credentials(self) -> bool:
        """Check if Google Cloud credentials are available."""
        try:
            # Check for credentials environment variable
            creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if creds_path and os.path.exists(creds_path):
                return True
            
            # Check for gcloud default credentials
            try:
                result = subprocess.run(['gcloud', 'auth', 'list', '--format=json'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    accounts = json.loads(result.stdout)
                    return len(accounts) > 0
            except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
                pass
            
            return False
        except Exception as e:
            logger.debug(f"Error checking Google credentials: {e}")
            return False
    
    def _google_tts(self, text: str, voice: str = "en-US-Standard-A") -> bool:
        """Use Google Cloud TTS to speak text."""
        try:
            from google.cloud import texttospeech
            
            # Initialize the client
            client = texttospeech.TextToSpeechClient()
            
            # Set up the input text
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build the voice request
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name=voice
            )
            
            # Select the type of audio file
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            # Perform the text-to-speech request
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config
            )
            
            # Save and play the audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tmp_file.write(response.audio_content)
                tmp_path = tmp_file.name
            
            # Play the audio file
            subprocess.run(['afplay', tmp_path], check=True)
            
            # Clean up
            os.unlink(tmp_path)
            
            logger.info(f"Google TTS successful for: {text[:50]}...")
            return True
            
        except ImportError:
            logger.warning("Google Cloud TTS library not installed")
            return False
        except Exception as e:
            logger.warning(f"Google TTS failed: {e}")
            return False
    
    def _say_fallback(self, text: str, voice: str = "Alex") -> bool:
        """Use macOS say command as fallback."""
        try:
            subprocess.run(['say', '-v', voice, text], check=True)
            logger.info(f"Say fallback successful for: {text[:50]}...")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Say command failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Say fallback error: {e}")
            return False
    
    def speak(self, text: str, force_fallback: bool = False) -> Dict[str, Any]:
        """
        Speak text using Google TTS with automatic fallback to say.
        
        Args:
            text: Text to speak
            force_fallback: If True, skip Google TTS and use say directly
            
        Returns:
            Dict with success status and method used
        """
        if not text.strip():
            return {"success": False, "error": "No text provided", "method": "none"}
        
        # Try Google TTS first (unless forced to fallback or not available)
        if not force_fallback and self.use_google_tts and self.google_available:
            if self._google_tts(text):
                return {"success": True, "method": "google_tts", "fallback_count": self.fallback_count}
            else:
                logger.info("Google TTS failed, falling back to say")
                self.fallback_count += 1
        
        # Fallback to say command
        if self._say_fallback(text):
            method = "say_fallback" if not force_fallback else "say_direct"
            return {"success": True, "method": method, "fallback_count": self.fallback_count}
        
        return {"success": False, "error": "Both TTS methods failed", "method": "none"}
    
    def set_google_preference(self, use_google: bool):
        """Enable or disable Google TTS preference."""
        self.use_google_tts = use_google
        logger.info(f"Google TTS preference set to: {use_google}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current TTS manager status."""
        return {
            "google_available": self.google_available,
            "google_preferred": self.use_google_tts,
            "fallback_count": self.fallback_count
        }

# Global TTS manager instance
tts_manager = TTSManager()

def speak_text(text: str, force_fallback: bool = False) -> Dict[str, Any]:
    """Convenience function to speak text."""
    return tts_manager.speak(text, force_fallback)

def set_tts_preference(use_google: bool):
    """Set TTS preference."""
    tts_manager.set_google_preference(use_google)

def get_tts_status() -> Dict[str, Any]:
    """Get TTS status."""
    return tts_manager.get_status()

def handle_tts_command(text_command: str) -> Optional[Dict[str, Any]]:
    """Handle TTS-related voice commands."""
    command_lower = text_command.lower().strip()
    
    # Switch to Google TTS
    if any(phrase in command_lower for phrase in ["use google voice", "switch to google", "google tts"]):
        set_tts_preference(True)
        return {
            "spoken_response": "Switched to Google text to speech.",
            "opened_url": None,
            "additional_context": "TTS preference changed to Google"
        }
    
    # Switch to say command
    if any(phrase in command_lower for phrase in ["use local voice", "switch to say", "use say command"]):
        set_tts_preference(False)
        return {
            "spoken_response": "Switched to local say command.",
            "opened_url": None,
            "additional_context": "TTS preference changed to say"
        }
    
    # TTS status
    if any(phrase in command_lower for phrase in ["tts status", "voice status", "what voice"]):
        status = get_tts_status()
        if status["google_preferred"] and status["google_available"]:
            current = "Google text to speech"
        elif status["google_preferred"] and not status["google_available"]:
            current = "Google text to speech (but using say fallback - no credentials)"
        else:
            current = "local say command"
        
        response = f"Currently using {current}."
        if status["fallback_count"] > 0:
            response += f" Fell back to say command {status['fallback_count']} times."
        
        return {
            "spoken_response": response,
            "opened_url": None,
            "additional_context": f"TTS Status: {status}"
        }
    
    # Test TTS
    if any(phrase in command_lower for phrase in ["test voice", "test tts", "test speech"]):
        result = speak_text("This is a test of the text to speech system.")
        return {
            "spoken_response": "Voice test completed.",
            "opened_url": None,
            "additional_context": f"TTS test result: {result}"
        }
    
    return None
