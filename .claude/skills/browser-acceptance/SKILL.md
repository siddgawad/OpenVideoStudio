---
name: Browser Acceptance Test
description: Test a web build through an isolated browser for functional, responsive, mobile, keyboard, accessibility, and recovery behavior.
disable-model-invocation: true
context: fork
agent: browser-tester
argument-hint: "[url] [scenario]"
---

Test:

$ARGUMENTS

Cover the specified scenario at desktop and mobile viewport sizes.

Record:

- exact steps;
- expected and observed behavior;
- console/network failures;
- keyboard and focus behavior;
- overflow, zoom and reflow;
- screenshots and artifact paths;
- severity;
- reproducibility.

Do not modify production data or authenticate to personal accounts.
