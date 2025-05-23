"""
Spotify handler for opening songs in Spotify web player or app.
"""

import re
import logging
import webbrowser
import subprocess
import json
import os
from datetime import datetime

logger = logging.getLogger('julie_julie')

# File to store remembered Spotify tracks
FAVORITES_FILE = os.path.expanduser("~/Library/Application Support/JulieJulie/spotify_favorites.json")

def handle_spotify_command(text_command):
    """
    Handle Spotify requests and memory commands.
    """
    try:
        command_lower = text_command.lower().strip()
        
        # Check if it's a memory command
        if _is_memory_command(command_lower):
            return _handle_memory_command(command_lower)
        
        # Check if it's a Spotify play request
        if _is_spotify_request(command_lower):
            return _handle_spotify_play(text_command, command_lower)
        
        return None
        
    except Exception as e:
        logger.error(f"Spotify handler error: {e}")
        return None

def _is_memory_command(command_lower):
    """Check if this is a remember/favorites command"""
    memory_phrases = [
        "remember this", "save this", "add to favorites", "favorite this",
        "remember that", "save that", "i like this", "add this to my list"
    ]
    return any(phrase in command_lower for phrase in memory_phrases)

def _is_spotify_request(command_lower):
    """Check if this is a Spotify play request"""
    # Spotify keyword at the start
    if command_lower.startswith("spotify "):
        return True
    
    # Other Spotify patterns
    spotify_patterns = [
        r"^spotify\s+",  # Starts with "spotify "
        "play on spotify",
        "spotify play"
    ]
    
    for pattern in spotify_patterns:
        if re.search(pattern, command_lower):
            return True
    
    return False

def _handle_spotify_play(original_command, command_lower):
    """Open Spotify and search for the song"""
    # Extract the song/artist from the command
    search_query = _extract_search_query(original_command, command_lower)
    
    if not search_query:
        return {
            "spoken_response": "What would you like me to play on Spotify?",
            "opened_url": None,
            "additional_context": None
        }
    
    logger.info(f"Opening Spotify for: {search_query}")
    
    try:
        # Use Spotify web player (always works, no app required)
        search_formatted = search_query.replace(' ', '%20')
        spotify_web_url = f"https://open.spotify.com/search/{search_formatted}"
        
        # Open in browser
        webbrowser.open(spotify_web_url)
        logger.info(f"Opened Spotify web player: {search_query}")
        
        # Store for memory
        _store_last_played(search_query, spotify_web_url)
        
        return {
            "spoken_response": f"Searching for {search_query} on Spotify. You can browse for free or sign up to start playing!",
            "opened_url": spotify_web_url,
            "additional_context": f"Spotify web: {search_query}"
        }
            
    except Exception as e:
        logger.error(f"Error opening Spotify: {e}")
        return {
            "spoken_response": f"I had trouble opening Spotify for {search_query}.",
            "opened_url": None,
            "additional_context": None
        }

def _extract_search_query(original_command, command_lower):
    """Extract the song/artist to search for"""
    # Remove Spotify command words
    remove_phrases = [
        r"^spotify\s+",  # Remove "spotify " from start
        r"^play\s+on\s+spotify\s+",
        r"^spotify\s+play\s+",
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
    
    success = _add_to_favorites(last_played["query"], last_played["url"])
    
    if success:
        return {
            "spoken_response": f"Got it! I've added {last_played['query']} to your Spotify favorites list.",
            "opened_url": None,
            "additional_context": f"Added to favorites: {last_played['query']}"
        }
    else:
        return {
            "spoken_response": "I had trouble saving that to your favorites.",
            "opened_url": None,
            "additional_context": None
        }

def _store_last_played(query, url):
    """Store the last played track"""
    try:
        os.makedirs(os.path.dirname(FAVORITES_FILE), exist_ok=True)
        
        last_played = {
            "query": query,
            "url": url,
            "timestamp": datetime.now().isoformat()
        }
        
        temp_file = FAVORITES_FILE.replace("spotify_favorites.json", "last_spotify_played.json")
        with open(temp_file, 'w') as f:
            json.dump(last_played, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error storing last played: {e}")

def _get_last_played():
    """Get the last played track"""
    try:
        temp_file = FAVORITES_FILE.replace("spotify_favorites.json", "last_spotify_played.json")
        if os.path.exists(temp_file):
            with open(temp_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error getting last played: {e}")
    return None

def _add_to_favorites(query, url):
    """Add a track to favorites"""
    try:
        os.makedirs(os.path.dirname(FAVORITES_FILE), exist_ok=True)
        
        favorites = []
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, 'r') as f:
                favorites = json.load(f)
        
        new_favorite = {
            "query": query,
            "url": url,
            "added_date": datetime.now().isoformat()
        }
        
        if not any(fav["query"].lower() == query.lower() for fav in favorites):
            favorites.append(new_favorite)
            
            with open(FAVORITES_FILE, 'w') as f:
                json.dump(favorites, f, indent=2)
            
            logger.info(f"Added to Spotify favorites: {query}")
            return True
        else:
            logger.info(f"Already in Spotify favorites: {query}")
            return True
            
    except Exception as e:
        logger.error(f"Error adding to favorites: {e}")
        return False
