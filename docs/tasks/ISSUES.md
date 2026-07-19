# Issue Queue

These drafts were created as GitHub issues #1–#10 on 2026-07-19 (assigned to
@siddgawad); I-001…I-004 map to #1–#4 and are closed by the Milestone-0 PR
(#11). This file remains as the durable, in-repo record.

---

## I-001 — Canonical scene graph: model, fingerprints, snapshots  `milestone-0` `done-in-pr-1`

Implement `studio/model.py`: dataclasses ↔ `project.json`, validation
(ModelError with precise messages), SHA-256 input fingerprints per scene
(D-005), atomic saves, `history/` snapshots + `restore_snapshot`.

**Acceptance:** round-trip preserves all fields; validation rejects empty
narration, duplicate ids, bad accents, wrong schema_version; fingerprint
changes only when inputs change; snapshot/restore round-trips. Covered by
`tests/test_model.py`.

---

## I-002 — Pipeline stages: plan, narrate, visualize, assemble, package  `milestone-0` `done-in-pr-1`

Planner (LLM via OpenAI-compatible endpoint + deterministic offline twin),
edge-tts narration (+ silent offline twin), Pillow slide/thumbnail renderer,
ffmpeg clip/concat/captions/mux, `pipeline.build()` with only-stale logic.

**Acceptance:** `new → build` produces final.mp4 + captions.srt + package/;
rebuild with no changes touches nothing; offline mode needs no network/keys.
Covered by `tests/test_media_and_visuals.py`, `tests/test_pipeline_cli.py`.

---

## I-003 — CLI: new · build · edit · status · restore  `milestone-0` `done-in-pr-1`

argparse CLI (`python -m studio`, `studio` entry point). Mutating commands
snapshot first. `edit --note` = LLM scene revision; `edit --narration` =
direct edit. Clean error messages, no tracebacks for expected failures.

**Acceptance:** full offline lifecycle test passes; editing s2 re-renders
only s2.clip.mp4 (verified by mtimes in test).

---

## I-004 — Live verification: Groq + edge-tts end-to-end  `milestone-0` `done-in-pr-1`

Verify the real-provider path: plan with Groq (llama-3.1-8b-instant), narrate
with en-US-GuyNeural, build, LLM-edit scene 1, selective rebuild.

**Result 2026-07-19:** 4-scene 23s video produced; streams h264+aac+mov_text;
audio peaks -4.2 dB; edit re-rendered only s1. Fixed en route: Cloudflare 403
on urllib default UA (added User-Agent), bullet line-height double-count.

---

## I-005 — Research stage with source traceability  `milestone-1`

Before planning, gather 3-5 sourced facts on the topic (web search provider
behind an interface); planner must ground narration in them; store per-scene
`sources[]` (url, claim, date checked). This is the claims-traceability
invariant from PROBLEM_DEFINITION.md.

---

## I-006 — Stock-asset visual provider with license recording  `milestone-1`

`visual.kind: "image"` path: Pexels/Openverse search behind a VisualProvider
interface; downloaded asset's source + license recorded in `sources[]`;
Ken Burns pan/zoom via ffmpeg zoompan for image scenes.

---

## I-007 — Background music bed with ducking  `milestone-1`

Optional royalty-free music track under narration with sidechain ducking
(ffmpeg sidechaincompress); per-project `music` field in the scene graph;
license recorded.

---

## I-008 — Word-aligned captions  `milestone-1`

Replace even-spread captions with real timing: edge-tts word-boundary
metadata (it emits WordBoundary events) or forced alignment; keep the
even-spread fallback for offline mode.

---

## I-009 — `studio review`: the agent watches its own output  `milestone-1`

Run the /watch skill (bradautomates/claude-video) over final.mp4, critique
hook strength, pacing, narration/visual mismatch; emit a review report the
user can turn into `edit` commands. Also: distill style notes from owner-
supplied reference videos (YouTube/Instagram) into planner prompt guidance.

---

## I-010 — `studio chat`: conversational editing loop  `milestone-2`

Natural-language feedback mapped to scene-graph edits (add/remove/reorder/
revise scenes, retone, retitle) with a diff preview before applying;
snapshots make every step reversible.
