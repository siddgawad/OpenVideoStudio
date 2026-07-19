# Handoff

## Session 2026-07-19 (Claude Fable, build session)

**What exists now:** Milestone 0 is built and verified on branch
`feat/mvp-pipeline` — canonical scene graph + full CLI pipeline
(plan → narrate → render → assemble → package) with selective regeneration,
history snapshots, offline mode, and an 18-test offline suite (all passing).
Live-verified with Groq + edge-tts: real 4-scene video produced; LLM edit of
scene 1 re-rendered only scene 1. See DECISION_LOG D-001…D-007,
docs/PROBLEM_DEFINITION.md, docs/ARCHITECTURE_MVP.md, docs/tasks/ISSUES.md.

**Environment (this machine):** ffmpeg 8.1.2 via winget (shim dir
`%LOCALAPPDATA%\Microsoft\WinGet\Links` — may need adding to PATH in fresh
shells; studio/media.py falls back to it automatically), yt-dlp 2026.7.4,
edge-tts 7.2.8, Pillow 12.3.0, Python 3.14. The /watch skill
(bradautomates/claude-video, cloned at `C:\Users\theof\claude-video`) is
installed at `~/.claude/skills/watch` for reference-video analysis.

**Blocked on owner:**
- `gh auth login` — needed to push the branch, create the issues in
  docs/tasks/ISSUES.md, and open the PR.
- Reference video links (YouTube/Instagram) for the style-analysis
  workstream (ROADMAP, I-009).

**Next session:** push + PR from `feat/mvp-pipeline`; create issues I-001…I-010;
then Milestone 1 starting with I-005 (research + source traceability) and
I-008 (word-aligned captions via edge-tts WordBoundary events).
