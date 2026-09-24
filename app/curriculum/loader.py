"""Load tracks and lessons from ``content/`` (blueprint §80)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from app.config import CONTENT_DIR
from app.curriculum import directives
from app.curriculum.schema import Lesson, LessonMeta, Track


@dataclass
class Curriculum:
    tracks: list[Track]
    lessons: dict[str, Lesson] = field(default_factory=dict)

    def track(self, track_id: str) -> Track:
        return next(t for t in self.tracks if t.id == track_id)

    def lessons_in(self, track_id: str) -> list[Lesson]:
        items = [lesson for lesson in self.lessons.values() if lesson.meta.track == track_id]
        return sorted(items, key=lambda lesson: lesson.meta.order)

    def ordered_lessons(self) -> list[Lesson]:
        order = {t.id: t.order for t in self.tracks}
        return sorted(
            self.lessons.values(), key=lambda les: (order.get(les.meta.track, 999), les.meta.order)
        )

    def neighbours(self, lesson_id: str) -> tuple[Lesson | None, Lesson | None]:
        seq = self.ordered_lessons()
        idx = next(i for i, les in enumerate(seq) if les.meta.id == lesson_id)
        prev_lesson = seq[idx - 1] if idx > 0 else None
        next_lesson = seq[idx + 1] if idx + 1 < len(seq) else None
        return prev_lesson, next_lesson


def load_tracks(content_dir: Path = CONTENT_DIR) -> list[Track]:
    raw = yaml.safe_load((content_dir / "tracks.yaml").read_text(encoding="utf-8"))
    return sorted((Track.model_validate(item) for item in raw["tracks"]), key=lambda t: t.order)


def load_lesson(lesson_dir: Path) -> Lesson:
    meta_raw = yaml.safe_load((lesson_dir / "lesson.yaml").read_text(encoding="utf-8"))
    meta = LessonMeta.model_validate(meta_raw)
    body = (lesson_dir / "lesson.md").read_text(encoding="utf-8")
    return Lesson(meta=meta, blocks=directives.parse(body), source_dir=str(lesson_dir))


def load_curriculum(content_dir: Path = CONTENT_DIR) -> Curriculum:
    curriculum = Curriculum(tracks=load_tracks(content_dir))
    for meta_file in sorted((content_dir / "lessons").glob("*/*/lesson.yaml")):
        lesson = load_lesson(meta_file.parent)
        if lesson.meta.id in curriculum.lessons:
            raise ValueError(f"duplicate lesson id: {lesson.meta.id}")
        curriculum.lessons[lesson.meta.id] = lesson
    return curriculum


def content_signature(content_dir: Path = CONTENT_DIR) -> tuple[tuple[str, float], ...]:
    """Cheap fingerprint so cached content reloads when an author edits a file."""
    files = [content_dir / "tracks.yaml", *content_dir.glob("lessons/*/*/lesson.*")]
    files += list(content_dir.glob("*.yaml"))
    return tuple(sorted((str(p), p.stat().st_mtime) for p in files if p.exists()))
