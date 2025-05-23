#!/usr/bin/env python3
"""
Quick test of the radio functionality - Updated for correct patterns
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from handlers.radio_handler import handle_radio_command, RADIO_STATIONS

def test_radio():
    print("🎵 Testing Radio Handler - Updated Patterns...")
    print("=" * 50)
    
    # Show what stations we have
    print("\n📻 Available Stations:")
    for key, station in RADIO_STATIONS.items():
        print(f"  {key.title()}: {station['name']} -> {station['url']}")
    
    print("\n🧪 Testing Commands (without 'play' to avoid YouTube):")
    print("-" * 50)
    
    # Test classical
    result = handle_radio_command("classical radio")
    print(f"Classical: {result['spoken_response'] if result else 'None'}")
    
    # Test jazz
    result = handle_radio_command("jazz music")
    print(f"Jazz: {result['spoken_response'] if result else 'None'}")
    
    # Test rock
    result = handle_radio_command("rock radio")
    print(f"Rock: {result['spoken_response'] if result else 'None'}")
    
    # Test progressive
    result = handle_radio_command("progressive rock")
    print(f"Progressive: {result['spoken_response'] if result else 'None'}")
    
    # Test NPR
    result = handle_radio_command("npr")
    print(f"NPR: {result['spoken_response'] if result else 'None'}")
    
    # Test news
    result = handle_radio_command("news")
    print(f"News: {result['spoken_response'] if result else 'None'}")
    
    # Test station list
    result = handle_radio_command("what radio stations do you have")
    if result:
        print(f"\nStation List Response:\n{result['spoken_response']}")
    
    # Test non-radio command
    result = handle_radio_command("what time is it")
    print(f"\nNon-radio command: {result}")
    
    print("\n✅ Radio handler tests completed!")
    print("\n🎵 Correct voice commands:")
    print("  - 'Julie Julie' → 'Classical radio'")
    print("  - 'Julie Julie' → 'Jazz music'") 
    print("  - 'Julie Julie' → 'Rock radio'")
    print("  - 'Julie Julie' → 'NPR'")
    print("  - 'Julie Julie' → 'News'")

if __name__ == "__main__":
    test_radio()
