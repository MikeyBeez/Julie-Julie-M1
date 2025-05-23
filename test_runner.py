#!/usr/bin/env python3
"""
Test runner for Julie Julie

This script runs the complete test suite for the Julie Julie voice assistant.
It can be run directly with Python without needing shell script permissions.

Usage:
    python test_runner.py                    # Run all tests
    python test_runner.py --unit             # Run only unit tests
    python test_runner.py --integration      # Run only integration tests
    python test_runner.py --coverage         # Run with coverage report
    python test_runner.py --verbose          # Run with verbose output
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{description}")
    print("=" * len(description))
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=False, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

def install_dependencies():
    """Install test dependencies if needed."""
    print("Checking and installing test dependencies...")
    
    dependencies = ["pytest", "pytest-cov", "pytest-mock", "requests"]
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
        except ImportError:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)

def main():
    parser = argparse.ArgumentParser(description="Run Julie Julie tests")
    parser.add_argument("--unit", action="store_true", 
                       help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", 
                       help="Run only integration tests") 
    parser.add_argument("--all", action="store_true",
                       help="Run ALL tests including server integration") 
    parser.add_argument("--coverage", action="store_true",
                       help="Run with coverage report")
    parser.add_argument("--verbose", action="store_true",
                       help="Run with verbose output")
    
    args = parser.parse_args()
    
    # Change to the project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Install dependencies
    install_dependencies()
    
    # Build pytest command
    pytest_cmd = [sys.executable, "-m", "pytest"]
    
    # Add test selection
    if args.unit:
        pytest_cmd.extend([
            "tests/test_command_handlers.py",
            "tests/test_core_logic.py",
            "tests/test_flask_api.py",
            "tests/test_simple_integration.py"
        ])
    elif args.integration:
        pytest_cmd.extend(["tests/test_integration.py"])
    elif args.all:
        pytest_cmd.extend(["tests/"])  # Run everything including server tests
    else:
        # Run all tests except the potentially problematic server integration test
        pytest_cmd.extend([
            "tests/test_command_handlers.py",
            "tests/test_core_logic.py", 
            "tests/test_flask_api.py",
            "tests/test_simple_integration.py"
        ])
    
    # Add options
    if args.verbose:
        pytest_cmd.extend(["-v"])
    
    if args.coverage:
        pytest_cmd.extend([
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-exclude=tests/"
        ])
    
    # Run tests
    print("Running Julie Julie Test Suite...")
    print("================================")
    print(f"Command: {' '.join(pytest_cmd)}")
    
    success = run_command(' '.join(pytest_cmd), "Executing Tests")
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("\nTest Categories Available:")
        print("  - Unit Tests: Individual component testing")
        print("  - Integration Tests: End-to-end workflow testing")
        print("  - API Tests: Flask endpoint testing")
        print("  - Handler Tests: Command processor testing")
        print("\nTo run specific categories:")
        print(f"  {sys.executable} test_runner.py --unit")
        print(f"  {sys.executable} test_runner.py --integration")
        print(f"  {sys.executable} test_runner.py --all          # Including server tests")
        print(f"  {sys.executable} test_runner.py --coverage")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
