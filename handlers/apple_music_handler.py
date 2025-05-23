"""
Apple Music handler for opening songs directly in Apple Music app.
"""

import re
import logging
import subprocess
import json
import os
from datetime import datetime

logger = logging.getLogger('julie_julie')

# File to store remembered Apple Music tracks
FAVORITES_FILE = os.path.expanduser("~/Library/Application Support/JulieJulie/apple_music_favorites.json")

def handle_apple_music_command(text_command):
    """
    Handle Apple Music requests and memory commands.
    """
    try:
        command_lower = text_command.lower().strip()
        
        # Check if it's a memory command
        if _is_memory_command(command_lower):
            return _handle_memory_command(command_lower)
        
        # Check if it's an Apple Music play request
        if _is_apple_play_request(command_lower):
            return _handle_apple_music_play(text_command, command_lower)
        
        return None
        
    except Exception as e:
        logger.error(f"Apple Music handler error: {e}")
        return None

def _is_memory_command(command_lower):
    """Check if this is a remember/favorites command"""
    memory_phrases = [
        "remember this", "save this", "add to favorites", "favorite this",
        "remember that", "save that", "i like this", "add this to my list"
    ]
    return any(phrase in command_lower for phrase in memory_phrases)

def _is_apple_play_request(command_lower):
    """Check if this is an Apple Music play request"""
    # Simple Apple keyword at the start
    if command_lower.startswith("apple "):
        return True
    
    # Other Apple Music patterns
    apple_patterns = [
        r"^apple\s+",  # Starts with "apple "
        "apple music",
        "music app"
    ]
    
    for pattern in apple_patterns:
        if re.search(pattern, command_lower):
            return True
    
    return False

def _handle_apple_music_play(original_command, command_lower):
    """Download from YouTube and play with VLC visualizer (Apple Music alternative)"""
    # Extract the song/artist from the command
    search_query = _extract_search_query(original_command, command_lower)
    
    if not search_query:
        return {
            "spoken_response": "What would you like me to play?",
            "opened_url": None,
            "additional_context": None
        }
    
    logger.info(f"Downloading and playing with visualizer: {search_query}")
    
    # Ensure music directory exists
    music_dir = os.path.expanduser("~/Library/Application Support/JulieJulie/Music")
    os.makedirs(music_dir, exist_ok=True)
    
    try:
        # Use yt-dlp to download audio
        search_term = f"{search_query} official"
        safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
        output_path = os.path.join(music_dir, f"{safe_filename}.%(ext)s")
        
        # yt-dlp command for audio only
        cmd = [
            "yt-dlp",
            "--format", "bestaudio[ext=m4a]/bestaudio",
            "--output", output_path,
            f"ytsearch1:{search_term}"
        ]
        
        logger.info(f"Downloading: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Find the downloaded file
            downloaded_files = [f for f in os.listdir(music_dir) if f.startswith(safe_filename)]
            
            if downloaded_files:
                downloaded_file = os.path.join(music_dir, downloaded_files[0])
                
                # Play with VLC and visualizer
                try:
                    subprocess.run([
                        "vlc",
                        "--intf", "dummy",  # No VLC interface
                        "--extraintf", "http",  # Enable web interface for control
                        "--audio-visual", "visual",  # Enable visualizations
                        "--effect-list", "spectrum",  # Spectrum analyzer
                        "--fullscreen",  # Fullscreen visualizer
                        downloaded_file
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    logger.info(f"Playing with VLC visualizer: {downloaded_file}")
                    
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # Fallback to simple audio playback
                    subprocess.run(["afplay", downloaded_file])
                    logger.info(f"Playing audio only: {downloaded_file}")
                
                # Store for memory
                _store_last_played(search_query, downloaded_file)
                
                return {
                    "spoken_response": f"Downloaded and playing {search_query} with visualizer!",
                    "opened_url": None,
                    "additional_context": f"File: {downloaded_file}"
                }
            else:
                return {
                    "spoken_response": f"Downloaded {search_query} but couldn't find the file.",
                    "opened_url": None,
                    "additional_context": None
                }
        else:
            logger.error(f"yt-dlp error: {result.stderr}")
            return {
                "spoken_response": f"I couldn't download {search_query}. Trying YouTube in browser instead.",
                "opened_url": None,
                "additional_context": None
            }
            
    except Exception as e:
        logger.error(f"Download error: {e}")
        return {
            "spoken_response": f"I had trouble downloading {search_query}.",
            "opened_url": None,
            "additional_context": f"Error: {str(e)}"
        }

def _extract_search_query(original_command, command_lower):
    """Extract the song/artist to search for"""
    # Remove Apple Music command words
    remove_phrases = [
        r"^apple\s+",  # Remove "apple " from start
        r"^apple\s+music\s+",
        r"^music\s+app\s+",
    ]
    
    query = original_command
    for pattern in remove_phrases:
        query = re.sub(pattern, "", query, flags=re.IGNORECASE)
    
    return query.strip()

def _handle_memory_command(command_lower):
    """Handle remembering the last played track"""
    last_played = _get_last_played()
    
    if not last_played:
        return {
            "spoken_response": "I don't have anything recent to remember. Play something first!",
            "opened_url": None,
            "additional_context": None
        }
    
    success = _add_to_favorites(last_played["query"], last_played["source"])
    
    if success:
        return {
            "spoken_response": f"Got it! I've added {last_played['query']} to your Apple Music favorites.",
            "opened_url": None,
            "additional_context": f"Added to favorites: {last_played['query']}"
        }
    else:
        return {
            "spoken_response": "I had trouble saving that to your favorites.",
            "opened_url": None,
            "additional_context": None
        }

def _store_last_played(query, source):
    """Store the last played track"""
    try:
        os.makedirs(os.path.dirname(FAVORITES_FILE), exist_ok=True)
        
        last_played = {
            "query": query,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
        
        temp_file = FAVORITES_FILE.replace("apple_music_favorites.json", "last_apple_played.json")
        with open(temp_file, 'w') as f:
            json.dump(last_played, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error storing last played: {e}")

def _get_last_played():
    """Get the last played track"""
    try:
        temp_file = FAVORITES_FILE.replace("apple_music_favorites.json", "last_apple_played.json")
        if os.path.exists(temp_file):
            with open(temp_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error getting last played: {e}")
    return None

def _add_to_favorites(query, source):
    """Add a track to favorites"""
    try:
        os.makedirs(os.path.dirname(FAVORITES_FILE), exist_ok=True)
        
        favorites = []
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, 'r') as f:
                favorites = json.load(f)
        
        new_favorite = {
            "query": query,
            "source": source,
            "added_date": datetime.now().isoformat()
        }
        
        if not any(fav["query"].lower() == query.lower() for fav in favorites):
            favorites.append(new_favorite)
            
            with open(FAVORITES_FILE, 'w') as f:
                json.dump(favorites, f, indent=2)
            
            logger.info(f"Added to Apple Music favorites: {query}")
            return True
        else:
            logger.info(f"Already in Apple Music favorites: {query}")
            return True
            
    except Exception as e:
        logger.error(f"Error adding to favorites: {e}")
        return False
