#!/usr/bin/env python3
"""
String_Multitool - Advanced text transformation tool with pipe support and RSA encryption.

A powerful command-line text transformation tool with intuitive rule-based syntax,
pipe support, and secure RSA encryption capabilities.

This is the new modular version with improved architecture, type safety,
and comprehensive error handling.

Usage:
    String_Multitool.py                          # Interactive mode (clipboard input)
    String_Multitool.py /t/l                     # Apply trim + lowercase to clipboard
    echo "text" | String_Multitool.py            # Interactive mode (pipe input)
    echo "text" | String_Multitool.py /t/l       # Apply trim + lowercase to piped text
    String_Multitool.py /enc                     # Encrypt clipboard text with RSA
    String_Multitool.py /dec                     # Decrypt clipboard text with RSA
    String_Multitool.py --daemon                 # Daemon mode (continuous monitoring)

Author: String_Multitool Development Team
Version: 2.1.0 (Refactored)
License: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO

# Ensure UTF-8 encoding for stdout/stderr on Windows
if sys.platform.startswith('win'):
    # Type-safe reconfigure with proper type checking
    stdout: TextIO = sys.stdout
    stderr: TextIO = sys.stderr
    if hasattr(stdout, 'reconfigure') and hasattr(stderr, 'reconfigure'):
        try:
            stdout.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
            stderr.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            # Fallback for older Python versions or encoding issues
            pass

# Add the current directory to Python path for imports
current_dir: Path = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import and run the main application with dependency injection
from string_multitool.application_factory import ApplicationFactory

def main() -> None:
    """Main entry point with dependency injection."""
    app = ApplicationFactory.create_application()
    app.run()

if __name__ == "__main__":
    main()