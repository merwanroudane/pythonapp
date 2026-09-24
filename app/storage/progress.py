"""Learner progress (blueprint §98).

Reading a page is not mastery. A lesson moves through three levels:
introduced (opened) → practiced (ran code / answered a check) → demonstrated
(passed every quiz and exercise in it).

Phase A keeps this in st.session_state only; persistent storage per §104 comes with
accounts in Phase G, behind this same interface.
"""

from __future__ import annotations

from collections import Counter
from typing import Literal

import streamlit as st

from app.curriculum.schema import Lesson

Status = Literal["not_started", "introduced", "practiced", "demonstrated"]

STATUS_LABELS: dict[Status, str] = {
    "not_started": "لم يبدأ",
    "introduced": "تعرّف",
    "practiced": "تدرّب",
    "demonstrated": "أتقن",
}
STATUS_ICONS: dict[Status, str] = {
    "not_started": ":material/radio_button_unchecked:",
    "introduced": ":material/visibility:",
    "practiced": ":material/fitness_center:",
    "demonstrated": ":material/verified:",
}


def _store() -> dict:
    return st.session_state.setdefault("progress", {})


def _entry(lesson_id: str) -> dict:
    return _store().setdefault(
        lesson_id, {"viewed": False, "ran": False, "quizzes": set(), "exercises": set()}
    )


def mark_viewed(lesson_id: str) -> None:
    _entry(lesson_id)["viewed"] = True
    st.session_state["last_lesson"] = lesson_id


def mark_ran(lesson_id: str) -> None:
    _entry(lesson_id)["ran"] = True


def mark_quiz(lesson_id: str, quiz_id: str) -> None:
    _entry(lesson_id)["quizzes"].add(quiz_id)


def mark_exercise(lesson_id: str, exercise_id: str) -> None:
    _entry(lesson_id)["exercises"].add(exercise_id)


def record_error(exception_type: str) -> None:
    """Feeds the dashboard's "Common errors I faced" panel (§4)."""
    st.session_state.setdefault("errors_faced", Counter())[exception_type] += 1


def errors_faced() -> Counter:
    return st.session_state.get("errors_faced", Counter())


def last_lesson() -> str | None:
    return st.session_state.get("last_lesson")


def status(lesson: Lesson) -> Status:
    entry = _store().get(lesson.meta.id)
    if not entry or not entry["viewed"]:
        return "not_started"
    need_quizzes = set(lesson.meta.quizzes)
    need_exercises = set(lesson.meta.exercises)
    if (
        (need_quizzes or need_exercises)
        and need_quizzes <= entry["quizzes"]
        and (need_exercises <= entry["exercises"])
    ):
        return "demonstrated"
    if entry["ran"] or entry["quizzes"] or entry["exercises"]:
        return "practiced"
    return "introduced"


def reset_lesson(lesson_id: str) -> None:
    """Forget progress and every widget/result state of one lesson (header Reset button)."""
    _store().pop(lesson_id, None)
    marker = f"-{lesson_id}-"
    for key in [k for k in st.session_state if isinstance(k, str) and marker in k]:
        del st.session_state[key]


def widget_key(kind: str, lesson_id: str, name: str | int) -> str:
    """CSS-safe widget key; also becomes the ``st-key-<key>`` class used by theme.py."""
    return f"{kind}-{lesson_id}-{name}"
