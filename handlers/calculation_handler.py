"""
Simple calculation handler for basic math operations.
Handles tips, percentages, basic arithmetic, and unit conversions.
Complex reasoning should go to Ollama.
"""

import re
import logging

logger = logging.getLogger('julie_julie')

def handle_calculation(text_command):
    """
    Handle simple calculations that don't need AI reasoning.
    Returns None if no calculation pattern is found (let Ollama handle it).
    """
    try:
        command_lower = text_command.lower().strip()
        
        # Tip calculations - most common use case
        result = _handle_tip_calculation(command_lower)
        if result:
            return result
        
        # Basic percentages 
        result = _handle_percentage_calculation(command_lower)
        if result:
            return result
        
        # Simple arithmetic
        result = _handle_basic_arithmetic(command_lower)
        if result:
            return result
        
        # Unit conversions
        result = _handle_unit_conversion(command_lower)
        if result:
            return result
        
        # No patterns matched - let Ollama handle it
        return None
        
    except Exception as e:
        logger.error(f"Calculation error: {e}")
        return None

def _handle_tip_calculation(command_lower):
    """Handle tip calculations like '15% tip on $47'"""
    patterns = [
        r'(\d+(?:\.\d+)?)\s*%\s*tip.*?(?:on\s+)?\$?(\d+(?:\.\d+)?)',
        r'(?:what\'s\s+)?(?:a\s+)?(\d+(?:\.\d+)?)\s*percent\s+tip.*?\$?(\d+(?:\.\d+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, command_lower)
        if match:
            percentage = float(match.group(1))
            amount = float(match.group(2))
            
            tip_amount = amount * (percentage / 100)
            total = amount + tip_amount
            
            return {
                "spoken_response": f"A {percentage}% tip on ${amount:.2f} is ${tip_amount:.2f}. Total would be ${total:.2f}.",
                "opened_url": None,
                "additional_context": None
            }
    
    return None

def _handle_percentage_calculation(command_lower):
    """Handle percentage calculations like 'what's 20% of 150'"""
    patterns = [
        r'(?:what\'s\s+)?(\d+(?:\.\d+)?)\s*%\s+of\s+(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*percent\s+of\s+(\d+(?:\.\d+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, command_lower)
        if match:
            percentage = float(match.group(1))
            amount = float(match.group(2))
            result = amount * (percentage / 100)
            
            return {
                "spoken_response": f"{percentage}% of {amount} is {result:.2f}.",
                "opened_url": None,
                "additional_context": None
            }
    
    return None

def _handle_basic_arithmetic(command_lower):
    """Handle basic arithmetic like '47 + 23' or 'what's 100 divided by 4'"""
    patterns = [
        (r'(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)', lambda a, b: (float(a) + float(b), f"{a} plus {b}")),
        (r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)', lambda a, b: (float(a) - float(b), f"{a} minus {b}")),
        (r'(\d+(?:\.\d+)?)\s*\*\s*(\d+(?:\.\d+)?)', lambda a, b: (float(a) * float(b), f"{a} times {b}")),
        (r'(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)', lambda a, b: (float(a) / float(b), f"{a} divided by {b}")),
        (r'what\'s\s+(\d+(?:\.\d+)?)\s+plus\s+(\d+(?:\.\d+)?)', lambda a, b: (float(a) + float(b), f"{a} plus {b}")),
        (r'what\'s\s+(\d+(?:\.\d+)?)\s+minus\s+(\d+(?:\.\d+)?)', lambda a, b: (float(a) - float(b), f"{a} minus {b}")),
        (r'what\'s\s+(\d+(?:\.\d+)?)\s+times\s+(\d+(?:\.\d+)?)', lambda a, b: (float(a) * float(b), f"{a} times {b}")),
        (r'what\'s\s+(\d+(?:\.\d+)?)\s+divided\s+by\s+(\d+(?:\.\d+)?)', lambda a, b: (float(a) / float(b), f"{a} divided by {b}")),
    ]
    
    for pattern, calc_func in patterns:
        match = re.search(pattern, command_lower)
        if match:
            try:
                result, description = calc_func(match.group(1), match.group(2))
                return {
                    "spoken_response": f"{description} equals {result:.2f}.",
                    "opened_url": None,
                    "additional_context": None
                }
            except ZeroDivisionError:
                return {
                    "spoken_response": "You can't divide by zero.",
                    "opened_url": None,
                    "additional_context": None
                }
    
    return None

def _handle_unit_conversion(command_lower):
    """Handle common unit conversions"""
    # Temperature conversions
    celsius_to_f = re.search(r'(\d+(?:\.\d+)?)\s*(?:degrees?\s+)?(?:celsius|c)\s+to\s+(?:fahrenheit|f)', command_lower)
    if celsius_to_f:
        celsius = float(celsius_to_f.group(1))
        fahrenheit = (celsius * 9/5) + 32
        return {
            "spoken_response": f"{celsius} degrees Celsius is {fahrenheit:.1f} degrees Fahrenheit.",
            "opened_url": None,
            "additional_context": None
        }
    
    fahrenheit_to_c = re.search(r'(\d+(?:\.\d+)?)\s*(?:degrees?\s+)?(?:fahrenheit|f)\s+to\s+(?:celsius|c)', command_lower)
    if fahrenheit_to_c:
        fahrenheit = float(fahrenheit_to_c.group(1))
        celsius = (fahrenheit - 32) * 5/9
        return {
            "spoken_response": f"{fahrenheit} degrees Fahrenheit is {celsius:.1f} degrees Celsius.",
            "opened_url": None,
            "additional_context": None
        }
    
    # Could add more conversions here (miles to km, etc.)
    return None
