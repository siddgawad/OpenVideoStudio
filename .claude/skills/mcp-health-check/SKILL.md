---
name: MCP Health Check
description: Verify the project MCP configuration, connected servers, scopes, authentication, and safety before research or implementation.
disable-model-invocation: true
allowed-tools: Read Bash(claude mcp *) Bash(python scripts/check-bootstrap.py *)
---

Perform the MCP readiness check.

1. Run `python scripts/check-bootstrap.py`.
2. Run `claude mcp list`.
3. Inspect `claude mcp get context7`.
4. Inspect `claude mcp get cloudflare-docs`.
5. Report whether GitHub and Hugging Face connectors are present.
6. Report pending approval, authentication, connection, timeout, or zero-tool failures.
7. Confirm no tracked file contains an actual token.
8. Confirm write-capable servers are not globally enabled.
9. Recommend only the minimum correction needed.

Do not add credentials or approve servers automatically.
