"""Helper utilities for ASA Manager."""

import re
from datetime import datetime
from typing import Dict, Optional


def generate_timestamp() -> str:
    """Generate a timestamp string."""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def parse_interface_config(config_block: str) -> Dict[str, Optional[str]]:
    """
    Parse interface configuration block.
    
    Args:
        config_block: Interface configuration text
        
    Returns:
        Dictionary with interface parameters
    """
    result = {
        'name': None,
        'nameif': None,
        'vlan': None,
        'security_level': None,
        'ip_address': None,
    }
    
    # Extract interface name
    name_match = re.search(r'interface\s+(\S+)', config_block)
    if name_match:
        result['name'] = name_match.group(1)
    
    # Extract nameif
    nameif_match = re.search(r'nameif\s+(\S+)', config_block)
    if nameif_match:
        result['nameif'] = nameif_match.group(1)
    
    # Extract VLAN
    vlan_match = re.search(r'vlan\s+(\d+)', config_block)
    if vlan_match:
        result['vlan'] = vlan_match.group(1)
    
    # Extract security level
    sec_match = re.search(r'security-level\s+(\d+)', config_block)
    if sec_match:
        result['security_level'] = sec_match.group(1)
    
    # Extract IP address
    ip_match = re.search(r'ip\s+address\s+(\S+\s+\S+)', config_block)
    if ip_match:
        result['ip_address'] = ip_match.group(1)
    
    return result


def clean_output(output: str) -> str:
    """
    Clean command output from ASA device.
    
    Args:
        output: Raw output from device
        
    Returns:
        Cleaned output
    """
    # Remove ANSI escape codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    cleaned = ansi_escape.sub('', output)
    
    # Remove common ASA prompts
    cleaned = re.sub(r'[\r\n]+[^\r\n]*#\s*$', '', cleaned)
    
    return cleaned.strip()


def format_interface_name(interface: str) -> str:
    """
    Normalize interface name format.
    
    Args:
        interface: Interface name
        
    Returns:
        Normalized interface name
    """
    # Handle common abbreviations
    replacements = {
        'Gi': 'GigabitEthernet',
        'gi': 'GigabitEthernet',
        'Te': 'TenGigabitEthernet',
        'te': 'TenGigabitEthernet',
    }
    
    for abbr, full in replacements.items():
        if interface.startswith(abbr):
            interface = interface.replace(abbr, full, 1)
            break
    
    return interface
