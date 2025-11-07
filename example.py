#!/usr/bin/env python3
"""
Example usage of ASA Configuration Manager.

This script demonstrates how to use the library to manage ASA interface configurations.
"""

from asa_manager import ASAManager

def main():
    """Main example function."""
    
    # Initialize the manager with device configuration
    manager = ASAManager(
        device_config='configs/device.yaml',
        backup_dir='backups',
        log_dir='logs'
    )
    
    try:
        # Connect to the ASA device
        print("Connecting to ASA device...")
        if not manager.connect():
            print("Failed to connect to device")
            return
        
        print("Connected successfully!\n")
        
        # Load the changes from configuration file
        print("Loading interface changes...")
        manager.load_changes('configs/changes.yaml')
        print("Changes loaded!\n")
        
        # Preview the changes before applying
        print("=" * 70)
        print("PREVIEW OF CHANGES")
        print("=" * 70)
        preview = manager.preview_changes()
        print(preview)
        print()
        
        # Ask for confirmation
        confirm = input("Do you want to apply these changes? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            # Apply the changes
            print("\nApplying changes...")
            result = manager.commit_changes(save_config=False, create_backup=True)
            
            if result['success']:
                print("✓ Changes applied successfully!")
                
                # Check if user wants to save
                save = input("\nDo you want to save the configuration? (yes/no): ").strip().lower()
                if save == 'yes':
                    manager.connection.save_config()
                    print("✓ Configuration saved!")
                else:
                    print("Configuration NOT saved (will be lost on reload)")
                
                # Ask about revert
                revert = input("\nDo you want to revert the changes? (yes/no): ").strip().lower()
                if revert == 'yes':
                    print("\nReverting changes...")
                    revert_result = manager.revert_changes()
                    if revert_result['success']:
                        print("✓ Changes reverted successfully!")
                    else:
                        print("✗ Revert failed:", revert_result.get('message'))
            else:
                print("✗ Failed to apply changes:", result.get('message'))
                print("\nDetails:")
                for item in result.get('results', []):
                    if not item['success']:
                        print(f"  - {item['interface']}: {item.get('error')}")
        else:
            print("Changes cancelled.")
        
        # Show available backups
        print("\n" + "=" * 70)
        print("AVAILABLE BACKUPS")
        print("=" * 70)
        backups = manager.list_backups()
        if backups:
            for backup in backups[:5]:  # Show last 5 backups
                print(f"  - {backup}")
        else:
            print("  No backups available")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always disconnect
        print("\nDisconnecting...")
        manager.disconnect()
        print("Done!")


def example_with_context_manager():
    """Example using context manager for automatic connection handling."""
    
    # Using context manager - automatically connects and disconnects
    with ASAManager(device_config='configs/device.yaml') as manager:
        # Load and preview changes
        manager.load_changes('configs/changes.yaml')
        print(manager.preview_changes())
        
        # Apply changes
        result = manager.commit_changes(create_backup=True)
        if result['success']:
            print("Changes applied!")


if __name__ == '__main__':
    main()
    
    # Uncomment to try context manager approach:
    # example_with_context_manager()
