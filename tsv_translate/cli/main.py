"""Main CLI implementation with argparse.

Educational example of clean command-line interface design
with proper argument parsing, help text, and error handling.
"""

import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import pyperclip

from ..core.engine import TSVTranslateEngine
from ..core.exceptions import TSVTranslateError


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser with comprehensive help and subcommands.
    
    Demonstrates argparse best practices with clear help text,
    proper argument groups, and intuitive command structure.
    """
    parser = argparse.ArgumentParser(
        prog="tsvtr",
        description="Convert clipboard text using TSV-defined rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tsvtr japanese_to_english    # Convert using specific rule set
  tsvtr ls                     # List available rule sets
  tsvtr rm old_rules           # Remove rule set from database
  tsvtr sync ~/rules           # Sync directory with database
  tsvtr info japanese_rules    # Show rule set information
  tsvtr --shell litecli        # Launch interactive SQLite shell with syntax highlighting
  tsvtr --shell sqlite3        # Launch standard SQLite command-line interface
        """
    )
    
    # Global options
    parser.add_argument(
        "--config",
        type=Path,
        default="config/tsv_translate.json",
        help="Configuration file path (default: config/tsv_translate.json)"
    )
    
    parser.add_argument(
        "--database",
        help="Database URL override"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    parser.add_argument(
        "--shell",
        choices=["litecli", "sqlite3"],
        help="Launch interactive SQLite shell for database access"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND"
    )
    
    # Convert command (default behavior)
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert clipboard text using rule set"
    )
    convert_parser.add_argument(
        "rule_set",
        help="Name of the rule set to use for conversion"
    )
    
    # List command
    subparsers.add_parser(
        "ls",
        aliases=["list"],
        help="List available rule sets"
    )
    
    # Remove command
    rm_parser = subparsers.add_parser(
        "rm",
        aliases=["remove"],
        help="Remove rule set from database"
    )
    rm_parser.add_argument(
        "rule_set",
        help="Name of the rule set to remove"
    )
    
    # Sync command
    sync_parser = subparsers.add_parser(
        "sync",
        help="Synchronize TSV files with database"
    )
    sync_parser.add_argument(
        "directory",
        type=Path,
        nargs="?",
        default="config/tsv_rules",
        help="Directory containing TSV files (default: config/tsv_rules)"
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Show detailed information about a rule set"
    )
    info_parser.add_argument(
        "rule_set",
        help="Name of the rule set to inspect"
    )
    
    # Health check command
    subparsers.add_parser(
        "health",
        help="Check system health status"
    )
    
    return parser


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration with sensible defaults.
    
    Demonstrates configuration loading with proper error handling
    and default value management.
    """
    default_config = {
        "database_url": "sqlite:///tsv_translate.db",
        "tsv_directory": "config/tsv_rules",
        "enable_file_watching": False,  # Disabled in CLI mode
        "debug": False
    }
    
    if not config_path.exists():
        return default_config
    
    try:
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Merge with defaults
        default_config.update(config)
        return default_config
        
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Failed to load config {config_path}: {e}")
        return default_config


def handle_convert_command(engine: TSVTranslateEngine, rule_set: str) -> int:
    """Handle text conversion command."""
    try:
        # Get text from clipboard
        text = pyperclip.paste()
        if not text.strip():
            print("Error: Clipboard is empty")
            return 1
        
        # Convert text
        result = engine.convert_text(text, rule_set)
        
        if result.is_successful:
            # Copy result back to clipboard
            pyperclip.copy(result.converted_text)
            
            if result.rules_applied > 0:
                print(f"✓ Converted using '{rule_set}' ({result.rules_applied} rules applied)")
            else:
                print(f"→ No changes (rule set '{rule_set}' processed)")
        else:
            print(f"Error: {result.error_message}")
            return 1
            
    except Exception as e:
        print(f"Error during conversion: {e}")
        return 1
    
    return 0


def handle_list_command(engine: TSVTranslateEngine) -> int:
    """Handle list rule sets command."""
    try:
        rule_sets = engine.list_rule_sets()
        
        if not rule_sets:
            print("No rule sets found. Add TSV files to sync directory.")
            return 0
        
        print("Available rule sets:")
        for rule_set in rule_sets:
            info = engine.get_rule_set_info(rule_set)
            rule_count = info["rule_count"] if info else "?"
            print(f"  {rule_set} ({rule_count} rules)")
            
    except Exception as e:
        print(f"Error listing rule sets: {e}")
        return 1
    
    return 0


def handle_remove_command(engine: TSVTranslateEngine, rule_set: str) -> int:
    """Handle remove rule set command."""
    try:
        result = engine.remove_rule_set(rule_set)
        
        if result.is_successful:
            print(f"✓ Removed rule set '{rule_set}' ({result.rules_deleted} rules)")
        else:
            print(f"Error: {result.error_message}")
            return 1
            
    except Exception as e:
        print(f"Error removing rule set: {e}")
        return 1
    
    return 0


def handle_sync_command(engine: TSVTranslateEngine, directory: Path) -> int:
    """Handle directory synchronization command."""
    try:
        results = engine.sync_directory(directory)
        
        success_count = sum(1 for r in results if r.is_successful)
        error_count = len(results) - success_count
        
        print(f"Synchronization complete: {success_count} successful, {error_count} errors")
        
        for result in results:
            if result.is_successful:
                print(f"  ✓ {result.rule_set_name}: {result.operation} ({result.rules_processed} rules)")
            else:
                print(f"  ✗ {result.rule_set_name}: {result.error_message}")
        
        return 0 if error_count == 0 else 1
        
    except Exception as e:
        print(f"Error during synchronization: {e}")
        return 1


def handle_info_command(engine: TSVTranslateEngine, rule_set: str) -> int:
    """Handle rule set information command."""
    try:
        info = engine.get_rule_set_info(rule_set)
        
        if not info:
            print(f"Rule set '{rule_set}' not found")
            return 1
        
        print(f"Rule Set: {info['name']}")
        print(f"  File: {info['file_path']}")
        print(f"  Rules: {info['rule_count']}")
        print(f"  Total Usage: {info['total_usage']}")
        print(f"  Created: {info['created_at']}")
        print(f"  Updated: {info['updated_at']}")
        
        if info.get('description'):
            print(f"  Description: {info['description']}")
            
    except Exception as e:
        print(f"Error getting rule set info: {e}")
        return 1
    
    return 0


def handle_health_command(engine: TSVTranslateEngine) -> int:
    """Handle system health check command."""
    try:
        health = engine.health_check()
        
        print("System Health Status:")
        all_healthy = True
        
        for component, status in health.items():
            status_icon = "✓" if status else "✗"
            print(f"  {status_icon} {component}")
            if not status:
                all_healthy = False
        
        return 0 if all_healthy else 1
        
    except Exception as e:
        print(f"Error during health check: {e}")
        return 1


def handle_shell_command(config: Dict[str, Any], shell_type: str) -> int:
    """Handle interactive shell command with security best practices.
    
    Args:
        config: Configuration dictionary containing database_url
        shell_type: Type of shell to launch ('litecli' or 'sqlite3')
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
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


def main() -> int:
    """Main CLI entry point with comprehensive error handling.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    
    # Special handling for direct rule set usage (backwards compatibility)
    if len(sys.argv) == 2 and sys.argv[1] not in ['ls', 'list', 'health', '--help', '-h']:
        # Check if it's a direct conversion command
        if not sys.argv[1].startswith('-'):
            sys.argv.insert(1, 'convert')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.database:
        config["database_url"] = args.database
    if args.debug:
        config["debug"] = True
    
    # Handle shell option before initializing engine
    if args.shell:
        return handle_shell_command(config, args.shell)
    
    # Initialize engine
    try:
        with TSVTranslateEngine(config) as engine:
            # Route commands
            if args.command == "convert" or (hasattr(args, 'rule_set') and not args.command):
                return handle_convert_command(engine, args.rule_set)
            elif args.command in ["ls", "list"]:
                return handle_list_command(engine)
            elif args.command in ["rm", "remove"]:
                return handle_remove_command(engine, args.rule_set)
            elif args.command == "sync":
                return handle_sync_command(engine, args.directory)
            elif args.command == "info":
                return handle_info_command(engine, args.rule_set)
            elif args.command == "health":
                return handle_health_command(engine)
            else:
                parser.print_help()
                return 1
                
    except TSVTranslateError as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        if config.get("debug"):
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())