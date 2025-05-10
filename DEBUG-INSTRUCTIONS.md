# Julie Julie Debug Instructions

This file contains instructions for debugging Julie Julie when things go wrong.

## Running Julie Julie with Debugging Output

To run Julie Julie with more detailed debug output, use:

```bash
cd /Users/bard/Code/Julie-Julie-M1
PYTHONUNBUFFERED=1 python julie_julie_app.py 2>&1 | tee debug.log
```

This will show the output in the terminal and also save it to debug.log for later review.

## Testing Weather Functionality Directly

You can test the weather functionality directly without using Voice Control or shortcuts:

```bash
curl -v -X POST "http://127.0.0.1:58586/activate_listening" -d "text_command=what's the weather"
```

This will send a direct request to Julie Julie and show both the request and response details.

To test with a specific location:

```bash
curl -v -X POST "http://127.0.0.1:58586/activate_listening" -d "text_command=what's the weather in New York"
```

## Checking Form Data Transmission

If you're having issues with shortcuts not sending the command properly, you can check how data is being sent:

```bash
curl -v -X POST "http://127.0.0.1:58586/activate_listening" -d "text_command=test message" -H "Content-Type: application/x-www-form-urlencoded"
```

## Testing Other Commands

Time:
```bash
curl -X POST "http://127.0.0.1:58586/activate_listening" -d "text_command=what time is it"
```

Open a website:
```bash
curl -X POST "http://127.0.0.1:58586/activate_listening" -d "text_command=open youtube.com"
```

Help:
```bash
curl -X POST "http://127.0.0.1:58586/activate_listening" -d "text_command=help"
```

## Troubleshooting

If you're encountering issues:

1. Check the logs: `~/Library/Logs/JulieJulie/julie_julie.log`
2. Make sure the server is running: `curl http://127.0.0.1:58586/`
3. Try running the debug version with terminal output
4. Test commands directly with curl to isolate issues
5. Check that Shortcuts is sending data in the right format

Remember that the weather functionality now uses a simple text-based response format from wttr.in, which should be more reliable than trying to parse complex JSON.
