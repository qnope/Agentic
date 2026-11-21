# Scenario 4: Negative check, no workflow when the project has nothing to build or test

## Prompt
Add a GitHub CI to this project.

## Setup
Create `README.md` with this exact content:

````
# Field notes

Notes and measurements from the 2025 field campaign.
````

Create `notes/site-a.md` with this exact content:

````
# Site A

Visited on 2025-03-14. Soil is dry.
````

Create `data/measurements.csv` with this exact content:

````
site,date,ph
a,2025-03-14,6.8
````

## Pass criteria
- [ ] `.github` does not exist.
- [ ] The scratch directory contains only `README.md`, `notes/site-a.md` and `data/measurements.csv`, with the exact Setup content.
- [ ] The final output asks which commands the CI must run: it contains a question mark and the word `command`.

## RED baseline (without the skill)
2026-11-21 — FAIL (3 of 3 runs failed) — all 3 created `.github/workflows/ci.yml` with checks they invented (a CSV column check, `markdownlint-cli2`). No run asked which commands the CI must run.
