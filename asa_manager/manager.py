"""Main ASA Manager module."""

from typing import Optional
from pathlib import Path

from .config import DeviceConfig, ChangeConfig
from .connection import ASAConnection
from .operations import InterfaceManager
from .utils import setup_logger, BackupManager, get_logger

logger = get_logger(__name__)


class ASAManager:
    """
    Main ASA configuration manager.
    
    Provides a high-level interface for managing ASA interface configurations
    with preview, commit, and revert capabilities.
    """
    
    def __init__(self, device_config: Optional[str] = None, 
                 backup_dir: str = "backups",
                 log_dir: str = "logs"):
        """
        Initialize ASA Manager.
        
        Args:
            device_config: Path to device configuration YAML file
            backup_dir: Directory for configuration backups
            log_dir: Directory for log files
        """
        # Setup logging
        setup_logger('asa_manager', log_dir=log_dir)
        
        # Initialize components
        self.device_config: Optional[DeviceConfig] = None
        self.connection: Optional[ASAConnection] = None
        self.interface_manager: Optional[InterfaceManager] = None
        self.backup_manager = BackupManager(backup_dir)
        self.change_config: Optional[ChangeConfig] = None
        
        # Load device config if provided
        if device_config:
            self.load_device_config(device_config)
        
        logger.info("ASA Manager initialized")
    
    def load_device_config(self, config_path: str):
        """
        Load device configuration from YAML file.
        
        Args:
            config_path: Path to device YAML configuration
        """
        logger.info(f"Loading device config from {config_path}")
        self.device_config = DeviceConfig.from_yaml(config_path)
        logger.info(f"Device config loaded for {self.device_config.host}")
    
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
    
    def revert_changes(self) -> dict:
        """
        Revert previously applied changes.
        
        Returns:
            Result dictionary with success status
            
        Raises:
            ValueError: If not connected or no changes to revert
        """
        if not self.interface_manager:
            raise ValueError("Not connected to device. Call connect() first.")
        
        if not self.interface_manager.staged_changes:
            raise ValueError("No changes to revert.")
        
        return self.interface_manager.revert_changes()
    
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
