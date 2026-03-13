import pytest
from pathlib import Path
from philiprehberger_duplicate_finder import find_duplicates, DuplicateGroup


def _make_file(path: Path, content: str = "hello"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_no_duplicates(tmp_path):
    _make_file(tmp_path / "a.txt", "aaa")
    _make_file(tmp_path / "b.txt", "bbb")
    result = find_duplicates(tmp_path)
    assert result == []


def test_finds_duplicates(tmp_path):
    _make_file(tmp_path / "a.txt", "same content")
    _make_file(tmp_path / "b.txt", "same content")
    result = find_duplicates(tmp_path)
    assert len(result) == 1
    assert result[0].count == 2


def test_duplicate_group_properties(tmp_path):
    content = "x" * 100
    _make_file(tmp_path / "a.txt", content)
    _make_file(tmp_path / "b.txt", content)
    _make_file(tmp_path / "c.txt", content)
    result = find_duplicates(tmp_path)
    assert len(result) == 1
    group = result[0]
    assert group.count == 3
    assert group.wasted_bytes == group.size * 2


def test_min_size_filter(tmp_path):
    _make_file(tmp_path / "a.txt", "x")
    _make_file(tmp_path / "b.txt", "x")
    result = find_duplicates(tmp_path, min_size=1000)
    assert result == []


def test_max_size_filter(tmp_path):
    content = "x" * 2000
    _make_file(tmp_path / "a.txt", content)
    _make_file(tmp_path / "b.txt", content)
    result = find_duplicates(tmp_path, max_size=100)
    assert result == []


def test_extension_filter(tmp_path):
    _make_file(tmp_path / "a.txt", "same")
    _make_file(tmp_path / "b.txt", "same")
    _make_file(tmp_path / "c.jpg", "same")
    result = find_duplicates(tmp_path, extensions=[".txt"])
    assert len(result) == 1
    paths = [str(p) for p in result[0].paths]
    assert all(".txt" in p for p in paths)


def test_recursive(tmp_path):
    _make_file(tmp_path / "a.txt", "dup")
    _make_file(tmp_path / "sub" / "b.txt", "dup")
    result = find_duplicates(tmp_path, recursive=True)
    assert len(result) == 1


def test_non_recursive(tmp_path):
    _make_file(tmp_path / "a.txt", "dup")
    _make_file(tmp_path / "sub" / "b.txt", "dup")
    result = find_duplicates(tmp_path, recursive=False)
    assert result == []


def test_empty_directory(tmp_path):
    result = find_duplicates(tmp_path)
    assert result == []


def test_multiple_directories(tmp_path):
    d1 = tmp_path / "dir1"
    d2 = tmp_path / "dir2"
    _make_file(d1 / "a.txt", "dup")
    _make_file(d2 / "b.txt", "dup")
    result = find_duplicates([d1, d2])
    assert len(result) == 1


def test_progress_callback(tmp_path):
    _make_file(tmp_path / "a.txt", "dup")
    _make_file(tmp_path / "b.txt", "dup")
    calls = []
    find_duplicates(tmp_path, on_progress=lambda cur, tot: calls.append((cur, tot)))
    assert len(calls) > 0


# --- New tests for v0.2.0 ---


def test_exclude_patterns(tmp_path):
    _make_file(tmp_path / "a.txt", "dup")
    _make_file(tmp_path / "node_modules" / "b.txt", "dup")
    result = find_duplicates(tmp_path, exclude_patterns=["node_modules"])
    assert result == []


def test_exclude_patterns_dot_git(tmp_path):
    _make_file(tmp_path / "a.txt", "same")
    _make_file(tmp_path / ".git" / "objects" / "b.txt", "same")
    _make_file(tmp_path / "c.txt", "same")
    result = find_duplicates(tmp_path, exclude_patterns=[".git"])
    assert len(result) == 1
    paths = [str(p) for p in result[0].paths]
    assert not any(".git" in p for p in paths)


def test_single_file(tmp_path):
    _make_file(tmp_path / "only.txt", "alone")
    result = find_duplicates(tmp_path)
    assert result == []


def test_extension_without_dot(tmp_path):
    _make_file(tmp_path / "a.txt", "same")
    _make_file(tmp_path / "b.txt", "same")
    _make_file(tmp_path / "c.jpg", "same")
    result = find_duplicates(tmp_path, extensions=["txt"])
    assert len(result) == 1


def test_md5_algorithm(tmp_path):
    _make_file(tmp_path / "a.txt", "dup")
    _make_file(tmp_path / "b.txt", "dup")
    result = find_duplicates(tmp_path, algorithm="md5")
    assert len(result) == 1
    assert len(result[0].hash) == 32  # MD5 produces 32 hex chars


def test_multiple_duplicate_groups(tmp_path):
    _make_file(tmp_path / "a1.txt", "group_a")
    _make_file(tmp_path / "a2.txt", "group_a")
    _make_file(tmp_path / "b1.txt", "group_b_longer")
    _make_file(tmp_path / "b2.txt", "group_b_longer")
    result = find_duplicates(tmp_path)
    assert len(result) == 2


def test_sorted_by_wasted_bytes(tmp_path):
    _make_file(tmp_path / "small1.txt", "sm")
    _make_file(tmp_path / "small2.txt", "sm")
    _make_file(tmp_path / "big1.txt", "x" * 1000)
    _make_file(tmp_path / "big2.txt", "x" * 1000)
    result = find_duplicates(tmp_path)
    assert len(result) == 2
    assert result[0].wasted_bytes >= result[1].wasted_bytes


def test_string_path(tmp_path):
    _make_file(tmp_path / "a.txt", "dup")
    _make_file(tmp_path / "b.txt", "dup")
    result = find_duplicates(str(tmp_path))
    assert len(result) == 1
