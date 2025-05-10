import rumps
import threading
import logging
import json
import os
import sys
import time
import re
from flask import Flask, request, jsonify
import webbrowser
import subprocess
from datetime import datetime
import requests

# --- Configuration ---
APP_NAME = "Julie Julie"
APP_VERSION = "0.3.0"  # Bumped version number for new features
APP_ICON = None  # Set to None to use default icon for now, or "icon.icns" if you have one
FLASK_PORT = 58586  # Unique port for Julie Julie's internal server
LOG_FILE = os.path.expanduser("~/Library/Logs/JulieJulie/julie_julie.log")

# --- Setup Logging ---
def setup_logging():
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging to both file and console with more detail
    logging.basicConfig(
        level=logging.DEBUG,  # Changed from INFO to DEBUG for more verbose logging
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Print a header to the console
    logger = logging.getLogger('julie_julie')
    print("=" * 80)
    print(f"Starting {APP_NAME} v{APP_VERSION} - Debug Mode")
    print(f"Log file: {LOG_FILE}")
    print("=" * 80)
    
    return logger

logger = setup_logging()

# --- Command Handlers ---
def handle_time_command():
    """Handle time-related queries."""
    now = datetime.now()
    return {
        "spoken_response": f"The current time is {now.strftime('%I:%M %p')}.",
        "opened_url": None,
        "additional_context": f"Today is {now.strftime('%A, %B %d, %Y')}."
    }

def handle_weather_command(location=None):
    """Handle weather-related queries with real data."""
    # Default to Hartford, Arkansas if no location specified
    if not location:
        location = "Hartford, Arkansas"
        logger.info(f"No location specified, using default: {location}")
        print(f"DEBUG: No location specified, using default: {location}")
    else:
        print(f"DEBUG: Using specified location: {location}")
    
    try:
        # We'll use a simple API that doesn't require registration
        logger.info(f"Fetching weather data for {location}")
        print(f"DEBUG: Fetching weather data for {location}")
        
        # Create a simple URL for weather information
        weather_url = f"https://wttr.in/{location}?format=3"  # Format 3 gives a single line forecast
        print(f"DEBUG: Weather URL: {weather_url}")
        
        # Make the request with proper error handling
        try:
            print(f"DEBUG: Sending request to weather API...")
            response = requests.get(weather_url, timeout=5)
            logger.info(f"Weather API response status: {response.status_code}")
            print(f"DEBUG: Weather API response status: {response.status_code}")
            
            if response.status_code == 200:
                # This format returns a simple text response, not JSON
                weather_text = response.text.strip()
                logger.info(f"Weather data: {weather_text}")
                print(f"DEBUG: Weather data: {weather_text}")
                
                # Create a nice spoken response
                spoken_response = f"The current weather in {location} is {weather_text}."
                print(f"DEBUG: Weather response: {spoken_response}")
                
                return {
                    "spoken_response": spoken_response,
                    "opened_url": None,
                    "additional_context": "Data provided by wttr.in."
                }
            else:
                logger.error(f"Weather API error: {response.status_code}")
                print(f"DEBUG: Weather API error: {response.status_code}")
                # Fall back to opening a weather website
                return {
                    "spoken_response": f"I couldn't get detailed weather for {location} right now.",
                    "opened_url": f"https://www.weather.com/weather/today/l/{location.replace(' ', '+')}",
                    "additional_context": "Opening a weather website instead."
                }
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            print(f"DEBUG: Request error: {e}")
            return {
                "spoken_response": f"I'm having trouble connecting to the weather service for {location}.",
                "opened_url": "https://weather.com",
                "additional_context": "Opening a weather website instead."
            }
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        print(f"DEBUG: Error fetching weather: {e}")
        # Open a weather website as fallback
        return {
            "spoken_response": f"I'm sorry, I couldn't fetch the weather information for {location}.",
            "opened_url": "https://weather.com",
            "additional_context": "There was an error with the weather service."
        }

def handle_search_command(query):
    """Handle search queries."""
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    return {
        "spoken_response": f"I've opened search results for {query}.",
        "opened_url": search_url,
        "additional_context": None
    }

def handle_wiki_command(topic):
    """Handle information queries via Wikipedia."""
    # For a basic implementation, just search Wikipedia
    wiki_url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
    return {
        "spoken_response": f"I've opened the Wikipedia page for {topic}.",
        "opened_url": wiki_url,
        "additional_context": None
    }

def handle_youtube_command(query):
    """Handle YouTube video search/playback."""
    youtube_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    return {
        "spoken_response": f"I've opened YouTube results for {query}.",
        "opened_url": youtube_url,
        "additional_context": None
    }

def handle_help_command():
    """Handle help requests."""
    help_text = """
    I can help you with:
    - Telling the time ("What time is it?")
    - Weather information ("What's the weather like?")
    - Web searches ("Search for...")
    - Wikipedia lookups ("Tell me about...")
    - Opening websites ("Open...")
    - YouTube searches ("YouTube...")
    """
    return {
        "spoken_response": "I can help you with time, weather, searches, YouTube, and opening websites. Ask me 'What can you do?' for more details.",
        "opened_url": None,
        "additional_context": help_text
    }

def handle_open_website_command(website):
    """Handle requests to open websites."""
    # Basic validation and URL formatting
    if not website.startswith(('http://', 'https://')):
        if '.' not in website:
            website = f"https://www.{website}.com"
        else:
            website = f"https://{website}"
    
    return {
        "spoken_response": f"Opening {website}",
        "opened_url": website,
        "additional_context": None
    }

# --- Core Application Logic ---
def process_command_from_user(text_command):
    """Process user commands and route to appropriate handlers."""
    if not text_command:
        logger.warning("Received empty command")
        print("[COMMAND] Error: Empty command received")
        return {
            "spoken_response": "I didn't receive any command. Please try again.",
            "opened_url": None,
            "additional_context": None
        }
    
    logger.info(f"Processing command: {text_command}")
    print(f"\n[COMMAND] Processing command: '{text_command}'")
    
    # Convert to lowercase for easier matching
    command_lower = text_command.lower().strip()
    print(f"[COMMAND] Normalized command: '{command_lower}'")
    
    # Improved command detection with better pattern matching
    result = None
    
    # Time-related commands
    time_patterns = [
        r"what(?:'s| is) the time",
        r"what time is it",
        r"current time",
        r"time now",
        r"^time$"
    ]
    if any(re.search(pattern, command_lower) for pattern in time_patterns):
        logger.info("Matched time command")
        print("[COMMAND] Matched time command")
        result = handle_time_command()
    
    # Weather-related commands
    weather_patterns = [
        r"what(?:'s| is) the weather",
        r"weather (?:like |in |forecast |now)",
        r"weather$",
        r"forecast",
        r"temperature"
    ]
    if any(re.search(pattern, command_lower) for pattern in weather_patterns):
        logger.info("Matched weather command")
        print("[COMMAND] Matched weather command")
        
        # Extract location if provided
        location = None
        location_match = re.search(r"(?:weather |forecast )(?:in|for) ([a-zA-Z0-9 ]+)(?:$|[?])", command_lower)
        if location_match:
            location = location_match.group(1).strip()
            print(f"[COMMAND] Extracted location via regex: '{location}'")
        elif "in " in command_lower:
            # Fallback to simpler extraction
            location = command_lower.split("in ", 1)[1].strip()
            # Remove any trailing punctuation
            location = re.sub(r'[.?!,;:]$', '', location)
            print(f"[COMMAND] Extracted location via split: '{location}'")
        else:
            print(f"[COMMAND] Using default location")
            
        logger.info(f"Extracted location: {location}")
        result = handle_weather_command(location)
    
    # Search commands
    if (command_lower.startswith(("search", "look up", "google", "find")) or 
        "search for" in command_lower or "look up" in command_lower):
        logger.info("Matched search command")
        
        # Extract the search query
        query = text_command
        for prefix in ["search for", "search", "look up", "google", "find"]:
            if command_lower.startswith(prefix):
                query = text_command[len(prefix):].strip()
                break
            elif prefix in command_lower:
                parts = command_lower.split(prefix, 1)
                if len(parts) > 1:
                    query = parts[1].strip()
                break
        
        logger.info(f"Extracted search query: {query}")
        result = handle_search_command(query)
    
    # YouTube commands
    youtube_patterns = [
        r"youtube (.*)",
        r"play (.*) on youtube",
        r"search youtube for (.*)",
        r"watch (.*) on youtube"
    ]
    for pattern in youtube_patterns:
        match = re.search(pattern, command_lower)
        if match:
            logger.info("Matched YouTube command")
            query = match.group(1).strip()
            logger.info(f"Extracted YouTube query: {query}")
            result = handle_youtube_command(query)
            break
    
    # Wikipedia/information commands
    info_patterns = [
        r"tell me about (.*)",
        r"who is (.*)",
        r"what is (.*)",
        r"define (.*)"
    ]
    if not result:  # Only check if no other command matched
        for pattern in info_patterns:
            match = re.search(pattern, command_lower)
            if match:
                logger.info("Matched information command")
                topic = match.group(1).strip()
                # Remove any trailing punctuation
                topic = re.sub(r'[.?!,;:]$', '', topic)
                logger.info(f"Extracted topic: {topic}")
                result = handle_wiki_command(topic)
                break
    
    # Open website commands
    if command_lower.startswith("open "):
        logger.info("Matched open website command")
        website = text_command[5:].strip()
        logger.info(f"Extracted website: {website}")
        result = handle_open_website_command(website)
    
    # Help command
    help_patterns = [
        r"help",
        r"what can you do",
        r"commands",
        r"features",
        r"capabilities"
    ]
    if any(re.search(pattern, command_lower) for pattern in help_patterns):
        logger.info("Matched help command")
        result = handle_help_command()
    
    # Fallback for unrecognized commands
    if not result:
        logger.warning(f"No command matched for: {command_lower}")
        # For a full implementation, this would connect to an LLM for more general responses
        result = {
            "spoken_response": f"I'm not sure how to handle '{text_command}'. Try asking for help to see what I can do.",
            "opened_url": None,
            "additional_context": None
        }
    
    # Assemble final spoken response
    spoken_response = result["spoken_response"]
    additional_context = result.get("additional_context")
    
    full_spoken_response = spoken_response
    if additional_context:
        full_spoken_response += f" {additional_context}"
    
    # 1. Speak the answer
    if full_spoken_response:
        logger.info(f"Speaking: {full_spoken_response}")
        try:
            subprocess.run(["say", full_spoken_response], check=True)
        except Exception as e:
            logger.error(f"Error during 'say' command: {e}")
    
    # 2. Open webpage if applicable
    if result["opened_url"]:
        logger.info(f"Opening URL: {result['opened_url']}")
        try:
            webbrowser.open(result["opened_url"])
        except Exception as e:
            logger.error(f"Error opening webpage: {e}")
    
    return {
        "spoken_response": spoken_response,
        "opened_url": result["opened_url"],
        "processed_command": text_command,
        "additional_context": additional_context
    }

# --- Speech-to-Text Functionality ---
def perform_speech_to_text():
    """Perform speech-to-text on audio input from the microphone."""
    logger.info("Starting speech recognition...")
    
    # Debug: List available microphones
    import speech_recognition as sr
    try:
        mics = sr.Microphone.list_microphone_names()
        logger.info(f"Available microphones: {mics}")
        print(f"Available microphones: {mics}")
    except Exception as e:
        logger.error(f"Could not list microphones: {e}")
        print(f"Could not list microphones: {e}")
    
    try:
        # For simplicity, we'll use macOS's built-in 'say' command to provide feedback
        subprocess.run(["say", "I'm listening"], check=True)
        
        # Use macOS's built-in speech recognition via the `speech_recognition` library
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        
        with sr.Microphone() as source:
            logger.debug("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            logger.debug("Listening for command...")
            # Increased timeout to give more time to speak
            print("Listening for your command... (speak now)")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            
            logger.debug("Recognition started...")
            # Use Google's speech recognition as it tends to be more accurate
            # In a production app, you might want to use macOS's native recognition
            # or a more privacy-focused solution
            text = recognizer.recognize_google(audio)
            logger.info(f"Recognized text: {text}")
            return text
    except ImportError as e:
        logger.error(f"Missing speech_recognition library: {e}")
        subprocess.run(["say", "Speech recognition library not installed. Please install it with pip install SpeechRecognition"], check=True)
        return None
    except sr.WaitTimeoutError:
        logger.warning("Timeout waiting for speech input")
        subprocess.run(["say", "I didn't hear anything"], check=True)
        return None
    except sr.RequestError as e:
        logger.error(f"Recognition service error: {e}")
        subprocess.run(["say", "I couldn't connect to the speech recognition service"], check=True)
        return None
    except sr.UnknownValueError:
        logger.warning("Speech was unintelligible")
        subprocess.run(["say", "I didn't understand that"], check=True)
        return None
    except Exception as e:
        logger.error(f"Error during speech recognition: {e}")
        subprocess.run(["say", "An error occurred during speech recognition"], check=True)
        return None

# --- Flask Web Server ---
flask_app = Flask(__name__)

@flask_app.route('/', methods=['GET'])
def home():
    """Root endpoint that confirms the server is running."""
    return jsonify({
        "status": "online",
        "app": APP_NAME,
        "version": APP_VERSION,
        "message": "Send POST requests to /command or /activate_listening with text_command parameter"
    })

@flask_app.route('/activate_listening', methods=['POST'])
def activate_listening_endpoint():
    """Endpoint for processing commands from shortcuts or speech recognition."""
    logger.info("Activation signal received")
    print("\n[ACTIVATION] Received activation signal")
    
    try:
        # Check if a text_command was provided directly (from shortcuts)
        if request.is_json:
            data = request.json
            text_command = data.get('text_command')
            print(f"[ACTIVATION] Command from JSON: {text_command}")
        else:
            text_command = request.form.get('text_command')
            print(f"[ACTIVATION] Command from form: {text_command}")
        
        # Log the received command for debugging
        logger.info(f"Received text_command: {text_command}")
        
        # Print request details for debugging
        print(f"[ACTIVATION] Request headers: {dict(request.headers)}")
        print(f"[ACTIVATION] Request form data: {dict(request.form)}")
        print(f"[ACTIVATION] Request content type: {request.content_type}")
        print(f"[ACTIVATION] Request data: {request.data}")
        
        # Process the command if provided
        if text_command:
            print(f"[ACTIVATION] Processing command: '{text_command}'")
            logger.info(f"Processing provided command: {text_command}")
            result = process_command_from_user(text_command)
            print(f"[ACTIVATION] Command processed successfully")
            return jsonify({
                "status": "success",
                "message": "Command processed",
                "details": result
            }), 200
        else:
            # No command provided, return an error
            print("[ACTIVATION] Error: No text_command provided")
            logger.warning("No text_command provided")
            return jsonify({
                "status": "error",
                "message": "No text_command provided"
            }), 400
    except Exception as e:
        print(f"[ACTIVATION] Error: {e}")
        logger.error(f"Error in activate_listening: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error processing activation: {str(e)}"
        }), 500

@flask_app.route('/command', methods=['POST'])
def command_endpoint():
    """Alternative endpoint for command processing."""
    try:
        # Handle both form data and JSON
        if request.is_json:
            data = request.json
            user_text_command = data.get('text_command')
        else:
            user_text_command = request.form.get('text_command')
        
        if user_text_command:
            result = process_command_from_user(user_text_command)
            return jsonify({
                "status": "success",
                "message": "Command processed",
                "details": result
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "No text_command provided"
            }), 400
    except Exception as e:
        logger.error(f"Error processing command: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error processing command: {str(e)}"
        }), 500

def run_flask_server():
    """Run the Flask web server."""
    logger.info(f"Starting Flask server on http://127.0.0.1:{FLASK_PORT}")
    try:
        flask_app.run(host='127.0.0.1', port=FLASK_PORT, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"Could not start Flask server: {e}")

# --- Rumps Menu Bar App ---
class JulieJulieRumpsApp(rumps.App):
    def __init__(self):
        super(JulieJulieRumpsApp, self).__init__(
            name=APP_NAME,
            icon=APP_ICON,
            quit_button="Quit Julie Julie"
        )
        
        # Add menu items
        self.menu = [
            "Enter Command...",
            None,  # Separator
            "Quick Commands",
            None,  # Separator
            "Status",
            "Show Log",
            "About"
        ]
        
        # Add submenu for quick commands
        quick_commands = rumps.MenuItem("Quick Commands")
        quick_commands.add("Time")
        quick_commands.add("Weather")
        quick_commands.add("Open YouTube")
        quick_commands.add("Help")
        self.menu["Quick Commands"] = quick_commands
        
        # Status tracking
        self.server_status = "Starting..."
        
        # Start the Flask web server in a daemon thread
        self.web_server_thread = threading.Thread(target=run_flask_server, daemon=True)
        self.web_server_thread.start()
        
        # Check server status after a brief delay
        threading.Timer(2.0, self.update_server_status).start()

    def update_server_status(self):
        """Check and update the status of the Flask server."""
        try:
            response = requests.get(f"http://127.0.0.1:{FLASK_PORT}/", timeout=1)
            if response.status_code == 200:
                self.server_status = "Online"
            else:
                self.server_status = f"Error (Status: {response.status_code})"
        except requests.RequestException:
            self.server_status = "Offline"
        
        logger.info(f"Server status updated: {self.server_status}")
        
        # Schedule the next status check
        threading.Timer(60.0, self.update_server_status).start()

    @rumps.clicked("Enter Command...")
    def enter_command(self, _):
        """Handle Enter Command menu item."""
        response = rumps.Window(
            message="What would you like Julie Julie to do?",
            title=f"{APP_NAME} Command",
            default_text="",
            ok="Send",
            cancel="Cancel"
        ).run()
        
        if response.clicked and response.text:
            logger.info(f"Command entered via menu: {response.text}")
            result = process_command_from_user(response.text)
            # No need to speak or open URL again, as process_command_from_user already does that

    @rumps.clicked("Quick Commands", "Time")
    def quick_command_time(self, _):
        """Quick command for time."""
        process_command_from_user("what time is it")

    @rumps.clicked("Quick Commands", "Weather")
    def quick_command_weather(self, _):
        """Quick command for weather."""
        process_command_from_user("what's the weather")

    @rumps.clicked("Quick Commands", "Open YouTube")
    def quick_command_youtube(self, _):
        """Quick command for YouTube."""
        process_command_from_user("open youtube.com")

    @rumps.clicked("Quick Commands", "Help")
    def quick_command_help(self, _):
        """Quick command for help."""
        process_command_from_user("help")

    @rumps.clicked("Status")
    def show_status(self, _):
        """Show server status information."""
        rumps.alert(
            title=f"{APP_NAME} Status",
            message=f"Server: {self.server_status}\nVersion: {APP_VERSION}\nPort: {FLASK_PORT}"
        )

    @rumps.clicked("Show Log")
    def show_log(self, _):
        """Open the log file."""
        try:
            # Open log file in system text editor
            subprocess.run(["open", LOG_FILE], check=True)
        except Exception as e:
            logger.error(f"Error opening log file: {e}")
            rumps.alert(
                title="Error",
                message=f"Could not open log file: {e}"
            )

    @rumps.clicked("About")
    def about(self, _):
        """Show information about the app."""
        rumps.alert(
            title=f"About {APP_NAME}",
            message=f"{APP_NAME} v{APP_VERSION}\nYour Local Voice Assistant\n\nListening on port {FLASK_PORT}"
        )

    def run(self):
        """Run the app."""
        logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        try:
            super(JulieJulieRumpsApp, self).run()
        finally:
            logger.info(f"{APP_NAME} is shutting down.")

if __name__ == '__main__':
    logger.info("Preparing to start Julie Julie app...")
    
    # Check for icon file
    if APP_ICON and not isinstance(APP_ICON, str):
        import os
        if not os.path.exists(APP_ICON):
            logger.warning(f"Icon file '{APP_ICON}' not found. Using default icon.")
            APP_ICON = None
    
    app = JulieJulieRumpsApp()
    app.run()
