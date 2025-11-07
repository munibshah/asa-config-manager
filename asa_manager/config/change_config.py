"""Change configuration model."""

from typing import Dict, Any, List, Optional
from .loader import ConfigLoader


class InterfaceChange:
    """Represents a single interface change."""
    
    def __init__(self, interface: str, vlan: Optional[int] = None, 
                 nameif: Optional[str] = None):
        """
        Initialize interface change.
        
        Args:
            interface: Interface name (e.g., 'GigabitEthernet0/1')
            vlan: New VLAN ID
            nameif: New nameif value
        """
        self.interface = interface
        self.vlan = vlan
        self.nameif = nameif
    
    def has_changes(self) -> bool:
        """Check if there are any changes specified."""
        return self.vlan is not None or self.nameif is not None
    
    def __repr__(self):
        changes = []
        if self.vlan is not None:
            changes.append(f"vlan={self.vlan}")
        if self.nameif is not None:
            changes.append(f"nameif={self.nameif}")
        return f"InterfaceChange({self.interface}: {', '.join(changes)})"


class ChangeConfig:
    """Represents interface change configuration."""
    
    def __init__(self):
        """Initialize change configuration."""
        self.changes: List[InterfaceChange] = []
    
    def add_change(self, interface: str, vlan: Optional[int] = None,
                   nameif: Optional[str] = None):
        """
        Add an interface change.
        
        Args:
            interface: Interface name
            vlan: New VLAN ID
            nameif: New nameif value
        """
        change = InterfaceChange(interface, vlan, nameif)
        if change.has_changes():
            self.changes.append(change)
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'ChangeConfig':
        """
        Load change configuration from YAML file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            ChangeConfig instance
        """
        config_dict = ConfigLoader.load(config_path)
        change_config = cls()
        
        # Support both 'interfaces' and 'changes' keys
        interfaces = config_dict.get('interfaces', config_dict.get('changes', []))
        
        for item in interfaces:
            interface = item.get('interface')
            if not interface:
                continue
            
            vlan = item.get('vlan')
            nameif = item.get('nameif')
            
            change_config.add_change(interface, vlan, nameif)
        
        return change_config
    
    def get_interfaces(self) -> List[str]:
        """Get list of interfaces to be changed."""
        return [change.interface for change in self.changes]
    
    def __len__(self):
        """Return number of changes."""
        return len(self.changes)
    
    def __repr__(self):
        return f"ChangeConfig({len(self.changes)} changes)"
