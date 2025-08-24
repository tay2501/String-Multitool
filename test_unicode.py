#!/usr/bin/env python3
"""Test Unicode handling in String_Multitool."""

import sys
import subprocess

def test_unicode_pipe():
    """Test Unicode input through pipe."""
    test_input = " Te Sｔ- _　  "
    
    # Test the corrected version
    try:
        result = subprocess.run(
            [sys.executable, "String_Multitool.py", "/t"],
            input=test_input,
            text=True,
            capture_output=True,
            encoding='utf-8',
            errors='replace'
        )
        
        print(f"Input: {repr(test_input)}")
        print(f"Output: {repr(result.stdout)}")
        print(f"Expected: {repr(test_input.strip())}")
        print(f"Success: {result.stdout.strip() == test_input.strip()}")
        
        if result.stderr:
            print(f"Stderr: {result.stderr}")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_unicode_pipe()