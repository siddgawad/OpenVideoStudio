"""End-to-end offline: new -> build -> edit -> selective rebuild -> restore.

Exercises the real CLI entry points with the offline planner and silent
narration; ffmpeg and Pillow run for real.
"""

from pathlib import Path

from studio.cli import main
from studio.model import Project


def _mtimes(project_dir: Path) -> dict[str, float]:
    return {p.name: p.stat().st_mtime_ns
            for p in (project_dir / "assets").glob("*.clip.mp4")}


def test_full_offline_lifecycle(tmp_path):
    d = tmp_path / "proj"

    # new
    assert main(["new", "quantum computing basics", "--dir", str(d),
                 "--scenes", "3", "--offline"]) == 0
    project = Project.load(d)
    assert len(project.scenes) == 3
    assert not (d / "final.mp4").exists()

    # build
    assert main(["build", str(d), "--offline"]) == 0
    assert (d / "final.mp4").is_file()
    assert (d / "captions.srt").is_file()
    assert (d / "package" / "metadata.json").is_file()
    assert (d / "package" / "thumbnail.png").is_file()
    project = Project.load(d)
    assert all(s.rendered_fingerprint for s in project.scenes)
    assert all((d / s.assets["clip"]).is_file() for s in project.scenes)

    # rebuild with no changes: nothing re-rendered, assembly skipped
    before = _mtimes(d)
    assert main(["build", str(d), "--offline"]) == 0
    assert _mtimes(d) == before

    # edit scene 2 only
    assert main(["edit", str(d), "--scene", "s2",
                 "--narration", "Completely new narration for scene two."]) == 0
    project = Project.load(d)
    assert [s.id for s in project.stale_scenes()] == ["s2"]

    # selective rebuild: only s2's clip changes (MVP success criterion #2)
    assert main(["build", str(d), "--offline"]) == 0
    after = _mtimes(d)
    changed = {k for k in before if before[k] != after[k]}
    assert changed == {"s2.clip.mp4"}

    # snapshot exists from the edit; restore brings old narration back
    assert main(["restore", str(d)]) == 0
    project = Project.load(d)
    assert "Completely new" not in project.scene("s2").narration

    # status runs on the restored project
    assert main(["status", str(d)]) == 0


def test_new_refuses_to_clobber(tmp_path):
    d = tmp_path / "proj"
    assert main(["new", "topic one", "--dir", str(d), "--offline"]) == 0
    assert main(["new", "topic two", "--dir", str(d), "--offline"]) == 2


def test_edit_requires_note_or_narration(tmp_path):
    d = tmp_path / "proj"
    assert main(["new", "topic", "--dir", str(d), "--offline"]) == 0
    assert main(["edit", str(d), "--scene", "s1"]) == 2


def test_unknown_scene_errors_cleanly(tmp_path):
    d = tmp_path / "proj"
    assert main(["new", "topic", "--dir", str(d), "--offline"]) == 0
    assert main(["edit", str(d), "--scene", "s99", "--narration", "x"]) == 1
