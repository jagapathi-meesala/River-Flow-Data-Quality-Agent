# Explainability

## Inputs
Each observation's timestamp, station identifier, flow value, unit, and record identifier are used when supplied. Optional numeric thresholds are supplied by the user.

## Decision
The agent applies deterministic validation checks: missing fields, invalid timestamps, duplicate station/timestamp pairs, nonnumeric flow, negative flow, configured bounds, and large adjacent changes within a station's time-sorted observations.

## Limits
Thresholds are not universal. Seasonal changes, rating-curve shifts, backwater effects, sensor maintenance, and real hydrological events can produce unusual readings. The tool does not access live gauges, estimate flood risk, or validate sensor calibration.

## Tool: validate-flow-observations
### Inputs and Data Sources
A JSON object with observations and optional configured bounds.
### Decision and Reasoning
Checks record completeness, parseable timestamps, numeric flow values, duplicate station/timestamp keys, and configured flow limits.
### Outputs and Evidence
Returns findings with code, severity, record index/ID, observed value, and explanation.
### Limits and Constraints
No external reference data or universal thresholds are used.
### Failure Handling
Malformed top-level input or missing observations array produces a clear error.
### Human Review
Confirm flags against gauge metadata, units, station logs, and source records.

## Tool: detect-flow-anomalies
### Inputs and Data Sources
Validated observations plus optional `max_step_change`.
### Decision and Reasoning
Flags large absolute differences between consecutive parseable numeric observations for the same station after timestamp sorting.
### Outputs and Evidence
Includes both values, absolute difference, and record identifiers where available.
### Limits and Constraints
A step-change flag is not proof of an error; floods and operational releases can cause genuine changes.
### Failure Handling
Records with invalid timestamps or flow values are excluded from this comparison and remain flagged by validation.
### Human Review
Compare with rainfall, reservoir operations, neighboring gauges, and instrument logs where available.

## Tool: build-quality-report
### Inputs and Data Sources
Validation findings and source record counts.
### Decision and Reasoning
Summarizes severity and finding-code counts without modifying data.
### Outputs and Evidence
Returns totals, findings, and a review recommendation.
### Limits and Constraints
Summary quality depends on the completeness and correctness of supplied observations.
### Failure Handling
Empty datasets return a report that identifies the absence of records.
### Human Review
Resolve or document flags before using the data in modeling or operational reporting.
