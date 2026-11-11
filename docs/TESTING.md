# Testing

## Running

From a checkout with the package importable:

```sh
python -m pytest tests/test_robust_outliers.py
```

## Policy

The test suite is the single file `tests/test_robust_outliers.py`; there is no `tests/conftest.py` and no conformance marker in the tests. Tests use pytest assertions and `pytest.raises`/`pytest.approx` and do not require a network or an external tool.

## Tiers

Only one tier is present: `tests/test_robust_outliers.py` runs locally and uses no downloaded tool.

## Layout

`tests/test_robust_outliers.py` is the only test file. `tests/__pycache__` is generated Python bytecode.

## Covered tests

- `test_detect_mad_acceptance`, `test_modified_z_scores_acceptance`, `test_detect_iqr_acceptance`: acceptance values for MAD detection, modified z-scores and Tukey IQR fences, including returned bounds.
- `test_mad_fallback_to_mean_ad`, `test_mad_no_spread_all_same`, `test_modified_z_scores_zeros_when_no_spread`: MAD zero fallback to mean absolute deviation and the all-zero-score case.
- `test_hampel_acceptance`, `test_hampel_zero_mad_window_flags_spike`, `test_hampel_zero_mad_constant_series`: Hampel filter output, zero-MAD windows and constant series.
- `test_empty_input_raises`, `test_non_finite_raises_with_index`, `test_bool_invalid_value`, `test_threshold_zero_invalid_options`, `test_invalid_method`, `test_input_too_large`, `test_detect_iqr_single_value`: error codes, invalid values and options, input size limit and the single-value IQR edge case.
