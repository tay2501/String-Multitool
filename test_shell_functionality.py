#!/usr/bin/env python3
"""Test script for --shell litecli functionality."""

import subprocess
import sqlite3
from pathlib import Path
from urllib.parse import urlparse


def handle_shell_command(config: dict, shell_type: str) -> int:
    """Handle interactive shell command with security best practices."""
    try:
        # Extract database path from URL
        database_url = config.get("database_url", "sqlite:///tsv_translate.db")
        
        # Parse SQLite URL
        if database_url.startswith("sqlite:///"):
            db_path = database_url[10:]  # Remove 'sqlite:///' prefix
        else:
            parsed = urlparse(database_url)
            if parsed.scheme == "sqlite":
                db_path = parsed.path.lstrip("/")
            else:
                print(f"Error: Unsupported database URL: {database_url}")
                return 1
        
        # Ensure database file exists or can be created
        db_path_obj = Path(db_path)
        if not db_path_obj.exists():
            # Create parent directories if needed
            db_path_obj.parent.mkdir(parents=True, exist_ok=True)
            print(f"Note: Database will be created at: {db_path}")
        
        # Launch appropriate shell using subprocess with security best practices
        if shell_type == "litecli":
            try:
                # Check if litecli is available
                subprocess.run(["litecli", "--version"], 
                             capture_output=True, check=True)
                print(f"Launching litecli for database: {db_path}")
                result = subprocess.run(["litecli", db_path], check=False)
                return result.returncode
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Error: litecli not found. Please install with: pip install litecli")
                return 1
                
        elif shell_type == "sqlite3":
            try:
                # Check if sqlite3 is available
                subprocess.run(["sqlite3", "--version"], 
                             capture_output=True, check=True)
                print(f"Launching sqlite3 for database: {db_path}")
                result = subprocess.run(["sqlite3", db_path], check=False)
                return result.returncode
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Error: sqlite3 not found. Please ensure SQLite is installed.")
                return 1
        
        else:
            print(f"Error: Unknown shell type: {shell_type}")
            return 1
            
    except Exception as e:
        print(f"Error launching shell: {e}")
        return 1


def test_shell_functionality():
    """Test the shell functionality."""
    print("Testing --shell litecli functionality")
    print("=" * 50)
    
    # Create test database
    test_db = "test_demo.db"
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Create sample TSV conversion table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversion_rules (
            id INTEGER PRIMARY KEY,
            source_text TEXT,
            target_text TEXT,
            rule_set_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample data
    sample_data = [
        ("API", "Application Programming Interface", "technical_terms"),
        ("DB", "Database", "technical_terms"),
        ("UI", "User Interface", "technical_terms"),
        ("SQL", "Structured Query Language", "technical_terms"),
    ]
    
    cursor.executemany(
        "INSERT INTO conversion_rules (source_text, target_text, rule_set_name) VALUES (?, ?, ?)",
        sample_data
    )
    
    conn.commit()
    conn.close()
    
    print(f"Created test database: {test_db}")
    print("Sample conversion rules added")
    print("\nTesting shell command...")
    
    # Test configuration
    config = {"database_url": f"sqlite:///{test_db}"}
    
    # Test with litecli
    print("\n1. Testing with litecli:")
    try:
        result = handle_shell_command(config, "litecli")
        print(f"litecli test result: {result}")
    except KeyboardInterrupt:
        print("Shell session interrupted by user")
        
    # Test with sqlite3 (will likely fail on Windows)
    print("\n2. Testing with sqlite3:")
    try:
        result = handle_shell_command(config, "sqlite3")
        print(f"sqlite3 test result: {result}")
    except KeyboardInterrupt:
        print("Shell session interrupted by user")
    
    print("\nTest completed!")


if __name__ == "__main__":
    test_shell_functionality()