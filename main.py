#!/usr/bin/env python3
"""
Julie Julie - A macOS menu bar assistant

This is the main entry point for the Julie Julie application.
It launches the menu bar app which handles commands via a Flask server.
"""

import sys
import os
import argparse
from julie_julie_app import JulieJulieRumpsApp, APP_NAME, APP_VERSION, logger

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=f'{APP_NAME} - A macOS menu bar assistant')
    parser.add_argument('--version', action='store_true', help='Show version information and exit')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Check for --version flag
    if args.version:
        print(f"{APP_NAME} v{APP_VERSION}")
        return 0
    
    # Set up debug mode if requested
    if args.debug:
        import logging
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Check if we're running on macOS
    if sys.platform != 'darwin':
        logger.error(f"{APP_NAME} is only supported on macOS")
        print(f"Error: {APP_NAME} is only supported on macOS")
        return 1
    
    try:
        # Launch the menu bar app
        logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        app = JulieJulieRumpsApp()
        app.run()
        return 0
    except Exception as e:
        logger.error(f"Error starting {APP_NAME}: {e}")
        print(f"Error starting {APP_NAME}: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
