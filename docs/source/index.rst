.. String-Multitool documentation master file, created by
   sphinx-quickstart on 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

String-Multitool Documentation
==============================

**String-Multitool** is an advanced text transformation tool with enterprise-grade architecture,
featuring POSIX-compliant CLI, case-insensitive TSV conversion, and comprehensive security features.

.. image:: https://img.shields.io/badge/Python-3.12%2B-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT License

.. image:: https://img.shields.io/badge/Code%20Style-Black-black.svg
   :target: https://github.com/psf/black
   :alt: Code Style: Black

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/tay2501/String-Multitool.git
   cd String-Multitool
   
   # Install with uv (recommended)
   uv sync --all-extras
   
   # Or install with pip
   pip install -e .

Basic Usage
~~~~~~~~~~~

.. code-block:: bash

   # Interactive mode
   python String_Multitool.py
   
   # Apply transformations directly
   python String_Multitool.py /t/l  # trim + lowercase
   
   # TSV conversion
   python String_Multitool.py /tsvtr technical_terms.tsv
   
   # Daemon mode
   python String_Multitool.py --daemon

Key Features
------------

🔧 **Advanced Text Transformations**
   - Case conversions (lower, upper, title, camel, pascal, snake)
   - Text formatting and trimming
   - Unicode width conversions (full ⇔ half width)
   - SQL IN clause generation

🔐 **Enterprise-Grade Security**
   - RSA-4096 + AES-256 hybrid encryption
   - Secure key management with proper permissions
   - Cryptographic hash functions (SHA-256, SHA-1, MD5)

📊 **TSV Database Integration**
   - Case-insensitive text conversion using SQLite
   - Rule set management and synchronization
   - Interactive database shell with syntax highlighting

⚡ **High Performance**
   - MVC architecture with loose coupling
   - Type-safe implementation with comprehensive annotations
   - EAFP (Easier to Ask for Forgiveness than Permission) error handling

🛠️ **Developer-Friendly**
   - Comprehensive test suite with pytest
   - Modern Python packaging with uv
   - Extensive documentation with Sphinx

Architecture Overview
---------------------

String-Multitool follows a modern **MVC (Model-View-Controller)** architecture:

.. code-block:: text

   string_multitool/
   ├── models/          # Business Logic Layer
   │   ├── transformations.py    # Text transformation engine
   │   ├── config.py            # Configuration management
   │   ├── crypto.py            # Cryptography operations
   │   └── interactive.py       # Interactive session management
   ├── io/              # View/Controller Layer
   │   ├── manager.py           # I/O operations and clipboard
   │   └── clipboard.py         # Clipboard monitoring
   ├── main.py          # Entry Point (Application flow)
   └── __init__.py      # Package initialization

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   user_guide
   api_reference
   developer_guide
   contributing
   changelog

