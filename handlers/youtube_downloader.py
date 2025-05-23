"""
YouTube downloader and player handler.
Downloads and plays music directly using yt-dlp.
"""

import re
import logging
import subprocess
import json
import os
import tempfile
from datetime import datetime

logger = logging.getLogger('julie_julie')

# Directory to store downloaded music
MUSIC_DIR = os.path.expanduser("~/Library/Application Support/JulieJulie/Music")
FAVORITES_FILE = os.path.expanduser("~/Library/Application Support/JulieJulie/favorites.json")

def handle_youtube_command(text_command):
    """
    Handle YouTube video requests and memory commands.
    """
    try:
        command_lower = text_command.lower().strip()
        
        # Check if it's a memory command
        if _is_memory_command(command_lower):
            return _handle_memory_command(command_lower)
        
        # Check if it's a YouTube play request
        if _is_youtube_request(command_lower):
            return _handle_youtube_download_and_play(text_command, command_lower)
        
        return None
        
    except Exception as e:
        logger.error(f"YouTube handler error: {e}")
        return None

def _is_memory_command(command_lower):
    """Check if this is a remember/favorites command"""
    memory_phrases = [
        "remember this", "save this", "add to favorites", "favorite this",
        "remember that", "save that", "i like this", "add this to my list"
    ]
    return any(phrase in command_lower for phrase in memory_phrases)

def _is_youtube_request(command_lower):
    """Check if this is a YouTube play request"""
    # Direct YouTube requests
    if "youtube" in command_lower:
        return True
    
    # Play requests
    play_patterns = [
        r"play\s+",  # "play something"
        r"^play\s",   # starts with "play "
    ]
    
    for pattern in play_patterns:
        if re.search(pattern, command_lower):
            return True
    
    # Music-related terms
    music_terms = ["music video", "song", "video of", "music by"]
    if any(term in command_lower for term in music_terms):
        return True
    
    # Artist possessive patterns like "Frank Zappa's Joe's garage"
    artist_possessive = re.search(r"\w+(?:'s|s')\s+\w+", command_lower)
    if artist_possessive:
        return True
    
    return False

def _handle_youtube_download_and_play(original_command, command_lower):
    """Download and play a YouTube video"""
    # Extract the song/artist from the command
    search_query = _extract_search_query(original_command, command_lower)
    
    if not search_query:
        return {
            "spoken_response": "What would you like me to play?",
            "opened_url": None,
            "additional_context": None
        }
    
    # Ensure music directory exists
    os.makedirs(MUSIC_DIR, exist_ok=True)
    
    try:
        logger.info(f"Searching and downloading: {search_query}")
        
        # Test if yt-dlp is accessible and try to update it
        try:
            test_result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, timeout=10)
            logger.info(f"yt-dlp version: {test_result.stdout.strip()}")
            
            # Try to update yt-dlp to latest version to handle YouTube changes
            logger.info("Updating yt-dlp to handle latest YouTube changes...")
            update_result = subprocess.run(["yt-dlp", "-U"], capture_output=True, text=True, timeout=30)
            if update_result.returncode == 0:
                logger.info("yt-dlp updated successfully")
            
        except Exception as e:
            logger.error(f"yt-dlp not accessible: {e}")
            return {
                "spoken_response": "yt-dlp is not installed or not accessible. Please install it with 'brew install yt-dlp'.",
                "opened_url": None,
                "additional_context": None
            }
        
        # Use yt-dlp to search and download the best audio
        search_term = f"{search_query} official"
        
        # Create safe filename
        safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
        output_path = os.path.join(MUSIC_DIR, f"{safe_filename}.%(ext)s")
        
        # yt-dlp command - use simpler format selection to avoid signature issues
        cmd = [
            "yt-dlp",
            "--format", "worst",  # Use worst quality to avoid signature extraction issues
            "--ignore-errors",
            "--no-warnings",
            "--output", output_path,
            f"ytsearch1:{search_term}"
        ]
        
        # Run download with better error handling
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # Increased timeout
        
        logger.info(f"yt-dlp return code: {result.returncode}")
        logger.info(f"yt-dlp stdout: {result.stdout}")
        if result.stderr:
            logger.error(f"yt-dlp stderr: {result.stderr}")
        
        if result.returncode == 0:
            # Find the downloaded file
            downloaded_files = [f for f in os.listdir(MUSIC_DIR) if f.startswith(safe_filename)]
            
            if downloaded_files:
                downloaded_file = os.path.join(MUSIC_DIR, downloaded_files[0])
                
                # Play the video fullscreen with VLC or IINA (best for fullscreen video)
                try:
                    # Try VLC first with fullscreen and visualizations
                    subprocess.run([
                        "vlc", 
                        "--fullscreen",
                        "--video-filter", "visual",  # Enable audio visualizations
                        "--effect-list", "spectrum",  # Spectrum analyzer
                        "--play-and-exit",
                        downloaded_file
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    logger.info(f"Playing fullscreen with VLC visualizations: {downloaded_file}")
                    
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # Try IINA (great macOS video player with visualizations)
                    try:
                        subprocess.run([
                            "iina",
                            "--fullscreen",
                            downloaded_file
                        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        logger.info(f"Playing fullscreen with IINA: {downloaded_file}")
                        
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # Fallback to QuickTime Player in fullscreen mode
                        try:
                            # Open with QuickTime and try to make it fullscreen
                            subprocess.run(["open", "-a", "QuickTime Player", downloaded_file])
                            
                            # Wait a moment, then send fullscreen command
                            import time
                            time.sleep(2)
                            
                            # Use AppleScript to make QuickTime go fullscreen
                            fullscreen_script = '''
                            tell application "QuickTime Player"
                                activate
                                tell front document to present
                            end tell
                            '''
                            subprocess.run(["osascript", "-e", fullscreen_script], 
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            logger.info(f"Playing with QuickTime fullscreen: {downloaded_file}")
                            
                        except Exception as e:
                            logger.error(f"Fallback player failed: {e}")
                            # Just open normally as last resort
                            subprocess.run(["open", downloaded_file])
                
                # Store for memory
                _store_last_played(search_query, downloaded_file)
                
                logger.info(f"Downloaded and playing: {downloaded_file}")
                
                return {
                    "spoken_response": f"Downloaded and playing {search_query}!",
                    "opened_url": None,
                    "additional_context": f"File: {downloaded_file}"
                }
            else:
                return {
                    "spoken_response": f"I downloaded {search_query} but couldn't find the file.",
                    "opened_url": None,
                    "additional_context": None
                }
        else:
            logger.error(f"yt-dlp error: {result.stderr}")
            return {
                "spoken_response": f"I couldn't download {search_query}. Make sure yt-dlp is installed.",
                "opened_url": None,
                "additional_context": f"Error: {result.stderr}"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "spoken_response": f"Downloading {search_query} is taking too long. Try again later.",
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
    # Remove common command words but preserve the full query
    remove_phrases = [
        r"^play\s+",
        r"^youtube\s+", 
        r"^music\s+video\s+",
        r"^video\s+",
        r"^song\s+",
        r"^play\s+me\s+",
        r"^find\s+",
        r"^search\s+for\s+",
        r"^look\s+up\s+"
    ]
    
    query = original_command
    for pattern in remove_phrases:
        query = re.sub(pattern, "", query, flags=re.IGNORECASE)
    
    return query.strip()

def _handle_memory_command(command_lower):
    """Handle remembering the last played video"""
    last_played = _get_last_played()
    
    if not last_played:
        return {
            "spoken_response": "I don't have anything recent to remember. Play something first!",
            "opened_url": None,
            "additional_context": None
        }
    
    success = _add_to_favorites(last_played["query"], last_played["file"])
    
    if success:
        return {
            "spoken_response": f"Got it! I've added {last_played['query']} to your favorites.",
            "opened_url": None,
            "additional_context": f"Added to favorites: {last_played['query']}"
        }
    else:
        return {
            "spoken_response": "I had trouble saving that to your favorites.",
            "opened_url": None,
            "additional_context": None
        }

def _store_last_played(query, file_path):
    """Store the last played track"""
    try:
        os.makedirs(os.path.dirname(FAVORITES_FILE), exist_ok=True)
        
        last_played = {
            "query": query,
            "file": file_path,
            "timestamp": datetime.now().isoformat()
        }
        
        temp_file = FAVORITES_FILE.replace("favorites.json", "last_played.json")
        with open(temp_file, 'w') as f:
            json.dump(last_played, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error storing last played: {e}")

def _get_last_played():
    """Get the last played track"""
    try:
        temp_file = FAVORITES_FILE.replace("favorites.json", "last_played.json")
        if os.path.exists(temp_file):
            with open(temp_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error getting last played: {e}")
    return None

def _add_to_favorites(query, file_path):
    """Add a track to favorites"""
    try:
        os.makedirs(os.path.dirname(FAVORITES_FILE), exist_ok=True)
        
        favorites = []
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, 'r') as f:
                favorites = json.load(f)
        
        new_favorite = {
            "query": query,
            "file": file_path,
            "added_date": datetime.now().isoformat()
        }
        
        if not any(fav["query"].lower() == query.lower() for fav in favorites):
            favorites.append(new_favorite)
            
            with open(FAVORITES_FILE, 'w') as f:
                json.dump(favorites, f, indent=2)
            
            logger.info(f"Added to favorites: {query}")
            return True
        else:
            logger.info(f"Already in favorites: {query}")
            return True
            
    except Exception as e:
        logger.error(f"Error adding to favorites: {e}")
        return False
