"""Interface configuration manager."""

from typing import List, Dict, Optional, Tuple
import re

from ..connection.asa_connection import ASAConnection
from ..config.change_config import InterfaceChange
from ..utils.logger import get_logger
from ..utils.helpers import parse_interface_config
from ..validators.interface_validator import InterfaceValidator

logger = get_logger(__name__)


class InterfaceManager:
    """Manages interface configuration changes."""
    
    def __init__(self, connection: ASAConnection):
        """
        Initialize interface manager.
        
        Args:
            connection: ASA connection instance
        """
        self.connection = connection
        self.staged_changes: List[Dict] = []
        self.current_configs: Dict[str, Dict] = {}
    
    def stage_change(self, change: InterfaceChange):
        """
        Stage an interface change for preview.
        
        Args:
            change: InterfaceChange object
        """
        # Get current interface config
        try:
            config_output = self.connection.get_interface_config(change.interface)
            current_config = parse_interface_config(config_output)
            self.current_configs[change.interface] = current_config
        except Exception as e:
            logger.warning(f"Could not get config for {change.interface}: {e}")
            current_config = {}
        
        # Generate forward and reverse commands
        forward_cmds = self._generate_forward_commands(change, current_config)
        reverse_cmds = self._generate_reverse_commands(change, current_config)
        
        staged = {
            'interface': change.interface,
            'change': change,
            'current_config': current_config,
            'forward_commands': forward_cmds,
            'reverse_commands': reverse_cmds,
        }
        
        self.staged_changes.append(staged)
        logger.info(f"Staged change for {change.interface}")
    
    def _generate_forward_commands(self, change: InterfaceChange, 
                                   current: Dict) -> List[str]:
        """
        Generate commands to apply the change.
        
        Args:
            change: InterfaceChange object
            current: Current interface configuration
            
        Returns:
            List of commands to execute
        """
        commands = [f'interface {change.interface}']
        
        if change.vlan is not None:
            commands.append(f'vlan {change.vlan}')
        
        if change.nameif is not None:
            commands.append(f'nameif {change.nameif}')
        
        return commands
    
    def _generate_reverse_commands(self, change: InterfaceChange,
                                   current: Dict) -> List[str]:
        """
        Generate commands to revert the change.
        
        Args:
            change: InterfaceChange object
            current: Current interface configuration
            
        Returns:
            List of commands to revert
        """
        commands = [f'interface {change.interface}']
        
        # Revert VLAN if changed
        if change.vlan is not None and current.get('vlan'):
            commands.append(f'vlan {current["vlan"]}')
        elif change.vlan is not None and not current.get('vlan'):
            # If no VLAN was set before, remove it
            commands.append('no vlan')
        
        # Revert nameif if changed
        if change.nameif is not None and current.get('nameif'):
            commands.append(f'nameif {current["nameif"]}')
        elif change.nameif is not None and not current.get('nameif'):
            # If no nameif was set before, remove it
            commands.append('no nameif')
        
        return commands
    
    def preview_changes(self) -> str:
        """
        Generate a preview of staged changes.
        
        Returns:
            Formatted preview string
        """
        if not self.staged_changes:
            return "No changes staged."
        
        preview_lines = ["=" * 70, "STAGED CHANGES PREVIEW", "=" * 70, ""]
        
        for idx, staged in enumerate(self.staged_changes, 1):
            interface = staged['interface']
            change = staged['change']
            current = staged['current_config']
            
            preview_lines.append(f"Change {idx}: {interface}")
            preview_lines.append("-" * 70)
            
            # Show current values
            preview_lines.append("Current Configuration:")
            if current.get('vlan'):
                preview_lines.append(f"  VLAN: {current['vlan']}")
            if current.get('nameif'):
                preview_lines.append(f"  Nameif: {current['nameif']}")
            if not current.get('vlan') and not current.get('nameif'):
                preview_lines.append("  (No VLAN or nameif configured)")
            
            # Show new values
            preview_lines.append("\nProposed Changes:")
            if change.vlan is not None:
                preview_lines.append(f"  VLAN: {current.get('vlan', 'none')} → {change.vlan}")
            if change.nameif is not None:
                preview_lines.append(f"  Nameif: {current.get('nameif', 'none')} → {change.nameif}")
            
            # Show commands
            preview_lines.append("\nCommands to Apply:")
            for cmd in staged['forward_commands']:
                preview_lines.append(f"  {cmd}")
            
            preview_lines.append("\nCommands to Revert:")
            for cmd in staged['reverse_commands']:
                preview_lines.append(f"  {cmd}")
            
            preview_lines.append("")
        
        preview_lines.append("=" * 70)
        return "\n".join(preview_lines)
    
    def commit_changes(self) -> Dict[str, any]:
        """
        Apply all staged changes.
        
        Returns:
            Result dictionary with success status and details
        """
        if not self.staged_changes:
            return {'success': False, 'message': 'No changes to commit'}
        
        results = []
        all_success = True
        
        for staged in self.staged_changes:
            interface = staged['interface']
            commands = staged['forward_commands']
            
            try:
                logger.info(f"Applying changes to {interface}...")
                output = self.connection.send_config_commands(commands)
                
                results.append({
                    'interface': interface,
                    'success': True,
                    'output': output
                })
                logger.info(f"Successfully applied changes to {interface}")
                
            except Exception as e:
                all_success = False
                results.append({
                    'interface': interface,
                    'success': False,
                    'error': str(e)
                })
                logger.error(f"Failed to apply changes to {interface}: {e}")
        
        return {
            'success': all_success,
            'results': results,
            'message': 'All changes applied' if all_success else 'Some changes failed'
        }
    
    def revert_changes(self) -> Dict[str, any]:
        """
        Revert all staged changes using reverse commands.
        
        Returns:
            Result dictionary with success status and details
        """
        if not self.staged_changes:
            return {'success': False, 'message': 'No changes to revert'}
        
        results = []
        all_success = True
        
        # Revert in reverse order
        for staged in reversed(self.staged_changes):
            interface = staged['interface']
            commands = staged['reverse_commands']
            
            try:
                logger.info(f"Reverting changes to {interface}...")
                output = self.connection.send_config_commands(commands)
                
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
        
        return {
            'success': all_success,
            'results': results,
            'message': 'All changes reverted' if all_success else 'Some reverts failed'
        }
    
    def clear_staged_changes(self):
        """Clear all staged changes."""
        self.staged_changes.clear()
        self.current_configs.clear()
        logger.info("Cleared all staged changes")
