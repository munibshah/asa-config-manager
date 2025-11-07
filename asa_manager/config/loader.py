"""YAML configuration loader."""

import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Load and parse YAML configuration files."""
    
    @staticmethod
    def load(config_path: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file.
        
        Args:
            config_path: Path to YAML file
            
        Returns:
            Parsed configuration dictionary
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        
        if not config:
            raise ValueError(f"Empty or invalid config file: {config_path}")
        
        return config
    
    @staticmethod
    def validate_required_keys(config: Dict[str, Any], required: list):
        """
        Validate that required keys exist in config.
        
        Args:
            config: Configuration dictionary
            required: List of required keys
            
        Raises:
            ValueError if any required keys are missing
        """
        missing = [key for key in required if key not in config]
        if missing:
            raise ValueError(f"Missing required config keys: {missing}")
