# Julie Julie Setup Guide

This guide provides detailed instructions for setting up Julie Julie on your macOS system.

## System Requirements

- macOS 10.15 (Catalina) or newer
- Python 3.10 or newer
- At least 100MB of disk space
- Active internet connection (for speech recognition)
- Microphone access permissions

## Step 1: Install Python

Julie Julie requires Python 3.10 or newer. To check your Python version:

```bash
python3 --version
```

If you need to install or update Python, we recommend using [Homebrew](https://brew.sh/):

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

## Step 2: Clone the Repository

Clone the Julie Julie repository to your local machine:

```bash
git clone https://github.com/yourusername/Julie-Julie-M1.git
cd Julie-Julie-M1
```

## Step 3: Set Up a Virtual Environment

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your command prompt should now show the virtual environment name, like `(.venv)`.

## Step 4: Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `rumps` - For macOS menu bar integration
- `Flask` - For the web server
- `SpeechRecognition` - For speech-to-text functionality
- `PyAudio` - For audio input processing
- `requests` - For HTTP requests

If you encounter problems with PyAudio installation, you may need to install portaudio first:

```bash
brew install portaudio
pip install pyaudio
```

## Step 5: Configure macOS Voice Control

To use voice activation with Julie Julie:

1. Open System Preferences
2. Go to Accessibility → Voice Control
3. Check "Enable Voice Control"
4. Click "Commands"
5. Click the "+" button to add a new command
6. Configure as follows:
   - When I say: "Julie Julie"
   - While using: Any Application
   - Action: Run Shortcut...
   - Select "Activate Julie Julie" (you'll create this shortcut in Step 6)
7. Click "Save"

## Step 6: Create Apple Shortcut

1. Open the Shortcuts app (comes with macOS)
2. Click the "+" button to create a new shortcut
3. Name it "Activate Julie Julie"
4. Add an action by clicking the "+" button
5. Search for "Run AppleScript" and add it
6. Paste the following AppleScript code directly into the action:
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
   
   This script takes an input (the voice command), converts it to text, and forwards it directly to Julie Julie.
7. Click "Done" to save the shortcut

## Step 7: Grant Required Permissions

Julie Julie needs several permissions to function properly:

1. **Microphone Access:**
   - Open System Preferences → Security & Privacy → Microphone
   - Ensure Terminal and Python are allowed

2. **Automation Permissions:**
   - When prompted, allow Shortcuts to control your computer
   - Allow Terminal to automate System Events if prompted

## Step 8: Test Basic Functionality

1. Start Julie Julie:
   ```bash
   cd /path/to/Julie-Julie-M1
   source .venv/bin/activate
   python main.py
   ```

2. The Julie Julie icon should appear in your menu bar

3. Test with the menu bar:
   - Click the Julie Julie icon
   - Select "Enter Command..."
   - Type "What time is it?"
   - Click "Send"
   - You should hear the current time spoken

4. Test with terminal interface:
   ```bash
   python terminal_julie.py
   ```
   Then type:
   ```
   Julie Julie what time is it stop
   ```

## Step 9: Test Voice Activation

1. Make sure Julie Julie is running
2. Make sure Voice Control is enabled
3. Say "Julie Julie" clearly
4. Wait for the listening prompt
5. Say a command like "What time is it?"
6. Julie Julie should respond with the current time

## Step 10: Configure Startup (Optional)

To have Julie Julie start automatically when you log in:

1. Open System Preferences → Users & Groups
2. Select your user account
3. Click the "Login Items" tab
4. Click the "+" button
5. Navigate to your virtual environment and select the Python executable
6. Add a script or app that launches Julie Julie

Alternatively, create a simple application with Automator:
1. Open Automator
2. Create a new Application
3. Add a "Run Shell Script" action
4. Enter:
   ```bash
   cd /path/to/Julie-Julie-M1
   source .venv/bin/activate
   python main.py
   ```
5. Save the application
6. Add this application to your Login Items

## Troubleshooting

### Menu Bar Icon Not Appearing
- Make sure `rumps` is installed correctly
- Check for error messages in the terminal
- Try running in debug mode: `bash run_debug.sh`

### Voice Recognition Not Working
- Verify microphone permissions in System Preferences
- Check internet connection (required for Google's speech recognition)
- Test your microphone with another application
- Try installing a different version of PyAudio

### Shortcut Not Activating Julie Julie
- Check the AppleScript code in your Shortcut
- Verify the Flask server is running (port 58586)
- Try running just the curl command directly from Terminal to test:
  ```bash
  curl -X POST http://127.0.0.1:58586/activate_listening
  ```

### Commands Not Being Recognized
- Check the log file at `~/Library/Logs/JulieJulie/julie_julie.log`
- Test with simple commands first (e.g., "what time is it")
- Try entering commands directly via the menu bar

## Uninstalling

To completely remove Julie Julie:

1. Quit the application if it's running
2. Remove the Voice Control command
3. Delete the Shortcut
4. Delete the repository directory
5. Remove any Login Items you added

## Getting Help

If you encounter issues not covered by this guide:
1. Check the log file for specific error messages
2. Refer to the DEBUG-INSTRUCTIONS.md file for detailed debugging steps
3. Run the application in debug mode for more information
