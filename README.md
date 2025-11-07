# ASA Configuration Manager

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for managing Cisco ASA interface configurations with a 
safe preview-commit-revert workflow.

## Features

- SSH-based connection to ASA devices
- Change VLAN assignments on interfaces
- Modify interface nameif values
- Preview changes before applying
- Automatic configuration backups
- Rollback capability with reverse commands

## Installation

### From GitHub
```bash
git clone https://github.com/munibshah/asa-config-manager.git
cd asa-config-manager
pip install -r requirements.txt
pip install -e .
```

### From Source
```bash
pip install -r requirements.txt
```

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## Configuration

1. Copy the example config files:
```bash
cp configs/device_example.yaml configs/device.yaml
cp configs/changes_example.yaml configs/changes.yaml
```

2. Edit `configs/device.yaml` with your ASA credentials
3. Edit `configs/changes.yaml` with desired interface changes

## Usage

### CLI Mode
```bash
# Preview changes
python -m asa_manager --preview

# Apply changes with backup
python -m asa_manager --commit

# Apply and save configuration
python -m asa_manager --commit --save
```

### Library Mode
```python
from asa_manager import ASAManager

# Initialize manager
manager = ASAManager(device_config='configs/device.yaml')

# Connect to device
manager.connect()

# Load changes from config
manager.load_changes('configs/changes.yaml')

# Preview changes
preview = manager.preview_changes()
print(preview)

# Apply changes (creates backup automatically)
result = manager.commit_changes()

# Revert if needed
if something_wrong:
    manager.revert_changes()

# Disconnect
manager.disconnect()
```

### Context Manager
```python
from asa_manager import ASAManager

with ASAManager(device_config='configs/device.yaml') as manager:
    manager.load_changes('configs/changes.yaml')
    print(manager.preview_changes())
    result = manager.commit_changes(save_config=True)
```

## Project Structure

- `src/asa_manager/` - Main package
  - `connection/` - SSH connection handling
  - `config/` - Configuration parsing
  - `operations/` - VLAN and nameif operations
  - `validators/` - Configuration validation
  - `utils/` - Logging, backups, helpers
- `configs/` - YAML configuration files
- `backups/` - Automatic config backups
- `logs/` - Application logs
- `tests/` - Unit tests

## Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Safety Features

- ✅ Preview changes before applying
- ✅ Automatic configuration backups
- ✅ Revert capability with reverse commands
- ✅ Input validation for all parameters
- ✅ Comprehensive logging

## Requirements

- Python 3.8+
- Network access to Cisco ASA device
- SSH enabled on ASA
- Valid credentials with appropriate privileges

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Munib Shah**
- GitHub: [@munibshah](https://github.com/munibshah)

## Acknowledgments

- Built with [Netmiko](https://github.com/ktbyers/netmiko) for SSH connectivity
- Inspired by network automation best practices

## Support

For issues, questions, or contributions, please open an issue on GitHub.
