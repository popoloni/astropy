#!/usr/bin/env python3
"""
Clean Cache Utility
Removes all __pycache__ directories from the codebase
"""

import os
import shutil
from pathlib import Path

def clean_pycache_directories():
    """Remove all __pycache__ directories recursively"""
    removed_count = 0
    total_size = 0
    
    print("🧹 Cleaning up Python cache directories...")
    
    # Walk through all directories
    for root, dirs, files in os.walk('.'):
        # Check if __pycache__ is in the current directory
        if '__pycache__' in dirs:
            pycache_path = Path(root) / '__pycache__'
            
            # Calculate size before deletion
            try:
                cache_size = sum(f.stat().st_size for f in pycache_path.rglob('*') if f.is_file())
                total_size += cache_size
                
                # Remove the directory
                shutil.rmtree(pycache_path)
                print(f"  ✅ Removed: {pycache_path}")
                removed_count += 1
                
                # Remove from dirs list to prevent os.walk from entering it
                dirs.remove('__pycache__')
                
            except Exception as e:
                print(f"  ❌ Error removing {pycache_path}: {e}")
    
    # Summary
    if removed_count > 0:
        size_mb = total_size / (1024 * 1024)
        print(f"\n🎉 Cleanup complete!")
        print(f"   • Removed {removed_count} __pycache__ directories")
        print(f"   • Freed up {size_mb:.2f} MB of disk space")
    else:
        print("\n✨ No __pycache__ directories found - codebase is already clean!")

if __name__ == "__main__":
    clean_pycache_directories() 