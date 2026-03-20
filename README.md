# philiprehberger-duplicate-finder

[![Tests](https://github.com/philiprehberger/py-duplicate-finder/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-duplicate-finder/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-duplicate-finder.svg)](https://pypi.org/project/philiprehberger-duplicate-finder/)
[![License](https://img.shields.io/github/license/philiprehberger/py-duplicate-finder)](LICENSE)

Content-hash duplicate file detection with two-pass efficiency.

## Installation

```bash
pip install philiprehberger-duplicate-finder
```

## Usage

```python
from philiprehberger_duplicate_finder import find_duplicates

# Find duplicates in a directory
groups = find_duplicates("~/Documents")

for group in groups:
    print(f"Size: {group.size} bytes, {group.count} copies, wasted: {group.wasted_bytes} bytes")
    for path in group.paths:
        print(f"  {path}")

# Multiple directories with filters
groups = find_duplicates(
    paths=["~/Documents", "~/Downloads"],
    min_size=1024,
    extensions=[".pdf", ".jpg", ".png"],
    algorithm="sha256",
)

# Progress tracking
groups = find_duplicates(
    "~/Pictures",
    on_progress=lambda current, total: print(f"{current}/{total}"),
)
```

### How it works

Two-pass approach for efficiency:
1. Groups files by size (fast — eliminates most files immediately)
2. Hashes only size-matched files (uses partial hashing for large files first)

Hard links to the same file are automatically detected and excluded from duplicate results.

## API

| Function / Class | Description |
|------------------|-------------|
| `find_duplicates(paths, *, min_size, max_size, extensions, exclude_patterns, algorithm, recursive, follow_symlinks, on_progress)` | Scan directories for duplicate files and return groups |

| Option | Default | Description |
|--------|---------|-------------|
| `min_size` | 1 | Minimum file size in bytes |
| `max_size` | None | Maximum file size in bytes |
| `extensions` | None | Filter by extensions |
| `exclude_patterns` | None | Directory/file patterns to skip (e.g., `[".git", "node_modules"]`) |
| `algorithm` | "sha256" | Hash algorithm (sha256, md5, sha1) |
| `recursive` | True | Scan subdirectories |
| `follow_symlinks` | False | Follow symbolic links |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
