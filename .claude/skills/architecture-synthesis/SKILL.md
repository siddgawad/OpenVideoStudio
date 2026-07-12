---
name: Architecture Synthesis
description: Convert approved research evidence into architecture decisions, ADRs, state machines, provider boundaries, deployment modes, and milestone scope.
disable-model-invocation: true
context: fork
agent: architecture-reviewer
effort: max
---

Read the complete approved Phase Zero package.

Synthesize architecture for:

$ARGUMENTS

Requirements:

1. Cite research evidence for every major decision.
2. Compare at least three viable options for critical components.
3. Create or update ADRs.
4. Define state machines, queues, retries, idempotency and cancellation.
5. Define provider interfaces and replacement strategies.
6. Separate browser, control-plane and heavy-compute responsibilities.
7. Define local, free-demo and scalable deployment modes.
8. Identify what must not enter the MVP.
9. Update risk, cost and handoff documents.

Do not implement application code.
