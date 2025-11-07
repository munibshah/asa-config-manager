"""Interface configuration validator."""

import re
from typing import Dict, List, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class InterfaceValidator:
    """Validates interface configurations."""
    
    @staticmethod
    def validate_interface_name(interface: str) -> bool:
        """
        Validate interface name format.
        
        Args:
            interface: Interface name
            
        Returns:
            True if valid
        """
        # Common ASA interface patterns
        patterns = [
            r'^GigabitEthernet\d+/\d+$',
            r'^TenGigabitEthernet\d+/\d+$',
            r'^Management\d+/\d+$',
            r'^Port-channel\d+$',
            r'^Vlan\d+$',
        ]
        
        for pattern in patterns:
            if re.match(pattern, interface, re.IGNORECASE):
                return True
        
        logger.warning(f"Invalid interface name format: {interface}")
        return False
    
    @staticmethod
    def validate_vlan_id(vlan: int) -> bool:
        """
        Validate VLAN ID.
        
        Args:
            vlan: VLAN ID
            
        Returns:
            True if valid (1-4094)
        """
        if 1 <= vlan <= 4094:
            return True
        
        logger.warning(f"Invalid VLAN ID: {vlan} (must be 1-4094)")
        return False
    
    @staticmethod
    def validate_nameif(nameif: str) -> bool:
        """
        Validate nameif value.
        
        Args:
            nameif: Nameif string
            
        Returns:
            True if valid
        """
        # Nameif must start with letter, alphanumeric + hyphen/underscore
        # Max 48 chars
        if not nameif:
            return False
        
        if len(nameif) > 48:
            logger.warning(f"Nameif too long: {nameif} (max 48 chars)")
            return False
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', nameif):
            logger.warning(f"Invalid nameif format: {nameif}")
            return False
        
        return True
    
    @staticmethod
    def validate_changes(changes: List[Dict]) -> List[str]:
        """
        Validate a list of interface changes.
        
        Args:
            changes: List of change dictionaries
            
        Returns:
            List of validation error messages (empty if all valid)
        """
        errors = []
        
        for idx, change in enumerate(changes):
            interface = change.get('interface')
            vlan = change.get('vlan')
            nameif = change.get('nameif')
            
            if not interface:
                errors.append(f"Change {idx}: Missing interface name")
                continue
            
            if not InterfaceValidator.validate_interface_name(interface):
                errors.append(f"Change {idx}: Invalid interface name '{interface}'")
            
            if vlan is not None:
                try:
                    vlan_int = int(vlan)
                    if not InterfaceValidator.validate_vlan_id(vlan_int):
                        errors.append(f"Change {idx}: Invalid VLAN ID {vlan}")
                except (ValueError, TypeError):
                    errors.append(f"Change {idx}: VLAN must be a number")
            
            if nameif is not None:
                if not InterfaceValidator.validate_nameif(str(nameif)):
                    errors.append(f"Change {idx}: Invalid nameif '{nameif}'")
            
            if vlan is None and nameif is None:
                errors.append(f"Change {idx}: No changes specified for {interface}")
        
        return errors
