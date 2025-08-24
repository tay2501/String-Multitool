#!/usr/bin/env python3
"""Database migration script to add tsv_file_name column to conversion_rules table.

Educational example of enterprise-grade database migration:
- Safe column addition with proper constraints
- Data migration for existing records
- Rollback capability for error recovery
- Comprehensive validation and logging
"""

import sys
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any


def validate_database_connection(db_path: Path) -> bool:
    """Validate database exists and is accessible.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        True if database is valid and accessible
    """
    try:
        if not db_path.exists():
            print(f"Error: Database file not found: {db_path}")
            return False
        
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            
            # Verify required tables exist
            tables = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            
            table_names = {table[0] for table in tables}
            required_tables = {'conversion_rules', 'rule_sets'}
            
            if not required_tables.issubset(table_names):
                missing = required_tables - table_names
                print(f"Error: Required tables missing: {missing}")
                return False
            
            print(f"SUCCESS: Database validation successful: {len(table_names)} tables found")
            return True
            
    except sqlite3.Error as e:
        print(f"Error: Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"Error: Unexpected validation error: {e}")
        return False


def check_column_exists(cursor: sqlite3.Cursor) -> bool:
    """Check if tsv_file_name column already exists.
    
    Args:
        cursor: SQLite database cursor
        
    Returns:
        True if column already exists
    """
    try:
        column_info = cursor.execute("PRAGMA table_info(conversion_rules)").fetchall()
        column_names = {col[1] for col in column_info}
        
        exists = 'tsv_file_name' in column_names
        if exists:
            print("SUCCESS: Column 'tsv_file_name' already exists - migration not needed")
        else:
            print("INFO: Column 'tsv_file_name' not found - proceeding with migration")
        
        return exists
        
    except sqlite3.Error as e:
        print(f"Error: Failed to check column existence: {e}")
        raise


def backup_table_data(cursor: sqlite3.Cursor) -> list[tuple]:
    """Create backup of conversion_rules data before migration.
    
    Args:
        cursor: SQLite database cursor
        
    Returns:
        List of all conversion_rules records
    """
    try:
        print("INFO: Creating backup of existing conversion_rules data...")
        
        backup_data = cursor.execute("""
            SELECT id, rule_set_id, source_text, target_text, 
                   usage_count, created_at, updated_at
            FROM conversion_rules
            ORDER BY id
        """).fetchall()
        
        print(f"SUCCESS: Backed up {len(backup_data)} existing records")
        return backup_data
        
    except sqlite3.Error as e:
        print(f"Error: Failed to backup table data: {e}")
        raise


def add_tsv_file_name_column(cursor: sqlite3.Cursor) -> None:
    """Add tsv_file_name column to conversion_rules table.
    
    Args:
        cursor: SQLite database cursor
    """
    try:
        print("INFO: Adding tsv_file_name column to conversion_rules table...")
        
        # Add column with NOT NULL constraint and default value
        cursor.execute("""
            ALTER TABLE conversion_rules 
            ADD COLUMN tsv_file_name VARCHAR(255) NOT NULL DEFAULT 'unknown.tsv'
        """)
        
        print("SUCCESS: Successfully added tsv_file_name column")
        
    except sqlite3.Error as e:
        print(f"Error: Failed to add column: {e}")
        raise


def populate_tsv_file_names(cursor: sqlite3.Cursor) -> None:
    """Populate tsv_file_name for existing records based on rule_set data.
    
    Args:
        cursor: SQLite database cursor
    """
    try:
        print("INFO: Populating tsv_file_name for existing records...")
        
        # Update tsv_file_name based on rule_set file_path
        cursor.execute("""
            UPDATE conversion_rules 
            SET tsv_file_name = (
                SELECT CASE 
                    WHEN rs.file_path LIKE '%.tsv' THEN 
                        substr(rs.file_path, 
                              instr(rs.file_path, '\') + 1,
                              length(rs.file_path) - instr(rs.file_path, '\'))
                    WHEN rs.file_path LIKE '%/' || rs.name || '.tsv' THEN 
                        rs.name || '.tsv'
                    ELSE 
                        rs.name || '.tsv'
                END
                FROM rule_sets rs 
                WHERE rs.id = conversion_rules.rule_set_id
            )
            WHERE tsv_file_name = 'unknown.tsv'
        """)
        
        updated_count = cursor.rowcount
        print(f"SUCCESS: Updated {updated_count} records with proper tsv_file_name")
        
        # Verify update results
        cursor.execute("""
            SELECT tsv_file_name, COUNT(*) 
            FROM conversion_rules 
            GROUP BY tsv_file_name
            ORDER BY tsv_file_name
        """)
        
        results = cursor.fetchall()
        print("Updated tsv_file_name distribution:")
        for filename, count in results:
            print(f"  {filename}: {count} records")
            
    except sqlite3.Error as e:
        print(f"Error: Failed to populate tsv_file_name: {e}")
        raise


def validate_migration_success(cursor: sqlite3.Cursor) -> bool:
    """Validate migration was successful.
    
    Args:
        cursor: SQLite database cursor
        
    Returns:
        True if migration validation passes
    """
    try:
        print("INFO: Validating migration success...")
        
        # Check column was added
        column_info = cursor.execute("PRAGMA table_info(conversion_rules)").fetchall()
        column_names = {col[1] for col in column_info}
        
        if 'tsv_file_name' not in column_names:
            print("Error: tsv_file_name column not found after migration")
            return False
        
        # Check no records have default/unknown values
        unknown_count = cursor.execute("""
            SELECT COUNT(*) FROM conversion_rules 
            WHERE tsv_file_name = 'unknown.tsv'
        """).fetchone()[0]
        
        if unknown_count > 0:
            print(f"Warning: {unknown_count} records still have unknown tsv_file_name")
        
        # Check all records have valid tsv_file_name
        total_count = cursor.execute("SELECT COUNT(*) FROM conversion_rules").fetchone()[0]
        valid_count = cursor.execute("""
            SELECT COUNT(*) FROM conversion_rules 
            WHERE tsv_file_name IS NOT NULL AND tsv_file_name != ''
        """).fetchone()[0]
        
        if total_count != valid_count:
            print(f"Error: {total_count - valid_count} records have invalid tsv_file_name")
            return False
        
        print(f"SUCCESS: Migration validation successful: {valid_count} records with valid tsv_file_name")
        return True
        
    except sqlite3.Error as e:
        print(f"Error: Migration validation failed: {e}")
        return False


def run_migration(db_path: Path, dry_run: bool = False) -> bool:
    """Execute the complete migration process.
    
    Args:
        db_path: Path to SQLite database file
        dry_run: If True, perform read-only validation without changes
        
    Returns:
        True if migration completed successfully
    """
    print("=" * 80)
    print("Database Migration: Add tsv_file_name to conversion_rules")
    print("=" * 80)
    print(f"Target database: {db_path}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
    print()
    
    if not validate_database_connection(db_path):
        return False
    
    try:
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            
            # Check if migration is needed
            if check_column_exists(cursor):
                print("Migration already completed - no action needed")
                return True
            
            if dry_run:
                print("DRY RUN: Would add tsv_file_name column and populate data")
                return True
            
            # Backup existing data
            backup_data = backup_table_data(cursor)
            
            # Perform migration steps
            add_tsv_file_name_column(cursor)
            populate_tsv_file_names(cursor)
            
            # Validate results
            if not validate_migration_success(cursor):
                print("Error: Migration validation failed - rolling back...")
                conn.rollback()
                return False
            
            # Commit changes
            conn.commit()
            print("SUCCESS: Migration completed successfully and committed to database")
            
            return True
            
    except Exception as e:
        print(f"Error: Migration failed: {e}")
        return False


def main() -> int:
    """Main migration entry point with command-line argument support."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Add tsv_file_name column to conversion_rules table"
    )
    parser.add_argument(
        "--database", 
        type=Path, 
        default="data/tsv_converter.db",
        help="Path to SQLite database file (default: data/tsv_converter.db)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Perform validation only without making changes"
    )
    
    args = parser.parse_args()
    
    # Convert to absolute path
    db_path = Path(__file__).parent / args.database
    
    success = run_migration(db_path, dry_run=args.dry_run)
    
    print()
    print("=" * 80)
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed - database unchanged")
    print("=" * 80)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())