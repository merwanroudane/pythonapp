"""Headless app tests with Streamlit's AppTest (blueprint §102.2)."""

import pytest
from streamlit.testing.v1 import AppTest

from app.config import ROOT
from app.curriculum.loader import load_curriculum

LESSON_IDS = sorted(load_curriculum().lessons)


def _lesson_script(lesson_id: str) -> None:
    import streamlit as st

    from app.ui.lesson_renderer import render_lesson
    from app.ui.navigation import build_navigation
    from app.ui.theme import inject_css

    inject_css()
    st.navigation(build_navigation(render_lesson), position="hidden")
    render_lesson(lesson_id)


def _lesson_app(lesson_id: str) -> AppTest:
    at = AppTest.from_function(_lesson_script, args=(lesson_id,), default_timeout=60)
    return at.run()


def test_home_dashboard_renders():
    at = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=60).run()
    assert not at.exception
    assert any("مختبر" in t.value for t in at.title)
    assert len(at.metric) == 4


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_every_lesson_renders_without_exception(lesson_id):
    at = _lesson_app(lesson_id)
    assert not at.exception, at.exception
    assert at.title, "lesson has no title"


def test_run_button_executes_and_shows_output():
    at = _lesson_app("variables-assignment")
    run_key = next(b.key for b in at.button if b.key and b.key.startswith("run-"))
    at.button(key=run_key).click().run()
    assert not at.exception
    assert any("10" in c.value for c in at.code), "stdout of the first cell not shown"


def test_quiz_marks_progress_when_correct():
    at = _lesson_app("print-vs-return")
    radio = next(r for r in at.radio if r.key and r.key.startswith("quizradio-"))
    radio.set_value(1).run()  # correct answer: None
    at.button(key=radio.key.replace("quizradio-", "quizbtn-")).click().run()
    assert any("إجابة صحيحة" in s.value for s in at.success)
    assert at.session_state["progress"]["print-vs-return"]["quizzes"]


def test_exercise_reference_solution_passes_in_the_ui():
    lesson = load_curriculum().lessons["print-vs-return"]
    at = _lesson_app("print-vs-return")
    editor = next(
        t for t in at.text_area if t.key and t.key.startswith("code-") and "def mean" in t.value
    )
    editor.set_value(lesson.meta.exercises["ex-mean"].solution).run()
    at.button(key=editor.key.replace("code-", "check-", 1)).click().run()
    assert any("أحسنت" in s.value for s in at.success)


def test_view_modes_filter_blocks():
    at = _lesson_app("for-loop")
    learn_count = len(at.code)
    at.segmented_control(key="view-for-loop-mode").set_value("review").run()
    assert not at.exception
    assert len(at.code) < learn_count
