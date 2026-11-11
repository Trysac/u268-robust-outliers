# Security notes

## Threat model

`robust_outliers` is a pure computation library. The only I/O path is `python -m robust_outliers`, which reads text from stdin. The library does not use `eval`, `exec`, network access or deserialization, and it has no runtime dependencies. Logging uses `logging.getLogger(__name__)` with a `NullHandler`.

### Defended

- Invalid values are rejected before computation: non-finite values raise `OutlierError` with code `non_finite` and the index; `bool` and non-numeric values raise code `invalid_value` with the index.
- Empty input raises `empty_input`. More than `MAX_VALUES = 10_000_000` values raises `input_too_large`.
- Invalid options raise `invalid_options`: an unknown `method`; a `threshold` that is not a positive finite number; a `half_window` that is not an integer >= 1; an `n_sigmas` that is not a positive finite number.
- The CLI caps stdin at `MAX_INPUT_BYTES = 104_857_600` bytes and returns 2 on oversized input. A non-numeric line returns 2. Invalid numeric input that reaches the library is reported through `OutlierError` and returns 2.
- The CLI does not invoke a shell and prints outliers as `<index>\t<value>` with the value as read.

### Not defended

- Statistical false positives and false negatives are not security issues; values at or inside the computed bounds are not outliers by design.
- There is no protection against resource exhaustion below the `10_000_000` value limit or the `104_857_600` byte stdin limit. There are no timeouts.
- Hampel windows are truncated at the edges and are not a streaming detector.
- The CLI trusts its local stdin and provides no authentication or authorization.

## Publishing

The package has no runtime dependencies. Release credentials and publishing configuration are not part of the code described here.
