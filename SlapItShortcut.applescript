on run {input, parameters}
    -- Get the input text from the user
    set userCommand to input as text
    
    -- First, turn off Voice Control listening
    tell application "System Events"
        keystroke "x" using {command down, option down}
    end tell
    
    -- Small delay to ensure Voice Control is off
    delay 0.2
    
    -- Set URL endpoint for sending commands  
    set serverURL to "http://127.0.0.1:58586/command"
    
    -- Execute the curl command to send the text command
    try
        set curlCommand to "curl -s -X POST " & serverURL & " -d 'text_command=" & userCommand & "'"
        set curlResult to do shell script curlCommand
        
        -- Parse the response to check if it was successful
        if curlResult contains "\"status\":\"success\"" then
            -- Command was sent successfully
            
            -- Wait for Julie Julie to finish responding
            -- We'll wait a bit longer to ensure all speech is complete
            delay 3
            
            -- Turn Voice Control listening back on
            tell application "System Events"
                keystroke "x" using {command down, option down}
            end tell
            
            return "Command sent to Julie Julie: " & userCommand
        else
            -- Command failed, turn listening back on immediately
            tell application "System Events"
                keystroke "x" using {command down, option down}
            end tell
            return "Error sending command to Julie Julie"
        end if
        
    on error errMsg number errNum
        -- If there's an error, make sure to turn listening back on
        tell application "System Events"
            keystroke "x" using {command down, option down}
        end tell
        return "Error: " & errMsg
    end try
end run
