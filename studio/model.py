"""Canonical scene graph: dataclasses <-> project.json, validation,
fingerprints, and history snapshots.

The project directory is the durable artifact. Everything in it is derivable
from project.json plus the pipeline; assets are a cache keyed by fingerprints.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import RENDERER_VERSION

SCHEMA_VERSION = "0.1"

_HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
_SCENE_ID = re.compile(r"^s\d+$")


class ModelError(ValueError):
    """Raised when a scene graph fails validation."""


@dataclass
class VisualSpec:
    kind: str = "slide"  # slide | image (image = user/stock asset, Milestone 1)
    heading: str = ""
    bullets: list[str] = field(default_factory=list)
    accent: str = "#4f8ef7"

    def validate(self, where: str) -> None:
        if self.kind not in ("slide", "image"):
            raise ModelError(f"{where}: unknown visual kind {self.kind!r}")
        if self.kind == "slide" and not self.heading.strip():
            raise ModelError(f"{where}: slide visual needs a heading")
        if not _HEX_COLOR.match(self.accent):
            raise ModelError(f"{where}: accent must be #rrggbb, got {self.accent!r}")
        if len(self.bullets) > 6:
            raise ModelError(f"{where}: at most 6 bullets, got {len(self.bullets)}")


@dataclass
class Scene:
    id: str
    index: int
    narration: str
    visual: VisualSpec = field(default_factory=VisualSpec)
    duration_s: float | None = None
    rendered_fingerprint: str | None = None
    assets: dict[str, str] = field(default_factory=dict)
    sources: list[dict] = field(default_factory=list)

    def validate(self) -> None:
        where = f"scene {self.id!r}"
        if not _SCENE_ID.match(self.id):
            raise ModelError(f"{where}: id must look like 's1'")
        if not self.narration.strip():
            raise ModelError(f"{where}: narration is empty")
        if len(self.narration) > 2000:
            raise ModelError(f"{where}: narration over 2000 chars")
        self.visual.validate(where)


@dataclass
class Brief:
    audience: str = "general viewers"
    tone: str = "clear and engaging"
    goal: str = ""


@dataclass
class ProjectMeta:
    id: str
    title: str
    topic: str
    created_at: str
    language: str = "en"
    aspect: str = "16:9"
    voice: str = "en-US-GuyNeural"
    theme: str = "dark"


@dataclass
class PackageMeta:
    title: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    thumbnail_text: str = ""


@dataclass
class Project:
    project: ProjectMeta
    brief: Brief = field(default_factory=Brief)
    scenes: list[Scene] = field(default_factory=list)
    package: PackageMeta = field(default_factory=PackageMeta)
    schema_version: str = SCHEMA_VERSION

    # ---- construction -------------------------------------------------

    @staticmethod
    def new(topic: str, *, title: str | None = None, voice: str | None = None,
            theme: str | None = None, tone: str | None = None) -> "Project":
        meta = ProjectMeta(
            id=uuid.uuid4().hex[:12],
            title=title or topic.strip().capitalize(),
            topic=topic.strip(),
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        if voice:
            meta.voice = voice
        if theme:
            meta.theme = theme
        brief = Brief()
        if tone:
            brief.tone = tone
        return Project(project=meta, brief=brief)

    # ---- validation ---------------------------------------------------

    def validate(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ModelError(
                f"schema_version {self.schema_version!r} != {SCHEMA_VERSION!r}")
        if not self.scenes:
            raise ModelError("project has no scenes")
        if len(self.scenes) > 40:
            raise ModelError(f"too many scenes ({len(self.scenes)}); max 40")
        seen: set[str] = set()
        for i, scene in enumerate(self.scenes):
            scene.index = i
            if scene.id in seen:
                raise ModelError(f"duplicate scene id {scene.id!r}")
            seen.add(scene.id)
            scene.validate()

    # ---- fingerprints (selective regeneration, D-005) -----------------

    def scene_fingerprint(self, scene: Scene) -> str:
        payload = json.dumps(
            {
                "narration": scene.narration,
                "visual": dataclasses.asdict(scene.visual),
                "voice": self.project.voice,
                "theme": self.project.theme,
                "aspect": self.project.aspect,
                "renderer": RENDERER_VERSION,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def stale_scenes(self) -> list[Scene]:
        return [s for s in self.scenes
                if s.rendered_fingerprint != self.scene_fingerprint(s)]

    def scene(self, scene_id: str) -> Scene:
        for s in self.scenes:
            if s.id == scene_id:
                return s
        raise ModelError(
            f"no scene {scene_id!r}; have {[s.id for s in self.scenes]}")

    # ---- persistence --------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "project": dataclasses.asdict(self.project),
            "brief": dataclasses.asdict(self.brief),
            "scenes": [dataclasses.asdict(s) for s in self.scenes],
            "package": dataclasses.asdict(self.package),
        }

    @staticmethod
    def from_dict(data: dict) -> "Project":
        try:
            scenes = [
                Scene(
                    id=s["id"],
                    index=int(s.get("index", i)),
                    narration=s["narration"],
                    visual=VisualSpec(**s.get("visual", {})),
                    duration_s=s.get("duration_s"),
                    rendered_fingerprint=s.get("rendered_fingerprint"),
                    assets=dict(s.get("assets", {})),
                    sources=list(s.get("sources", [])),
                )
                for i, s in enumerate(data.get("scenes", []))
            ]
            return Project(
                schema_version=data.get("schema_version", ""),
                project=ProjectMeta(**data["project"]),
                brief=Brief(**data.get("brief", {})),
                scenes=scenes,
                package=PackageMeta(**data.get("package", {})),
            )
        except (KeyError, TypeError) as exc:
            raise ModelError(f"malformed project.json: {exc}") from exc

    @staticmethod
    def load(project_dir: Path) -> "Project":
        path = Path(project_dir) / "project.json"
        if not path.is_file():
            raise ModelError(f"{path} not found — is this a studio project dir?")
        return Project.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def save(self, project_dir: Path, *, snapshot: bool = True) -> None:
        """Write project.json atomically, snapshotting the previous version."""
        project_dir = Path(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)
        path = project_dir / "project.json"
        if snapshot and path.is_file():
            hist = project_dir / "history"
            hist.mkdir(exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
            (hist / f"{stamp}.json").write_bytes(path.read_bytes())
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
                       encoding="utf-8")
        tmp.replace(path)


def restore_snapshot(project_dir: Path, snapshot: str | None = None) -> str:
    """Restore project.json from history/. Returns the snapshot name used."""
    project_dir = Path(project_dir)
    hist = project_dir / "history"
    candidates = sorted(hist.glob("*.json")) if hist.is_dir() else []
    if not candidates:
        raise ModelError(f"no snapshots under {hist}")
    if snapshot:
        chosen = hist / (snapshot if snapshot.endswith(".json") else snapshot + ".json")
        if not chosen.is_file():
            raise ModelError(f"snapshot {snapshot!r} not found in {hist}")
    else:
        chosen = candidates[-1]
    Project.from_dict(json.loads(chosen.read_text(encoding="utf-8")))  # validate parse
    (project_dir / "project.json").write_bytes(chosen.read_bytes())
    return chosen.stem
