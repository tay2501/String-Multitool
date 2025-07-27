#!/usr/bin/env python3
"""
Clipboard Transformer - Text transformation tool with pipe and argument support.

Usage:
    app.py                          # Interactive mode (clipboard input)
    app.py /t/l                     # Apply trim + lowercase to clipboard
    echo "text" | app.py            # Interactive mode (pipe input)
    echo "text" | app.py /t/l       # Apply trim + lowercase to piped text
"""

import sys
import re
import pyperclip
from typing import List, Optional, Callable


class TextTransformer:
    """Text transformation engine with rule-based processing."""
    
    def __init__(self):
        """Initialize the transformer with available rules."""
        self.rules = {
            # Basic transformations
            'uh': ('Underbar to Hyphen', self._underbar_to_hyphen),
            'hu': ('Hyphen to Underbar', self._hyphen_to_underbar),
            'fh': ('Full-width to Half-width', self._fullwidth_to_halfwidth),
            'hf': ('Half-width to Full-width', self._halfwidth_to_fullwidth),
            
            # Case transformations
            'l': ('Lowercase', self._lowercase),
            'u': ('Uppercase', self._uppercase),
            'p': ('Pascalcase', self._pascalcase),
            'c': ('Camelcase', self._camelcase),
            's': ('Snakecase', self._snakecase),
            'a': ('Capitalize', self._capitalize),
            
            # String operations
            't': ('Trim', self._trim),
            'r': ('Reverse', self._reverse),
            'si': ('SQL IN Clause', self._sql_in_clause),
            'dlb': ('Delete Line Breaks', self._delete_line_breaks),
        }
        
        # Rules with arguments
        self.arg_rules = {
            'S': ('Slugify', self._slugify),
            'R': ('Replace', self._replace),
        }
    
    def _underbar_to_hyphen(self, text: str) -> str:
        """Convert underscores to hyphens."""
        return text.replace('_', '-')
    
    def _hyphen_to_underbar(self, text: str) -> str:
        """Convert hyphens to underscores."""
        return text.replace('-', '_')
    
    def _fullwidth_to_halfwidth(self, text: str) -> str:
        """Convert full-width characters to half-width."""
        # Full-width to half-width mapping (including hyphen)
        fullwidth = "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚー－"
        halfwidth = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz--"
        return text.translate(str.maketrans(fullwidth, halfwidth))
    
    def _halfwidth_to_fullwidth(self, text: str) -> str:
        """Convert half-width characters to full-width."""
        # Half-width to full-width mapping (including hyphen)
        halfwidth = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-"
        fullwidth = "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ－"
        return text.translate(str.maketrans(halfwidth, fullwidth))
    
    def _lowercase(self, text: str) -> str:
        """Convert to lowercase."""
        return text.lower()
    
    def _uppercase(self, text: str) -> str:
        """Convert to uppercase."""
        return text.upper()
    
    def _pascalcase(self, text: str) -> str:
        """Convert to PascalCase and remove non-word/non-digit chars."""
        # Remove non-word and non-digit chars, split by spaces/punctuation
        words = re.findall(r'[a-zA-Z0-9]+', text)
        return ''.join(word.capitalize() for word in words)
    
    def _camelcase(self, text: str) -> str:
        """Convert to camelCase and remove non-word/non-digit chars."""
        # Remove non-word and non-digit chars, split by spaces/punctuation
        words = re.findall(r'[a-zA-Z0-9]+', text)
        if not words:
            return text
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    def _snakecase(self, text: str) -> str:
        """Convert to snake_case."""
        # Replace spaces and punctuation with underscores, then lowercase
        result = re.sub(r'[^a-zA-Z0-9]+', '_', text)
        result = re.sub(r'_+', '_', result)  # Remove multiple underscores
        result = result.strip('_').lower()
        return result
    
    def _capitalize(self, text: str) -> str:
        """Capitalize first char of each word."""
        return text.title()
    
    def _trim(self, text: str) -> str:
        """Trim whitespace from beginning and end."""
        return text.strip()
    
    def _reverse(self, text: str) -> str:
        """Reverse the string."""
        return text[::-1]
    
    def _sql_in_clause(self, text: str) -> str:
        """Convert line-separated text to SQL IN clause format with preserved line breaks."""
        # Split by line breaks (handle both \r\n and \n)
        lines = text.replace('\r\n', '\n').split('\n')
        # Filter out empty lines and quote each line
        quoted_lines = [f"'{line.strip()}'" for line in lines if line.strip()]
        # Join with comma and CRLF
        return ',\r\n'.join(quoted_lines)
    
    def _delete_line_breaks(self, text: str) -> str:
        """Delete all line breaks from text."""
        # Remove all types of line breaks
        return text.replace('\r\n', '').replace('\r', '').replace('\n', '')
    
    def _slugify(self, text: str, replacement: str = '-') -> str:
        """Remove non-word/non-digit chars and merge with replacement."""
        # Remove all non-word and non-digit chars, replace with replacement
        result = re.sub(r'[^a-zA-Z0-9]+', replacement, text)
        result = re.sub(f'{re.escape(replacement)}+', replacement, result)  # Remove multiple replacements
        return result.strip(replacement)
    
    def _replace(self, text: str, substring: str, replacement: str = '') -> str:
        """Replace all substring occurrences with replacement."""
        return text.replace(substring, replacement)
    
    def parse_rules(self, rule_string: str) -> List[tuple]:
        """Parse rule string into list of (rule, args) tuples."""
        if not rule_string.startswith('/'):
            raise ValueError("Rules must start with '/'")
        
        # Use regex to parse rules and arguments properly
        # Pattern: /rule or /rule 'arg1' 'arg2'
        pattern = r"/([a-zA-Z]+)(?:\s+'([^']*)'(?:\s+'([^']*)')?)?|/([a-zA-Z]+)"
        matches = re.findall(pattern, rule_string)
        
        parsed_rules = []
        for match in matches:
            if match[0]:  # Rule with potential arguments
                rule = match[0]
                args = [arg for arg in match[1:3] if arg]  # Get non-empty args
            elif match[3]:  # Rule without arguments
                rule = match[3]
                args = []
            else:
                continue
            
            if rule in self.rules:
                parsed_rules.append((rule, []))
            elif rule in self.arg_rules:
                parsed_rules.append((rule, args))
            else:
                raise ValueError(f"Unknown rule: {rule}")
        
        if not parsed_rules:
            raise ValueError("No valid rules found")
        
        return parsed_rules
    
    def apply_rules(self, text: str, rule_string: str) -> str:
        """Apply transformation rules to text."""
        parsed_rules = self.parse_rules(rule_string)
        result = text
        
        for rule, args in parsed_rules:
            if rule in self.rules:
                result = self.rules[rule][1](result)
            elif rule in self.arg_rules:
                result = self.arg_rules[rule][1](result, *args)
        
        return result
    
    def get_available_rules(self) -> dict:
        """Get all available rules with descriptions."""
        all_rules = {}
        
        # No-arg rules
        for rule, (desc, _) in self.rules.items():
            all_rules[rule] = f"/{rule} - {desc}"
        
        # Arg rules
        for rule, (desc, _) in self.arg_rules.items():
            all_rules[rule] = f"/{rule} '<args>' - {desc}"
        
        return all_rules


def get_input_text() -> str:
    """Get input text from stdin or clipboard."""
    if not sys.stdin.isatty():
        # Reading from pipe
        return sys.stdin.read().rstrip('\n\r')
    else:
        # Reading from clipboard
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Error reading clipboard: {e}", file=sys.stderr)
            sys.exit(1)


def set_output_text(text: str) -> None:
    """Set output text to clipboard."""
    try:
        pyperclip.copy(text)
        print("✅ Text copied to clipboard")
    except Exception as e:
        print(f"Error copying to clipboard: {e}", file=sys.stderr)
        sys.exit(1)


def show_help():
    """Show help message."""
    transformer = TextTransformer()
    rules = transformer.get_available_rules()
    
    print("📋 Clipboard Transformer")
    print("=" * 50)
    print()
    print("Usage:")
    print("  String_Multitool.py                    # Interactive mode (clipboard input)")
    print("  String_Multitool.py /t/l               # Apply trim + lowercase to clipboard")
    print("  echo 'text' | String_Multitool.py      # Interactive mode (pipe input)")
    print("  echo 'text' | String_Multitool.py /t/l # Apply trim + lowercase to piped text")
    print()
    print("Available Rules:")
    print("-" * 30)
    
    # Group rules by category
    categories = {
        "Basic Transformations": ['uh', 'hu', 'fh', 'hf'],
        "Case Transformations": ['l', 'u', 'p', 'c', 's', 'a'],
        "String Operations": ['t', 'r', 'si', 'dlb'],
        "Advanced (with args)": ['S', 'R']
    }
    
    for category, rule_list in categories.items():
        print(f"\n{category}:")
        for rule in rule_list:
            if rule in rules:
                print(f"  {rules[rule]}")
    
    print()
    print("Examples:")
    print("  /t                        # Trim whitespace")
    print("  /t/l                      # Trim then lowercase")
    print("  /S '-'                    # Slugify with hyphen")
    print("  /R 'old' 'new'            # Replace 'old' with 'new'")


def interactive_mode(input_text: str):
    """Run in interactive mode."""
    transformer = TextTransformer()
    
    print("📋 Clipboard Transformer - Interactive Mode")
    print("=" * 45)
    print(f"Input text: '{input_text[:50]}{'...' if len(input_text) > 50 else ''}'")
    print()
    print("Enter transformation rules (e.g., /t/l) or 'help' for available rules:")
    
    while True:
        try:
            rule_input = input("Rules: ").strip()
            
            if not rule_input:
                print("Please enter a rule or 'help'")
                continue
            
            if rule_input.lower() in ['help', 'h', '?']:
                show_help()
                continue
            
            if rule_input.lower() in ['quit', 'q', 'exit']:
                print("Goodbye!")
                break
            
            # Apply transformation
            result = transformer.apply_rules(input_text, rule_input)
            set_output_text(result)
            
            print(f"Result: '{result[:100]}{'...' if len(result) > 100 else ''}'")
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Type 'help' for available rules")


def main():
    """Main application entry point."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            show_help()
            return
        
        # Rules provided as argument - join all arguments to handle quoted strings
        rule_string = ' '.join(sys.argv[1:])
        input_text = get_input_text()
        
        try:
            transformer = TextTransformer()
            result = transformer.apply_rules(input_text, rule_string)
            set_output_text(result)
            print(f"✅ Applied: {rule_string}")
            print(f"Result: '{result[:100]}{'...' if len(result) > 100 else ''}'")
            print("📋 Result copied to clipboard!")
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Interactive mode
        input_text = get_input_text()
        interactive_mode(input_text)


if __name__ == "__main__":
    main()