"""
I/O components for String_Multitool.
"""

from .clipboard import ClipboardMonitor
from .manager import InputOutputManager

__all__ = [
    "InputOutputManager",
    "ClipboardMonitor",
]
