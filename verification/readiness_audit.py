from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
required = [
    'agent.yaml','SOUL.md','RULES.md','DUTIES.md','AGENTS.md','EXPLAINABILITY.md','README.md',
    'requirements.txt','.gitignore','pytest.ini','core/__init__.py','core/analyzer.py','core/cli.py',
    'tests/test_analyzer.py','examples/river_flow_case.json','tools/validate-flow-observations.yaml',
    'tools/detect-flow-anomalies.yaml','tools/build-quality-report.yaml',
    'skills/river-flow-validation/SKILL.md','skills/hydrological-anomaly-review/SKILL.md',
    'skills/data-quality-reporting/SKILL.md'
]
missing = [name for name in required if not (ROOT / name).is_file()]
manifest = (ROOT / 'agent.yaml').read_text() if (ROOT / 'agent.yaml').exists() else ''
name_match = re.search(r'^name:\s*([a-z][a-z0-9-]*)\s*$', manifest, re.M)
checks = [
    ("required files", not missing, f"{len(required)-len(missing)}/{len(required)} present"),
    ("manifest name format", bool(name_match and name_match.group(1) == 'river-flow-data-quality-agent'), "lowercase hyphenated agent name"),
    ("explainability sections", all(h in (ROOT/'EXPLAINABILITY.md').read_text() for h in ['## Inputs','## Decision','## Limits','## Tool: validate-flow-observations','## Tool: detect-flow-anomalies','## Tool: build-quality-report']), "required headings present"),
]
for label, ok, detail in checks:
    print(f"{'PASS' if ok else 'FAIL'}: {label} — {detail}")
if missing:
    print('Missing:', ', '.join(missing))
raise SystemExit(0 if all(c[1] for c in checks) else 1)
