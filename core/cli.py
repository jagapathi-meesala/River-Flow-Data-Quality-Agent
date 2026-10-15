"""Command-line interface for river flow data quality screening."""
import argparse
import json
from pathlib import Path
from .analyzer import analyze


def main() -> int:
    parser = argparse.ArgumentParser(description="Screen river-flow observations for data-quality issues.")
    parser.add_argument("input", help="Path to input JSON")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = analyze(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
