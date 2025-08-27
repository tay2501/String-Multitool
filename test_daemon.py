#!/usr/bin/env python3
"""
Test script for daemon mode signal handling.
"""

import sys
import time
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from string_multitool.application_factory import ApplicationFactory


def main():
    """Test daemon mode functionality."""
    try:
        print("Creating application...")
        app = ApplicationFactory.create_application()
        
        print("Starting daemon mode...")
        if app.daemon_mode:
            app.daemon_mode.start_monitoring()
        else:
            print("Daemon mode not available")
            
    except KeyboardInterrupt:
        print("\nTest completed - Ctrl+C handled successfully!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()