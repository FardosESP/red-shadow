"""
Unit tests for CLI argument parser
"""

import pytest
import sys
from io import StringIO
from unittest.mock import patch
from ambani_integration.cli.parser import (
    create_parser,
    parse_args,
    validate_args,
    args_to_config,
    show_legal_disclaimer
)


class TestCreateParser:
    """Tests for create_parser function"""
    
    def test_parser_creation(self):
        """Test that parser is created successfully"""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == 'red-shadow-ambani'
    
    def test_parser_has_required_arguments(self):
        """Test that parser has all required arguments"""
        parser = create_parser()
        
        # Parse with minimal args to check structure
        args = parser.parse_args(['/path/to/dump'])
        
        # Check core attributes exist
        assert hasattr(args, 'dump_path')
        assert hasattr(args, 'ambani_mode')
        assert hasattr(args, 'safe_mode')
        assert hasattr(args, 'dry_run')
        assert hasattr(args, 'auto_stop_mode')


class TestParseArgs:
    """Tests for parse_args function"""
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_parse_basic_args(self, mock_disclaimer):
        """Test parsing basic arguments"""
        args = parse_args(['/path/to/dump'])
        
        assert args is not None
        assert args.dump_path == '/path/to/dump'
        assert args.ambani_mode is False
        assert args.safe_mode is True
        assert args.dry_run is False
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_parse_ambani_mode(self, mock_disclaimer):
        """Test parsing with --ambani-mode flag"""
        args = parse_args(['/path/to/dump', '--ambani-mode'])
        
        assert args is not None
        assert args.ambani_mode is True
        mock_disclaimer.assert_called_once()
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=False)
    def test_parse_ambani_mode_disclaimer_rejected(self, mock_disclaimer):
        """Test that program exits when disclaimer is rejected"""
        with pytest.raises(SystemExit) as exc_info:
            parse_args(['/path/to/dump', '--ambani-mode'])
        
        assert exc_info.value.code == 1
        mock_disclaimer.assert_called_once()
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_parse_safe_mode_flags(self, mock_disclaimer):
        """Test safe mode flag variations"""
        # Default safe mode
        args = parse_args(['/path/to/dump'])
        assert args.safe_mode is True
        
        # Explicit safe mode
        args = parse_args(['/path/to/dump', '--safe-mode'])
        assert args.safe_mode is True
        
        # Disable safe mode
        args = parse_args(['/path/to/dump', '--no-safe-mode'])
        assert args.safe_mode is False
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_parse_dry_run(self, mock_disclaimer):
        """Test --dry-run flag"""
        args = parse_args(['/path/to/dump', '--dry-run'])
        
        assert args is not None
        assert args.dry_run is True
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_parse_auto_stop_modes(self, mock_disclaimer):
        """Test --auto-stop-mode flag with different values"""
        # Manual mode (default)
        args = parse_args(['/path/to/dump'])
        assert args.auto_stop_mode == 'manual'
        
        # Notify mode
        args = parse_args(['/path/to/dump', '--auto-stop-mode', 'notify'])
        assert args.auto_stop_mode == 'notify'
        
        # Auto mode
        args = parse_args(['/path/to/dump', '--auto-stop-mode', 'auto'])
        assert args.auto_stop_mode == 'auto'
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_parse_auto_stop_threshold(self, mock_disclaimer):
        """Test --auto-stop-threshold flag"""
        args = parse_args(['/path/to/dump', '--auto-stop-threshold', '90'])
        
        assert args is not None
        assert args.auto_stop_threshold == 90
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_parse_skip_flags(self, mock_disclaimer):
        """Test skip analysis flags"""
        args = parse_args([
            '/path/to/dump',
            '--skip-ml',
            '--skip-network',
            '--skip-memory',
            '--skip-bytecode'
        ])
        
        assert args is not None
        assert args.skip_ml is True
        assert args.skip_network is True
        assert args.skip_memory is True
        assert args.skip_bytecode is True
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_parse_output_options(self, mock_disclaimer):
        """Test output configuration flags"""
        args = parse_args([
            '/path/to/dump',
            '--output', '/custom/output',
            '--format', 'json', 'pdf',
            '--no-gui'
        ])
        
        assert args is not None
        assert args.output_dir == '/custom/output'
        assert args.report_formats == ['json', 'pdf']
        assert args.no_gui is True
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_parse_logging_options(self, mock_disclaimer):
        """Test logging configuration flags"""
        args = parse_args([
            '/path/to/dump',
            '--verbose',
            '--log-file', '/custom/log.txt',
            '--no-color'
        ])
        
        assert args is not None
        assert args.verbose is True
        assert args.log_file == '/custom/log.txt'
        assert args.no_color is True
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_parse_resource_management(self, mock_disclaimer):
        """Test resource whitelist/blacklist flags"""
        args = parse_args([
            '/path/to/dump',
            '--whitelist', 'resource1', 'resource2',
            '--blacklist', 'resource3'
        ])
        
        assert args is not None
        assert args.resource_whitelist == ['resource1', 'resource2']
        assert args.resource_blacklist == ['resource3']


class TestValidateArgs:
    """Tests for validate_args function"""
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_validate_valid_args(self, mock_disclaimer):
        """Test validation of valid arguments"""
        args = parse_args(['/path/to/dump'])
        assert validate_args(args) is True
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_validate_invalid_threshold(self, mock_disclaimer):
        """Test validation fails for invalid threshold"""
        args = parse_args(['/path/to/dump', '--auto-stop-threshold', '150'])
        # parse_args returns None when validation fails
        assert args is None
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_validate_conflicting_verbose_quiet(self, mock_disclaimer):
        """Test validation fails for conflicting verbose and quiet flags"""
        args = parse_args(['/path/to/dump', '--verbose', '--quiet'])
        # parse_args returns None when validation fails
        assert args is None
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_validate_conflicting_gui_flags(self, mock_disclaimer):
        """Test validation fails for conflicting GUI flags"""
        args = parse_args(['/path/to/dump', '--no-gui', '--cmd-gui'])
        # parse_args returns None when validation fails
        assert args is None


class TestArgsToConfig:
    """Tests for args_to_config function"""
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_args_to_config_basic(self, mock_disclaimer):
        """Test conversion of basic arguments to config"""
        args = parse_args(['/path/to/dump'])
        config = args_to_config(args)
        
        assert config['ambani']['enabled'] is False
        assert config['ambani']['safe_mode'] is True
        assert config['ambani']['dry_run'] is False
        assert config['auto_stop']['mode'] == 'manual'
        assert config['auto_stop']['critical_threshold'] == 85
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_args_to_config_ambani_mode(self, mock_disclaimer):
        """Test conversion with Ambani mode enabled"""
        args = parse_args([
            '/path/to/dump',
            '--ambani-mode',
            '--dry-run',
            '--auto-stop-mode', 'auto',
            '--auto-stop-threshold', '90'
        ])
        config = args_to_config(args)
        
        assert config['ambani']['enabled'] is True
        assert config['ambani']['dry_run'] is True
        assert config['auto_stop']['mode'] == 'auto'
        assert config['auto_stop']['critical_threshold'] == 90
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_args_to_config_skip_flags(self, mock_disclaimer):
        """Test conversion with skip flags"""
        args = parse_args([
            '/path/to/dump',
            '--skip-ml',
            '--skip-network'
        ])
        config = args_to_config(args)
        
        assert config['ml']['enabled'] is False
        assert config['network_monitor']['enabled'] is False
        assert config['memory_forensics']['enabled'] is True
        assert config['bytecode_decompiler']['enabled'] is True
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_args_to_config_output_options(self, mock_disclaimer):
        """Test conversion with output options"""
        args = parse_args([
            '/path/to/dump',
            '--output', '/custom/output',
            '--format', 'json', 'pdf'
        ])
        config = args_to_config(args)
        
        assert config['reporting']['output_dir'] == '/custom/output'
        assert config['reporting']['formats'] == ['json', 'pdf']
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_args_to_config_logging(self, mock_disclaimer):
        """Test conversion with logging options"""
        args = parse_args([
            '/path/to/dump',
            '--verbose',
            '--log-file', '/custom/log.txt',
            '--no-color'
        ])
        config = args_to_config(args)
        
        assert config['logging']['level'] == 'DEBUG'
        assert config['logging']['file'] == '/custom/log.txt'
        assert config['logging']['colored'] is False
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_args_to_config_quiet_mode(self, mock_disclaimer):
        """Test conversion with quiet mode"""
        args = parse_args(['/path/to/dump', '--quiet'])
        config = args_to_config(args)
        
        assert config['logging']['level'] == 'ERROR'


class TestLegalDisclaimer:
    """Tests for legal disclaimer functionality"""
    
    @patch('builtins.input', return_value='yes')
    def test_disclaimer_accepted_yes(self, mock_input):
        """Test disclaimer acceptance with 'yes'"""
        result = show_legal_disclaimer()
        assert result is True
    
    @patch('builtins.input', return_value='y')
    def test_disclaimer_accepted_y(self, mock_input):
        """Test disclaimer acceptance with 'y'"""
        result = show_legal_disclaimer()
        assert result is True
    
    @patch('builtins.input', return_value='no')
    def test_disclaimer_rejected_no(self, mock_input):
        """Test disclaimer rejection with 'no'"""
        result = show_legal_disclaimer()
        assert result is False
    
    @patch('builtins.input', return_value='n')
    def test_disclaimer_rejected_n(self, mock_input):
        """Test disclaimer rejection with 'n'"""
        result = show_legal_disclaimer()
        assert result is False
    
    @patch('builtins.input', side_effect=KeyboardInterrupt)
    def test_disclaimer_interrupted(self, mock_input):
        """Test disclaimer handling of keyboard interrupt"""
        result = show_legal_disclaimer()
        assert result is False
    
    @patch('builtins.input', side_effect=EOFError)
    def test_disclaimer_eof(self, mock_input):
        """Test disclaimer handling of EOF"""
        result = show_legal_disclaimer()
        assert result is False


class TestIntegration:
    """Integration tests for complete CLI workflows"""
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_full_ambani_workflow(self, mock_disclaimer):
        """Test complete Ambani mode workflow"""
        args = parse_args([
            '/path/to/dump',
            '--ambani-mode',
            '--safe-mode',
            '--dry-run',
            '--auto-stop-mode', 'auto',
            '--auto-stop-threshold', '90',
            '--learning-mode',
            '--output', '/output',
            '--format', 'json', 'html',
            '--verbose'
        ])
        
        assert args is not None
        assert validate_args(args) is True
        
        config = args_to_config(args)
        
        # Verify all settings are correctly converted
        assert config['ambani']['enabled'] is True
        assert config['ambani']['safe_mode'] is True
        assert config['ambani']['dry_run'] is True
        assert config['auto_stop']['mode'] == 'auto'
        assert config['auto_stop']['critical_threshold'] == 90
        assert config['auto_stop']['learning_mode'] is True
        assert config['reporting']['output_dir'] == '/output'
        assert config['reporting']['formats'] == ['json', 'html']
        assert config['logging']['level'] == 'DEBUG'
    
    @patch('ambani_integration.cli.parser.show_legal_disclaimer', return_value=True)
    def test_minimal_workflow(self, mock_disclaimer):
        """Test minimal workflow with just dump path"""
        args = parse_args(['/path/to/dump'])
        
        assert args is not None
        assert validate_args(args) is True
        
        config = args_to_config(args)
        
        # Verify defaults
        assert config['ambani']['enabled'] is False
        assert config['ambani']['safe_mode'] is True
        assert config['auto_stop']['mode'] == 'manual'
        assert config['ml']['enabled'] is True
        assert config['network_monitor']['enabled'] is True
