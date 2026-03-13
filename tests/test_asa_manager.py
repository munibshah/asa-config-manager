"""Unit tests for ASA Manager."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

from asa_manager import ASAManager
from asa_manager.config import DeviceConfig, ChangeConfig, InterfaceChange
from asa_manager.connection import ASAConnection
from asa_manager.operations import InterfaceManager
from asa_manager.validators import InterfaceValidator


class TestDeviceConfig(unittest.TestCase):
    """Test DeviceConfig class."""
    
    def test_device_config_initialization(self):
        """Test device config initialization."""
        config_dict = {
            'host': '192.168.1.1',
            'username': 'admin',
            'password': 'password',
            'device_type': 'cisco_asa',
            'port': 22,
            'device_name': 'test-asa'
        }
        
        device_config = DeviceConfig(config_dict)
        self.assertEqual(device_config.host, '192.168.1.1')
        self.assertEqual(device_config.username, 'admin')
        self.assertEqual(device_config.device_type, 'cisco_asa')
        self.assertEqual(device_config.port, 22)
    
    def test_to_netmiko_dict(self):
        """Test conversion to Netmiko dictionary."""
        config_dict = {
            'host': '192.168.1.1',
            'username': 'admin',
            'password': 'password',
            'device_type': 'cisco_asa',
            'secret': 'enable_password'
        }
        
        device_config = DeviceConfig(config_dict)
        netmiko_dict = device_config.to_netmiko_dict()
        
        self.assertIn('host', netmiko_dict)
        self.assertIn('username', netmiko_dict)
        self.assertIn('password', netmiko_dict)
        self.assertIn('secret', netmiko_dict)


class TestInterfaceChange(unittest.TestCase):
    """Test InterfaceChange class."""
    
    def test_interface_change_creation(self):
        """Test creating an interface change."""
        change = InterfaceChange('GigabitEthernet0/1', vlan=100, nameif='inside')
        
        self.assertEqual(change.interface, 'GigabitEthernet0/1')
        self.assertEqual(change.vlan, 100)
        self.assertEqual(change.nameif, 'inside')
        self.assertTrue(change.has_changes())
    
    def test_no_changes(self):
        """Test interface change with no actual changes."""
        change = InterfaceChange('GigabitEthernet0/1')
        self.assertFalse(change.has_changes())


class TestChangeConfig(unittest.TestCase):
    """Test ChangeConfig class."""
    
    def test_add_change(self):
        """Test adding changes to config."""
        config = ChangeConfig()
        config.add_change('GigabitEthernet0/1', vlan=100, nameif='inside')
        
        self.assertEqual(len(config), 1)
        self.assertIn('GigabitEthernet0/1', config.get_interfaces())
    
    def test_empty_change_not_added(self):
        """Test that changes with no modifications aren't added."""
        config = ChangeConfig()
        config.add_change('GigabitEthernet0/1')
        
        self.assertEqual(len(config), 0)


class TestInterfaceValidator(unittest.TestCase):
    """Test InterfaceValidator class."""
    
    def test_valid_interface_names(self):
        """Test valid interface name validation."""
        valid_names = [
            'GigabitEthernet0/1',
            'GigabitEthernet1/0',
            'TenGigabitEthernet0/1',
            'Management0/0',
            'Port-channel1',
            'Vlan100'
        ]
        
        for name in valid_names:
            self.assertTrue(
                InterfaceValidator.validate_interface_name(name),
                f"{name} should be valid"
            )
    
    def test_invalid_interface_names(self):
        """Test invalid interface name validation."""
        invalid_names = [
            'InvalidInterface',
            'Gi0/1',  # Abbreviated form not supported
            'GigabitEthernet',
            ''
        ]
        
        for name in invalid_names:
            self.assertFalse(
                InterfaceValidator.validate_interface_name(name),
                f"{name} should be invalid"
            )
    
    def test_valid_vlan_ids(self):
        """Test valid VLAN ID validation."""
        self.assertTrue(InterfaceValidator.validate_vlan_id(1))
        self.assertTrue(InterfaceValidator.validate_vlan_id(100))
        self.assertTrue(InterfaceValidator.validate_vlan_id(4094))
    
    def test_invalid_vlan_ids(self):
        """Test invalid VLAN ID validation."""
        self.assertFalse(InterfaceValidator.validate_vlan_id(0))
        self.assertFalse(InterfaceValidator.validate_vlan_id(4095))
        self.assertFalse(InterfaceValidator.validate_vlan_id(-1))
    
    def test_valid_nameif(self):
        """Test valid nameif validation."""
        valid_nameifs = ['inside', 'outside', 'dmz', 'test-interface', 'test_interface']
        
        for nameif in valid_nameifs:
            self.assertTrue(
                InterfaceValidator.validate_nameif(nameif),
                f"{nameif} should be valid"
            )
    
    def test_invalid_nameif(self):
        """Test invalid nameif validation."""
        invalid_nameifs = [
            '123invalid',  # Starts with number
            'invalid space',  # Contains space
            'a' * 49,  # Too long
            '',  # Empty
        ]
        
        for nameif in invalid_nameifs:
            self.assertFalse(
                InterfaceValidator.validate_nameif(nameif),
                f"{nameif} should be invalid"
            )


class TestInterfaceManager(unittest.TestCase):
    """Test InterfaceManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection = Mock(spec=ASAConnection)
        self.mock_connection.get_interface_config.return_value = """
interface GigabitEthernet0/1
 nameif inside
 vlan 10
 security-level 100
"""
        self.manager = InterfaceManager(self.mock_connection)
    
    def test_stage_change(self):
        """Test staging an interface change."""
        change = InterfaceChange('GigabitEthernet0/1', vlan=100, nameif='new_inside')
        self.manager.stage_change(change)
        
        self.assertEqual(len(self.manager.staged_changes), 1)
        self.assertIn('GigabitEthernet0/1', self.manager.current_configs)
    
    def test_preview_no_changes(self):
        """Test preview with no staged changes."""
        preview = self.manager.preview_changes()
        self.assertIn("No changes staged", preview)
    
    def test_clear_staged_changes(self):
        """Test clearing staged changes."""
        change = InterfaceChange('GigabitEthernet0/1', vlan=100)
        self.manager.stage_change(change)
        
        self.assertEqual(len(self.manager.staged_changes), 1)
        
        self.manager.clear_staged_changes()
        self.assertEqual(len(self.manager.staged_changes), 0)


class TestASAManager(unittest.TestCase):
    """Test ASAManager class."""
    
    @patch('asa_manager.manager.DeviceConfig')
    @patch('asa_manager.manager.ASAConnection')
    def test_manager_initialization(self, mock_connection, mock_device_config):
        """Test manager initialization."""
        manager = ASAManager()
        self.assertIsNotNone(manager.backup_manager)
    
    def test_context_manager(self):
        """Test using manager as context manager."""
        with patch('asa_manager.manager.DeviceConfig') as mock_config:
            with patch('asa_manager.manager.ASAConnection') as mock_conn:
                mock_conn.return_value.connect.return_value = True
                
                manager = ASAManager(device_config='test.yaml')
                
                with manager:
                    pass  # Context manager should handle connect/disconnect


if __name__ == '__main__':
    unittest.main()
