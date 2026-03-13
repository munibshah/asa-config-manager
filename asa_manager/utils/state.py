"""State management for tracking applied changes."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .logger import get_logger

logger = get_logger(__name__)


class StateManager:
    """Manages state persistence for revert functionality.
    
    State is stored per-device so that parallel commits to multiple
    devices never overwrite each other.  Each device gets its own
    file: ``<state_dir>/<device_name>.json``.
    
    The legacy ``last_applied_changes.json`` single-file format is
    still read (and migrated) for backward compatibility.
    """
    
    def __init__(self, state_dir: str = "state"):
        """
        Initialize state manager.
        
        Args:
            state_dir: Directory to store state files
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        # Legacy single-device file (kept for backward compat reads)
        self._legacy_file = self.state_dir / "last_applied_changes.json"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _device_state_file(self, device_name: str) -> Path:
        """Return the per-device state file path."""
        safe_name = device_name.replace("/", "_").replace("\\", "_")
        return self.state_dir / f"{safe_name}.json"

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

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
        
        for change in changes:
            change_obj = change.get("change")
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
            state_file = self._device_state_file(device_name)
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Saved applied changes state to {state_file}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            raise

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def load_device_state(self, device_name: str) -> Optional[Dict[str, Any]]:
        """
        Load state for a specific device.
        
        Falls back to the legacy single-file format if the per-device
        file does not exist but the legacy file references this device.
        
        Returns:
            State dict or None
        """
        state_file = self._device_state_file(device_name)
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                logger.info(f"Loaded state for device {device_name}")
                return state
            except Exception as e:
                logger.error(f"Failed to load state for {device_name}: {e}")
                return None

        # Fallback: legacy single file
        return self._load_legacy_if_matches(device_name)

    def load_all_device_states(self) -> List[Dict[str, Any]]:
        """
        Load state for ALL devices that have revertible changes.
        
        Returns:
            List of state dicts (one per device)
        """
        states: List[Dict[str, Any]] = []
        seen_devices: set = set()

        # Per-device files
        for f in sorted(self.state_dir.glob("*.json")):
            if f.name == "last_applied_changes.json":
                continue
            try:
                with open(f, 'r') as fh:
                    state = json.load(fh)
                device = state.get("device_name", f.stem)
                if device not in seen_devices:
                    seen_devices.add(device)
                    states.append(state)
            except Exception as e:
                logger.warning(f"Skipping corrupt state file {f}: {e}")

        # Legacy fallback
        if not states and self._legacy_file.exists():
            try:
                with open(self._legacy_file, 'r') as fh:
                    state = json.load(fh)
                if state and state.get("applied_changes"):
                    states.append(state)
            except Exception:
                pass

        return states

    def load_last_applied_changes(self) -> Optional[Dict[str, Any]]:
        """Backward-compatible: return the first available state."""
        states = self.load_all_device_states()
        return states[0] if states else None

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def clear_device_state(self, device_name: str) -> None:
        """Clear state for a specific device after successful revert."""
        state_file = self._device_state_file(device_name)
        try:
            if state_file.exists():
                state_file.unlink()
                logger.info(f"Cleared state for device {device_name}")
        except Exception as e:
            logger.error(f"Failed to clear state for {device_name}: {e}")

    def clear_state(self) -> None:
        """Clear ALL state (legacy compat + per-device files)."""
        for f in self.state_dir.glob("*.json"):
            try:
                f.unlink()
                logger.info(f"Cleared state file {f}")
            except Exception as e:
                logger.error(f"Failed to clear state file {f}: {e}")

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def has_revertible_changes(self) -> bool:
        """Check if there are revertible changes for any device."""
        return len(self.load_all_device_states()) > 0

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _load_legacy_if_matches(self, device_name: str) -> Optional[Dict[str, Any]]:
        """Load legacy file only if it matches the requested device."""
        if not self._legacy_file.exists():
            return None
        try:
            with open(self._legacy_file, 'r') as f:
                state = json.load(f)
            if state.get("device_name") == device_name:
                logger.info(f"Loaded legacy state for {device_name}")
                return state
        except Exception:
            pass
        return None