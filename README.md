# robust-outliers

[![PyPI version](https://img.shields.io/pypi/v/trysac-robust-outliers)](https://pypi.org/project/trysac-robust-outliers/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-robust-outliers)](LICENSE)
[![CI](https://github.com/Trysac/u268-robust-outliers/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u268-robust-outliers/actions/workflows/ci.yml)

Robust outlier detection with modified z-scores from the median absolute deviation, Tukey fences on inclusive quartiles and a Hampel filter for series, with explicit bounds

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-robust-outliers
# or
uv add trysac-robust-outliers
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import robust_outliers

# normalize() trims surrounding whitespace and lower-cases the text.
print(robust_outliers.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    robust_outliers.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
