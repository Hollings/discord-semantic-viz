#!/usr/bin/env python3
"""Save hash of exports folder after successful pipeline run."""

import hashlib
from pathlib import Path

EXPORTS_DIR = Path('/app/exports')
HASH_FILE = Path('/app/output/.exports_hash')

def main():
    files = sorted(EXPORTS_DIR.glob('*.json'))
    hasher = hashlib.md5()
    for f in files:
        stat = f.stat()
        hasher.update(f"{f.name}:{stat.st_size}:{int(stat.st_mtime)}".encode())
    HASH_FILE.write_text(hasher.hexdigest())
    print("Cache hash saved")

if __name__ == '__main__':
    main()
