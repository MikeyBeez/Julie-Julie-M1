# tests/__init__.py
"""
Julie Julie Test Suite

This package contains unit tests and integration tests for the Julie Julie voice assistant.

Test Categories:
- test_command_handlers.py: Tests for individual command handlers (calculations, music, YouTube, etc.)
- test_core_logic.py: Tests for core application logic (time, weather, command processing)
- test_flask_api.py: Tests for the Flask web API endpoints
- test_integration.py: End-to-end integration tests

Running Tests:
- Run all tests: python -m pytest tests/
- Run specific test file: python -m pytest tests/test_command_handlers.py
- Run with verbose output: python -m pytest tests/ -v
- Run with coverage: python -m pytest tests/ --cov=.

Note: These tests use mocking to avoid actual voice output, web browsing, and music control.
"""
