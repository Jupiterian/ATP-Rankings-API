# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Optional Live Tennis API source for the weekly ATP top 100 update, selected
  with `LIVETENNIS_API_KEY` (PRO plan required). Validates publication dates and
  complete snapshots, preserves existing weeks, and inserts each new week atomically.
- Offline regression tests for the source and weekly updater selection.

## [1.0.0] - 2025-11-02

###  Major Reorganization

#### Added
- **Organized Directory Structure**: Split files into logical directories
  - `src/` - Core application code (main.py, services.py, mcp_router.py)
  - `scripts/` - Utility and maintenance scripts
  - `docs/` - All documentation files
  - `templates/` - HTML templates (unchanged)
  - `tests/` - Test files (unchanged)
  - `Examples/` - Example visualizations (unchanged)

- **Python Package Structure**: Added `src/__init__.py` to make src a proper Python package
- **Comprehensive README**: Completely rewritten with clear structure, quick start, and better organization
- **CHANGELOG**: This file to track project changes

#### Changed
- **Import Paths**: Updated all imports to use `src.` prefix
  - `main.py` imports from `src.services` and `src.mcp_router`
  - `mcp_router.py` imports from `src.services`
  - `tests/test_mcp.py` imports from `src.main`

- **Deployment Configuration**:
  - Updated `Procfile` to use `src.main:app`
  - Updated `Dockerfile` to copy `src/` directory and use `src.main:app`

- **File Locations**:
  - Moved `main.py`, `services.py`, `mcp_router.py`, `mcp_manifest.json` → `src/`
  - Moved `analyze.py`, `generate.py`, `filler.py`, `debug.py` → `scripts/`
  - Moved `test_mcp.sh`, `test_render_mcp.py`, `keep_alive.py`, `deploy.sh` → `scripts/`
  - Moved `MCP_README.md`, `MCP_DEPLOYMENT.md`, etc. → `docs/`

#### Removed
- **Cache Files**: Deleted `__pycache__/` directory
- **Scattered Files**: Cleaned up 17 files in root directory → organized into 7 directories

#### Improved
- **.gitignore**: Added more patterns for temporary files and OS-specific files
- **README.md**: 
  - Clear project structure diagram
  - Better quick start instructions
  - Organized sections with emojis
  - Links to all documentation
  - Deployment instructions
  - Testing instructions

###  New Directory Structure

```
ATP-Rankings-Data-Visualization/
├── src/                  # Core application
├── scripts/              # Utilities
├── docs/                 # Documentation
├── templates/            # HTML templates
├── tests/                # Test suite
└── Examples/             # Visualizations
```

###  Migration Notes

If you have existing deployments or scripts:

1. **Update uvicorn command**:
   ```bash
   # Old
   uvicorn main:app
   
   # New
   uvicorn src.main:app
   ```

2. **Update imports in custom scripts**:
   ```python
   # Old
   from main import app
   from services import get_player_factfile
   
   # New
   from src.main import app
   from src.services import get_player_factfile
   ```

3. **Render/Heroku deployments**: 
   - `Procfile` already updated, no action needed
   - Just push to trigger redeploy

4. **Docker deployments**:
   - `Dockerfile` already updated
   - Rebuild image: `docker build -t atp-rankings .`

###  Testing

All tests pass with new structure:
```bash
pytest tests/test_mcp.py -v
```

All syntax checks pass:
```bash
python3 -m py_compile src/main.py src/services.py src/mcp_router.py
```

---

## [Previous Versions]

For previous changes, see git history.
