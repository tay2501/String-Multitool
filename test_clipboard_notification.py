#!/usr/bin/env python3
"""
Test script to verify clipboard change notification with content preview.
"""

import time
import subprocess
import sys

def set_clipboard(content):
    """Set clipboard content using PowerShell."""
    try:
        subprocess.run([
            "powershell", "-Command", 
            f"echo '{content}' | Set-Clipboard"
        ], check=True, capture_output=True)
        print(f"✅ Set clipboard to: '{content}'")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set clipboard: {e}")
        return False

def main():
    print("🧪 Clipboard Notification Test")
    print("=" * 40)
    print("This script will change clipboard content to test notifications.")
    print("Start String_Multitool.py in another terminal, then press Enter here.")
    
    input("Press Enter to start test...")
    
    test_contents = [
        "Hello World!",
        "This is a longer text content to test the preview functionality",
        "Short",
        "Multi\nLine\nContent\nWith\nBreaks",
        "Special chars: !@#$%^&*()_+-={}[]|\\:;\"'<>?,./"
    ]
    
    for i, content in enumerate(test_contents, 1):
        print(f"\n📋 Test {i}/5: Setting clipboard content...")
        if set_clipboard(content):
            print(f"   Expected notification: 🔔 Clipboard changed! New content available ({len(content)} chars)")
            preview = content[:100] + "..." if len(content) > 100 else content
            preview = preview.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            print(f"   Expected content: '{preview}'")
        
        print("   Check String_Multitool for notification...")
        time.sleep(3)
    
    print("\n✅ Test completed!")
    print("Check String_Multitool terminal for notifications with content previews.")

if __name__ == "__main__":
    main()