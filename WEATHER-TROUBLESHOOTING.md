# Troubleshooting Weather Functionality in Julie Julie

This document provides specific guidance for diagnosing and fixing issues with the weather functionality in Julie Julie.

## Current Implementation

The weather function in Julie Julie:
1. Extracts location information from the user's query
2. Makes an HTTP request to wttr.in (a text-based weather service)
3. Displays and speaks the weather information
4. Falls back to opening a weather website if the API call fails

## Testing the Weather Function

### Direct API Test

You can test the wttr.in service directly to see if it's responding:

```bash
curl "https://wttr.in/New York?format=3"
```

You should receive a simple text response like:
```
New York: ☀️ +72°F
```

### Command Line Test

Test the Julie Julie weather command through the API:

```bash
curl -X POST "http://127.0.0.1:58586/activate_listening" -d "text_command=what's the weather in New York"
```

### Debug Mode

Run Julie Julie in debug mode to see detailed logs:

```bash
bash run_debug.sh
```

Then try a weather command from the menu bar or through terminal_julie.py.

## Common Weather Function Issues

### 1. Location Extraction Problems

The function that extracts location from user queries might not be working correctly. Check the debug output for:

```
[COMMAND] Extracted location via regex: '...'
```

or

```
[COMMAND] Extracted location via split: '...'
```

If you don't see these messages, or if they show an incorrect location, the location extraction logic might be failing.

**Solution:** Try simplifying your weather requests to:
- "What's the weather in New York"
- "Weather in Chicago"

### 2. API Connection Issues

If Julie Julie can't connect to wttr.in, check these messages in the debug output:

```
DEBUG: Weather API error: ...
```

or

```
DEBUG: Request error: ...
```

**Solutions:**
- Check your internet connection
- Try a different location
- The wttr.in service might be temporarily down

### 3. Response Parsing Issues

If Julie Julie receives a response but doesn't speak it correctly, look for:

```
DEBUG: Weather data: ...
```

but no corresponding

```
DEBUG: Weather response: ...
```

**Solution:** The parsing logic might need adjustment. Try simple locations like major cities.

## Fixing the Weather Functionality

### Testing Specific Parts

1. **Test location extraction:**
   ```python
   command_lower = "what's the weather in new york"
   location_match = re.search(r"(?:weather |forecast )(?:in|for) ([a-zA-Z0-9 ]+)(?:$|[?])", command_lower)
   if location_match:
       location = location_match.group(1).strip()
       print(f"Extracted location: {location}")
   elif "in " in command_lower:
       location = command_lower.split("in ", 1)[1].strip()
       location = re.sub(r'[.?!,;:]$', '', location)
       print(f"Extracted location via split: {location}")
   ```

2. **Test the weather API directly:**
   ```python
   import requests
   location = "New York"
   weather_url = f"https://wttr.in/{location}?format=3"
   response = requests.get(weather_url, timeout=5)
   print(f"Status code: {response.status_code}")
   print(f"Response: {response.text}")
   ```

### Key Code Areas to Check

1. The regex pattern for extracting locations:
   ```python
   location_match = re.search(r"(?:weather |forecast )(?:in|for) ([a-zA-Z0-9 ]+)(?:$|[?])", command_lower)
   ```
   This might need adjustment to catch more patterns.

2. The weather URL construction:
   ```python
   weather_url = f"https://wttr.in/{location}?format=3"
   ```
   Make sure the URL is being constructed properly.

3. The response handling:
   ```python
   if response.status_code == 200:
       weather_text = response.text.strip()
       spoken_response = f"The current weather in {location} is {weather_text}."
   ```
   Check if the response is being parsed correctly.

## Logging Improvements

To add more detailed logging for weather functionality, you can modify the `handle_weather_command` function:

```python
def handle_weather_command(location=None):
    """Handle weather-related queries with real data."""
    # Added more logging
    logger.info(f"Weather command received. Raw location: {location}")
    
    # Default to Hartford, Arkansas if no location specified
    if not location:
        location = "Hartford, Arkansas"
        logger.info(f"No location specified, using default: {location}")
    else:
        logger.info(f"Using specified location: {location}")
    
    # Log the formatted location
    location_formatted = location.replace(' ', '+')
    logger.info(f"Formatted location for URL: {location_formatted}")
    
    # ... rest of the function
```

## Temporary Workaround

If the weather function isn't working reliably, you can modify the handler to default to opening a weather website:

```python
def handle_weather_command(location=None):
    """Handle weather-related queries with real data."""
    # Default to Hartford, Arkansas if no location specified
    if not location:
        location = "Hartford, Arkansas"
    
    # Always open a weather website for now
    return {
        "spoken_response": f"Opening weather information for {location}.",
        "opened_url": f"https://www.weather.com/weather/today/l/{location.replace(' ', '+')}",
        "additional_context": "Opening a weather website."
    }
```

This will ensure users get weather information while you fix the API integration.
