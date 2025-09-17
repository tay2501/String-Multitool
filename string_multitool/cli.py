"""
Modern CLI interface for String_Multitool using Typer.

This module provides a type-safe, modern command-line interface with
comprehensive help system, auto-completion support, and intuitive subcommands.
"""

from __future__ import annotations

import sys
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typer import Typer

from .exceptions import ConfigurationError, StringMultitoolError, ValidationError
from .main import ApplicationInterface

# Import logging utilities
from .utils.unified_logger import get_logger, log_error, log_info, log_warning

# Rich console for beautiful output
console: Console = Console()

# Type alias for command decorator
CommandDecorator = Any

# Completion functions for MCP operations
def complete_context7_operations(incomplete: str) -> list[str]:
    """Provide completion for Context7 MCP operations."""
    operations = [
        "resolve-library-id",
        "get-library-docs",
        "search-examples",
        "list-libraries"
    ]
    return [op for op in operations if incomplete.lower() in op.lower()]


def complete_serena_operations(incomplete: str) -> list[str]:
    """Provide completion for Serena MCP operations."""
    operations = [
        "find-symbol",
        "get-symbols-overview",
        "search-for-pattern",
        "list-dir",
        "find-file",
        "read-memory",
        "write-memory",
        "find-referencing-symbols"
    ]
    return [op for op in operations if incomplete.lower() in op.lower()]

# Main Typer application with Tab completion enabled
app: Typer = typer.Typer(
    name="string-multitool",
    help="Advanced text transformation tool with Context7/Serena MCP support and Tab completion",
    epilog="Examples:\n  string-multitool transform '/t/l'           # Trim and lowercase\n  string-multitool context7 resolve-library-id # Context7 MCP operation\n  string-multitool serena find-symbol          # Serena MCP operation\n  string-multitool completion --install         # Install Tab completion",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=True,  # Enable Typer's built-in completion system
)

# Create application instance (will be initialized when needed)
_app_instance: ApplicationInterface | None = None


def get_app() -> ApplicationInterface:
    """Get or create application instance using EAFP pattern.

    Returns:
        ApplicationInterface: Singleton application instance

    Raises:
        ConfigurationError: If application initialization fails
    """
    global _app_instance
    if _app_instance is None:
        try:
            from .application_factory import ApplicationFactory

            _app_instance = ApplicationFactory.create_application()
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize application: {e}",
                {"error_type": type(e).__name__},
            ) from e
    return _app_instance


def _handle_cli_error(error: Exception, operation: str, **context: Any) -> None:
    """Centralized CLI error handling with consistent logging.

    Args:
        error: The exception that occurred
        operation: Description of the operation that failed
        **context: Additional context information
    """
    logger = get_logger(__name__)

    if isinstance(error, StringMultitoolError):
        log_error(logger, f"Error in {operation}: {error}")
        raise typer.Exit(1)
    else:
        log_error(logger, f"Unexpected error in {operation}: {error}")
        raise ConfigurationError(
            f"{operation} failed: {error}",
            {"error_type": type(error).__name__, **context},
        ) from error


def _get_input_text(
    app_instance: ApplicationInterface,
    text: str | None,
    use_clipboard_fallback: bool = False,
) -> str:
    """Get input text from various sources using EAFP pattern.

    Args:
        app_instance: Application instance
        text: Optional explicit text input
        use_clipboard_fallback: Whether to use clipboard as fallback

    Returns:
        Input text string

    Raises:
        ValidationError: If no input text is available
    """
    try:
        if text is not None:
            return text

        if use_clipboard_fallback:
            input_text = app_instance.io_manager.get_clipboard_text()
        else:
            input_text = app_instance.io_manager.get_input_text()

        if not input_text.strip():
            raise ValidationError(
                "No input text available",
                {"text_source": ("clipboard" if use_clipboard_fallback else "pipe_or_clipboard")},
            )

        return input_text
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(
            f"Failed to get input text: {e}", {"error_type": type(e).__name__}
        ) from e


def _output_result(
    app_instance: ApplicationInterface,
    result: str,
    should_output: bool,
    success_message: str,
) -> None:
    """Output transformation result with consistent formatting.

    Args:
        app_instance: Application instance
        result: Result text to output
        should_output: Whether to copy to clipboard
        success_message: Success message to display
    """
    try:
        if should_output:
            app_instance.io_manager.set_output_text(result)

        console.print(f"[green]{success_message}[/green]")
        console.print(f"[cyan]Result:[/cyan] '{result[:100]}{'...' if len(result) > 100 else ''}'")
    except Exception as e:
        logger = get_logger(__name__)
        log_warning(logger, f"Failed to output result: {e}")
        # Continue execution - output failure shouldn't stop the operation


@app.command("interactive", help="Start interactive mode for real-time text transformation")
def interactive_mode() -> None:
    """Start interactive mode with clipboard monitoring and real-time transformation."""
    try:
        app_instance = get_app()
        input_text = app_instance.io_manager.get_input_text()
        app_instance._run_interactive_mode()
    except StringMultitoolError as e:
        logger = get_logger(__name__)
        log_error(logger, f"Error: {e}")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        logger = get_logger(__name__)
        log_info(logger, "\nGoodbye!")
        raise typer.Exit(0)
    except Exception as e:
        logger = get_logger(__name__)
        log_error(logger, f"Unexpected error in interactive mode: {e}")
        raise ConfigurationError(
            f"Interactive mode failed: {e}",
            {"error_type": type(e).__name__},
        )


@app.command("transform", help="Apply transformation rules to text")
def transform_text(
    rules: Annotated[
        str,
        typer.Argument(help="Transformation rules (e.g., '/t/l' for trim + lowercase)"),
    ],
    text: Annotated[
        str | None,
        typer.Option("--text", "-t", help="Input text (if not provided, uses clipboard or pipe)"),
    ] = None,
    output: Annotated[
        bool, typer.Option("--output", "-o", help="Copy result to clipboard")
    ] = True,
) -> None:
    """Apply transformation rules to input text with simplified error handling.

    Args:
        rules: Transformation rules string (e.g., '/t/l/u')
        text: Optional input text (uses clipboard/pipe if not provided)
        output: Whether to copy result to clipboard
    """
    try:
        app_instance = get_app()
        input_text = _get_input_text(app_instance, text)

        result = app_instance.transformation_engine.apply_transformations(input_text, rules)

        _output_result(app_instance, result, output, f"Transformation applied: {rules}")

    except Exception as e:
        _handle_cli_error(e, "text transformation", rules=rules)


@app.command("encrypt", help="Encrypt text using RSA+AES hybrid encryption")
def encrypt_text(
    text: Annotated[
        str | None,
        typer.Option("--text", "-t", help="Text to encrypt (if not provided, uses clipboard)"),
    ] = None,
    output: Annotated[
        bool, typer.Option("--output", "-o", help="Copy result to clipboard")
    ] = True,
) -> None:
    """Encrypt text using hybrid RSA+AES encryption with simplified error handling.

    Args:
        text: Optional text to encrypt (uses clipboard if not provided)
        output: Whether to copy result to clipboard
    """
    try:
        app_instance = get_app()

        # Validate crypto manager availability
        if app_instance.crypto_manager is None:
            raise ConfigurationError(
                "Cryptography not available - encryption dependencies missing",
                {"crypto_available": False},
            )

        input_text = _get_input_text(app_instance, text, use_clipboard_fallback=True)
        encrypted = app_instance.crypto_manager.encrypt_text(input_text)

        _output_result(app_instance, encrypted, output, "Text encrypted successfully")
        console.print(f"[cyan]Encrypted length:[/cyan] {len(encrypted)} characters")

    except Exception as e:
        _handle_cli_error(e, "text encryption")


@app.command("decrypt", help="Decrypt text using RSA+AES hybrid decryption")
def decrypt_text(
    text: Annotated[
        str | None,
        typer.Option("--text", "-t", help="Text to decrypt (if not provided, uses clipboard)"),
    ] = None,
    output: Annotated[
        bool, typer.Option("--output", "-o", help="Copy result to clipboard")
    ] = True,
) -> None:
    """Decrypt text using hybrid RSA+AES decryption with simplified error handling.

    Args:
        text: Optional text to decrypt (uses clipboard if not provided)
        output: Whether to copy result to clipboard
    """
    try:
        app_instance = get_app()

        # Validate crypto manager availability
        if app_instance.crypto_manager is None:
            raise ConfigurationError(
                "Cryptography not available - decryption dependencies missing",
                {"crypto_available": False},
            )

        input_text = _get_input_text(app_instance, text, use_clipboard_fallback=True)
        decrypted = app_instance.crypto_manager.decrypt_text(input_text)

        _output_result(app_instance, decrypted, output, "Text decrypted successfully")

    except Exception as e:
        _handle_cli_error(e, "text decryption")


@app.command("daemon", help="Start daemon mode (not implemented)")
def daemon_mode() -> None:
    """Daemon mode is not currently implemented."""
    typer.echo("Daemon mode is not available in this version.")
    raise typer.Exit(1)


@app.command("rules", help="Display available transformation rules")
def show_rules(
    category: Annotated[
        str | None,
        typer.Option(
            "--category",
            "-c",
            help="Filter by category (basic, case, string, advanced)",
        ),
    ] = None,
    search: Annotated[
        str | None, typer.Option("--search", "-s", help="Search rules by keyword")
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
        console.print("  [cyan]string-multitool transform '/t/l'[/cyan] - Trim and lowercase")
        console.print("  [cyan]string-multitool transform '/u/R'[/cyan] - Uppercase and reverse")
        console.print(
            "  [cyan]echo 'text' | string-multitool transform '/p'[/cyan] - PascalCase from pipe"
        )

    except StringMultitoolError as e:
        logger = get_logger(__name__)
        log_error(logger, f"Error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger = get_logger(__name__)
        log_error(logger, f"Unexpected error in rules display: {e}")
        raise ConfigurationError(
            f"Rules display failed: {e}",
            {"error_type": type(e).__name__, "category": category, "search": search},
        )


@app.command("context7", help="Execute Context7 MCP operations for library documentation")
def context7_command(
    operation: Annotated[
        str,
        typer.Argument(help="Context7 MCP operation", autocompletion=complete_context7_operations)
    ],
    library: Annotated[
        str | None,
        typer.Option("--library", "-l", help="Library name for documentation lookup")
    ] = None,
    topic: Annotated[
        str | None,
        typer.Option("--topic", "-t", help="Specific topic to focus on")
    ] = None,
    tokens: Annotated[
        int,
        typer.Option("--tokens", help="Maximum tokens for documentation")
    ] = 3000,
) -> None:
    """Execute Context7 MCP operations for library documentation."""
    console.print(Panel(
        f"Context7 Operation: [blue]{operation}[/blue]\n"
        f"Library: [green]{library or 'N/A'}[/green]\n"
        f"Topic: [yellow]{topic or 'N/A'}[/yellow]\n"
        f"Tokens: [cyan]{tokens}[/cyan]",
        title="Context7 MCP",
        border_style="blue"
    ))

    # Note: Actual MCP integration would be implemented here
    console.print("[dim]Note: MCP integration requires separate setup[/dim]")
    console.print("[yellow]Use: npx -y @upstash/context7-mcp@latest --transport stdio[/yellow]")


@app.command("serena", help="Execute Serena MCP operations for code analysis")
def serena_command(
    operation: Annotated[
        str,
        typer.Argument(help="Serena MCP operation", autocompletion=complete_serena_operations)
    ],
    path: Annotated[
        str,
        typer.Option("--path", "-p", help="File or directory path")
    ] = ".",
    pattern: Annotated[
        str | None,
        typer.Option("--pattern", help="Search pattern for pattern-based operations")
    ] = None,
) -> None:
    """Execute Serena MCP operations for code analysis."""
    console.print(Panel(
        f"Serena Operation: [blue]{operation}[/blue]\n"
        f"Path: [green]{path}[/green]\n"
        f"Pattern: [yellow]{pattern or 'N/A'}[/yellow]",
        title="Serena MCP",
        border_style="magenta"
    ))

    # Note: Actual MCP integration would be implemented here
    console.print("[dim]Note: MCP integration requires separate setup[/dim]")
    console.print("[yellow]Serena MCP should be configured in your IDE/environment[/yellow]")


@app.command("completion", help="Manage shell completion installation")
def completion_command(
    install: Annotated[
        bool,
        typer.Option("--install", help="Install shell completion")
    ] = False,
    show: Annotated[
        str | None,
        typer.Option("--show", help="Show completion script for shell (bash, zsh, fish, powershell)")
    ] = None,
    shell: Annotated[
        str | None,
        typer.Option("--shell", help="Target shell for installation")
    ] = None,
) -> None:
    """Manage shell completion installation."""
    if install:
        console.print("[blue]Installing shell completion...[/blue]")
        console.print("[yellow]Run: python scripts/setup_completion.py --install[/yellow]")
        if shell:
            console.print(f"[dim]Target shell: {shell}[/dim]")
    elif show:
        console.print(f"[blue]Showing completion script for {show}...[/blue]")
        console.print(f"[yellow]Run: python scripts/setup_completion.py --show {show}[/yellow]")
    else:
        console.print(Panel(
            "Shell Completion Management:\n\n"
            "[cyan]Install completion:[/cyan]\n"
            "  string-multitool completion --install\n"
            "  string-multitool completion --install --shell bash\n\n"
            "[cyan]Show completion script:[/cyan]\n"
            "  string-multitool completion --show bash\n"
            "  string-multitool completion --show zsh\n\n"
            "[cyan]Supported shells:[/cyan]\n"
            "  bash, zsh, fish, powershell",
            title="Shell Completion Help",
            border_style="blue"
        ))


@app.command("version", help="Show version information")
def show_version() -> None:
    """Display version and system information."""
    console.print(
        Panel.fit(
            "[bold cyan]String_Multitool[/bold cyan]\n"
            "[green]Version:[/green] 2.6.0 (Tab Completion Edition)\n"
            "[green]Python:[/green] " + sys.version.split()[0] + "\n"
            "[green]Platform:[/green] " + sys.platform + "\n"
            "[green]Features:[/green] Context7 MCP, Serena MCP, Tab Completion",
            title="Version Info",
            border_style="blue",
        )
    )


def run_cli() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    run_cli()
