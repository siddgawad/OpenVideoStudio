---
name: Repository Due Diligence
description: Deeply inspect named repositories before deciding to reuse, integrate, fork, study, defer, or reject them.
argument-hint: "[owner/repo ...]"
context: fork
agent: repository-auditor
effort: max
---

Audit these repositories:

$ARGUMENTS

Inspect actual repository files, license, releases, commits, tests, CI, documentation, security, dependencies, hardware requirements, open issues and integration surface.

Return one scored decision record per repository plus raw evidence suitable for the research dataset.
