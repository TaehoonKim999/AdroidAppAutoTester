"""
Unit Tests for Phase 7: CLI Main

Tests:
- CLI class initialization and basic functionality
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Mock uiautomator2 before importing src modules
sys.modules['uiautomator2'] = Mock()

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import CLI
from src.config_manager import GlobalSettings


class TestCLI:
    """Test cases for CLI class."""
    
    def test_initialization(self):
        """Test CLI initialization."""
        with patch('src.main.get_global_settings') as mock_get_settings:
            mock_settings = Mock(spec=GlobalSettings)
            mock_get_settings.return_value = mock_settings
            
            cli = CLI()
            
            assert cli.config_manager is not None
            assert cli.settings is not None
            assert cli.device_manager is None
            assert cli.args is None
            
            print("✓ CLI initialization test passed")
    
    def test_parse_args_list_command(self):
        """Test parsing list command."""
        with patch('src.main.get_global_settings') as mock_get_settings:
            mock_settings = Mock(spec=GlobalSettings)
            mock_get_settings.return_value = mock_settings
            
            cli = CLI()
            
            # Patch sys.argv
            with patch.object(sys, 'argv', ['test', 'list']):
                args = cli._parse_args()
            
            assert args.command == "list"
            assert args.apps is False
            
            print("✓ CLI parse args list command test passed")
    
    def test_parse_args_list_apps_command(self):
        """Test parsing list --apps command."""
        with patch('src.main.get_global_settings') as mock_get_settings:
            mock_settings = Mock(spec=GlobalSettings)
            mock_get_settings.return_value = mock_settings
            
            cli = CLI()
            
            with patch.object(sys, 'argv', ['test', 'list', '--apps']):
                args = cli._parse_args()
            
            assert args.command == "list"
            assert args.apps is True
            
            print("✓ CLI parse args list --apps command test passed")
    
    def test_parse_args_run_command(self):
        """Test parsing run command."""
        with patch('src.main.get_global_settings') as mock_get_settings:
            mock_settings = Mock(spec=GlobalSettings)
            mock_get_settings.return_value = mock_settings
            
            cli = CLI()
            
            with patch.object(sys, 'argv', ['test', 'run']):
                args = cli._parse_args()
            
            assert args.command == "run"
            assert args.app is None
            assert args.duration is None
            assert args.report == ["text"]
            
            print("✓ CLI parse args run command test passed")
    
    def test_parse_args_run_with_options(self):
        """Test parsing run command with options."""
        with patch('src.main.get_global_settings') as mock_get_settings:
            mock_settings = Mock(spec=GlobalSettings)
            mock_get_settings.return_value = mock_settings
            
            cli = CLI()
            
            with patch.object(sys, 'argv', [
                'test', 'run',
                '--app', 'com.example.test',
                '--duration', '60',
                '--actions', 'scroll', 'click_buttons',
                '--report', 'html', 'json'
            ]):
                args = cli._parse_args()
            
            assert args.command == "run"
            assert args.app == "com.example.test"
            assert args.duration == 60
            assert args.actions == ["scroll", "click_buttons"]
            assert "html" in args.report
            assert "json" in args.report
            
            print("✓ CLI parse args run with options test passed")
    
    def test_parse_args_run_disable_options(self):
        """Test parsing run command with disable options."""
        with patch('src.main.get_global_settings') as mock_get_settings:
            mock_settings = Mock(spec=GlobalSettings)
            mock_get_settings.return_value = mock_settings
            
            cli = CLI()
            
            with patch.object(sys, 'argv', [
                'test', 'run',
                '--no-logcat',
                '--no-screenshot'
            ]):
                args = cli._parse_args()
            
            assert args.command == "run"
            assert args.no_logcat is True
            assert args.no_screenshot is True
            
            print("✓ CLI parse args run disable options test passed")
    
    def test_parse_args_config_command(self):
        """Test parsing config command."""
        with patch('src.main.get_global_settings') as mock_get_settings:
            mock_settings = Mock(spec=GlobalSettings)
            mock_get_settings.return_value = mock_settings
            
            cli = CLI()
            
            with patch.object(sys, 'argv', ['test', 'config']):
                args = cli._parse_args()
            
            assert args.command == "config"
            assert args.set is None
            assert args.get is None
            assert args.reset is False
            
            print("✓ CLI parse args config command test passed")
    
    def test_parse_args_config_set(self):
        """Test parsing config --set command."""
        with patch('src.main.get_global_settings') as mock_get_settings:
            mock_settings = Mock(spec=GlobalSettings)
            mock_get_settings.return_value = mock_settings
            
            cli = CLI()
            
            with patch.object(sys, 'argv', [
                'test', 'config',
                '--set', 'test_duration', '60'
            ]):
                args = cli._parse_args()
            
            assert args.command == "config"
            assert args.set == ["test_duration", "60"]
            
            print("✓ CLI parse args config --set test passed")
    
    def test_parse_args_config_get(self):
        """Test parsing config --get command."""
        with patch('src.main.get_global_settings') as mock_get_settings:
            mock_settings = Mock(spec=GlobalSettings)
            mock_get_settings.return_value = mock_settings
            
            cli = CLI()
            
            with patch.object(sys, 'argv', [
                'test', 'config',
                '--get', 'test_duration'
            ]):
                args = cli._parse_args()
            
            assert args.command == "config"
            assert args.get == "test_duration"
            
            print("✓ CLI parse args config --get test passed")
    
    def test_parse_args_config_reset(self):
        """Test parsing config --reset command."""
        with patch('src.main.get_global_settings') as mock_get_settings:
            mock_settings = Mock(spec=GlobalSettings)
            mock_get_settings.return_value = mock_settings
            
            cli = CLI()
            
            with patch.object(sys, 'argv', ['test', 'config', '--reset']):
                args = cli._parse_args()
            
            assert args.command == "config"
            assert args.reset is True
            
            print("✓ CLI parse args config --reset test passed")


def run_all_tests():
    """Run all Phase 7 unit tests."""
    print("\n" + "="*60)
    print("  Phase 7: CLI Main Tests")
    print("="*60 + "\n")
    
    print("Testing CLI...")
    test_cli = TestCLI()
    test_cli.test_initialization()
    test_cli.test_parse_args_list_command()
    test_cli.test_parse_args_list_apps_command()
    test_cli.test_parse_args_run_command()
    test_cli.test_parse_args_run_with_options()
    test_cli.test_parse_args_run_disable_options()
    test_cli.test_parse_args_config_command()
    test_cli.test_parse_args_config_set()
    test_cli.test_parse_args_config_get()
    test_cli.test_parse_args_config_reset()
    print()
    
    print("="*60)
    print("  All Phase 7 Tests Passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()