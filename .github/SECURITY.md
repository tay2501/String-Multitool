# Security Policy

## Supported Versions

We actively support the following versions of String Multitool with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   |  Fully supported |
| 0.x.x   | L Not supported   |

## Security Features

String Multitool implements several security measures:

### Cryptographic Security
- **RSA-4096**: Industry-standard RSA encryption with 4096-bit keys
- **AES-256-CBC**: Advanced Encryption Standard with 256-bit keys
- **Hybrid Encryption**: Combines RSA + AES for optimal security and performance
- **Secure Key Generation**: Cryptographically secure random key generation
- **Proper Key Storage**: Private keys stored with restricted permissions (0o600)

### Input Security
- **Input Validation**: All user inputs are validated and sanitized
- **Buffer Protection**: Protection against buffer overflow attacks
- **Safe File Handling**: Secure file operations with proper error handling

### Configuration Security
- **Secure Defaults**: All security configurations use safe default values
- **JSON Validation**: Configuration files are validated against schemas
- **Sensitive Data Protection**: No sensitive data logged or exposed

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly:

### For Critical Vulnerabilities
**DO NOT** create a public GitHub issue. Instead:

1. **Email**: Send details to `[your-security-email@example.com]` (replace with actual email)
2. **Subject**: `[SECURITY] String Multitool Vulnerability Report`
3. **Encryption**: Use our PGP key if possible (see below)

### For Non-Critical Issues
You can create a private security advisory through GitHub:
1. Go to the Security tab in the repository
2. Click "Report a vulnerability" 
3. Fill out the advisory form

### What to Include
Please provide:
- **Description**: Clear description of the vulnerability
- **Impact**: Potential security impact and attack scenarios  
- **Reproduction**: Steps to reproduce (if safe to share)
- **Affected Versions**: Which versions are affected
- **Suggested Fix**: If you have ideas for mitigation

### Response Timeline
- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Timeline**: Varies by severity
  - Critical: 1-7 days
  - High: 1-4 weeks  
  - Medium: 1-8 weeks
  - Low: Next regular release

## Security Best Practices for Users

### Key Management
- **Protect Private Keys**: Never share your RSA private keys
- **Backup Safely**: Store key backups in secure locations
- **Key Rotation**: Consider rotating keys periodically

### Configuration
- **Review Settings**: Regularly review your security configurations
- **Update Dependencies**: Keep Python and dependencies updated
- **Monitor Logs**: Check logs for suspicious activity

### Usage Guidelines
- **Trusted Sources**: Only process data from trusted sources
- **Validate Outputs**: Verify encrypted/decrypted content integrity
- **Secure Environment**: Use String Multitool in secure environments

## Security Contacts

- **Security Team**: `[your-security-email@example.com]` (replace with actual email)
- **Maintainer**: [@tay2501](https://github.com/tay2501)

## PGP Key (Optional)
```
-----BEGIN PGP PUBLIC KEY BLOCK-----
[Your PGP public key if you want to provide one]
-----END PGP PUBLIC KEY BLOCK-----
```

## Security Updates

Security updates are released as:
- **Patch Releases**: For backward-compatible fixes
- **Security Advisories**: Published through GitHub Security Advisories
- **Release Notes**: Security fixes documented in release notes

Subscribe to releases and security advisories to stay informed.

## Scope

This security policy covers:
- String Multitool core application
- Configuration files and dependencies
- Build and distribution processes
- Documentation and examples

**Out of Scope**:
- Third-party integrations not officially supported
- User-modified code or configurations
- Issues in underlying OS or Python interpreter

## Acknowledgments

We appreciate security researchers and users who report vulnerabilities responsibly. Contributors will be acknowledged in:
- Security advisories (with permission)
- Release notes
- This security policy

---

**Last Updated**: August 2024
**Next Review**: February 2025