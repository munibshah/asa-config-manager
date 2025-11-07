# Quick Start Guide

## Setup

1. **Clone and navigate to the project:**
   ```bash
   cd asa-config-manager
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

## Configuration

1. **Create your device configuration:**
   ```bash
   cp configs/device_example.yaml configs/device.yaml
   ```
   
   Edit `configs/device.yaml` with your ASA credentials:
   ```yaml
   host: "192.168.1.1"
   username: "admin"
   password: "your_password"
   device_type: "cisco_asa"
   port: 22
   secret: "enable_password"  # Optional
   device_name: "my-asa"
   ```

2. **Create your changes configuration:**
   ```bash
   cp configs/changes_example.yaml configs/changes.yaml
   ```
   
   Edit `configs/changes.yaml` with your desired changes:
   ```yaml
   interfaces:
     - interface: "GigabitEthernet0/1"
       vlan: 100
       nameif: "inside"
     
     - interface: "GigabitEthernet0/2"
       vlan: 200
       nameif: "dmz"
   ```

## Usage

### Option 1: Using the Example Script

```bash
python example.py
```

This interactive script will:
- Connect to your ASA
- Load and preview changes
- Ask for confirmation before applying
- Optionally revert changes

### Option 2: Using the CLI

**Preview changes:**
```bash
python -m asa_manager --preview
```

**Apply changes with backup:**
```bash
python -m asa_manager --commit
```

**Apply and save to startup-config:**
```bash
python -m asa_manager --commit --save
```

**List backups:**
```bash
python -m asa_manager --list-backups
```

### Option 3: Using as a Library

```python
from asa_manager import ASAManager

# Context manager (auto connects/disconnects)
with ASAManager(device_config='configs/device.yaml') as manager:
    # Load changes
    manager.load_changes('configs/changes.yaml')
    
    # Preview
    print(manager.preview_changes())
    
    # Apply
    result = manager.commit_changes(save_config=False)
    
    # Revert if needed
    if result['success']:
        manager.revert_changes()
```

## Running Tests

```bash
python -m pytest tests/
# or
python -m unittest discover tests
```

## Safety Features

✅ **Preview before apply** - Always see what will change  
✅ **Automatic backups** - Config saved before changes  
✅ **Revert capability** - Undo changes with reverse commands  
✅ **Validation** - Interface names, VLANs, and nameif validated  
✅ **Logging** - All operations logged to `logs/`  

## Troubleshooting

**Connection issues:**
- Verify ASA is reachable: `ping <asa-ip>`
- Check SSH is enabled on ASA
- Verify credentials in `configs/device.yaml`

**Module not found:**
- Ensure you've installed: `pip install -e .`
- Activate virtual environment if using one

**Permission errors:**
- Check user has privilege 15 or appropriate admin rights
- Verify enable password (secret) if required

## Next Steps

1. Test connection with `--preview` first
2. Apply changes without `--save` to test
3. Verify changes on ASA
4. Use `--save` to make permanent
5. Keep backups for rollback if needed
