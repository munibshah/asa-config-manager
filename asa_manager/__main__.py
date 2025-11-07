"""
ASA Configuration Manager CLI.

Run the package as a command-line tool:
    python -m asa_manager --help
"""

import argparse
import sys
from pathlib import Path

from .manager import ASAManager
from .utils import get_logger, CLIFormatter, format_commit_operation, format_revert_operation, show_operation_result

logger = get_logger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='ASA Configuration Manager - Manage Cisco ASA interface configurations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes
  python -m asa_manager -d configs/device.yaml -c configs/changes.yaml --preview

  # Apply changes with backup
  python -m asa_manager -d configs/device.yaml -c configs/changes.yaml --commit

  # Apply and save configuration
  python -m asa_manager -d configs/device.yaml -c configs/changes.yaml --commit --save

  # Revert last applied changes
  python -m asa_manager --revert

  # List backups
  python -m asa_manager --list-backups
        """
    )
    
    parser.add_argument(
        '-d', '--device-config',
        help='Path to device configuration YAML file',
        default='configs/device.yaml'
    )
    
    parser.add_argument(
        '-c', '--changes-config',
        help='Path to changes configuration YAML file',
        default='configs/changes.yaml'
    )
    
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview changes without applying'
    )
    
    parser.add_argument(
        '--commit',
        action='store_true',
        help='Apply changes to the device'
    )
    
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save configuration after applying changes'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup before changes'
    )
    
    parser.add_argument(
        '--list-backups',
        action='store_true',
        help='List available configuration backups'
    )
    
    parser.add_argument(
        '--revert',
        action='store_true',
        help='Revert the last applied changes'
    )
    
    parser.add_argument(
        '--backup-dir',
        default='backups',
        help='Directory for backups (default: backups)'
    )
    
    parser.add_argument(
        '--log-dir',
        default='logs',
        help='Directory for logs (default: logs)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not (args.preview or args.commit or args.list_backups or args.revert):
        parser.error("Must specify --preview, --commit, --list-backups, or --revert")
    
    try:
        # Initialize manager
        manager = ASAManager(
            device_config=args.device_config if Path(args.device_config).exists() else None,
            backup_dir=args.backup_dir,
            log_dir=args.log_dir
        )
        
        # Handle list backups command
        if args.list_backups:
            print("=" * 70)
            print("AVAILABLE BACKUPS")
            print("=" * 70)
            backups = manager.list_backups()
            if backups:
                for backup in backups:
                    print(f"  {backup}")
            else:
                print("  No backups found")
            return 0
        
        # Handle revert command
        if args.revert:
            # Check if there are revertible changes before connecting
            if not manager.has_revertible_changes():
                CLIFormatter.warning("No changes to revert. No changes have been applied recently.")
                return 0
            
            # Load device config if not already loaded
            if not manager.device_config:
                if not Path(args.device_config).exists():
                    CLIFormatter.error(f"Device config file not found: {args.device_config}")
                    print("Please create it from the example:")
                    print(f"  cp configs/device_example.yaml {args.device_config}")
                    return 1
                manager.load_device_config(args.device_config)
            
            # Connect to device with progress
            CLIFormatter.progress_start(f"Connecting to {manager.device_config.host}")
            if not manager.connect():
                print()
                CLIFormatter.error("Failed to connect to device")
                return 1
            CLIFormatter.progress_done()
            
            try:
                # Show enhanced revert display
                state = manager.state_manager.load_last_applied_changes()
                format_revert_operation(state)
                
                CLIFormatter.progress_start("Reverting configuration changes")
                CLIFormatter.spinner(0.5)
                result = manager.revert_last_changes()
                CLIFormatter.progress_done()
                
                show_operation_result(result['success'], 
                                    "Changes reverted successfully!" if result['success'] else f"Failed to revert changes: {result.get('message')}", 
                                    result.get('results'))
                
                if result['success']:
                    CLIFormatter.info(f"Reverted changes originally applied at: {result.get('reverted_at')}")
                    if result.get('backup_available'):
                        CLIFormatter.info(f"Original backup available at: {result.get('backup_available')}")
                    return 0
                else:
                    return 1
            
            finally:
                manager.disconnect()

        # Load device config if not already loaded
        if not manager.device_config:
            if not Path(args.device_config).exists():
                print(f"Error: Device config file not found: {args.device_config}")
                print("Please create it from the example:")
                print(f"  cp configs/device_example.yaml {args.device_config}")
                return 1
            manager.load_device_config(args.device_config)
        
        # Verify changes config exists (only for preview/commit operations)
        if not args.revert and not Path(args.changes_config).exists():
            print(f"Error: Changes config file not found: {args.changes_config}")
            print("Please create it from the example:")
            print(f"  cp configs/changes_example.yaml {args.changes_config}")
            return 1
        
        # Connect to device
        print(f"Connecting to {manager.device_config.host}...")
        if not manager.connect():
            print("Failed to connect to device")
            return 1
        print("Connected successfully!\n")
        
        try:
            # Load changes
            manager.load_changes(args.changes_config)
            
            # Preview changes
            if args.preview:
                print(manager.preview_changes())
            
            # Commit changes
            if args.commit:
                # Show enhanced commit display
                format_commit_operation(manager.interface_manager.staged_changes)
                
                CLIFormatter.progress_start("Creating configuration backup")
                CLIFormatter.spinner(0.3)
                
                result = manager.commit_changes(
                    save_config=args.save,
                    create_backup=not args.no_backup
                )
                
                CLIFormatter.progress_done()
                CLIFormatter.progress_start("Applying configuration changes")
                CLIFormatter.spinner(0.5)
                CLIFormatter.progress_done()
                
                show_operation_result(result['success'], 
                                    "Changes applied successfully!" if result['success'] else f"Failed to apply changes: {result.get('message')}", 
                                    result.get('results'))
                
                if result['success']:
                    if result.get('config_saved'):
                        CLIFormatter.success("Configuration saved to startup-config")
                    elif args.save:
                        CLIFormatter.warning("Failed to save configuration")
                    return 0
                else:
                    return 1
        
        finally:
            manager.disconnect()
        
        return 0
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        logger.exception("CLI error")
        return 1


if __name__ == '__main__':
    sys.exit(main())
