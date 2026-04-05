# AstroScope Cleanup Scripts

This document describes the cleanup scripts available for maintaining a clean development environment.

## Quick Cleanup

For immediate cleanup before testing or committing:

```bash
# Option 1: Use the bash wrapper (fastest)
./clean.sh

# Option 2: Run the Python script directly
python3 clean_cache.py

# Option 3: Make it executable and run
chmod +x clean_cache.py
./clean_cache.py
```

## What Gets Cleaned

The cleanup scripts remove:

### Python-related
- `__pycache__` directories
- `*.pyc` compiled Python files
- `*.pyo` optimization files
- `*.egg-info` directories
- `build/` and `dist/` directories

### Logs and Temporary Files
- All `.log` files in `logs/` and `mobile_app/logs/`
- JSON debug export files
- `temp_report.txt`
- `*.tmp` files
- Backup files (`*~`)
- Vim swap files (`*.swp`)

### Test and Development Files
- Test temporary plots in `tests/temp_plots/`
- Regression test results in `tests/regression/`
- Temporary baseline plots

### System Files
- `.DS_Store` files (macOS)
- `Thumbs.db` files (Windows)

### IDE and Editor Files
- `.vscode/.ropeproject`
- `.idea/` (PyCharm)
- `.ropeproject/`
- `.ipynb_checkpoints/` (Jupyter)

### Coverage and Profiling
- `.coverage*` files
- `*.prof` files

### Application Caches
- Matplotlib cache
- Astropy cache (if in project)

## When to Use

### Before Testing
```bash
./clean.sh && python3 mobile_app/main.py
```

### Before Committing
```bash
./clean.sh && git add . && git commit -m "Your commit message"
```

### After Development Session
```bash
./clean.sh
```

## Script Details

### `clean_cache.py`
- Comprehensive Python script with detailed progress reporting
- Safe removal with error handling
- Shows summary of operations performed
- Displays project size after cleanup

### `clean.sh`
- Simple bash wrapper for quick access
- Minimal output for fast cleanup

### `utilities/clean_cache.py`
- Legacy cleanup script (still functional)
- Located in utilities directory

## Safety Features

- All operations are safe and reversible
- No source code or important data files are removed
- Error handling prevents script crashes
- Warnings shown for any failed operations
- Preserves important files like:
  - Source code (`.py`, `.json`, `.md`)
  - Configuration files
  - Data catalogs
  - Documentation

## Example Output

```
🧹 AstroScope Cache and Log Cleanup
========================================

[1/26] Cleaning Python cache directories (__pycache__)...
✅ No items found to remove

[2/26] Cleaning Compiled Python files (*.pyc)...
✅ Removed 15 items

...

========================================
🎯 Cleanup Summary:
   Successful operations: 26/26
✅ All cleanup operations completed successfully!
🚀 Environment is now clean for testing or committing.
📊 Current project size: 10M
```

## Integration with Development Workflow

Add to your development routine:

1. **Start of session**: `./clean.sh` (optional, for clean start)
2. **Before testing**: `./clean.sh` (recommended)
3. **Before committing**: `./clean.sh` (highly recommended)
4. **End of session**: `./clean.sh` (good practice)

## Troubleshooting

If the script fails:
1. Check file permissions: `ls -la clean_cache.py clean.sh`
2. Make executable: `chmod +x clean_cache.py clean.sh`
3. Run with Python directly: `python3 clean_cache.py`
4. Check for file locks or permissions issues

## Customization

To add custom cleanup operations, edit `clean_cache.py` and add entries to the `cleanup_operations` list following the existing pattern. 