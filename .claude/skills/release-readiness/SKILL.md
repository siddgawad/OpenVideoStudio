---
name: Release Readiness Review
description: Verify that a milestone or release has complete evidence, tests, documentation, security, accessibility, licensing, migration, rollback, and operational readiness.
disable-model-invocation: true
context: fork
agent: architecture-reviewer
effort: max
---

Review release candidate:

$ARGUMENTS

Require evidence for:

- build, lint, typecheck and tests;
- end-to-end user journeys;
- accessibility checks;
- security and dependency checks;
- license and attribution status;
- migrations and rollback;
- configuration and secrets;
- monitoring and health checks;
- documentation and setup reproduction;
- known limitations;
- unresolved blockers and majors.

Return a release decision: BLOCK, CONDITIONAL, or READY.

Do not deploy.
