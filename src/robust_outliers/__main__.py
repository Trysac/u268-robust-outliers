"""Command-line interface for robust_outliers."""

from __future__ import annotations

import argparse
import sys

from . import OutlierError, detect, hampel

MAX_INPUT_BYTES = 104_857_600


def main(argv: list[str] | None = None) -> int:
    """Run the CLI.

    Reads one number per line from stdin. Blank lines are ignored.
    Prints ``index\\tvalue`` for each outlier. Returns 0 if no outliers,
    1 if outliers were found, 2 on usage or input errors.
    """
    parser = argparse.ArgumentParser(
        prog="python -m robust_outliers",
        description="Robust outlier detection from stdin (one value per line)",
    )
    parser.add_argument("--method", choices=("mad", "iqr"), default="mad", help="detection method")
    parser.add_argument("--threshold", type=float, help="threshold for MAD or IQR (positive)")
    parser.add_argument(
        "--hampel",
        type=int,
        metavar="N",
        help="run Hampel filter with half-window N instead of detect",
    )
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2

    if args.hampel is not None and args.hampel < 1:
        print("--hampel must be >= 1", file=sys.stderr)
        return 2

    try:
        data = sys.stdin.read()
    except Exception:
        return 2
    if len(data.encode("utf-8")) > MAX_INPUT_BYTES:
        print("input too large", file=sys.stderr)
        return 2

    parsed: list[tuple[str, float]] = []
    for line in data.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            value = float(stripped)
        except ValueError:
            print(f"invalid numeric value: {stripped!r}", file=sys.stderr)
            return 2
        parsed.append((stripped, value))

    values = [v for _, v in parsed]
    try:
        if args.hampel is not None:
            outliers = hampel(values, half_window=args.hampel, n_sigmas=3.0)
        else:
            result = detect(values, method=args.method, threshold=args.threshold)
            outliers = list(result.indices)
    except OutlierError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    for idx in outliers:
        original, _ = parsed[idx]
        print(f"{idx}\t{original}")
    return 1 if outliers else 0


if __name__ == "__main__":
    raise SystemExit(main())
