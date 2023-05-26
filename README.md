# philiprehberger-duplicate-finder

[![Tests](https://github.com/philiprehberger/py-duplicate-finder/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-duplicate-finder/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-duplicate-finder.svg)](https://pypi.org/project/philiprehberger-duplicate-finder/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-duplicate-finder)](https://github.com/philiprehberger/py-duplicate-finder/commits/main)

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

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-duplicate-finder)

🐛 [Report issues](https://github.com/philiprehberger/py-duplicate-finder/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-duplicate-finder/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
