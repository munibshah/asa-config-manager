"""ASA SSH connection handler."""

from typing import Optional, List
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
import paramiko

from ..config.device_config import DeviceConfig
from ..utils.logger import get_logger
from ..utils.helpers import clean_output

logger = get_logger(__name__)


class ASAConnection:
    """Manages SSH connection to ASA device."""
    
    def __init__(self, device_config: DeviceConfig):
        """
        Initialize ASA connection.
        
        Args:
            device_config: Device configuration object
        """
        self.device_config = device_config
        self.connection: Optional[ConnectHandler] = None
        self.is_connected = False
        
        # Configure paramiko to support legacy SSH algorithms for older ASA devices
        self._configure_legacy_ssh_support()
    
    def _configure_legacy_ssh_support(self):
        """Configure paramiko to support legacy SSH algorithms for older ASA devices."""
        try:
            # Add legacy algorithms to the supported lists (convert to lists first)
            paramiko.Transport._preferred_kex = list(paramiko.Transport._preferred_kex) + [
                'diffie-hellman-group1-sha1',
                'diffie-hellman-group14-sha1', 
                'diffie-hellman-group-exchange-sha1',
                'diffie-hellman-group-exchange-sha256',
            ]
            
            paramiko.Transport._preferred_ciphers = list(paramiko.Transport._preferred_ciphers) + [
                'aes128-cbc',
                'aes192-cbc', 
                'aes256-cbc',
                'des3-cbc',
            ]
            
            paramiko.Transport._preferred_macs = list(paramiko.Transport._preferred_macs) + [
                'hmac-sha1',
                'hmac-sha1-96',
                'hmac-md5',
                'hmac-md5-96',
            ]
            
            logger.debug("Legacy SSH algorithms configured for older ASA devices")
        except Exception as e:
            logger.warning(f"Could not configure legacy SSH support: {e}")

    def connect(self) -> bool:
        """
        Establish SSH connection to ASA device.
        
        Returns:
            True if connection successful
            
        Raises:
            NetmikoTimeoutException: Connection timeout
            NetmikoAuthenticationException: Auth failed
        """
        try:
            logger.info(f"Connecting to {self.device_config.host}...")
            
            self.connection = ConnectHandler(
                **self.device_config.to_netmiko_dict()
            )
            
            # Enter enable mode if secret provided
            if self.device_config.secret:
                self.connection.enable()
            
            self.is_connected = True
            logger.info(f"Connected to {self.device_config.host}")
            return True
            
        except NetmikoTimeoutException as e:
            logger.error(f"Connection timeout: {e}")
            raise
        except NetmikoAuthenticationException as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise
    
    def disconnect(self):
        """Close SSH connection."""
        if self.connection:
            try:
                self.connection.disconnect()
                self.is_connected = False
                logger.info(f"Disconnected from {self.device_config.host}")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
    
    def send_command(self, command: str, expect_string: Optional[str] = None) -> str:
        """
        Send a command to the device.
        
        Args:
            command: Command to send
            expect_string: String to expect in response
            
        Returns:
            Command output
        """
        if not self.is_connected or not self.connection:
            raise ConnectionError("Not connected to device")
        
        try:
            logger.debug(f"Sending command: {command}")
            output = self.connection.send_command(
                command,
                expect_string=expect_string
            )
            return clean_output(output)
            
        except Exception as e:
            logger.error(f"Error sending command '{command}': {e}")
            raise
    
    def send_config_commands(self, commands: List[str]) -> str:
        """
        Send configuration commands to device.
        
        Args:
            commands: List of configuration commands
            
        Returns:
            Command output
        """
        if not self.is_connected or not self.connection:
            raise ConnectionError("Not connected to device")
        
        try:
            logger.debug(f"Sending config commands: {commands}")
            output = self.connection.send_config_set(commands)
            return clean_output(output)
            
        except Exception as e:
            logger.error(f"Error sending config commands: {e}")
            raise
    
    def get_running_config(self) -> str:
        """
        Get the running configuration.
        
        Returns:
            Running configuration text
        """
        return self.send_command('show running-config')
    
    def get_interface_config(self, interface: str) -> str:
        """
        Get configuration for a specific interface.
        
        Args:
            interface: Interface name
            
        Returns:
            Interface configuration text
        """
        return self.send_command(f'show running-config interface {interface}')
    
    def save_config(self):
        """Save running config to startup config."""
        logger.info("Saving configuration...")
        self.send_command('write memory')
        logger.info("Configuration saved")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
