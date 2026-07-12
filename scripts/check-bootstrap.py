from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "PROJECT_CHARTER.md",
    "CLAUDE.md",
    ".mcp.json",
    ".claude/settings.json",
    "docs/MCP_SETUP.md",
    "docs/MCP_SERVER_PLAN.md",
    "docs/SECURITY_BOUNDARIES.md",
    "docs/PHASE_ZERO_PROMPT.md",
    ".claude/skills/phase-zero/SKILL.md",
    ".claude/skills/mcp-health-check/SKILL.md",
    ".claude/agents/research-coordinator.md",
]

errors: list[str] = []

for rel in REQUIRED:
    if not (ROOT / rel).exists():
        errors.append(f"Missing required file: {rel}")

for rel in [".mcp.json", ".mcp.optional.example.json", ".claude/settings.json"]:
    path = ROOT / rel
    if path.exists():
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {rel}: {exc}")

for path in (ROOT / ".claude" / "skills").glob("*/SKILL.md"):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"Missing YAML frontmatter in {path.relative_to(ROOT)}")
    if len(text.splitlines()) > 500:
        errors.append(f"Skill exceeds 500 lines: {path.relative_to(ROOT)}")

for path in (ROOT / "data" / "research").glob("*.json"):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, list):
            errors.append(f"Research dataset must be a JSON array: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")

tracked_text = []
for path in ROOT.rglob("*"):
    if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt", ".example"}:
        tracked_text.append(path.read_text(encoding="utf-8", errors="ignore"))

for marker in ["ghp_", "github_pat_", "hf_", "sbp_"]:
    # Allow variable names/examples, but flag token-like strings longer than a trivial prefix.
    for text in tracked_text:
        if marker in text and any(len(part) > 30 for part in text.split() if marker in part):
            errors.append(f"Possible committed credential containing prefix {marker}")
            break

if errors:
    print("Bootstrap validation FAILED:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print("Bootstrap validation passed.")
print(f"Skills: {len(list((ROOT / '.claude' / 'skills').glob('*/SKILL.md')))}")
print(f"Agents: {len(list((ROOT / '.claude' / 'agents').glob('*.md')))}")
