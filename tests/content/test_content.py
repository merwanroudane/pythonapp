"""The shipped curriculum must always validate (blueprint §101)."""

from app.curriculum.blocks import KNOWN_TYPES
from app.curriculum.loader import load_curriculum
from app.curriculum.validation import validate


def test_curriculum_has_no_validation_issues():
    issues = validate(load_curriculum())
    assert not issues, "\n".join(map(str, issues))


def test_all_25_tracks_are_declared_in_order():
    tracks = load_curriculum().tracks
    assert [t.code for t in tracks] == [f"{i:02d}" for i in range(25)]


def test_every_lesson_meets_the_minimum_lecture_standard():
    """A slice of the §2.12 quality checklist that can be checked mechanically."""
    for lesson in load_curriculum().lessons.values():
        types = {b.type for b in lesson.blocks}
        assert types <= KNOWN_TYPES
        assert "code" in types, f"{lesson.meta.id}: no interactive code cell"
        assert types & {"quiz"}, f"{lesson.meta.id}: no predict/check activity"
        assert types & {"mistake", "warning"}, f"{lesson.meta.id}: no common mistake / warning"
        assert types & {"sketchnote", "cheatsheet"}, f"{lesson.meta.id}: no visual summary"
        if lesson.meta.kind == "practice":
            assert lesson.meta.exercises, f"{lesson.meta.id}: no exercise"
        else:
            assert "theory" in types, f"{lesson.meta.id}: theory lecture without theory blocks"
        assert lesson.meta.last_verified, f"{lesson.meta.id}: no last_verified date"
