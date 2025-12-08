# Contributing to UBEM Analysis MCP

Thank you for your interest in contributing! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- Clear and descriptive title
- Exact steps to reproduce the problem
- Expected vs actual behaviour
- Your environment (OS, Python version, EnergyPlus version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Include:

- Clear and descriptive title
- Detailed description of the proposed functionality
- Explanation of why this enhancement would be useful
- Alternative solutions you've considered

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code, add tests
3. Update documentation if needed
4. Ensure the test suite passes
5. Make sure your code follows the existing style
6. Write a clear commit message

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/JINGFENGZ/ubem-mcp
cd ubem-mcp
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Configure Your Environment

```bash
export UBEM_PROJECT_ROOT="/path/to/your/project"
export ENERGYPLUS_ROOT="/path/to/EnergyPlus"
```

## Coding Standards

### Code Style

We use `black` for code formatting and `ruff` for linting:

```bash
black ubem_analysis_mcp/ examples/
ruff check ubem_analysis_mcp/ examples/
```

### Type Hints

Use type hints where appropriate:

```python
def analyze_weather(epw_file: str, top_n: int = 3) -> Dict:
    ...
```

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update README.md if you add new features

## Testing

### Running Tests

```bash
pytest
```

### Writing Tests

Place tests in the `tests/` directory:

```python
import pytest
from ubem_analysis_mcp.tools.weather_analysis import analyze_epw_hottest_days

def test_analyze_weather_file():
    result = analyze_epw_hottest_days("path/to/test.epw", top_n=3)
    assert result["success"] is True
```

## Commit Message Guidelines

Follow conventional commits:

```
<type>(<scope>): <subject>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:

```
feat(weather): add support for custom date ranges

Added ability to analyse weather data for specific date ranges.

Closes #123
```

## Questions?

Open an issue with the "question" label or start a discussion.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

