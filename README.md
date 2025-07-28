# String_Multitool

An advanced, enterprise-grade text transformation tool with modular architecture, configurable rules, and military-grade RSA encryption. Features pipe support, intuitive rule-based syntax, and extensible configuration system for professional development workflows.

## Features

### Core Functionality
- **Intuitive Syntax**: Use `/rule` format for transformations (e.g., `/t/l` for trim + lowercase)
- **Pipe Support**: Works with stdin/stdout for seamless integration with shell commands
- **Interactive Mode**: Prompt-based interface when no arguments provided
- **Sequential Processing**: Chain multiple transformations (e.g., `/t/l/u`)
- **Argument Support**: Advanced rules with parameters (e.g., `/R 'old' 'new'`)
- **Clipboard Integration**: Automatically copies results to clipboard
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Unicode Support**: Full-width ↔ half-width character conversion for Japanese text

### Enterprise Features
- **Modular Architecture**: Clean separation of concerns with dedicated managers
- **Configuration-Driven**: Rules and security settings externalized to JSON files
- **Enhanced Security**: RSA-4096 encryption with AES-256-CBC hybrid encryption
- **Extensible Design**: Easy to add new transformation rules via configuration
- **Professional Error Handling**: Comprehensive error messages and graceful degradation
- **Type Safety**: Full type hints and dataclass-based rule definitions

## Quick Start

### Installation

```bash
# Clone the repository
git clone String-Multitool
cd String_Multitool

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Interactive mode (clipboard input)
python String_Multitool.py

# Apply rules to clipboard
python String_Multitool.py /t/l

# Pipe input with interactive mode
echo "  HELLO WORLD  " | python String_Multitool.py

# Pipe input with rules
echo "  HELLO WORLD  " | python String_Multitool.py /t/l
# Result: "hello world" (trimmed and lowercased)

# File input with rules
Get-Content file.txt | python String_Multitool.py /t/l
```

## Transformation Rules

### Basic Transformations

| Rule | Name | Example |
|------|------|---------|
| `/uh` | Underbar to Hyphen | `TBL_CHA1` → `TBL-CHA1` |
| `/hu` | Hyphen to Underbar | `TBL-CHA1` → `TBL_CHA1` |
| `/fh` | Full-width to Half-width | `ＴＢＬ－ＣＨＡ１` → `TBL-CHA1` |
| `/hf` | Half-width to Full-width | `TBL-CHA1` → `ＴＢＬ－ＣＨＡ１` |

### Case Transformations

| Rule | Name | Example |
|------|------|---------|
| `/l` | Lowercase | `HELLO WORLD` → `hello world` |
| `/u` | Uppercase | `hello world` → `HELLO WORLD` |
| `/p` | PascalCase | `the quick brown fox` → `TheQuickBrownFox` |
| `/c` | camelCase | `is error state` → `isErrorState` |
| `/s` | snake_case | `is error state` → `is_error_state` |
| `/a` | Capitalize | `hello world` → `Hello World` |

### String Operations

| Rule | Name | Example |
|------|------|---------|
| `/t` | Trim | `  hello world  ` → `hello world` |
| `/r` | Reverse | `hello` → `olleh` |
| `/si` | SQL IN Clause | `A0001\r\nA0002\r\nA0003` → `'A0001',\r\n'A0002',\r\n'A0003'` |
| `/dlb` | Delete Line Breaks | `A0001\r\nA0002\r\nA0003` → `A0001A0002A0003` |

### Advanced Rules (with arguments)

| Rule | Name | Example |
|------|------|---------|
| `/S '<replacement>'` | Slugify | `/S '+'` → `http://foo.bar` → `http+foo+bar` |
| `/R '<find>' '<replace>'` | Replace | `/R 'old' 'new'` → `old text` → `new text` |
| `/enc` | RSA Encrypt | `Secret message` → `Base64 encrypted text` |
| `/dec` | RSA Decrypt | `Base64 encrypted text` → `Secret message` |

**Default Arguments:**
- `/S` (no argument) uses `-` as replacement
- `/R '<find>'` (no replacement) removes the substring

## Usage Examples

### Sequential Processing

Chain multiple transformations by combining rules:

```bash
# Trim whitespace, then convert to lowercase
echo "  HELLO WORLD  " | python String_Multitool.py /t/l
# Result: "hello world"

# Convert to snake_case, then uppercase
echo "The Quick Brown Fox" | python String_Multitool.py /s/u
# Result: "THE_QUICK_BROWN_FOX"

# Trim, slugify with plus, then uppercase
echo "  hello world test  " | python String_Multitool.py /t/S/u
# Result: "HELLO-WORLD-TEST"
```

### Advanced Transformations

```bash
# Slugify with custom replacement
echo "http://foo.bar/baz" | python String_Multitool.py "/S '+'"
# Result: "http+foo+bar+baz"

# Replace text
echo "I'm Will, Will's son" | python String_Multitool.py "/R 'Will' 'Bill'"
# Result: "I'm Bill, Bill's son"

# Remove substring (replace with empty)
echo "remove this text" | python String_Multitool.py "/R 'this'"
# Result: "remove  text"

# RSA Encryption with Japanese text support
echo "秘密のメッセージ Secret message" | python String_Multitool.py "/enc"
# Result: Base64 encoded encrypted text (supports any text size)

# RSA Decryption (assumes encrypted text is in clipboard)
python String_Multitool.py "/dec"
# Result: Original message with Japanese characters restored
```

### RSA Encryption/Decryption

The application includes RSA encryption capabilities with hybrid AES+RSA encryption:

- **`/enc`**: Encrypt clipboard text using hybrid AES+RSA encryption
- **`/dec`**: Decrypt clipboard text using RSA private key
- **Auto Key Generation**: RSA-4096 key pair is automatically created if not found
- **Key Storage**: Keys are stored in `rsa/` directory (excluded from version control)
  - Private key: `rsa/rsa` (PEM format)
  - Public key: `rsa/rsa.pub` (PEM format)
- **Hybrid Encryption**: Uses AES-256-CBC for data + RSA-4096 for key encryption
- **Unlimited Size**: Can encrypt text of any length (no 190-byte RSA limit)
- **Base64 Output**: Encrypted data is base64 encoded for safe text handling
- **Japanese Support**: Full UTF-8 support for Japanese and other Unicode text

**Security Features:**
- RSA-4096 bit keys for military-grade security
- AES-256-CBC encryption for data payload
- PKCS7 padding with validation
- OAEP padding for RSA operations
- SHA-256 hash algorithm with MGF1
- Cryptographically secure random number generation
- Automatic padding correction for base64 decoding
- Secure key storage with proper file permissions (0o600 for private keys)
- Keys are automatically excluded from version control
- Configurable security parameters via JSON configuration

**Example Usage:**
```bash
# Encrypt a message
echo "機密データ Confidential data" | python String_Multitool.py "/enc"
# Output: Base64 encoded encrypted text

# Decrypt (assumes encrypted text is in clipboard)
python String_Multitool.py "/dec"
# Output: Original message restored

# Chain with other transformations
echo "Secret Message" | python String_Multitool.py "/enc/t"
# Encrypt then trim whitespace from result
```

### Interactive Mode

When no arguments are provided, the app enters interactive mode:

```bash
python String_Multitool.py
# 📋 String_Multitool - Interactive Mode
# =============================================
# Input text: 'your clipboard content...'
# 
# Enter transformation rules (e.g., /t/l) or 'help' for available rules:
# Rules: /t/l
# ✅ Text copied to clipboard
# Result: 'transformed text'
```

### File Processing

Process text files using PowerShell or bash:

```bash
# PowerShell
Get-Content input.txt | python String_Multitool.py /t/l | Out-File output.txt

# Bash
cat input.txt | python String_Multitool.py /t/l > output.txt
```

## Use Cases

### Database Development
```bash
# Convert table names
echo "user_profile_settings" | python String_Multitool.py /uh  # user-profile-settings
echo "user-profile-settings" | python String_Multitool.py /hu  # user_profile_settings
```

### Japanese Text Processing
```bash
# Convert full-width to half-width
echo "ＴＢＬ－ＣＨＡ１" | python String_Multitool.py /fh  # TBL-CHA1

# Convert half-width to full-width
echo "TBL-CHA1" | python String_Multitool.py /hf  # ＴＢＬ－ＣＨＡ１
```

### Code Formatting
```bash
# Convert to different naming conventions
echo "user profile settings" | python String_Multitool.py /p   # UserProfileSettings
echo "user profile settings" | python String_Multitool.py /c   # userProfileSettings
echo "user profile settings" | python String_Multitool.py /s   # user_profile_settings
```

### Text Cleanup
```bash
# Clean and format text
echo "  messy   text   with   spaces  " | python String_Multitool.py /t/s  # messy_text_with_spaces
```

### SQL and Data Processing
```bash
# Convert to SQL IN clause format
echo -e "A0001\nA0002\nA0003" | python String_Multitool.py /si
# Result: 'A0001',\r\n'A0002',\r\n'A0003'

# Remove all line breaks
echo -e "A0001\nA0002\nA0003" | python String_Multitool.py /dlb
# Result: A0001A0002A0003
```

## Installation & Setup

### Requirements

- Python 3.6+
- `pyperclip` library for clipboard operations

### Setup

```bash
# Clone repository
git clone <repository-url>
cd String_Multitool

# Install dependencies
pip install -r requirements.txt

# Test installation
python String_Multitool.py help
```

### Dependencies

The application requires the following dependencies:

```
pyperclip>=1.8.0     # Clipboard operations
cryptography>=41.0.0  # RSA encryption/decryption
```

## Command Reference

### Help

```bash
python String_Multitool.py help        # Show all available rules
python String_Multitool.py -h          # Show help
python String_Multitool.py --help      # Show help
```

### Rule Syntax

- **Single rule**: `/rule` (e.g., `/t`, `/l`, `/u`)
- **Multiple rules**: `/rule1/rule2/rule3` (e.g., `/t/l/u`)
- **Rules with arguments**: `/rule 'arg1' 'arg2'` (e.g., `/R 'old' 'new'`)

### Input Sources

1. **Clipboard** (default when no pipe input)
2. **Stdin** (when piped from other commands)

### Output

- Results are automatically copied to clipboard
- Status messages are printed to stdout
- Errors are printed to stderr

## Troubleshooting

### Common Issues

**Clipboard access errors:**
- Ensure no other applications are locking the clipboard
- Try running with administrator privileges on Windows

**Unicode/encoding issues:**
- Ensure your terminal supports UTF-8 encoding
- Use appropriate code page on Windows: `chcp 65001`

**Rule parsing errors:**
- Ensure rules start with `/`
- Use quotes around arguments with spaces: `/R 'old text' 'new text'`
- Check rule names are correct (case-sensitive)

**RSA encryption/decryption errors:**
- Ensure `cryptography` library is installed: `pip install cryptography`
- Check that RSA keys exist in `rsa/` directory (auto-generated on first use)
- Verify encrypted text is properly base64 encoded
- For "Incorrect padding" errors, the tool automatically corrects base64 padding

**Key generation issues:**
- Ensure write permissions to create `rsa/` directory
- On first encryption, key generation may take a few seconds
- Keys are automatically excluded from git commits

### Getting Help

```bash
# Show all available rules
python String_Multitool.py help

# Test specific transformation
echo "test text" | python String_Multitool.py /rule
```

## Development

### Project Structure

```
String_Multitool/
├── String_Multitool.py              # Main application with modular architecture
├── config/                          # Configuration files
│   ├── transformation_rules.json    # Rule definitions and metadata
│   └── security_config.json        # Security and encryption settings
├── rsa/                            # RSA key storage (auto-generated, git-ignored)
│   ├── rsa                         # Private key (PEM format)
│   └── rsa.pub                     # Public key (PEM format)
├── test_transform.py               # Test suite
├── requirements.txt                # Dependencies
├── .gitignore                      # Git ignore rules
└── README.md                      # Documentation
```

### Architecture Overview

The application follows a modular, enterprise-grade architecture:

- **ConfigurationManager**: Handles JSON configuration loading and caching
- **CryptographyManager**: Manages RSA key generation, encryption, and decryption
- **TextTransformationEngine**: Core transformation logic with rule processing
- **InputOutputManager**: Handles clipboard and stdin/stdout operations
- **ApplicationInterface**: Main UI and user interaction logic
- **TransformationRule**: Dataclass for type-safe rule definitions

### Running Tests

```bash
python test_transform.py
```

### Adding New Rules

#### Method 1: Configuration-Based (Recommended)
1. Add rule definition to `config/transformation_rules.json`
2. Implement the transformation method in `TextTransformationEngine`
3. Register the method in `_initialize_rules()` method
4. Add test cases to `test_transform.py`
5. Update documentation

#### Method 2: Code-Based
1. Add rule function to `TextTransformationEngine` class
2. Register in `transformation_rules` or `argument_rules` dictionary
3. Add corresponding entry in `config/transformation_rules.json`
4. Add test cases to `test_transform.py`
5. Update documentation

#### Example: Adding a New Rule
```python
# In TextTransformationEngine class
def _my_new_rule(self, text: str) -> str:
    """My custom transformation."""
    return text.upper().replace(' ', '_')

# In config/transformation_rules.json
{
  "custom_transformations": {
    "mn": {
      "name": "My New Rule",
      "description": "Convert to uppercase and replace spaces with underscores",
      "example": "hello world → HELLO_WORLD"
    }
  }
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 2.1.0 (Enterprise Refactor)
- **Architecture Overhaul**: Complete refactor to modular, enterprise-grade architecture
- **Configuration System**: Externalized rules and security settings to JSON files
- **Enhanced Security**: Upgraded to RSA-4096 with configurable security parameters
- **Type Safety**: Added comprehensive type hints and dataclass-based rule definitions
- **Improved Error Handling**: Professional error messages and graceful degradation
- **Extensibility**: Easy rule addition via configuration files
- **Security Enhancements**:
  - RSA-4096 key generation (upgraded from RSA-2048)
  - PKCS7 padding validation
  - Configurable hash algorithms and key sizes
  - Secure file permissions (0o600 for private keys)
  - Enhanced base64 validation and padding correction
- **Code Quality**: Clean separation of concerns, improved maintainability
- **Documentation**: Comprehensive inline documentation and type annotations

### Version 2.0.0
- Complete rewrite with new rule-based syntax
- Added pipe support for stdin/stdout
- Implemented sequential rule processing
- Added argument support for advanced rules
- Improved Unicode handling for Japanese text
- Simplified command-line interface
- Added comprehensive test suite
