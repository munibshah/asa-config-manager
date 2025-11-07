# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-11-06

### Added
- Initial project structure and core functionality
- SSH-based connection to ASA devices using Netmiko
- YAML configuration support for device credentials and interface changes
- Preview-commit-revert workflow for interface changes
- Automatic configuration backups before applying changes
- Reverse command generation for rollback capability
- VLAN assignment changes on interfaces
- Nameif configuration changes on interfaces
- Comprehensive logging system with file and console output
- Configuration validation for interfaces, VLANs, and nameif values
- Context manager support for automatic connection handling
- Example configuration files and usage scripts
- Complete documentation in README
- **CLI interface via `python -m asa_manager`**
- **Interactive example script (`example.py`)**
- **Comprehensive unit tests**
- **Quick start guide (QUICKSTART.md)**
- **.gitignore for Python projects**
- **Directory placeholders for logs/ and backups/**
- **MIT License**
- **GitHub repository setup**

### Components
- `ASAManager`: Main library interface
- `ASAConnection`: SSH connection handler
- `InterfaceManager`: Interface configuration operations
- `DeviceConfig`: Device configuration model
- `ChangeConfig`: Interface change configuration model
- `BackupManager`: Configuration backup management
- `InterfaceValidator`: Configuration validation
- Utility modules: logging, helpers, backup management

### Project Completeness
- ✅ All core modules implemented
- ✅ CLI tool ready to use
- ✅ Example scripts provided
- ✅ Unit tests created
- ✅ Documentation complete
- ✅ Git configuration set up
- ✅ Published to GitHub: https://github.com/munibshah/asa-config-manager
