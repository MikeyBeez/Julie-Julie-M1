on run {input, parameters}
	-- This script sends dictated text to Julie Julie
	
	-- Get the input text (from "Get Text from Input" action)
	set userCommand to input as text
	
	-- Log the command
	log "Julie Julie Shortcut - Sending command: " & userCommand
	
	-- Set URL endpoint for sending commands
	set serverURL to "http://127.0.0.1:58586/process_command"
	
	-- Execute the curl command to send the text command
	try
		set curlCommand to "curl -s -X POST " & serverURL & " -d 'command=" & userCommand & "'"
		set curlResult to do shell script curlCommand
		log "Curl result: " & curlResult
		return "Sent to Julie Julie: " & userCommand
	on error errMsg number errNum
		log "Error sending command to Julie Julie: " & errMsg & " (Number: " & errNum & ")"
		return "Error: " & errMsg
	end try
end run
