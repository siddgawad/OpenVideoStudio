# Decision Log

Format: D-NNN · date · status. Facts vs. inference vs. recommendation are separated
where it matters. Reversals get a new entry, never an edit.

---

## D-001 · 2026-07-19 · ACCEPTED — Owner directive supersedes full Phase Zero

The repository charter gates implementation behind a complete Phase Zero audit. On
2026-07-19 the owner (siddgawad) directed: analyze, plan, then **build the MVP
end-to-end now**. Conflict recorded per CLAUDE.md. Resolution: run a *condensed*
feasibility pass inline (tooling, licensing of direct dependencies, cost truth),
build the MVP, and leave the full Phase Zero research program as a parallel
workstream in ROADMAP.md rather than a blocking gate.

## D-002 · 2026-07-19 · ACCEPTED — MVP is a local-first CLI pipeline over a canonical scene graph

Rationale: the charter's hard invariants (provider independence, selective
regeneration, version history, editable artifact) are all properties of the **data
model**, not of a UI. Building the scene-graph substrate + pipeline first means the
future conversational/web surface is a thin client over an already-proven core.
Alternative rejected: starting with a web app (locks us into UI decisions before the
data model is proven; violates "do not spend the session generating generic UI").

## D-003 · 2026-07-19 · ACCEPTED — Provider choices for the free-by-default MVP

| Capability | Provider | Why | License/cost (checked 2026-07-19) |
|---|---|---|---|
| LLM (script/planning) | Any OpenAI-compatible chat endpoint; Groq free tier default | Owner already has a Groq key; endpoint-shape independence = provider independence | Groq free tier; interface works with OpenAI, Ollama (local, $0), LM Studio |
| TTS | edge-tts 7.x (pip) | Free Microsoft neural voices, no key, good quality | LGPL-3.0 (used as unmodified library dependency — acceptable; can vendor-swap to piper/kokoro later) |
| Visual rendering | Pillow (local slide/motion-graphic renderer) | Zero keys, deterministic, testable | MIT-CMU |
| Media assembly | ffmpeg (external binary, shelled out) | Universal, already the industry substrate | LGPL/GPL build — external process, not linked, so no license coupling |
| Video analysis (inspiration/QC) | bradautomates/claude-video `/watch` skill | Lets the agent watch reference videos (YouTube/Instagram) to inform style | MIT |

Fact: all of the above verified installed and working on the dev machine 2026-07-19
(ffmpeg 8.1.2, yt-dlp 2026.7.4, edge-tts 7.2.8, Pillow 12.3.0, Python 3.14).

## D-004 · 2026-07-19 · ACCEPTED — Core stays dependency-light (stdlib + Pillow + edge-tts)

No pydantic/typer/moviepy in the core. Scene graph = dataclasses + explicit
validation; CLI = argparse; media ops = ffmpeg subprocess. Inspired by
claude-video's pure-stdlib discipline: fewer deps → installable everywhere, fewer
supply-chain reviews (SECURITY_BOUNDARIES.md §9), easier for contributors.

## D-005 · 2026-07-19 · ACCEPTED — Selective regeneration via input fingerprints

Every scene stores a SHA-256 fingerprint of its *inputs* (narration text, visual
spec, voice, theme). A build step re-renders a scene only when its fingerprint
differs from the one recorded at last render. Assembly re-runs when any scene asset
changed. This makes "edit scene 3" provably touch only scene 3 (MVP success
criterion #2).

## D-006 · 2026-07-19 · ACCEPTED — Offline deterministic mode is a first-class path

`--offline` swaps the LLM for a deterministic template planner and TTS for
ffmpeg-synthesized silence, so the *entire* pipeline (plan → build → edit →
assemble → package) runs with no network, no keys. This is what the test suite
exercises; live providers are an integration concern, not a unit-test concern.

## D-007 · 2026-07-19 · ACCEPTED — No publish automation in core

The package stage emits metadata + thumbnail only. YouTube upload (even private
drafts) is deferred to a future consent-gated MCP per docs/MCP_SERVER_PLAN.md.
