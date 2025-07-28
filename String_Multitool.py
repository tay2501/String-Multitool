#!/usr/bin/env python3
"""
Clipboard Transformer - Text transformation tool with pipe and argument support.

Usage:
    app.py                          # Interactive mode (clipboard input)
    app.py /t/l                     # Apply trim + lowercase to clipboard
    echo "text" | app.py            # Interactive mode (pipe input)
    echo "text" | app.py /t/l       # Apply trim + lowercase to piped text
    app.py /enc                     # Encrypt clipboard text with RSA
    app.py /dec                     # Decrypt clipboard text with RSA
"""

import sys
import re
import pyperclip
import os
import base64
from pathlib import Path
from typing import List, Optional, Callable

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    import secrets
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


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
            
            # Encryption/Decryption
            'enc': ('RSA Encrypt', self._rsa_encrypt),
            'dec': ('RSA Decrypt', self._rsa_decrypt),
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
    
    def _ensure_rsa_keys(self) -> tuple:
        """Ensure RSA key pair exists, create if not found."""
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography library not installed. Run: pip install cryptography>=41.0.0")
        
        rsa_dir = Path("rsa")
        private_key_path = rsa_dir / "rsa"
        public_key_path = rsa_dir / "rsa.pub"
        
        # Create rsa directory if it doesn't exist
        rsa_dir.mkdir(exist_ok=True)
        
        # Check if keys exist
        if private_key_path.exists() and public_key_path.exists():
            try:
                # Load existing keys
                with open(private_key_path, 'rb') as f:
                    private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None
                    )
                
                with open(public_key_path, 'rb') as f:
                    public_key = serialization.load_pem_public_key(f.read())
                
                print("Using existing RSA key pair")
                return private_key, public_key
                
            except Exception as e:
                print(f"Warning: Error loading existing keys: {e}")
                print("Generating new key pair...")
        
        # Generate new key pair
        print("Generating new RSA key pair...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        # Save private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        with open(private_key_path, 'wb') as f:
            f.write(private_pem)
        
        # Save public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(public_key_path, 'wb') as f:
            f.write(public_pem)
        
        # Set appropriate permissions (readable only by owner)
        try:
            os.chmod(private_key_path, 0o600)  # rw-------
            os.chmod(public_key_path, 0o644)   # rw-r--r--
        except OSError:
            pass  # Windows doesn't support chmod the same way
        
        print("RSA key pair generated and saved:")
        print(f"   Private key: {private_key_path}")
        print(f"   Public key:  {public_key_path}")
        
        return private_key, public_key
    
    def _rsa_encrypt(self, text: str) -> str:
        """Encrypt text using hybrid encryption (AES + RSA)."""
        try:
            private_key, public_key = self._ensure_rsa_keys()
            
            # Convert text to bytes
            text_bytes = text.encode('utf-8')
            
            # Use hybrid encryption for any size text
            # Generate random AES key (256-bit)
            aes_key = secrets.token_bytes(32)  # 256 bits
            
            # Generate random IV for AES
            iv = secrets.token_bytes(16)  # 128 bits
            
            # Encrypt the text with AES
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Pad the text to be multiple of 16 bytes (AES block size)
            padding_length = 16 - (len(text_bytes) % 16)
            padded_text = text_bytes + bytes([padding_length] * padding_length)
            
            # Encrypt the text
            encrypted_text = encryptor.update(padded_text) + encryptor.finalize()
            
            # Encrypt the AES key with RSA
            encrypted_aes_key = public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Combine encrypted AES key, IV, and encrypted text
            # Format: [encrypted_aes_key_length(4 bytes)][encrypted_aes_key][iv(16 bytes)][encrypted_text]
            encrypted_aes_key_length = len(encrypted_aes_key).to_bytes(4, byteorder='big')
            combined = encrypted_aes_key_length + encrypted_aes_key + iv + encrypted_text
            
            # Encode as base64 for text representation
            encrypted_b64 = base64.b64encode(combined).decode('ascii')
            
            print(f"Text encrypted successfully (hybrid AES+RSA, {len(text_bytes)} bytes)")
            return encrypted_b64
            
        except Exception as e:
            raise RuntimeError(f"Encryption failed: {e}")
    
    def _rsa_decrypt(self, text: str) -> str:
        """Decrypt text using hybrid decryption (AES + RSA)."""
        try:
            private_key, public_key = self._ensure_rsa_keys()
            
            # Clean the input text (remove whitespace, newlines, etc.)
            cleaned_text = ''.join(text.split())
            
            # Validate base64 format
            if not cleaned_text:
                raise ValueError("Empty encrypted text")
            
            # Debug: Check for invalid characters
            base64_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
            invalid_chars = [c for c in cleaned_text if c not in base64_chars]
            
            if invalid_chars:
                # Show first few invalid characters for debugging
                invalid_sample = invalid_chars[:5]
                raise ValueError(f"Text contains non-base64 characters: {invalid_sample} (found {len(invalid_chars)} invalid chars total)")
            
            # Fix base64 padding if necessary
            missing_padding = len(cleaned_text) % 4
            if missing_padding:
                cleaned_text += '=' * (4 - missing_padding)
            
            # Decode from base64
            try:
                encrypted_bytes = base64.b64decode(cleaned_text.encode('ascii'))
            except Exception as e:
                # Try with strict validation disabled
                try:
                    encrypted_bytes = base64.b64decode(cleaned_text.encode('ascii'), validate=False)
                except Exception as e2:
                    raise ValueError(f"Invalid base64 format: {e} (also tried without validation: {e2})")
            
            # Extract components
            # Format: [encrypted_aes_key_length(4 bytes)][encrypted_aes_key][iv(16 bytes)][encrypted_text]
            if len(encrypted_bytes) < 4:
                raise ValueError("Invalid encrypted data format")
            
            # Get encrypted AES key length
            encrypted_aes_key_length = int.from_bytes(encrypted_bytes[:4], byteorder='big')
            
            if len(encrypted_bytes) < 4 + encrypted_aes_key_length + 16:
                raise ValueError("Invalid encrypted data format")
            
            # Extract encrypted AES key
            encrypted_aes_key = encrypted_bytes[4:4 + encrypted_aes_key_length]
            
            # Extract IV
            iv = encrypted_bytes[4 + encrypted_aes_key_length:4 + encrypted_aes_key_length + 16]
            
            # Extract encrypted text
            encrypted_text = encrypted_bytes[4 + encrypted_aes_key_length + 16:]
            
            # Decrypt the AES key with RSA
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt the text with AES
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt the text
            padded_text = decryptor.update(encrypted_text) + decryptor.finalize()
            
            # Remove padding
            padding_length = padded_text[-1]
            if padding_length > 16 or padding_length == 0:
                raise ValueError("Invalid padding")
            
            # Verify padding
            for i in range(padding_length):
                if padded_text[-(i+1)] != padding_length:
                    raise ValueError("Invalid padding")
            
            decrypted_text = padded_text[:-padding_length].decode('utf-8')
            
            print(f"Text decrypted successfully (hybrid AES+RSA, {len(decrypted_text)} chars)")
            return decrypted_text
            
        except Exception as e:
            raise RuntimeError(f"Decryption failed: {e}")
    
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
        try:
            # Handle encoding properly for Windows
            import codecs
            if sys.platform.startswith('win'):
                sys.stdin.reconfigure(encoding='utf-8')
            return sys.stdin.read().rstrip('\n\r')
        except Exception:
            # Fallback to default encoding
            return sys.stdin.read().rstrip('\n\r')
    else:
        # Reading from clipboard
        try:
            clipboard_text = pyperclip.paste()
            # For encrypted data, we might need to preserve exact formatting
            # But for most cases, strip whitespace is fine
            return clipboard_text.strip() if clipboard_text else ""
        except Exception as e:
            print(f"Error reading clipboard: {e}", file=sys.stderr)
            sys.exit(1)


def set_output_text(text: str) -> None:
    """Set output text to clipboard."""
    try:
        pyperclip.copy(text)
        print("Text copied to clipboard")
    except Exception as e:
        print(f"Error copying to clipboard: {e}", file=sys.stderr)
        sys.exit(1)


def show_help():
    """Show help message."""
    transformer = TextTransformer()
    rules = transformer.get_available_rules()
    
    print("Clipboard Transformer")
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
        "Encryption/Decryption": ['enc', 'dec'],
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
    print("  /enc                      # Encrypt with RSA")
    print("  /dec                      # Decrypt with RSA")
    print("  /S '-'                    # Slugify with hyphen")
    print("  /R 'old' 'new'            # Replace 'old' with 'new'")
    print()
    print("RSA Encryption Notes:")
    print("  • Keys are auto-generated in rsa/ folder")
    print("  • Private key: rsa/rsa")
    print("  • Public key: rsa/rsa.pub")
    print("  • Uses hybrid encryption (AES+RSA) for any text size")
    print("  • Secure for both short and long texts")


def interactive_mode(input_text: str):
    """Run in interactive mode."""
    transformer = TextTransformer()
    
    print("Clipboard Transformer - Interactive Mode")
    print("=" * 45)
    print(f"Input text: '{input_text[:50]}{'...' if len(input_text) > 50 else ''}'")
    print()
    print("Enter transformation rules (e.g., /t/l) or 'help' for available rules:")
    
    while True:
        try:
            try:
                rule_input = input("Rules: ").strip()
            except EOFError:
                print("\nGoodbye!")
                break
            
            if not rule_input:
                print("Please enter a rule or 'help'")
                continue
            
            if rule_input.lower() in ['help', 'h', '?']:
                show_help()
                continue
            
            if rule_input.lower() in ['quit', 'q', 'exit']:
                print("Goodbye!")
                break
            
            # For decryption, get fresh clipboard content
            if rule_input.strip() == '/dec':
                current_input = get_input_text()
                result = transformer.apply_rules(current_input, rule_input)
            else:
                result = transformer.apply_rules(input_text, rule_input)
            
            set_output_text(result)
            
            # For encrypted data, show more characters to avoid truncation issues
            if rule_input.strip() == '/enc':
                print(f"Result: '{result}'")
                print("(Full encrypted text copied to clipboard)")
                # Update input_text for next iteration
                input_text = result
            else:
                print(f"Result: '{result[:100]}{'...' if len(result) > 100 else ''}'")
                # Update input_text for next iteration
                input_text = result
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
            print(f"Applied: {rule_string}")
            
            # For encrypted data, show more characters to avoid truncation issues
            if rule_string.strip() == '/enc':
                print(f"Result: '{result}'")
                print("(Full encrypted text copied to clipboard)")
            else:
                print(f"Result: '{result[:100]}{'...' if len(result) > 100 else ''}'")
            print("Result copied to clipboard!")
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Interactive mode
        input_text = get_input_text()
        interactive_mode(input_text)


if __name__ == "__main__":
    main()