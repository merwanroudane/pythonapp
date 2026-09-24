"""Content validation (blueprint §101.3). Used by scripts/validate_content.py and tests."""

from __future__ import annotations

from dataclasses import dataclass

from app.curriculum.blocks import KNOWN_TYPES, REFERENCES
from app.curriculum.loader import Curriculum


@dataclass(frozen=True)
class Issue:
    lesson: str
    message: str

    def __str__(self) -> str:
        return f"[{self.lesson}] {self.message}"


def _compiles(code: str) -> bool:
    try:
        compile(code, "<content>", "exec")
    except SyntaxError:
        return False
    return True


def validate(curriculum: Curriculum) -> list[Issue]:
    issues: list[Issue] = []
    track_ids = {t.id for t in curriculum.tracks}
    lesson_ids = set(curriculum.lessons)

    for lesson_id, lesson in curriculum.lessons.items():
        meta = lesson.meta

        def add(msg: str, _lid: str = lesson_id) -> None:
            issues.append(Issue(_lid, msg))

        if meta.track not in track_ids:
            add(f"unknown track '{meta.track}'")
        if not meta.objectives:
            add("lesson has no objectives")
        for prereq in meta.prerequisites:
            if prereq not in lesson_ids:
                add(f"prerequisite '{prereq}' does not exist")
        if not meta.docs_url:
            add("missing docs_url")

        used: dict[str, set[str]] = {collection: set() for collection in REFERENCES.values()}
        for block in lesson.blocks:
            where = f"lesson.md line {block.line}"
            if block.type not in KNOWN_TYPES:
                add(f"{where}: unknown block type '{block.type}'")
                continue
            if block.type in REFERENCES:
                ref = block.attrs.get("id")
                collection = REFERENCES[block.type]
                if not ref:
                    add(f"{where}: '{block.type}' needs an id")
                elif ref not in getattr(meta, collection):
                    add(f"{where}: {block.type} id '{ref}' not found in lesson.yaml {collection}")
                else:
                    used[collection].add(ref)
            if block.type == "code":
                expects_error = block.attrs.get("expect") == "syntax_error"
                if not block.body.strip():
                    add(f"{where}: empty code block")
                elif _compiles(block.body) == expects_error:
                    state = "compiles" if expects_error else "has a syntax error"
                    add(f"{where}: code block {state}")

        for collection, used_ids in used.items():
            for unused in set(getattr(meta, collection)) - used_ids:
                add(f"{collection} item '{unused}' is defined but never placed in lesson.md")

        for ex_id, exercise in meta.exercises.items():
            if not _compiles(exercise.solution + "\n" + exercise.tests):
                add(f"exercise '{ex_id}': solution + tests do not compile")
        for anim_id, anim in meta.animations.items():
            if not _compiles(anim.code):
                add(f"animation '{anim_id}': code does not compile")
    return issues
