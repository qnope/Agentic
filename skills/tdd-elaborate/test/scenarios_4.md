# Scenario 4: Negative check, a question is not a feature

## Prompt
What does `add(2, 3)` in `calc.py` return? Answer in one sentence. Do not change anything.

## Setup
Create `calc.py` with this exact content:

```
def add(a, b):
    return a + b
```

## Pass criteria
- [ ] The scratch directory contains no `specs` folder.
- [ ] `calc.py` has the exact Setup content and is the only file in the scratch directory.
- [ ] The final output contains `5`.

## RED baseline (without the skill)
2026-11-21 — PASS (0 of 3 runs failed) — expected: this is a negative check, it guards against over-triggering. All 3 runs answered "5" in one sentence and wrote no file.
