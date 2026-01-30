#!/usr/bin/env python3
"""
Check if pipeline needs to run based on exports folder hash.
Returns exit code 0 if pipeline should run, 1 if cached output is valid.
"""

import hashlib
import os
import sys
from pathlib import Path

EXPORTS_DIR = Path('/app/exports')
OUTPUT_DIR = Path('/app/output')
HASH_FILE = OUTPUT_DIR / '.exports_hash'
VIZ_DATA = OUTPUT_DIR / 'viz_data.json'

def get_exports_hash():
    """Generate hash of exports folder contents (filenames + sizes + mtimes)."""
    if not EXPORTS_DIR.exists():
        return None

    files = sorted(EXPORTS_DIR.glob('*.json'))
    if not files:
        return None

    hasher = hashlib.md5()
    for f in files:
        stat = f.stat()
        # Include filename, size, and mtime in hash
        hasher.update(f"{f.name}:{stat.st_size}:{int(stat.st_mtime)}".encode())

    return hasher.hexdigest()

def main():
    current_hash = get_exports_hash()

    if current_hash is None:
        print("No export files found - pipeline needs to run")
        sys.exit(0)  # Run pipeline

    # Check if output exists
    if not VIZ_DATA.exists():
        print("No viz_data.json found - pipeline needs to run")
        sys.exit(0)  # Run pipeline

    # Check if hash matches
    if HASH_FILE.exists():
        stored_hash = HASH_FILE.read_text().strip()
        if stored_hash == current_hash:
            print("Exports unchanged and viz_data.json exists - skipping pipeline")
            sys.exit(1)  # Skip pipeline

    print("Exports changed - pipeline needs to run")
    sys.exit(0)  # Run pipeline

if __name__ == '__main__':
    main()
