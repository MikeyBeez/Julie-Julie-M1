"""
Utility for capturing stdout to prevent unwanted text output.
"""

import sys
import io
from contextlib import contextmanager

@contextmanager
def capture_stdout():
    """Context manager to capture and suppress stdout."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()
    try:
        yield captured_output
    finally:
        sys.stdout = old_stdout

@contextmanager
def suppress_stdout():
    """Context manager to completely suppress stdout."""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout
