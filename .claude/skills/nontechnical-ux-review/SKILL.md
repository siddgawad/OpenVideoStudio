---
name: Nontechnical User Experience Review
description: Evaluate whether a non-technical user can complete the end-to-end video workflow on desktop, tablet, and mobile without understanding the underlying stack.
context: fork
agent: architecture-reviewer
effort: high
---

Review:

$ARGUMENTS

Check:

- plain-language conversation and guided defaults;
- first-run completion without documentation;
- progressive disclosure;
- understandable progress and failure recovery;
- direct selection plus natural-language editing;
- interpretation confirmation for expensive edits;
- version comparison and rollback;
- keyboard, screen-reader, zoom, mobile and low-bandwidth use;
- whether any ordinary action exposes technical infrastructure.

Return blockers, majors, test scenarios, and concrete product corrections.
