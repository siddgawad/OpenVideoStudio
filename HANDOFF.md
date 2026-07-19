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

**GitHub state:** branch pushed; issues #1–#10 created and assigned to
@siddgawad (via stored git credentials — the `gh` CLI itself is still
unauthenticated); PR #11 open: Milestone 0 (closes #1–#4).

**Blocked on owner:**
- Review + merge PR #11.
- Reference video links (YouTube/Instagram) for the style-analysis
  workstream (ROADMAP, issue #9).

**Next session:** Milestone 1 starting with #5 (research + source
traceability) and #8 (word-aligned captions via edge-tts WordBoundary
events).
