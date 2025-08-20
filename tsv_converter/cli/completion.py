"""Tab completion support for CLI commands.

Educational implementation of command-line completion using argcomplete
with dynamic rule set name completion.
"""

from typing import List, Optional
from pathlib import Path

try:
    import argcomplete
    from argcomplete import CompletionFinder
    COMPLETION_AVAILABLE = True
except ImportError:
    COMPLETION_AVAILABLE = False

from ..core.engine import TSVConverterEngine
from .main import load_config


class RuleSetCompleter:
    """Dynamic completer for rule set names.
    
    Demonstrates how to create dynamic completion that queries
    the database for available rule sets.
    """
    
    def __init__(self, config_path: Path = Path("config/tsv_converter.json")):
        self.config_path = config_path
    
    def __call__(self, prefix: str, **kwargs) -> List[str]:
        """Return completion options for rule set names.
        
        Args:
            prefix: Current partial input from user
            
        Returns:
            List of matching rule set names
        """
        try:
            config = load_config(self.config_path)
            
            # Quick engine initialization for completion
            with TSVConverterEngine(config) as engine:
                rule_sets = engine.list_rule_sets()
                
                # Filter by prefix
                return [
                    rule_set for rule_set in rule_sets 
                    if rule_set.startswith(prefix)
                ]
                
        except Exception:
            # Fallback to empty completion on any error
            # Completion should never crash the CLI
            return []


def setup_completion(parser, config_path: Optional[Path] = None) -> None:
    """Setup tab completion for the argument parser.
    
    Educational example of how to add intelligent completion
    to argparse-based CLIs.
    
    Args:
        parser: ArgumentParser instance to enhance
        config_path: Optional path to configuration file
    """
    if not COMPLETION_AVAILABLE:
        return
    
    # Create completer instance
    rule_set_completer = RuleSetCompleter(
        config_path or Path("config/tsv_converter.json")
    )
    
    # Add completion to specific arguments
    if hasattr(parser, '_subparsers'):
        for action in parser._subparsers._actions:
            if hasattr(action, 'choices'):
                for choice, subparser in action.choices.items():
                    if choice in ['convert', 'rm', 'remove', 'info']:
                        # Add rule set completion to these commands
                        for sub_action in subparser._actions:
                            if sub_action.dest == 'rule_set':
                                sub_action.completer = rule_set_completer
    
    # Enable argcomplete
    argcomplete.autocomplete(parser)


def install_completion_script() -> None:
    """Generate and display shell completion installation instructions.
    
    Educational helper for users to enable tab completion
    in their shell environment.
    """
    if not COMPLETION_AVAILABLE:
        print("Tab completion requires 'argcomplete' package:")
        print("  pip install argcomplete")
        return
    
    print("To enable tab completion, add this to your shell profile:")
    print()
    print("For bash (.bashrc or .bash_profile):")
    print("  eval \"$(register-python-argcomplete convertbytsv)\"")
    print()
    print("For zsh (.zshrc):")
    print("  autoload -U bashcompinit")
    print("  bashcompinit")
    print("  eval \"$(register-python-argcomplete convertbytsv)\"")
    print()
    print("Then restart your shell or run:")
    print("  source ~/.bashrc  # or your shell profile file")


if __name__ == "__main__":
    # CLI tool for completion setup
    install_completion_script()