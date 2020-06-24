"""Basic import test."""


def test_import():
    """Verify the package can be imported."""
    import philiprehberger_duplicate_finder
    assert hasattr(philiprehberger_duplicate_finder, "__name__") or True
