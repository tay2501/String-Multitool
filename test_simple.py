#!/usr/bin/env python3
"""Simple test for Unicode handling."""

import sys
from string_multitool.io.manager import InputOutputManager

def test_unicode_input():
    """Test Unicode input processing."""
    test_input = " Te Sｔ- _　  "
    
    print(f"Original: {repr(test_input)}")
    print(f"Stripped: {repr(test_input.strip())}")
    
    # Test direct encoding/decoding
    try:
        # Simulate the problematic encoding scenario
        # Convert to bytes and back with different encodings
        utf8_bytes = test_input.encode('utf-8')
        print(f"UTF-8 bytes: {utf8_bytes}")
        
        # Decode with errors='replace'
        decoded = utf8_bytes.decode('utf-8', errors='replace')
        print(f"Decoded: {repr(decoded)}")
        print(f"Stripped decoded: {repr(decoded.strip())}")
        
    except Exception as e:
        print(f"Encoding test failed: {e}")

if __name__ == "__main__":
    test_unicode_input()