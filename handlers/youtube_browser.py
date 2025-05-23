"""
YouTube browser player handler.
Opens YouTube in browser for natural viewing experience.
"""

import re
import logging
import webbrowser
import json
import os
from datetime import datetime

logger = logging.getLogger('julie_julie')

# File to store remembered videos
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
            return _handle_youtube_browser_play(text_command, command_lower)
        
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

def _handle_youtube_browser_play(original_command, command_lower):
    """Open YouTube in browser and search for the video"""
    # Extract the song/artist from the command
    search_query = _extract_search_query(original_command, command_lower)
    
    if not search_query:
        return {
            "spoken_response": "What would you like me to play on YouTube?",
            "opened_url": None,
            "additional_context": None
        }
    
    # Add "official music video" to prioritize official versions and music videos
    enhanced_search = f"{search_query} official music video"
    search_formatted = enhanced_search.replace(' ', '+')
    
    # Create YouTube search URL
    youtube_url = f"https://www.youtube.com/results?search_query={search_formatted}"
    
    logger.info(f"Opening YouTube for: {search_query}")
    
    try:
        # Open YouTube in browser
        webbrowser.open(youtube_url)
        
        # Store for memory
        _store_last_played(search_query, youtube_url)
        
        return {
            "spoken_response": f"Found {search_query} on YouTube. Click the first video to start playing, and let me know if you'd like me to remember it!",
            "opened_url": youtube_url,
            "additional_context": f"Search: {enhanced_search}"
        }
    except Exception as e:
        logger.error(f"Error opening YouTube: {e}")
        return {
            "spoken_response": f"I had trouble opening YouTube for {search_query}.",
            "opened_url": None,
            "additional_context": None
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
    
    success = _add_to_favorites(last_played["query"], last_played["url"])
    
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

def _store_last_played(query, url):
    """Store the last played video temporarily"""
    try:
        os.makedirs(os.path.dirname(FAVORITES_FILE), exist_ok=True)
        
        last_played = {
            "query": query,
            "url": url,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in a temp file
        temp_file = FAVORITES_FILE.replace("favorites.json", "last_played.json")
        with open(temp_file, 'w') as f:
            json.dump(last_played, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error storing last played: {e}")

def _get_last_played():
    """Get the last played video"""
    try:
        temp_file = FAVORITES_FILE.replace("favorites.json", "last_played.json")
        if os.path.exists(temp_file):
            with open(temp_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error getting last played: {e}")
    return None

def _add_to_favorites(query, url):
    """Add a video to the favorites list"""
    try:
        os.makedirs(os.path.dirname(FAVORITES_FILE), exist_ok=True)
        
        # Load existing favorites
        favorites = []
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, 'r') as f:
                favorites = json.load(f)
        
        # Add new favorite
        new_favorite = {
            "query": query,
            "url": url,
            "added_date": datetime.now().isoformat()
        }
        
        # Check if already exists
        if not any(fav["query"].lower() == query.lower() for fav in favorites):
            favorites.append(new_favorite)
            
            # Save updated favorites
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

def get_favorites():
    """Get all favorites (for potential future use)"""
    try:
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading favorites: {e}")
    return []
