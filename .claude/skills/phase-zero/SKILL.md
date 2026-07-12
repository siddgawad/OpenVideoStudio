---
name: Phase Zero Research Program
description: Run the complete pre-implementation market, repository, model, license, cost, UX, safety, architecture, and handoff program for the conversational video studio.
disable-model-invocation: true
context: fork
agent: research-coordinator
effort: max
allowed-tools: Agent Read Write Edit Grep Glob Bash
---

Read the project charter and Phase Zero mission.

Execute the complete research program using isolated specialist agents.

Required behavior:

1. Inventory existing documents and datasets.
2. Create a workstream tracker with owners, outputs, evidence requirements, and status.
3. Delegate independent research in parallel.
4. Require primary-source citations, dates, confidence, and uncertainty.
5. Validate all machine-readable datasets.
6. Synthesize product requirements and architecture constraints only after research.
7. Define MVP, beta, deferred scope, and rejected assumptions.
8. Create the Claude–Codex operating model and first implementation backlog.
9. Run an independent adversarial review.
10. Correct every blocker and major finding.
11. Update `docs/HANDOFF.md`.

Do not implement production application code.

Additional user direction: $ARGUMENTS
