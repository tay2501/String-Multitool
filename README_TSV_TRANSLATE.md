# TSV Translator System

A clean, educational implementation of a TSV-to-database synchronization system with string conversion capabilities.

## 🎓 Educational Features

This project demonstrates modern Python development best practices:

- **Clean Architecture**: Separation of concerns with distinct layers (models, services, CLI)
- **SOLID Principles**: Dependency injection, interface segregation, and single responsibility
- **Type Safety**: Comprehensive type hints following PEP 484/526
- **Database Design**: Optimized SQLAlchemy 2.0 models with proper indexing
- **Error Handling**: Hierarchical exception design with specific error types
- **Testing**: Comprehensive test suite with pytest and proper fixtures
- **Security**: Optional database encryption with proper key management

## 🚀 Quick Start

### Installation

#### Recommended: UV Package Manager

```bash
# Install with uv (recommended - fastest dependency resolution)
uv sync --group dev

# Create required directories
mkdir -p data logs config/tsv_rules

# Verify TSV functionality
uv run python String_Multitool.py /tsvtr --help
```

#### Alternative: Traditional Pip

```bash
# Install dependencies
pip install -e .

# Or with requirements file
pip install -r requirements.txt

# Create directories
mkdir -p data logs config/tsv_rules
```

### Basic Usage

#### Modern CLI Interface with Case-Insensitive Support

```bash
# Standard TSV conversion
uv run python String_Multitool.py /tsvtr technical_terms.tsv

# NEW: Case-insensitive matching (powerful feature for flexible conversion)
echo "api documentation" | uv run python String_Multitool.py /tsvtr tech_terms.tsv --case-insensitive
# Result: "Application Programming Interface documentation"

# Database management
uv run python -m tsv_translate.cli.main ls                     # List rule sets
uv run python -m tsv_translate.cli.main sync config/tsv_rules  # Sync TSV files
uv run python -m tsv_translate.cli.main info japanese_english  # Rule set details

# Interactive database shell
uv run python -m tsv_translate.cli.main --shell litecli       # Enhanced SQLite shell
```

## 📁 Project Structure

```
tsv_translator/
├── models/              # SQLAlchemy data models
│   ├── base.py         # Base model with audit fields
│   ├── rule_set.py     # TSV file metadata
│   └── conversion_rule.py  # Individual conversion rules
├── services/           # Business logic layer
│   ├── base.py         # Abstract service base class
│   ├── sync_service.py # File-database synchronization
│   ├── conversion_service.py  # Text conversion operations
│   └── file_watcher.py # File system monitoring
├── cli/                # Command-line interface
│   ├── main.py         # Main CLI implementation
│   └── completion.py   # Tab completion support
├── core/               # Core utilities and types
│   ├── engine.py       # Main facade/coordinator
│   ├── exceptions.py   # Exception hierarchy
│   ├── types.py        # Data classes and types
│   └── security.py     # Security and encryption
└── tests/              # Comprehensive test suite
    ├── conftest.py     # Test fixtures
    ├── test_models.py  # Model testing
    ├── test_services.py # Service layer testing
    ├── test_engine.py  # Integration testing
    └── test_cli.py     # CLI testing
```

## 🗄️ Database Design

### Tables

**rule_sets** - TSV file metadata
- `id`: Primary key
- `name`: Unique rule set name (derived from filename)
- `file_path`: Absolute path to TSV file
- `file_hash`: SHA-256 hash for change detection
- `rule_count`: Number of conversion rules
- `created_at`, `updated_at`: Audit timestamps

**conversion_rules** - Individual conversion pairs
- `id`: Primary key
- `rule_set_id`: Foreign key to rule_sets
- `source_text`: Text to be converted (indexed)
- `target_text`: Conversion result
- `usage_count`: Usage statistics

### Optimizations

- **Composite Index**: `(rule_set_id, source_text)` for fast conversion lookups
- **Unique Constraints**: Prevent duplicate rule sets and rules
- **Cascade Deletes**: Automatic cleanup when rule sets are removed
- **Usage Statistics**: Performance monitoring and optimization insights

## 📄 TSV File Format

```tsv
hello	こんにちは
goodbye	さようなら
thank you	ありがとう
```

**Requirements:**
- UTF-8 encoding
- CRLF line endings
- Tab-separated values
- No header row
- Two columns: source_text → target_text

## 🔧 Configuration

Edit `config/tsv_translator.json`:

```json
{
  "database_url": "sqlite:///data/tsv_translator.db",
  "tsv_directory": "config/tsv_rules",
  "enable_file_watching": true,
  "security": {
    "enable_encryption": false,
    "key_derivation_iterations": 100000
  },
  "performance": {
    "connection_pool_size": 5,
    "sync_batch_size": 1000
  }
}
```

## 🛡️ Security Features

### Database Encryption (Optional)

Enable database encryption in configuration:

```json
{
  "security": {
    "enable_encryption": true,
    "encryption_algorithm": "AES-256-GCM"
  }
}
```

**Key Management:**
- Keys derived using PBKDF2 with configurable iterations
- Secure key storage with proper file permissions
- Environment variable support for master passwords

## 🧪 Testing

### Comprehensive Test Suite with Modern Pytest

```bash
# Run all TSV-related tests with uv
uv run pytest tests/ -m "tsv" -v

# Test case-insensitive functionality specifically
uv run pytest tests/ -m "tsv" -k "case_insensitive" -v

# Run with coverage reporting
uv run pytest tests/ -m "tsv" --cov=string_multitool --cov-report=html

# Performance testing for large TSV files
uv run pytest tests/ -m "tsv and performance" -v

# Traditional method (if not using uv)
python -m pytest tests/ -m "tsv" -v
```

## 📊 Performance Characteristics

- **Conversion Speed**: Sub-millisecond lookups via optimized indexing
- **Sync Performance**: Batch processing for large TSV files
- **Memory Usage**: Efficient SQLAlchemy session management
- **Scalability**: Tested with 10K+ conversion rules

## 🎯 Design Patterns Demonstrated

1. **Repository Pattern**: Data access abstraction
2. **Service Layer**: Business logic encapsulation
3. **Facade Pattern**: Simplified interface (TSVConverterEngine)
4. **Factory Pattern**: Dynamic service creation
5. **Observer Pattern**: File system change notifications
6. **Strategy Pattern**: Configurable security implementations

## 🔍 Code Quality

### Type Safety
```python
# Comprehensive type annotations
def convert_text(self, text: str, rule_set_name: str) -> ConversionResult:
    """Convert text with full type safety."""
```

### Error Handling
```python
# Specific exception types
class ValidationError(TSVConverterError):
    """Raised when data validation fails."""

class SyncError(TSVConverterError):
    """Raised when synchronization fails."""
```

### Clean Architecture
```python
# Dependency injection
class ConversionService(BaseService):
    def __init__(self, db_session: Session) -> None:
        self._db_session = db_session
```

## 🚀 Advanced Usage

### Case-Insensitive TSV Conversion (New Feature)

The enhanced TSV system now supports flexible case-insensitive matching:

```bash
# Create technical glossary
echo -e "API\tApplication Programming Interface\nSQL\tStructured Query Language\nREST\tRepresentational State Transfer" > tech_terms.tsv

# Standard conversion (case-sensitive)
echo "Use API with SQL" | uv run python String_Multitool.py /tsvtr tech_terms.tsv
# Result: "Use Application Programming Interface with Structured Query Language"

# Case-insensitive conversion (flexible matching)
echo "api and rest integration" | uv run python String_Multitool.py /tsvtr tech_terms.tsv --case-insensitive
# Result: "Application Programming Interface and Representational State Transfer integration"

# Mixed case input handling
echo "Modern sql and Api patterns" | uv run python String_Multitool.py /tsvtr tech_terms.tsv --case-insensitive
# Result: "Modern Structured Query Language and Application Programming Interface patterns"
```

### Database Management

```bash
# Install development dependencies for enhanced database tools
uv sync --group dev

# Enhanced SQLite shell with syntax highlighting
uv run python -m tsv_translate.cli.main --shell litecli

# Standard SQLite shell
uv run python -m tsv_translate.cli.main --shell sqlite3
```

### Development and Testing

#### File Watching (Development Mode)

Enable automatic synchronization in development:

```json
{
  "enable_file_watching": true,
  "case_insensitive_default": false
}
```

The system will automatically detect TSV file changes and update the database.

#### Testing Case-Insensitive Features

```bash
# Test the new case-insensitive functionality
uv run pytest tests/ -m "tsv" -k "case_insensitive" -v

# Benchmark case-insensitive performance
uv run pytest tests/ -m "tsv and performance" --benchmark-only
```

### Direct Database Access

```bash
# Connect to SQLite database directly
sqlite3 data/tsv_translator.db

# Example queries
.schema
SELECT * FROM rule_sets;
SELECT * FROM conversion_rules WHERE usage_count > 10;
```

## 🤝 Contributing

This educational codebase demonstrates:

- Clean commit messages following conventional commits
- Comprehensive test coverage
- Type safety with mypy
- Code formatting with black
- Import sorting with isort
- Documentation following PEP 257

## 📚 Learning Resources

This implementation showcases concepts from:

- **Clean Architecture** (Robert Martin)
- **SQLAlchemy 2.0** best practices
- **Modern Python** (type hints, dataclasses, context managers)
- **Database Design** principles and optimization
- **Security** best practices for data protection

## 📝 License

Educational implementation for learning purposes.