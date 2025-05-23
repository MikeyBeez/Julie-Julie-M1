"""
Voice Control manager for Julie Julie.
Handles starting and stopping macOS Voice Control to prevent feedback loops.
"""

import subprocess
import logging
import time
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger('julie_julie')

class VoiceControlManager:
    """Manages macOS Voice Control state to prevent speech feedback."""
    
    def __init__(self):
        self.voice_control_available = self._check_voice_control_available()
        self.auto_manage = True  # Automatically manage voice control during speech
        
    def _check_voice_control_available(self) -> bool:
        """Check if Voice Control is available and enabled."""
        try:
            # Check if Voice Control is enabled using AppleScript
            script = '''
            tell application "System Events"
                tell process "ControlCenter"
                    return exists (menu bar item "Voice Control" of menu bar 1)
                end tell
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return result.returncode == 0 and result.stdout.strip() == "true"
            
        except Exception as e:
            logger.debug(f"Error checking Voice Control availability: {e}")
            return False
    
    def stop_listening(self) -> bool:
        """Stop Voice Control listening."""
        try:
            # AppleScript to stop Voice Control listening
            script = '''
            tell application "System Events"
                key code 53 using {command down}
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                logger.debug("Voice Control listening stopped")
                return True
            else:
                logger.debug(f"Failed to stop Voice Control: {result.stderr}")
                return False
                
        except Exception as e:
            logger.debug(f"Error stopping Voice Control: {e}")
            return False
    
    def start_listening(self) -> bool:
        """Start Voice Control listening."""
        try:
            # AppleScript to start Voice Control listening
            script = '''
            tell application "System Events"
                key code 53 using {command down}
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                logger.debug("Voice Control listening started")
                return True
            else:
                logger.debug(f"Failed to start Voice Control: {result.stderr}")
                return False
                
        except Exception as e:
            logger.debug(f"Error starting Voice Control: {e}")
            return False
    
    def get_listening_status(self) -> Optional[bool]:
        """Check if Voice Control is currently listening."""
        try:
            # AppleScript to check Voice Control status
            script = '''
            tell application "System Events"
                tell process "ControlCenter"
                    try
                        set vcStatus to value of attribute "AXDescription" of (menu bar item "Voice Control" of menu bar 1)
                        if vcStatus contains "listening" then
                            return true
                        else
                            return false
                        end if
                    on error
                        return false
                    end try
                end tell
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                return result.stdout.strip() == "true"
            else:
                return None
                
        except Exception as e:
            logger.debug(f"Error checking Voice Control status: {e}")
            return None
    
    @contextmanager
    def speech_context(self):
        """Context manager to prevent Voice Control from hearing speech."""
        if not self.auto_manage or not self.voice_control_available:
            yield
            return
        
        try:
            # Just yield - Voice Control should already be stopped when we start speaking
            yield
            
        finally:
            # Small delay after speech to ensure it's finished
            time.sleep(0.3)
    
    def restart_listening_after_response(self):
        """Restart Voice Control listening after a complete response."""
        if self.auto_manage and self.voice_control_available:
            # Wait a bit longer to ensure all speech is complete
            time.sleep(0.7)
            self.start_listening()
    
    def set_auto_manage(self, enabled: bool):
        """Enable or disable automatic Voice Control management."""
        self.auto_manage = enabled
        logger.info(f"Voice Control auto-management set to: {enabled}")

# Global Voice Control manager instance
voice_control_manager = VoiceControlManager()

@contextmanager
def managed_speech():
    """Context manager for speech that automatically manages Voice Control."""
    with voice_control_manager.speech_context():
        yield

def stop_voice_control():
    """Stop Voice Control listening."""
    return voice_control_manager.stop_listening()

def start_voice_control():
    """Start Voice Control listening."""
    return voice_control_manager.start_listening()

def get_voice_control_status():
    """Get Voice Control listening status."""
    return voice_control_manager.get_listening_status()

def set_voice_control_auto_manage(enabled: bool):
    """Enable or disable automatic Voice Control management."""
    voice_control_manager.set_auto_manage(enabled)

def restart_voice_control_after_response():
    """Restart Voice Control listening after a complete response."""
    voice_control_manager.restart_listening_after_response()

def handle_voice_control_command(text_command: str) -> Optional[dict]:
    """Handle Voice Control-related voice commands."""
    command_lower = text_command.lower().strip()
    
    # Stop listening
    if any(phrase in command_lower for phrase in ["stop listening", "voice control off", "stop voice control"]):
        success = stop_voice_control()
        return {
            "spoken_response": "Voice Control stopped." if success else "Failed to stop Voice Control.",
            "opened_url": None,
            "additional_context": f"Voice Control stop: {success}"
        }
    
    # Start listening
    if any(phrase in command_lower for phrase in ["start listening", "voice control on", "start voice control"]):
        success = start_voice_control()
        return {
            "spoken_response": "Voice Control started." if success else "Failed to start Voice Control.",
            "opened_url": None,
            "additional_context": f"Voice Control start: {success}"
        }
    
    # Check status
    if any(phrase in command_lower for phrase in ["voice control status", "listening status", "is voice control on"]):
        status = get_voice_control_status()
        if status is True:
            response = "Voice Control is listening."
        elif status is False:
            response = "Voice Control is not listening."
        else:
            response = "Unable to determine Voice Control status."
        
        auto_status = "enabled" if voice_control_manager.auto_manage else "disabled"
        response += f" Auto-management is {auto_status}."
        
        return {
            "spoken_response": response,
            "opened_url": None,
            "additional_context": f"VC Status: {status}, Auto: {voice_control_manager.auto_manage}"
        }
    
    # Enable/disable auto-management
    if any(phrase in command_lower for phrase in ["enable voice control auto", "auto manage voice control"]):
        set_voice_control_auto_manage(True)
        return {
            "spoken_response": "Voice Control auto-management enabled.",
            "opened_url": None,
            "additional_context": "Auto-management on"
        }
    
    if any(phrase in command_lower for phrase in ["disable voice control auto", "no auto manage"]):
        set_voice_control_auto_manage(False)
        return {
            "spoken_response": "Voice Control auto-management disabled.",
            "opened_url": None,
            "additional_context": "Auto-management off"
        }
    
    return None
