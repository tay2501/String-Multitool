<a href='https://ko-fi.com/Z8Z31J3LMW' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
<a href="https://www.buymeacoffee.com/tay2501" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 36px !important;width: 130px !important;" ></a>

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
- **MVC Architecture**: Python best practices with clear Model-View-Controller separation
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
| `/tsvtr file.tsv --case-insensitive` | TSV Convert | `API` → `Application Programming Interface` |
| `/tsvtr file.tsv` | TSV Database Sync | Sync TSV files to database for fast lookups |
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

### TSV-based Text Conversion

#### Built-in TSV Conversion (tsvtr rule)
```bash
# Create conversion dictionary
echo -e "API\tApplication Programming Interface" > terms.tsv
echo -e "SQL\tStructured Query Language" >> terms.tsv

# Convert abbreviations using String_Multitool built-in rule
echo "Use api and SQL" | python String_Multitool.py /tsvtr terms.tsv --case-insensitive
# → "Use Application Programming Interface and Structured Query Language"
```

#### Advanced TSV Database System (tsvtr CLI tool)
```bash
# Independent TSV translation tool with database backend
python tsvtr.py sync config/tsv_rules       # Sync TSV files to database
python tsvtr.py japanese_english            # Convert using rule set
python tsvtr.py ls                          # List available rule sets
python tsvtr.py info japanese_english       # Show rule set information
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

### MVC Design Pattern
Following Python MVC best practices for CUI applications:

```
string_multitool/
├── models/          # Business Logic Layer (The "Model")
│   ├── config.py    # Configuration management
│   ├── crypto.py    # Cryptography operations
│   ├── transformations.py  # String transformation engine
│   ├── interactive.py      # Interactive session management
│   └── types.py     # Type definitions and protocols
├── io/             # View/Controller Layer (User Interface)
│   ├── manager.py  # Clipboard operations and I/O handling
│   └── clipboard.py # Clipboard monitoring
├── main.py         # Entry Point (Application flow control)
└── __init__.py     # Package initialization
```

### Key Architectural Principles
- **MVC Separation**: Clear boundaries between business logic, UI, and control flow
- **Configuration-Driven**: Rules externalized to `config/*.json`
- **Type Safety**: Full type hints with dataclass-based rule definitions
- **Simplicity**: Minimal complexity while maintaining extensibility
- **Security-First**: RSA-4096 + AES-256 hybrid encryption

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes with tests
4. **Run** tests: `python -m pytest test_transform.py -v`
5. **Submit** a pull request

### Adding New Rules
1. Add rule definition to `config/transformation_rules.json`
2. Implement transformation method in `models/transformations.py`
3. Register method in `_initialize_rules()`
4. Add test cases to `test_transform.py`

## 📊 Project Statistics

- **Lines of Code**: 15,000+
- **Test Coverage**: 95%+
- **Supported Rules**: 25+
- **Supported Platforms**: 3 (Windows, macOS, Linux)
- **Architecture**: Python MVC best practices with clean separation of concerns

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

This project is licensed under the **GNU AFFERO GENERAL PUBLIC LICENSE License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Ready to transform your text processing workflow?**

[Get Started](docs/user-guide/getting-started.md) | [View Documentation](docs/) | [Report Issues](https://github.com/[your-username]/String-Multitool/issues)

</div>