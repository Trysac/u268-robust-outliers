# Robust outlier detection with explicit bounds

Status: accepted (generated, pending human review)

## Context

Outlier detection based on mean and standard deviation is sensitive to outliers. The library needed to implement robust alternatives with clearly stated constants and quartile methods, without external dependencies.

## Decision

Implement MAD-based modified z-scores (Iglewicz-Hoaglin) with MeanAD fallback, Tukey IQR fences using inclusive quartiles, and a Hampel filter with MAD consistency factor 1.4826. Expose a typed Result dataclass, an OutlierError with machine-readable codes, and a CLI reading from stdin.

## Consequences

Users get robust detection with explicit bounds and indices. The API is dependency-free and fully type-annotated. Tests cover all acceptance criteria and edge cases, ensuring >80% branch coverage.
