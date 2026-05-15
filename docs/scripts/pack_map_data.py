#!/usr/bin/env python3
"""Pack the leaderboard map_data directory into a tar.gz archive.

Creates docs/source/_extra/leaderboard/map_data.tar.gz from the contents of
docs/source/_extra/leaderboard/map_data/.

Usage:
    python docs/scripts/pack_map_data.py
"""

import sys
import tarfile
from pathlib import Path

# Resolve project root (two levels above this script: docs/scripts/ -> docs/ -> project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LEADERBOARD_DIR = PROJECT_ROOT / "docs" / "source" / "_extra" / "leaderboard"
MAP_DATA_DIR = LEADERBOARD_DIR / "map_data"
ARCHIVE_PATH = LEADERBOARD_DIR / "map_data.tar.gz"


def main() -> int:
    if not MAP_DATA_DIR.is_dir():
        print(f"[pack_map_data] ERROR: map_data directory not found: {MAP_DATA_DIR}", file=sys.stderr)
        return 1

    files = sorted(MAP_DATA_DIR.rglob("*"))
    data_files = [f for f in files if f.is_file()]

    if not data_files:
        print(f"[pack_map_data] WARNING: no files found in {MAP_DATA_DIR}; archive not created.")
        return 0

    print(f"[pack_map_data] Packing {len(data_files)} files → {ARCHIVE_PATH}")
    with tarfile.open(ARCHIVE_PATH, "w:gz") as tf:
        for filepath in data_files:
            arcname = filepath.relative_to(LEADERBOARD_DIR)
            tf.add(filepath, arcname=str(arcname))

    size_kb = ARCHIVE_PATH.stat().st_size / 1024
    print(f"[pack_map_data] Done — {ARCHIVE_PATH.name} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
