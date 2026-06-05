# HARNESS-001: Rupture Pipeline

## Status
RASCUNHO

## Objective
Prove pipeline produces correct rupture numbers.

## Levels
| Level | Metric | Tolerance | Frequency |
|------:|--------|----------:|-----------|
| 1 | sum() | ±0.5% | every run |
| 2 | sum() by group | ±1.0% | weekly |
| 3 | sample | visual | monthly |

## Treatment
| Status | Action |
|--------|--------|
| OK | Proceed |
| ALERT | Investigate |
| CRITICAL | Block |
