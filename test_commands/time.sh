#!/bin/bash
# This script sends the "what time is it" command to Julie Julie
curl -s -X POST http://127.0.0.1:58586/activate_listening -d "text_command=what time is it"
