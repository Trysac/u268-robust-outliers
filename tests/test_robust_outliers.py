from __future__ import annotations

import io
import math
import sys
from collections.abc import Sequence

import pytest

from robust_outliers import (
    MAX_VALUES,
    OutlierError,
    detect,
    hampel,
    modified_z_scores,
)


class TooLong(Sequence):
    def __len__(self) -> int:
        return MAX_VALUES + 1

    def __getitem__(self, index: int) -> float:
        raise NotImplementedError


def test_detect_mad_acceptance() -> None:
    result = detect([10, 12, 11, 13, 12, 11, 95])
    assert result.indices == (6,)
    assert result.center == 12
    assert result.scale == 1
    assert result.method == "mad"
    assert round(result.lower, 4) == 6.811
    assert round(result.upper, 4) == 17.189


def test_modified_z_scores_acceptance() -> None:
    values = [10, 12, 11, 13, 12, 11, 95]
    expected = [-1.349, 0.0, -0.6745, 0.6745, 0.0, -0.6745, 55.9835]
    result = modified_z_scores(values)
    assert [round(z, 4) for z in result] == expected


def test_detect_iqr_acceptance() -> None:
    result = detect([10, 12, 11, 13, 12, 11, 95], method="iqr")
    assert result.indices == (6,)
    assert result.lower == 8.75
    assert result.upper == 14.75
    assert result.center == 12
    assert result.scale == 1.5
    assert result.method == "iqr"


def test_mad_fallback_to_mean_ad() -> None:
    result = detect([5, 5, 5, 5, 9])
    assert result.indices == (4,)
    assert result.center == 5
    assert result.scale == pytest.approx(0.8)
    # (9-5)/(1.253314*0.8) ≈ 3.989 > 3.5
    assert result.lower == pytest.approx(5 - 3.5 * 1.253314 * 0.8)
    assert result.upper == pytest.approx(5 + 3.5 * 1.253314 * 0.8)


def test_mad_no_spread_all_same() -> None:
    result = detect([5, 5, 5])
    assert result.indices == ()
    assert result.center == 5
    assert result.scale == 0
    assert result.lower == 5
    assert result.upper == 5


def test_hampel_acceptance() -> None:
    series = [10, 11, 10, 12, 50, 11, 10, 12]
    assert hampel(series, half_window=2, n_sigmas=3.0) == [4]


def test_hampel_zero_mad_window_flags_spike() -> None:
    # A window with MAD == 0 has a zero threshold, so any deviation is flagged.
    assert hampel([5, 5, 5, 5, 9], half_window=2) == [4]


def test_hampel_zero_mad_constant_series() -> None:
    # x == median means deviation 0, which is not strictly greater than 0.
    assert hampel([5, 5, 5, 5, 5], half_window=2) == []


def test_empty_input_raises() -> None:
    with pytest.raises(OutlierError) as exc_info:
        detect([])
    assert exc_info.value.code == "empty_input"


def test_non_finite_raises_with_index() -> None:
    with pytest.raises(OutlierError) as exc_info:
        detect([1.0, 2.0, math.nan])
    assert exc_info.value.code == "non_finite"
    assert "index 2" in str(exc_info.value)

    with pytest.raises(OutlierError) as exc_info:
        modified_z_scores([1.0, math.inf])
    assert exc_info.value.code == "non_finite"
    assert "index 1" in str(exc_info.value)


def test_bool_invalid_value() -> None:
    with pytest.raises(OutlierError) as exc_info:
        detect([1, True, 3])
    assert exc_info.value.code == "invalid_value"
    assert "index 1" in str(exc_info.value)


def test_threshold_zero_invalid_options() -> None:
    with pytest.raises(OutlierError) as exc_info:
        detect([1, 2, 3], threshold=0)
    assert exc_info.value.code == "invalid_options"


def test_invalid_method() -> None:
    with pytest.raises(OutlierError) as exc_info:
        detect([1, 2], method="bad")  # type: ignore[arg-type]
    assert exc_info.value.code == "invalid_options"


def test_input_too_large() -> None:
    with pytest.raises(OutlierError) as exc_info:
        detect(TooLong())
    assert exc_info.value.code == "input_too_large"


def test_modified_z_scores_zeros_when_no_spread() -> None:
    assert modified_z_scores([5, 5, 5]) == [0.0, 0.0, 0.0]


def test_detect_iqr_single_value() -> None:
    result = detect([42], method="iqr")
    assert result.indices == ()
    assert result.center == 42
    assert result.scale == 0
    assert result.lower == 42
    assert result.upper == 42


def test_detect_iqr_even_count() -> None:
    result = detect([1, 2, 3, 4], method="iqr")
    # statistics.quantiles(method="inclusive") -> Q1=1.75, Q2=2.5, Q3=3.25
    assert result.center == pytest.approx(2.5)
    assert result.scale == pytest.approx(1.5)
    assert result.lower == pytest.approx(1.75 - 1.5 * 1.5)
    assert result.upper == pytest.approx(3.25 + 1.5 * 1.5)
    assert result.indices == ()  # no outliers


def test_detect_two_values() -> None:
    result = detect([1, 3])
    assert result.center == 2
    assert result.scale == 1
    assert result.indices == ()


def test_detect_negative_values() -> None:
    result = detect([-10, -12, -11, -13, -12, -11, -95])
    assert result.indices == (6,)
    assert result.center == -12
    assert result.scale == 1


def test_ties_at_fence_are_not_outliers() -> None:
    # threshold * MAD / 0.6745 == 1.0, so the bounds fall exactly on 1 and 3.
    result = detect([1, 2, 3], threshold=0.6745)
    assert result.lower == pytest.approx(1.0)
    assert result.upper == pytest.approx(3.0)
    assert result.indices == ()


def test_hampel_invalid_half_window() -> None:
    with pytest.raises(OutlierError) as exc_info:
        hampel([1, 2, 3], half_window=0)
    assert exc_info.value.code == "invalid_options"


def test_hampel_invalid_n_sigmas() -> None:
    with pytest.raises(OutlierError) as exc_info:
        hampel([1, 2, 3], n_sigmas=0)
    assert exc_info.value.code == "invalid_options"


def test_cli_outliers_found(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stdin_data = "10\n12\n11\n13\n12\n11\n95\n"
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin_data))
    rc = __import__("robust_outliers.__main__", fromlist=["main"]).main(["--method", "iqr"])
    captured = capsys.readouterr()
    assert rc == 1
    assert captured.out == "6\t95\n"
    assert captured.err == ""


def test_cli_no_outliers(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stdin_data = "1\n2\n3\n"
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin_data))
    rc = __import__("robust_outliers.__main__", fromlist=["main"]).main([])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out == ""
    assert captured.err == ""


def test_cli_invalid_numeric(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stdin_data = "1\nfoo\n3\n"
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin_data))
    rc = __import__("robust_outliers.__main__", fromlist=["main"]).main([])
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.out == ""
    assert "invalid numeric value" in captured.err


def test_cli_usage_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("1\n"))
    rc = __import__("robust_outliers.__main__", fromlist=["main"]).main(["--method", "bad"])
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.out == ""
