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

```bash
# Install dependencies
pip install -r requirements-tsv.txt

# Create directories
mkdir -p data logs config/tsv_rules
```

### Basic Usage

```bash
# List available rule sets
python tsvtr.py ls

# Convert clipboard text using a rule set
python tsvtr.py japanese_english

# Sync TSV files with database
python tsvtr.py sync config/tsv_rules

# Get detailed information about a rule set
python tsvtr.py info japanese_english
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

```bash
# Run all tests
python -m pytest tsv_translator/tests/ -v

# Run with coverage
python -m pytest tsv_translator/tests/ --cov=tsv_translator --cov-report=html

# Run specific test categories
python -m pytest tsv_translator/tests/test_models.py -v
python -m pytest tsv_translator/tests/test_services.py -v
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

### Tab Completion

Enable tab completion for rule set names:

```bash
# Install argcomplete
pip install argcomplete

# Enable completion
eval "$(register-python-argcomplete tsvtr.py)"
```

### File Watching

Enable automatic synchronization:

```json
{
  "enable_file_watching": true
}
```

The system will automatically detect TSV file changes and update the database.

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