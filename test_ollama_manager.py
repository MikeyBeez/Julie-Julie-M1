#!/usr/bin/env python3
"""
Test script for Ollama manager functionality.
Run with: python test_ollama_manager.py
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, '/Users/bard/Code/Julie-Julie-M1')

def test_ollama_manager_import():
    """Test that we can import the Ollama manager."""
    try:
        from handlers.ollama_manager import OllamaManager, handle_ollama_command
        print("✓ Ollama manager imports successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_ollama_manager_init():
    """Test OllamaManager initialization."""
    try:
        from handlers.ollama_manager import OllamaManager
        manager = OllamaManager()
        print(f"✓ OllamaManager initialized - Auto-start: {manager.auto_start_enabled}")
        return True
    except Exception as e:
        print(f"✗ OllamaManager init failed: {e}")
        return False

def test_ollama_status_check():
    """Test Ollama status checking."""
    try:
        from handlers.ollama_manager import OllamaManager
        manager = OllamaManager()
        
        # Check if Ollama is running (won't try to start it)
        is_running = manager.check_ollama_running()
        model_available = manager.check_model_available() if is_running else False
        
        print(f"✓ Status check completed - Running: {is_running}, Model available: {model_available}")
        return True
    except Exception as e:
        print(f"✗ Status check failed: {e}")
        return False

def test_ollama_commands():
    """Test Ollama command handling."""
    try:
        from handlers.ollama_manager import handle_ollama_command
        
        # Test status command
        result = handle_ollama_command("ollama status")
        if result and "spoken_response" in result:
            print("✓ Ollama status command works")
        else:
            print("✗ Ollama status command failed")
            return False
        
        # Test auto-start commands
        result = handle_ollama_command("enable ollama auto start")
        if result and "enabled" in result["spoken_response"]:
            print("✓ Enable auto-start command works")
        else:
            print("✗ Enable auto-start command failed")
            return False
        
        result = handle_ollama_command("disable ollama auto start")
        if result and "disabled" in result["spoken_response"]:
            print("✓ Disable auto-start command works")
        else:
            print("✗ Disable auto-start command failed")
            return False
        
        # Test unrecognized command
        result = handle_ollama_command("random command")
        if result is None:
            print("✓ Unrecognized command returns None")
        else:
            print("✗ Should return None for unrecognized commands")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Command test failed: {e}")
        return False

def test_ensure_ollama_available():
    """Test the ensure_ollama_available function (without actually starting)."""
    try:
        from handlers.ollama_manager import OllamaManager
        manager = OllamaManager()
        
        # Temporarily disable auto-start to avoid actually starting Ollama
        original_auto_start = manager.auto_start_enabled
        manager.auto_start_enabled = False
        
        # This should return False if Ollama isn't running
        result = manager.ensure_ollama_available()
        
        # Restore original setting
        manager.auto_start_enabled = original_auto_start
        
        print(f"✓ ensure_ollama_available works (returned {result})")
        return True
    except Exception as e:
        print(f"✗ ensure_ollama_available test failed: {e}")
        return False

def test_get_status():
    """Test getting Ollama manager status."""
    try:
        from handlers.ollama_manager import get_ollama_status
        
        status = get_ollama_status()
        required_keys = ["ollama_running", "model_available", "auto_start_enabled", "model_name"]
        
        for key in required_keys:
            if key not in status:
                print(f"✗ Missing key '{key}' in status")
                return False
        
        print("✓ Status function returns complete information")
        print(f"    Running: {status['ollama_running']}")
        print(f"    Model: {status['model_name']}")
        print(f"    Auto-start: {status['auto_start_enabled']}")
        return True
    except Exception as e:
        print(f"✗ Status test failed: {e}")
        return False

def main():
    """Run all Ollama manager tests."""
    print("Running Ollama Manager Tests")
    print("=" * 40)
    
    tests = [
        test_ollama_manager_import,
        test_ollama_manager_init,
        test_ollama_status_check,
        test_ollama_commands,
        test_ensure_ollama_available,
        test_get_status
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! ✓")
        print("\nNote: These tests don't actually start/stop Ollama to avoid")
        print("disrupting your system. To test auto-start functionality,")
        print("ensure Ollama is not running and try asking Julie Julie")
        print("a conversational question.")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())
