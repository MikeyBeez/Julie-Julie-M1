# "Slap It" Voice Control Setup Guide

This guide shows you how to set up the "slap it" command that properly manages Voice Control to prevent speech feedback.

## Why "Slap It"?

The problem with "enter" is that Voice Control stays active after processing the command, so it picks up Julie Julie's speech responses and converts them back to text. The "slap it" command solves this by:

1. **Turning off Voice Control** before sending the command
2. **Sending the command** to Julie Julie  
3. **Waiting for the response** to complete
4. **Turning Voice Control back on** when done

## Setup Instructions

### Step 1: Create the Voice Control Command

1. Open **System Preferences** → **Accessibility** → **Voice Control**
2. Click **Commands** → **+** (Add new command)
3. Create a new command:
   - **When I say**: "slap it"
   - **Action**: Run Shortcut → "Julie Julie Slap It" (you'll create this next)

### Step 2: Create the Shortcut

1. Open the **Shortcuts** app
2. Create a new shortcut named **"Julie Julie Slap It"**
3. Add an **"Ask for Text"** action:
   - Set prompt: "What would you like Julie Julie to do?"
   - **Disable "Allow Multiline"** 
4. Add a **"Run AppleScript"** action
5. Paste this AppleScript code:

```applescript
on run {input, parameters}
    -- Get the input text from the user
    set userCommand to input as text
    
    -- Turn off Voice Control listening
    tell application "System Events"
        keystroke "x" using {command down, option down}
    end tell
    
    -- Small delay to ensure Voice Control is off
    delay 0.3
    
    -- Set URL endpoint for sending commands  
    set serverURL to "http://127.0.0.1:58586/command"
    
    try
        -- Send the command to Julie Julie
        set curlCommand to "curl -s -X POST " & serverURL & " -d 'text_command=" & userCommand & "'"
        set curlResult to do shell script curlCommand
        
        -- Wait for response to complete based on command type
        if userCommand contains "time" or userCommand contains "weather" or userCommand contains "calculate" or userCommand contains "%" then
            -- Quick response commands
            delay 2.5
        else
            -- Potentially longer AI responses
            delay 4
        end if
        
    on error errMsg number errNum
        -- If curl fails, still wait a moment
        delay 1
    end try
    
    -- Always turn Voice Control listening back on
    tell application "System Events"
        keystroke "x" using {command down, option down}
    end tell
    
    return "Julie Julie command completed: " & userCommand
end run
```

6. Save the shortcut

## Usage

### Instead of saying "Julie Julie" → typing command → "enter":

1. Say **"slap it"**
2. Type your command in the dialog
3. Click **Done** or press **Return**
4. Julie Julie will respond without Voice Control interference
5. Voice Control automatically turns back on when done

### Examples:
- "slap it" → "what time is it" → **Done**
- "slap it" → "why is the sky blue" → **Done**  
- "slap it" → "list models" → **Done**

## Benefits

✅ **No more speech echo** - Voice Control won't convert Julie Julie's responses to text  
✅ **Automatic management** - Voice Control turns off and on automatically  
✅ **Clean terminal** - No stray text fragments in your output  
✅ **Smart timing** - Different delays for quick vs. long responses  
✅ **Error handling** - Voice Control restarts even if something goes wrong  

## Troubleshooting

**If Voice Control doesn't turn off/on:**
- Make sure the keyboard shortcut `Cmd+Option+X` is set for Voice Control toggle
- Check System Preferences → Accessibility → Voice Control → Commands

**If commands don't reach Julie Julie:**
- Verify Julie Julie is running on port 58586
- Test with: `curl http://127.0.0.1:58586/`

**If timing is wrong:**
- Adjust the delay values in the AppleScript
- Shorter delays for quick commands, longer for AI conversations

## Alternative Versions

The repository includes two AppleScript files:

1. **`SlapItShortcut.applescript`** - Simple version with fixed delays
2. **`SlapItShortcutSmart.applescript`** - Smart version with adaptive timing

You can experiment with both to see which works better for your usage patterns.
