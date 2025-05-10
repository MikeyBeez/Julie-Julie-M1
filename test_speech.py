#!/usr/bin/env python3
"""
Test script for speech recognition functionality.
Run this to verify your microphone and speech recognition are working correctly.
"""

import speech_recognition as sr
import subprocess
import sys

def list_microphones():
    """List all available microphones."""
    print("Available microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"{index}: {name}")
    print()

def test_speech_recognition():
    """Test speech recognition functionality."""
    recognizer = sr.Recognizer()
    
    # Default microphone
    print("Using default microphone.")
    
    try:
        # Use system's say command to provide feedback
        subprocess.run(["say", "I will start listening in 3 seconds"], check=True)
        print("I will start listening in 3 seconds...")
        
        import time
        time.sleep(3)
        
        subprocess.run(["say", "I'm listening now, please speak"], check=True)
        print("Listening... Speak now!")
        
        with sr.Microphone() as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Listen for audio input
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Processing speech...")
            
            # Recognize using Google's speech recognition
            text = recognizer.recognize_google(audio)
            
            print(f"You said: {text}")
            subprocess.run(["say", f"You said: {text}"], check=True)
            
            return True, text
            
    except sr.WaitTimeoutError:
        print("No speech detected within timeout period.")
        subprocess.run(["say", "I didn't hear anything"], check=True)
        return False, "Timeout waiting for speech"
        
    except sr.UnknownValueError:
        print("Could not understand audio")
        subprocess.run(["say", "I couldn't understand what you said"], check=True)
        return False, "Speech unintelligible"
        
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        subprocess.run(["say", "I couldn't connect to the speech recognition service"], check=True)
        return False, f"Service error: {e}"
        
    except Exception as e:
        print(f"Error: {e}")
        subprocess.run(["say", "An error occurred"], check=True)
        return False, f"Error: {e}"

def main():
    """Main function to run the test."""
    print("Julie Julie Speech Recognition Test")
    print("==================================\n")
    
    # Check if speech_recognition is installed
    try:
        import speech_recognition as sr
    except ImportError:
        print("ERROR: speech_recognition library is not installed.")
        print("Install it with: pip install SpeechRecognition PyAudio")
        return 1
    
    # Check if PyAudio is installed
    try:
        import pyaudio
    except ImportError:
        print("ERROR: PyAudio is not installed.")
        print("Install it with: pip install PyAudio")
        print("If that fails, try: brew install portaudio && pip install PyAudio")
        return 1
    
    # List available microphones
    list_microphones()
    
    # Test speech recognition
    print("Testing speech recognition...")
    success, result = test_speech_recognition()
    
    if success:
        print("\nSpeech recognition test PASSED!")
    else:
        print(f"\nSpeech recognition test FAILED: {result}")
        print("Please check your microphone settings and try again.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
