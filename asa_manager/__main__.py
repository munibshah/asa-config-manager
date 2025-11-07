"""
ASA Configuration Manager CLI.

Run the package as a command-line tool:
    python -m asa_manager --help
"""

import argparse
import sys
from pathlib import Path

from .manager import ASAManager
from .utils import get_logger

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
    if not (args.preview or args.commit or args.list_backups):
        parser.error("Must specify --preview, --commit, or --list-backups")
    
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
        
        # Load device config if not already loaded
        if not manager.device_config:
            if not Path(args.device_config).exists():
                print(f"Error: Device config file not found: {args.device_config}")
                print("Please create it from the example:")
                print(f"  cp configs/device_example.yaml {args.device_config}")
                return 1
            manager.load_device_config(args.device_config)
        
        # Verify changes config exists
        if not Path(args.changes_config).exists():
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
                print("\n" + "=" * 70)
                print("APPLYING CHANGES")
                print("=" * 70)
                
                result = manager.commit_changes(
                    save_config=args.save,
                    create_backup=not args.no_backup
                )
                
                if result['success']:
                    print("✓ Changes applied successfully!")
                    if result.get('config_saved'):
                        print("✓ Configuration saved to startup-config")
                    elif args.save:
                        print("✗ Warning: Failed to save configuration")
                else:
                    print(f"✗ Failed to apply changes: {result.get('message')}")
                    for item in result.get('results', []):
                        if not item['success']:
                            print(f"  - {item['interface']}: {item.get('error')}")
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
