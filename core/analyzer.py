"""Deterministic validation and anomaly screening for river-flow observations."""
from __future__ import annotations
from datetime import datetime
from collections import Counter
from typing import Any


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        # Normalize naive timestamps as naive; aware timestamps remain aware.
        return parsed
    except ValueError:
        return None


def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("observations"), list):
        raise ValueError("Input must be a JSON object containing an 'observations' array.")
    observations = payload["observations"]
    findings: list[dict[str, Any]] = []
    seen: dict[tuple[str, str], int] = {}
    usable: dict[str, list[tuple[datetime, float, int, Any]]] = {}

    def add(code: str, severity: str, idx: int, record: dict[str, Any], message: str, **extra: Any) -> None:
        finding = {"code": code, "severity": severity, "record_index": idx,
                   "record_id": record.get("record_id"), "station_id": record.get("station_id"),
                   "message": message}
        finding.update(extra)
        findings.append(finding)

    for idx, raw in enumerate(observations):
        if not isinstance(raw, dict):
            findings.append({"code": "INVALID_RECORD", "severity": "high", "record_index": idx,
                             "record_id": None, "station_id": None, "message": "Observation must be a JSON object."})
            continue
        record = raw
        for field in ("station_id", "timestamp", "flow"):
            if field not in record or record[field] is None or record[field] == "":
                add("MISSING_FIELD", "medium", idx, record, f"Required field '{field}' is missing.", field=field)
        station = str(record.get("station_id", ""))
        ts_text = record.get("timestamp")
        ts = _parse_timestamp(ts_text)
        if ts_text not in (None, "") and ts is None:
            add("INVALID_TIMESTAMP", "high", idx, record, "Timestamp could not be parsed as ISO 8601.", observed=ts_text)
        if ts is not None:
            key = (station, str(ts))
            if key in seen:
                add("DUPLICATE_STATION_TIMESTAMP", "medium", idx, record,
                    "Another observation has the same station and timestamp.", duplicate_of_index=seen[key])
            else:
                seen[key] = idx
        value = record.get("flow")
        try:
            if isinstance(value, bool) or value is None or str(value).strip() == "":
                raise ValueError
            flow = float(value)
        except (ValueError, TypeError):
            if value is not None and str(value).strip() != "":
                add("NON_NUMERIC_FLOW", "high", idx, record, "Flow value is not numeric.", observed=value)
            continue
        if flow != flow or flow in (float("inf"), float("-inf")):
            add("NON_FINITE_FLOW", "high", idx, record, "Flow value must be finite.", observed=value)
            continue
        if flow < 0:
            add("NEGATIVE_FLOW", "high", idx, record, "Negative flow is flagged for domain-specific review.", observed=flow)
        min_flow = payload.get("min_flow")
        max_flow = payload.get("max_flow")
        try:
            if min_flow is not None and flow < float(min_flow):
                add("BELOW_CONFIGURED_MIN", "medium", idx, record, "Flow is below the configured minimum.", observed=flow, threshold=float(min_flow))
            if max_flow is not None and flow > float(max_flow):
                add("ABOVE_CONFIGURED_MAX", "medium", idx, record, "Flow is above the configured maximum.", observed=flow, threshold=float(max_flow))
        except (ValueError, TypeError):
            raise ValueError("min_flow and max_flow must be numeric when supplied.")
        if ts is not None and station:
            usable.setdefault(station, []).append((ts, flow, idx, record.get("record_id")))

    max_step = payload.get("max_step_change")
    if max_step is not None:
        try:
            max_step = float(max_step)
            if max_step < 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError("max_step_change must be a non-negative number when supplied.")
        for station, rows in usable.items():
            rows.sort(key=lambda row: row[0])
            for previous, current in zip(rows, rows[1:]):
                delta = abs(current[1] - previous[1])
                if delta > max_step:
                    idx = current[2]
                    record = observations[idx] if isinstance(observations[idx], dict) else {}
                    add("ABRUPT_FLOW_CHANGE", "medium", idx, record,
                        "Absolute change from the previous timestamp exceeds the configured threshold.",
                        previous_flow=previous[1], observed_flow=current[1], absolute_change=delta,
                        threshold=max_step, previous_record_id=previous[3])

    counts = Counter(f["severity"] for f in findings)
    code_counts = Counter(f["code"] for f in findings)
    return {
        "agent": "river-flow-data-quality-agent",
        "observation_count": len(observations),
        "finding_count": len(findings),
        "severity_counts": dict(counts),
        "finding_code_counts": dict(code_counts),
        "findings": findings,
        "status": "review_required" if findings else "no_flags_from_configured_checks",
        "limitations": [
            "Configured thresholds are screening criteria, not universal hydrological standards.",
            "An abrupt change may reflect a real hydrological event rather than a data error.",
            "No source-gauge, calibration, rainfall, or official warning data is consulted.",
            "Input observations are not modified or imputed."
        ]
    }
