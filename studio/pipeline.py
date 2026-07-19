"""Pipeline orchestration over the scene graph.

`build()` is idempotent: it renders only scenes whose input fingerprint
differs from the fingerprint recorded at their last successful render
(selective regeneration, D-005), then re-assembles when anything changed.
"""

from __future__ import annotations

import json
from pathlib import Path

from .media import concat_clips, mux_subtitles, probe_duration, write_srt
from .model import Project, Scene
from .tts import get_speaker
from .visuals import render_slide, render_thumbnail


class BuildReport:
    def __init__(self) -> None:
        self.rendered: list[str] = []
        self.skipped: list[str] = []
        self.assembled = False

    def summary(self) -> str:
        parts = [f"rendered {len(self.rendered)} scene(s)"
                 + (f" ({', '.join(self.rendered)})" if self.rendered else ""),
                 f"reused {len(self.skipped)}"]
        parts.append("assembled final.mp4" if self.assembled
                     else "assembly skipped (up to date)")
        return "; ".join(parts)


def _render_scene(project: Project, scene: Scene, project_dir: Path,
                  speaker, total: int) -> None:
    assets = project_dir / "assets"
    assets.mkdir(exist_ok=True)
    audio = assets / f"{scene.id}.narration.mp3"
    image = assets / f"{scene.id}.slide.png"
    clip = assets / f"{scene.id}.clip.mp4"

    speaker.speak(scene.narration, audio)
    render_slide(scene.visual, project.project.theme, image,
                 scene_number=scene.index + 1, total_scenes=total)

    from .media import still_plus_audio_clip
    scene.duration_s = round(still_plus_audio_clip(image, audio, clip), 3)
    scene.assets = {
        "audio": f"assets/{audio.name}",
        "image": f"assets/{image.name}",
        "clip": f"assets/{clip.name}",
    }
    scene.rendered_fingerprint = project.scene_fingerprint(scene)


def _assemble(project: Project, project_dir: Path) -> None:
    clips = []
    for scene in project.scenes:
        clip = project_dir / scene.assets.get("clip", "")
        if not clip.is_file():
            raise FileNotFoundError(f"{scene.id}: missing clip {clip} — rebuild")
        clips.append(clip)

    body = project_dir / "body.mp4"
    concat_clips(clips, body)

    # captions: narration text spread across each scene's real time window
    entries, cursor = [], 0.0
    for scene in project.scenes:
        dur = scene.duration_s or probe_duration(project_dir / scene.assets["clip"])
        entries.append((cursor, cursor + dur, scene.narration))
        cursor += dur
    srt = project_dir / "captions.srt"
    write_srt(entries, srt)

    final = project_dir / "final.mp4"
    mux_subtitles(body, srt, final)
    body.unlink(missing_ok=True)


def _package(project: Project, project_dir: Path) -> None:
    pkg_dir = project_dir / "package"
    pkg_dir.mkdir(exist_ok=True)
    meta = {
        "title": project.package.title or project.project.title,
        "description": project.package.description,
        "tags": project.package.tags,
        "publish_note": "Review before publishing. This tool never uploads.",
    }
    (pkg_dir / "metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    accent = project.scenes[0].visual.accent if project.scenes else "#4f8ef7"
    render_thumbnail(project.package.thumbnail_text or project.project.title,
                     accent, project.project.theme, pkg_dir / "thumbnail.png")


def build(project_dir: Path, *, offline: bool = False,
          force: bool = False) -> BuildReport:
    project_dir = Path(project_dir)
    project = Project.load(project_dir)
    project.validate()

    report = BuildReport()
    speaker = get_speaker(project.project.voice, offline)
    total = len(project.scenes)

    for scene in project.scenes:
        stale = force or project.scene_fingerprint(scene) != scene.rendered_fingerprint
        clip_ok = (project_dir / scene.assets.get("clip", "__missing__")).is_file()
        if stale or not clip_ok:
            _render_scene(project, scene, project_dir, speaker, total)
            report.rendered.append(scene.id)
            # persist progress scene-by-scene; render bookkeeping is not an
            # intent mutation, so no history snapshot
            project.save(project_dir, snapshot=False)
        else:
            report.skipped.append(scene.id)

    final = project_dir / "final.mp4"
    if report.rendered or not final.is_file():
        _assemble(project, project_dir)
        _package(project, project_dir)
        report.assembled = True

    project.save(project_dir, snapshot=False)
    return report
