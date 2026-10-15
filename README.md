# River Flow Data Quality Agent

A dependency-free Python agent for screening river-flow observations for missing fields, invalid timestamps, duplicate station/time records, nonnumeric or negative flow, configured range violations, and abrupt changes between adjacent observations.

## Input
JSON object with `observations`: an array of records. Example:

```json
{
  "observations": [
    {"record_id":"R1","station_id":"G-01","timestamp":"2026-10-15T08:00:00Z","flow":12.4,"unit":"m3/s"},
    {"record_id":"R2","station_id":"G-01","timestamp":"2026-10-15T09:00:00Z","flow":13.1,"unit":"m3/s"}
  ],
  "min_flow": 0,
  "max_flow": 500,
  "max_step_change": 100
}
```

## Run

```bash
python3 -m core.cli examples/river_flow_case.json --output report.json
```

## Tests and audit

```bash
python3 -m unittest discover -s tests -v
python3 verification/readiness_audit.py
```

Thresholds are configurable screening criteria, not universal hydrological standards. A flagged change may be a real river event. This tool does not provide flood warnings or replace official gauge validation.
