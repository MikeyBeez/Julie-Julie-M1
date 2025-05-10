-- Simple Julie Julie activation script
-- This script sends an activation signal to Julie Julie's web server
-- The server will handle speech recognition

-- Set URL endpoint
set serverURL to "http://127.0.0.1:58586/activate_listening"

-- Execute the curl command to send activation signal
try
    do shell script "curl -s -X POST " & serverURL
    -- No return value needed for Voice Control
on error errMsg number errNum
    display dialog "Error activating Julie Julie: " & errMsg buttons {"OK"} default button "OK"
end try
