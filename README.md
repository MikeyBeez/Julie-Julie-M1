# Julie Julie

A macOS voice assistant that lives in your menu bar, providing quick access to time, weather, calculations, music control, web searches, and conversational AI via Ollama.

## Overview

Julie Julie is a voice-activated assistant for macOS that:
- Lives in your menu bar for easy access
- Responds to voice or text commands
- Gives spoken responses using macOS text-to-speech
- Opens relevant websites when needed
- Provides quick access to common tasks (time, weather, search)
- Integrates with Spotify, Apple Music, and YouTube
- Supports real-time streaming conversations via Ollama

You can interact with Julie Julie through:
1. Voice commands (triggered via macOS Voice Control)
2. Menu bar dropdown
3. HTTP API endpoints
4. Terminal interface for testing

## Current Status

- ✅ Time queries - fully working
- ✅ Weather queries - working with National Weather Service API
- ✅ Calculations - working with calculation handler
- ✅ Music control - Spotify and Apple Music integration
- ✅ Radio stations - Classical, Jazz, Rock, and NPR streaming
- ✅ Audio control - Speaker switching and device listing
- ✅ YouTube searches - fully implemented
- ✅ Visualizer commands - working
- ✅ Ollama integration - streaming AI conversations with real-time speech
- ✅ Opening websites - working
- ✅ **Text-to-Speech**: Google Cloud TTS with automatic fallback to macOS say
- ✅ **Ollama Auto-Start**: Automatically starts Ollama service when needed for AI conversations

## Installation

### Prerequisites

- macOS (required for menu bar integration and TTS)
- Python 3.10 or higher
- Required Python packages (see requirements.txt)
- macOS Voice Control enabled (for voice activation)

### Setup

1. Clone this repository
```bash
git clone https://github.com/yourusername/Julie-Julie-M1.git
cd Julie-Julie-M1
```

2. Set up a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Optional: Set up Google Cloud TTS (for better voice quality)
   - Create a Google Cloud project and enable the Text-to-Speech API
   - Download service account credentials JSON file
   - Set environment variable: `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"`
   - Or use gcloud: `gcloud auth application-default login`
   - Note: Julie Julie will automatically fall back to macOS `say` command if Google TTS isn't available

5. Configure Voice Control (for voice activation):
   - Open System Preferences → Accessibility → Voice Control
   - Enable Voice Control
   - Click "Commands" → "+"
   - Create a new command:
     - When I say: "Julie Julie"
     - Action: Run Shortcut → "Activate Julie Julie" (create this shortcut in step 5)

6. Create the "Activate Julie Julie" shortcut:
   - Open the Shortcuts app
   - Create a new shortcut named "Activate Julie Julie"
   - Add an "Ask for Text" action:
     - Set a custom prompt (e.g., "What would you like Julie Julie to do?")
     - Disable "Allow Multiline" to keep input focused on single commands
   - Add a "Run AppleScript" action
   - Paste the following AppleScript code:
     ```applescript
     on run {input, parameters}
         -- Get the input text
         set userCommand to input as text
         
         -- Set URL endpoint for sending commands  
         set serverURL to "http://127.0.0.1:58586/command"
         
         -- Execute the curl command to send the text command
         try
             set curlCommand to "curl -s -X POST " & serverURL & " -d 'text_command=" & userCommand & "'"
             set curlResult to do shell script curlCommand
             return "Sent to Julie Julie: " & userCommand
         on error errMsg number errNum
             return "Error: " & errMsg
         end try
     end run
     ```
   - Save the shortcut

   When triggered (via Voice Control saying "Julie Julie" or manually), this shortcut will:
   1. Show a text input dialog
   2. Send the typed command to Julie Julie's `/command` endpoint
   3. Julie Julie will process the command and provide spoken responses

## Usage

### Running Julie Julie

1. Activate the virtual environment
```bash
source .venv/bin/activate
```

2. Start Julie Julie
```bash
python main.py
```

For debugging:
```bash
bash run_debug.sh
```

Julie Julie will appear in your menu bar, ready to respond to commands.

### Important Note on Voice Activation

Julie Julie uses a text-based input system rather than direct speech recognition to avoid interference with Voice Control. The workflow is:

1. **Voice Control Activation**: Say "Julie Julie" to trigger the shortcut
2. **Text Input Dialog**: A dialog appears asking "What would you like Julie Julie to do?"
3. **Type Your Command**: Enter your command as text (multiline disabled for focus)
4. **Processing**: Julie Julie receives the command via the `/command` endpoint
5. **Response**: Julie Julie speaks the response using macOS text-to-speech

This approach avoids:
- Speech recognition conflicts with Voice Control
- Feedback loops from Julie Julie's spoken responses
- Complex microphone management issues

The macOS `say` command (used for Julie Julie's responses) can still sometimes be picked up by Voice Control, so you may need to say "Stop listening" after getting spoken responses.

See [VOICE-CONTROL-CHALLENGES.md](VOICE-CONTROL-CHALLENGES.md) for detailed information on these challenges and workarounds.

### Menu Bar Commands

Julie Julie appears in your menu bar with these options:
- **Enter Command...** - Type a command directly
- **Quick Commands** - Access common tasks (Time, Weather, YouTube, Help)
- **Status** - Check server status
- **Show Log** - View the application log file
- **About** - App information
- **Quit** - Exit the application

### Terminal Testing

For testing without voice activation:
```bash
python terminal_julie.py
```

This provides a simple terminal interface where you can type:
```
Julie Julie what time is it stop
```

### Advanced Features

#### AI Model Management

Julie Julie can manage multiple Ollama models and switch between them:

- **"List models"** - Shows all downloaded models and current selection
- **"Use [model name]"** - Switch to a specific model (e.g., "Use llama3", "Use codellama")
- **"Pull model"** - Download the currently selected model
- **"Ollama status"** - Check service status and current model

The system supports partial model name matching, so "Use llama" will match "llama3.2" if it's the only llama model available.

#### Text-to-Speech Options

Julie Julie supports both Google Cloud TTS (higher quality) and macOS say command (always available):

- **"Use Google voice"** - Switch to Google Cloud TTS
- **"Use local voice"** - Switch to macOS say command  
- **"TTS status"** - Check current TTS configuration
- **"Test voice"** - Test the current TTS system

### Command Examples

Julie Julie understands a variety of commands, including:

- **Time**: "What time is it?" or "What's the current time?"
- **Weather**: "What's the weather like?" or "What's the weather in San Francisco?"
- **Calculations**: "What's 15 times 23?" or "15% tip on $50"
- **Music & Radio**: "Spotify music", "Classical radio", "Jazz music", "NPR"
- **Audio Control**: "What speakers are available?", "Switch to Yamaha", "Use soundbar"
- **YouTube**: "YouTube cute cat videos" or "Play funny animals on YouTube"
- **Conversations**: "Tell me about quantum physics" or "Who is Marie Curie?"
- **Web Search**: "Search for chocolate chip cookie recipes"
- **Open Websites**: "Open github.com"
- **TTS Control**: "Use Google voice", "Switch to local voice", "TTS status", "Test voice"
- **Voice Control**: "Stop listening", "Start listening", "Voice Control status", "Enable auto manage"
- **Ollama Control**: "Start Ollama", "Stop Ollama", "Ollama status", "Enable auto start", "List models", "Use llama3"
- **Help**: "What can you do?" or "Help"

## Testing

Julie Julie includes a comprehensive test suite that tests the core functionality without requiring actual voice input/output.

### Running Tests

1. **Install test dependencies** (if not already installed):
```bash
pip install pytest pytest-cov pytest-mock
```

2. **Run all tests**:
```bash
# Using the test runner
python test_runner.py

# Or directly with pytest
python -m pytest tests/ -v
```

3. **Run specific test categories**:
```bash
# Unit tests only
python test_runner.py --unit

# Integration tests only
python test_runner.py --integration

# With coverage report
python test_runner.py --coverage
```

### Test Categories

- **Unit Tests**: Test individual command handlers (calculations, music, YouTube, etc.)
- **Core Logic Tests**: Test main application logic (time, weather, command processing)
- **API Tests**: Test Flask endpoints and HTTP communication
- **Integration Tests**: Test complete workflows from HTTP request to response

### Testing Strategy

The tests use **mocking** to avoid actual voice output, web browsing, and external API calls:
- Speech output (`say` commands) are mocked to prevent audio
- Web browser opening is mocked to prevent unwanted windows
- External APIs (weather, music) are mocked for consistent testing
- Ollama integration is mocked to avoid AI service dependency

See [TESTING.md](TESTING.md) for detailed testing documentation.

## Architecture

Julie Julie consists of several components:

1. **Menu Bar App** (using `rumps`): Provides a GUI interface in macOS
2. **Flask Web Server**: Handles HTTP requests including API endpoints
3. **Command Handlers**: Process different types of user requests
4. **TTS Manager**: Handles Google Cloud TTS with automatic fallback to macOS say
5. **Speech-to-Text**: Converts audio to text using Google's speech recognition (when needed)

The application flow is:
1. User makes a request (via voice, menu, or API)
2. The request is processed to determine the command type
3. The appropriate handler processes the command
4. A response is both spoken and displayed or a website is opened

## API

Julie Julie runs a local HTTP server on port 58586. You can interact with it programmatically:

- **Check server status**:
  ```bash
  curl http://127.0.0.1:58586/
  ```

- **Send a text command**:
  ```bash
  curl -X POST http://127.0.0.1:58586/command -d "text_command=What time is it?"
  ```

Note: The primary interface is the `/command` endpoint which is used by the Shortcuts integration. Julie Julie processes text commands and responds with spoken output and/or opens relevant websites.

## Troubleshooting

If Julie Julie isn't working as expected:

1. Check the logs at `~/Library/Logs/JulieJulie/julie_julie.log`
2. Run the debug script: `bash run_debug.sh`
3. Test API endpoints directly with curl commands
4. Verify your microphone is working properly
5. Ensure all dependencies are installed
6. Check that port 58586 isn't being used by another application

### Common Issues

- **Shortcut not triggering**: Ensure Voice Control is enabled and the "Julie Julie" command is properly configured
- **Text dialog not appearing**: Check that the Shortcuts app has necessary permissions
- **Commands not processed**: Verify Julie Julie is running and the Flask server is active on port 58586
- **No spoken responses**: Check that macOS text-to-speech (`say` command) is working
- **Ollama integration issues**: Ensure Ollama is running locally with the deepseek-r1 model available

## Future Enhancements

- Integration with local language models
- Custom voice and speech settings
- Calendar integration
- Local document search
- More sophisticated conversational context
- Additional command types

## License

[MIT License](LICENSE)
