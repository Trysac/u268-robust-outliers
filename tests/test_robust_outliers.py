"""Behavior tests for the public API of robust_outliers."""

from __future__ import annotations

import pytest

import robust_outliers


def test_normalize_trims_and_lowercases() -> None:
    assert robust_outliers.normalize("  Hello World ") == "hello world"


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_normalize_rejects_blank_input(value: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        robust_outliers.normalize(value)


def test_version_is_semver() -> None:
    parts = robust_outliers.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
