# MVP Architecture (Milestone 0)

## Shape

```
topic ─▶ plan ─▶ project.json (scene graph) ─▶ build ─▶ final.mp4 + package/
              ▲                                 │
              └────── edit (scene-level) ◀──────┘   only stale scenes re-render
```

Everything durable lives in a **project directory**:

```
my-video/
├── project.json          # canonical scene graph — the single source of truth
├── history/              # timestamped snapshots of project.json (rollback)
├── assets/
│   ├── s1.narration.mp3  # per-scene narration audio
│   ├── s1.slide.png      # per-scene visual
│   └── s1.clip.mp4       # per-scene rendered clip
├── captions.srt
├── final.mp4
└── package/
    ├── metadata.json     # title, description, tags
    └── thumbnail.png
```

## Scene graph (`project.json`, schema_version 0.1)

```jsonc
{
  "schema_version": "0.1",
  "project": { "id", "title", "topic", "created_at", "language",
               "aspect": "16:9", "voice", "theme" },
  "brief":   { "audience", "tone", "goal" },
  "scenes": [
    {
      "id": "s1", "index": 0,
      "narration": "spoken text …",
      "visual": { "kind": "slide", "heading": "…", "bullets": ["…"], "accent": "#4f8ef7" },
      "duration_s": 7.4,              // measured from narration audio after render
      "rendered_fingerprint": "sha256…", // inputs at last successful render; null = never rendered
      "assets": { "audio": "assets/s1.narration.mp3", "image": "assets/s1.slide.png",
                  "clip": "assets/s1.clip.mp4" },
      "sources": []                    // rights/claims traceability (Milestone 1 fills this)
    }
  ],
  "package": { "title", "description", "tags", "thumbnail_text" }
}
```

**Fingerprint** = SHA-256 over (narration, visual spec, voice, theme, aspect,
renderer version). `build` renders a scene iff `fingerprint(inputs) !=
rendered_fingerprint`. Assembly re-runs iff any scene rendered or the output is
missing. This is the mechanism behind selective regeneration (D-005).

**Snapshots**: every mutating command copies `project.json` →
`history/<utc-timestamp>.json` before writing. `studio restore` copies one back.

## Module layout (`studio/` package)

| Module | Responsibility | External surface it wraps |
|---|---|---|
| `model.py` | dataclasses ↔ JSON, validation, fingerprints, snapshots | — |
| `llm.py` | chat-completion client (stdlib urllib), JSON-object responses, retry; `OfflinePlanner` | any OpenAI-compatible endpoint (Groq default) |
| `planner.py` | topic/brief → scenes + package metadata; scene-level revision prompts | `llm.py` |
| `tts.py` | narration text → mp3 + measured duration; offline = ffmpeg silence | edge-tts CLI / ffmpeg |
| `visuals.py` | visual spec → 1920×1080 PNG (theme, wrapped text, accent bar); thumbnail | Pillow |
| `media.py` | ffmpeg/ffprobe wrappers: still+audio→clip, concat, srt, mux subtitles | ffmpeg |
| `pipeline.py` | orchestrates stages over the scene graph; only-stale logic | all above |
| `cli.py` | `new · build · edit · status · restore` (argparse) | — |

Provider independence: `planner` depends on a `Chat` protocol (any callable
returning a JSON object), `tts` on a `Speaker` protocol. Swapping Groq→Ollama is an
env-var change (`STUDIO_LLM_BASE_URL`, `STUDIO_LLM_MODEL`, `STUDIO_LLM_API_KEY`);
swapping edge-tts→piper is one new Speaker class.

## CLI contract

```
python -m studio new  "<topic>" [--dir D] [--scenes N] [--tone T] [--voice V] [--offline]
python -m studio build <dir> [--offline] [--force]
python -m studio edit  <dir> --scene s3 --note "make it punchier" [--offline]
python -m studio edit  <dir> --scene s3 --narration "exact new text"
python -m studio status <dir>
python -m studio restore <dir> [--snapshot NAME]   # latest if omitted
```

`new` plans and writes the scene graph (no rendering). `build` renders stale scenes
and assembles. `edit --note` asks the LLM to revise that scene only; `--narration`
is a direct, no-LLM edit. Both mark the scene stale via fingerprint mismatch.

## Failure policy

- ffmpeg/edge-tts failures raise with captured stderr; nothing half-written — stages
  write to temp names and rename on success.
- LLM output is schema-validated; one repair retry with the validation error, then
  a hard, explained failure. Offline mode never fails.

## Testing policy (mirrors claude-video's approach)

Unit/integration tests are **offline and keyless**: deterministic planner, silence
TTS, real Pillow rendering, real ffmpeg assembly on synthesized media. Live Groq +
edge-tts runs are a manual verification step, not CI.
