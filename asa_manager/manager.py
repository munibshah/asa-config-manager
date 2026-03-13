"""Main ASA Manager module."""

from typing import Optional, List
from pathlib import Path

from .config import DeviceConfig, ChangeConfig
from .connection import ASAConnection
from .operations import InterfaceManager
from .utils import setup_logger, BackupManager, StateManager, get_logger

logger = get_logger(__name__)


class ASAManager:
    """
    Main ASA configuration manager.
    
    Provides a high-level interface for managing ASA interface configurations
    with preview, commit, and revert capabilities.
    """
    
    def __init__(self, device_config: Optional[str] = None, 
                 backup_dir: str = "backups",
                 log_dir: str = "logs",
                 state_dir: str = "state"):
        """
        Initialize ASA Manager.
        
        Args:
            device_config: Path to device configuration YAML file
            backup_dir: Directory for configuration backups
            log_dir: Directory for log files
            state_dir: Directory for state persistence
        """
        # Setup logging
        setup_logger('asa_manager', log_dir=log_dir)
        
        # Initialize components
        self.device_config: Optional[DeviceConfig] = None
        self.device_configs: List[DeviceConfig] = []
        self.connection: Optional[ASAConnection] = None
        self.interface_manager: Optional[InterfaceManager] = None
        self.backup_manager = BackupManager(backup_dir)
        self.state_manager = StateManager(state_dir)
        self.change_config: Optional[ChangeConfig] = None
        
        # Load device config if provided
        if device_config:
            self.load_device_config(device_config)
        
        logger.info("ASA Manager initialized")
    
    def load_device_config(self, config_path: str):
        """
        Load device configuration(s) from YAML file.
        
        Args:
            config_path: Path to device YAML configuration
        """
        logger.info(f"Loading device config from {config_path}")
        self.device_configs = DeviceConfig.from_yaml_multi(config_path)
        # Set the first device as the active device for backward compat
        self.device_config = self.device_configs[0]
        logger.info(f"Loaded {len(self.device_configs)} device(s)")
        for dc in self.device_configs:
            logger.info(f"  Device: {dc.device_name} ({dc.host})")
    
    def load_changes(self, config_path: str):
        """
        Load interface changes from YAML file.
        
        Args:
            config_path: Path to changes YAML configuration
        """
        logger.info(f"Loading changes from {config_path}")
        self.change_config = ChangeConfig.from_yaml(config_path)
        logger.info(f"Loaded {len(self.change_config)} changes")
        
        # Stage all changes
        if self.interface_manager:
            for change in self.change_config.changes:
                self.interface_manager.stage_change(change)
    
    def connect(self) -> bool:
        """
        Connect to ASA device.
        
        Returns:
            True if connection successful
            
        Raises:
            ValueError: If device config not loaded
        """
        if not self.device_config:
            raise ValueError("Device config not loaded. Call load_device_config() first.")
        
        self.connection = ASAConnection(self.device_config)
        success = self.connection.connect()
        
        if success:
            self.interface_manager = InterfaceManager(self.connection)
            
            # Re-stage changes if they were loaded before connection
            if self.change_config:
                for change in self.change_config.changes:
                    self.interface_manager.stage_change(change)
        
        return success
    
    def disconnect(self):
        """Disconnect from ASA device."""
        if self.connection:
            self.connection.disconnect()
            self.connection = None
            self.interface_manager = None
    
    def preview_changes(self) -> str:
        """
        Preview staged changes.
        
        Returns:
            Formatted preview string
            
        Raises:
            ValueError: If not connected or no changes loaded
        """
        if not self.interface_manager:
            raise ValueError("Not connected to device. Call connect() first.")
        
        return self.interface_manager.preview_changes()
    
    def commit_changes(self, save_config: bool = False, 
                      create_backup: bool = True) -> dict:
        """
        Apply staged changes to the device.
        
        Args:
            save_config: Whether to save config to startup-config
            create_backup: Whether to create config backup before changes
            
        Returns:
            Result dictionary with success status
            
        Raises:
            ValueError: If not connected or no changes staged
        """
        if not self.interface_manager:
            raise ValueError("Not connected to device. Call connect() first.")
        
        if not self.interface_manager.staged_changes:
            raise ValueError("No changes staged. Call load_changes() first.")
        
        backup_path = None
        
        # Create backup if requested
        if create_backup and self.connection:
            try:
                logger.info("Creating configuration backup...")
                running_config = self.connection.get_running_config()
                backup_path = self.backup_manager.create_backup(
                    running_config,
                    self.device_config.device_name
                )
                logger.info(f"Backup created: {backup_path}")
            except Exception as e:
                logger.error(f"Failed to create backup: {e}")
                return {
                    'success': False,
                    'message': f'Backup failed: {e}'
                }
        
        # Apply changes
        result = self.interface_manager.commit_changes()
        
        # Save state for revert capability if changes were successful
        if result['success']:
            try:
                self.state_manager.save_applied_changes(
                    self.device_config.device_name,
                    self.interface_manager.staged_changes,
                    backup_path
                )
                logger.info("Saved applied changes state for revert capability")
            except Exception as e:
                logger.warning(f"Failed to save state for revert: {e}")
        
        # Save config if requested and changes were successful
        if save_config and result['success'] and self.connection:
            try:
                self.connection.save_config()
                result['config_saved'] = True
            except Exception as e:
                logger.error(f"Failed to save config: {e}")
                result['config_saved'] = False
                result['save_error'] = str(e)
        
        return result
    
    def revert_last_changes(self) -> dict:
        """
        Revert the last applied changes using saved state.
        
        Returns:
            Result dictionary with success status
            
        Raises:
            ValueError: If not connected or no changes to revert
        """
        if not self.connection:
            raise ValueError("Not connected to device. Call connect() first.")
        
        # Load state for THIS specific device
        state = self.state_manager.load_device_state(self.device_config.device_name)
        if not state:
            return {
                'success': False,
                'message': f'No revertible changes found for device {self.device_config.device_name}.'
            }
        
        logger.info(f"Reverting changes on {self.device_config.device_name}...")
        
        results = []
        all_success = True
        
        # Apply reverse commands in reverse order
        for change in reversed(state['applied_changes']):
            interface = change['interface']
            reverse_commands = change['reverse_commands']
            
            try:
                logger.info(f"Reverting changes to {interface}...")
                output = self.connection.send_config_commands(reverse_commands)
                
                results.append({
                    'interface': interface,
                    'success': True,
                    'output': output
                })
                logger.info(f"Successfully reverted changes to {interface}")
                
            except Exception as e:
                all_success = False
                results.append({
                    'interface': interface,
                    'success': False,
                    'error': str(e)
                })
                logger.error(f"Failed to revert changes to {interface}: {e}")
        
        # Clear state for THIS device only if revert was successful
        if all_success:
            self.state_manager.clear_device_state(self.device_config.device_name)
            logger.info(f"Cleared revert state for {self.device_config.device_name}")
        
        return {
            'success': all_success,
            'results': results,
            'message': 'All changes reverted' if all_success else 'Some reverts failed',
            'reverted_at': state.get('timestamp'),
            'backup_available': state.get('backup_path')
        }
    
    def has_revertible_changes(self) -> bool:
        """
        Check if there are changes that can be reverted.
        
        Returns:
            True if there are revertible changes
        """
        return self.state_manager.has_revertible_changes()
    
    def get_interface_config(self, interface: str) -> str:
        """
        Get current configuration for an interface.
        
        Args:
            interface: Interface name
            
        Returns:
            Interface configuration text
        """
        if not self.connection:
            raise ValueError("Not connected to device. Call connect() first.")
        
        return self.connection.get_interface_config(interface)
    
    def list_backups(self) -> list:
        """
        List available configuration backups.
        
        Returns:
            List of backup file paths
        """
        device_name = self.device_config.device_name if self.device_config else None
        return self.backup_manager.list_backups(device_name)
    
    def __enter__(self):
        """Context manager entry."""
        if self.device_config and not self.connection:
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
