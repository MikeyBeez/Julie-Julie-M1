"""
Radio handler for streaming radio stations.
Handles classical, jazz, and classic/progressive rock stations.
"""

import re
import logging
import webbrowser

logger = logging.getLogger('julie_julie')

# Curated radio stations with reliable web players
RADIO_STATIONS = {
    "classical": {
        "url": "https://radioparadise.com/player",
        "name": "Radio Paradise Main Mix",
        "backup_url": "https://radioparadise.com/player"
    },
    "jazz": {
        "url": "https://somafm.com/player/#/now-playing/groovesalad",
        "name": "SomaFM Groove Salad",
        "backup_url": "https://somafm.com/groovesalad/"
    },
    "rock": {
        "url": "https://radioparadise.com/player",
        "name": "Radio Paradise Rock Mix",
        "backup_url": "https://radioparadise.com/listen/rock-mix"
    },
    "progressive": {
        "url": "https://somafm.com/player/#/now-playing/bagel",
        "name": "SomaFM BAGeL Radio",
        "backup_url": "https://somafm.com/bagel/"
    },
    "npr": {
        "url": "https://www.npr.org/player/live",
        "name": "NPR Live Radio",
        "backup_url": "https://www.npr.org/"
    },
    "news": {
        "url": "https://www.npr.org/player/live",
        "name": "NPR Live Radio",
        "backup_url": "https://www.npr.org/"
    }
}

def handle_radio_command(text_command):
    """
    Handle radio station requests.
    Supports classical, jazz, and classic/progressive rock.
    """
    try:
        command_lower = text_command.lower().strip()
        
        # Check if it's a radio command
        if not _is_radio_request(command_lower):
            return None
        
        # Determine which station to play
        station_key = _determine_station(command_lower)
        
        if not station_key:
            return _list_available_stations()
        
        return _play_station(station_key)
        
    except Exception as e:
        logger.error(f"Radio handler error: {e}")
        return {
            "spoken_response": "I had trouble starting the radio station.",
            "opened_url": None,
            "additional_context": None
        }

def _is_radio_request(command_lower):
    """Check if this is a radio request"""
    radio_keywords = [
        "radio", "classical music", "jazz music", "rock music", "news", "npr",
        "classical radio", "jazz radio", "rock radio", "npr radio",
        "progressive rock", "classic rock", "public radio", "national public radio"
    ]
    
    return any(keyword in command_lower for keyword in radio_keywords)

def _determine_station(command_lower):
    """Determine which radio station to play based on command"""
    # NPR/News patterns
    if any(word in command_lower for word in ["npr", "news", "public radio", "national public radio"]):
        return "npr"
    
    # Classical patterns
    if any(word in command_lower for word in ["classical", "orchestra", "symphony", "baroque", "mozart"]):
        return "classical"
    
    # Jazz patterns  
    if any(word in command_lower for word in ["jazz", "smooth", "groove", "bebop", "swing"]):
        return "jazz"
    
    # Progressive rock patterns
    if any(phrase in command_lower for phrase in ["progressive rock", "prog rock", "progressive", "prog"]):
        return "progressive"
    
    # Classic rock patterns
    if any(word in command_lower for word in ["rock", "classic rock", "guitar", "70s", "80s"]):
        return "rock"
    
    return None

def _play_station(station_key):
    """Play the specified radio station"""
    if station_key not in RADIO_STATIONS:
        return _list_available_stations()
    
    station = RADIO_STATIONS[station_key]
    
    try:
        # Open the web player (most reliable approach)
        webbrowser.open(station["url"])
        
        logger.info(f"Opened radio station: {station['name']}")
        
        return {
            "spoken_response": f"Playing {station['name']}. Enjoy the music!",
            "opened_url": station["url"],
            "additional_context": f"Radio: {station['name']}"
        }
        
    except Exception as e:
        logger.error(f"Error opening radio station {station_key}: {e}")
        return {
            "spoken_response": f"I couldn't start {station['name']} right now.",
            "opened_url": None,
            "additional_context": None
        }

def _list_available_stations():
    """List available radio stations when user asks for radio without specifying"""
    station_list = []
    for key, station in RADIO_STATIONS.items():
        station_list.append(station['name'])
    
    stations_text = ", ".join(station_list)
    
    return {
        "spoken_response": f"I can play these radio stations: {stations_text}. Just say 'play classical radio', 'play jazz radio', or 'play rock radio'.",
        "opened_url": None,
        "additional_context": f"Available stations: {stations_text}"
    }

def get_station_info():
    """Get information about available stations (for help/status)"""
    info = {}
    for key, station in RADIO_STATIONS.items():
        info[key] = {
            "name": station["name"],
            "genre": key.title()
        }
    return info

# Voice command examples:
# "Classical radio"
# "Jazz music" 
# "Rock radio"
# "Progressive rock"
# "NPR"
# "News"
# "What radio stations do you have?"
