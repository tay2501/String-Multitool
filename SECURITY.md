# Security Policy

## Supported Versions

We actively support the following versions of String Multitool with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.6.x   | :white_check_mark: |
| 2.5.x   | :white_check_mark: |
| < 2.5   | :x:                |

## Reporting a Security Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in String Multitool, please help us by reporting it responsibly.

### For Security Vulnerabilities

**Please DO NOT create a public GitHub issue for security vulnerabilities.**

Instead, please use one of these methods:

1. **GitHub Security Advisories** (Recommended)
   - Go to the [Security tab](https://github.com/[your-username]/String-Multitool/security/advisories) of this repository
   - Click "Report a vulnerability"
   - Fill out the private vulnerability report

2. **Email** (Alternative)
   - Email: [your-security-email@example.com]
   - Subject: "[SECURITY] String Multitool Vulnerability Report"
   - Include: Detailed description, steps to reproduce, potential impact

### What to Include

When reporting a vulnerability, please provide:

- **Description**: Clear description of the vulnerability
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Impact**: Potential impact and attack scenarios
- **Affected Versions**: Which versions are affected
- **Suggested Fix**: If you have ideas for a fix (optional)

### Response Timeline

- **Initial Response**: We aim to respond within 48 hours
- **Assessment**: We will assess the vulnerability within 5 business days
- **Fix Development**: Timeline depends on severity and complexity
- **Disclosure**: Coordinated disclosure after fix is available

## Security Considerations

String Multitool handles sensitive data and includes cryptographic features. Please be aware of these security considerations:

### Cryptographic Features

- **RSA Encryption**: Uses RSA-4096 with OAEP padding
- **AES Encryption**: Uses AES-256 in CBC mode with PKCS7 padding
- **Key Storage**: Private keys stored with 0o600 permissions (Unix) or NTFS permissions (Windows)
- **Key Generation**: Uses cryptographically secure random number generation

### Input Handling

- **Clipboard Data**: Clipboard contents are processed and may contain sensitive information
- **File Operations**: TSV files and configuration files are read from disk
- **Command Line**: Arguments may be logged or visible in process lists

### Best Practices for Users

1. **Keep Updated**: Always use the latest supported version
2. **Secure Environment**: Run in a secure environment for sensitive data
3. **Key Management**: Protect RSA private keys appropriately
4. **Review Configuration**: Regularly review configuration files
5. **Monitor Usage**: Be aware of what data is being processed

### Security Features

- **Input Validation**: All user inputs are validated
- **Error Handling**: Errors don't expose sensitive information
- **Secure Defaults**: Default configuration emphasizes security
- **Dependency Management**: Dependencies are regularly updated and scanned

## Known Security Considerations

### Clipboard Access

String Multitool requires clipboard access to function. This means:
- The application can read clipboard contents
- Transformed text is automatically copied to clipboard
- Consider data sensitivity when using clipboard features

### File System Access

The application requires file system access for:
- Configuration files in `config/` directory
- RSA key storage in `rsa/` directory
- TSV files for conversion rules
- Log files for debugging

### Network Access

String Multitool does not make network connections. All processing is local.

## Reporting Non-Security Issues

For non-security bugs and issues, please use the normal [GitHub Issues](https://github.com/[your-username]/String-Multitool/issues) process.

## Security Updates

Security updates are distributed through:
- GitHub Releases with security notes
- Changelog documentation
- Security advisories (for critical issues)

## Dependencies

We regularly monitor and update dependencies for security vulnerabilities:
- Automated dependency scanning via Dependabot
- Security advisories monitoring
- Regular dependency updates

## Acknowledgments

We appreciate security researchers and users who report vulnerabilities responsibly. We will acknowledge your contribution (with your permission) in our security advisories and release notes.

---

**Last Updated**: December 2024
**Version**: 1.0