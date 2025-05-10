#!/usr/bin/env python3
"""
Julie Julie Terminal Input Mode

This simple script listens for the pattern "Julie Julie [command] stop" in terminal input
and sends the command to the Julie Julie server. This is a simple way to test the 
Julie Julie assistant with a pattern similar to what we want to achieve with Voice Control.
"""

import re
import requests
import subprocess
import sys
import time

# Configuration
SERVER_URL = "http://127.0.0.1:58586"

def check_server():
    """Check if the Julie Julie server is running."""
    try:
        response = requests.get(SERVER_URL, timeout=2)
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException:
        return False

def process_command(command):
    """Send the command to Julie Julie server."""
    try:
        response = requests.post(
            f"{SERVER_URL}/activate_listening", 
            data={"text_command": command}
        )
        
        if response.status_code == 200:
            print(f"Julie Julie processed: '{command}'")
            return True
        else:
            print(f"Error: Server returned status code {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Error communicating with Julie Julie server: {e}")
        return False

def main():
    """Main function to run the terminal input processor."""
    print("Julie Julie Terminal Input Mode")
    print("==============================")
    
    # Check if server is running
    if not check_server():
        print(f"ERROR: Julie Julie server is not running at {SERVER_URL}")
        print("Please start Julie Julie first with: python julie_julie_app.py")
        return 1
    
    print("\nServer is running! You can now use Julie Julie.")
    print("Format: 'Julie Julie [your command] stop'")
    print("Example: 'Julie Julie what time is it stop'")
    print("Type 'exit' to quit\n")
    
    # Compile regex pattern for command extraction
    pattern = re.compile(r'Julie\s+Julie\s+(.+?)\s+stop', re.IGNORECASE)
    
    # Main input loop
    while True:
        try:
            # Get user input
            user_input = input("> ")
            
            # Check for exit command
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            # Try to match the pattern
            match = pattern.search(user_input)
            
            if match:
                # Extract the command part
                command = match.group(1).strip()
                print(f"Sending command: '{command}'")
                process_command(command)
            else:
                # Check if input starts with Julie Julie but doesn't have stop
                if user_input.lower().startswith("julie julie"):
                    print("Missing 'stop' keyword. Format: 'Julie Julie [command] stop'")
                # For testing, allow direct commands too
                elif user_input.strip():
                    print(f"Direct command: '{user_input}'")
                    process_command(user_input)
        
        except KeyboardInterrupt:
            print("\nExiting Julie Julie Terminal Input Mode")
            break
        
        except Exception as e:
            print(f"Error: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
