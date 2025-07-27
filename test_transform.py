#!/usr/bin/env python3
"""
Test script for the new transformation rules.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from String_Multitool import TextTransformer

def test_transformations():
    """Test all transformation rules."""
    transformer = TextTransformer()
    
    print("🧪 Testing Transformations")
    print("=" * 50)
    
    # Test cases for no-arg rules
    test_cases = [
        ('/uh', 'TBL_CHA1', 'TBL-CHA1'),
        ('/hu', 'TBL-CHA1', 'TBL_CHA1'),
        ('/fh', 'ＴＢＬ－ＣＨＡ１', 'TBL-CHA1'),
        ('/hf', 'TBL-CHA1', 'ＴＢＬ－ＣＨＡ１'),
        ('/l', 'SAY HELLO TO MY LITTLE FRIEND!', 'say hello to my little friend!'),
        ('/u', 'Can you hear me, Major Tom?', 'CAN YOU HEAR ME, MAJOR TOM?'),
        ('/p', 'The quick brown fox jumps over the lazy dog', 'TheQuickBrownFoxJumpsOverTheLazyDog'),
        ('/c', 'is error state!', 'isErrorState'),
        ('/s', 'is error state!', 'is_error_state'),
        ('/t', '  Well, something is happening  ', 'Well, something is happening'),
        ('/a', 'the quick brown fox jumps over the lazy dog', 'The Quick Brown Fox Jumps Over The Lazy Dog'),
        ('/r', 'hello', 'olleh'),
        ('/si', 'A0001\r\nA0002\r\nA0003', "'A0001',\r\n'A0002',\r\n'A0003'"),
        ('/dlb', 'A0001\r\nA0002\r\nA0003', 'A0001A0002A0003'),
        ('/t/l', '  HELLO WORLD  ', 'hello world'),
        ('/s/u', 'The Quick Brown Fox', 'THE_QUICK_BROWN_FOX'),
    ]
    
    for rule, input_text, expected in test_cases:
        try:
            result = transformer.apply_rules(input_text, rule)
            status = "✅" if result == expected else "❌"
            print(f"{status} {rule}: '{input_text}' → '{result}'")
            if result != expected:
                print(f"   Expected: '{expected}'")
        except Exception as e:
            print(f"❌ {rule}: Error - {e}")
    
    print("\n🔧 Testing Argument-based Transformations")
    print("=" * 50)
    
    # Test argument-based rules
    arg_test_cases = [
        ("/S '+'", 'http://foo.bar/baz/brrr', 'http+foo+bar+baz+brrr'),
        ("/R 'Will' 'Bill'", "I'm Will, Will's son", "I'm Bill, Bill's son"),
        ("/S", 'hello world test', 'hello-world-test'),  # Default replacement
        ("/R 'this'", 'remove this text', 'remove  text'),  # Default replacement (empty)
    ]
    
    for rule, input_text, expected in arg_test_cases:
        try:
            result = transformer.apply_rules(input_text, rule)
            status = "✅" if result == expected else "❌"
            print(f"{status} {rule}: '{input_text}' → '{result}'")
            if result != expected:
                print(f"   Expected: '{expected}'")
        except Exception as e:
            print(f"❌ {rule}: Error - {e}")

if __name__ == "__main__":
    test_transformations()