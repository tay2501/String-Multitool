# Clipboard Transformer

A powerful command-line text transformation tool with pipe support and intuitive rule-based syntax. Transform text from clipboard or stdin using simple `/rule` commands with support for sequential processing.

## Features

- **Intuitive Syntax**: Use `/rule` format for transformations (e.g., `/t/l` for trim + lowercase)
- **Pipe Support**: Works with stdin/stdout for seamless integration with shell commands
- **Interactive Mode**: Prompt-based interface when no arguments provided
- **Sequential Processing**: Chain multiple transformations (e.g., `/t/l/u`)
- **Argument Support**: Advanced rules with parameters (e.g., `/R 'old' 'new'`)
- **Clipboard Integration**: Automatically copies results to clipboard
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Unicode Support**: Full-width ↔ half-width character conversion for Japanese text

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
```

### Interactive Mode

When no arguments are provided, the app enters interactive mode:

```bash
python String_Multitool.py
# 📋 Clipboard Transformer - Interactive Mode
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
cd clipboard-transformer

# Install dependencies
pip install -r requirements.txt

# Test installation
python String_Multitool.py help
```

### Dependencies

The application requires minimal dependencies:

```
pyperclip>=1.8.0  # Clipboard operations
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
clipboard-transformer/
├── String_Multitool.py       # Main application
├── test_transform.py         # Test suite
├── requirements.txt          # Dependencies
└── README.md                # Documentation
```

### Running Tests

```bash
python test_transform.py
```

### Adding New Rules

1. Add rule function to `TextTransformer` class
2. Register in `self.rules` or `self.arg_rules` dictionary
3. Add test cases to `test_transform.py`
4. Update documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 2.0.0
- Complete rewrite with new rule-based syntax
- Added pipe support for stdin/stdout
- Implemented sequential rule processing
- Added argument support for advanced rules
- Improved Unicode handling for Japanese text
- Simplified command-line interface
- Added comprehensive test suite
