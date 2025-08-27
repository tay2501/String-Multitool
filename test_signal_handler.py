#!/usr/bin/env python3
"""
Simple test for signal handling verification.
"""

import signal
import threading
import time
import sys


def main():
    """Test signal handling."""
    shutdown_event = threading.Event()
    
    def signal_handler(signum, frame):
        print(f"\n[TEST] Received signal {signum}, shutting down gracefully...")
        shutdown_event.set()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("[TEST] Signal handler test active. Press Ctrl+C to test graceful shutdown.")
    
    try:
        while not shutdown_event.is_set():
            shutdown_event.wait(timeout=0.1)
    except KeyboardInterrupt:
        print("\n[TEST] KeyboardInterrupt caught, shutting down...")
        shutdown_event.set()
    finally:
        print("[TEST] Cleanup completed!")
    
    print("[TEST] Test completed successfully!")


if __name__ == "__main__":
    main()