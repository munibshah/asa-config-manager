"""Device configuration model."""

from typing import Dict, Any, Optional
from .loader import ConfigLoader


class DeviceConfig:
    """Represents ASA device connection configuration."""
    
    REQUIRED_KEYS = ['host', 'username', 'password', 'device_type']
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize device configuration.
        
        Args:
            config_dict: Configuration dictionary
        """
        self.host: str = ''
        self.username: str = ''
        self.password: str = ''
        self.device_type: str = 'cisco_asa'
        self.port: int = 22
        self.secret: Optional[str] = None
        self.device_name: Optional[str] = None
        
        if config_dict:
            self.load_from_dict(config_dict)
    
    def load_from_dict(self, config: Dict[str, Any]):
        """Load configuration from dictionary."""
        ConfigLoader.validate_required_keys(config, self.REQUIRED_KEYS)
        
        self.host = config['host']
        self.username = config['username']
        self.password = config['password']
        self.device_type = config.get('device_type', 'cisco_asa')
        self.port = config.get('port', 22)
        self.secret = config.get('secret')
        self.device_name = config.get('device_name', self.host)
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'DeviceConfig':
        """
        Load device configuration from YAML file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            DeviceConfig instance
        """
        config_dict = ConfigLoader.load(config_path)
        return cls(config_dict)
    
    def to_netmiko_dict(self) -> Dict[str, Any]:
        """
        Convert to Netmiko connection dictionary.
        
        Returns:
            Dictionary compatible with Netmiko ConnectHandler
        """
        conn_dict = {
            'device_type': self.device_type,
            'host': self.host,
            'username': self.username,
            'password': self.password,
            'port': self.port,
        }
        
        if self.secret:
            conn_dict['secret'] = self.secret
        
        return conn_dict
