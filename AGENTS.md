# Agent Operating Notes

Use the CLI with a JSON file containing an `observations` array. Each observation may include `timestamp`, `station_id`, `flow`, `unit`, and `record_id`. Optional configuration supports `min_flow`, `max_flow`, and `max_step_change`. Output is a screening report, not an operational alert.
