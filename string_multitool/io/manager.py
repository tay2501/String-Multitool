"""
Input/Output management for String_Multitool.

This module handles all input and output operations including
clipboard access and pipe input detection.
"""

import sys
from typing import Any

from ..exceptions import ClipboardError
from ..core.types import IOManagerProtocol

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


class InputOutputManager:
    """Manages input and output operations for the application.
    
    This class provides centralized I/O handling with proper error
    management and fallback mechanisms.
    """
    
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
                {"stdin_isatty": sys.stdin.isatty(), "error_type": type(e).__name__}
            ) from e
    
    def get_clipboard_text(self) -> str:
        """Get text from clipboard.
        
        Returns:
            Current clipboard content
            
        Raises:
            ClipboardError: If clipboard access fails
        """
        if not CLIPBOARD_AVAILABLE:
            raise ClipboardError("Clipboard functionality not available")
        
        try:
            content = pyperclip.paste()
            return content if content is not None else ""
            
        except Exception as e:
            raise ClipboardError(
                f"Failed to read from clipboard: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    @staticmethod
    def set_output_text(text: str) -> None:
        """Set output text to clipboard.
        
        Args:
            text: Text to copy to clipboard
            
        Raises:
            ClipboardError: If clipboard operation fails
        """
        if not CLIPBOARD_AVAILABLE:
            raise ClipboardError("Clipboard functionality not available")
        
        try:
            pyperclip.copy(text)
            print("✅ Text copied to clipboard")
            
        except Exception as e:
            raise ClipboardError(
                f"Error copying to clipboard: {e}",
                {"text_length": len(text), "error_type": type(e).__name__}
            ) from e