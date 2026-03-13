# TODO: Repository Reorganization

## Plan
The repository root was cluttered with stale duplicate files/directories that already exist inside `asa_manager/`. Clean up, fix broken references, and ensure internal docs aren't pushed to GitHub.

## Checklist
- [x] Remove root-level duplicate Python files (7 files)
- [x] Remove root-level duplicate directories (5 dirs: config/, connection/, operations/, utils/, validators/)
- [x] Remove root-level duplicate config examples (changes_example.yaml, device_example.yaml)
- [x] Move example.py → examples/
- [x] Move PROJECT_REVIEW.md → docs/
- [x] Move test_credentials.py, test_ssh.py → tests/
- [x] Fix setup.py (remove non-existent src/ reference)
- [x] Fix asa_manager/config/__init__.py (export InterfaceChange)
- [x] Fix tests/test_asa_manager.py (remove stale sys.path for src/)
- [x] Add .github/ and copilot-docs/ to .gitignore
- [x] Untrack .github/ and copilot-docs/ from git index
- [x] Clean all __pycache__ directories
- [x] Update README project structure
- [x] Update CHANGE.md
- [x] Run tests — 17/17 passed
- [x] Test CLI --help — works
- [x] Test CLI --preview — 2/2 devices succeeded
- [x] Verify .github/ and copilot-docs/ gitignored — confirmed
- [x] Commit
- [x] Push to GitHub

## Review
- 37 files changed, 2,033 lines of stale code removed
- All 17 unit tests pass
- CLI preview connects to both ASA devices in parallel successfully
- `.github/` and `copilot-docs/` confirmed excluded from GitHub via git check-ignore
- setup.py correctly finds packages at root level
- Repository structure is now clean and well-organized

---
