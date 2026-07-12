---
name: Adversarial Review
description: Independently try to invalidate research, architecture, task contracts, implementations, costs, licenses, security, UX, and completion claims.
disable-model-invocation: true
context: fork
agent: architecture-reviewer
effort: max
---

Adversarially review:

$ARGUMENTS

Assume the original author was capable but overconfident.

Find:

- blockers;
- major defects;
- minor defects;
- unsupported claims;
- missing evidence;
- stale data;
- license errors;
- hidden paid dependencies;
- security and privacy failures;
- unbuildable scope;
- fake completion;
- missing tests;
- rollback and portability gaps.

For every blocker and major issue provide evidence, affected documents/files, and a concrete correction. Do not praise the work.
