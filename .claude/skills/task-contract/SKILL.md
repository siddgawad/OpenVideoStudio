---
name: Implementation Task Contract
description: Create a bounded, testable implementation task for Codex from approved specifications.
disable-model-invocation: true
argument-hint: "[task-id] [objective]"
effort: high
---

Create an implementation contract for:

$ARGUMENTS

Use `templates/TASK_CONTRACT_TEMPLATE.md`.

The contract must include:

- immutable task ID;
- source specification and version;
- base commit;
- user value;
- objective;
- scope and out-of-scope;
- dependencies;
- affected files and interfaces;
- data migration implications;
- security and accessibility requirements;
- acceptance criteria;
- deterministic verification commands;
- manual verification;
- expected evidence and artifacts;
- rollback;
- stop and escalation conditions.

Do not implement the task.
