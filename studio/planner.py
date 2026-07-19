"""Planning stage: topic -> brief + scenes + package metadata, and
scene-level revision. Two interchangeable planners (provider independence):

- LivePlanner  — LLM via studio.llm.chat_json
- OfflinePlanner — deterministic templates; no network, no keys (D-006)
"""

from __future__ import annotations

import re

from .model import ModelError, PackageMeta, Project, Scene, VisualSpec

ACCENTS = ["#4f8ef7", "#f7784f", "#43c59e", "#e4c441", "#b07cf7", "#f75f8e"]

_PLAN_SYSTEM = """You are the head writer for a video studio. You turn a topic
into a tight YouTube video plan. Reply with ONLY a JSON object:

{
  "title": "video title, <=70 chars, curiosity without clickbait lies",
  "description": "2-4 sentence YouTube description",
  "tags": ["8-14 short tags"],
  "thumbnail_text": "3-5 punchy words for the thumbnail",
  "scenes": [
    {
      "narration": "what the narrator says in this scene, 1-3 spoken sentences, no stage directions",
      "heading": "on-screen heading, <=6 words",
      "bullets": ["0-4 short on-screen bullet points, <=8 words each"]
    }
  ]
}

Rules:
- Scene 1 is the hook: open with the payoff or a sharp question, never "welcome to".
- One idea per scene. Narration must read naturally aloud.
- Last scene closes the loop and gives one clear takeaway or call to action.
- Write narration for the requested tone and audience."""

_REVISE_SYSTEM = """You revise ONE scene of a video. Reply with ONLY a JSON object:
{"narration": "...", "heading": "...", "bullets": ["..."]}
Keep the scene's role in the overall flow; apply the requested change. Narration
is spoken text only, 1-3 sentences, no stage directions."""


def _clean_scene_fields(raw: dict, where: str) -> tuple[str, str, list[str]]:
    narration = str(raw.get("narration", "")).strip()
    heading = str(raw.get("heading", "")).strip() or "—"
    bullets = [str(b).strip() for b in raw.get("bullets", []) if str(b).strip()][:4]
    if not narration:
        raise ModelError(f"{where}: planner returned empty narration")
    return narration, heading, bullets


class LivePlanner:
    def plan(self, project: Project, n_scenes: int) -> None:
        from .llm import chat_json
        user = (
            f"Topic: {project.project.topic}\n"
            f"Audience: {project.brief.audience}\n"
            f"Tone: {project.brief.tone}\n"
            f"Language: {project.project.language}\n"
            f"Scene count: exactly {n_scenes} scenes."
        )
        data = chat_json(_PLAN_SYSTEM, user)
        scenes_raw = data.get("scenes") or []
        if not isinstance(scenes_raw, list) or not scenes_raw:
            raise ModelError("planner returned no scenes")
        project.scenes = []
        for i, raw in enumerate(scenes_raw[:n_scenes]):
            narration, heading, bullets = _clean_scene_fields(raw, f"scene {i + 1}")
            project.scenes.append(Scene(
                id=f"s{i + 1}", index=i, narration=narration,
                visual=VisualSpec(kind="slide", heading=heading, bullets=bullets,
                                  accent=ACCENTS[i % len(ACCENTS)]),
            ))
        title = str(data.get("title", "")).strip() or project.project.title
        project.project.title = title[:80]
        project.package = PackageMeta(
            title=title[:100],
            description=str(data.get("description", "")).strip(),
            tags=[str(t).strip() for t in data.get("tags", []) if str(t).strip()][:15],
            thumbnail_text=str(data.get("thumbnail_text", "")).strip() or title[:40],
        )
        project.validate()

    def revise(self, project: Project, scene_id: str, note: str) -> None:
        from .llm import chat_json
        scene = project.scene(scene_id)
        outline = "\n".join(f"{s.id}: {s.visual.heading} — {s.narration[:90]}"
                            for s in project.scenes)
        user = (
            f"Video topic: {project.project.topic}\n"
            f"Tone: {project.brief.tone}\n"
            f"Full outline:\n{outline}\n\n"
            f"Scene to revise: {scene.id}\n"
            f"Current narration: {scene.narration}\n"
            f"Current heading: {scene.visual.heading}\n"
            f"Current bullets: {scene.visual.bullets}\n\n"
            f"Requested change: {note}"
        )
        data = chat_json(_REVISE_SYSTEM, user)
        narration, heading, bullets = _clean_scene_fields(data, scene.id)
        scene.narration = narration
        scene.visual.heading = heading
        scene.visual.bullets = bullets
        project.validate()


class OfflinePlanner:
    """Deterministic, key-free planner for tests, demos, and air-gapped use."""

    def plan(self, project: Project, n_scenes: int) -> None:
        topic = project.project.topic
        project.scenes = []
        for i in range(max(2, n_scenes)):
            if i == 0:
                narration = (f"What if you could master {topic} in the next few "
                             f"minutes? Here's the short version.")
                heading, bullets = topic.title()[:48], ["The short version"]
            elif i == max(2, n_scenes) - 1:
                narration = (f"That's the core of {topic}. Start with one step "
                             f"today, and build from there.")
                heading, bullets = "Your move", ["Start with one step"]
            else:
                narration = (f"Key idea {i}: break {topic} into small, concrete "
                             f"parts, and practice each one deliberately.")
                heading, bullets = f"Key idea {i}", ["Small concrete parts",
                                                     "Deliberate practice"]
            project.scenes.append(Scene(
                id=f"s{i + 1}", index=i, narration=narration,
                visual=VisualSpec(kind="slide", heading=heading, bullets=bullets,
                                  accent=ACCENTS[i % len(ACCENTS)]),
            ))
        title = f"{topic.title()}, Explained Simply"
        project.project.title = title[:80]
        project.package = PackageMeta(
            title=title[:100],
            description=f"A quick, practical introduction to {topic}.",
            tags=[w.lower() for w in re.findall(r"[A-Za-z]{3,}", topic)][:10]
                 or ["video"],
            thumbnail_text=topic.title()[:40],
        )
        project.validate()

    def revise(self, project: Project, scene_id: str, note: str) -> None:
        scene = project.scene(scene_id)
        scene.narration = f"{scene.narration.rstrip('.')}. ({note.strip()})"
        project.validate()


def get_planner(offline: bool):
    return OfflinePlanner() if offline else LivePlanner()
