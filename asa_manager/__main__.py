"""
ASA Configuration Manager CLI.

Run the package as a command-line tool:
    python -m asa_manager --help
"""

import argparse
import io
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .config import DeviceConfig
from .manager import ASAManager
from .utils import get_logger, CLIFormatter, format_commit_operation, format_revert_operation, show_operation_result

logger = get_logger(__name__)


def _run_preview_on_device(device_config: DeviceConfig, changes_config_path: str,
                           backup_dir: str, log_dir: str) -> dict:
    """
    Run preview operation on a single device. Thread-safe — each call
    creates its own ASAManager with an independent connection.
    All output is written to a StringIO buffer (never to sys.stdout).

    Returns:
        dict with 'device_name', 'host', 'success', 'output', and optional 'error'
    """
    buf = io.StringIO()
    device_name = device_config.device_name or device_config.host
    try:
        manager = ASAManager(backup_dir=backup_dir, log_dir=log_dir)
        manager.device_config = device_config
        manager.device_configs = [device_config]

        buf.write(f"Connecting to {device_config.host}...\n")
        if not manager.connect():
            buf.write("Failed to connect to device\n")
            return {'device_name': device_name, 'host': device_config.host,
                    'success': False, 'output': buf.getvalue(),
                    'error': 'Connection failed'}

        buf.write("Connected successfully!\n\n")
        try:
            manager.load_changes(changes_config_path)
            buf.write(manager.preview_changes())
            buf.write("\n")
        finally:
            manager.disconnect()

        return {'device_name': device_name, 'host': device_config.host,
                'success': True, 'output': buf.getvalue()}

    except Exception as e:
        logger.exception(f"Error on device {device_name}")
        return {'device_name': device_name, 'host': device_config.host,
                'success': False, 'output': buf.getvalue(),
                'error': str(e)}


def _run_commit_on_device(device_config: DeviceConfig, changes_config_path: str,
                          backup_dir: str, log_dir: str,
                          save_config: bool, no_backup: bool) -> dict:
    """
    Run commit operation on a single device. Thread-safe.
    All output is written to a StringIO buffer (never to sys.stdout).

    Returns:
        dict with 'device_name', 'host', 'success', 'output', and optional 'error'
    """
    buf = io.StringIO()
    device_name = device_config.device_name or device_config.host
    try:
        manager = ASAManager(backup_dir=backup_dir, log_dir=log_dir)
        manager.device_config = device_config
        manager.device_configs = [device_config]

        buf.write(f"⚙ Connecting to {device_config.host}...")
        if not manager.connect():
            buf.write("\n✗ Failed to connect to device\n")
            return {'device_name': device_name, 'host': device_config.host,
                    'success': False, 'output': buf.getvalue(),
                    'error': 'Connection failed'}
        buf.write(" Done!\n")

        try:
            manager.load_changes(changes_config_path)

            # Build commit preview text
            staged = manager.interface_manager.staged_changes
            buf.write("\nChanges to Apply\n")
            buf.write("-" * 16 + "\n")
            for change in staged:
                change_obj = change.get('change', {})
                current_config = change.get('current_config', {})
                if hasattr(change_obj, 'nameif') and change_obj.nameif:
                    current_nameif = current_config.get('nameif', 'none')
                    buf.write(f"  {change['interface']}\n")
                    buf.write(f"    nameif: {current_nameif} → {change_obj.nameif}\n")
                if hasattr(change_obj, 'vlan') and change_obj.vlan:
                    current_vlan = current_config.get('vlan', 'none')
                    buf.write(f"  {change['interface']}\n")
                    buf.write(f"    vlan: {current_vlan} → {change_obj.vlan}\n")
            buf.write("\n")

            buf.write("⚙ Creating configuration backup...")
            result = manager.commit_changes(
                save_config=save_config,
                create_backup=not no_backup
            )
            buf.write(" Done!\n")
            buf.write("⚙ Applying configuration changes... Done!\n")

            if result['success']:
                buf.write("✓ Changes applied successfully!\n")
                if result.get('config_saved'):
                    buf.write("✓ Configuration saved to startup-config\n")
                elif save_config:
                    buf.write("⚠ Failed to save configuration\n")
            else:
                buf.write(f"✗ Failed to apply changes: {result.get('message')}\n")

            return {'device_name': device_name, 'host': device_config.host,
                    'success': result['success'], 'output': buf.getvalue()}
        finally:
            manager.disconnect()

    except Exception as e:
        logger.exception(f"Error on device {device_name}")
        return {'device_name': device_name, 'host': device_config.host,
                'success': False, 'output': buf.getvalue(),
                'error': str(e)}


def _run_revert_on_device(device_config: DeviceConfig,
                          backup_dir: str, log_dir: str) -> dict:
    """
    Run revert operation on a single device. Thread-safe.
    All output is written to a StringIO buffer (never to sys.stdout).

    Returns:
        dict with 'device_name', 'host', 'success', 'output', and optional 'error'
    """
    buf = io.StringIO()
    device_name = device_config.device_name or device_config.host
    try:
        manager = ASAManager(backup_dir=backup_dir, log_dir=log_dir)
        manager.device_config = device_config
        manager.device_configs = [device_config]

        # Check if this device has revertible state
        state = manager.state_manager.load_device_state(device_name)
        if not state:
            buf.write(f"No revertible changes found for {device_name}\n")
            return {'device_name': device_name, 'host': device_config.host,
                    'success': True, 'output': buf.getvalue(),
                    'skipped': True}

        buf.write(f"⚙ Connecting to {device_config.host}...")
        if not manager.connect():
            buf.write("\n✗ Failed to connect to device\n")
            return {'device_name': device_name, 'host': device_config.host,
                    'success': False, 'output': buf.getvalue(),
                    'error': 'Connection failed'}
        buf.write(" Done!\n\n")

        try:
            # Show what will be reverted
            buf.write(f"ℹ Reverting changes applied at: {state.get('timestamp', 'Unknown')}\n")
            if state.get('backup_path'):
                buf.write(f"📁 Backup: {state['backup_path']}\n")
            buf.write("\nChanges to Revert\n")
            buf.write("-" * 17 + "\n")
            for change in state.get('applied_changes', []):
                interface = change['interface']
                original_config = change.get('original_config', {})
                change_data = change.get('change_data', {})
                if change_data.get('nameif'):
                    original_nameif = original_config.get('nameif', 'none')
                    buf.write(f"  {interface}\n")
                    buf.write(f"    nameif: {change_data['nameif']} → {original_nameif}\n")
                if change_data.get('vlan'):
                    original_vlan = original_config.get('vlan', 'none')
                    buf.write(f"  {interface}\n")
                    buf.write(f"    vlan: {change_data['vlan']} → {original_vlan}\n")
            buf.write("\n")

            buf.write("⚙ Reverting configuration changes...")
            result = manager.revert_last_changes()
            buf.write(" Done!\n")

            if result['success']:
                buf.write("✓ Changes reverted successfully!\n")
                if result.get('backup_available'):
                    buf.write(f"ℹ Original backup: {result['backup_available']}\n")
            else:
                buf.write(f"✗ {result.get('message', 'Revert failed')}\n")

            return {'device_name': device_name, 'host': device_config.host,
                    'success': result['success'], 'output': buf.getvalue()}
        finally:
            manager.disconnect()

    except Exception as e:
        logger.exception(f"Error reverting device {device_name}")
        return {'device_name': device_name, 'host': device_config.host,
                'success': False, 'output': buf.getvalue(),
                'error': str(e)}


def _print_device_results(results: list) -> int:
    """
    Print collected per-device results sequentially.

    Returns:
        0 if all succeeded, 1 if any failed
    """
    any_failed = False
    for r in results:
        CLIFormatter.header(f"DEVICE: {r['device_name']} ({r['host']})")
        if r['output']:
            print(r['output'])
        if not r['success']:
            any_failed = True
            CLIFormatter.error(f"Operation failed on {r['device_name']}: {r.get('error', 'unknown error')}")
        print()

    # Summary
    total = len(results)
    succeeded = sum(1 for r in results if r['success'])
    failed = total - succeeded
    print("=" * 70)
    print(f"  SUMMARY: {succeeded}/{total} devices succeeded", end="")
    if failed:
        print(f", {failed} failed")
    else:
        print()
    print("=" * 70)

    return 1 if any_failed else 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='ASA Configuration Manager - Manage Cisco ASA interface configurations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes (all devices in parallel)
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
        # Initialize manager (used for list-backups, revert, and loading configs)
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
        
        # Handle revert command — multi-device parallel revert
        if args.revert:
            if not manager.has_revertible_changes():
                CLIFormatter.warning("No changes to revert. No changes have been applied recently.")
                return 0
            
            if not manager.device_configs:
                if not Path(args.device_config).exists():
                    CLIFormatter.error(f"Device config file not found: {args.device_config}")
                    print("Please create it from the example:")
                    print(f"  cp configs/device_example.yaml {args.device_config}")
                    return 1
                manager.load_device_config(args.device_config)

            # Build a lookup: device_name -> DeviceConfig
            dc_lookup = {dc.device_name: dc for dc in manager.device_configs}

            # Find which devices have revertible state
            states = manager.state_manager.load_all_device_states()
            revert_configs = []
            for state in states:
                dname = state.get('device_name')
                if dname in dc_lookup:
                    revert_configs.append(dc_lookup[dname])
                else:
                    CLIFormatter.warning(
                        f"State exists for '{dname}' but no matching device in config — skipping")

            if not revert_configs:
                CLIFormatter.warning("No matching devices found for revert.")
                return 0

            num = len(revert_configs)
            CLIFormatter.info(f"Reverting changes on {num} device(s)...")
            print()

            if num == 1:
                r = _run_revert_on_device(revert_configs[0],
                                          args.backup_dir, args.log_dir)
                return _print_device_results([r])

            results = []
            with ThreadPoolExecutor(max_workers=num) as executor:
                futs = {executor.submit(_run_revert_on_device, dc,
                                        args.backup_dir, args.log_dir): dc
                        for dc in revert_configs}
                for future in as_completed(futs):
                    results.append(future.result())

            results.sort(key=lambda r: r['device_name'])
            return _print_device_results(results)

        # ----- Preview / Commit: multi-device parallel execution -----

        # Load device configs
        if not manager.device_configs:
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
        
        device_configs = manager.device_configs
        num_devices = len(device_configs)

        CLIFormatter.info(f"Found {num_devices} device(s) in configuration")

        # Single device — run directly (no thread pool overhead)
        if num_devices == 1:
            dc = device_configs[0]
            if args.preview:
                r = _run_preview_on_device(dc, args.changes_config,
                                           args.backup_dir, args.log_dir)
            else:
                r = _run_commit_on_device(dc, args.changes_config,
                                          args.backup_dir, args.log_dir,
                                          args.save, args.no_backup)
            return _print_device_results([r])

        # Multiple devices — run in parallel
        CLIFormatter.info(f"Running operations in parallel across {num_devices} devices...")
        print()

        results = []
        with ThreadPoolExecutor(max_workers=num_devices) as executor:
            future_to_device = {}
            for dc in device_configs:
                if args.preview:
                    fut = executor.submit(
                        _run_preview_on_device, dc, args.changes_config,
                        args.backup_dir, args.log_dir)
                else:
                    fut = executor.submit(
                        _run_commit_on_device, dc, args.changes_config,
                        args.backup_dir, args.log_dir,
                        args.save, args.no_backup)
                future_to_device[fut] = dc

            for future in as_completed(future_to_device):
                results.append(future.result())

        # Sort results by device name for consistent output order
        results.sort(key=lambda r: r['device_name'])
        return _print_device_results(results)
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        logger.exception("CLI error")
        return 1


if __name__ == '__main__':
    sys.exit(main())
