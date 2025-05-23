#!/usr/bin/env python3
"""
Debug script to test system_profiler parsing
"""

import subprocess
import sys
import os

def debug_system_profiler():
    print("🔍 Debugging system_profiler parsing...")
    print("=" * 50)
    
    try:
        # Run the actual system command
        result = subprocess.run([
            'system_profiler', 'SPAudioDataType'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ system_profiler failed: {result.stderr}")
            return
        
        print("✅ system_profiler output received")
        print("\n📋 Raw output (first 1000 chars):")
        print("-" * 40)
        print(result.stdout[:1000])
        print("-" * 40)
        
        # Parse line by line
        lines = result.stdout.split('\\n')
        devices = []
        current_device = None
        
        print(f"\n🔍 Parsing {len(lines)} lines...")
        
        for i, line in enumerate(lines):
            # Show lines that contain colons (potential device names)
            if ':' in line and i < 50:  # Limit to first 50 lines for readability
                print(f"Line {i:2d}: '{line}' (len={len(line)}, starts_8_spaces={line.startswith('        ')})")
                
                # Check if this looks like a device name
                if ':' in line and not line.strip().startswith('Audio:') and not line.strip().startswith('Devices:'):
                    # Exclude property lines
                    if not any(prop in line for prop in ['Output Channels', 'Input Channels', 'Current SampleRate', 
                                                        'Manufacturer', 'Transport', 'Default', 'Source']):
                        device_name = line.strip().replace(':', '').strip()
                        if device_name and len(device_name) > 1:
                            current_device = device_name
                            print(f"  📱 Found potential device: '{current_device}'")
            
            # Check for output channels
            elif 'Output Channels:' in line and current_device:
                devices.append(current_device)
                print(f"  ✅ Confirmed output device: '{current_device}'")
                current_device = None
        
        print(f"\n🎵 Final detected devices: {devices}")
        
        if not devices:
            print("\\n❌ No devices found! Let's try a different approach...")
            
            # Alternative parsing - look for any line with colon that's indented
            print("\\n🔍 Alternative parsing attempt:")
            for i, line in enumerate(lines):
                if ':' in line and line.startswith(' ') and i < 30:
                    print(f"  Line {i}: '{line.strip()}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_system_profiler()
