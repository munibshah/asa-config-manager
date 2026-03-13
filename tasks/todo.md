# TODO: Repository Reorganization

## Problem
The repository has a messy structure with:
- **Root-level duplicate files**: `__init__.py`, `__main__.py`, `manager.py`, `asa_connection.py`, `change_config.py`, `device_config.py`, `loader.py` — all are STALE copies of newer code inside `asa_manager/`
- **Root-level duplicate directories**: `config/`, `connection/`, `operations/`, `utils/`, `validators/` — all are STALE copies of `asa_manager/` subdirectories (missing `console.py`, `state.py`, updated code)
- **Loose config examples**: `changes_example.yaml`, `device_example.yaml` at root (already in `configs/`)
- **Loose test/debug scripts**: `test_credentials.py`, `test_ssh.py` at root (should be in `tests/`)
- **`setup.py` references `src/`** directory which doesn't exist — package is at `asa_manager/` not `src/asa_manager/`
- **`.gitignore` missing**: `.github/` and `copilot-docs/` exclusions
- **`example.py`** at root — should be in `examples/`
- **Root `.gitkeep`** — unnecessary at root level
- **`PROJECT_REVIEW.md`** — move to `docs/`

## Plan

### Phase 1: Update .gitignore
- [x] Add `.github/` and `copilot-docs/` to `.gitignore` so they are NOT pushed to GitHub

### Phase 2: Remove root-level stale duplicate files
- [x] Remove `__init__.py` (root) — stale copy of `asa_manager/__init__.py`
- [x] Remove `__main__.py` (root) — stale copy of `asa_manager/__main__.py`
- [x] Remove `manager.py` (root) — stale copy of `asa_manager/manager.py`
- [x] Remove `asa_connection.py` (root) — stale copy of `asa_manager/connection/asa_connection.py`
- [x] Remove `change_config.py` (root) — stale copy of `asa_manager/config/change_config.py`
- [x] Remove `device_config.py` (root) — stale copy of `asa_manager/config/device_config.py`
- [x] Remove `loader.py` (root) — stale copy of `asa_manager/config/loader.py`

### Phase 3: Remove root-level stale duplicate directories
- [x] Remove `config/` (root) — stale copy of `asa_manager/config/`
- [x] Remove `connection/` (root) — stale copy of `asa_manager/connection/`
- [x] Remove `operations/` (root) — stale copy of `asa_manager/operations/`
- [x] Remove `utils/` (root) — stale copy of `asa_manager/utils/`
- [x] Remove `validators/` (root) — stale copy of `asa_manager/validators/`

### Phase 4: Move loose files to proper locations
- [x] Move `changes_example.yaml` (root) — already in `configs/`, remove root copy
- [x] Move `device_example.yaml` (root) — already in `configs/`, remove root copy
- [x] Move `test_credentials.py` → `tests/test_credentials.py`
- [x] Move `test_ssh.py` → `tests/test_ssh.py`
- [x] Move `example.py` → `examples/example.py`
- [x] Move `PROJECT_REVIEW.md` → `docs/PROJECT_REVIEW.md`
- [x] Remove root `.gitkeep` (unnecessary at root)

### Phase 5: Fix setup.py
- [x] Change `package_dir={"": "src"}` → `package_dir={"": "."}` (package is at `asa_manager/`, not `src/asa_manager/`)
- [x] Change `packages=find_packages(where="src")` → `packages=find_packages(where=".")`

### Phase 6: Clean up __pycache__
- [x] Remove all `__pycache__` directories

### Phase 7: Verification
- [x] Run `python -m asa_manager --help` to verify CLI still works
- [x] Run tests if available
- [x] Verify `.github/` and `copilot-docs/` are gitignored

### Phase 8: Commit & Document
- [x] Update `CHANGE.md`
- [x] Git commit with descriptive message
- [x] Verify commit

## Expected Final Structure
```
asa-config-manager/
├── .env.example
├── .gitignore
├── CHANGE.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── QUICKSTART.md
├── README.md
├── requirements.txt
├── setup.py
├── asa_manager/           # Main package (THE source of truth)
│   ├── __init__.py
│   ├── __main__.py
│   ├── manager.py
│   ├── config/
│   ├── connection/
│   ├── operations/
│   ├── utils/
│   └── validators/
├── configs/               # YAML config files + examples
├── backups/               # Config backups
├── logs/                  # App logs
├── state/                 # Revert state persistence
├── tests/                 # All tests
├── examples/              # Example scripts
├── docs/                  # Additional docs
├── tasks/                 # Task tracking
├── .github/               # (gitignored — not pushed)
└── copilot-docs/          # (gitignored — not pushed)
