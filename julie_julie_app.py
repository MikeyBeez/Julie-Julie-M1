import rumps
import threading
from flask import Flask, request, jsonify
import webbrowser # For opening webpages
import subprocess # For using the 'say' command
from datetime import datetime # For the time command

# --- Configuration ---
APP_NAME = "Julie Julie"
APP_ICON = None  # Set to None to use default icon for now, or "icon.icns" if you have one
FLASK_PORT = 58586     # Unique port for Julie Julie's internal server

# --- Core Application Logic (will be expanded significantly) ---
def process_command_from_user(text_command):
    print(f"Julie Julie received command: {text_command}")
    
    # Placeholder for LLM interaction
    # For now, just echo and decide on a webpage based on keywords
    
    spoken_response = f"I received your command: {text_command}"
    webpage_to_open = None
    additional_context = None # From LLM later

    # --- Dummy logic to simulate LLM deciding to open a webpage ---
    # Convert to lowercase for easier matching
    command_lower = text_command.lower()

    if "21st president" in command_lower:
        spoken_response = "Chester A. Arthur was the 21st President of the United States."
        # This URL would ideally come from the LLM's structured response
        webpage_to_open = "https://en.wikipedia.org/wiki/Chester_A._Arthur"
        additional_context = "He took office after James A. Garfield's assassination."
    elif "weather" in command_lower:
        spoken_response = "I'd tell you the weather, but my weather module isn't ready yet!"
    elif "time" in command_lower:
        now = datetime.now()
        spoken_response = f"The current time is {now.strftime('%I:%M %p')}." # e.g., 03:45 PM
    # --- End Dummy Logic ---

    # Assemble final spoken response
    full_spoken_response = spoken_response
    if additional_context:
        full_spoken_response += f" {additional_context}"

    # 1. Speak the answer (using macOS 'say' command for now)
    if full_spoken_response:
        print(f"Julie Julie speaking: {full_spoken_response}")
        try:
            # Using a list of arguments for subprocess.run is generally safer
            subprocess.run(["say", full_spoken_response], check=True)
        except FileNotFoundError:
            print("macOS 'say' command not found. Make sure you're on macOS.")
        except subprocess.CalledProcessError as e:
            print(f"Error during 'say' command: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while trying to speak: {e}")


    # 2. Open webpage if applicable
    if webpage_to_open:
        print(f"Julie Julie opening: {webpage_to_open}")
        try:
            webbrowser.open(webpage_to_open)
        except Exception as e:
            print(f"An unexpected error occurred while trying to open webpage: {e}")
    
    # This dict can be returned by the Flask endpoint if needed
    return {"spoken_response": spoken_response, "opened_url": webpage_to_open, "processed_command": text_command}

# --- Flask Web Server (to receive commands from AppleScript) ---
flask_app = Flask(__name__)

@flask_app.route('/command', methods=['POST'])
def command_endpoint():
    data = request.form
    user_text_command = data.get('text_command')
    if user_text_command:
        # In a more complex app, you might queue this work
        # or pass it to the rumps app instance to handle.
        result = process_command_from_user(user_text_command)
        return jsonify({"status": "success", "message": "Command processed", "details": result}), 200
    else:
        return jsonify({"status": "error", "message": "No text_command provided"}), 400

def run_flask_server():
    # Run Flask in a separate thread.
    print(f"Starting Flask server on http://127.0.0.1:{FLASK_PORT}")
    try:
        flask_app.run(host='127.0.0.1', port=FLASK_PORT, debug=False)
    except Exception as e:
        print(f"Could not start Flask server: {e}")
        # Optionally, notify the user through the rumps app if it's already running
        # For instance, by updating a status or showing an alert.

# --- Rumps Menu Bar App ---
class JulieJulieRumpsApp(rumps.App):
    def __init__(self):
        # Note: if APP_ICON is None or invalid, rumps uses a default.
        super(JulieJulieRumpsApp, self).__init__(name=APP_NAME, icon=APP_ICON, quit_button="Quit Julie Julie")
        # self.menu = ["Show Log", "About"] # Example menu items
        
        # Start the Flask web server in a daemon thread
        # Daemon threads exit when the main program exits.
        self.web_server_thread = threading.Thread(target=run_flask_server, daemon=True)
        self.web_server_thread.start()
        
        if self.web_server_thread.is_alive():
            print(f"{APP_NAME} menu bar app started. Flask server thread initiated.")
        else:
            print(f"ERROR: {APP_NAME} started, but Flask server thread failed to start.")
            # You might want to show an error to the user here via rumps.alert
            rumps.alert(title=f"{APP_NAME} Startup Error", message="Could not start internal web server. Commands will not be received.")


    # @rumps.clicked("Show Log") # Example menu item action
    # def show_log(self, _):
    #     rumps.alert(title=APP_NAME, message="Log window not implemented yet.")

    # @rumps.clicked("About")
    # def about(self, _):
    #     rumps.alert(title=APP_NAME, message="Julie Julie - Your Local LLM Assistant. (v0.1)")

    def run(self):
        # rumps.App.run will block here until the app is quit.
        try:
            super(JulieJulieRumpsApp, self).run()
        finally:
            print(f"{APP_NAME} is shutting down.")
            # Add any explicit cleanup here if needed, though daemon threads should exit.
            # For example, if the web server needed an explicit shutdown signal (not typical for Flask's dev server).

if __name__ == '__main__':
    print("Preparing to start Julie Julie app...")
    # If APP_ICON is set to a filename like "icon.icns", ensure the file exists
    # in the same directory as the script, or provide a full path.
    # If it's None, rumps will use a default icon.
    if APP_ICON and not isinstance(APP_ICON, str) : # Basic check if using a path
         import os
         if not os.path.exists(APP_ICON):
            print(f"Warning: Icon file '{APP_ICON}' not found. Using default icon.")
            APP_ICON = None # Fallback to default

    app = JulieJulieRumpsApp()
    app.run()
