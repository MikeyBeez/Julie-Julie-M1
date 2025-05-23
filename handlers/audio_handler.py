"""
Audio handler for switching between different audio output devices.
Simplified version with better parsing logic.
"""

import subprocess
import re
import logging

logger = logging.getLogger('julie_julie')

def handle_audio_command(text_command):
    """
    Handle audio output device switching and listing.
    """
    try:
        command_lower = text_command.lower().strip()
        
        # Check if it's an audio request
        if not _is_audio_request(command_lower):
            return None
        
        # List available speakers
        if _is_list_request(command_lower):
            return _list_audio_devices()
        
        # Switch to specific speaker
        speaker_name = _extract_speaker_name(command_lower)
        if speaker_name:
            return _switch_to_speaker(speaker_name)
        
        # If no specific speaker mentioned, list available options
        return _list_audio_devices()
        
    except Exception as e:
        logger.error(f"Audio handler error: {e}")
        return {
            "spoken_response": "I had trouble with the audio settings.",
            "opened_url": None,
            "additional_context": None
        }

def _is_audio_request(command_lower):
    """Check if this is an audio device request"""
    audio_keywords = [
        "audio", "speaker", "speakers", "sound", "output",
        "audio device", "sound output", "switch audio"
    ]
    
    return any(keyword in command_lower for keyword in audio_keywords)

def _is_list_request(command_lower):
    """Check if user wants to list available speakers"""
    list_patterns = [
        "list", "show", "what", "available", "options",
        "speakers do you have", "audio devices", "sound devices"
    ]
    
    return any(pattern in command_lower for pattern in list_patterns)

def _get_audio_devices():
    """Get actual device names by running system_profiler command with improved parsing"""
    try:
        # Run the actual system command
        result = subprocess.run([
            'system_profiler', 'SPAudioDataType'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            logger.error(f"system_profiler failed: {result.stderr}")
            return []
        
        # More robust parsing approach
        devices = []
        lines = result.stdout.split('\\n')
        
        in_devices_section = False
        current_device = None
        
        for line in lines:
            # Look for the Devices section
            if 'Devices:' in line:
                in_devices_section = True
                continue
            
            if not in_devices_section:
                continue
            
            # Device names are indented and end with colon
            # Look for lines that are indented but not too deeply indented (properties)
            if ':' in line:
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip())
                
                # Device names typically have 8 spaces, properties have 10+ spaces
                if 6 <= leading_spaces <= 9:
                    # This might be a device name
                    device_name = line.strip().replace(':', '').strip()
                    
                    # Skip known property names
                    skip_words = ['Default', 'Manufacturer', 'Output Channels', 'Input Channels', 
                                 'Current SampleRate', 'Transport', 'Source']
                    
                    if not any(word in line for word in skip_words) and device_name:
                        current_device = device_name
                        logger.info(f"Found potential device: {current_device}")
                
                # Look for Output Channels to confirm it's an output device
                elif 'Output Channels:' in line and current_device:
                    devices.append(current_device)
                    logger.info(f"Confirmed output device: {current_device}")
                    current_device = None
        
        # If the above didn't work, try a simpler approach
        if not devices:
            logger.info("First parsing attempt failed, trying simpler approach...")
            devices = _get_audio_devices_simple(result.stdout)
        
        logger.info(f"Final audio output devices: {devices}")
        return devices
        
    except Exception as e:
        logger.error(f"Error running system_profiler: {e}")
        return []

def _get_audio_devices_simple(output):
    """Simpler parsing as fallback"""
    devices = []
    lines = output.split('\\n')
    
    for line in lines:
        # Look for any line that's indented, has a colon, and looks like a device name
        if ':' in line and line.startswith('        '):
            device_name = line.strip().replace(':', '').strip()
            
            # Skip obvious property names
            if device_name and not any(word in device_name for word in 
                ['Default', 'Manufacturer', 'Output', 'Input', 'Current', 'Transport', 'Source']):
                devices.append(device_name)
                logger.info(f"Simple parsing found: {device_name}")
    
    # Remove duplicates while preserving order
    unique_devices = []
    for device in devices:
        if device not in unique_devices:
            unique_devices.append(device)
    
    return unique_devices

def _list_audio_devices():
    """List all available audio output devices"""
    devices = _get_audio_devices()
    
    if not devices:
        return {
            "spoken_response": "I couldn't find any audio devices.",
            "opened_url": None,
            "additional_context": None
        }
    
    # Create a spoken list of the actual device names
    if len(devices) == 1:
        device_list = devices[0]
    elif len(devices) == 2:
        device_list = f"{devices[0]} and {devices[1]}"
    else:
        device_list = ", ".join(devices[:-1]) + f", and {devices[-1]}"
    
    return {
        "spoken_response": f"Available speakers: {device_list}. Say 'switch to' followed by the speaker name.",
        "opened_url": None,
        "additional_context": f"Found {len(devices)} audio devices"
    }

def _extract_speaker_name(command_lower):
    """Extract speaker name from command"""
    # Look for "switch to X" or "use X" patterns
    patterns = [
        r"switch to (.+)",
        r"use (.+)",
        r"set audio to (.+)",
        r"change to (.+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, command_lower)
        if match:
            return match.group(1).strip()
    
    return None

def _switch_to_speaker(speaker_name):
    """Switch to specified speaker"""
    try:
        # Get the actual list of devices to find the best match
        devices = _get_audio_devices()
        
        if not devices:
            return {
                "spoken_response": "I couldn't find any audio devices to switch to.",
                "opened_url": None,
                "additional_context": None
            }
        
        # Find the best matching device name
        target_device = _find_matching_device(speaker_name, devices)
        
        if not target_device:
            device_list = ", ".join(devices)
            return {
                "spoken_response": f"I couldn't find a speaker named '{speaker_name}'. Available speakers are: {device_list}",
                "opened_url": None,
                "additional_context": None
            }
        
        # Try to switch using SwitchAudioSource if available
        try:
            result = subprocess.run([
                'SwitchAudioSource', '-s', target_device
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return {
                    "spoken_response": f"Switched audio to {target_device}.",
                    "opened_url": None,
                    "additional_context": f"Audio output: {target_device}"
                }
        except FileNotFoundError:
            # SwitchAudioSource not installed
            pass
        
        # Fallback: Open Sound preferences for manual selection
        applescript = '''
        tell application "System Preferences"
            activate
            set current pane to pane "com.apple.preference.sound"
        end tell
        '''
        
        subprocess.run(['osascript', '-e', applescript], timeout=10)
        
        return {
            "spoken_response": f"Opened Sound preferences. Please select {target_device} manually.",
            "opened_url": None,
            "additional_context": f"Manual selection needed for: {target_device}"
        }
        
    except Exception as e:
        logger.error(f"Error switching speaker: {e}")
        return {
            "spoken_response": f"I couldn't switch to {speaker_name}. Please check Sound preferences manually.",
            "opened_url": None,
            "additional_context": None
        }

def _find_matching_device(speaker_name, devices):
    """Find the best matching device from the actual device list"""
    speaker_lower = speaker_name.lower()
    
    # First, try exact match (case insensitive)
    for device in devices:
        if speaker_lower == device.lower():
            return device
    
    # Then try partial matches
    for device in devices:
        device_lower = device.lower()
        
        # Check if speaker name is contained in device name
        if speaker_lower in device_lower:
            return device
        
        # Check if device name is contained in speaker name
        if device_lower in speaker_lower:
            return device
        
        # Check for common abbreviations/keywords
        if 'rca' in speaker_lower and 'rca' in device_lower:
            return device
        if 'dgx' in speaker_lower and 'dgx' in device_lower:
            return device
        if 'yamaha' in speaker_lower and 'dgx' in device_lower:
            return device
        if 'w75' in speaker_lower and 'w75' in device_lower:
            return device
        if 'tv' in speaker_lower and 'w75' in device_lower:
            return device
        if 'mac' in speaker_lower and 'mac mini' in device_lower:
            return device
        if 'built' in speaker_lower and 'mac mini' in device_lower:
            return device
    
    return None

# Voice command examples:
# "What speakers are available?"
# "List audio devices"
# "Switch to RCA RTS7010B"
# "Use DGX-670"
# "Switch to W75"
# "Change to Mac mini Speakers"
