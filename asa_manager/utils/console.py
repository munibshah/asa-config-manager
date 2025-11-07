"""Enhanced console output utilities for CLI operations."""

import time
from typing import List, Dict, Any


class CLIFormatter:
    """Provides enhanced console formatting for CLI operations."""
    
    # Color codes for terminal output
    COLORS = {
        'GREEN': '\033[92m',
        'RED': '\033[91m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'CYAN': '\033[96m',
        'MAGENTA': '\033[95m',
        'WHITE': '\033[97m',
        'BOLD': '\033[1m',
        'DIM': '\033[2m',
        'RESET': '\033[0m'
    }
    
    @classmethod
    def header(cls, title: str, width: int = 70) -> None:
        """Print a formatted header."""
        print(f"\n{cls.COLORS['BOLD']}{cls.COLORS['CYAN']}{'='*width}{cls.COLORS['RESET']}")
        print(f"{cls.COLORS['BOLD']}{cls.COLORS['WHITE']}{title.center(width)}{cls.COLORS['RESET']}")
        print(f"{cls.COLORS['BOLD']}{cls.COLORS['CYAN']}{'='*width}{cls.COLORS['RESET']}")
    
    @classmethod
    def subheader(cls, title: str, width: int = 70) -> None:
        """Print a formatted subheader."""
        print(f"\n{cls.COLORS['BOLD']}{cls.COLORS['BLUE']}{title}{cls.COLORS['RESET']}")
        print(f"{cls.COLORS['DIM']}{'-'*len(title)}{cls.COLORS['RESET']}")
    
    @classmethod
    def success(cls, message: str) -> None:
        """Print a success message."""
        print(f"{cls.COLORS['BOLD']}{cls.COLORS['GREEN']}✓ {message}{cls.COLORS['RESET']}")
    
    @classmethod
    def error(cls, message: str) -> None:
        """Print an error message."""
        print(f"{cls.COLORS['BOLD']}{cls.COLORS['RED']}✗ {message}{cls.COLORS['RESET']}")
    
    @classmethod
    def warning(cls, message: str) -> None:
        """Print a warning message."""
        print(f"{cls.COLORS['BOLD']}{cls.COLORS['YELLOW']}⚠ {message}{cls.COLORS['RESET']}")
    
    @classmethod
    def info(cls, message: str) -> None:
        """Print an info message."""
        print(f"{cls.COLORS['BLUE']}ℹ {message}{cls.COLORS['RESET']}")
    
    @classmethod
    def progress_start(cls, message: str) -> None:
        """Print a progress start message."""
        print(f"{cls.COLORS['CYAN']}⚙ {message}...{cls.COLORS['RESET']}", end='', flush=True)
    
    @classmethod
    def progress_done(cls) -> None:
        """Complete a progress message."""
        print(f" {cls.COLORS['GREEN']}Done!{cls.COLORS['RESET']}")
    
    @classmethod
    def spinner(cls, duration: float = 1.0) -> None:
        """Show a simple spinner animation."""
        spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            print(f'\r{cls.COLORS["CYAN"]}{spinner_chars[i % len(spinner_chars)]}{cls.COLORS["RESET"]}', end='', flush=True)
            time.sleep(0.1)
            i += 1
        print('\r', end='')
    
    @classmethod
    def change_preview(cls, interface: str, current: str, new: str, change_type: str = "nameif") -> None:
        """Print a formatted change preview."""
        print(f"  {cls.COLORS['BOLD']}{interface}{cls.COLORS['RESET']}")
        print(f"    {change_type}: {cls.COLORS['DIM']}{current}{cls.COLORS['RESET']} → {cls.COLORS['GREEN']}{new}{cls.COLORS['RESET']}")
    
    @classmethod
    def revert_preview(cls, interface: str, current: str, original: str, change_type: str = "nameif") -> None:
        """Print a formatted revert preview."""
        print(f"  {cls.COLORS['BOLD']}{interface}{cls.COLORS['RESET']}")
        print(f"    {change_type}: {cls.COLORS['RED']}{current}{cls.COLORS['RESET']} → {cls.COLORS['CYAN']}{original}{cls.COLORS['RESET']}")
    
    @classmethod
    def backup_info(cls, backup_path: str) -> None:
        """Print backup information."""
        print(f"{cls.COLORS['DIM']}📁 Backup: {backup_path}{cls.COLORS['RESET']}")
    
    @classmethod
    def command_list(cls, commands: List[str], title: str = "Commands") -> None:
        """Print a list of commands to be executed."""
        cls.subheader(title)
        for cmd in commands:
            print(f"  {cls.COLORS['DIM']}{cmd}{cls.COLORS['RESET']}")


def format_commit_operation(changes: List[Dict], backup_path: str = None) -> None:
    """Format the commit operation display."""
    formatter = CLIFormatter()
    
    formatter.header("APPLYING CONFIGURATION CHANGES")
    
    if backup_path:
        formatter.info(f"Configuration backup created: {backup_path}")
    
    formatter.subheader("Changes to Apply")
    for change in changes:
        change_obj = change.get('change', {})
        current_config = change.get('current_config', {})
        
        if hasattr(change_obj, 'nameif') and change_obj.nameif:
            current_nameif = current_config.get('nameif', 'none')
            formatter.change_preview(change['interface'], current_nameif, change_obj.nameif)
        
        if hasattr(change_obj, 'vlan') and change_obj.vlan:
            current_vlan = current_config.get('vlan', 'none')
            formatter.change_preview(change['interface'], current_vlan, str(change_obj.vlan), "vlan")
    
    print()


def format_revert_operation(state: Dict[str, Any]) -> None:
    """Format the revert operation display."""
    formatter = CLIFormatter()
    
    formatter.header("REVERTING CONFIGURATION CHANGES")
    
    timestamp = state.get('timestamp', 'Unknown')
    formatter.info(f"Reverting changes applied at: {timestamp}")
    
    if state.get('backup_path'):
        formatter.backup_info(state['backup_path'])
    
    formatter.subheader("Changes to Revert")
    for change in state['applied_changes']:
        interface = change['interface']
        original_config = change.get('original_config', {})
        change_data = change.get('change_data', {})
        
        if change_data.get('nameif'):
            current_nameif = change_data['nameif']
            original_nameif = original_config.get('nameif', 'none')
            formatter.revert_preview(interface, current_nameif, original_nameif)
        
        if change_data.get('vlan'):
            current_vlan = str(change_data['vlan'])
            original_vlan = original_config.get('vlan', 'none')
            formatter.revert_preview(interface, current_vlan, str(original_vlan), "vlan")
    
    print()


def show_operation_result(success: bool, message: str, results: List[Dict] = None) -> None:
    """Show the result of an operation."""
    formatter = CLIFormatter()
    
    if success:
        formatter.success(message)
    else:
        formatter.error(message)
        if results:
            for result in results:
                if not result.get('success'):
                    formatter.error(f"{result.get('interface')}: {result.get('error')}")
    
    print()