# Julie Julie

A macOS voice assistant that lives in your menu bar, providing quick access to time, weather, web searches, and more.

## Overview

Julie Julie is a voice-activated assistant for macOS that:
- Lives in your menu bar for easy access
- Responds to voice or text commands
- Gives spoken responses using macOS text-to-speech
- Opens relevant websites when needed
- Provides quick access to common tasks (time, weather, search)

You can interact with Julie Julie through:
1. Voice commands (triggered via macOS Voice Control)
2. Menu bar dropdown
3. HTTP API endpoints
4. Terminal interface for testing

## Current Status

- ✅ Time queries - fully working
- ⚠️ Weather queries - partially implemented
- ⚠️ Web search - partially implemented
- ⚠️ Wikipedia - partially implemented
- ⚠️ YouTube - partially implemented
- ✅ Opening websites - working

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

4. Configure Voice Control (for voice activation):
   - Open System Preferences → Accessibility → Voice Control
   - Enable Voice Control
   - Click "Commands" → "+"
   - Create a new command:
     - When I say: "Julie Julie"
     - Action: Run Shortcut → "Activate Julie Julie" (create this shortcut in step 5)

5. Create the "Activate Julie Julie" shortcut:
   - Open the Shortcuts app
   - Create a new shortcut named "Activate Julie Julie"
   - Add a "Run AppleScript" action
   - Paste the following AppleScript code:
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
   - Save the shortcut

   When using Voice Control, this shortcut will receive the voice command and forward it to Julie Julie.

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

Using Voice Control with Julie Julie can create some interference challenges. The macOS `say` command (used for Julie Julie's responses) can sometimes be picked up by Voice Control, creating feedback loops.

Some tips to avoid issues:
- Consider using Voice Control in "Commands Only" mode
- Close the Shortcuts app before testing Julie Julie
- You may need to say "Stop listening" before getting spoken responses

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

### Command Examples

Julie Julie understands a variety of commands, including:

- **Time**: "What time is it?" or "What's the current time?"
- **Weather**: "What's the weather like?" or "What's the weather in San Francisco?"
- **Web Search**: "Search for chocolate chip cookie recipes"
- **Information**: "Tell me about quantum physics" or "Who is Marie Curie?"
- **Open Websites**: "Open github.com"
- **YouTube**: "YouTube cute cat videos" or "Play funny animals on YouTube"
- **Help**: "What can you do?" or "Help"

## Architecture

Julie Julie consists of several components:

1. **Menu Bar App** (using `rumps`): Provides a GUI interface in macOS
2. **Flask Web Server**: Handles HTTP requests including API endpoints
3. **Command Handlers**: Process different types of user requests
4. **Speech-to-Text**: Converts audio to text using Google's speech recognition
5. **Text-to-Speech**: Uses macOS built-in 'say' command

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

- **Activate voice listening**:
  ```bash
  curl -X POST http://127.0.0.1:58586/activate_listening
  ```

- **Send a text command**:
  ```bash
  curl -X POST http://127.0.0.1:58586/activate_listening -d "text_command=What time is it?"
  ```
  or
  ```bash
  curl -X POST http://127.0.0.1:58586/command -d "text_command=What time is it?"
  ```

## Troubleshooting

If Julie Julie isn't working as expected:

1. Check the logs at `~/Library/Logs/JulieJulie/julie_julie.log`
2. Run the debug script: `bash run_debug.sh`
3. Test API endpoints directly with curl commands
4. Verify your microphone is working properly
5. Ensure all dependencies are installed
6. Check that port 58586 isn't being used by another application

### Common Issues

- **Missing speech_recognition or PyAudio**: Run `pip install SpeechRecognition PyAudio`
- **Authentication issues with Google Speech API**: Check your network connection
- **Weather API not working**: Check connection to wttr.in service

## Future Enhancements

- Integration with local language models
- Custom voice and speech settings
- Calendar integration
- Local document search
- More sophisticated conversational context
- Additional command types

## License

[MIT License](LICENSE)
