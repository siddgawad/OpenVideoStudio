"""CLI: new · build · edit · status · restore.

Every mutating command snapshots project.json first (rollback), then writes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from .model import ModelError, Project, restore_snapshot
from .planner import get_planner


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:40] or "video"


def cmd_new(args) -> int:
    project = Project.new(args.topic, voice=args.voice, theme=args.theme,
                          tone=args.tone)
    project_dir = Path(args.dir) if args.dir else Path(_slug(args.topic))
    if (project_dir / "project.json").is_file():
        print(f"error: {project_dir} already has a project.json "
              f"(use `edit`/`build`, or choose --dir)", file=sys.stderr)
        return 2
    get_planner(args.offline).plan(project, args.scenes)
    project.save(project_dir)
    print(f"Planned {len(project.scenes)} scenes -> {project_dir / 'project.json'}")
    print(f"Title: {project.project.title}")
    for s in project.scenes:
        print(f"  {s.id}: {s.visual.heading} — {s.narration[:70]}"
              f"{'…' if len(s.narration) > 70 else ''}")
    print(f"\nNext: python -m studio build {project_dir}"
          f"{' --offline' if args.offline else ''}")
    return 0


def cmd_build(args) -> int:
    from .pipeline import build
    report = build(Path(args.dir), offline=args.offline, force=args.force)
    print(report.summary())
    final = Path(args.dir) / "final.mp4"
    if final.is_file():
        print(f"Output: {final}")
        print(f"Package: {Path(args.dir) / 'package'}")
    return 0


def cmd_edit(args) -> int:
    project_dir = Path(args.dir)
    project = Project.load(project_dir)
    scene = project.scene(args.scene)
    if args.narration:
        scene.narration = args.narration
        if args.heading:
            scene.visual.heading = args.heading
        project.validate()
    elif args.note:
        get_planner(args.offline).revise(project, args.scene, args.note)
    else:
        print("error: pass --note (LLM revision) or --narration (direct edit)",
              file=sys.stderr)
        return 2
    project.save(project_dir)  # snapshots previous version first
    stale = [s.id for s in project.stale_scenes()]
    print(f"Updated {scene.id}. Stale scenes: {', '.join(stale) or 'none'}")
    print(f"Next: python -m studio build {project_dir}")
    return 0


def cmd_status(args) -> int:
    project_dir = Path(args.dir)
    project = Project.load(project_dir)
    stale = {s.id for s in project.stale_scenes()}
    print(f"{project.project.title}  ({len(project.scenes)} scenes, "
          f"voice={project.project.voice}, theme={project.project.theme})")
    total = 0.0
    for s in project.scenes:
        mark = "stale " if s.id in stale else ("ok    " if s.rendered_fingerprint
                                               else "never ")
        dur = f"{s.duration_s:5.1f}s" if s.duration_s else "  --  "
        print(f"  {mark} {s.id:>3} {dur}  {s.visual.heading}")
        total += s.duration_s or 0
    print(f"Total rendered runtime: {total:.1f}s")
    final = project_dir / "final.mp4"
    print(f"final.mp4: {'present' if final.is_file() else 'not built'}")
    hist = sorted((project_dir / "history").glob("*.json")) \
        if (project_dir / "history").is_dir() else []
    print(f"History snapshots: {len(hist)}")
    return 0


def cmd_restore(args) -> int:
    name = restore_snapshot(Path(args.dir), args.snapshot)
    print(f"Restored project.json from snapshot {name}. "
          f"Run `build` to regenerate assets.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="studio",
        description="OpenVideoStudio — topic to release-ready video package.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("new", help="plan a new video project")
    p.add_argument("topic")
    p.add_argument("--dir", help="project directory (default: slug of topic)")
    p.add_argument("--scenes", type=int, default=6)
    p.add_argument("--tone", default=None)
    p.add_argument("--voice", default=None,
                   help="edge-tts voice, e.g. en-US-AriaNeural")
    p.add_argument("--theme", choices=["dark", "light"], default=None)
    p.add_argument("--offline", action="store_true",
                   help="deterministic planner, no LLM")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("build", help="render stale scenes and assemble")
    p.add_argument("dir")
    p.add_argument("--offline", action="store_true",
                   help="silent narration, no network")
    p.add_argument("--force", action="store_true", help="re-render everything")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("edit", help="revise one scene")
    p.add_argument("dir")
    p.add_argument("--scene", required=True, help="scene id, e.g. s3")
    p.add_argument("--note", help="natural-language change request (LLM)")
    p.add_argument("--narration", help="replace narration text directly")
    p.add_argument("--heading", help="with --narration: replace heading too")
    p.add_argument("--offline", action="store_true")
    p.set_defaults(func=cmd_edit)

    p = sub.add_parser("status", help="show scene/build state")
    p.add_argument("dir")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("restore", help="roll back project.json from history/")
    p.add_argument("dir")
    p.add_argument("--snapshot", help="snapshot name (default: latest)")
    p.set_defaults(func=cmd_restore)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ModelError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # provider/media failures: explain, don't traceback
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
