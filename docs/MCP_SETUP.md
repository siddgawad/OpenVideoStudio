# MCP Setup

## Why the setup is staged

Loading every possible MCP server into every session is bad engineering. Tool search reduces context cost, but it does not remove authentication risk, prompt-injection exposure, accidental writes, or operational complexity.

This project uses four classes:

1. **Project-safe read-only servers** committed in `.mcp.json`.
2. **User-authenticated connectors** configured outside the repository.
3. **Subagent-scoped servers** connected only for a specific specialist.
4. **Deferred write-capable servers** enabled only after the related infrastructure exists.

## Step 1: Approve project MCP servers

Start Claude Code interactively from the repository and accept workspace trust.

```bash
claude
```

Then inspect:

```text
/mcp
```

Expected project servers:

- `context7`
- `cloudflare-docs`

## Step 2: Connect GitHub

Preferred for Claude Code cloud sessions:

- Add GitHub under Claude/claude.ai connectors.
- Authenticate there.
- Confirm it appears in `/mcp`.

CLI alternative:

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_FINE_GRAINED_GITHUB_TOKEN"
```

Use a fine-grained token limited to the project repository. Do not grant organization-wide administration.

## Step 3: Connect Hugging Face

Use the Hugging Face MCP settings page while logged in and copy the client-specific configuration, or connect the Hugging Face connector from Claude if offered.

Enable only tools needed for Phase Zero:

- Model Search
- Papers Semantic Search
- Documentation Semantic Search
- Spaces Semantic Search

Do not enable job execution during Phase Zero.

## Step 4: Install official vendor skills

### Context7

```bash
npx ctx7 setup --claude
```

Choose CLI + Skills or MCP. This repository already includes the MCP endpoint, so the skill-only option is sufficient.

### Playwright CLI skills

```bash
npm install -g @playwright/cli@latest
playwright-cli install --skills
```

Use the CLI skills for routine browser testing. Use Playwright MCP only for persistent exploratory browser loops through the dedicated subagent.

### Supabase

```bash
npx skills add supabase/agent-skills --skill supabase
npx skills add supabase/agent-skills --skill supabase-postgres-best-practices
```

Install now if desired, but do not connect Supabase MCP until a development project exists.

### Cloudflare

Inside Claude Code:

```text
/plugin marketplace add cloudflare/skills
```

Install only the Cloudflare skills needed by the selected deployment architecture.

### Hugging Face

Inside Claude Code:

```text
/plugin marketplace add huggingface/skills
/plugin install hf-cli@huggingface/skills
/plugin install huggingface-papers@huggingface/skills
/plugin install transformers-js@huggingface/skills
/plugin install gradio@huggingface/skills
```

Install model-training skills only if training enters the approved roadmap.

### Official MCP server development plugin

Inside Claude Code:

```text
/plugin marketplace add anthropics/claude-plugins-official
/plugin install mcp-server-dev@claude-plugins-official
/reload-plugins
```

Use later with:

```text
/mcp-server-dev:build-mcp-server
```

## Step 5: Validate

```bash
python scripts/check-bootstrap.py
```

Then invoke:

```text
/mcp-health-check
```

## Step 6: Start Phase Zero

```bash
claude --model fable --effort max --permission-mode plan
```

Then:

```text
/phase-zero
```
