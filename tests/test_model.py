import json

import pytest

from studio.model import ModelError, Project, Scene, VisualSpec, restore_snapshot


def make_project(n=3):
    p = Project.new("test topic")
    p.scenes = [
        Scene(id=f"s{i+1}", index=i, narration=f"Narration {i+1}.",
              visual=VisualSpec(heading=f"Heading {i+1}"))
        for i in range(n)
    ]
    return p


def test_roundtrip_preserves_everything(tmp_path):
    p = make_project()
    p.scenes[1].duration_s = 4.2
    p.scenes[1].rendered_fingerprint = "abc"
    p.scenes[1].assets = {"clip": "assets/s2.clip.mp4"}
    p.save(tmp_path)
    q = Project.load(tmp_path)
    assert q.to_dict() == p.to_dict()


def test_validation_rejects_bad_graphs():
    p = make_project()
    p.scenes[0].narration = "   "
    with pytest.raises(ModelError, match="narration is empty"):
        p.validate()

    p = make_project()
    p.scenes[1].id = "s1"
    with pytest.raises(ModelError, match="duplicate"):
        p.validate()

    p = make_project()
    p.scenes[0].visual.accent = "blue"
    with pytest.raises(ModelError, match="accent"):
        p.validate()

    p = make_project()
    p.schema_version = "9.9"
    with pytest.raises(ModelError, match="schema_version"):
        p.validate()


def test_fingerprint_changes_only_on_input_change():
    p = make_project()
    fp = p.scene_fingerprint(p.scenes[0])
    # non-input fields don't affect the fingerprint
    p.scenes[0].duration_s = 99
    p.scenes[0].assets = {"clip": "x"}
    assert p.scene_fingerprint(p.scenes[0]) == fp
    # inputs do
    p.scenes[0].narration = "Different."
    assert p.scene_fingerprint(p.scenes[0]) != fp
    p = make_project()
    p.project.voice = "en-GB-SoniaNeural"
    assert p.scene_fingerprint(p.scenes[0]) != fp


def test_stale_scenes_tracks_fingerprints():
    p = make_project()
    assert [s.id for s in p.stale_scenes()] == ["s1", "s2", "s3"]
    for s in p.scenes:
        s.rendered_fingerprint = p.scene_fingerprint(s)
    assert p.stale_scenes() == []
    p.scenes[2].narration = "Changed."
    assert [s.id for s in p.stale_scenes()] == ["s3"]


def test_snapshot_and_restore(tmp_path):
    p = make_project()
    p.save(tmp_path)                      # first save: no snapshot yet
    assert not (tmp_path / "history").exists()
    original_narration = p.scenes[0].narration
    p.scenes[0].narration = "Edited."
    p.save(tmp_path)                      # snapshots the previous version
    snaps = list((tmp_path / "history").glob("*.json"))
    assert len(snaps) == 1
    name = restore_snapshot(tmp_path)
    assert name == snaps[0].stem
    q = Project.load(tmp_path)
    assert q.scenes[0].narration == original_narration


def test_load_rejects_malformed(tmp_path):
    (tmp_path / "project.json").write_text(json.dumps({"scenes": []}))
    with pytest.raises(ModelError, match="malformed"):
        Project.load(tmp_path)
