# OpenVideoStudio

**Describe the video. Review the direction. Give feedback naturally. Get a
release-ready YouTube package.** Open source, provider-independent, free by
default.

```
$ studio new "why the sky is blue" --scenes 4
Planned 4 scenes -> why-the-sky-is-blue/project.json

$ studio build why-the-sky-is-blue
rendered 4 scene(s); assembled final.mp4

$ studio edit why-the-sky-is-blue --scene s1 --note "open with a bolder hook"
Updated s1. Stale scenes: s1

$ studio build why-the-sky-is-blue
rendered 1 scene(s) (s1); reused 3; assembled final.mp4
```

The result: a narrated 1080p MP4 with captions, plus `package/` containing a
YouTube title, description, tags, and a thumbnail. Editing scene 1 re-rendered
*only* scene 1 — everything you already approved stays byte-identical.

## Why this exists

Every "AI video" product locks your project inside its web app, regenerates
everything when you ask for one change, and welds you to one vendor's models
and pricing. OpenVideoStudio inverts that:

- **The project is a file, not a database row.** `project.json` is a canonical,
  human-readable scene graph. Version it, diff it, edit it by hand, or point
  another tool (or AI agent) at it.
- **Selective regeneration.** Every scene carries a fingerprint of its inputs;
  a change re-renders exactly the scenes it touches.
- **Provider independence.** The LLM is any OpenAI-compatible endpoint (Groq
  free tier, OpenAI, local Ollama). TTS and rendering sit behind interfaces.
- **Free by default.** Core pipeline needs zero paid APIs: free Groq key for
  planning (or `--offline`), free Microsoft neural voices, local rendering.
- **You publish, not the tool.** No upload automation. Ever, without consent.

## Install

Requirements: Python 3.10+, ffmpeg on PATH.

```bash
# ffmpeg: winget install Gyan.FFmpeg   |   brew install ffmpeg   |   apt install ffmpeg
git clone https://github.com/siddgawad/OpenVideoStudio.git
cd OpenVideoStudio
pip install -e .
```

For LLM planning, set a key (free at console.groq.com/keys):

```bash
export GROQ_API_KEY=...            # or STUDIO_LLM_API_KEY
# optional overrides:
export STUDIO_LLM_BASE_URL=https://api.groq.com/openai/v1   # any OpenAI-compatible URL
export STUDIO_LLM_MODEL=llama-3.3-70b-versatile
```

No key? Everything still runs with `--offline` (deterministic script, silent
narration) — useful for trying the mechanics, testing, and CI.

## Commands

| Command | What it does |
|---|---|
| `studio new "<topic>" [--scenes N] [--tone T] [--voice V] [--theme dark\|light]` | Plan the video: brief, script, scenes, metadata → `project.json` |
| `studio build <dir>` | Render stale scenes (narration + slide + clip) and assemble `final.mp4`, `captions.srt`, `package/` |
| `studio edit <dir> --scene s3 --note "…"` | LLM revises that one scene |
| `studio edit <dir> --scene s3 --narration "…"` | Direct text edit, no LLM |
| `studio status <dir>` | Scene table: rendered/stale, durations, snapshots |
| `studio restore <dir>` | Roll back `project.json` to a previous snapshot |

Voices: any [edge-tts voice](https://github.com/rany2/edge-tts) (`edge-tts --list-voices`),
e.g. `--voice en-US-AriaNeural`.

## The scene graph

```jsonc
{
  "schema_version": "0.1",
  "project": { "title": "…", "topic": "…", "voice": "en-US-GuyNeural", "theme": "dark" },
  "scenes": [
    { "id": "s1",
      "narration": "What if you could…",
      "visual": { "kind": "slide", "heading": "The Hook", "bullets": ["…"], "accent": "#4f8ef7" },
      "rendered_fingerprint": "sha256…",
      "assets": { "audio": "assets/s1.narration.mp3", "clip": "assets/s1.clip.mp4" } }
  ],
  "package": { "title": "…", "description": "…", "tags": ["…"], "thumbnail_text": "…" }
}
```

Every mutating command snapshots the previous `project.json` into `history/`
first, so any state is recoverable. Full spec: `docs/ARCHITECTURE_MVP.md`.

## Development

```bash
pip install -e .[dev]
python -m pytest -q     # 18 tests, fully offline — no keys, no network
```

Tests exercise the real pipeline (Pillow rendering, ffmpeg encoding/concat/mux)
on synthesized media, in the spirit of
[claude-video](https://github.com/bradautomates/claude-video)'s test suite.

## Project governance & roadmap

This repo doubles as a Claude-driven research/build workspace — see
`PROJECT_CHARTER.md`, `docs/PROBLEM_DEFINITION.md`, `DECISION_LOG.md`, and
`ROADMAP.md`. Current limits (honest list):

- Visuals are motion-graphic slides only — stock/generated footage is Milestone 1.
- Caption timing is spread evenly per scene, not word-aligned.
- No music bed yet; no web/chat UI yet (the CLI + scene graph is the substrate).
- English-first prompts; other languages work but are untested.

## License

MIT.
