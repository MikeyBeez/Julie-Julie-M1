on run {input, parameters}
    -- Get the input text from the user
    set userCommand to input as text
    
    -- Turn off Voice Control listening using the toggle command
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
        
        -- Check if command was successful
        if curlResult contains "\"status\":\"success\"" then
            -- Command sent successfully, now wait for response to complete
            
            -- For simple commands (time, weather, calculations), 2-3 seconds is enough
            -- For AI conversations, we might need longer
            if userCommand contains "time" or userCommand contains "weather" or userCommand contains "calculate" or userCommand contains "%" then
                -- Quick response commands
                delay 2.5
            else
                -- Potentially longer AI responses or complex commands
                delay 4
            end if
            
            -- Check if Julie Julie is still active by trying to ping the server
            try
                set statusCommand to "curl -s " & serverURL & "/"
                set statusResult to do shell script statusCommand
                -- If we get a response, Julie Julie is still running
            on error
                -- If server doesn't respond, add extra delay
                delay 1
            end try
            
        else
            -- Command failed, shorter delay
            delay 0.5
        end if
        
    on error errMsg number errNum
        -- If curl fails, still wait a moment before restarting
        delay 1
    end try
    
    -- Always turn Voice Control listening back on
    tell application "System Events"
        keystroke "x" using {command down, option down}
    end tell
    
    -- Return status
    return "Julie Julie command completed: " & userCommand
end run
