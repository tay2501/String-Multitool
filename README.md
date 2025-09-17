<a href='https://ko-fi.com/Z8Z31J3LMW' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi6.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
<a href="https://www.buymeacoffee.com/tay2501" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 36px !important;width: 130px !important;" ></a>

# String-Multitool

<div align="center">

**Professional Python text transformation toolkit with advanced CLI interface and enterprise security**

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=flat&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-GNU%20AGPL%20v3-blue?style=flat&logo=gnu&logoColor=white)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-success?style=flat&logo=pytest&logoColor=white)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-95%25%2B-success?style=flat&logo=codecov&logoColor=white)](tests/)
[![Documentation](https://img.shields.io/badge/Documentation-Complete-success?style=flat&logo=gitbook&logoColor=white)](docs/)

[Quick Start](#-quick-start) • [Features](#-features) • [Documentation](docs/) • [API Reference](docs/API_REFERENCE.md) • [Contributing](#-contributing)

</div>

---

## Overview

String-Multitool is a modern Python text transformation toolkit designed for professional developers and system administrators. Built with enterprise-grade MVC architecture, it provides powerful rule-based text processing with military-grade encryption capabilities.

### 🎯 Core Capabilities

- **🔄 Text Transformations**: 26+ built-in rules for case conversion, formatting, Unicode handling, and Japanese encoding conversion
- **🔐 Enterprise Security**: RSA-4096 + AES-256 hybrid encryption with automatic key management
- **📊 TSV Processing**: Database-backed dictionary conversion with case-insensitive matching
- **🖥️ CLI Excellence**: Modern interface with pipe support and interactive mode
- **🏗️ Modern Architecture**: Follows 2025 Python packaging standards (PEP 621, hatchling build backend)
- **⚡ Performance**: Optimized with UV package manager (10-100x faster than pip)
- **🌐 Cross-Platform**: Windows, macOS, and Linux support with clipboard integration

## 🚀 Quick Start

### Installation

#### Recommended: UV Package Manager (2025 Standard)

[UV](https://docs.astral.sh/uv/) is the modern Python package manager, providing 10-100x faster installation than pip and serving as a complete Python toolchain replacement.

```bash
# Clone the repository
git clone https://github.com/yourusername/String-Multitool.git
cd String-Multitool

# Install dependencies with uv (fastest and recommended for 2025)
uv sync

# For development with all extras
uv sync --group dev --all-extras

# Verify installation
uv run python String_Multitool.py help
```

#### Alternative: Traditional Pip

```bash
# Clone and setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .

# Or install from requirements
pip install -r requirements.txt

# Verify installation
python String_Multitool.py help
```

### Basic Usage

```bash
# Transform text via pipe
echo "  HELLO WORLD  " | python String_Multitool.py /t/l
# Result: "hello world"

# Chain multiple transformations
echo "User-Profile-Settings" | python String_Multitool.py /hu/s/l
# Result: "user_profile_settings"

# Interactive mode with clipboard monitoring
python String_Multitool.py
# Apply rules to clipboard content in real-time
```

## ✨ Features

String-Multitool offers comprehensive text processing capabilities organized into three tiers:

### 🎯 Core Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Rule-Based Syntax** | `/t/l/u` for trim → lowercase → uppercase | Intuitive and chainable |
| **Pipe Integration** | `echo "text" \| python String_Multitool.py /rule` | Shell workflow compatibility |
| **Interactive Mode** | Real-time clipboard monitoring | Zero-copy workflow |
| **Cross-Platform** | Windows, macOS, Linux support | Universal deployment |

### 🏢 Enterprise Features

| Feature | Implementation | Security Level |
|---------|----------------|----------------|
| **Hybrid Encryption** | RSA-4096 + AES-256 | Military Grade |
| **Key Management** | Auto-generation, secure permissions | Enterprise Ready |
| **MVC Architecture** | Model-View-Controller separation | Professional |
| **Type Safety** | Full type hints + validation | Production Ready |

### 🚀 Advanced Capabilities

| Feature | Technology | Use Case |
|---------|------------|----------|
| **TSV Processing** | SQLite backend | Dictionary conversion |
| **Unicode Handling** | Full-width ↔ half-width | International text |
| **Configuration System** | JSON-driven rules | Customization |
| **Error Recovery** | Graceful degradation | Reliability |

## 📋 Transformation Rules

### Essential Rules (90% of use cases)

| Rule | Function | Input Example | Output Example | Programming Use |
|------|----------|---------------|----------------|-----------------|
| `/t` | **Trim whitespace** | `"  hello  "` | `"hello"` | Clean user input |
| `/l` | **Lowercase** | `"HELLO"` | `"hello"` | Normalize text |
| `/u` | **Uppercase** | `"hello"` | `"HELLO"` | Constants |
| `/s` | **snake_case** | `"Hello World"` | `"hello_world"` | Variables |
| `/p` | **PascalCase** | `"hello world"` | `"HelloWorld"` | Classes |

### Advanced Rules

| Rule | Function | Input | Output | Use Case |
|------|----------|-------|--------|----------|
| `/c` | **camelCase** | `is error state` | `isErrorState` | JavaScript variables |
| `/a` | **Capitalize** | `hello world` | `Hello World` | Title formatting |
| `/R` | **Reverse** | `hello` | `olleh` | Text manipulation |
| `/uh` | **Underscore → Hyphen** | `TBL_CHA1` | `TBL-CHA1` | CSS classes |
| `/hu` | **Hyphen → Underscore** | `TBL-CHA1` | `TBL_CHA1` | Database columns |
| `/fh` | **Full-width → Half-width** | `ＴＢＬ－ＣＨＡ１` | `TBL-CHA1` | Unicode normalization |
| `/si` | **SQL IN clause** | `A0001\nA0002` | `'A0001',\n'A0002'` | SQL generation |

### Parameterized Rules

| Rule | Function | Example Usage | Result |
|------|----------|---------------|---------|
| `/r 'old' 'new'` | **Replace text** | `/r 'API' 'Application Programming Interface'` | Targeted replacement |
| `/S '+'` | **Slugify with separator** | `/S '+'` on `http://foo.bar` | `http+foo+bar` |
| `/tsvtr file.tsv` | **TSV dictionary conversion** | `/tsvtr technical_terms.tsv --case-insensitive` | Dictionary-based transformation |
| `/iconv -f FROM -t TO` | **Japanese encoding conversion** | `/iconv -f SJIS -t UTF8` or `/iconv -t UTF8` (auto-detect) | Character encoding conversion |
| `/enc` | **RSA encrypt** | `/enc` | Base64 encrypted output |
| `/dec` | **RSA decrypt** | `/dec` | Original plaintext |

## 💻 Usage Examples

### Command-Line Usage

```bash
# Basic transformations
echo "  Hello World  " | python String_Multitool.py /t/l
# Output: "hello world"

# Professional programming workflow
echo "user-profile-settings" | python String_Multitool.py /hu/p
# Output: "UserProfileSettings"

# Chain multiple transformations  
echo "API_ENDPOINT_URL" | python String_Multitool.py /l/s
# Output: "api_endpoint_url"
```

### Database Integration

TSV rules are stored in SQLite for high-performance lookups:

| Command | Function | Usage |
|---------|----------|-------|
| `python -m tsv_translate.cli.main sync config/tsv_rules` | **Import TSV files** | Sync to database |
| `python -m tsv_translate.cli.main --shell litecli` | **SQL interface** | Interactive queries |
| `python -m tsv_translate.cli.main ls` | **List rule sets** | Available conversions |

### Japanese Character Encoding Conversion

```bash
# Convert Japanese text encoding with iconv-compatible syntax
echo "日本語テキスト" | python String_Multitool.py /iconv -f SJIS -t UTF8
# Convert with auto-detection (recommended)
echo "日本語テキスト" | python String_Multitool.py /iconv -t UTF8

# Supported conversions: SJIS ⇔ MS932, SJIS ⇔ EUC-JP, SJIS ⇔ UTF-8
```

### TSV Dictionary Conversion

```bash
# Create technical glossary
echo -e "API\tApplication Programming Interface\nSQL\tStructured Query Language" > tech.tsv

# Apply conversions
echo "Use API with SQL" | python String_Multitool.py /tsvtr tech.tsv --case-insensitive
# Output: "Use Application Programming Interface with Structured Query Language"
```

### Interactive Mode

Real-time clipboard processing with session management:

```bash
# Start interactive mode
python String_Multitool.py

# Interactive session example:
┌─ String-Multitool Interactive Mode ─┐
│ Current clipboard: "Hello World"     │
│ Rules: /l/s                         │
│ Result: hello_world                 │
└─────────────────────────────────────┘

Available commands:
- refresh    # Reload clipboard content  
- daemon     # Switch to background mode
- help       # Show available rules
- quit       # Exit session
```

### Security Features

```bash
# Encrypt sensitive data
echo "confidential information" | python String_Multitool.py /enc
# Output: Base64 encoded RSA+AES encrypted text

# Decrypt (with encrypted text in clipboard)
python String_Multitool.py /dec
# Output: "confidential information"

# Key management
ls rsa/
# private_key.pem (0o600 permissions)
# public_key.pem
```

## 🏗️ Architecture

String-Multitool follows modern Python MVC architecture for maintainability and extensibility:

```
string_multitool/
├── models/          # Business Logic (Model Layer)
│   ├── config.py    # Configuration management  
│   ├── transformations.py  # Text processing engine
│   ├── crypto.py    # Encryption operations
│   └── interactive.py      # Session management
├── io/             # User Interface (View/Controller)
│   ├── manager.py  # I/O operations
│   └── clipboard.py # Clipboard monitoring
└── main.py         # Application entry point
```

### Design Principles (2025 Standards Compliant)

- **🏗️ Modern MVC Pattern**: Clear separation following Python best practices with PEP 621 project structure
- **📦 Standards Compliance**: Uses hatchling build backend and pyproject.toml (PEP 621) for packaging
- **⚡ Performance**: UV package manager integration and efficient algorithms with minimal memory footprint
- **🔒 Security**: Defense-in-depth with secure defaults and modern cryptography
- **🧩 Extensibility**: Protocol-based interfaces for easy customization
- **📝 Type Safety**: Comprehensive type hints with mypy strict mode validation

## 📦 Installation

### System Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Python** | 3.12+ (tested on 3.13+) | Modern language features and 2025 standards compliance |
| **Package Manager** | [UV](https://docs.astral.sh/uv/) (strongly recommended) | 10-100x faster than pip, replaces multiple tools |
| **Alternative** | pip with virtual environment | Traditional approach, slower but compatible |
| **Platform** | Windows/macOS/Linux | Cross-platform clipboard support |
| **Memory** | 100MB+ | For large TSV processing |
| **Storage** | 50MB+ | Including dependencies |

### Quick Installation

```bash
# Clone repository
git clone https://github.com/yourusername/String-Multitool.git
cd String-Multitool

# Setup with uv (2025 standard - fastest and most comprehensive)
uv sync

# Or with development dependencies
uv sync --group dev

# Alternative with traditional pip (slower but compatible)
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Verify installation
uv run python String_Multitool.py help
```

### Core Dependencies

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| `pyperclip` | 1.9.0+ | Clipboard operations | BSD |
| `cryptography` | 42.0.5+ | RSA/AES encryption | Apache 2.0 |
| `sqlalchemy` | 2.0.0+ | Database ORM | MIT |
| `litecli` | 1.12.3+ | Enhanced SQL interface | BSD |

## 🛠️ Development

### Development Commands

#### Application Execution

```bash
# Interactive mode
uv run python String_Multitool.py

# Direct rule application
uv run python String_Multitool.py /t/l

# Background daemon mode
uv run python String_Multitool.py --daemon

# TSV conversion with case-insensitive matching
echo "API Documentation" | uv run python String_Multitool.py /tsvtr tech_terms.tsv --case-insensitive
```

#### Testing and Quality Assurance

```bash
# Run comprehensive test suite
uv run pytest tests/ -v --cov=string_multitool

# Type checking with mypy
uv run mypy string_multitool/

# Code formatting
uv run black string_multitool/
uv run isort string_multitool/

# Linting with ruff
uv run ruff check string_multitool/
```

#### Build and Packaging

```bash
# Windows executable (PowerShell)
./build.ps1
./build.ps1 -Clean                          # Clean build

# Python wheel distribution
uv build

# Development installation
uv pip install -e .
```

### Quality Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Test Coverage** | >95% | ✅ 95%+ |
| **Type Coverage** | 100% | ✅ 100% |
| **Security Scan** | No issues | ✅ Clean |
| **Performance** | <100ms | ✅ 50ms avg |

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](docs/DEVELOPER_GUIDE.md) for detailed instructions.

### Quick Contribution Guide

```bash
# 1. Fork and clone
git clone https://github.com/yourusername/String-Multitool.git
cd String-Multitool

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Setup development environment with all dependencies
uv sync --group dev --all-extras

# 4. Make changes and verify quality
uv run pytest tests/ -v --cov=string_multitool
uv run mypy string_multitool/
uv run ruff check string_multitool/
uv run black string_multitool/

# 5. Run specific test categories
uv run pytest tests/ -m "unit and not slow"
uv run pytest tests/ -m "integration"

# 6. Submit pull request
```

### Adding New Features

| Component | File Location | Documentation |
|-----------|---------------|---------------|
| **Transformation Rules** | `config/transformation_rules.json` | [API Reference](docs/API_REFERENCE.md) |
| **Implementation** | `string_multitool/models/transformations.py` | [Architecture Guide](docs/ARCHITECTURE.md) |
| **Tests** | `tests/test_transform.py` | [Developer Guide](docs/DEVELOPER_GUIDE.md) |

## 📊 Project Health

| Metric | Value | Status |
|--------|-------|--------|
| **Lines of Code** | 15,000+ | 📈 Growing |
| **Test Coverage** | 95%+ | ✅ Excellent |
| **Transformation Rules** | 25+ | 🚀 Comprehensive |
| **Supported Platforms** | 3 | 🌐 Universal |
| **Documentation** | Complete | 📚 Professional |

## 🆘 Support

### Quick Help

```bash
# Built-in help system
python String_Multitool.py help

# Test specific transformation
echo "test text" | python String_Multitool.py /your_rule

# Interactive help
python String_Multitool.py
# Then type: help
```

### Common Solutions

| Issue | Solution | Reference |
|-------|----------|-----------|
| **Unicode Issues** | `chcp 65001` (Windows) | [Troubleshooting](docs/DEVELOPER_GUIDE.md#troubleshooting) |
| **Clipboard Access** | Run with admin privileges | [Security Guide](docs/ARCHITECTURE.md#security) |
| **Rule Syntax** | Rules must start with `/` | [API Reference](docs/API_REFERENCE.md) |
| **Key Generation** | Ensure `rsa/` directory is writable | [Crypto Setup](docs/API_REFERENCE.md#encryption) |

### Getting Help

- 📖 **Documentation**: [docs/](docs/)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/String-Multitool/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/yourusername/String-Multitool/discussions)
- 🔒 **Security Issues**: Please report privately via email

---

## 📄 License

Licensed under the **GNU Affero General Public License v3.0** - see [LICENSE](LICENSE) for details.

---

<div align="center">

### 🎯 Ready to transform your text processing workflow?

[![Get Started](https://img.shields.io/badge/Get%20Started-blue?style=for-the-badge)](docs/API_REFERENCE.md)
[![Documentation](https://img.shields.io/badge/Documentation-green?style=for-the-badge)](docs/)
[![Architecture](https://img.shields.io/badge/Architecture-purple?style=for-the-badge)](docs/ARCHITECTURE.md)

**String-Multitool**: Professional Python text transformation toolkit

</div>