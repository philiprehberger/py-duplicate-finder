# philiprehberger-duplicate-finder

[![Tests](https://github.com/philiprehberger/py-duplicate-finder/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-duplicate-finder/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-duplicate-finder.svg)](https://pypi.org/project/philiprehberger-duplicate-finder/)
[![GitHub release](https://img.shields.io/github/v/release/philiprehberger/py-duplicate-finder)](https://github.com/philiprehberger/py-duplicate-finder/releases)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-duplicate-finder)](https://github.com/philiprehberger/py-duplicate-finder/commits/main)
[![License](https://img.shields.io/github/license/philiprehberger/py-duplicate-finder)](LICENSE)
[![Bug Reports](https://img.shields.io/github/issues/philiprehberger/py-duplicate-finder/bug)](https://github.com/philiprehberger/py-duplicate-finder/issues?q=is%3Aissue+is%3Aopen+label%3Abug)
[![Feature Requests](https://img.shields.io/github/issues/philiprehberger/py-duplicate-finder/enhancement)](https://github.com/philiprehberger/py-duplicate-finder/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ec6cb9)](https://github.com/sponsors/philiprehberger)

Content-hash duplicate file detection with two-pass efficiency.

## Installation

```bash
pip install philiprehberger-duplicate-finder
```

## Usage

### Finding Duplicates

```python
from philiprehberger_duplicate_finder import find_duplicates

# Find duplicates in a directory
groups = find_duplicates("~/Documents")

for group in groups:
    print(f"Size: {group.size} bytes, {group.count} copies, wasted: {group.wasted_bytes} bytes")
    for path in group.paths:
        print(f"  {path}")
```

### Filtering Options

```python
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

### Smart Keep/Delete Suggestions

```python
for group in groups:
    # Keep the most recently modified file
    keep = group.keep_newest()
    print(f"Keep: {keep}")

    # Or keep the file with the shortest path (shallowest)
    keep = group.keep_shortest_path()
    print(f"Keep: {keep}")

    # Get the list of files safe to delete
    to_delete = group.deletable(strategy="newest")
    for path in to_delete:
        print(f"  Delete: {path}")
```

## API

| Function / Class | Description |
|------------------|-------------|
| `find_duplicates(paths, ...)` | Find duplicate files using a two-pass size-then-hash approach |
| `DuplicateGroup` | A group of duplicate files with `paths`, `size`, `hash`, `count`, and `wasted_bytes` |
| `DuplicateGroup.keep_newest()` | Return the path with the most recent modification time |
| `DuplicateGroup.keep_shortest_path()` | Return the path with the shortest string length |
| `DuplicateGroup.deletable(strategy)` | Return all paths except the one to keep (`"newest"` or `"shortest_path"`) |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this package useful, consider giving it a star on GitHub — it helps motivate continued maintenance and development.

[![LinkedIn](https://img.shields.io/badge/Philip%20Rehberger-LinkedIn-0A66C2?logo=linkedin)](https://www.linkedin.com/in/philiprehberger)
[![More packages](https://img.shields.io/badge/more-open%20source%20packages-blue)](https://philiprehberger.com/open-source-packages)

## License

[MIT](LICENSE)
