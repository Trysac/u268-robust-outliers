# Project record

## Objective

Implement `robust_outliers`, a Python library for robust outlier detection with modified z-scores from the median absolute deviation, Tukey fences on inclusive quartiles and a Hampel filter for series, with explicit bounds.

## Scope

- In scope: the public API `Result`, `modified_z_scores`, `detect`, `hampel` and `OutlierError`; MAD and IQR detection with explicit thresholds and bounds; Hampel filtering with truncated edge windows; the `python -m robust_outliers` command-line interface; typed and tested code with no runtime dependencies.
- Out of scope: multivariate methods, seasonal decomposition, generalised ESD and streaming windows.

## Timeline

| Date | Event |
|---|---|
| 2026 | Repository created from the factory utility template. |

## Effort metrics

Measured values only; a value that has not been measured stays "pending measurement".

| Metric | Value |
|---|---|
| Tokens (input / output) | 372712 / 41383 |
| Hours (human) | pending measurement |
| Cost (USD) | 0.0674 |

## Factory run u268 (measured from API usage)

| Date (UTC) | Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|---|
| 2026-11-10 | generation | deepseek-v4-pro | yes | 1593 | 13428 | 0 | 3328 | 0.0277 |
| 2026-11-10 | fix-1 | deepseek-flash | no | 7477 | 5475 | 0 | 49920 | 0.0046 |
| 2026-11-10 | audit | deepseek-flash | no | 11612 | 12307 | 0 | 139008 | 0.0095 |
| 2026-11-10 | fix-2 | deepseek-flash | no | 6473 | 2141 | 0 | 30336 | 0.0023 |
| 2026-11-10 | docs | deepseek-flash | no | 122709 | 8032 | 0 | 256 | 0.0232 |

Total: $0.0674. Prices: deepseek line, as measured by its adapter. Providers serve the current version of each model id, so the date tells which version answered; versions, launch stages and price sources per line are in the factory's model register (docs/MODELS.md).
