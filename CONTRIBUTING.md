# Contributing to ATP Rankings Data Visualization

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Reporting Issues](#reporting-issues)

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ATP-Rankings-Data-Visualization.git
   cd ATP-Rankings-Data-Visualization
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 💻 Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   uvicorn src.main:app --reload
   ```

3. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

## 📁 Project Structure

```
src/                    # Core application code
├── main.py            # FastAPI application
├── services.py        # Business logic
└── mcp_router.py      # MCP endpoints

scripts/               # Utility scripts
├── analyze.py         # CLI analysis tool
├── generate.py        # Database generation
└── filler.py          # Database updates

templates/             # HTML templates
tests/                 # Test suite
docs/                  # Documentation
```

## ✏️ Making Changes

### Adding New Features

1. **Service Layer** (`src/services.py`):
   - Add business logic and database operations
   - Functions should return data structures (dicts, lists)
   - Raise `ValueError` for error conditions

2. **API Endpoints** (`src/main.py`):
   - Add REST API routes for web access
   - Convert service errors to HTTP exceptions

3. **MCP Endpoints** (`src/mcp_router.py`):
   - Add MCP-compliant endpoints for AI access
   - Use `MCPResponse` wrapper for consistent format
   - Update `mcp_manifest.json` with new tool definitions

4. **Templates** (`templates/`):
   - Add HTML templates for new web pages
   - Use Jinja2 templating
   - Include Chart.js for visualizations

### Database Changes

- Use `scripts/generate.py` as reference for scraping
- Update `scripts/filler.py` for incremental updates
- Test with `scripts/debug.py` to find issues

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Tests
```bash
pytest tests/test_mcp.py::TestMCPHealth -v
```

### Test Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Manual Testing
```bash
# Test MCP endpoints
bash scripts/test_mcp.sh

# Test web interface
uvicorn src.main:app --reload
# Visit http://localhost:8000
```

### Add Tests for New Features

When adding features, please include:
- Unit tests for service functions
- Integration tests for API endpoints
- MCP endpoint tests if applicable

Example:
```python
# tests/test_your_feature.py
def test_new_feature():
    from src.services import your_new_function
    result = your_new_function(test_input)
    assert result == expected_output
```

## 📤 Submitting Changes

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: clear description of changes"
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**:
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Provide a clear description of changes
   - Reference any related issues

### Pull Request Guidelines

- **Title**: Clear, concise description of changes
- **Description**: 
  - What does this PR do?
  - Why is this change needed?
  - How has it been tested?
- **Tests**: Include tests for new features
- **Documentation**: Update README.md or docs/ if needed

## 🎨 Code Style

### Python

Follow PEP 8 style guidelines:

```python
# Good
def get_player_stats(player_name: str) -> dict:
    """Get statistics for a player.
    
    Args:
        player_name: Full name of the player
        
    Returns:
        Dictionary with player statistics
    """
    return stats

# Use descriptive variable names
player_data = get_player_stats("Roger Federer")

# Type hints for function signatures
def process_rankings(week: str, limit: int = 100) -> list[dict]:
    pass
```

### FastAPI

```python
# Use Pydantic models for request/response
class PlayerRequest(BaseModel):
    player: str = Field(..., description="Player name")

@router.post("/player-stats")
async def get_stats(request: PlayerRequest):
    return {"ok": True, "result": stats}
```

### Comments

- Use docstrings for functions and classes
- Inline comments for complex logic
- Keep comments up-to-date with code changes

## 🐛 Reporting Issues

### Bug Reports

Please include:
1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Exact steps to reproduce the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: 
   - OS (Linux, macOS, Windows)
   - Python version
   - Browser (if web-related)
6. **Logs**: Any error messages or logs

### Feature Requests

Please include:
1. **Description**: Clear description of the feature
2. **Use Case**: Why is this feature needed?
3. **Proposed Solution**: How could this be implemented?
4. **Alternatives**: Any alternative solutions considered?

## 📝 Documentation

When adding features, please update:

- **README.md**: For user-facing changes
- **docs/**: For technical documentation
- **Code comments**: For implementation details
- **CHANGELOG.md**: For all changes

## ✅ Checklist Before Submitting

- [ ] Code follows project style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with main
- [ ] No merge conflicts

## 🤝 Code Review Process

1. Maintainers will review your PR
2. They may request changes or ask questions
3. Address feedback and push updates
4. Once approved, your PR will be merged
5. Your contribution will be credited in CHANGELOG.md

## 💡 Tips

- Start small - fix bugs or improve documentation first
- Ask questions - open an issue to discuss large changes
- Be patient - reviews may take a few days
- Be respectful - follow the code of conduct

## 📧 Questions?

Open an issue on GitHub with the "question" label.

---

Thank you for contributing to ATP Rankings Data Visualization! 🎾
