# MCP Server Plan

## Tier 0: Required to begin research

| Server | Scope | Mode | Purpose |
|---|---|---|---|
| Context7 | Project | Read-only | Current library/API documentation |
| Cloudflare Docs | Project | Read-only | Current Cloudflare documentation |
| GitHub | User/connector | Least-privilege read, selected writes | Repository research, issues, PRs, handoffs |
| Hugging Face | User/connector | Read-only tools during Phase Zero | Models, datasets, papers, Spaces, model cards |
| Playwright | Browser-tester subagent only | Isolated local stdio | Persistent exploratory browser validation |

## Tier 1: Enable when implementation starts

| Server | Rule |
|---|---|
| Supabase | Development project only; project-scoped; `read_only=true` by default |
| Cloudflare API | Narrow OAuth scopes or narrow API token; never full-account permissions |
| Playwright MCP | Use only for persistent iterative browser work; prefer CLI + Skills for routine tests |
| Sentry | Enable after a deployment exists; read-only incident analysis first |

## Tier 2: Build as project-owned MCP servers

These should be custom, narrow, auditable servers rather than miscellaneous community packages.

### Research Registry MCP

Expose:

- `register_source`
- `register_product`
- `register_repository`
- `register_model`
- `record_verification`
- `validate_research_dataset`

Resources:

- `research://status`
- `research://schemas/{name}`
- `research://unverified`
- `research://conflicts`

### Project Control MCP

Expose:

- `list_approved_tasks`
- `claim_task`
- `record_handoff`
- `record_verification_result`
- `request_review`
- `mark_blocked`

Do not allow it to merge or deploy.

### Media Worker MCP

Expose asynchronous job submission and status only:

- image generation;
- video generation;
- inpainting;
- narration;
- alignment;
- rendering.

Every expensive or identity-sensitive operation must require user interaction.

### Asset Rights MCP

Expose:

- asset search;
- license record;
- attribution generation;
- rights conflict check.

### YouTube Draft MCP

Future only. Allow metadata validation and private/unlisted draft upload after explicit user approval. Never expose automatic public publishing.

## Rejected global servers

Do not install these globally merely because they are fashionable:

- generic filesystem MCP: Claude already has repository file tools;
- generic memory MCP: durable state belongs in version-controlled documents and databases;
- generic shell MCP: Claude already has Bash with permissions;
- unrestricted browser MCP: high prompt-injection exposure;
- production database MCP: unacceptable data and mutation risk;
- unrestricted cloud-account MCP: excessive blast radius;
- arbitrary community n8n MCP: review source, license, maintenance, and permissions first.

## Transport policy

- Prefer remote Streamable HTTP for cloud services.
- Use stdio for project-local tools and isolated subagents.
- Do not introduce new SSE servers; SSE is deprecated when HTTP is available.
- Use OAuth for remote user authentication where supported.
- Keep secrets out of `.mcp.json`; use user connectors, environment variables, or secure headers helpers.
