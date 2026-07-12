# Claude Video Studio Bootstrap

A repository bootstrap for using Claude Code as the research, architecture, review, and planning system for an open-source conversational YouTube production studio.

This package intentionally does **not** install every MCP server globally. Powerful servers are scoped to the smallest agent or phase that needs them. That keeps context usage, prompt-injection exposure, and accidental write access under control.

## Start tonight

1. Create a new GitHub repository.
2. Copy this package into the repository root.
3. Commit it.
4. In Claude Code, trust the repository and approve the project MCP servers.
5. Connect GitHub and Hugging Face through Claude/claude.ai connectors.
6. Run `/mcp-health-check`.
7. Start Fable Max in plan mode and run `/phase-zero`.

Recommended session:

```bash
claude --model fable --effort max --permission-mode plan
```

Then invoke:

```text
/phase-zero
```

The phase-zero skill coordinates competitive research, repository due diligence, model feasibility, licensing, free-use economics, security, UX, and architecture constraints. It writes durable output to `docs/` and `data/research/`.

## Authoritative files

1. `PROJECT_CHARTER.md`
2. `docs/PHASE_ZERO_PROMPT.md`
3. `docs/MCP_SERVER_PLAN.md`
4. `docs/SECURITY_BOUNDARIES.md`
5. `CLAUDE.md`
6. `.claude/skills/*/SKILL.md`
7. `.claude/agents/*.md`

## Important operating rule

MCP is for connecting external systems. It is not a replacement for:

- repository documentation;
- deterministic scripts;
- tests;
- CI;
- task contracts;
- human approval for destructive operations.

The repository is the durable memory. Chat history is not.
