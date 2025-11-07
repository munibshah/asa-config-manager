"""State management for tracking applied changes."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .logger import get_logger

logger = get_logger(__name__)


class StateManager:
    """Manages state persistence for revert functionality."""
    
    def __init__(self, state_dir: str = "state"):
        """
        Initialize state manager.
        
        Args:
            state_dir: Directory to store state files
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "last_applied_changes.json"
    
    def save_applied_changes(self, device_name: str, changes: List[Dict], 
                           backup_path: Optional[str] = None) -> None:
        """
        Save information about applied changes for revert capability.
        
        Args:
            device_name: Name of the device
            changes: List of applied changes with their revert commands
            backup_path: Path to backup file created before changes
        """
        state = {
            "timestamp": datetime.now().isoformat(),
            "device_name": device_name,
            "backup_path": backup_path,
            "applied_changes": []
        }
        
        # Store essential info for each change
        for change in changes:
            change_obj = change.get("change")
            
            # Serialize the InterfaceChange object properly
            change_data = {}
            if change_obj:
                change_data = {
                    "interface": change_obj.interface,
                    "vlan": change_obj.vlan,
                    "nameif": change_obj.nameif
                }
            
            state["applied_changes"].append({
                "interface": change["interface"],
                "original_config": change.get("current_config", {}),
                "forward_commands": change.get("forward_commands", []),
                "reverse_commands": change.get("reverse_commands", []),
                "change_data": change_data
            })
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Saved applied changes state to {self.state_file}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            raise
    
    def load_last_applied_changes(self) -> Optional[Dict[str, Any]]:
        """
        Load information about the last applied changes.
        
        Returns:
            Dictionary with last applied changes info or None if no state exists
        """
        try:
            if not self.state_file.exists():
                return None
            
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            logger.info("Loaded last applied changes state")
            return state
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None
    
    def clear_state(self) -> None:
        """Clear the saved state after successful revert."""
        try:
            if self.state_file.exists():
                self.state_file.unlink()
                logger.info("Cleared applied changes state")
        except Exception as e:
            logger.error(f"Failed to clear state: {e}")
    
    def has_revertible_changes(self) -> bool:
        """
        Check if there are revertible changes available.
        
        Returns:
            True if there are changes that can be reverted
        """
        state = self.load_last_applied_changes()
        return state is not None and len(state.get("applied_changes", [])) > 0