#!/usr/bin/env python3
"""
AstroScope Cache and Log Cleanup Script
=======================================

This script cleans all caches, logs, temporary files, and generated content
to ensure a clean environment for testing or before committing changes.

Usage:
    python3 clean_cache.py
    
Or make it executable and run directly:
    chmod +x clean_cache.py
    ./clean_cache.py
"""

import os
import shutil
import glob
import sys
from pathlib import Path

def print_status(message, success=True):
    """Print status message with color coding"""
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

def safe_remove_dir(path):
    """Safely remove directory and its contents"""
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
            return True
    except Exception as e:
        print(f"⚠️  Warning: Could not remove {path}: {e}")
    return False

def safe_remove_file(path):
    """Safely remove a single file"""
    try:
        if os.path.exists(path):
            os.remove(path)
            return True
    except Exception as e:
        print(f"⚠️  Warning: Could not remove {path}: {e}")
    return False

def safe_remove_pattern(pattern):
    """Safely remove files matching a pattern"""
    try:
        files = glob.glob(pattern, recursive=True)
        removed_count = 0
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
                removed_count += 1
            elif os.path.isdir(file):
                shutil.rmtree(file)
                removed_count += 1
        return removed_count
    except Exception as e:
        print(f"⚠️  Warning: Could not remove pattern {pattern}: {e}")
        return 0

def main():
    """Main cleanup function"""
    print("🧹 AstroScope Cache and Log Cleanup")
    print("=" * 40)
    
    # Get the script directory (should be the project root)
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    cleanup_operations = [
        # Python cache cleanup
        {
            'name': 'Python cache directories (__pycache__)',
            'action': lambda: safe_remove_pattern('**/__pycache__'),
            'type': 'pattern'
        },
        {
            'name': 'Compiled Python files (*.pyc)',
            'action': lambda: safe_remove_pattern('**/*.pyc'),
            'type': 'pattern'
        },
        {
            'name': 'Python optimization files (*.pyo)',
            'action': lambda: safe_remove_pattern('**/*.pyo'),
            'type': 'pattern'
        },
        
        # Log file cleanup
        {
            'name': 'Main log files',
            'action': lambda: safe_remove_pattern('logs/*.log'),
            'type': 'pattern'
        },
        {
            'name': 'Mobile app log files',
            'action': lambda: safe_remove_pattern('mobile_app/logs/*.log'),
            'type': 'pattern'
        },
        {
            'name': 'Mobile app JSON debug exports',
            'action': lambda: safe_remove_pattern('mobile_app/logs/*.json'),
            'type': 'pattern'
        },
        
        # Temporary file cleanup
        {
            'name': 'Temporary report files',
            'action': lambda: safe_remove_file('temp_report.txt'),
            'type': 'file'
        },
        {
            'name': 'Temporary files (*.tmp)',
            'action': lambda: safe_remove_pattern('**/*.tmp'),
            'type': 'pattern'
        },
        {
            'name': 'Backup files (*~)',
            'action': lambda: safe_remove_pattern('**/*~'),
            'type': 'pattern'
        },
        {
            'name': 'Vim swap files (*.swp)',
            'action': lambda: safe_remove_pattern('**/*.swp'),
            'type': 'pattern'
        },
        
        # Test and development cleanup
        {
            'name': 'Test temporary plots',
            'action': lambda: safe_remove_pattern('tests/temp_plots/*.png'),
            'type': 'pattern'
        },
        {
            'name': 'Regression test results',
            'action': lambda: safe_remove_pattern('tests/regression/*.json'),
            'type': 'pattern'
        },
        {
            'name': 'Test baseline plots (if regenerating)',
            'action': lambda: safe_remove_pattern('tests/baseline_plots/*_temp.png'),
            'type': 'pattern'
        },
        
        # System file cleanup
        {
            'name': 'macOS .DS_Store files',
            'action': lambda: safe_remove_pattern('**/.DS_Store'),
            'type': 'pattern'
        },
        {
            'name': 'Windows Thumbs.db files',
            'action': lambda: safe_remove_pattern('**/Thumbs.db'),
            'type': 'pattern'
        },
        
        # IDE and editor cleanup
        {
            'name': 'VS Code settings cache',
            'action': lambda: safe_remove_dir('.vscode/.ropeproject'),
            'type': 'dir'
        },
        {
            'name': 'PyCharm cache',
            'action': lambda: safe_remove_dir('.idea'),
            'type': 'dir'
        },
        {
            'name': 'Rope project files',
            'action': lambda: safe_remove_dir('.ropeproject'),
            'type': 'dir'
        },
        
        # Package and environment cleanup
        {
            'name': 'Egg info directories',
            'action': lambda: safe_remove_pattern('**/*.egg-info'),
            'type': 'pattern'
        },
        {
            'name': 'Build directories',
            'action': lambda: safe_remove_pattern('**/build'),
            'type': 'pattern'
        },
        {
            'name': 'Distribution directories',
            'action': lambda: safe_remove_pattern('**/dist'),
            'type': 'pattern'
        },
        
        # Jupyter notebook cleanup
        {
            'name': 'Jupyter notebook checkpoints',
            'action': lambda: safe_remove_pattern('**/.ipynb_checkpoints'),
            'type': 'pattern'
        },
        
        # Coverage and profiling cleanup
        {
            'name': 'Coverage files',
            'action': lambda: safe_remove_pattern('**/.coverage*'),
            'type': 'pattern'
        },
        {
            'name': 'Profiling files',
            'action': lambda: safe_remove_pattern('**/*.prof'),
            'type': 'pattern'
        },
        
        # Application-specific cleanup
        {
            'name': 'Matplotlib cache',
            'action': lambda: safe_remove_dir(os.path.expanduser('~/.matplotlib')),
            'type': 'dir'
        },
        {
            'name': 'Astropy cache (if exists in project)',
            'action': lambda: safe_remove_dir('.astropy'),
            'type': 'dir'
        }
    ]
    
    # Execute cleanup operations
    total_operations = len(cleanup_operations)
    successful_operations = 0
    
    for i, operation in enumerate(cleanup_operations, 1):
        print(f"\n[{i}/{total_operations}] Cleaning {operation['name']}...")
        
        try:
            result = operation['action']()
            if operation['type'] == 'pattern' and isinstance(result, int):
                if result > 0:
                    print_status(f"Removed {result} items")
                    successful_operations += 1
                else:
                    print_status("No items found to remove")
                    successful_operations += 1
            elif operation['type'] in ['file', 'dir'] and result:
                print_status("Removed successfully")
                successful_operations += 1
            elif operation['type'] in ['file', 'dir'] and not result:
                print_status("Nothing to remove")
                successful_operations += 1
            else:
                print_status("Completed")
                successful_operations += 1
        except Exception as e:
            print_status(f"Failed: {e}", success=False)
    
    # Summary
    print("\n" + "=" * 40)
    print(f"🎯 Cleanup Summary:")
    print(f"   Successful operations: {successful_operations}/{total_operations}")
    
    if successful_operations == total_operations:
        print("✅ All cleanup operations completed successfully!")
        print("🚀 Environment is now clean for testing or committing.")
    else:
        failed = total_operations - successful_operations
        print(f"⚠️  {failed} operations had warnings (see details above)")
        print("🚀 Environment cleanup mostly completed.")
    
    # Optional: Show current directory size
    try:
        import subprocess
        result = subprocess.run(['du', '-sh', '.'], capture_output=True, text=True)
        if result.returncode == 0:
            size = result.stdout.strip().split()[0]
            print(f"📊 Current project size: {size}")
    except:
        pass  # du command not available or failed

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Cleanup failed with error: {e}")
        sys.exit(1) 