#!/bin/bash
# Run the debug version of Julie Julie

echo "====================================="
echo "Starting Julie Julie in DEBUG mode"
echo "====================================="

# Make sure you're in the right directory
cd /Users/bard/Code/Julie-Julie-M1

# Activate the virtual environment if necessary
# Uncomment the next line if needed
# source .venv/bin/activate

# Run the app with debug level info to the console
PYTHONUNBUFFERED=1 python julie_julie_app.py 2>&1 | tee julie_julie_debug.log

echo "====================================="
echo "Julie Julie has exited"
echo "====================================="
