# Remaining project phases

Updated 2026-10-31. Topic registration/finalization and project data sharing are
confirmed resolved by the technical lead. Separate teammate approval is not a
gate for the lead's own work. Existing automated checks remain required, and
verification records must distinguish executed tests from human sign-off.

## Foundation completed

The preliminary daily panel, read-only audit, validation reports, coverage
table, preparation command, 20 passing tests and brief topic outline exist.
The panel has 140,256 rows over 16 cities and 8,766 days; the sole missing
Guwahati date is explicit. The November 6 preliminary materials are prepared;
assessment-specific final packaging and submission still need to happen.

## Phase 1: finalize the measurement method

- Confirm IMD temperature units, observation windows and the interpretation
  of the exported grid-cell coordinates from authoritative sources.
- Document appropriate temperature quality-control bounds; preserve and flag
  unexpected values rather than silently deleting them.
- Choose and record what qualifies as an extreme day and night: threshold
  type, reference period, city/season adjustment, leap-day treatment, isolated
  days versus consecutive spells, and missing-data rules.
- Define comparable frequency measures and how change between day and night
  will be expressed. Keep these settings explicit in configuration.

Output: a cited method and recorded analytical choices. Existing preparation
continues to run without prematurely fixing these choices.

## Phase 2: generate the final research variables

- Implement the agreed thresholds and daily extreme-day/extreme-night flags.
- Produce city-year counts and shares with observed-day denominators, so a
  missing observation is never counted as a non-extreme day.
- Integrate the calculations into the preparation command and document the
  extended schemas. Preserve the original temperature columns and missingness.
- Test threshold boundaries, reference-period behavior, missing dates and
  agreement between daily flags and annual totals.

Output: final daily dataset, annual summary table and validation reports.

## Phase 3: produce descriptive summaries and figures

- Summarize coverage and the distributions of daytime/nighttime temperatures.
- Compare annual extreme-day/night frequencies across cities and time.
- Generate a small set of reproducible figures with sources, units, dates and
  clearly stated definitions. Check sensitivity to reasonable alternative
  threshold/reference choices.
- Write a short description of actual results and limitations. Interpret the
  1-degree cells as regional exposure proxies; causal effects require a
  separate research design and additional data.

Output: summary tables, figures and a concise factual interpretation.

## Phase 4: complete the economics and documentation

- Write the environmental economics motivation and 2-3 candidate research
  questions within the registered topic.
- For each question, explain policy relevance, an applicable course technique
  and any additional data needed. Keep descriptive temperature comparisons
  distinct from claims about health, electricity demand or policy effects.
- Finish the README, data dictionary, source citations, limitations and the
  complete ordered preparation instructions. Make implemented/pending status
  consistent throughout the repository.

Output: the written components required by the final assignment.

## Phase 5: assemble and verify the replication package

- Prepare a self-contained submission folder with the permitted data, code,
  configuration, dependencies, README and candidate questions.
- Regenerate all required outputs from an untouched copy using only the
  documented commands; compare fingerprints and record the outcome.
- Remove development clutter from the submission copy and check all required
  files are actually included. Package the final deliverable ahead of the
  November 30 deadline.
- Submission itself and changes to the separate private submission repository
  remain distinct actions; do not claim either happened without executing it.

Output: a reproducible final package ready to submit.
