-- Activate Julie Julie voice listening mode
-- This script sends an activation signal to Julie Julie's web server
-- It doesn't prompt for a command, as the command will be captured by STT

-- Log activation
log "Julie Julie AppleScript - Sending activation signal"

-- Set URL endpoint
set serverURL to "http://127.0.0.1:58586/activate_listening"

-- Set curl command
set curlCommand to "curl -s -X POST " & serverURL

-- Log command to execute
log "Executing curl command: " & curlCommand
log serverURL

try
    -- Execute command and get result
    set curlResult to do shell script curlCommand
    log "Curl result: " & curlResult
on error errMsg number errNum
    -- Handle errors
    log "Error sending command: " & errMsg & " (Number: " & errNum & ")"
    display dialog "Julie Julie couldn't process that. Error: " & errMsg buttons {"OK"} default button "OK"
end try
