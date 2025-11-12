#!/usr/bin/env python3
"""
Create timestamped backups of a SQLite database safely.

Features:
- Uses sqlite3 Connection.backup for a consistent copy when possible.
- Creates a `backups/` directory by default and writes files like
  `backups/momentum-2025-11-12T15-30-00.db` (colons replaced with dashes).
- Optional gzip compression (`--compress`).
- Optional retention (`--keep N`) to prune old backups.

Usage examples:
  python scripts/maintenance/backup_db.py
  python scripts/maintenance/backup_db.py --src momentum.db --compress --keep 5

"""
from __future__ import annotations

import argparse
import gzip
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import List


def timestamped_name(src: Path) -> str:
    now = datetime.utcnow().isoformat(timespec="seconds")
    # Replace characters that are problematic in filenames
    safe_ts = now.replace(":", "-")
    return f"{src.stem}-{safe_ts}{src.suffix}"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def backup_sqlite(src: Path, dest: Path) -> None:
    """Use sqlite3 backup API to copy src -> dest for a consistent snapshot."""
    # Connect to source and destination and use backup
    # If source is not a valid SQLite DB this will raise an error.
    src_conn = sqlite3.connect(str(src))
    try:
        dest_conn = sqlite3.connect(str(dest))
        try:
            src_conn.backup(dest_conn)
        finally:
            dest_conn.close()
    finally:
        src_conn.close()


def compress_file(path: Path) -> Path:
    gz_path = path.with_suffix(path.suffix + ".gz")
    with path.open("rb") as f_in, gzip.open(gz_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    path.unlink()
    return gz_path


def prune_backups(backups_dir: Path, pattern: str, keep: int) -> List[Path]:
    # Find files matching pattern (simple prefix search)
    files = sorted([p for p in backups_dir.iterdir() if p.is_file() and p.name.startswith(pattern)], key=lambda p: p.stat().st_mtime, reverse=True)
    removed: List[Path] = []
    for old in files[keep:]:
        try:
            old.unlink()
            removed.append(old)
        except Exception:
            # ignore failures but report later
            pass
    return removed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backup a SQLite database into backups/ with timestamped filename")
    parser.add_argument("--src", "-s", default="momentum.db", help="Source SQLite DB file (default: momentum.db)")
    parser.add_argument("--dest", "-d", help="Destination file path (default: backups/<timestamped>)")
    parser.add_argument("--compress", action="store_true", help="Compress the backup with gzip (.gz)")
    parser.add_argument("--keep", type=int, default=0, help="Keep only the most recent N backups (0 = keep all)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    src = Path(args.src)
    if not src.exists():
        print(f"Source DB not found: {src}")
        return 2

    backups_dir = Path("backups")
    ensure_dir(backups_dir)

    if args.dest:
        dest = Path(args.dest)
        if dest.is_dir():
            print("Error: --dest must be a file path, not a directory")
            return 3
    else:
        name = timestamped_name(src)
        dest = backups_dir / name

    if args.dry_run:
        print(f"DRY RUN: would back up {src} -> {dest}")
        if args.compress:
            print(f"DRY RUN: would compress {dest} to {dest}.gz")
        if args.keep and args.keep > 0:
            print(f"DRY RUN: would keep the most recent {args.keep} backups and prune others")
        return 0

    try:
        print(f"Backing up {src} -> {dest}...")
        backup_sqlite(src, dest)
    except sqlite3.DatabaseError as e:
        print(f"SQLite error during backup: {e}")
        return 4
    except Exception as e:
        print(f"Unexpected error during backup: {e}")
        return 5

    final_path = dest
    if args.compress:
        try:
            print(f"Compressing {dest}...")
            final_path = compress_file(dest)
        except Exception as e:
            print(f"Compression failed: {e}")
            # keep the uncompressed file if compression fails

    print(f"Backup created: {final_path}")

    if args.keep and args.keep > 0:
        pattern = src.stem  # e.g., 'momentum'
        removed = prune_backups(backups_dir, pattern, args.keep)
        if removed:
            print("Pruned old backups:")
            for p in removed:
                print(" -", p)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
