# robust-outliers

[![PyPI version](https://img.shields.io/pypi/v/trysac-robust-outliers)](https://pypi.org/project/trysac-robust-outliers/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-robust-outliers)](LICENSE)
[![CI](https://github.com/Trysac/u268-robust-outliers/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u268-robust-outliers/actions/workflows/ci.yml)

Robust outlier detection with modified z-scores from the median absolute deviation, Tukey fences on inclusive quartiles and a Hampel filter for series, with explicit bounds

## Problem

Mean and standard deviation outlier rules fail on exactly the data that has outliers, because one extreme value inflates the deviation and hides itself. This library implements modified z-scores from the median absolute deviation (MAD), Tukey fences on inclusive quartiles and a Hampel filter. It returns the outlier indices and the center, scale, lower and upper bounds used.

## Install

```sh
pip install trysac-robust-outliers
# or
uv add trysac-robust-outliers
```

Requires Python 3.10 or newer. No runtime dependencies; the package uses the standard library (`statistics`, `math`, `logging`, `argparse`).

## Usage

```python
from robust_outliers import detect, modified_z_scores, hampel

result = detect([10, 12, 11, 13, 12, 11, 95])
print(result.indices, result.center, result.scale, round(result.lower, 4), round(result.upper, 4))
# (6,) 12 1 6.811 17.189

print([round(z, 4) for z in modified_z_scores([10, 12, 11, 13, 12, 11, 95])])
print(hampel([10, 11, 10, 12, 50, 11, 10, 12], half_window=2))
```

On the command line, `python -m robust_outliers` reads one number per line from stdin, ignores blank lines and prints `<index>\t<value>` for every outlier. It exits 0 when no outliers are found, 1 when outliers are found and 2 on usage or input errors. Options: `--method mad|iqr`, `--threshold X`, `--hampel N`.

## Public API

- `Result` is a frozen dataclass with `indices: tuple[int, ...]`, `center: float`, `scale: float`, `lower: float`, `upper: float` and `method: Literal["mad", "iqr"]`. Indices are zero-based positions in the input sequence, ascending.
- `modified_z_scores(values: Sequence[float]) -> list[float]` returns modified z-scores using the MAD. When the MAD is zero it uses the mean absolute deviation; when both are zero all scores are `0.0`.
- `detect(values: Sequence[float], *, method: Literal["mad", "iqr"] = "mad", threshold: float | None = None) -> Result` detects outliers using MAD or IQR. MAD defaults to threshold `3.5`; IQR defaults to `1.5` as the Tukey fence multiplier. Outliers are strictly outside the computed bounds. For IQR, quartiles use `statistics.quantiles(..., n=4, method="inclusive")`; a single value gives no outliers.
- `hampel(series: Sequence[float], *, half_window: int = 3, n_sigmas: float = 3.0) -> list[int]` returns the indices of Hampel-filter outliers. Each window has size `2 * half_window + 1`, truncated at the edges, and a point is flagged when `abs(x - median(window)) > n_sigmas * 1.4826 * MAD(window)`. `half_window` must be an integer >= 1; `n_sigmas` must be a positive finite number.
- `OutlierError` has a `code` attribute with one of `empty_input`, `non_finite`, `invalid_value`, `invalid_options`, `input_too_large`.

Limits: values must be finite `int` or `float` values and `bool` is rejected; at most `10_000_000` values are accepted. The CLI reads at most `104_857_600` bytes from stdin.

## Why not z-scores or scipy

Mean and standard-deviation z-scores are not used because one extreme value inflates the standard deviation and hides itself. This package is robust by default, has no runtime dependencies, and states and returns the constants and quartile method it used; scipy is not required.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [stack](docs/STACK.md)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
