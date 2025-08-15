"""
Modern CLI interface for String_Multitool using Typer.

This module provides a type-safe, modern command-line interface with
comprehensive help system, auto-completion support, and intuitive subcommands.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Any, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typer import Typer

from .core.types import TextSource
from .exceptions import StringMultitoolError
from .main import ApplicationInterface

# Import logging utilities
from .utils.logger import get_logger, log_debug, log_error, log_info, log_warning

# Rich console for beautiful output
console: Console = Console()

# Type alias for command decorator
CommandDecorator = Any

# Main Typer application
app: Typer = typer.Typer(
    name="string-multitool",
    help="Advanced text transformation tool with pipe support and RSA encryption",
    epilog="Examples:\n  string-multitool transform '/t/l'           # Trim and lowercase\n  string-multitool encrypt                     # Encrypt clipboard\n  echo 'text' | string-multitool transform '/u' # Uppercase piped text",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Create application instance (will be initialized when needed)
_app_instance: ApplicationInterface | None = None


def get_app() -> ApplicationInterface:
    """Get or create application instance."""
    global _app_instance
    if _app_instance is None:
        _app_instance = ApplicationInterface()
    return _app_instance


@app.command("interactive", help="Start interactive mode for real-time text transformation")  # type: ignore
def interactive_mode() -> None:
    """Start interactive mode with clipboard monitoring and real-time transformation."""
    try:
        app_instance = get_app()
        input_text = app_instance.io_manager.get_input_text()
        app_instance.run_interactive_mode(input_text)
    except StringMultitoolError as e:
        logger = get_logger(__name__)
        log_error(logger, f"Error: {e}")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        logger = get_logger(__name__)
        log_info(logger, "\nGoodbye!")
        raise typer.Exit(0)


@app.command("transform", help="Apply transformation rules to text")  # type: ignore
def transform_text(
    rules: Annotated[
        str,
        typer.Argument(help="Transformation rules (e.g., '/t/l' for trim + lowercase)"),
    ],
    text: Annotated[
        Optional[str],
        typer.Option(
            "--text", "-t", help="Input text (if not provided, uses clipboard or pipe)"
        ),
    ] = None,
    output: Annotated[
        bool, typer.Option("--output", "-o", help="Copy result to clipboard")
    ] = True,
) -> None:
    """Apply transformation rules to input text.

    Args:
        rules: Transformation rules string (e.g., '/t/l/u')
        text: Optional input text (uses clipboard/pipe if not provided)
        output: Whether to copy result to clipboard
    """
    try:
        app_instance = get_app()

        # Get input text
        if text is None:
            input_text = app_instance.io_manager.get_input_text()
        else:
            input_text = text

        # Apply transformations
        result = app_instance.transformation_engine.apply_transformations(
            input_text, rules
        )

        # Output result
        if output:
            app_instance.io_manager.set_output_text(result)

        console.print(f"[green]Transformation applied:[/green] {rules}")
        console.print(f"[cyan]Result:[/cyan] '{result}'")

    except StringMultitoolError as e:
        logger = get_logger(__name__)
        log_error(logger, f"Error: {e}")
        raise typer.Exit(1)


@app.command("encrypt", help="Encrypt text using RSA+AES hybrid encryption")  # type: ignore
def encrypt_text(
    text: Annotated[
        Optional[str],
        typer.Option(
            "--text", "-t", help="Text to encrypt (if not provided, uses clipboard)"
        ),
    ] = None,
    output: Annotated[
        bool, typer.Option("--output", "-o", help="Copy result to clipboard")
    ] = True,
) -> None:
    """Encrypt text using hybrid RSA+AES encryption.

    Args:
        text: Optional text to encrypt (uses clipboard if not provided)
        output: Whether to copy result to clipboard
    """
    try:
        app_instance = get_app()

        if app_instance.crypto_manager is None:
            logger = get_logger(__name__)
            log_error(logger, "Cryptography not available")
            raise typer.Exit(1)

        # Get input text
        if text is None:
            input_text = app_instance.io_manager.get_clipboard_text()
        else:
            input_text = text

        if not input_text:
            logger = get_logger(__name__)
            log_warning(logger, "No text to encrypt")
            raise typer.Exit(1)

        # Encrypt text
        encrypted = app_instance.crypto_manager.encrypt_text(input_text)

        # Output result
        if output:
            app_instance.io_manager.set_output_text(encrypted)

        console.print("[green]Text encrypted successfully[/green]")
        console.print(f"[cyan]Encrypted length:[/cyan] {len(encrypted)} characters")

    except StringMultitoolError as e:
        logger = get_logger(__name__)
        log_error(logger, f"Error: {e}")
        raise typer.Exit(1)


@app.command("decrypt", help="Decrypt text using RSA+AES hybrid decryption")  # type: ignore
def decrypt_text(
    text: Annotated[
        Optional[str],
        typer.Option(
            "--text", "-t", help="Text to decrypt (if not provided, uses clipboard)"
        ),
    ] = None,
    output: Annotated[
        bool, typer.Option("--output", "-o", help="Copy result to clipboard")
    ] = True,
) -> None:
    """Decrypt text using hybrid RSA+AES decryption.

    Args:
        text: Optional text to decrypt (uses clipboard if not provided)
        output: Whether to copy result to clipboard
    """
    try:
        app_instance = get_app()

        if app_instance.crypto_manager is None:
            logger = get_logger(__name__)
            log_error(logger, "Cryptography not available")
            raise typer.Exit(1)

        # Get input text
        if text is None:
            input_text = app_instance.io_manager.get_clipboard_text()
        else:
            input_text = text

        if not input_text:
            logger = get_logger(__name__)
            log_warning(logger, "No text to decrypt")
            raise typer.Exit(1)

        # Decrypt text
        decrypted = app_instance.crypto_manager.decrypt_text(input_text)

        # Output result
        if output:
            app_instance.io_manager.set_output_text(decrypted)

        console.print("[green]Text decrypted successfully[/green]")
        console.print(f"[cyan]Decrypted:[/cyan] '{decrypted}'")

    except StringMultitoolError as e:
        logger = get_logger(__name__)
        log_error(logger, f"Error: {e}")
        raise typer.Exit(1)


@app.command("daemon", help="Start daemon mode for continuous clipboard monitoring")  # type: ignore
def daemon_mode(
    rules: Annotated[
        Optional[str],
        typer.Option(
            "--rules", "-r", help="Transformation rules to apply automatically"
        ),
    ] = None,
    preset: Annotated[
        Optional[str], typer.Option("--preset", "-p", help="Use predefined rule preset")
    ] = None,
) -> None:
    """Start daemon mode for continuous clipboard monitoring.

    Args:
        rules: Optional transformation rules to apply automatically
        preset: Optional preset name to use
    """
    try:
        app_instance = get_app()

        # Check if daemon mode is available
        if app_instance.daemon_mode is None:
            logger = get_logger(__name__)
            log_error(logger, "Daemon mode not available")
            raise typer.Exit(1)

        # Configure daemon mode if rules or preset provided
        if rules:
            app_instance.daemon_mode.set_transformation_rules([rules])
        elif preset:
            app_instance.daemon_mode.set_preset(preset)

        logger = get_logger(__name__)
        log_info(logger, "Starting daemon mode...")
        log_info(logger, "Press Ctrl+C to stop")

        app_instance.run_daemon_mode()

    except StringMultitoolError as e:
        logger = get_logger(__name__)
        log_error(logger, f"Error: {e}")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        logger = get_logger(__name__)
        log_info(logger, "\nDaemon mode stopped")
        raise typer.Exit(0)


@app.command("rules", help="Display available transformation rules")  # type: ignore
def show_rules(
    category: Annotated[
        Optional[str],
        typer.Option(
            "--category",
            "-c",
            help="Filter by category (basic, case, string, advanced)",
        ),
    ] = None,
    search: Annotated[
        Optional[str], typer.Option("--search", "-s", help="Search rules by keyword")
    ] = None,
) -> None:
    """Display available transformation rules with examples.

    Args:
        category: Optional category filter
        search: Optional search keyword
    """
    try:
        app_instance = get_app()
        rules = app_instance.transformation_engine.get_available_rules()

        table = Table(title="Available Transformation Rules", show_header=True)
        table.add_column("Rule", style="cyan", width=8)
        table.add_column("Name", style="green", width=20)
        table.add_column("Description", style="white", width=40)
        table.add_column("Example", style="yellow", width=15)

        for rule_key, rule_info in rules.items():
            # Apply filters
            if (
                category
                and hasattr(rule_info, "rule_type")
                and rule_info.rule_type.name.lower() != category.lower()
            ):
                continue
            if (
                search
                and search.lower() not in rule_info.name.lower()
                and search.lower() not in rule_info.description.lower()
            ):
                continue

            table.add_row(
                f"/{rule_key}",
                rule_info.name,
                rule_info.description,
                getattr(rule_info, "example", "N/A"),
            )

        console.print(table)

        # Show usage examples
        console.print("\n[bold]Usage Examples:[/bold]")
        console.print(
            "  [cyan]string-multitool transform '/t/l'[/cyan] - Trim and lowercase"
        )
        console.print(
            "  [cyan]string-multitool transform '/u/R'[/cyan] - Uppercase and reverse"
        )
        console.print(
            "  [cyan]echo 'text' | string-multitool transform '/p'[/cyan] - PascalCase from pipe"
        )

    except StringMultitoolError as e:
        logger = get_logger(__name__)
        log_error(logger, f"Error: {e}")
        raise typer.Exit(1)


@app.command("version", help="Show version information")  # type: ignore
def show_version() -> None:
    """Display version and system information."""
    console.print(
        Panel.fit(
            "[bold cyan]String_Multitool[/bold cyan]\n"
            "[green]Version:[/green] 2.1.0 (Typer Edition)\n"
            "[green]Python:[/green] " + sys.version.split()[0] + "\n"
            "[green]Platform:[/green] " + sys.platform,
            title="Version Info",
            border_style="blue",
        )
    )


def run_cli() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    run_cli()
