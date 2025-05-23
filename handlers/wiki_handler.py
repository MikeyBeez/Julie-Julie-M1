import requests
import logging

logger = logging.getLogger('julie_julie')

def handle_wiki_command(topic, ollama_url="http://localhost:11434/api/generate"):
    """Handle information queries via Wikipedia with Ollama query reformatting."""
    try:
        # First, ask Ollama to reformat the query for Wikipedia
        logger.info(f"Reformatting query with Ollama: {topic}")
        
        reformat_payload = {
            "model": "deepseek-r1",
            "prompt": f"Convert this query into a proper Wikipedia page title (just the title, nothing else): {topic}",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "max_tokens": 20
            }
        }
        
        reformat_response = requests.post(ollama_url, json=reformat_payload, timeout=10)
        
        if reformat_response.status_code == 200:
            result = reformat_response.json()
            wiki_topic = result.get('response', topic).strip()
            logger.info(f"Ollama reformatted '{topic}' -> '{wiki_topic}'")
        else:
            wiki_topic = topic
            logger.warning(f"Ollama reformat failed, using original: {topic}")
        
        # Now fetch from Wikipedia
        logger.info(f"Fetching Wikipedia info for: {wiki_topic}")
        wiki_api_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + wiki_topic.replace(' ', '_')
        
        response = requests.get(wiki_api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            extract = data.get('extract', '')
            
            if extract:
                # Get first 2-3 sentences for a good spoken summary
                sentences = extract.split('. ')
                summary = '. '.join(sentences[:3]) + '.'
                summary = summary.replace('  ', ' ').strip()
                
                return {
                    "spoken_response": summary,
                    "opened_url": data.get('content_urls', {}).get('desktop', {}).get('page', f"https://en.wikipedia.org/wiki/{wiki_topic.replace(' ', '_')}"),
                    "additional_context": "I've also opened the full Wikipedia page for more details."
                }
            else:
                wiki_url = f"https://en.wikipedia.org/wiki/{wiki_topic.replace(' ', '_')}"
                return {
                    "spoken_response": f"I couldn't find a summary for {wiki_topic}, but I've opened the Wikipedia page.",
                    "opened_url": wiki_url,
                    "additional_context": None
                }
        else:
            wiki_url = f"https://en.wikipedia.org/wiki/{wiki_topic.replace(' ', '_')}"
            return {
                "spoken_response": f"I couldn't retrieve information about {wiki_topic} right now, but I've opened the Wikipedia page.",
                "opened_url": wiki_url,
                "additional_context": None
            }
    
    except Exception as e:
        logger.error(f"Wikipedia error: {e}")
        wiki_url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
        return {
            "spoken_response": f"I had trouble getting information about {topic}, but I've opened the Wikipedia page.",
            "opened_url": wiki_url,
            "additional_context": None
        }
