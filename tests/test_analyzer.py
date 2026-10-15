import unittest
from core.analyzer import analyze

class AnalyzerTests(unittest.TestCase):
    def test_clean_observations_have_no_flags(self):
        r = analyze({"observations": [{"station_id":"A", "timestamp":"2026-01-01T00:00:00Z", "flow":2}]})
        self.assertEqual(r["finding_count"], 0)

    def test_missing_field_flagged(self):
        r = analyze({"observations": [{"station_id":"A", "timestamp":"2026-01-01T00:00:00Z"}]})
        self.assertIn("MISSING_FIELD", r["finding_code_counts"])

    def test_invalid_timestamp_flagged(self):
        r = analyze({"observations": [{"station_id":"A", "timestamp":"bad", "flow":2}]})
        self.assertIn("INVALID_TIMESTAMP", r["finding_code_counts"])

    def test_duplicate_station_timestamp_flagged(self):
        row = {"station_id":"A", "timestamp":"2026-01-01T00:00:00Z", "flow":2}
        r = analyze({"observations": [row, row]})
        self.assertIn("DUPLICATE_STATION_TIMESTAMP", r["finding_code_counts"])

    def test_nonnumeric_flow_flagged(self):
        r = analyze({"observations": [{"station_id":"A", "timestamp":"2026-01-01T00:00:00Z", "flow":"lots"}]})
        self.assertIn("NON_NUMERIC_FLOW", r["finding_code_counts"])

    def test_negative_flow_flagged(self):
        r = analyze({"observations": [{"station_id":"A", "timestamp":"2026-01-01T00:00:00Z", "flow":-1}]})
        self.assertIn("NEGATIVE_FLOW", r["finding_code_counts"])

    def test_configured_range_flagged(self):
        r = analyze({"min_flow":0, "max_flow":5, "observations": [{"station_id":"A", "timestamp":"2026-01-01T00:00:00Z", "flow":7}]})
        self.assertIn("ABOVE_CONFIGURED_MAX", r["finding_code_counts"])

    def test_step_change_flagged(self):
        r = analyze({"max_step_change":3, "observations": [
            {"station_id":"A", "timestamp":"2026-01-01T00:00:00Z", "flow":2},
            {"station_id":"A", "timestamp":"2026-01-01T01:00:00Z", "flow":10}]})
        self.assertIn("ABRUPT_FLOW_CHANGE", r["finding_code_counts"])

    def test_bad_top_level_input_rejected(self):
        with self.assertRaises(ValueError):
            analyze({"rows": []})

if __name__ == "__main__":
    unittest.main()
