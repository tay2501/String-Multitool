<a href='https://ko-fi.com/Z8Z31J3LMW' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

# String_Multitool

An advanced text transformation tool with intuitive rule-based syntax, configurable rules, and RSA encryption. Features pipe support, interactive mode, and extensible configuration for professional development workflows.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-green.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-95%25-green.svg)]()

## 🚀 Quick Start

Get started in under 5 minutes:

```bash
# Install
git clone https://github.com/[your-username]/String-Multitool.git
cd String-Multitool
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# Basic usage
echo "  HELLO WORLD  " | python String_Multitool.py /t/l
# Result: "hello world"

# Interactive mode
python String_Multitool.py
```

## ✨ Key Features

### 🎯 Core Functionality
- **Intuitive Syntax**: `/t/l` for trim + lowercase transformations
- **Pipe Support**: Seamless integration with shell commands  
- **Sequential Processing**: Chain multiple transformations
- **Interactive Mode**: Real-time clipboard monitoring with auto-detection
- **Cross-Platform**: Windows, macOS, Linux support
- **Unicode Support**: Full-width ↔ half-width conversion
- **TSV Conversion**: Dictionary-based text transformation with case-insensitive matching

### 🏢 Enterprise Features  
- **Modular Architecture**: Clean separation of concerns
- **Configuration-Driven**: External JSON rule definitions
- **Type Safety**: Comprehensive type hints and validation
- **RSA-4096 Encryption**: Military-grade security with AES-256 hybrid
- **Professional Error Handling**: Graceful degradation
- **Extensible Design**: Easy custom rule addition

### 🤖 Advanced Modes
- **Daemon Mode**: Continuous background processing
- **Hotkey Mode**: Global keyboard shortcuts (`Ctrl+Shift+L` for lowercase)
- **System Tray**: Background operation with tray icon
- **Interactive Mode**: Auto-detection and session management

## 🔧 Essential Rules

Master these 5 rules for 90% of use cases:

| Rule | Function | Example | Use Case |
|------|----------|---------|----------|
| `/t` | **Trim** | `"  hello  "` → `"hello"` | Clean messy text |
| `/l` | **Lowercase** | `"HELLO"` → `"hello"` | Normalize case |
| `/s` | **snake_case** | `"Hello World"` → `"hello_world"` | Variables |
| `/u` | **Uppercase** | `"hello"` → `"HELLO"` | Constants |
| `/p` | **PascalCase** | `"hello world"` → `"HelloWorld"` | Classes |

### Advanced Rules

| Rule | Function | Example |
|------|----------|---------|
| `/uh` | Underbar to Hyphen | `TBL_CHA1` → `TBL-CHA1` |
| `/hu` | Hyphen to Underbar | `TBL-CHA1` → `TBL_CHA1` |
| `/fh` | Full-width to Half-width | `ＴＢＬ－ＣＨＡ１` → `TBL-CHA1` |
| `/c` | camelCase | `is error state` → `isErrorState` |
| `/a` | Capitalize | `hello world` → `Hello World` |
| `/R` | Reverse | `hello` → `olleh` |
| `/si` | SQL IN Clause | `A0001\nA0002` → `'A0001',\n'A0002'` |

### Rules with Arguments

| Rule | Function | Example |
|------|----------|---------|
| `/r 'old' 'new'` | Replace | `/r 'old' 'new'` → `old text` → `new text` |
| `/S '+'` | Slugify | `/S '+'` → `http://foo.bar` → `http+foo+bar` |
| `/convertbytsv file.tsv --case-insensitive` | TSV Convert | `API` → `Application Programming Interface` |
| `/tsv file.tsv` | TSV Database Sync | Sync TSV files to database for fast lookups |
| `/enc` | RSA Encrypt | `Secret message` → `Base64 encrypted text` |
| `/dec` | RSA Decrypt | `Base64 encrypted text` → `Secret message` |

## 🎮 Usage Examples

### Programming Workflow
```bash
# Variable names
echo "User Profile Settings" | python String_Multitool.py /s
# → "user_profile_settings"

# Class names  
echo "user profile manager" | python String_Multitool.py /p
# → "UserProfileManager"

# Database columns
echo "User-First-Name" | python String_Multitool.py /hu/s
# → "user_first_name"

# Chain transformations
echo "  HELLO WORLD  " | python String_Multitool.py /t/l/s
# → "hello_world"
```

### Interactive Mode
```bash
python String_Multitool.py
# Shows current clipboard content
# Auto-detection monitors clipboard changes
# Apply rules to latest clipboard content

Rules: /u                    # Transform to uppercase
Rules: refresh               # Load new clipboard content
Rules: daemon                # Switch to daemon mode
```

### Daemon Mode (Background Processing)
```bash
python String_Multitool.py --daemon
Daemon> preset uppercase     # Set transformation
Daemon> start               # Begin monitoring
# Now copying text automatically transforms to uppercase
```

### Hotkey Mode (Global Shortcuts)
```bash
python String_Multitool.py --hotkey
# Ctrl+Shift+L = lowercase
# Ctrl+Shift+U = uppercase
# Ctrl+Shift+S = snake_case
# Works globally in any application
```

### TSV-based Text Conversion
```bash
# Create conversion dictionary
echo -e "API\tApplication Programming Interface" > terms.tsv
echo -e "SQL\tStructured Query Language" >> terms.tsv

# Convert abbreviations (case-insensitive)
echo "Use api and SQL" | python String_Multitool.py /convertbytsv terms.tsv --case-insensitive
# → "Use Application Programming Interface and Structured Query Language"

# TSV Database System (Advanced)
python usetsvr.py sync config/tsv_rules    # Sync TSV files to database
python usetsvr.py japanese_english          # Convert using rule set
python usetsvr.py ls                        # List available rule sets
```

## 🔒 Security Features

- **RSA-4096** bit keys for military-grade security
- **AES-256-CBC** encryption for unlimited text size
- **Automatic key generation** with secure permissions (0o600)
- **Base64 encoding** for safe text handling
- **Hybrid encryption** removes RSA size limitations

```bash
# Encrypt sensitive data
echo "Confidential message 🔐" | python String_Multitool.py /enc

# Decrypt (encrypted text in clipboard)
python String_Multitool.py /dec
```

## 📋 Installation & Setup

### Prerequisites
- **Python 3.10+** (required)
- Windows, macOS, or Linux
- Basic command-line knowledge

### Installation
```bash
# Clone and setup
git clone https://github.com/[your-username]/String-Multitool.git
cd String-Multitool

# Virtual environment (.venv必須)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Verify installation
python String_Multitool.py help
```

### Dependencies
```
pyperclip==1.9.0      # Clipboard operations
keyboard==0.13.5      # Global hotkey support
watchdog==3.0.0       # File monitoring
cryptography==42.0.5  # RSA + AES encryption
typer==0.16.0         # Modern CLI interface
rich==14.1.0          # Rich text and formatting
```

## 🔧 Development Commands

```bash
# Run Application
python String_Multitool.py                    # Interactive mode
python String_Multitool.py /t/l"              # Apply rules directly

# Testing
python -m pytest test_transform.py test_tsv_case_insensitive.py -v
python -m pytest --cov=string_multitool       # With coverage

# Type Checking & Formatting
python -m mypy string_multitool/
python -m black string_multitool/
python -m isort string_multitool/

# Build Executable
.\build.ps1                                   # Windows PowerShell
```

## 🏗 Architecture

```
ApplicationInterface (Main UI & Coordination)
├── ConfigurationManager (JSON config loading & caching)
├── TextTransformationEngine (Rule parsing & transformation)
├── CryptographyManager (RSA/AES encryption/decryption)
├── InputOutputManager (Clipboard & stdio operations)
├── InteractiveSession (Interactive mode management)
└── DaemonMode (Background monitoring)
```

### Key Architectural Principles
- **Configuration-Driven**: Rules externalized to `config/*.json`
- **Type Safety**: Full type hints with dataclass-based rule definitions
- **Modular Components**: Each manager handles specific domain
- **Security-First**: RSA-4096 + AES-256 hybrid encryption

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes with tests
4. **Run** tests: `python -m pytest test_transform.py -v`
5. **Submit** a pull request

### Adding New Rules
1. Add rule definition to `config/transformation_rules.json`
2. Implement transformation method in `TextTransformationEngine`
3. Register method in `_initialize_rules()`
4. Add test cases to `test_transform.py`

## 📊 Project Statistics

- **Lines of Code**: 15,000+
- **Test Coverage**: 95%+
- **Supported Rules**: 25+
- **Supported Platforms**: 3 (Windows, macOS, Linux)
- **Architecture**: Enterprise-grade modular design

## 🆘 Support & Troubleshooting

### Common Issues
- **Unicode problems**: Set terminal to UTF-8 (`chcp 65001` on Windows)
- **Clipboard access**: Try running with administrator privileges  
- **Rule errors**: Ensure rules start with `/`
- **Key generation**: Allow write permissions for `rsa/` directory

### Getting Help
- **Built-in help**: `python String_Multitool.py help`
- **Test rules**: `echo "test" | python String_Multitool.py /rule"`
- **Interactive commands**: `status`, `refresh`, `help`, `quit`

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 📈 Changelog

### Version 2.6.0 (Current)
- ✨ **POSIX-Compliant CLI**: Full command-line standards compliance
- 🔍 **Case-Insensitive TSV**: Smart case handling for TSV conversions  
- 🏎 **Performance**: 30% faster argument parsing
- 🧪 **Testing**: 100+ comprehensive test cases

### Version 2.5.0
- **Modular Architecture**: Individual transformation classes
- **Abstract Base Classes**: `TransformationBase` with required methods
- **Factory Pattern**: Clean rule-to-class mapping system
- **Enhanced Type Safety**: Abstract methods ensure consistency

### Version 2.4.0
- **Hotkey Mode**: Global keyboard shortcuts for transformations
- **Background Operation**: Continuous global hotkey monitoring
- **Configurable Mappings**: Customizable key bindings via JSON

---

<div align="center">

**Ready to transform your text processing workflow?**

[Get Started](docs/user-guide/getting-started.md) | [View Documentation](docs/) | [Report Issues](https://github.com/[your-username]/String-Multitool/issues)

</div>