# Problem Definition (v1 — 2026-07-19)

## The problem, stated maximally

A person with an idea for a YouTube video — but no editing skill, no design skill, no
scripting experience, and no budget — cannot today turn that idea into a publishable
video without either (a) learning a professional toolchain (Premiere/Resolve/CapCut +
scripting + voiceover + thumbnails), (b) paying a stack of SaaS subscriptions
(Jasper + ElevenLabs + Pictory/InVideo + Canva), or (c) hiring people. Every existing
"AI video" product fails on at least one of these axes:

1. **Opaque regeneration.** Feedback like "make scene 3 punchier" forces a full
   regeneration; the user loses everything they already approved.
2. **Provider lock-in.** The script, voice, and visuals are welded to one vendor's
   models and one vendor's pricing.
3. **No durable, editable artifact.** The "project" lives inside a web app; there is
   no portable file a user (or another tool) can open, diff, version, or repair.
4. **Dishonest economics.** "Free" tiers hide compute costs; users cannot see what a
   video actually costs to produce.
5. **No rights traceability.** Users cannot answer "am I allowed to publish this?" —
   which assets are licensed, which voices are consented, which claims are sourced.

## The answer we are building

An open-source, conversational video-production studio whose center of gravity is a
**canonical, human-readable project file (the scene graph)** rather than a vendor's
database row. Everything else — LLMs, TTS, image sources, renderers — plugs into that
file through provider-independent interfaces.

**Product promise (from the charter):** Describe the video. Review the direction.
Give feedback naturally. Receive a polished, editable, release-ready YouTube package.

## Users

- **Primary:** non-technical creators (educators, small-business owners, hobbyists)
  who can describe what they want in plain language.
- **Secondary:** technical creators who want a scriptable, versionable pipeline
  (the same CLI/file format, driven by automation or an AI agent).

## What "end-to-end" means (the full loop)

idea → brief → research → script → scene plan → narration audio → per-scene visuals
→ per-scene clips → assembled video with captions → title/description/tags/thumbnail
→ human review → **targeted revision of individual scenes** → re-assembly →
release-ready package. Publication is always a human act — never automated.

## Invariants (from PROJECT_CHARTER.md — restated as testable constraints)

| Invariant | Testable form |
|---|---|
| Provider independence | Every external capability sits behind an interface; swapping the LLM/TTS/visual provider changes zero pipeline code |
| Structured editable scene graph | `project.json` fully describes the video; deleting all rendered assets and rebuilding reproduces it |
| Selective regeneration | Editing scene N re-renders only scene N + re-assembly; all other assets are byte-identical (fingerprint check) |
| Version history & rollback | Every mutation snapshots the project file; any snapshot can be restored |
| Rights traceability | Every asset in the project records its source and license |
| Consent & approval | No publish/upload capability without explicit human action; no voice cloning in core |
| Honest economics | Every provider call can be attributed; free-by-default MVP (no paid API required) |
| FOSS core | Core runs entirely on free/local components: Groq free tier or any OpenAI-compatible endpoint, edge-tts, ffmpeg, Pillow |

## MVP scope (in)

- CLI-first studio (`python -m studio …`) producing a narrated 16:9 MP4 with burned
  or sidecar captions, per-scene motion-graphic slides (local rendering — zero API
  keys required for visuals), scene-level regeneration, project versioning, and a
  metadata package (title, description, tags, thumbnail).
- Deterministic offline mode (`--offline`) so the entire pipeline runs and is testable
  with no network and no keys.
- LLM via any OpenAI-compatible chat endpoint (Groq free tier default).
- TTS via edge-tts (free Microsoft neural voices), pluggable.

## MVP scope (out — deferred, recorded in ROADMAP.md)

- Web UI / conversational chat surface (the CLI + project file is the substrate it
  will drive later).
- Generated video/image models (SDXL, etc.), stock-footage integration, music beds.
- YouTube draft upload MCP, hosted/cloud rendering, accounts, collaboration.
- Voice cloning and likeness features (consent machinery must exist first).

## Success criteria for the MVP

1. `studio new "topic" && studio build` produces a watchable MP4 + package on a
   clean machine with only ffmpeg + Python + (optionally) a free Groq key.
2. `studio edit --scene s3 --note "…"` changes only scene 3's assets (verified by
   fingerprints) and re-assembles.
3. Full pytest suite passes offline with no API keys.
4. A non-technical user can follow README quickstart without touching internals.
