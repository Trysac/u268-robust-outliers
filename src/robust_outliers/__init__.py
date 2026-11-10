"""Robust outlier detection with explicit bounds and robust statistics.

Provides modified z-scores using the median absolute deviation (MAD),
Tukey fences on inclusive quartiles, and a Hampel filter for time series.
"""

from __future__ import annotations

import logging
import math
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import fmean, median, quantiles
from typing import Literal

__all__ = ["OutlierError", "Result", "detect", "hampel", "modified_z_scores"]

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

MAX_VALUES = 10_000_000

OutlierCode = Literal[
    "empty_input",
    "non_finite",
    "invalid_value",
    "invalid_options",
    "input_too_large",
]


class OutlierError(Exception):
    """Error raised for invalid input or invalid options."""

    def __init__(self, code: OutlierCode, message: str | None = None) -> None:
        self.code = code
        super().__init__(message if message is not None else code)


@dataclass(frozen=True)
class Result:
    """Result of outlier detection.

    Indices are zero-based positions in the input sequence, ascending.
    """

    indices: tuple[int, ...]
    center: float
    scale: float
    lower: float
    upper: float
    method: Literal["mad", "iqr"]


def _validate_values(values: Sequence[float]) -> Sequence[float]:
    """Validate input sequence and return it unchanged."""
    if not isinstance(values, Sequence):
        values = tuple(values)
    if len(values) == 0:
        raise OutlierError("empty_input")
    if len(values) > MAX_VALUES:
        raise OutlierError(
            "input_too_large",
            f"input has {len(values)} values; maximum is {MAX_VALUES}",
        )
    for i, value in enumerate(values):
        if isinstance(value, bool):
            raise OutlierError("invalid_value", f"invalid value at index {i}: {value!r}")
        if not isinstance(value, (int, float)):
            raise OutlierError("invalid_value", f"invalid value at index {i}: {value!r}")
        if not math.isfinite(value):
            raise OutlierError("non_finite", f"non-finite value at index {i}")
    return values


def modified_z_scores(values: Sequence[float]) -> list[float]:
    """Return modified z-scores using the median absolute deviation (MAD).

    When the MAD is zero, the mean absolute deviation (MeanAD) is used as a
    fallback. If both are zero, all scores are 0.0.
    """
    validated = _validate_values(values)
    center = median(validated)
    deviations = [abs(x - center) for x in validated]
    mad = median(deviations)
    if mad > 0:
        return [0.6745 * (x - center) / mad for x in validated]
    mean_ad = fmean(deviations)
    if mean_ad > 0:
        return [(x - center) / (1.253314 * mean_ad) for x in validated]
    return [0.0] * len(validated)


def _detect_mad(values: Sequence[float], threshold: float) -> Result:
    center = median(values)
    deviations = [abs(x - center) for x in values]
    mad = median(deviations)
    indices: list[int] = []
    if mad > 0:
        scale = mad
        factor = 0.6745
        for i, x in enumerate(values):
            m_score = factor * (x - center) / mad
            if abs(m_score) > threshold:
                indices.append(i)
        lower = center - threshold * mad / factor
        upper = center + threshold * mad / factor
    else:
        mean_ad = fmean(deviations)
        if mean_ad > 0:
            scale = mean_ad
            factor = 1.253314
            for i, x in enumerate(values):
                m_score = (x - center) / (factor * mean_ad)
                if abs(m_score) > threshold:
                    indices.append(i)
            lower = center - threshold * factor * mean_ad
            upper = center + threshold * factor * mean_ad
        else:
            scale = 0.0
            lower = center
            upper = center
    return Result(tuple(indices), center, scale, lower, upper, "mad")


def _detect_iqr(values: Sequence[float], threshold: float) -> Result:
    if len(values) == 1:
        return Result((), values[0], 0.0, values[0], values[0], "iqr")
    q1, q2, q3 = quantiles(values, n=4, method="inclusive")
    iqr = q3 - q1
    lower = q1 - threshold * iqr
    upper = q3 + threshold * iqr
    indices = [i for i, x in enumerate(values) if x < lower or x > upper]
    return Result(tuple(indices), q2, iqr, lower, upper, "iqr")


def detect(
    values: Sequence[float],
    *,
    method: Literal["mad", "iqr"] = "mad",
    threshold: float | None = None,
) -> Result:
    """Detect outliers using the MAD or IQR method.

    For MAD, the threshold defaults to 3.5. For IQR, it defaults to 1.5 and
    acts as the Tukey fence multiplier. Outliers are strictly outside the
    computed bounds.
    """
    if method not in ("mad", "iqr"):
        raise OutlierError("invalid_options", f"method must be 'mad' or 'iqr', got {method!r}")
    if threshold is not None:
        if (
            isinstance(threshold, bool)
            or not isinstance(threshold, (int, float))
            or not math.isfinite(threshold)
            or threshold <= 0
        ):
            raise OutlierError("invalid_options", "threshold must be a positive finite number")
    else:
        threshold = 3.5 if method == "mad" else 1.5
    validated = _validate_values(values)
    if method == "mad":
        return _detect_mad(validated, threshold)
    return _detect_iqr(validated, threshold)


def hampel(
    series: Sequence[float],
    *,
    half_window: int = 3,
    n_sigmas: float = 3.0,
) -> list[int]:
    """Return indices of outliers detected by the Hampel filter.

    For each data point, a window of size ``2 * half_window + 1`` centered at
    the point (truncated at edges) is used. An outlier is flagged when
    ``abs(x - median(window)) > n_sigmas * 1.4826 * MAD(window)``.
    """
    if isinstance(half_window, bool) or not isinstance(half_window, int) or half_window < 1:
        raise OutlierError("invalid_options", "half_window must be an integer >= 1")
    if (
        isinstance(n_sigmas, bool)
        or not isinstance(n_sigmas, (int, float))
        or not math.isfinite(n_sigmas)
        or n_sigmas <= 0
    ):
        raise OutlierError("invalid_options", "n_sigmas must be a positive finite number")
    validated = _validate_values(series)
    indices: list[int] = []
    n = len(validated)
    for i, x in enumerate(validated):
        lo = max(0, i - half_window)
        hi = min(n, i + half_window + 1)
        window = validated[lo:hi]
        med = median(window)
        deviations = [abs(w - med) for w in window]
        mad = median(deviations)
        scale = 1.4826 * mad
        if abs(x - med) > n_sigmas * scale:
            indices.append(i)
    return indices
