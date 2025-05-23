import rumps
import threading
import logging
import os
import sys
import json
from flask import Flask, request, jsonify
import subprocess
from datetime import datetime
import requests

# Import handlers
from handlers.calculation_handler import handle_calculation
from handlers.youtube_browser import handle_youtube_command
from handlers.apple_music_handler import handle_apple_music_command
from handlers.spotify_handler import handle_spotify_command
from handlers.visualizer_handler import handle_visualizer_command

# --- Configuration ---
APP_NAME = "Julie Julie"
APP_VERSION = "0.4.0"
APP_ICON = None
FLASK_PORT = 58586
LOG_FILE = os.path.expanduser("~/Library/Logs/JulieJulie/julie_julie.log")

# --- Setup Logging ---
def setup_logging():
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('julie_julie')
    print("=" * 80)
    print(f"Starting {APP_NAME} v{APP_VERSION}")
    print("=" * 80)
    
    return logger

logger = setup_logging()

# --- Simple Handlers ---
def handle_time_command():
    now = datetime.now()
    return {
        "spoken_response": f"The current time is {now.strftime('%I:%M %p')}.",
        "opened_url": None,
        "additional_context": None
    }

def handle_weather_command(location=None):
    try:
        if not location:
            location = "Kansas City, Missouri"  # Default location
        
        logger.info(f"Fetching weather for: {location}")
        
        # Use National Weather Service API (free, no API key needed, very reliable for US)
        # First, we need to geocode the location to get coordinates
        geocode_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1&countrycodes=us"
        
        try:
            geo_response = requests.get(geocode_url, timeout=10, headers={'User-Agent': 'Julie-Julie-Voice-Assistant'})
            if geo_response.status_code == 200:
                geo_data = geo_response.json()
                if geo_data:
                    lat = float(geo_data[0]['lat'])
                    lon = float(geo_data[0]['lon'])
                    display_name = geo_data[0]['display_name']
                    logger.info(f"Found coordinates for {location}: {lat}, {lon} ({display_name})")
                    
                    # Now get weather from National Weather Service
                    nws_url = f"https://api.weather.gov/points/{lat},{lon}"
                    nws_response = requests.get(nws_url, timeout=10, headers={'User-Agent': 'Julie-Julie-Voice-Assistant'})
                    
                    if nws_response.status_code == 200:
                        nws_data = nws_response.json()
                        forecast_url = nws_data['properties']['forecast']
                        
                        # Get the actual forecast
                        forecast_response = requests.get(forecast_url, timeout=10, headers={'User-Agent': 'Julie-Julie-Voice-Assistant'})
                        if forecast_response.status_code == 200:
                            forecast_data = forecast_response.json()
                            current_period = forecast_data['properties']['periods'][0]
                            
                            temp = current_period['temperature']
                            temp_unit = current_period['temperatureUnit']
                            conditions = current_period['shortForecast']
                            detailed = current_period['detailedForecast']
                            
                            # Create a clean location name
                            location_parts = display_name.split(',')
                            clean_location = f"{location_parts[0]}, {location_parts[-2].strip()}"
                            
                            weather_response = f"The weather in {clean_location} is {conditions}, {temp} degrees {temp_unit}."
                            logger.info(f"Weather response: {weather_response}")
                            
                            return {
                                "spoken_response": weather_response,
                                "opened_url": None,
                                "additional_context": f"Full forecast: {detailed}"
                            }
                else:
                    logger.warning(f"No geocoding results for: {location}")
        except Exception as e:
            logger.error(f"NWS weather error: {e}")
        
        return {
            "spoken_response": f"I couldn't get the weather for {location} right now.",
            "opened_url": None,
            "additional_context": None
        }
    
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return {
            "spoken_response": f"I'm having trouble getting the weather for {location}.",
            "opened_url": None,
            "additional_context": None
        }

def handle_ollama_query(user_query):
    try:
        logger.info(f"Sending streaming query to Ollama: {user_query}")
        
        ollama_url = "http://localhost:11434/api/generate"
        payload = {
            "model": "deepseek-r1",
            "prompt": f"You are Julie Julie, a friendly and helpful voice assistant. Respond naturally and conversationally. Keep your response brief and spoken-friendly (1-3 sentences). User says: {user_query}",
            "stream": True,  # Enable streaming
            "options": {
                "temperature": 0.7,
                "max_tokens": 100
            }
        }
        
        response = requests.post(ollama_url, json=payload, timeout=30, stream=True)
        
        if response.status_code == 200:
            full_response = ""
            sentence_buffer = ""
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        token = data.get('response', '')
                        
                        if token:
                            sentence_buffer += token
                            full_response += token
                            
                            # Check if we have a complete sentence
                            if any(punct in sentence_buffer for punct in ['.', '!', '?']):
                                # Find the end of the sentence
                                for punct in ['.', '!', '?']:
                                    if punct in sentence_buffer:
                                        sentence_end = sentence_buffer.find(punct) + 1
                                        complete_sentence = sentence_buffer[:sentence_end].strip()
                                        
                                        if complete_sentence:
                                            logger.info(f"Speaking sentence: {complete_sentence}")
                                            # Speak the sentence immediately
                                            subprocess.run(["say", complete_sentence], check=True)
                                        
                                        # Keep remainder for next sentence
                                        sentence_buffer = sentence_buffer[sentence_end:].strip()
                                        break
                        
                        # Check if generation is done
                        if data.get('done', False):
                            # Speak any remaining text
                            if sentence_buffer.strip():
                                logger.info(f"Speaking final fragment: {sentence_buffer.strip()}")
                                subprocess.run(["say", sentence_buffer.strip()], check=True)
                            break
                            
                    except json.JSONDecodeError:
                        continue
            
            return {
                "spoken_response": full_response.strip(),
                "opened_url": None,
                "additional_context": "Response was streamed and spoken in real-time"
            }
        else:
            return {
                "spoken_response": "I'm having trouble thinking right now.",
                "opened_url": None,
                "additional_context": None
            }
    
    except Exception as e:
        logger.error(f"Ollama streaming error: {e}")
        return {
            "spoken_response": "Something went wrong while thinking about that.",
            "opened_url": None,
            "additional_context": None
        }

# --- Core Logic ---
def process_command_from_user(text_command):
    if not text_command:
        return {
            "spoken_response": "I didn't receive any command.",
            "opened_url": None,
            "additional_context": None
        }
    
    logger.info(f"Processing command: {text_command}")
    command_lower = text_command.lower().strip()
    
    # Time commands
    if any(word in command_lower for word in ["time", "clock"]):
        result = handle_time_command()
        # Speak time responses immediately since they're not streamed
        spoken_response = result["spoken_response"]
        if spoken_response:
            try:
                subprocess.run(["say", spoken_response], check=True)
            except Exception as e:
                logger.error(f"Error during 'say' command: {e}")
        return result
    
    # Try calculation handler first (for simple math)
    calc_result = handle_calculation(text_command)
    if calc_result:
        # It's a calculation - speak immediately
        spoken_response = calc_result["spoken_response"]
        if spoken_response:
            logger.info(f"Quick calculation: {spoken_response}")
            try:
                subprocess.run(["say", spoken_response], check=True)
            except Exception as e:
                logger.error(f"Error during calculation speech: {e}")
        return calc_result
        
    # Try visualizer handler
    viz_result = handle_visualizer_command(text_command)
    if viz_result:
        # It's a visualizer command - speak immediately
        spoken_response = viz_result["spoken_response"]
        if spoken_response:
            logger.info(f"Visualizer command: {spoken_response}")
            try:
                subprocess.run(["say", spoken_response], check=True)
            except Exception as e:
                logger.error(f"Error during visualizer speech: {e}")
        return viz_result
        
    # Try Spotify handler (for "Spotify" commands)
    spotify_result = handle_spotify_command(text_command)
    if spotify_result:
        # It's a Spotify command - speak immediately
        spoken_response = spotify_result["spoken_response"]
        if spoken_response:
            logger.info(f"Spotify command: {spoken_response}")
            try:
                subprocess.run(["say", spoken_response], check=True)
            except Exception as e:
                logger.error(f"Error during Spotify speech: {e}")
        return spotify_result
            
    # Try Apple Music handler (for "Apple" commands)
    apple_result = handle_apple_music_command(text_command)
    if apple_result:
        # It's an Apple Music command - speak immediately
        spoken_response = apple_result["spoken_response"]
        if spoken_response:
            logger.info(f"Apple Music command: {spoken_response}")
            try:
                subprocess.run(["say", spoken_response], check=True)
            except Exception as e:
                logger.error(f"Error during Apple Music speech: {e}")
        return apple_result
                
    # Try YouTube handler
    youtube_result = handle_youtube_command(text_command)
    if youtube_result:
        # It's a YouTube command - speak immediately
        spoken_response = youtube_result["spoken_response"]
        if spoken_response:
            logger.info(f"YouTube command: {spoken_response}")
            try:
                subprocess.run(["say", spoken_response], check=True)
            except Exception as e:
                logger.error(f"Error during YouTube speech: {e}")
        return youtube_result
                    
    # Weather commands
    if "weather" in command_lower:
        # Extract location if mentioned
        location = None
        if " in " in command_lower:
            location_part = command_lower.split(" in ", 1)[1]
            location = location_part.replace("?", "").strip()
        elif " for " in command_lower:
            location_part = command_lower.split(" for ", 1)[1]
            location = location_part.replace("?", "").strip()
        
        result = handle_weather_command(location)
        # Speak weather responses immediately since they're not streamed
        spoken_response = result["spoken_response"]
        if spoken_response:
            logger.info(f"About to speak weather: '{spoken_response}'")
            try:
                subprocess.run(["say", spoken_response], check=True)
                logger.info("Weather speech completed successfully")
            except Exception as e:
                logger.error(f"Error during weather 'say' command: {e}")
        return result
                    
    # Everything else goes to Ollama for conversation (streaming with real-time speech)
    result = handle_ollama_query(text_command)
    # Note: Ollama responses are already spoken during streaming
    return result

# --- Flask Server ---
flask_app = Flask(__name__)

@flask_app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "app": APP_NAME,
        "version": APP_VERSION
    })

@flask_app.route('/command', methods=['POST'])
def command_endpoint():
    try:
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
            "message": f"Error: {str(e)}"
        }), 500

def run_flask_server():
    logger.info(f"Starting Flask server on http://127.0.0.1:{FLASK_PORT}")
    try:
        flask_app.run(host='127.0.0.1', port=FLASK_PORT, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"Could not start Flask server: {e}")

# --- Menu Bar App ---
class JulieJulieRumpsApp(rumps.App):
    def __init__(self):
        super(JulieJulieRumpsApp, self).__init__(
            name=APP_NAME,
            icon=APP_ICON,
            quit_button="Quit Julie Julie"
        )
        
        self.menu = [
            "Enter Command...",
            "Status"
        ]
        
        self.server_status = "Starting..."
        
        # Start Flask server
        self.web_server_thread = threading.Thread(target=run_flask_server, daemon=True)
        self.web_server_thread.start()

    @rumps.clicked("Enter Command...")
    def enter_command(self, _):
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

    @rumps.clicked("Status")
    def show_status(self, _):
        rumps.alert(
            title=f"{APP_NAME} Status",
            message=f"Version: {APP_VERSION}\nPort: {FLASK_PORT}"
        )

    def run(self):
        logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        try:
            super(JulieJulieRumpsApp, self).run()
        finally:
            logger.info(f"{APP_NAME} is shutting down.")

if __name__ == '__main__':
    app = JulieJulieRumpsApp()
    app.run()
