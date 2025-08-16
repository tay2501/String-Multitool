# String_Multitool Architecture Documentation

## Overview

String_Multitool follows a modular, enterprise-grade architecture designed for maintainability, extensibility, and security. The application is structured using the separation of concerns principle with dedicated managers for different aspects of functionality.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    ApplicationInterface                      │
│  (Main UI and user interaction logic)                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌─────────┐ ┌─────────────┐ ┌─────────────────┐
│   I/O   │ │Transformation│ │  Configuration  │
│Manager  │ │   Engine     │ │    Manager      │
└─────────┘ └─────────────┘ └─────────────────┘
                  │                     │
                  ▼                     ▼
        ┌─────────────────┐    ┌─────────────────┐
        │  Cryptography   │    │  JSON Config    │
        │    Manager      │    │     Files       │
        └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. ApplicationInterface
**Purpose**: Main application entry point and user interaction handler

**Responsibilities**:
- Command-line argument parsing
- Interactive mode management
- Help system display
- Error handling and user feedback
- Coordination between other components

**Key Methods**:
- `run()`: Main application entry point
- `run_interactive_mode()`: Interactive user interface
- `run_command_mode()`: Command-line rule execution
- `display_help()`: Comprehensive help display

### 2. ConfigurationManager
**Purpose**: Manages application configuration from JSON files

**Responsibilities**:
- Loading and caching configuration files
- JSON parsing and validation
- Configuration file error handling
- Lazy loading of configuration data

**Configuration Files**:
- `config/transformation_rules.json`: Rule definitions and metadata
- `config/security_config.json`: Security and encryption settings
- `config/daemon_config.json`: Daemon mode presets and configuration
- `config/hotkey_config.json`: Hotkey mappings and settings
- `config/logging_config.json`: Logging configuration and levels

**Key Methods**:
- `load_transformation_rules()`: Load rule configurations
- `load_security_config()`: Load security settings

### 3. TextTransformationEngine
**Purpose**: Core text transformation logic with configurable rules

**Responsibilities**:
- Rule initialization from configuration
- Rule string parsing and validation
- Sequential transformation application
- Rule method registration and execution
- Error handling for transformation failures

**Rule Categories**:
- Basic transformations (character conversion)
- Case transformations (uppercase, lowercase, etc.)
- String operations (trim, reverse, etc.)
- Advanced rules with arguments
- Encryption/decryption operations

**Key Methods**:
- `apply_transformations()`: Apply rule chain to text
- `parse_rule_string()`: Parse rule syntax
- `get_available_rules()`: Return available rules

### 4. CryptographyManager
**Purpose**: RSA encryption and decryption with enhanced security

**Responsibilities**:
- RSA key pair generation and management
- Hybrid AES+RSA encryption/decryption
- Secure key storage with proper permissions
- Base64 encoding/decoding with validation
- Cryptographic parameter configuration

**Security Features**:
- RSA-4096 key generation
- AES-256-CBC for data encryption
- OAEP padding for RSA operations
- PKCS7 padding for AES operations
- SHA-256 hash algorithm
- Cryptographically secure random generation

**Key Methods**:
- `encrypt_text()`: Hybrid encryption
- `decrypt_text()`: Hybrid decryption
- `ensure_key_pair()`: Key management

### 5. InputOutputManager
**Purpose**: Input and output operations management

**Responsibilities**:
- Stdin/stdout handling
- Clipboard operations
- Encoding management (UTF-8)
- Cross-platform compatibility
- Error handling for I/O operations

**Key Methods**:
- `get_input_text()`: Read from stdin or clipboard
- `set_output_text()`: Write to clipboard

### 6. TransformationRule (Dataclass)
**Purpose**: Type-safe rule definition structure

**Properties**:
- `name`: Human-readable rule name
- `description`: Rule description
- `example`: Usage example
- `function`: Transformation function reference
- `requires_args`: Whether rule needs arguments
- `default_args`: Default argument values

## Configuration System

### Transformation Rules Configuration
Location: `config/transformation_rules.json`

Structure:
```json
{
  "category_name": {
    "rule_key": {
      "name": "Human-readable name",
      "description": "Rule description",
      "example": "input → output"
    }
  }
}
```

### Security Configuration
Location: `config/security_config.json`

Structure:
```json
{
  "rsa_encryption": {
    "key_size": 4096,
    "public_exponent": 65537,
    "hash_algorithm": "SHA256",
    "mgf_algorithm": "MGF1",
    "aes_key_size": 32,
    "aes_iv_size": 16,
    "aes_mode": "CBC"
  }
}
```

## Security Architecture

### Encryption Flow
1. **Text Input**: UTF-8 encoded plaintext
2. **AES Key Generation**: 256-bit cryptographically secure random key
3. **IV Generation**: 128-bit cryptographically secure random IV
4. **AES Encryption**: Plaintext encrypted with AES-256-CBC
5. **RSA Key Encryption**: AES key encrypted with RSA-4096-OAEP
6. **Data Combination**: [key_length][encrypted_key][iv][encrypted_data]
7. **Base64 Encoding**: Final output as base64 string

### Key Management
- **Generation**: RSA-4096 keys generated on first use
- **Storage**: PEM format in `rsa/` directory
- **Permissions**: Private key (0o600), Public key (0o644)
- **Exclusion**: Keys automatically excluded from version control

## Error Handling Strategy

### Hierarchical Error Handling
1. **Component Level**: Each manager handles its own errors
2. **Application Level**: ApplicationInterface handles user-facing errors
3. **Graceful Degradation**: Fallback options when possible
4. **User Feedback**: Clear, actionable error messages

### Error Categories
- **Configuration Errors**: Missing or invalid config files
- **Cryptography Errors**: Key generation, encryption/decryption failures
- **I/O Errors**: Clipboard, stdin/stdout issues
- **Rule Errors**: Invalid rule syntax or execution failures

## Extensibility

### Adding New Rule Categories
1. Add category to `config/transformation_rules.json`
2. Implement methods in `TextTransformationEngine`
3. Register methods in `_initialize_rules()`
4. Update help system display

### Adding New Security Algorithms
1. Update `config/security_config.json`
2. Modify `CryptographyManager` implementation
3. Ensure backward compatibility
4. Update documentation

### Adding New I/O Sources
1. Extend `InputOutputManager` with new methods
2. Update `ApplicationInterface` to use new sources
3. Add configuration options if needed
4. Test cross-platform compatibility

## Performance Considerations

### Configuration Caching
- JSON files loaded once and cached
- Lazy loading prevents unnecessary file reads
- Configuration validation on first access

### Cryptographic Operations
- Key pair reused across operations
- Efficient hybrid encryption for large texts
- Secure random generation optimized

### Memory Management
- Minimal memory footprint
- Efficient string operations
- Proper cleanup of sensitive data

## Testing Strategy

### Unit Testing
- Each component tested independently
- Mock dependencies for isolation
- Configuration-driven test cases

### Integration Testing
- End-to-end transformation workflows
- Cross-platform compatibility testing
- Error condition testing

### Security Testing
- Cryptographic operation validation
- Key generation testing
- Padding and encoding validation

## Deployment Considerations

### Dependencies
- Minimal external dependencies
- Version pinning for security
- Optional dependency handling

### Configuration Management
- Default configurations included
- Environment-specific overrides
- Validation and error reporting

### Security Hardening
- Secure file permissions
- Key storage best practices
- Input validation and sanitization

## Current Implementation Status

### Implemented Features
- Modular enterprise architecture with dependency injection
- Comprehensive text transformation engine
- RSA-4096 + AES-256 hybrid encryption
- Interactive, daemon, and hotkey operation modes
- JSON-based configuration system
- Type-safe implementation with full annotations
- Comprehensive test suite
- Modern CLI interface with Typer and Rich

## Future Enhancements

### Planned Features
- Plugin system for custom rules
- Web API interface
- Batch processing capabilities
- Configuration validation schema

### Security Improvements
- Hardware security module support
- Key rotation mechanisms
- Audit logging
- Multi-factor authentication for key access

### Performance Optimizations
- Parallel processing for batch operations
- Caching for frequently used transformations
- Memory optimization for large texts