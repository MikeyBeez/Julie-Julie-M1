# Contributing to Julie Julie

Thank you for your interest in contributing to Julie Julie! This document provides guidelines and information for contributors.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see SETUP-GUIDE.md)
4. Create a new branch for your changes

## Code Structure

Julie Julie follows a modular structure:

- `main.py` - Entry point
- `julie_julie_app.py` - Core application code
- Supporting scripts and tools in the root directory
- Documentation in markdown files

## Development Environment

We recommend using a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For development, run Julie Julie in debug mode:

```bash
bash run_debug.sh
```

## Coding Guidelines

### Python Style

- Follow PEP 8 guidelines
- Use descriptive variable and function names
- Add docstrings to all functions and classes
- Include type hints where possible
- Keep functions focused on a single responsibility

### Code Example

```python
def handle_new_feature(parameter: str) -> dict:
    """
    Handle a new feature in Julie Julie.
    
    Args:
        parameter: The input parameter for the feature
        
    Returns:
        A dictionary with response information
    """
    # Implementation
    return {
        "spoken_response": "Response text",
        "opened_url": None,
        "additional_context": "Additional information"
    }
```

## Adding Features

To add a new command type:

1. Create a handler function in `julie_julie_app.py`
2. Add pattern matching in the `process_command_from_user()` function
3. Update the help command to document your feature
4. Add tests for your feature
5. Update documentation as needed

## Testing

Julie Julie doesn't currently have automated tests, but you should manually test:

1. Basic functionality through the menu bar interface
2. API endpoints with curl or a similar tool
3. Voice recognition (if applicable)
4. Edge cases and error conditions

## Pull Request Process

1. Update documentation to reflect your changes
2. Test your changes thoroughly
3. Submit a PR with a clear description of the changes and their purpose
4. Be responsive to feedback and requests for changes

## Features to Work On

Here are some areas where Julie Julie needs improvement:

1. **Weather Integration**
   - Fix and improve the current wttr.in integration
   - Add more weather data points (forecast, humidity, etc.)
   - Support more location formats

2. **Web Search Enhancement**
   - Improve search result processing
   - Add support for different search engines
   - Implement more structured search results

3. **UI Improvements**
   - Add a settings interface
   - Improve the menu bar interface
   - Add visual feedback during operations

4. **Voice Recognition**
   - Enhance speech recognition accuracy
   - Add support for custom activation phrases
   - Implement offline speech recognition options

5. **Additional Commands**
   - Calendar integration
   - Reminders
   - Notes
   - Calculator functions
   - Timer and alarms

## Reporting Bugs

When reporting bugs, please include:

1. What you were trying to do
2. The exact steps to reproduce the issue
3. What you expected to happen
4. What actually happened
5. Logs from `~/Library/Logs/JulieJulie/julie_julie.log`
6. Your environment details (macOS version, Python version)

## Communication

For questions, suggestions, or discussions:

- Open an issue on GitHub
- Add comments to relevant pull requests
- Tag issues with appropriate labels

## Code of Conduct

- Be respectful and inclusive in your language and interactions
- Focus feedback on code and technical matters, not individuals
- Help create a positive environment for all contributors
- Accept constructive criticism gracefully

Thank you for contributing to Julie Julie!
