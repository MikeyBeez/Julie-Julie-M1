#!/usr/bin/env python3
"""
Test the audio handler with actual system_profiler output
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from handlers.audio_handler import handle_audio_command, _get_audio_devices

def test_audio():
    print("🔊 Testing Audio Handler - Dynamic Device Detection...")
    print("=" * 60)
    
    # First, let's see what devices are actually detected
    print("\n📋 Running system_profiler to detect devices...")
    devices = _get_audio_devices()
    print(f"Detected devices: {devices}")
    
    print("\n🧪 Testing Commands:")
    print("-" * 40)
    
    # Test listing devices
    result = handle_audio_command("what speakers are available")
    print(f"List devices: {result['spoken_response'] if result else 'None'}")
    
    # Test with your actual device names
    if devices:
        print(f"\n🎯 Testing with your actual devices:")
        for device in devices[:3]:  # Test first 3 devices
            result = handle_audio_command(f"switch to {device}")
            print(f"Switch to '{device}': {result['spoken_response'] if result else 'None'}")
    
    # Test common abbreviations
    print(f"\n🎵 Testing common names:")
    test_names = ["RCA", "Yamaha", "TV", "W75", "Mac"]
    for name in test_names:
        result = handle_audio_command(f"switch to {name}")
        print(f"Switch to '{name}': {result['spoken_response'] if result else 'None'}")
    
    # Test non-audio command
    result = handle_audio_command("what time is it")
    print(f"\nNon-audio command: {result}")
    
    print("\n✅ Audio handler tests completed!")
    print(f"\n🎵 Your actual voice commands based on detected devices:")
    if devices:
        for device in devices:
            print(f"  - 'Julie Julie' → 'Switch to {device}'")
    else:
        print("  - No devices detected - check system_profiler output")

if __name__ == "__main__":
    test_audio()
