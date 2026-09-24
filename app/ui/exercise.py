"""Exercise engine v1 (blueprint §76): write code, check it with hidden tests, graded hints."""

from __future__ import annotations

import streamlit as st

from app.components.code_editor import code_editor
from app.curriculum.schema import Exercise
from app.execution.client import run_code
from app.storage import progress
from app.ui.output_panel import render_error

_HINT_LEVELS = ["تلميح مفاهيمي", "تلميح في الصياغة", "جزء من الحل"]


def render_exercise(exercise: Exercise, *, exercise_id: str, lesson_id: str, key: str) -> None:
    editor_key, verdict_key, hints_key = f"code-{key}", f"verdict-{key}", f"hints-{key}"
    st.session_state.setdefault(hints_key, 0)

    def more_hints() -> None:
        st.session_state[hints_key] += 1

    with st.container(key=f"card-practice-{key}", border=True):
        with st.container(key=f"cardtitle-{key}"):
            st.markdown(f":material/exercise: تمرين · Exercise — {exercise.title}")
        st.markdown(exercise.prompt)
        editor = code_editor(
            exercise.starter,
            key=editor_key,
            label="حلّك",
            min_lines=max(5, exercise.starter.count("\n") + 2),
        )
        source = editor.code
        shown = st.session_state[hints_key]
        total_hints = len(exercise.hints)
        with st.container(horizontal=True, gap="small"):
            check = st.button(
                "تحقّق من الحل", icon=":material/fact_check:", type="primary", key=f"check-{key}"
            )
            st.button(
                f"تلميح ({min(shown, total_hints)}/{total_hints})",
                icon=":material/lightbulb:",
                key=f"hint-{key}",
                on_click=more_hints,
                disabled=shown > total_hints,
            )

        for level, hint in enumerate(exercise.hints[:shown]):
            name = _HINT_LEVELS[min(level, len(_HINT_LEVELS) - 1)]
            st.info(f"**{name}:** {hint}", icon=":material/lightbulb:")
        if shown > total_hints:
            with st.expander(":material/visibility: الحل المرجعي · Reference solution"):
                st.code(exercise.solution, language="python")

        if check or editor.run_requested:
            program = f"{source}\n\n# --- checks ---\n{exercise.tests}\n"
            with st.spinner("يجري الفحص…"):
                result = run_code(program, mode=exercise.mode)
            st.session_state[verdict_key] = (result, source.count("\n") + 1)
            progress.mark_ran(lesson_id)
            if result.status == "ok":
                progress.mark_exercise(lesson_id, exercise_id)
            elif result.exception:
                progress.record_error(result.exception.type)

        verdict = st.session_state.get(verdict_key)
        if verdict is None:
            return
        result, learner_lines = verdict
        if result.status == "ok":
            st.success("**أحسنت! اجتاز حلّك كل الفحوص.**", icon=":material/celebration:")
            if result.stdout:
                st.code(result.stdout, language="text")
            with st.expander(":material/compare: قارن مع الحل المرجعي"):
                st.code(exercise.solution, language="python")
                st.caption("حلّك صحيح حتى لو اختلف شكله؛ قد توجد أكثر من طريقة صالحة.")
        elif result.status == "timeout":
            st.warning(result.runner_message or "Timeout", icon=":material/timer_off:")
        elif result.exception:
            exc = result.exception
            in_checks = exc.lineno is not None and exc.lineno > learner_lines
            if exc.type == "AssertionError" and in_checks:
                st.error(
                    f"**لم يجتز الفحص:** {exc.message or 'النتيجة لا تطابق المتوقع.'}",
                    icon=":material/rule:",
                )
            elif in_checks and exc.type == "NameError":
                st.error(
                    f"**الفحص يبحث عن اسم غير موجود:** `{exc.missing_name}`. "
                    "هل سمّيت الدالة أو المتغير كما يطلب التمرين؟",
                    icon=":material/rule:",
                )
            else:
                render_error(result, f"exverdict-{key}")
