#!/usr/bin/env python3
"""
Setup script for String_Multitool.
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read the contents of README file using pathlib
this_directory = Path(__file__).parent.resolve()
readme_path = this_directory / "README.md"
with open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

# Read requirements using pathlib
requirements_path = this_directory / "requirements.txt"
with open(requirements_path, encoding="utf-8") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

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
        "Bug Reports": "https://github.com/tay2501/String-Multitool/issues",
        "Source": "https://github.com/tay2501/String-Multitool",
        "Documentation": "https://github.com/tay2501/String-Multitool#readme",
    },
)
