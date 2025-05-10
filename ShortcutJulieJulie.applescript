on run {input, parameters}
	-- This is a simplified script specifically for running from Shortcuts
	
	-- Log activation
	log "Julie Julie Shortcut - Sending activation signal"
	
	-- Set URL endpoint
	set serverURL to "http://127.0.0.1:58586/activate_listening"
	
	-- Execute the curl command to send activation signal
	try
		set curlCommand to "curl -s -X POST " & serverURL
		set curlResult to do shell script curlCommand
		log "Curl result: " & curlResult
		return "Activated Julie Julie"
	on error errMsg number errNum
		log "Error activating Julie Julie: " & errMsg & " (Number: " & errNum & ")"
		return "Error: " & errMsg
	end try
end run
