"""
Input/Output management for String_Multitool.

This module handles all input and output operations including
clipboard access and pipe input detection.
"""

from __future__ import annotations

import sys
from contextlib import suppress
from typing import Final

from ..exceptions import ClipboardError

# Import logging utilities
from ..utils.unified_logger import get_logger, log_debug

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
                # Input is piped - ensure UTF-8 encoding
                try:
                    # First try to read with current encoding
                    raw_input: str = sys.stdin.read()

                    # If the input contains decode errors, try to fix them
                    if isinstance(raw_input, str) and "\udcef" in raw_input:
                        # Raw bytes were decoded incorrectly, need to handle encoding
                        # Read the buffer content directly as bytes and decode properly

                        # Try to decode with UTF-8 error handling
                        try:
                            # Encode back to bytes using latin-1 to preserve raw bytes
                            raw_bytes = raw_input.encode("latin-1", errors="ignore")
                            # Decode as UTF-8 with error handling
                            corrected_input = raw_bytes.decode("utf-8", errors="replace")
                            return str(corrected_input.strip())
                        except (UnicodeDecodeError, UnicodeEncodeError):
                            # Fallback to original input with replacement chars removed
                            return str(
                                raw_input.replace("\udcef", "")
                                .replace("\udc94", "")
                                .replace("\udc80", "")
                                .strip()
                            )

                    return str(raw_input.strip())

                except (UnicodeDecodeError, UnicodeEncodeError) as encoding_error:
                    # If encoding fails, try reading with explicit UTF-8
                    try:
                        import io

                        utf8_stdin = io.TextIOWrapper(
                            sys.stdin.buffer, encoding="utf-8", errors="replace"
                        )
                        return utf8_stdin.read().strip()
                    except Exception:
                        # Final fallback - return with replacement characters
                        return str(encoding_error).strip()
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
        with suppress(Exception):
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()  # Hide window
            content = root.clipboard_get()
            root.destroy()
            return content if content is not None else ""

        # Method 3: PowerShell fallback (Windows)
        with suppress(Exception):
            import subprocess
            import sys

            if sys.platform == "win32":
                result = subprocess.run(
                    ["powershell", "-Command", "Get-Clipboard"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return result.stdout.strip()

        # Method 4: Windows clip command fallback
        with suppress(Exception):
            import subprocess
            import sys

            if sys.platform == "win32":
                # Use echo to get clipboard content via pipeline
                result = subprocess.run(
                    ["cmd", "/c", "echo off && powershell Get-Clipboard"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return result.stdout.strip()

        raise ClipboardError(
            f"Failed to read from clipboard after trying all methods: {last_error}",
            {
                "error_type": type(last_error).__name__ if last_error else "Unknown",
                "methods_tried": 4,
            },
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
        with suppress(Exception):
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()  # Hide window
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()  # Required to finalize clipboard operation
            root.destroy()
            log_debug(logger, "[SUCCESS] Text copied to clipboard via tkinter")
            return

        # Method 3: PowerShell fallback (Windows)
        with suppress(Exception):
            import subprocess
            import sys

            if sys.platform == "win32":
                result = subprocess.run(
                    ["powershell", "-Command", f"Set-Clipboard -Value '{text}'"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    log_debug(logger, "[SUCCESS] Text copied to clipboard via PowerShell")
                    return

        # Method 4: Windows clip command fallback
        with suppress(Exception):
            import subprocess
            import sys

            if sys.platform == "win32":
                result = subprocess.run(
                    ["cmd", "/c", "clip"], check=False, input=text, text=True, timeout=5
                )
                if result.returncode == 0:
                    log_debug(logger, "[SUCCESS] Text copied to clipboard via clip command")
                    return

        raise ClipboardError(
            f"Failed to copy to clipboard after trying all methods: {last_error}",
            {
                "text_length": len(text),
                "error_type": type(last_error).__name__ if last_error else "Unknown",
                "methods_tried": 4,
            },
        ) from last_error

    def get_pipe_input(self) -> str | None:
        """Get input from pipe if available.

        Returns:
            Piped input text or None if no pipe input
        """
        try:
            if not sys.stdin.isatty():
                # Input is piped - ensure UTF-8 encoding
                try:
                    # First try to read with current encoding
                    raw_input: str = sys.stdin.read()

                    # If the input contains decode errors, try to fix them
                    if isinstance(raw_input, str) and "\udcef" in raw_input:
                        # Raw bytes were decoded incorrectly, need to handle encoding
                        try:
                            # Encode back to bytes using latin-1 to preserve raw bytes
                            raw_bytes = raw_input.encode("latin-1", errors="ignore")
                            # Decode as UTF-8 with error handling
                            corrected_input = raw_bytes.decode("utf-8", errors="replace")
                            return str(corrected_input.strip())
                        except (UnicodeDecodeError, UnicodeEncodeError):
                            # Fallback to original input with replacement chars removed
                            return str(
                                raw_input.replace("\udcef", "")
                                .replace("\udc94", "")
                                .replace("\udc80", "")
                                .strip()
                            )

                    return str(raw_input.strip())

                except (UnicodeDecodeError, UnicodeEncodeError):
                    # If encoding fails, try reading with explicit UTF-8
                    try:
                        import io

                        utf8_stdin = io.TextIOWrapper(
                            sys.stdin.buffer, encoding="utf-8", errors="replace"
                        )
                        return utf8_stdin.read().strip()
                    except Exception:
                        # Final fallback - return None
                        return None
            else:
                # No pipe input available
                return None

        except Exception:
            # If there's any error reading from stdin, return None
            return None
