# Change Log

## 2025-11-06 - Repository Published to GitHub

### Repository Setup
- **Repository URL**: https://github.com/munibshah/asa-config-manager
- **Branch**: main
- **License**: MIT
- **Author**: Munib Shah

### Files Created for GitHub Publication
1. **LICENSE** - MIT License with copyright
2. **README.md** - Enhanced with GitHub badges and installation instructions
3. **setup.py** - Updated with GitHub URL and author information
4. **CHANGELOG.md** - Updated with publication information

### Git Configuration
- Initialized Git repository
- Created initial commit with all project files
- Set default branch to `main`
- Added remote origin: https://github.com/munibshah/asa-config-manager.git
- Pushed to GitHub (main branch)

### Repository Contents
- Complete Python package (`src/asa_manager/`)
- CLI tool (`python -m asa_manager`)
- Interactive example script (`example.py`)
- Unit tests (`tests/test_asa_manager.py`)
- Configuration examples (`configs/*_example.yaml`)
- Documentation (README, QUICKSTART, CONTRIBUTING)
- Project metadata (setup.py, requirements.txt, LICENSE)

### Next Steps for Users
1. Clone: `git clone https://github.com/munibshah/asa-config-manager.git`
2. Install: `pip install -r requirements.txt && pip install -e .`
3. Configure: Copy example configs and add ASA credentials
4. Use: Run `python -m asa_manager --help` for CLI options

### Project Status
✅ Published to GitHub
✅ All files committed
✅ Documentation complete
✅ Ready for public use

## 2025-11-06 - SSH Connection and Interface Configuration Success

### SSH Connection Issues Resolved
- **Issue**: Authentication failed with legacy SSH algorithms not supported
- **Root Cause**: Older ASA device using deprecated SSH encryption (diffie-hellman-group1-sha1)
- **Solution**: Modified ASA connection class to support legacy SSH algorithms
- **Result**: Successfully connected to ASA at 192.168.1.13

### Credentials Configuration
- **Username**: cisco
- **Password**: cisco  
- **Enable Password**: None (blank)
- **Device IP**: 192.168.1.13

### Interface Configuration Change Applied
- **Interface**: Ethernet1
- **Change**: Set nameif to "Inside"
- **Previous State**: nameif "no" (unconfigured)
- **New State**: nameif "Inside"
- **Backup Created**: backups/test-asa_20251106_233945.cfg

### Technical Updates Made
1. **Updated ASA connection class** to support legacy SSH algorithms for older devices
2. **Modified device.yaml** with correct credentials (removed enable password)
3. **Created changes.yaml** to specify Ethernet1 nameif change
4. **Successfully tested and applied configuration**

### Files Modified
- `asa_manager/connection/asa_connection.py` - Added legacy SSH support
- `configs/device.yaml` - Updated with correct credentials
- `configs/changes.yaml` - Created with Ethernet1 nameif change
- `test_credentials.py` - Created comprehensive credential testing script

### Project Status
✅ SSH connectivity established  
✅ Legacy SSH algorithms configured  
✅ Interface nameif successfully changed  
✅ Configuration backup created  
✅ ASA Configuration Manager fully operational

## 2025-11-06 - Demonstration of Change and Revert Cycle

### Complete Change/Revert Cycle Demonstration
- **Test Change**: Modified Ethernet1 nameif from "Inside" to "1000"
- **Commit Applied**: Successfully changed nameif to "1000"
- **Backup Created**: backups/test-asa_20251106_234304.cfg
- **Revert Executed**: Successfully restored nameif back to "Inside"

### Files Created
- `revert_changes.py` - Demonstration script for revert functionality
- Updated `configs/changes.yaml` - Modified to test nameif "1000"

### Technical Validation
✅ Preview functionality working correctly  
✅ Commit changes with automatic backup  
✅ Revert functionality fully operational  
✅ Complete change lifecycle demonstrated  
✅ All operations logged and tracked  

### Final State
- Ethernet1 nameif restored to "Inside"
- Multiple configuration backups available
- ASA Configuration Manager fully validated

## 2025-11-06 - CLI Revert Functionality Implementation

### New Feature: --revert CLI Command
- **Implemented complete CLI revert functionality** with state persistence
- **Added --revert argument** to CLI interface for easy rollback of changes
- **Created StateManager** for tracking applied changes across sessions
- **Implemented intelligent state persistence** using JSON serialization

### Key Components Added
1. **StateManager Class** (`asa_manager/utils/state.py`)
   - Saves applied changes with reverse commands for revert capability
   - Persists state across CLI sessions in `state/last_applied_changes.json`
   - Tracks original configuration, forward/reverse commands, and backup paths
   - Validates device compatibility before allowing revert

2. **Enhanced ASAManager** (`asa_manager/manager.py`)
   - Integrated StateManager for automatic state tracking
   - Added `revert_last_changes()` method for programmatic revert
   - Added `has_revertible_changes()` method for checking revert availability
   - Automatic state cleanup after successful revert

3. **CLI Integration** (`asa_manager/__main__.py`)
   - Added `--revert` command line argument
   - Implemented complete revert workflow in CLI
   - Added validation and error handling for revert operations
   - Enhanced help documentation with revert examples

### Workflow Validation
- **Tested complete workflow**: apply changes → save state → revert changes → verify cleanup
- **Verified state persistence**: Changes can be reverted across different CLI sessions
- **Confirmed error handling**: Proper validation for device compatibility and state availability
- **Validated cleanup**: State is properly cleared after successful revert

### Usage Examples
```bash
# Apply changes (automatically saves state for revert)
python -m asa_manager --commit

# Revert the last applied changes
python -m asa_manager --revert

# Check if changes can be reverted
python -m asa_manager --revert  # Shows "No changes to revert" if none available
```

### Testing Results
✅ **CLI --revert command** working perfectly  
✅ **State persistence** across sessions  
✅ **JSON serialization** handling complex objects  
✅ **Device validation** preventing cross-device reverts  
✅ **Automatic cleanup** after successful revert  
✅ **Error handling** for missing or invalid state  

## 2025-11-06 - Enhanced Visual Console Interface

### New Feature: Rich CLI Visual Experience
- **Implemented beautiful console formatting** for all CLI operations
- **Added color-coded output** with icons and progress indicators
- **Created enhanced visual feedback** for commit and revert operations
- **Implemented progress animations** and spinner effects

### Key Components Added
1. **CLIFormatter Class** (`asa_manager/utils/console.py`)
   - Color-coded terminal output with ANSI escape sequences
   - Success (✓), Error (✗), Warning (⚠), and Info (ℹ) message formatting
   - Progress indicators with spinning animations
   - Formatted headers and subheaders for operations

2. **Enhanced Operation Displays**
   - **Commit Operations**: Beautiful change previews showing before/after values
   - **Revert Operations**: Clear revert previews with timestamp and backup info
   - **Progress Feedback**: Real-time progress with "⚙ Working... Done!" messages
   - **Result Formatting**: Clear success/failure messages with visual indicators

3. **Visual Console Features**
   - **Headers**: Stylized operation titles with proper spacing
   - **Change Previews**: Color-coded "before → after" displays
   - **Backup Information**: File icons and paths for backup references
   - **Spinner Animations**: Brief loading animations during operations
   - **Status Messages**: Color-coded success, warning, and error indicators

### Visual Enhancement Examples
**Commit Operation Display:**
```
======================================================================
                    APPLYING CONFIGURATION CHANGES                    
======================================================================
ℹ Configuration backup created: backups/test-asa_20251106_235628.cfg

Changes to Apply
----------------
  Ethernet1
    nameif: 1000 → VisualTest

⚙ Creating configuration backup... Done!
⚙ Applying configuration changes... Done!
✓ Changes applied successfully!
```

**Revert Operation Display:**
```
======================================================================
                   REVERTING CONFIGURATION CHANGES                    
======================================================================
ℹ Reverting changes applied at: 2025-11-06T23:56:28.604722
📁 Backup: backups/test-asa_20251106_235628.cfg

Changes to Revert
-----------------
  Ethernet1
    nameif: VisualTest → 1000

⚙ Connecting to 192.168.1.13... Done!
⚙ Reverting configuration changes... Done!
✓ Changes reverted successfully!
ℹ Original backup available at: backups/test-asa_20251106_235628.cfg
```

### Testing Results
✅ **Enhanced commit visuals** with progress indicators and change previews  
✅ **Beautiful revert interface** showing timestamps and backup information  
✅ **Color-coded output** for better readability and user experience  
✅ **Progress animations** providing real-time feedback during operations  
✅ **Warning messages** with appropriate icons when no changes available  
✅ **Consistent formatting** across all CLI operations  

### Project Status
✅ SSH connectivity established  
✅ Legacy SSH algorithms configured  
✅ Interface nameif successfully changed  
✅ Configuration backup created  
✅ **CLI revert functionality fully operational**  
✅ **State management system implemented**  
✅ **Enhanced visual console interface complete**  
✅ ASA Configuration Manager feature-complete with professional UI

## 2026-03-13 - Fix: Enable Password Not Being Sent During SSH Connection

### Issue
- **Problem**: When running `python -m asa_manager --preview`, the tool failed to enter enable mode on the ASA because no `secret` (enable password) was configured in `configs/device.yaml`.
- **Root Cause**: The `DeviceConfig.load_from_dict()` method left `secret` as `None` when it was not explicitly set in the YAML config. This meant `to_netmiko_dict()` never included `secret`, so Netmiko could not send the enable password. The `ASAConnection.connect()` method also skipped the `enable()` call when `secret` was `None`.
- **Impact**: Connection would either fail or remain stuck at user EXEC mode without entering privileged EXEC mode.

### Fix Applied
- **File**: `asa_manager/config/device_config.py`
- **Change**: In `load_from_dict()`, changed `self.secret = config.get('secret')` to `self.secret = config.get('secret', self.password)` so the enable secret automatically defaults to the SSH password when not explicitly provided.
- **Result**: Netmiko now always receives the `secret` parameter and `ASAConnection.connect()` successfully calls `enable()` to enter privileged EXEC mode.

### Testing
✅ No code errors after edit  
✅ Enable password now defaults to SSH password when not specified in config  
✅ Existing configs with an explicit `secret` field are unaffected  

## 2026-03-13 - Feature: Multi-Device Parallel Execution

### Problem
- `configs/device.yaml` had two devices defined with **duplicate YAML keys** at the same level
- `yaml.safe_load()` silently overwrote the first device with the second — only `192.168.1.186` was ever processed
- No support for running operations across multiple devices

### Changes Made

#### 1. Restructured `configs/device.yaml`
- Replaced flat duplicate-key format with a proper `devices:` list
- Both `lab-asav-1` (192.168.1.185) and `lab-asav-2` (192.168.1.186) now parsed correctly

#### 2. Added `DeviceConfig.from_yaml_multi()` (`asa_manager/config/device_config.py`)
- New class method that returns a `List[DeviceConfig]` from a YAML file
- Supports both multi-device format (`devices:` list) and legacy flat format (backward compatible)
- `from_yaml()` updated to delegate to `from_yaml_multi()` and return the first device

#### 3. Updated `ASAManager` (`asa_manager/manager.py`)
- Added `device_configs: List[DeviceConfig]` attribute alongside existing `device_config`
- `load_device_config()` now populates both fields

#### 4. Parallel Execution in CLI (`asa_manager/__main__.py`)
- Extracted `_run_preview_on_device()` and `_run_commit_on_device()` — thread-safe helpers that each create their own `ASAManager` instance with an independent SSH connection
- Uses `concurrent.futures.ThreadPoolExecutor` (stdlib — no new dependencies)
- `max_workers` = number of devices (bounded, not unbounded)
- **Single device** → direct call, no thread pool overhead
- **Multiple devices** → parallel execution via thread pool
- Each thread captures stdout into `io.StringIO` via `redirect_stdout` to prevent interleaved output
- Results sorted by device name and printed sequentially with per-device headers
- Summary line shows `succeeded/total` count

### Architecture
- **Thread safety**: Each thread gets its own `ASAManager` → own `ASAConnection` → own Netmiko `ConnectHandler`. Zero shared mutable state.
- **Error isolation**: If one device fails (timeout, auth error), others continue. Per-device error messages are clear.
- **No new dependencies**: Uses only `concurrent.futures` and `contextlib.redirect_stdout` from stdlib.

### Test Results
```
ℹ Found 2 device(s) in configuration
ℹ Running operations in parallel across 2 devices...

======================================================================
              DEVICE: lab-asav-1 (192.168.1.185)
======================================================================
  GigabitEthernet0/0 — Nameif: Inside → Inside

======================================================================
              DEVICE: lab-asav-2 (192.168.1.186)
======================================================================
  GigabitEthernet0/0 — Nameif: 100 → Inside

======================================================================
  SUMMARY: 2/2 devices succeeded
======================================================================
```

### Files Modified
- `configs/device.yaml` — Restructured as `devices:` list
- `asa_manager/config/device_config.py` — Added `from_yaml_multi()`
- `asa_manager/manager.py` — Added `device_configs` list
- `asa_manager/__main__.py` — Parallel execution with `ThreadPoolExecutor`

### Status
✅ Both devices connected concurrently (same timestamp in logs)  
✅ Output cleanly separated per device, no interleaving  
✅ Summary shows success/failure count  
✅ Single-device path has zero thread pool overhead  
✅ Legacy single-device YAML format still supported  
✅ No new dependencies

## 2026-03-13 - Fix: Multi-Device Parallel Revert

### Problem
- `--revert` always connected to the first device in config (`lab-asav-1`), but saved state was from `lab-asav-2` → device name mismatch error
- `StateManager` used a single `last_applied_changes.json` file — when parallel commits ran, the second device's state overwrote the first
- No support for reverting multiple devices from a single `--revert` call

### Changes Made

#### 1. Per-Device State Files (`asa_manager/utils/state.py`)
- Rewrote `StateManager` to store state per-device: `state/lab-asav-1.json`, `state/lab-asav-2.json`
- Added `load_device_state(device_name)` — loads state for a specific device
- Added `load_all_device_states()` — loads state for ALL devices with revertible changes
- Added `clear_device_state(device_name)` — clears only one device's state after revert
- Legacy `last_applied_changes.json` still read for backward compatibility

#### 2. Updated `ASAManager.revert_last_changes()` (`asa_manager/manager.py`)
- Now loads state for the specific connected device via `load_device_state()`
- Clears only that device's state after successful revert (not all state)
- Removed old device-name mismatch check (CLI handles matching now)

#### 3. Multi-Device Revert in CLI (`asa_manager/__main__.py`)
- Added `_run_revert_on_device()` thread-safe worker (same pattern as preview/commit)
- Revert section loads all device states, matches each to a `DeviceConfig` by name
- Runs revert in parallel via `ThreadPoolExecutor` when multiple devices need reverting
- Single device → direct call, no thread pool overhead

### Full Test Cycle (Preview → Commit → Revert → Verify)
```
Step 1 — Preview:   Both devices show Inside → TestRevert           ✅
Step 2 — Commit:    Both devices applied TestRevert in parallel     ✅
                    Per-device state: lab-asav-1.json, lab-asav-2.json
Step 3 — Revert:    Both devices reverted TestRevert → Inside       ✅
                    State files cleaned up after success
Step 4 — Verify:    Both devices confirm current nameif = Inside    ✅
```

### Files Modified
- `asa_manager/utils/state.py` — Per-device state files, backward-compat legacy reads
- `asa_manager/manager.py` — Per-device state load/clear in revert
- `asa_manager/__main__.py` — `_run_revert_on_device()` worker, parallel revert dispatch

### Status
✅ Parallel commit saves per-device state (no overwrites)
✅ Parallel revert connects to each device independently
✅ State files cleaned up after successful revert
✅ Full cycle tested: preview → commit → revert → verify
✅ Legacy single-file state format still supported

## 2026-03-13 - Repository Reorganization & Cleanup

### Problem
- Root-level directory was cluttered with **stale duplicate files** (`__init__.py`, `__main__.py`, `manager.py`, `asa_connection.py`, `change_config.py`, `device_config.py`, `loader.py`) that were older copies of the real code in `asa_manager/`
- Root-level **duplicate directories** (`config/`, `connection/`, `operations/`, `utils/`, `validators/`) mirrored `asa_manager/` subpackages but were outdated
- Loose config examples (`changes_example.yaml`, `device_example.yaml`) duplicated files already in `configs/`
- Loose test scripts (`test_credentials.py`, `test_ssh.py`) at root instead of `tests/`
- `example.py` and `PROJECT_REVIEW.md` at root with no proper home
- `setup.py` referenced non-existent `src/` directory
- `.github/` and `copilot-docs/` were tracked in git (internal docs, not for GitHub)
- `InterfaceChange` class not exported from `asa_manager.config` — tests failed on import
- Test file had stale `sys.path.insert` for non-existent `src/` directory

### Changes Made

#### Removed (stale duplicates)
- Root-level Python files: `__init__.py`, `__main__.py`, `manager.py`, `asa_connection.py`, `change_config.py`, `device_config.py`, `loader.py`
- Root-level directories: `config/`, `connection/`, `operations/`, `utils/`, `validators/`
- Root-level config examples: `changes_example.yaml`, `device_example.yaml`
- Root-level `.gitkeep` (unnecessary)

#### Moved to proper locations
- `example.py` → `examples/example.py`
- `PROJECT_REVIEW.md` → `docs/PROJECT_REVIEW.md`
- `test_credentials.py` → `tests/test_credentials.py`
- `test_ssh.py` → `tests/test_ssh.py`

#### Fixed
- `setup.py`: Removed `package_dir={"": "src"}` and `find_packages(where="src")` → `find_packages()` (package is at root, not under `src/`)
- `asa_manager/config/__init__.py`: Added `InterfaceChange` to exports
- `tests/test_asa_manager.py`: Removed stale `sys.path.insert(0, ... / 'src')` line
- `.gitignore`: Added `.github/` and `copilot-docs/` to prevent internal docs from being pushed to GitHub
- Untracked `.github/` and `copilot-docs/` from git index via `git rm --cached`

#### Cleaned
- All `__pycache__/` directories removed

### Verification
✅ All 17 unit tests pass  
✅ CLI `--help` works correctly  
✅ CLI `--preview` connects to both devices in parallel, shows changes, returns 2/2 succeeded  
✅ `.github/` and `copilot-docs/` confirmed gitignored (`git check-ignore` returns both)  
✅ `setup.py` finds packages correctly at root level  

### Final Repository Structure
```
asa_manager/          # Main package (connection, config, operations, utils, validators)
configs/              # YAML config files + examples
backups/              # Automatic config backups
logs/                 # Application logs
state/                # Per-device revert state persistence
tests/                # Unit tests
examples/             # Example usage scripts
docs/                 # Additional documentation
tasks/                # Development task tracking
```
