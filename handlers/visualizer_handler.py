"""
Visualizer handler for system-wide audio visualization using IINA.
"""

import re
import logging
import subprocess
import time

logger = logging.getLogger('julie_julie')

def handle_visualizer_command(text_command):
    """
    Handle visualizer on/off commands.
    """
    try:
        command_lower = text_command.lower().strip()
        
        if _is_visualizer_on_request(command_lower):
            return _start_visualizer()
        elif _is_visualizer_off_request(command_lower):
            return _stop_visualizer()
        
        return None
        
    except Exception as e:
        logger.error(f"Visualizer handler error: {e}")
        return None

def _is_visualizer_on_request(command_lower):
    """Check if this is a visualizer start request"""
    on_patterns = [
        "visualizer",
        "visualizer on",
        "start visualizer",
        "show visualizer",
        "enable visualizer"
    ]
    
    return any(pattern in command_lower for pattern in on_patterns)

def _is_visualizer_off_request(command_lower):
    """Check if this is a visualizer stop request"""
    off_patterns = [
        "visualizer off",
        "stop visualizer",
        "hide visualizer",
        "disable visualizer",
        "close visualizer"
    ]
    
    return any(pattern in command_lower for pattern in off_patterns)

def _start_visualizer():
    """Start IINA with system audio visualizer"""
    try:
        logger.info("Starting IINA audio visualizer")
        
        # Start IINA with system audio capture
        # Use 'default' to capture system audio, or try 'desktop' or screen capture
        subprocess.run([
            "iina",
            "--no-stdin",
            "avfoundation://default"  # Capture system audio
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait a moment for IINA to start
        time.sleep(2)
        
        # Try to enable visualizer via AppleScript
        visualizer_script = '''
        tell application "IINA"
            activate
        end tell
        
        delay 1
        
        tell application "System Events"
            tell process "IINA"
                try
                    -- Try to enable visualizer via menu
                    click menu item "Video Visualizer" of menu "View" of menu bar 1
                end try
            end tell
        end tell
        '''
        
        subprocess.run(["osascript", "-e", visualizer_script], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        return {
            "spoken_response": "Visualizer is now running! It should respond to any audio playing on your system.",
            "opened_url": None,
            "additional_context": "IINA visualizer started"
        }
        
    except subprocess.CalledProcessError:
        # Fallback: just open IINA normally
        try:
            subprocess.run(["open", "-a", "IINA"])
            return {
                "spoken_response": "Opened IINA. Go to View menu and select Video Visualizer, then open system audio.",
                "opened_url": None,
                "additional_context": "IINA opened manually"
            }
        except Exception as e:
            logger.error(f"Failed to open IINA: {e}")
            return {
                "spoken_response": "I couldn't start the visualizer. Make sure IINA is installed.",
                "opened_url": None,
                "additional_context": None
            }
    
    except Exception as e:
        logger.error(f"Visualizer start error: {e}")
        return {
            "spoken_response": "I had trouble starting the visualizer.",
            "opened_url": None,
            "additional_context": f"Error: {str(e)}"
        }

def _stop_visualizer():
    """Stop IINA visualizer"""
    try:
        logger.info("Stopping IINA visualizer")
        
        # Try to quit IINA
        quit_script = '''
        tell application "IINA"
            quit
        end tell
        '''
        
        subprocess.run(["osascript", "-e", quit_script], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        return {
            "spoken_response": "Visualizer stopped.",
            "opened_url": None,
            "additional_context": "IINA closed"
        }
        
    except Exception as e:
        logger.error(f"Visualizer stop error: {e}")
        return {
            "spoken_response": "I had trouble stopping the visualizer.",
            "opened_url": None,
            "additional_context": f"Error: {str(e)}"
        }
