<a href='https://ko-fi.com/Z8Z31J3LMW' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

# String_Multitool

An advanced, enterprise-grade text transformation tool with modular architecture, configurable rules, and military-grade RSA encryption. Features pipe support, intuitive rule-based syntax, and extensible configuration system for professional development workflows.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Transformation Rules](#transformation-rules)
- [Usage Examples](#usage-examples)
- [Interactive Mode](#interactive-mode)
  - [Auto-Detection Feature](#auto-detection-feature-detailed-guide)
- [Daemon Mode](#daemon-mode-continuous-monitoring)
- [Use Cases](#use-cases)
- [Installation & Setup](#installation--setup)
- [Development](#development)

## Features

### Core Functionality
- **Intuitive Syntax**: Use `/rule` format for transformations (e.g., `/t/l` for trim + lowercase)
- **Pipe Support**: Works with stdin/stdout for seamless integration with shell commands
- **Interactive Mode**: Prompt-based interface with startup clipboard content display
- **Sequential Processing**: Chain multiple transformations (e.g., `/t/l/u`)
- **Argument Support**: Advanced rules with parameters (e.g., `/r 'old' 'new'`)
- **Clipboard Integration**: Automatically copies results to clipboard
- **Auto-Detection**: Smart clipboard monitoring with notifications in interactive mode
- **Daemon Mode**: Continuous background processing for automated workflows
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Modern Python**: Requires Python 3.10+ with latest language features
- **Unicode Support**: Full-width ↔ half-width character conversion for East Asian text

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
git clone <repository-url>
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

# Interactive mode with auto-detection (enabled by default)
python String_Multitool.py
Rules: /t/s                  # Set transformation rule
# Copy text from any app → automatic notification → type 'refresh' to process
# Use 'auto off' to disable monitoring if needed

# Daemon mode (fully automatic)
python String_Multitool.py --daemon
Daemon> rules /hu            # Set hyphen-to-underscore rule
Daemon> start                # Start automatic processing
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
| `/R` | Reverse | `hello` → `olleh` |
| `/si` | SQL IN Clause | `A0001\r\nA0002\r\nA0003` → `'A0001',\r\n'A0002',\r\n'A0003'` |
| `/dlb` | Delete Line Breaks | `A0001\r\nA0002\r\nA0003` → `A0001A0002A0003` |

### Advanced Rules (with arguments)

| Rule | Name | Example |
|------|------|---------|
| `/s '<replacement>'` | Slugify | `/s '+'` → `http://foo.bar` → `http+foo+bar` |
| `/r '<find>' '<replace>'` | Replace | `/r 'old' 'new'` → `old text` → `new text` |
| `/enc` | RSA Encrypt | `Secret message` → `Base64 encrypted text` |
| `/dec` | RSA Decrypt | `Base64 encrypted text` → `Secret message` |

**Default Arguments:**
- `/s` (no argument) uses `-` as replacement
- `/r '<find>'` (no replacement) removes the substring

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
echo "  hello world test  " | python String_Multitool.py /t/s/u
# Result: "HELLO-WORLD-TEST"
```

### Advanced Transformations

```bash
# Slugify with custom replacement
echo "http://foo.bar/baz" | python String_Multitool.py "/s '+'"
# Result: "http+foo+bar+baz"

# Replace text
echo "I'm Will, Will's son" | python String_Multitool.py "/r 'Will' 'Bill'"
# Result: "I'm Bill, Bill's son"

# Remove substring (replace with empty)
echo "remove this text" | python String_Multitool.py "/r 'this'"
# Result: "remove  text"

# RSA Encryption with Unicode text support
echo "Secret message with Unicode 🔒" | python String_Multitool.py "/enc"
# Result: Base64 encoded encrypted text (supports any text size)

# RSA Decryption (assumes encrypted text is in clipboard)
python String_Multitool.py "/dec"
# Result: Original message with Unicode characters restored
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
- **Unicode Support**: Full UTF-8 support for Unicode text including East Asian characters

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
echo "Confidential data with Unicode 🔐" | python String_Multitool.py "/enc"
# Output: Base64 encoded encrypted text

# Decrypt (assumes encrypted text is in clipboard)
python String_Multitool.py "/dec"
# Output: Original message restored

# Chain with other transformations
echo "Secret Message" | python String_Multitool.py "/enc/t"
# Encrypt then trim whitespace from result
```

### Interactive Mode

When no arguments are provided, the app enters enhanced interactive mode with dynamic clipboard support:

```bash
python String_Multitool.py
# String_Multitool - Interactive Mode
# =============================================
# Input text: 'your clipboard content...' (25 chars, from clipboard)
# Auto-detection: ON
#
# 📋 Current clipboard content:
#    'your clipboard content here'
#
# Available commands: help, refresh, auto, status, clear, copy, commands, quit
# Enter transformation rules (e.g., /t/l) or command:
# Note: Transformation rules will use the latest clipboard content
# 
# Rules: /u
# [CLIPBOARD] Using fresh content: 'hello world' -> 'new text from clipboard'
# ✅ Text copied to clipboard
# Result: 'NEW TEXT FROM CLIPBOARD'
```

#### Dynamic Clipboard Processing

The interactive mode automatically uses the **latest clipboard content** for each transformation:

1. **Copy Text**: Copy "hello-world" to clipboard
2. **Apply Rule**: Type `/u` → Result: "HELLO-WORLD"
3. **Copy New Text**: Copy "test_string" to clipboard  
4. **Apply Rule**: Type `/s` → Result: "test_string" (not "HELLO_WORLD")

This allows seamless workflow without restarting the application for each new text.

#### Interactive Commands

The interactive mode now supports powerful clipboard management commands:

**Clipboard Operations:**
- `refresh`, `reload`, `replace` - Refresh input text from clipboard
- `auto [on|off]` - Toggle automatic clipboard change detection
- `copy` - Copy current working text back to clipboard
- `clear` - Clear current working text

**Session Management:**
- `status` - Show detailed session information
- `commands`, `cmd` - List all available commands
- `help` - Show transformation rules
- `quit`, `q`, `exit` - Exit application

#### Dynamic Clipboard Workflow

1. **Start Interactive Mode**: Launch with current clipboard content
2. **Apply Transformations**: Use transformation rules as usual
3. **Copy New Content**: Copy different text to clipboard in another app
4. **Refresh**: Type `refresh` to load new clipboard content
5. **Auto-Detection**: Enable with `auto on` for automatic change notifications
6. **Continue Working**: Seamlessly work with multiple text snippets

**Example Session:**
```bash
Rules: /u                    # Transform to uppercase
Rules: refresh               # Load new clipboard content
Rules: /t/s                  # Trim and convert to snake_case
Rules: auto on               # Enable auto-detection
Rules: status                # Check session status
Rules: copy                  # Copy result back to clipboard
```

#### Auto-Detection Feature (Detailed Guide)

Auto-detection is a powerful feature that **automatically monitors clipboard changes during interactive mode** and notifies you when new content is available.

##### 🔍 What is Auto-Detection?

Auto-detection monitors your clipboard in the background while you work in interactive mode. When new content is copied to the clipboard, it automatically notifies you, allowing for efficient batch processing of multiple text snippets.

##### 📋 How It Works

1. **Auto-Enabled**: Monitoring starts automatically when entering interactive mode
2. **Startup Display**: Shows current clipboard content (up to 200 chars) at startup
3. **Background Monitoring**: Checks clipboard every 1 second for changes
4. **Smart Notification**: Displays alert with content preview when new content is detected
5. **Content Preview**: Shows first 100 characters of new clipboard content
6. **Manual Processing**: Use `refresh` to load the new content when ready
7. **Optional Control**: Use `auto off` to disable monitoring if needed

##### 🎯 When to Use Auto-Detection

**Perfect for these scenarios:**

**1. Batch Text Processing**
```bash
Rules: /t/s                  # Set transformation rule (auto-detection already ON)

# Copy text from document → 🔔 Clipboard changed! New content available (25 chars)
#                            Content: 'new text from document'
Rules: refresh               # Load new content
Rules: copy                  # Process and copy result
# Repeat for next text snippet
```

**2. Code Review & Variable Naming**
```bash
Rules: /p                    # PascalCase conversion (auto-detection already ON)

# Copy variable names from IDE → 🔔 Clipboard changed! New content available (15 chars)
#                                Content: 'userFirstName'
# Transform to consistent naming → copy back to IDE
# Continue with next variable
```

**3. Document Formatting Workflow**
```bash
Rules: /t/l                  # Trim and lowercase (auto-detection already ON)

# Copy text from Word/Email → 🔔 Clipboard changed! New content available (42 chars)
#                              Content: '  IMPORTANT DOCUMENT SECTION TITLE  '
# Apply formatting → paste back to document
# Move to next section → copy → 🔔 Clipboard changed! New content available (28 chars)
#                                Content: 'Next section content here'
```

##### ⚡ Auto-Detection vs Daemon Mode

| Feature | Auto-Detection | Daemon Mode |
|---------|----------------|-------------|
| **Location** | Inside Interactive Mode | Separate Background Process |
| **Control** | Manual processing after notification | Fully automatic transformation |
| **Flexibility** | Change rules anytime | Fixed rules until restart |
| **Use Case** | Interactive workflow | Set-and-forget automation |
| **Processing** | On-demand with `refresh` | Immediate automatic processing |

##### 🛠 Auto-Detection Commands

```bash
auto on          # Enable automatic clipboard monitoring
auto off         # Disable monitoring
auto             # Toggle current state
status           # Check if monitoring is active
refresh          # Load detected clipboard changes
```

##### 💡 Practical Examples

**Example 1: API Response Formatting**
```bash
python String_Multitool.py  # Auto-detection starts automatically
Rules: /t                    # Set trim rule

# Copy JSON from Postman → 🔔 Clipboard changed! New content available (156 chars)
#                          Content: '{"user": "john", "status": "active", "data": {...}}'
Rules: refresh               # Load the JSON
Rules: /p                    # Convert to PascalCase
Rules: copy                  # Copy formatted result

# Copy next API response → 🔔 Clipboard changed! New content available (89 chars)
#                           Content: '{"result": "success", "message": "Operation completed"}'
Rules: refresh               # Process next response
```

**Example 2: Database Column Names**
```bash
Rules: /s                    # snake_case conversion (auto-detection already ON)

# Copy "UserFirstName" from schema → 🔔 Clipboard changed! New content available (13 chars)
#                                    Content: 'UserFirstName'
Rules: refresh               # Load: "UserFirstName"
# Result: "user_first_name"
Rules: copy                  # Copy converted name

# Copy "OrderCreatedDate" → 🔔 Clipboard changed! New content available (16 chars)
#                              Content: 'OrderCreatedDate'
Rules: refresh               # Load and convert automatically
```

**Example 3: Multi-Language Text Processing**
```bash
Rules: /fh                   # Full-width to half-width (auto-detection already ON)

# Copy Japanese text with full-width chars → 🔔 Clipboard changed! New content available (9 chars)
#                                           Content: 'ＴＢＬ－ＣＨＡ１'
Rules: refresh               # Load: "ＴＢＬ－ＣＨＡ１"
# Result: "TBL-CHA1"
Rules: copy                  # Copy normalized text
```

##### 🔧 Configuration Options

Customize auto-detection behavior in `config/security_config.json`:

```json
{
  "interactive_mode": {
    "clipboard_refresh": {
      "auto_detection_interval": 1.0,           // Check interval (seconds)
      "enable_auto_detection_by_default": true,  // Auto-enable on startup
      "max_content_size": 1048576,              // Max clipboard size (1MB)
      "show_character_count": true,             // Show char count in status
      "show_timestamps": true                   // Show last update time
    }
  }
}
```

##### 📊 Status Information

Check auto-detection status anytime:

```bash
Rules: status
# =============================================
# Input text: 'your clipboard content...' (25 chars, from clipboard)
# Auto-detection: ON                    ← Monitoring active
# Monitor active: Yes                   ← Background monitoring running
# Last updated: 2 seconds ago          ← Time since last clipboard change
# =============================================
```

##### 🚀 Pro Tips

1. **Efficient Workflow**: Auto-detection is enabled by default - just start using it!
2. **Content Preview**: Notification shows first 100 characters of new clipboard content
3. **Rule Changes**: Change transformation rules anytime while monitoring continues
4. **Batch Processing**: Perfect for processing multiple similar text snippets
5. **Resource Friendly**: Uses minimal system resources (1-second intervals)
6. **Cross-Application**: Works with any application that uses system clipboard
7. **Optional Control**: Use `auto off` to disable monitoring when not needed

**Auto-detection makes interactive mode incredibly efficient for repetitive text processing tasks!**

### Daemon Mode (Continuous Monitoring)

For continuous clipboard monitoring and automatic transformation:

```bash
python String_Multitool.py --daemon
```

**Daemon Mode Workflow:**
1. **Start Daemon Mode**: `python String_Multitool.py --daemon`
2. **Set Transformation**: Choose a preset or custom rules
3. **Start Monitoring**: Begin automatic clipboard processing
4. **Copy Text**: Any text copied to clipboard gets automatically transformed
5. **Continue Working**: Daemon runs in background until stopped

**Example Daemon Session:**
```bash
python String_Multitool.py --daemon

# Set transformation preset
Daemon> preset uppercase
[DAEMON] Preset 'uppercase' activated: /u

# Start monitoring
Daemon> start
[DAEMON] Starting clipboard monitoring...
[DAEMON] Active transformation: /u
[DAEMON] Press Ctrl+C to stop

# Now copy "hello world" to clipboard
[DAEMON] Transformed: 'hello world' -> 'HELLO WORLD'

# Copy "test-string" to clipboard  
[DAEMON] Transformed: 'test-string' -> 'TEST-STRING'

# Stop daemon
Daemon> stop
[DAEMON] Stopped after 0:02:15
[DAEMON] Transformations applied: 2
```

**Available Presets:**
- `uppercase`: Convert to UPPERCASE
- `lowercase`: Convert to lowercase
- `snake_case`: Convert to snake_case
- `pascal_case`: Convert to PascalCase
- `camel_case`: Convert to camelCase
- `trim_lowercase`: Trim whitespace and convert to lowercase
- `hyphen_to_underscore`: Convert hyphens to underscores

**Custom Rules:**
```bash
# Set custom transformation rules
Daemon> rules /t/l/s
[DAEMON] Active rules set: /t/l/s

# This will: trim -> lowercase -> snake_case
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

### East Asian Text Processing
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

- Python 3.10+
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
- **Rules with arguments**: `/rule 'arg1' 'arg2'` (e.g., `/r 'old' 'new'`)

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
- Use quotes around arguments with spaces: `/r 'old text' 'new text'`
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
│   ├── security_config.json        # Security and encryption settings
│   └── daemon_config.json          # Daemon mode configuration
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

### Version 2.2.0 (Dynamic Clipboard Enhancement)
- **Dynamic Clipboard Refresh**: Refresh input text from clipboard during interactive sessions
- **Auto-Detection**: Optional automatic clipboard change monitoring with notifications
- **Enhanced Interactive Commands**: New commands for session management and clipboard operations
- **Session State Management**: Track text source, timestamps, and character counts
- **Improved User Experience**: Better status information and command feedback
- **Background Monitoring**: Efficient clipboard monitoring with configurable intervals
- **Resource Management**: Size limits and memory management for large clipboard content

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
- Improved Unicode handling for East Asian text
- Simplified command-line interface
- Added comprehensive test suite
