#!/usr/bin/env python3
"""
Shell completion setup script for String-Multitool.

This script uses Typer's built-in completion system to generate and install
shell completion scripts for various shells (bash, zsh, fish, powershell).

Usage:
    python scripts/setup_completion.py --install
    python scripts/setup_completion.py --show bash
    python scripts/setup_completion.py --uninstall
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Literal

import typer
from rich.console import Console
from rich.panel import Panel

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

console = Console()

ShellType = Literal["bash", "zsh", "fish", "powershell"]


def get_completion_script(shell: ShellType, program_name: str = "string-multitool") -> str:
    """Generate completion script for specified shell."""
    scripts = {
        "bash": f'''
# String-Multitool completion for Bash
_STRING_MULTITOOL_COMPLETE=bash_source {program_name} > /dev/null 2>&1 && {{
    eval "$(_STRING_MULTITOOL_COMPLETE=bash_source {program_name})"
}}
''',
        "zsh": f'''
# String-Multitool completion for Zsh
_STRING_MULTITOOL_COMPLETE=zsh_source {program_name} > /dev/null 2>&1 && {{
    eval "$(_STRING_MULTITOOL_COMPLETE=zsh_source {program_name})"
}}
''',
        "fish": f'''
# String-Multitool completion for Fish
_STRING_MULTITOOL_COMPLETE=fish_source {program_name} > /dev/null 2>&1; and eval (_STRING_MULTITOOL_COMPLETE=fish_source {program_name})
''',
        "powershell": f'''
# String-Multitool completion for PowerShell
if (Get-Command {program_name} -ErrorAction SilentlyContinue) {{
    $env:_STRING_MULTITOOL_COMPLETE = "powershell_source"
    Invoke-Expression "$({program_name})"
}}
'''
    }
    return scripts.get(shell, "")


def detect_shell() -> ShellType | None:
    """Auto-detect current shell."""
    try:
        import shellingham
        shell_name, _ = shellingham.detect_shell()

        # Map shell names to our types
        shell_mapping = {
            "bash": "bash",
            "zsh": "zsh",
            "fish": "fish",
            "powershell": "powershell",
            "pwsh": "powershell"
        }

        return shell_mapping.get(shell_name.lower())
    except ImportError:
        # Fallback detection
        shell_env = os.environ.get("SHELL", "").lower()
        if "bash" in shell_env:
            return "bash"
        elif "zsh" in shell_env:
            return "zsh"
        elif "fish" in shell_env:
            return "fish"

    return None


def install_completion(shell: ShellType | None = None) -> None:
    """Install completion for specified shell or auto-detect."""
    if shell is None:
        shell = detect_shell()
        if shell is None:
            console.print("[red]Could not detect shell. Please specify with --shell option.[/red]")
            raise typer.Exit(1)

    console.print(f"[blue]Installing completion for {shell}...[/blue]")

    # Get shell configuration file paths
    config_files = {
        "bash": [Path.home() / ".bashrc", Path.home() / ".bash_profile"],
        "zsh": [Path.home() / ".zshrc"],
        "fish": [Path.home() / ".config" / "fish" / "config.fish"],
        "powershell": [Path.home() / "Documents" / "PowerShell" / "profile.ps1"]
    }

    script = get_completion_script(shell)
    marker = "# String-Multitool completion"

    for config_file in config_files.get(shell, []):
        try:
            # Create parent directory if it doesn't exist
            config_file.parent.mkdir(parents=True, exist_ok=True)

            # Read existing content
            content = ""
            if config_file.exists():
                content = config_file.read_text()

            # Check if already installed
            if marker in content:
                console.print(f"[yellow]Completion already installed in {config_file}[/yellow]")
                continue

            # Append completion script
            with config_file.open("a") as f:
                f.write(f"\n{script}")

            console.print(f"[green]Completion installed in {config_file}[/green]")
            console.print("[blue]Please restart your terminal or run:[/blue]")
            console.print(f"[cyan]source {config_file}[/cyan]")
            return

        except Exception as e:
            console.print(f"[red]Failed to install in {config_file}: {e}[/red]")

    console.print(f"[red]Could not install completion for {shell}[/red]")


def show_completion(shell: ShellType) -> None:
    """Show completion script for specified shell."""
    script = get_completion_script(shell)

    panel = Panel(
        script.strip(),
        title=f"{shell.capitalize()} Completion Script",
        border_style="blue"
    )

    console.print(panel)
    console.print(f"\n[blue]To install manually, add this to your {shell} configuration file.[/blue]")


def uninstall_completion() -> None:
    """Remove completion from shell configuration files."""
    config_files = [
        Path.home() / ".bashrc",
        Path.home() / ".bash_profile",
        Path.home() / ".zshrc",
        Path.home() / ".config" / "fish" / "config.fish",
        Path.home() / "Documents" / "PowerShell" / "profile.ps1"
    ]

    marker = "# String-Multitool completion"
    removed_count = 0

    for config_file in config_files:
        if not config_file.exists():
            continue

        try:
            lines = config_file.read_text().split("\n")
            new_lines = []
            skip_next = False

            for line in lines:
                if marker in line:
                    skip_next = True
                    removed_count += 1
                    continue
                elif skip_next and line.strip() == "":
                    skip_next = False
                    continue
                elif skip_next:
                    skip_next = False

                new_lines.append(line)

            if len(new_lines) != len(lines):
                config_file.write_text("\n".join(new_lines))
                console.print(f"[green]Removed completion from {config_file}[/green]")

        except Exception as e:
            console.print(f"[red]Failed to process {config_file}: {e}[/red]")

    if removed_count == 0:
        console.print("[yellow]No completion installations found.[/yellow]")
    else:
        console.print(f"[green]Removed {removed_count} completion installation(s).[/green]")


def main(
    install: bool = typer.Option(False, "--install", help="Install shell completion"),
    show: ShellType = typer.Option(None, "--show", help="Show completion script for shell"),
    uninstall: bool = typer.Option(False, "--uninstall", help="Remove shell completion"),
    shell: ShellType = typer.Option(None, "--shell", help="Target shell (auto-detect if not specified)")
) -> None:
    """Setup shell completion for String-Multitool."""

    console.print(Panel(
        "String-Multitool Shell Completion Setup",
        subtitle="Tab completion for commands and MCP operations",
        style="bold blue"
    ))

    if install:
        install_completion(shell)
    elif show:
        show_completion(show)
    elif uninstall:
        uninstall_completion()
    else:
        console.print("[red]Please specify an action: --install, --show, or --uninstall[/red]")
        console.print("Use --help for more information.")
        raise typer.Exit(1)


if __name__ == "__main__":
    typer.run(main)