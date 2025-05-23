#!/usr/bin/env python3
"""
Simple test script for TTS handler that can be run manually.
Run with: python run_tts_tests.py
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, '/Users/bard/Code/Julie-Julie-M1')

def test_tts_manager_import():
    """Test that we can import the TTS handler."""
    try:
        from handlers.tts_handler import TTSManager, handle_tts_command
        print("✓ TTS handler imports successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_tts_manager_init():
    """Test TTSManager initialization."""
    try:
        from handlers.tts_handler import TTSManager
        manager = TTSManager()
        print(f"✓ TTSManager initialized - Google available: {manager.google_available}")
        return True
    except Exception as e:
        print(f"✗ TTSManager init failed: {e}")
        return False

def test_tts_commands():
    """Test TTS command handling."""
    try:
        from handlers.tts_handler import handle_tts_command
        
        # Test status command
        result = handle_tts_command("tts status")
        if result and "spoken_response" in result:
            print("✓ TTS status command works")
        else:
            print("✗ TTS status command failed")
            return False
        
        # Test preference commands
        result = handle_tts_command("use google voice")
        if result and "Google" in result["spoken_response"]:
            print("✓ Google voice command works")
        else:
            print("✗ Google voice command failed")
            return False
        
        result = handle_tts_command("use local voice")
        if result and "local" in result["spoken_response"]:
            print("✓ Local voice command works")
        else:
            print("✗ Local voice command failed")
            return False
        
        # Test unrecognized command
        result = handle_tts_command("random command")
        if result is None:
            print("✓ Unrecognized command returns None")
        else:
            print("✗ Should return None for unrecognized commands")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Command test failed: {e}")
        return False

def test_say_fallback():
    """Test the say fallback (without actually speaking)."""
    try:
        from handlers.tts_handler import TTSManager
        manager = TTSManager()
        
        # Mock the subprocess call to avoid actual speech
        import unittest.mock
        with unittest.mock.patch('subprocess.run') as mock_run:
            result = manager._say_fallback("test")
            if mock_run.called:
                print("✓ Say fallback calls subprocess correctly")
                return True
            else:
                print("✗ Say fallback didn't call subprocess")
                return False
    except Exception as e:
        print(f"✗ Say fallback test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running TTS Handler Tests")
    print("=" * 40)
    
    tests = [
        test_tts_manager_import,
        test_tts_manager_init,
        test_tts_commands,
        test_say_fallback
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
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())
