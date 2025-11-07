"""Backup management for ASA configurations."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from .logger import get_logger

logger = get_logger(__name__)


class BackupManager:
    """Manages configuration backups."""
    
    def __init__(self, backup_dir: str = "backups"):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.current_backup_file: Optional[Path] = None
    
    def create_backup(self, config: str, device_name: str) -> str:
        """
        Create a backup of the current configuration.
        
        Args:
            config: Configuration content to backup
            device_name: Name of the device
            
        Returns:
            Path to the backup file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{device_name}_{timestamp}.cfg"
        backup_path = self.backup_dir / filename
        
        try:
            with open(backup_path, 'w') as f:
                f.write(config)
            
            self.current_backup_file = backup_path
            logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
        
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    def read_backup(self, backup_file: Optional[str] = None) -> str:
        """
        Read a backup file.
        
        Args:
            backup_file: Path to backup file (uses last backup if None)
            
        Returns:
            Backup file content
        """
        if backup_file:
            path = Path(backup_file)
        elif self.current_backup_file:
            path = self.current_backup_file
        else:
            raise ValueError("No backup file specified or available")
        
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read backup {path}: {e}")
            raise
    
    def list_backups(self, device_name: Optional[str] = None) -> list:
        """
        List available backups.
        
        Args:
            device_name: Filter by device name (optional)
            
        Returns:
            List of backup file paths
        """
        pattern = f"{device_name}_*.cfg" if device_name else "*.cfg"
        backups = sorted(self.backup_dir.glob(pattern), reverse=True)
        return [str(b) for b in backups]
