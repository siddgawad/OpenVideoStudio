from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "research"

errors: list[str] = []
for path in sorted(DATA.glob("*.json")):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name}: invalid JSON: {exc}")
        continue
    if not isinstance(data, list):
        errors.append(f"{path.name}: top-level value must be an array")
        continue

    ids = set()
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"{path.name}[{index}]: item must be an object")
            continue
        item_id = item.get("id")
        if item_id:
            if item_id in ids:
                errors.append(f"{path.name}[{index}]: duplicate id {item_id}")
            ids.add(item_id)

if errors:
    print("Research data validation FAILED:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print("Research data validation passed.")
