#!/usr/bin/env python3
"""
Demo script for the new TTS capabilities in Julie Julie.
Shows how to switch between Google TTS and say command.
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, '/Users/bard/Code/Julie-Julie-M1')

def demo_tts_switching():
    """Demonstrate TTS switching capabilities."""
    print("Julie Julie TTS Demo")
    print("=" * 40)
    
    try:
        from handlers.tts_handler import speak_text, set_tts_preference, get_tts_status, handle_tts_command
        
        # Show initial status
        print("Initial TTS Status:")
        status = get_tts_status()
        print(f"  Google Available: {status['google_available']}")
        print(f"  Google Preferred: {status['google_preferred']}")
        print(f"  Fallback Count: {status['fallback_count']}")
        print()
        
        # Test voice commands
        print("Testing voice commands:")
        
        # Switch to Google
        print("1. Switching to Google TTS...")
        result = handle_tts_command("use google voice")
        if result:
            print(f"   Response: {result['spoken_response']}")
        
        # Test speaking with Google (or fallback)
        print("2. Testing speech...")
        speech_result = speak_text("Hello, this is a test of Google text to speech.")
        print(f"   Method used: {speech_result['method']}")
        print(f"   Success: {speech_result['success']}")
        
        # Switch to local say
        print("3. Switching to local say command...")
        result = handle_tts_command("use local voice")
        if result:
            print(f"   Response: {result['spoken_response']}")
        
        # Test speaking with say
        print("4. Testing local speech...")
        speech_result = speak_text("Hello, this is a test of the local say command.")
        print(f"   Method used: {speech_result['method']}")
        print(f"   Success: {speech_result['success']}")
        
        # Test forced fallback
        print("5. Testing forced fallback...")
        speech_result = speak_text("This will always use the say command.", force_fallback=True)
        print(f"   Method used: {speech_result['method']}")
        print(f"   Success: {speech_result['success']}")
        
        # Final status
        print()
        print("Final TTS Status:")
        status = get_tts_status()
        print(f"  Google Available: {status['google_available']}")
        print(f"  Google Preferred: {status['google_preferred']}")
        print(f"  Fallback Count: {status['fallback_count']}")
        
        print()
        print("Demo completed successfully!")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed.")
    except Exception as e:
        print(f"Error during demo: {e}")

def demo_julie_integration():
    """Show how TTS integrates with Julie Julie commands."""
    print()
    print("Julie Julie Integration Demo")
    print("=" * 40)
    
    try:
        # Import the main processing function
        from julie_julie_app import process_command_from_user
        
        print("Testing TTS commands through Julie Julie:")
        
        # Test TTS status command
        print("1. Checking TTS status...")
        result = process_command_from_user("tts status")
        print(f"   Response: {result.get('spoken_response', 'No response')}")
        
        # Test switching voice
        print("2. Switching to Google voice...")
        result = process_command_from_user("use google voice")
        print(f"   Response: {result.get('spoken_response', 'No response')}")
        
        # Test a regular command (should use new TTS)
        print("3. Testing time command with new TTS...")
        result = process_command_from_user("what time is it")
        print(f"   Response: {result.get('spoken_response', 'No response')}")
        
        print()
        print("Integration demo completed!")
        
    except ImportError as e:
        print(f"Import error: {e}")
    except Exception as e:
        print(f"Error during integration demo: {e}")

def main():
    """Run the TTS demo."""
    print("Starting TTS demonstration...")
    print()
    
    # Run the TTS switching demo
    demo_tts_switching()
    
    # Run the Julie integration demo
    demo_julie_integration()
    
    print()
    print("All demos completed!")

if __name__ == "__main__":
    main()
