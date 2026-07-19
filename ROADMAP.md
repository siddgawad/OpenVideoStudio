# Roadmap

## Milestone 0 — Substrate (this PR)

The canonical scene graph + a working end-to-end pipeline, CLI-first, free-by-default.

- [x] Problem definition, decisions, architecture docs
- [x] `studio/` package: scene-graph model with validation, fingerprints, snapshots
- [x] Planner stage (LLM via OpenAI-compatible endpoint; deterministic offline mode)
- [x] Narration stage (edge-tts; offline silence synth)
- [x] Visual stage (local 1920×1080 motion-graphic slide renderer, themable)
- [x] Scene render + assembly (ffmpeg: clips, concat, captions)
- [x] Package stage (title/description/tags + thumbnail)
- [x] Scene-level edit + selective regeneration
- [x] Offline pytest suite; live end-to-end verification
- [x] README quickstart

## Milestone 1 — Trust & polish

- [ ] Research stage: sourced facts injected into planning, recorded per-scene
  (rights/claims traceability from PROBLEM_DEFINITION invariants)
- [ ] Stock-asset provider (Pexels/Openverse) behind the visual interface, with
  license recording per asset
- [ ] Background-music bed with ducking under narration
- [ ] Ken Burns / animated slide variants; per-scene visual styles
- [ ] Word-level caption timing (forced alignment) instead of even distribution
- [ ] `studio review` — agent watches its own output via the /watch skill and
  critiques hook, pacing, and visual/narration mismatch

## Milestone 2 — Conversational surface

- [ ] Chat loop (`studio chat`) that maps natural feedback to scene-graph edits
- [ ] Web UI (thin client over the same project file)
- [ ] Multi-aspect output (9:16 Shorts from the same scene graph)

## Milestone 3 — Ecosystem

- [ ] YouTube draft-upload MCP (consent-gated, private/unlisted only) per docs/MCP_SERVER_PLAN.md
- [ ] Hosted/cloud rendering profile
- [ ] Full Phase Zero research program (docs/PHASE_ZERO_PROMPT.md) resumed as a
  parallel workstream feeding provider decisions — see DECISION_LOG D-001

## Reference-video analysis workstream (continuous)

Use the `/watch` skill (bradautomates/claude-video, installed locally) on reference
YouTube/Instagram videos supplied by the owner; distill findings into
`docs/research/style-notes.md` and turn them into planner prompt improvements.
