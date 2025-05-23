"""
Custom logging formatter and handlers for Julie Julie using Rich.
Provides beautiful, properly wrapped output with colors and formatting.
"""

import logging
import sys
from typing import TextIO
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich import box
from datetime import datetime

# Global Rich console
console = Console()

class JulieJulieRichHandler(RichHandler):
    """Custom Rich handler for Julie Julie with special formatting for different message types."""
    
    def __init__(self):
        super().__init__(
            console=console,
            show_time=True,
            show_level=True,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=False
        )
    
    def emit(self, record):
        """Custom emit method with special handling for different message types."""
        message = record.getMessage()
        
        # Handle AI speech specially
        if "Speaking sentence:" in message or "Speaking final fragment:" in message:
            speech_text = message.split(": ", 1)[1] if ": " in message else message
            
            # Create a beautiful panel for AI speech
            ai_panel = Panel(
                Text(speech_text, style="bright_green"),
                title="🎤 AI Response",
                title_align="left",
                border_style="green",
                box=box.ROUNDED,
                padding=(0, 1)
            )
            
            console.print()
            console.print(ai_panel)
            console.print()
            return
        
        # Handle user commands specially
        elif "Processing command:" in message:
            command_text = message.split(": ", 1)[1] if ": " in message else message
            
            command_panel = Panel(
                Text(command_text, style="bright_blue bold"),
                title="📝 User Command",
                title_align="left",
                border_style="blue",
                box=box.SIMPLE,
                padding=(0, 1)
            )
            
            console.print(command_panel)
            return
        
        # For all other messages, use the standard Rich handler
        super().emit(record)

def setup_rich_logging(app_name: str, log_file: str, debug: bool = False) -> logging.Logger:
    """Set up Rich logging for Julie Julie."""
    
    # Create logger
    logger = logging.getLogger(app_name.lower().replace(' ', '_'))
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with Rich
    console_handler = JulieJulieRichHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler without Rich (plain text)
    import os
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Prevent propagation to avoid duplicate messages
    logger.propagate = False
    
    return logger

def print_startup_banner(app_name: str, version: str):
    """Print a beautiful startup banner."""
    title_text = Text(f"{app_name} v{version}", style="bold magenta")
    subtitle_text = Text("Voice Assistant Ready", style="dim cyan")
    
    banner = Panel(
        Align.center(f"[bold magenta]{app_name} v{version}[/]\n[dim cyan]Voice Assistant Ready[/]"),
        title="🚀 Starting",
        border_style="magenta",
        box=box.DOUBLE
    )
    
    console.print()
    console.print(banner)
    console.print()

def print_status_message(message: str, status_type: str = "info"):
    """Print a status message with appropriate styling."""
    styles = {
        "info": ("ℹ️", "cyan"),
        "success": ("✅", "green"),
        "warning": ("⚠️", "yellow"),
        "error": ("❌", "red")
    }
    
    icon, color = styles.get(status_type, ("ℹ️", "cyan"))
    console.print(f"[{color}]{icon} {message}[/]")

def print_ai_thinking():
    """Show a thinking indicator for AI processing."""
    console.print("[dim yellow]🤔 Thinking...[/]")

# Legacy function names for compatibility
def setup_colored_logging(app_name: str, log_file: str, debug: bool = False) -> logging.Logger:
    """Legacy function name - redirects to Rich logging."""
    return setup_rich_logging(app_name, log_file, debug)

def log_ai_response(text: str, logger: logging.Logger):
    """Log AI response with special formatting."""
    logger.info(f"Speaking sentence: {text}")

def log_user_command(command: str, logger: logging.Logger):
    """Log user command with special formatting."""
    logger.info(f"Processing command: {command}")

def log_success(message: str, logger: logging.Logger):
    """Log success message with special formatting."""
    logger.info(message)

def log_error(message: str, logger: logging.Logger):
    """Log error message with special formatting."""
    logger.error(message)
