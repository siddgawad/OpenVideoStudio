---
name: Codex Handoff
description: Produce a self-contained execution packet so Codex can implement an approved task without reconstructing intent from chat history.
disable-model-invocation: true
argument-hint: "[task-id]"
effort: high
---

Prepare the Codex handoff for task:

$ARGUMENTS

Include:

- task contract path;
- approved spec and ADR paths;
- base commit SHA;
- branch/worktree name;
- exact in-scope files;
- interfaces that must remain stable;
- tests to add or preserve;
- commands to run;
- prohibited scope expansion;
- completion-report schema;
- known risks and assumptions.

Write the packet under `docs/handoffs/`.

The final instruction to Codex must require evidence, not a success claim.
