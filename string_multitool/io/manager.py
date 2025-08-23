"""
Input/Output management for String_Multitool.

This module handles all input and output operations including
clipboard access and pipe input detection.
"""

from __future__ import annotations

import sys
from typing import Final

from ..core.types import IOManagerProtocol
from ..exceptions import ClipboardError

# Import logging utilities
from ..utils.logger import get_logger, log_debug, log_error, log_info, log_warning

try:
    import pyperclip

    _clipboard_available = True
except ImportError:
    _clipboard_available = False

CLIPBOARD_AVAILABLE: Final[bool] = _clipboard_available


class InputOutputManager:
    """Manages input and output operations for the application.

    This class provides centralized I/O handling with proper error
    management and fallback mechanisms.
    """

    def __init__(self) -> None:
        """Initialize the I/O manager."""
        # Instance variable annotations following PEP 526
        self.clipboard_available: bool = CLIPBOARD_AVAILABLE

    def get_input_text(self) -> str:
        """Get input text from the most appropriate source.

        Determines whether to read from stdin (pipe) or clipboard
        based on the execution context.

        Returns:
            Input text from pipe or clipboard

        Raises:
            ClipboardError: If clipboard operations fail
        """
        try:
            if not sys.stdin.isatty():
                # Input is piped
                return sys.stdin.read().strip()
            else:
                # No pipe input, use clipboard
                return self.get_clipboard_text()

        except Exception as e:
            raise ClipboardError(
                f"Failed to get input text: {e}",
                {"stdin_isatty": sys.stdin.isatty(), "error_type": type(e).__name__},
            ) from e

    def get_clipboard_text(self) -> str:
        """Get text from clipboard with multiple fallback methods.

        Returns:
            Current clipboard content

        Raises:
            ClipboardError: If all clipboard access methods fail
        """
        if not CLIPBOARD_AVAILABLE:
            raise ClipboardError("Clipboard functionality not available")

        # Method 1: pyperclip with retry mechanism
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                content = pyperclip.paste()
                return content if content is not None else ""
            except Exception as e:
                last_error = e
                if attempt < 2:  # Don't sleep on last attempt
                    import time
                    time.sleep(0.1 * (attempt + 1))  # Progressive delay

        # Method 2: tkinter fallback
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide window
            content = root.clipboard_get()
            root.destroy()
            return content if content is not None else ""
        except Exception:
            pass

        # Method 3: PowerShell fallback (Windows)
        try:
            import subprocess
            import sys
            if sys.platform == "win32":
                result = subprocess.run(
                    ["powershell", "-Command", "Get-Clipboard"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip()
        except Exception:
            pass

        # Method 4: Windows clip command fallback
        try:
            import subprocess
            import sys
            if sys.platform == "win32":
                # Use echo to get clipboard content via pipeline
                result = subprocess.run(
                    ["cmd", "/c", "echo off && powershell Get-Clipboard"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip()
        except Exception:
            pass

        raise ClipboardError(
            f"Failed to read from clipboard after trying all methods: {last_error}",
            {"error_type": type(last_error).__name__ if last_error else "Unknown", "methods_tried": 4}
        ) from last_error

    @staticmethod
    def set_output_text(text: str) -> None:
        """Set output text to clipboard with multiple fallback methods.

        Args:
            text: Text to copy to clipboard

        Raises:
            ClipboardError: If all clipboard copy methods fail
        """
        if not CLIPBOARD_AVAILABLE:
            raise ClipboardError("Clipboard functionality not available")

        logger = get_logger(__name__)
        
        # Method 1: pyperclip with retry mechanism
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                pyperclip.copy(text)
                log_debug(logger, "[SUCCESS] Text copied to clipboard via pyperclip")
                return
            except Exception as e:
                last_error = e
                if attempt < 2:  # Don't sleep on last attempt
                    import time
                    time.sleep(0.1 * (attempt + 1))  # Progressive delay

        # Method 2: tkinter fallback
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide window
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()  # Required to finalize clipboard operation
            root.destroy()
            log_debug(logger, "[SUCCESS] Text copied to clipboard via tkinter")
            return
        except Exception:
            pass

        # Method 3: PowerShell fallback (Windows)
        try:
            import subprocess
            import sys
            if sys.platform == "win32":
                result = subprocess.run(
                    ["powershell", "-Command", f"Set-Clipboard -Value '{text}'"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    log_debug(logger, "[SUCCESS] Text copied to clipboard via PowerShell")
                    return
        except Exception:
            pass

        # Method 4: Windows clip command fallback
        try:
            import subprocess
            import sys
            if sys.platform == "win32":
                result = subprocess.run(
                    ["cmd", "/c", "clip"],
                    input=text,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    log_debug(logger, "[SUCCESS] Text copied to clipboard via clip command")
                    return
        except Exception:
            pass

        raise ClipboardError(
            f"Failed to copy to clipboard after trying all methods: {last_error}",
            {"text_length": len(text), "error_type": type(last_error).__name__ if last_error else "Unknown", "methods_tried": 4}
        ) from last_error

    def get_pipe_input(self) -> str | None:
        """Get input from pipe if available.

        Returns:
            Piped input text or None if no pipe input
        """
        try:
            if not sys.stdin.isatty():
                # Input is piped
                return sys.stdin.read().strip()
            else:
                # No pipe input available
                return None

        except Exception:
            # If there's any error reading from stdin, return None
            return None
