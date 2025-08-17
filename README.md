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
- [System Tray Mode](#system-tray-mode-background-operation)
- [Hotkey Mode](#hotkey-mode-global-keyboard-shortcuts)
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
- **Auto-Detection**: Automatic clipboard monitoring with notifications in interactive mode (always enabled)
- **Daemon Mode**: Continuous background processing for automated workflows
- **System Tray Mode**: Background operation with system tray icon interface
- **Hotkey Mode**: Global keyboard shortcuts for instant transformations (Ctrl+Shift+S + key)
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Modern Python**: Requires Python 3.10+ with full type annotations and latest language features
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
git clone https://github.com/yourusername/String-Multitool.git
cd String-Multitool

# Create virtual environment (Python 3.10+ required)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python String_Multitool.py help
```

### Basic Usage

#### Legacy CLI (Backward Compatible)
```bash
# Interactive mode (clipboard input)
python String_Multitool.py

# Apply rules to clipboard
python String_Multitool.py /t/l

# Hotkey mode (global keyboard shortcuts)
python String_Multitool.py --hotkey

# Pipe input with rules
echo "  HELLO WORLD  " | python String_Multitool.py /t/l
# Result: "hello world" (trimmed and lowercased)
```

#### Modern Typer CLI (Recommended)
```bash
# Interactive mode
string-multitool interactive

# Transform text with rules
string-multitool transform "/t/l" --text "  HELLO WORLD  "
echo "  HELLO WORLD  " | string-multitool transform "/t/l"

# Encrypt/decrypt text
string-multitool encrypt --text "Secret message"
string-multitool decrypt  # Uses clipboard content

# Daemon mode with presets
string-multitool daemon --preset uppercase
string-multitool daemon --rules "/t/l"

# System tray mode (background with tray icon)
python String_Multitool.py --tray
string-multitool tray

# Hotkey mode (global keyboard shortcuts)
python String_Multitool.py --hotkey
string-multitool hotkey

# Show available rules
string-multitool rules
string-multitool rules --category case
string-multitool rules --search "uppercase"

# Version information
string-multitool version
```

# File input with rules
Get-Content file.txt | python String_Multitool.py /t/l

# Interactive mode with auto-detection (always enabled)
python String_Multitool.py
Rules: /t/s                  # Set transformation rule
# Copy text from any app → automatic notification → type 'refresh' to process
Rules: daemon                # Switch to daemon mode without restarting

# Daemon mode (fully automatic)
python String_Multitool.py --daemon
Daemon> /hu                  # Set hyphen-to-underscore rule (shortcut)
Daemon> start                # Start automatic processing
Daemon> interactive          # Switch back to interactive mode
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
| `/S '<replacement>'` | Slugify | `/S '+'` → `http://foo.bar` → `http+foo+bar` |
| `/r '<find>' '<replace>'` | Replace | `/r 'old' 'new'` → `old text` → `new text` |
| `/enc` | RSA Encrypt | `Secret message` → `Base64 encrypted text` |
| `/dec` | RSA Decrypt | `Base64 encrypted text` → `Secret message` |

**Default Arguments:**
- `/S` (no argument) uses `-` as replacement
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
echo "http://foo.bar/baz" | python String_Multitool.py "/S '+'"
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
- `copy` - Copy current working text back to clipboard
- `clear` - Clear current working text

**Session Management:**
- `status` - Show detailed session information
- `commands`, `cmd` - List all available commands
- `help` - Show transformation rules
- `daemon` - Switch to daemon mode
- `quit`, `q`, `exit` - Exit application

#### Dynamic Clipboard Workflow

1. **Start Interactive Mode**: Launch with current clipboard content
2. **Apply Transformations**: Use transformation rules as usual
3. **Copy New Content**: Copy different text to clipboard in another app
4. **Refresh**: Type `refresh` to load new clipboard content
5. **Auto-Detection**: Automatically monitors clipboard changes and provides notifications
6. **Continue Working**: Seamlessly work with multiple text snippets

**Example Session:**
```bash
Rules: /u                    # Transform to uppercase
Rules: refresh               # Load new clipboard content
Rules: /t/s                  # Trim and convert to snake_case
Rules: status                # Check session status
Rules: copy                  # Copy result back to clipboard
```

#### Auto-Detection Feature (Detailed Guide)

Auto-detection is a powerful feature that **automatically monitors clipboard changes during interactive mode** and notifies you when new content is available.

##### 🔍 What is Auto-Detection?

Auto-detection monitors your clipboard in the background while you work in interactive mode. When new content is copied to the clipboard, it automatically notifies you, allowing for efficient batch processing of multiple text snippets.

##### 📋 How It Works

1. **Always Enabled**: Monitoring starts automatically when entering interactive mode
2. **Startup Display**: Shows current clipboard content (up to 200 chars) at startup
3. **Background Monitoring**: Checks clipboard every 1 second for changes
4. **Smart Notification**: Displays alert with content preview when new content is detected
5. **Content Preview**: Shows first 100 characters of new clipboard content
6. **Manual Processing**: Use `refresh` to load the new content when ready

##### 🎯 When to Use Auto-Detection

**Perfect for these scenarios:**

**1. Batch Text Processing**
```bash
Rules: /t/s                  # Set transformation rule (auto-detection is always ON)

# Copy text from document → 🔔 Clipboard changed! New content available (25 chars)
#                            Content: 'new text from document'
Rules: refresh               # Load new content
Rules: copy                  # Process and copy result
# Repeat for next text snippet
```

**2. Code Review & Variable Naming**
```bash
Rules: /p                    # PascalCase conversion (auto-detection is always ON)

# Copy variable names from IDE → 🔔 Clipboard changed! New content available (15 chars)
#                                Content: 'userFirstName'
# Transform to consistent naming → copy back to IDE
# Continue with next variable
```

**3. Document Formatting Workflow**
```bash
Rules: /t/l                  # Trim and lowercase (auto-detection is always ON)

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
# Auto-detection is always enabled - no toggle commands needed
# Use these commands to interact with clipboard monitoring:

status           # Check current auto-detection state
refresh          # Manually refresh from clipboard
commands         # Show all available commands
```

##### 💡 Practical Examples

**Example 1: API Response Formatting**
```bash
python String_Multitool.py  # Auto-detection is always active
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
Rules: /s                    # snake_case conversion (auto-detection is always ON)

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
Rules: /fh                   # Full-width to half-width (auto-detection is always ON)

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
# Auto-detection: ON (always enabled)   ← Monitoring always active
# Monitor active: Yes                   ← Background monitoring running
# Last updated: 2 seconds ago          ← Time since last clipboard change
# =============================================
```

##### 🚀 Pro Tips

1. **Efficient Workflow**: Auto-detection is always enabled - just start using it!
2. **Content Preview**: Notification shows first 100 characters of new clipboard content
3. **Rule Changes**: Change transformation rules anytime while monitoring continues
4. **Batch Processing**: Perfect for processing multiple similar text snippets
5. **Resource Friendly**: Uses minimal system resources (1-second intervals)
6. **Cross-Application**: Works with any application that uses system clipboard

**Auto-detection makes interactive mode incredibly efficient for repetitive text processing tasks!**

### Daemon Mode (Continuous Monitoring)

For continuous clipboard monitoring and automatic transformation:

#### Legacy CLI
```bash
python String_Multitool.py --daemon
```

#### Modern Typer CLI
```bash
# Start daemon with preset
string-multitool daemon --preset uppercase

# Start daemon with custom rules
string-multitool daemon --rules "/t/l/s"

# Start daemon interactively
string-multitool daemon
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

# Or set rules directly (shortcut)
Daemon> /u
[DAEMON] Active rules set: /u

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
# Set custom transformation rules (traditional way)
Daemon> rules /t/l/s
[DAEMON] Active rules set: /t/l/s

# Set transformation rules directly (shortcut)
Daemon> /t/l/s
[DAEMON] Active rules set: /t/l/s

# This will: trim -> lowercase -> snake_case
```

**Daemon Commands:**
- `preset <name>` - Set transformation preset
- `rules <rules>` - Set custom transformation rules
- `/rule` - Set transformation rule directly (shortcut)
- `start` - Start daemon monitoring
- `stop` - Stop daemon monitoring
- `status` - Show daemon status
- `interactive` - Switch to interactive mode
- `quit` - Exit daemon mode

#### Mode Switching

Seamlessly switch between interactive and daemon modes without restarting:

```bash
# Start in interactive mode
python String_Multitool.py
Rules: /u                    # Apply transformations
Rules: daemon                # Switch to daemon mode

# Now in daemon mode
Daemon> rules /l             # Set lowercase rule
Daemon> start                # Start monitoring
Daemon> interactive          # Switch back to interactive mode

# Back in interactive mode
Rules: /s                    # Continue with transformations
```

**Benefits:**
- **No Restart Required**: Switch modes instantly
- **Preserve Context**: Current clipboard content is maintained
- **Flexible Workflow**: Choose the right mode for each task
- **Efficient**: No need to exit and restart the application

### System Tray Mode (Background Operation)

For background operation with system tray icon interface:

#### Starting System Tray Mode

```bash
# Legacy CLI
python String_Multitool.py --tray

# Modern Typer CLI
string-multitool tray
```

#### How It Works

System tray mode provides a convenient background service with system tray icon:

1. **Background Service**: Runs silently in the background with minimal resource usage
2. **Tray Icon Interface**: Right-click tray icon for all control options
3. **Daemon Integration**: Uses daemon mode internally for clipboard monitoring
4. **Visual Feedback**: Icon tooltip shows current status and active preset
5. **Easy Access**: No command line required after startup

#### System Tray Features

**Tray Menu Options:**
- **Start/Stop Monitoring**: Toggle clipboard monitoring on/off
- **Set Preset 1/2/3**: Quick access to configured transformation presets
- **Status**: View current monitoring status and active rules
- **Help**: Show usage information in console
- **Exit**: Stop application and remove tray icon

**Status Indicators:**
- Icon tooltip shows current state: "Monitoring Active" or "Monitoring Stopped"
- Menu items update to reflect current monitoring status
- Visual confirmation of active preset selection

#### Example Workflow

```bash
# 1. Start system tray mode
python String_Multitool.py --tray
# Console: "[TRAY] Starting system tray mode..."
# Console: "[TRAY] Right-click the tray icon for options"

# 2. Right-click tray icon → Set Preset 1 (e.g., uppercase transformation)
# Console: "[TRAY] Preset 1 activated"

# 3. Right-click tray icon → Start Monitoring
# Console: "[TRAY] Monitoring started"

# 4. Copy text in any application → automatic transformation
# Copy "hello world" → automatically becomes "HELLO WORLD"

# 5. Right-click tray icon → Stop Monitoring (when needed)
# Console: "[TRAY] Monitoring stopped"

# 6. Right-click tray icon → Exit (to close)
# Console: "[TRAY] Exiting application..."
```

#### Configuration

System tray mode uses the same daemon configuration file for presets:

**`config/daemon_config.json`:**
```json
{
  "presets": {
    "1": {
      "name": "uppercase",
      "rules": "/u",
      "description": "Convert to UPPERCASE"
    },
    "2": {
      "name": "lowercase", 
      "rules": "/l",
      "description": "Convert to lowercase"
    },
    "3": {
      "name": "snake_case",
      "rules": "/s", 
      "description": "Convert to snake_case"
    }
  }
}
```

#### System Requirements

- **Dependency**: Requires `pystray` and `PIL` (Pillow) libraries
- **Installation**: `pip install pystray pillow`
- **Platform**: Windows, macOS, Linux (with system tray support)
- **Icon**: Uses custom icon from `resources/icon.png` or default blue square

#### Benefits

- **Set and Forget**: Start once, runs until you stop it
- **Visual Interface**: No need to remember command line syntax
- **Quick Preset Access**: Switch transformation types with menu clicks
- **Background Operation**: Works while using any application
- **Resource Efficient**: Minimal CPU and memory usage
- **No Application Switching**: Direct tray icon access from anywhere

#### Use Cases

**1. Daily Text Processing**
```bash
# Morning: Start tray → Set Preset 1 (uppercase) → Start monitoring
# Work day: Copy email addresses → auto-uppercase for database entry
# Evening: Right-click → Exit
```

**2. Development Workflow**
```bash
# Project start: Tray → Set Preset 3 (snake_case) → Start monitoring  
# During coding: Copy variable names → auto-convert to snake_case
# Code review: Stop monitoring when not needed
```

**3. Documentation Tasks**
```bash
# Document editing: Tray → Set Preset 2 (lowercase) → Start monitoring
# Content creation: Copy headings → auto-normalize case
# Quick preset switching for different formatting needs
```

#### Troubleshooting

**Tray icon not appearing:**
- Install required dependencies: `pip install pystray pillow`
- Check system tray is enabled in your OS
- Try running with administrator privileges

**Menu not responding:**
- Ensure no other clipboard applications conflict
- Check console output for error messages
- Restart application if menu becomes unresponsive

**Dependencies missing:**
```bash
# Install system tray dependencies
pip install pystray pillow

# Verify installation
python -c "import pystray; print('pystray available')"
```

### Hotkey Mode (Global Keyboard Shortcuts)

For instant text transformation using global keyboard shortcuts:

#### Starting Hotkey Mode

```bash
# Legacy CLI
python String_Multitool.py --hotkey

# Modern Typer CLI
string-multitool hotkey
```

#### How It Works

Hotkey mode provides direct keyboard shortcuts that work globally across all applications:

1. **Direct Shortcuts**: Press key combination directly (e.g., `Ctrl+Shift+L` for lowercase)
2. **Sequence Shortcuts**: Press first combination, then second key (e.g., `Ctrl+Shift+H` → `U` for hyphen-to-underscore)  
3. **Instant Transformation**: Current clipboard content is transformed and replaced immediately

#### Direct Key Mappings

| Shortcut | Transformation | Example |
|----------|---------------|---------|
| `Ctrl+Shift+L` | Lowercase | `HELLO WORLD` → `hello world` |
| `Ctrl+Shift+U` | Uppercase | `hello world` → `HELLO WORLD` |
| `Ctrl+Shift+T` | Trim | `  hello  ` → `hello` |
| `Ctrl+Shift+C` | Capitalize | `hello world` → `Hello World` |
| `Ctrl+Shift+R` | Reverse | `hello` → `olleh` |
| `Ctrl+Shift+S` | snake_case | `hello world` → `hello_world` |
| `Ctrl+Shift+P` | PascalCase | `hello world` → `HelloWorld` |
| `Ctrl+Shift+A` | Capitalize Words | `hello world` → `Hello World` |
| `Ctrl+Shift+E` | Encrypt | `secret` → `encrypted text` |
| `Ctrl+Shift+D` | Decrypt | `encrypted text` → `secret` |

#### Sequence Key Mappings

| First Key | Second Key | Transformation | Example |
|-----------|------------|---------------|---------|
| `Ctrl+Shift+Alt+H` | `Ctrl+Shift+Alt+U` | Hyphen to Underscore | `hello-world` → `hello_world` |
| `Ctrl+Shift+Alt+U` | `Ctrl+Shift+Alt+H` | Underscore to Hyphen | `hello_world` → `hello-world` |
| `Ctrl+Shift+Alt+H` | `Ctrl+Shift+Alt+H` | Hash (SHA-256) | `password` → `5e884...` |
| `Ctrl+Shift+Alt+H` | `Ctrl+Shift+Alt+F` | Half-width to Full-width | `HELLO` → `ＨＥＬＬＯ` |
| `Ctrl+Shift+Alt+B` | `Ctrl+Shift+Alt+E` | Base64 Encode | `hello` → `aGVsbG8=` |
| `Ctrl+Shift+Alt+B` | `Ctrl+Shift+Alt+D` | Base64 Decode | `aGVsbG8=` → `hello` |
| `Ctrl+Shift+Alt+F` | `Ctrl+Shift+Alt+H` | Full-width to Half-width | `ＨＥＬＬＯ` → `HELLO` |
| `Ctrl+Shift+Alt+F` | `Ctrl+Shift+Alt+J` | Format JSON | `{"a":1}` → formatted JSON |

#### Example Workflow

```bash
# 1. Start hotkey mode
python String_Multitool.py --hotkey
# Console shows: Direct hotkey mode started successfully

# 2. Copy text in any application (e.g., "  HELLO WORLD  ")

# 3. Press Ctrl+Shift+L for lowercase
# Result: "  hello world  " is now in clipboard

# 4. Or press Ctrl+Shift+T for trim
# Result: "HELLO WORLD" is now in clipboard

# 5. For sequence shortcuts, press Ctrl+Shift+H, then U
# Result: Transforms "hello-world" to "hello_world"
```

#### Configuration

Customize hotkey mappings in `config/hotkey_config.json`:

```json
{
    "hotkey_settings": {
        "enabled": true,
        "sequence_timeout_seconds": 2.0,
        "modifier_key": "ctrl+shift"
    },
    "direct_hotkeys": {
        "ctrl+shift+l": {"command": "/l", "description": "Convert to lowercase"},
        "ctrl+shift+u": {"command": "/u", "description": "Convert to uppercase"},
        "ctrl+shift+t": {"command": "/t", "description": "Trim whitespace"}
    },
    "sequence_hotkeys": {
        "h": {
            "sequences": {
                "u": {"command": "/hu", "description": "Hyphen to underscore"},
                "h": {"command": "/h", "description": "Hash (SHA-256)"}
            }
        }
    }
}
```

#### Features

- **Global Hotkeys**: Works across all applications and windows
- **Direct Access**: Single key combination for most common operations
- **Sequence Support**: Two-key sequences for advanced operations
- **Configurable**: Customize all key combinations and commands
- **Real-time Processing**: Instant clipboard transformation
- **Background Operation**: Runs continuously until stopped
- **No GUI**: Pure keyboard-driven workflow
- **Memory Efficient**: Minimal resource usage

#### Use Cases

**1. Development Workflow**
```bash
# Copy variable name from IDE → Ctrl+Shift+S → snake_case conversion
# Copy API endpoint → Ctrl+Shift+L → lowercase normalization
# Copy SQL table name → Ctrl+Shift+U → uppercase formatting
```

**2. Documentation Editing**
```bash
# Copy messy text → Ctrl+Shift+T → trim whitespace
# Copy code snippet → Ctrl+Shift+F then J → format JSON properly
# Copy sensitive data → Ctrl+Shift+E → encrypt immediately
```

**3. Data Processing**
```bash
# Copy database values → Ctrl+Shift+H then H → hash for anonymization
# Copy encoded data → Ctrl+Shift+B then D → base64 decode
# Copy hyphenated text → Ctrl+Shift+H then U → convert hyphens to underscores
```

#### System Requirements

- Windows: Tested on Windows 10/11
- Administrator privileges may be required for global hotkeys
- `keyboard` library for global hotkey monitoring (included in requirements.txt)

#### Troubleshooting

**Hotkeys not working:**
- **Key Conflicts**: Some key combinations may conflict with applications:
  - `Ctrl+Shift+T` (Terminal), `Ctrl+Shift+C` (Copy), `Ctrl+Shift+S` (Save As)
  - **Solution**: Customize mappings in `config/hotkey_config.json`
  - **Alternative modifiers**: `Ctrl+Alt`, `Win`, `Alt+Shift`
- **Administrator Rights**: Try running as administrator on Windows
- **Antivirus Blocking**: Check if antivirus is blocking global keyboard library access
- **Application Priority**: Some applications may capture certain key combinations first

**Sequence timeout issues:**
- Increase `sequence_timeout_seconds` in `config/hotkey_config.json`
- Practice the two-key sequence timing (default: 2 seconds)

**Configuration errors:**
- Verify JSON syntax in config file
- Check that all command strings are valid transformation rules

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
git clone https://github.com/yourusername/String-Multitool.git
cd String-Multitool

# Create and activate virtual environment (Python 3.10+ required)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Test installation
python String_Multitool.py help
python -m pytest test_transform.py -v
```

### Dependencies

The application requires the following dependencies:

```
pyperclip>=1.8.0      # Cross-platform clipboard operations
pynput>=1.7.0         # Keyboard/mouse input handling for daemon mode  
watchdog>=3.0.0       # File system monitoring for advanced features
cryptography>=41.0.0  # RSA-4096 + AES-256 encryption/decryption
pytest>=7.0.0         # Testing framework for development
pyinstaller>=5.0.0    # Executable building for distribution
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
├── String_Multitool.py              # Legacy entry point (backward compatible)
├── string_multitool/               # Main package directory
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # Application interface
│   ├── cli.py                      # Modern Typer CLI
│   ├── exceptions.py               # Custom exceptions
│   ├── core/                       # Core functionality
│   │   ├── config.py               # Configuration manager
│   │   ├── crypto.py               # Encryption/decryption
│   │   ├── transformations.py      # Text transformation engine
│   │   └── types.py                # Type definitions
│   ├── io/                         # Input/Output operations
│   │   ├── clipboard.py            # Clipboard operations
│   │   └── manager.py              # IO manager
│   ├── modes/                      # Application modes
│   │   ├── daemon.py               # Daemon mode
│   │   ├── interactive.py          # Interactive mode
│   │   └── hotkey.py               # Hotkey mode
│   └── utils/                      # Utilities
│       └── logger.py               # Logging utilities
├── config/                         # Configuration files
│   ├── transformation_rules.json   # Rule definitions
│   ├── security_config.json       # Security settings
│   ├── daemon_config.json         # Daemon configuration
│   └── hotkey_config.json         # Hotkey configuration
├── rsa/                           # RSA key storage (auto-generated)
├── .vscode/                       # VSCode configuration
│   └── settings.json              # Python interpreter settings
├── test_transform.py              # Core transformation tests
├── test_hotkey.py                 # Hotkey mode tests
├── pyproject.toml                 # Project configuration
├── pyrightconfig.json             # Pylance configuration
├── requirements.txt               # Dependencies
├── .gitignore                     # Git ignore rules
└── README.md                     # Documentation
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

#### Method 1: Individual Class-Based (Recommended)
1. Create new transformation class in appropriate module under `string_multitool/transformations/`
2. Inherit from `TransformationBase` and implement required abstract methods:
   - `transform(text: str) -> str`: Main transformation logic
   - `get_transformation_rule() -> str`: Return rule identifier
   - `get_input_text() -> str`: Return input text
   - `get_output_text() -> str`: Return output text
3. Add class to `__init__.py` exports and `get_transformation_class_map()`
4. Add rule definition to `config/transformation_rules.json`
5. Add comprehensive test cases to `test_transform.py`
6. Update documentation

#### Method 2: Configuration-Based (Legacy)
1. Add rule definition to `config/transformation_rules.json`
2. Implement the transformation method in `TextTransformationEngine`
3. Register the method in `_initialize_rules()` method
4. Add test cases to `test_transform.py`
5. Update documentation

#### Example: Adding a New Rule
```python
# Create string_multitool/transformations/custom_transformations.py
from ..core.transformation_base import TransformationBase
from ..core.types import ConfigDict
from ..exceptions import TransformationError

class MyNewRuleTransformation(TransformationBase):
    """Custom transformation that converts to uppercase and replaces spaces with underscores."""
    
    def __init__(self, config: ConfigDict | None = None) -> None:
        super().__init__(config)
        self._rule: str = "mn"
        self._input_text: str = ""
        self._output_text: str = ""
    
    def transform(self, text: str) -> str:
        """Convert to uppercase and replace spaces with underscores."""
        try:
            self._input_text = text
            self._output_text = text.upper().replace(' ', '_')
            return self._output_text
        except Exception as e:
            self.set_error_context({
                "rule": self._rule,
                "input_length": len(text),
                "error_type": type(e).__name__
            })
            raise TransformationError(f"Custom transformation failed: {e}", self.get_error_context()) from e
    
    def get_transformation_rule(self) -> str:
        return self._rule
    
    def get_input_text(self) -> str:
        return self._input_text
    
    def get_output_text(self) -> str:
        return self._output_text

# Add to string_multitool/transformations/__init__.py
from .custom_transformations import MyNewRuleTransformation

# Update get_transformation_class_map()
def get_transformation_class_map() -> dict[str, type]:
    return {
        # ... existing mappings ...
        "mn": MyNewRuleTransformation,
    }

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

### Version 2.5.0 (Modular Transformation Architecture)
- **Modular Architecture**: Complete refactor of transformation system into individual classes
- **Abstract Base Classes**: Introduction of `TransformationBase` with required abstract methods
- **Individual Transformation Classes**: Each rule implemented as a separate, testable class
- **Enhanced Type Safety**: Abstract methods ensure consistent interface across all transformations
- **Improved Maintainability**: Clear separation of concerns with dedicated classes per transformation
- **Factory Pattern**: Clean rule-to-class mapping system for dynamic transformation instantiation
- **State Management**: Internal tracking of input/output text for debugging and analysis
- **Error Context**: Enhanced error handling with transformation-specific context information
- **Protocol-Based Design**: Type-safe interfaces using Python protocols
- **Extensibility**: Simplified addition of new transformation rules as individual classes
- **Documentation**: Updated architecture documentation and development guidelines

### Version 2.4.0 (Global Hotkey Support)
- **Hotkey Mode**: Global keyboard shortcuts for instant text transformations
- **Sequential Key Input**: Emacs-style prefix + command key combinations (Ctrl+Shift+S + key)
- **Background Operation**: Continuous global hotkey monitoring across all applications
- **Configurable Mappings**: Customizable key bindings via JSON configuration
- **Timeout Management**: Configurable timeout for key sequence completion
- **Real-time Processing**: Instant clipboard transformation without application switching
- **System Integration**: Works with any application that uses clipboard
- **Memory Efficient**: Minimal resource usage for background monitoring
- **Cross-platform Support**: Windows 10/11 with global hotkey capabilities
- **Enhanced Documentation**: Comprehensive hotkey usage examples and troubleshooting

### Version 2.3.0 (Modern CLI & Type Safety)
- **Modern Typer CLI**: Professional command-line interface with subcommands
- **Enhanced Type Safety**: Comprehensive type hints and Pylance compatibility
- **Modular Architecture**: Clean separation into packages and modules
- **IDE Integration**: VSCode configuration for optimal development experience
- **Build System**: Modern pyproject.toml configuration
- **Documentation**: Updated for new CLI interface and architecture

### Version 2.2.0 (Dynamic Clipboard Enhancement)
- **Dynamic Clipboard Refresh**: Refresh input text from clipboard during interactive sessions
- **Auto-Detection**: Automatic clipboard change monitoring with notifications (always enabled)
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
