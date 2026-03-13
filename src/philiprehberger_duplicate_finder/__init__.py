"""Content-hash duplicate file detection with two-pass efficiency."""

from __future__ import annotations

import fnmatch
import hashlib
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal

__all__ = ["find_duplicates", "DuplicateGroup"]

HashAlgorithm = Literal["sha256", "md5", "sha1"]

PARTIAL_HASH_SIZE = 65536  # 64KB for partial hashing


@dataclass
class DuplicateGroup:
    """A group of files that are duplicates of each other."""

    paths: list[Path]
    size: int
    hash: str

    @property
    def count(self) -> int:
        return len(self.paths)

    @property
    def wasted_bytes(self) -> int:
        return self.size * (self.count - 1)


def _hash_file(
    path: Path,
    algorithm: HashAlgorithm = "sha256",
    partial: bool = False,
) -> str:
    h = hashlib.new(algorithm)
    try:
        with open(path, "rb") as f:
            if partial:
                # Read first chunk
                chunk = f.read(PARTIAL_HASH_SIZE)
                if chunk:
                    h.update(chunk)
                # Read last chunk
                file_size = path.stat().st_size
                if file_size > PARTIAL_HASH_SIZE * 2:
                    f.seek(-PARTIAL_HASH_SIZE, 2)
                    chunk = f.read(PARTIAL_HASH_SIZE)
                    if chunk:
                        h.update(chunk)
            else:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def find_duplicates(
    paths: str | Path | list[str | Path],
    *,
    min_size: int = 1,
    max_size: int | None = None,
    extensions: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
    algorithm: HashAlgorithm = "sha256",
    recursive: bool = True,
    follow_symlinks: bool = False,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[DuplicateGroup]:
    """Find duplicate files across one or more directories.

    Uses a two-pass approach:
    1. Group by file size (fast, eliminates most files)
    2. Hash only size-matched files (uses partial hashing for large files first)

    Args:
        paths: Directory or list of directories to scan.
        min_size: Minimum file size in bytes to consider.
        max_size: Maximum file size in bytes to consider.
        extensions: Only consider files with these extensions (e.g., [".jpg", ".png"]).
        exclude_patterns: Directory/file name patterns to skip (e.g., [".git", "node_modules"]).
        algorithm: Hash algorithm to use.
        recursive: Whether to scan subdirectories.
        follow_symlinks: Whether to follow symbolic links.
        on_progress: Callback(current, total) for progress tracking.

    Returns:
        List of DuplicateGroup objects, sorted by wasted bytes (largest first).
    """
    if isinstance(paths, (str, Path)):
        paths = [paths]

    # Normalize extensions
    ext_set = None
    if extensions:
        ext_set = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in extensions}

    # Collect all files
    all_files: list[Path] = []
    seen_inodes: set[tuple[int, int]] = set()
    for p in paths:
        root = Path(p).expanduser().resolve()
        if not root.is_dir():
            continue
        iterator = root.rglob("*") if recursive else root.iterdir()
        for fp in iterator:
            if not fp.is_file():
                continue
            if not follow_symlinks and fp.is_symlink():
                continue
            if exclude_patterns and any(
                fnmatch.fnmatch(part, pat)
                for part in fp.parts
                for pat in exclude_patterns
            ):
                continue
            if ext_set and fp.suffix.lower() not in ext_set:
                continue
            try:
                stat = fp.stat()
                size = stat.st_size
            except OSError:
                continue
            # Skip hard links to already-seen files
            inode_key = (stat.st_dev, stat.st_ino)
            if inode_key in seen_inodes:
                continue
            seen_inodes.add(inode_key)
            if size < min_size:
                continue
            if max_size is not None and size > max_size:
                continue
            all_files.append(fp)

    total_files = len(all_files)

    # Pass 1: Group by size
    size_groups: dict[int, list[Path]] = defaultdict(list)
    for fp in all_files:
        try:
            size_groups[fp.stat().st_size].append(fp)
        except OSError:
            continue

    # Keep only groups with 2+ files
    candidates: list[tuple[int, list[Path]]] = [
        (size, files) for size, files in size_groups.items() if len(files) > 1
    ]

    # Pass 2: Hash files in same-size groups
    results: list[DuplicateGroup] = []
    processed = 0

    for size, files in candidates:
        # For large files, do partial hash first
        use_partial = size > PARTIAL_HASH_SIZE * 4

        if use_partial:
            partial_groups: dict[str, list[Path]] = defaultdict(list)
            for fp in files:
                h = _hash_file(fp, algorithm, partial=True)
                if h:
                    partial_groups[h].append(fp)
                processed += 1
                if on_progress:
                    on_progress(processed, total_files)

            # Full hash only partial-hash matches
            for partial_hash, partial_files in partial_groups.items():
                if len(partial_files) < 2:
                    continue
                full_groups: dict[str, list[Path]] = defaultdict(list)
                for fp in partial_files:
                    h = _hash_file(fp, algorithm, partial=False)
                    if h:
                        full_groups[h].append(fp)
                for full_hash, matched in full_groups.items():
                    if len(matched) >= 2:
                        results.append(DuplicateGroup(
                            paths=sorted(matched),
                            size=size,
                            hash=full_hash,
                        ))
        else:
            hash_groups: dict[str, list[Path]] = defaultdict(list)
            for fp in files:
                h = _hash_file(fp, algorithm, partial=False)
                if h:
                    hash_groups[h].append(fp)
                processed += 1
                if on_progress:
                    on_progress(processed, total_files)

            for file_hash, matched in hash_groups.items():
                if len(matched) >= 2:
                    results.append(DuplicateGroup(
                        paths=sorted(matched),
                        size=size,
                        hash=file_hash,
                    ))

    # Sort by wasted bytes descending
    results.sort(key=lambda g: g.wasted_bytes, reverse=True)
    return results
