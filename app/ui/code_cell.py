"""Interactive code cell (blueprint §5.1): editor → Run → Output Inspector."""

from __future__ import annotations

import streamlit as st

from app.components.code_editor import code_editor, reset_editor
from app.execution.client import run_code
from app.execution.models import RunResult
from app.storage import progress
from app.ui.output_panel import render_output
from app.ui.stepper import render_stepper, steps_from_run

MODE_LABELS = {"script": "Script mode · .py", "notebook": "Notebook mode · .ipynb"}


def render_code_cell(
    code: str,
    *,
    key: str,
    lesson_id: str | None = None,
    mode: str = "script",
    allow_mode_switch: bool = False,
    inputs: str | None = None,
    runnable: bool = True,
) -> RunResult | None:
    if not runnable:
        st.code(code, language="python", line_numbers=True)
        return None

    editor_key, result_key = f"code-{key}", f"result-{key}"
    inputs_key, trace_key = f"inputs-{key}", f"trace-{key}"

    def reset() -> None:
        reset_editor(editor_key, code)
        st.session_state.pop(result_key, None)
        st.session_state.pop(trace_key, None)

    with st.container(border=True, key=f"cell-{key}"):
        if allow_mode_switch:
            chosen = st.segmented_control(
                "وضع التنفيذ",
                ["script", "notebook"],
                default=mode,
                key=f"mode-{key}",
                format_func=MODE_LABELS.get,
                label_visibility="collapsed",
            )
            mode = chosen or mode
        else:
            st.caption(f":material/terminal: {MODE_LABELS[mode]}")

        editor = code_editor(code, key=editor_key, min_lines=max(3, code.count("\n") + 1))
        feed = None
        if inputs is not None:
            st.session_state.setdefault(inputs_key, inputs)
            feed = st.text_area(
                "قيم input() — قيمة في كل سطر",
                key=inputs_key,
                height=80,
                help="تُمرَّر هذه القيم بالترتيب إلى كل استدعاء لـ`input()`.",
            )

        with st.container(horizontal=True, gap="small", vertical_alignment="center"):
            run_clicked = st.button(
                "تشغيل · Run", icon=":material/play_arrow:", type="primary", key=f"run-{key}"
            )
            step_clicked = st.button("خطوة بخطوة", icon=":material/footprint:", key=f"step-{key}")
            st.button(
                "إعادة الكود", icon=":material/restart_alt:", key=f"reset-{key}", on_click=reset
            )
            st.caption("Ctrl + Enter")

        if run_clicked or step_clicked or editor.run_requested:
            feed_values = feed.splitlines() if feed else []
            with st.spinner("يعمل الكود…"):
                result = run_code(editor.code, mode=mode, trace=step_clicked, inputs=feed_values)
            st.session_state[result_key] = result
            if step_clicked:
                st.session_state[trace_key] = editor.code
                st.session_state.pop(f"stepper-{key}-idx", None)
            else:
                st.session_state.pop(trace_key, None)
            if lesson_id:
                progress.mark_ran(lesson_id)
            if result.exception:
                progress.record_error(result.exception.type)

        result = st.session_state.get(result_key)
        if result is not None:
            render_output(result, notebook_mode=mode == "notebook", key=f"out-{key}")
            traced_source = st.session_state.get(trace_key)
            if traced_source is not None and result.trace is not None:
                render_stepper(traced_source, steps_from_run(result), key=f"stepper-{key}")
    return result
