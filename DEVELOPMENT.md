# Julie Julie Development Guide

## Notes on this Unconventional Architecture

The Julie Julie architecture represents an unconventional approach to creating a voice assistant on macOS:

- **Non-Standard Integration:** This system combines macOS Voice Control, Shortcuts, AppleScript, and a Python Flask application in a way not commonly documented or officially supported.

- **Creative Workaround:** In the absence of official APIs for creating Siri-like assistants on macOS, this approach cobbles together several platform capabilities to achieve voice control.

- **Challenge Areas:** This architecture introduces several challenges, particularly around interference between Voice Control and the `say` command used for responses. See [VOICE-CONTROL-CHALLENGES.md](VOICE-CONTROL-CHALLENGES.md) for details.

- **Custom Pipeline:** The command flow essentially creates a custom voice assistant pipeline:
  `Voice Control → Shortcuts → AppleScript → HTTP → Flask → Command Processors`

- **Advantages:** Despite its unconventional nature, this approach offers benefits:
  - Leverages macOS's superior voice recognition
  - Uses native automation tools rather than requiring custom speech recognition
  - Creates a modular, loosely-coupled system
  - Achieves voice assistant functionality without complex native app development

This document provides information for developers who want to understand, modify, or extend Julie Julie.

## Project Structure

- `main.py` - The main entry point for the application
- `julie_julie_app.py` - Core application code including menu bar app, Flask server, and command handlers
- `terminal_julie.py` - A terminal-based testing interface
- `SendToJulieJulie.applescript`, `ShortcutJulieJulie.applescript`, `SimpleJulieJulie.applescript` - Example AppleScript files (note: currently not being used; AppleScript is directly embedded in the Shortcuts app)
- `run_debug.sh` - Bash script for running Julie Julie in debug mode
- `test_commands/` - Directory containing test commands
- `test_speech.py` - Script for testing speech recognition

## Architecture Overview

Julie Julie is structured around several key components:

1. **Menu Bar Interface** - Built with the `rumps` library, provides UI access
2. **Flask Web Server** - Handles HTTP requests for command processing
3. **Command Handlers** - Process different types of user requests
4. **Speech Recognition** - Converts voice to text using Google's API
5. **Text-to-Speech** - Uses macOS built-in 'say' command

### Command Flow

1. A command is received (via menu bar, HTTP, or voice)
2. `process_command_from_user()` parses the command
3. The appropriate handler function is called
4. The handler generates a response object
5. The response is spoken using the 'say' command
6. If applicable, a URL is opened in the default browser

## Adding New Command Types

To add a new command type, follow these steps:

1. Create a new handler function in `julie_julie_app.py`:

```python
def handle_new_command_type(parameter):
    """Handle a new command type."""
    # Process the command
    return {
        "spoken_response": "Your response here",
        "opened_url": None,  # or a URL to open
        "additional_context": None  # optional additional information
    }
```

2. Add pattern matching in `process_command_from_user()`:

```python
# New command type patterns
new_patterns = [
    r"pattern one (.*)",
    r"pattern two (.*)"
]
if any(re.search(pattern, command_lower) for pattern in new_patterns):
    logger.info("Matched new command type")
    # Extract any parameters if needed
    parameter = extract_parameter(command_lower)
    result = handle_new_command_type(parameter)
```

3. Add documentation for the new command type in the help function

## Understanding Command Handlers

Each command handler follows a consistent pattern:

1. Process the input (extract parameters, etc.)
2. Perform the core function (get time, fetch weather, etc.)
3. Return a response object with these keys:
   - `spoken_response`: What will be spoken to the user
   - `opened_url`: URL to open (or None)
   - `additional_context`: Optional additional information

For example, the time handler:

```python
def handle_time_command():
    now = datetime.now()
    return {
        "spoken_response": f"The current time is {now.strftime('%I:%M %p')}.",
        "opened_url": None,
        "additional_context": f"Today is {now.strftime('%A, %B %d, %Y')}."
    }
```

## Flask API Endpoints

Julie Julie exposes several HTTP endpoints:

- `GET /` - Status check endpoint
- `POST /activate_listening` - Trigger voice listening or process a command
- `POST /command` - Alternative endpoint for command processing

Both command endpoints accept a `text_command` parameter.

## Speech Recognition

The `perform_speech_to_text()` function:
1. Lists available microphones for debugging
2. Uses the `speech_recognition` library to capture audio
3. Sends the audio to Google's speech recognition API
4. Returns the recognized text or handles various errors

## Menu Bar App

The `JulieJulieRumpsApp` class:
1. Creates a menu bar icon with dropdown options
2. Starts the Flask server in a separate thread
3. Provides methods for handling menu item clicks
4. Includes quick command shortcuts and status information

## Debugging Tips

1. Use the debug script to see detailed output:
```bash
bash run_debug.sh
```

2. Check the log file for errors:
```bash
cat ~/Library/Logs/JulieJulie/julie_julie.log
```

3. Test API endpoints directly with curl:
```bash
curl -v -X POST "http://127.0.0.1:58586/activate_listening" -d "text_command=what time is it"
```

4. Use the terminal interface for testing without voice:
```bash
python terminal_julie.py
```

## Integration with Voice Control

Julie Julie integrates with macOS Voice Control via Apple Shortcuts:

1. A Voice Control command listens for "Julie Julie"
2. This triggers a Shortcut containing embedded AppleScript
3. The AppleScript receives the voice command as input, formats it, and sends it directly to Julie Julie's server
4. The script formats the request as a POST request with the text_command parameter
5. Julie Julie processes the command and responds

The AppleScript used in the Shortcut:

```applescript
on run {input, parameters}
    -- Just get the input and send it directly
    set serverURL to "http://127.0.0.1:58586/activate_listening"
    
    -- Convert input to text in the simplest way
    set userCommand to input as text
    
    -- Send command to server with minimal processing
    set curlResult to do shell script "curl -s -X POST " & serverURL & " -d 'text_command=" & userCommand & "'"
    
    -- Return result
    return "Sent to Julie Julie: " & userCommand
end run
```

This approach allows the voice command to be captured by macOS Voice Control and passed directly to Julie Julie without requiring a separate speech recognition step.

## Common Issues and Solutions

### Speech Recognition Issues

If speech recognition isn't working:
- Verify microphone permissions
- Check network connectivity (required for Google API)
- Install PyAudio: `pip install PyAudio`

### Menu Bar App Not Appearing

If the menu bar app doesn't appear:
- Check for Python exceptions in the debug output
- Make sure `rumps` is installed
- Verify you're running on macOS

### Flask Server Issues

If the HTTP server isn't responding:
- Check if port 58586 is already in use
- Look for server startup errors in the logs
- Verify Flask is installed: `pip install Flask`

## Future Development Roadmap

Planned enhancements:

1. **Local LLM Integration** - Connect to a local language model for more advanced NLP
2. **Conversational Memory** - Remember context from previous interactions
3. **Custom Activation Phrase** - Allow users to change the activation phrase
4. **Plugin System** - Enable third-party extensions 
5. **Custom Voice Settings** - Select different system voices
6. **Advanced Web Searches** - More sophisticated search capabilities
