#!/usr/bin/env python3
"""
Setup script for String_Multitool.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="string-multitool",
    version="2.2.0",
    author="String_Multitool Development Team",
    author_email="",
    description="Advanced text transformation tool with modular architecture and RSA encryption",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/String-Multitool",
    py_modules=["String_Multitool"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Text Processing",
        "Topic :: Utilities",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "string-multitool=String_Multitool:main",
        ],
    },
    keywords="text transformation clipboard encryption rsa unicode",
    project_urls={
        "Bug Reports": "https://github.com/your-username/String-Multitool/issues",
        "Source": "https://github.com/your-username/String-Multitool",
        "Documentation": "https://github.com/your-username/String-Multitool#readme",
    },
)