"""Test cases for CLI interface.

Testing command-line functionality with proper argument parsing,
output verification, and error handling scenarios.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

from ..cli.main import main, create_parser, handle_convert_command


class TestCLIParsing:
    """Test cases for command-line argument parsing."""
    
    def test_create_parser_basic(self):
        """Test parser creation and basic structure."""
        parser = create_parser()
        
        assert parser.prog == "tsvtr"
        assert "Convert clipboard text" in parser.description
    
    def test_parse_convert_command(self):
        """Test parsing convert command."""
        parser = create_parser()
        
        args = parser.parse_args(["convert", "test_rules"])
        
        assert args.command == "convert"
        assert args.rule_set == "test_rules"
    
    def test_parse_list_command(self):
        """Test parsing list command."""
        parser = create_parser()
        
        args = parser.parse_args(["ls"])
        assert args.command == "ls"
        
        # Test alias
        args = parser.parse_args(["list"])
        assert args.command == "list"
    
    def test_parse_remove_command(self):
        """Test parsing remove command."""
        parser = create_parser()
        
        args = parser.parse_args(["rm", "old_rules"])
        assert args.command == "rm"
        assert args.rule_set == "old_rules"
    
    def test_parse_sync_command(self):
        """Test parsing sync command."""
        parser = create_parser()
        
        # With default directory
        args = parser.parse_args(["sync"])
        assert args.command == "sync"
        assert args.directory == Path("config/tsv_rules")
        
        # With custom directory
        args = parser.parse_args(["sync", "/custom/path"])
        assert args.directory == Path("/custom/path")
    
    def test_parse_global_options(self):
        """Test parsing global options."""
        parser = create_parser()
        
        args = parser.parse_args([
            "--config", "custom_config.json",
            "--database", "sqlite:///custom.db",
            "--debug",
            "ls"
        ])
        
        assert args.config == Path("custom_config.json")
        assert args.database == "sqlite:///custom.db"
        assert args.debug is True


class TestCLICommands:
    """Test cases for CLI command execution."""
    
    @patch('pyperclip.paste')
    @patch('pyperclip.copy')
    def test_convert_command_success(self, mock_copy, mock_paste, converter_engine, sample_tsv_file):
        """Test successful text conversion via CLI."""
        # Setup
        mock_paste.return_value = "hello"
        converter_engine.sync_file(sample_tsv_file)
        
        # Execute conversion
        result = handle_convert_command(converter_engine, "test_rules")
        
        # Verify
        assert result == 0  # Success exit code
        mock_copy.assert_called_once_with("こんにちは")
    
    @patch('pyperclip.paste')
    def test_convert_command_empty_clipboard(self, mock_paste, converter_engine):
        """Test conversion with empty clipboard."""
        mock_paste.return_value = ""
        
        with patch('builtins.print') as mock_print:
            result = handle_convert_command(converter_engine, "any_rules")
            
            assert result == 1  # Error exit code
            mock_print.assert_called_with("Error: Clipboard is empty")
    
    @patch('pyperclip.paste')
    def test_convert_command_missing_rule_set(self, mock_paste, converter_engine):
        """Test conversion with nonexistent rule set."""
        mock_paste.return_value = "test text"
        
        with patch('builtins.print') as mock_print:
            result = handle_convert_command(converter_engine, "nonexistent")
            
            assert result == 1  # Error exit code
            # Should print error message
            mock_print.assert_called()
            args, _ = mock_print.call_args
            assert "Error:" in args[0]
    
    @patch('pyperclip.paste')
    @patch('pyperclip.copy')
    def test_convert_command_no_changes(self, mock_copy, mock_paste, converter_engine, sample_tsv_file):
        """Test conversion when no rules match."""
        mock_paste.return_value = "no_match"
        converter_engine.sync_file(sample_tsv_file)
        
        with patch('builtins.print') as mock_print:
            result = handle_convert_command(converter_engine, "test_rules")
            
            assert result == 0  # Success exit code
            mock_copy.assert_called_once_with("no_match")  # Unchanged
            mock_print.assert_called()
            args, _ = mock_print.call_args
            assert "No changes" in args[0]


class TestMainFunction:
    """Test cases for main CLI entry point."""
    
    @patch('sys.argv', ['usetsvr', '--help'])
    def test_help_display(self):
        """Test help display functionality."""
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0  # Help exits with 0
    
    @patch('sys.argv', ['usetsvr', 'health'])
    def test_health_command_success(self, converter_engine):
        """Test health check command."""
        with patch('tsv_converter.cli.main.TSVConverterEngine') as mock_engine:
            mock_engine.return_value.__enter__.return_value = converter_engine
            converter_engine.health_check = MagicMock(return_value={
                "engine": True,
                "database": True,
                "services": True
            })
            
            with patch('builtins.print') as mock_print:
                result = main()
                
                assert result == 0
                mock_print.assert_called()
    
    @patch('sys.argv', ['usetsvr', 'nonexistent_command'])
    def test_invalid_command(self):
        """Test handling of invalid commands."""
        with patch('builtins.print'):
            result = main()
            assert result == 1  # Error exit code
    
    def test_keyboard_interrupt_handling(self):
        """Test graceful handling of Ctrl+C."""
        with patch('tsv_converter.cli.main.TSVConverterEngine') as mock_engine:
            mock_engine.side_effect = KeyboardInterrupt()
            
            with patch('builtins.print') as mock_print:
                result = main()
                
                assert result == 1
                mock_print.assert_called_with("\nOperation cancelled by user")
    
    def test_configuration_loading(self, temp_directory):
        """Test configuration file loading."""
        import json
        
        # Create test config file
        config_file = temp_directory / "test_config.json"
        test_config = {
            "database_url": "sqlite:///test.db",
            "debug": True
        }
        
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Test config loading
        from ..cli.main import load_config
        loaded_config = load_config(config_file)
        
        assert loaded_config["database_url"] == "sqlite:///test.db"
        assert loaded_config["debug"] is True
    
    def test_configuration_defaults(self, temp_directory):
        """Test default configuration when file doesn't exist."""
        nonexistent_config = temp_directory / "nonexistent.json"
        
        from ..cli.main import load_config
        config = load_config(nonexistent_config)
        
        assert "database_url" in config
        assert "tsv_directory" in config
        assert config["enable_file_watching"] is False  # CLI default