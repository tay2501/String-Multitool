#!/usr/bin/env python3
"""
Tab completion system for String-Multitool with Context7 and Serena MCP support.

This module implements Tab completion using Typer's built-in completion system,
following best practices for minimal code and maximum reuse of existing packages.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, List

import typer
from rich.console import Console
from rich.table import Table

# Import project modules
from .models.transformation_coordinator import TransformationCoordinator
from .models.types_modern import CompletionChoice, CompletionContext

console = Console()


class CompletionEngine:
    """Handles Tab completion for String-Multitool commands and MCP operations."""

    def __init__(self, coordinator: TransformationCoordinator) -> None:
        """Initialize completion engine with transformation coordinator."""
        self.coordinator = coordinator
        self.app = typer.Typer(
            help="String-Multitool with Tab completion support",
            no_args_is_help=True,
            add_completion=True,  # Enable Typer's built-in completion
        )
        self._setup_commands()

    def _setup_commands(self) -> None:
        """Setup Typer commands with completion support."""

        @self.app.command("transform")
        def transform_command(
            rule: str = typer.Argument(
                ...,
                help="Transformation rule (e.g., /t/l, /u, /enc)",
                autocompletion=self.complete_transformation_rules
            ),
            text: str = typer.Option(
                None,
                "--text", "-t",
                help="Input text (if not provided, uses clipboard)"
            ),
            silent: bool = typer.Option(
                False,
                "--silent", "-s",
                help="Silent mode - show only result"
            )
        ) -> None:
            """Apply transformation rule to text."""
            try:
                if text is None:
                    # Use clipboard as default input
                    from .io.clipboard import get_clipboard_text
                    text = get_clipboard_text()

                result = self.coordinator.apply_transformations(text, rule)

                if silent:
                    typer.echo(result)
                else:
                    console.print(f"[green]Result:[/green] {result}")

            except Exception as e:
                console.print(f"[red]Error:[/red] {e}", err=True)
                raise typer.Exit(1)

        @self.app.command("context7")
        def context7_command(
            operation: str = typer.Argument(
                ...,
                help="Context7 MCP operation",
                autocompletion=self.complete_context7_operations
            ),
            library: str = typer.Option(
                None,
                "--library", "-l",
                help="Library name for documentation lookup"
            )
        ) -> None:
            """Execute Context7 MCP operations."""
            console.print(f"[blue]Context7 Operation:[/blue] {operation}")
            if library:
                console.print(f"[blue]Library:[/blue] {library}")

        @self.app.command("serena")
        def serena_command(
            operation: str = typer.Argument(
                ...,
                help="Serena MCP operation",
                autocompletion=self.complete_serena_operations
            ),
            path: str = typer.Option(
                ".",
                "--path", "-p",
                help="File or directory path"
            )
        ) -> None:
            """Execute Serena MCP operations."""
            console.print(f"[blue]Serena Operation:[/blue] {operation}")
            console.print(f"[blue]Path:[/blue] {path}")

        @self.app.command("list-rules")
        def list_rules() -> None:
            """List available transformation rules."""
            rules = self.coordinator.get_available_rules()

            table = Table(title="Available Transformation Rules")
            table.add_column("Rule", style="cyan")
            table.add_column("Description", style="green")
            table.add_column("Example", style="yellow")

            for rule_name, rule in rules.items():
                table.add_row(
                    f"/{rule_name}",
                    rule.description,
                    rule.example or "N/A"
                )

            console.print(table)

    def complete_transformation_rules(
        self,
        incomplete: str,
        ctx: typer.Context | None = None
    ) -> List[CompletionChoice]:
        """Provide completion for transformation rules."""
        try:
            rules = self.coordinator.get_available_rules()
            choices = []

            for rule_name, rule in rules.items():
                rule_text = f"/{rule_name}"
                if incomplete in rule_text.lower():
                    choices.append(CompletionChoice(
                        value=rule_text,
                        description=rule.description
                    ))

            return choices

        except Exception:
            # Fallback to basic completion
            return [
                CompletionChoice(value="/t", description="Trim whitespace"),
                CompletionChoice(value="/l", description="Convert to lowercase"),
                CompletionChoice(value="/u", description="Convert to uppercase"),
                CompletionChoice(value="/enc", description="RSA encrypt"),
                CompletionChoice(value="/dec", description="RSA decrypt"),
            ]

    def complete_context7_operations(
        self,
        incomplete: str,
        ctx: typer.Context | None = None
    ) -> List[CompletionChoice]:
        """Provide completion for Context7 MCP operations."""
        operations = [
            CompletionChoice(value="resolve-library", description="Resolve library ID from name"),
            CompletionChoice(value="get-docs", description="Get library documentation"),
            CompletionChoice(value="search-code", description="Search code examples"),
            CompletionChoice(value="list-libraries", description="List available libraries"),
        ]

        return [op for op in operations if incomplete.lower() in op.value.lower()]

    def complete_serena_operations(
        self,
        incomplete: str,
        ctx: typer.Context | None = None
    ) -> List[CompletionChoice]:
        """Provide completion for Serena MCP operations."""
        operations = [
            CompletionChoice(value="find-symbol", description="Find code symbols"),
            CompletionChoice(value="get-overview", description="Get symbols overview"),
            CompletionChoice(value="search-pattern", description="Search for patterns"),
            CompletionChoice(value="list-dir", description="List directory contents"),
            CompletionChoice(value="find-file", description="Find files by pattern"),
            CompletionChoice(value="read-memory", description="Read project memory"),
            CompletionChoice(value="write-memory", description="Write project memory"),
        ]

        return [op for op in operations if incomplete.lower() in op.value.lower()]

    def run_completion_setup(self) -> None:
        """Setup shell completion for the application."""
        self.app()


def create_completion_app() -> typer.Typer:
    """Factory function to create completion-enabled Typer app."""
    from .application_factory import ApplicationFactory

    # Create application with all dependencies
    app_interface = ApplicationFactory.create_application()
    coordinator = app_interface.transformation_engine

    # Create completion engine
    completion_engine = CompletionEngine(coordinator)

    return completion_engine.app


# Main CLI entry point with completion
completion_app = create_completion_app()


def main() -> None:
    """Main entry point for completion-enabled CLI."""
    completion_app()


if __name__ == "__main__":
    main()