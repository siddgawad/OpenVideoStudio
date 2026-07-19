from studio.model import Project
from studio.planner import OfflinePlanner


def test_offline_plan_is_valid_and_deterministic():
    a = Project.new("learning python")
    b = Project.new("learning python")
    OfflinePlanner().plan(a, 5)
    OfflinePlanner().plan(b, 5)
    assert len(a.scenes) == 5
    a.validate()
    assert [s.narration for s in a.scenes] == [s.narration for s in b.scenes]
    assert a.package.title and a.package.tags


def test_offline_plan_minimum_two_scenes():
    p = Project.new("x")
    OfflinePlanner().plan(p, 1)
    assert len(p.scenes) == 2


def test_offline_revise_marks_scene_stale():
    p = Project.new("learning python")
    OfflinePlanner().plan(p, 4)
    for s in p.scenes:
        s.rendered_fingerprint = p.scene_fingerprint(s)
    OfflinePlanner().revise(p, "s2", "make it about dictionaries")
    assert "dictionaries" in p.scene("s2").narration
    assert [s.id for s in p.stale_scenes()] == ["s2"]
