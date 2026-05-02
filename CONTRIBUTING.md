# Contributing to GhostPrint

Thank you for your interest in contributing to GhostPrint! This document provides guidelines for contributing.

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported
- Include Python version, OS, and GhostPrint version
- Provide steps to reproduce
- Include error messages and logs

### Suggesting Features

- Open an issue with the `[FEATURE]` tag
- Describe the use case
- Explain why it would be useful

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ghostprint.git
cd ghostprint

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Run tests
pytest
```

## Coding Standards

- Follow PEP 8 style guide
- Add docstrings to functions
- Write tests for new features
- Keep functions focused and modular

## Adding New OSINT Sources

When adding new modules:

1. Create a new file in `ghostprint/modules/`
2. Implement async methods where possible
3. Add error handling
4. Add tests in `tests/`
5. Update documentation

## Questions?

Feel free to open an issue for questions or discussions.