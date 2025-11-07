# Contributing to ASA Configuration Manager

## Development Setup

1. **Fork and clone the repository**
2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install in development mode:**
   ```bash
   pip install -e .
   ```

## Project Structure

```
asa-config-manager/
├── src/asa_manager/          # Main package source
│   ├── __init__.py           # Package exports
│   ├── __main__.py           # CLI entry point
│   ├── manager.py            # Main ASAManager class
│   ├── config/               # Configuration models
│   ├── connection/           # SSH connection handling
│   ├── operations/           # Interface operations
│   ├── utils/                # Utilities (logging, backup, helpers)
│   └── validators/           # Input validation
├── configs/                  # Configuration files
├── tests/                    # Unit tests
├── backups/                  # Auto-generated backups
├── logs/                     # Auto-generated logs
├── example.py                # Interactive example
├── QUICKSTART.md             # Quick start guide
└── README.md                 # Main documentation
```

## Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test
python tests/test_asa_manager.py

# Run with coverage (if pytest-cov installed)
python -m pytest tests/ --cov=asa_manager
```

## Code Style

- Follow PEP 8 guidelines
- Use docstrings for all public methods
- Type hints where applicable
- Keep functions focused and small

## Adding New Features

1. Create a new branch: `git checkout -b feature/your-feature`
2. Implement the feature with tests
3. Update documentation
4. Run tests to ensure nothing breaks
5. Submit a pull request

## Testing Locally

Before committing, test:
- Unit tests pass
- CLI commands work
- Example script runs
- No linting errors

## Security

- Never commit actual device credentials
- Use example files with placeholder data
- Keep sensitive configs in `.gitignore`
