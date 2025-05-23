#!/bin/bash

# Run all tests for Julie Julie
echo "Running Julie Julie Test Suite..."
echo "================================="

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install test dependencies if they don't exist
echo "Checking test dependencies..."
pip install pytest pytest-cov requests > /dev/null 2>&1

echo ""
echo "Running Unit Tests..."
echo "--------------------"

# Run tests with coverage
python -m pytest tests/ -v --cov=. --cov-report=term-missing --cov-exclude=tests/

echo ""
echo "Test Results Summary:"
echo "===================="
echo "- Unit tests verify individual components work correctly"
echo "- Integration tests verify the full application flow"
echo "- All voice/audio output is mocked to prevent actual speech"
echo "- API endpoints are tested with mock data"
echo ""
echo "To run specific test categories:"
echo "  python -m pytest tests/test_command_handlers.py  # Handler tests"
echo "  python -m pytest tests/test_core_logic.py        # Core logic tests"
echo "  python -m pytest tests/test_flask_api.py         # API tests"
echo "  python -m pytest tests/test_integration.py       # Integration tests"
