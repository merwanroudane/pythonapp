"""Step-by-step execution view (blueprint §7.2, §89, §90).

A declarative list of steps — generated from a real execution trace or authored by
hand in lesson.yaml — is played back with a unified control bar:
Play/Pause · Step back/forward · Reset · Speed · current-line highlight · state panel.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field

import streamlit as st

from app.curriculum.schema import Animation, CommandNote
from app.execution.client import run_code
from app.execution.models import RunResult
from app.ui.bidi import ltr
from app.ui.loop_view import LoopState, loop_state

SPEEDS = {"0.5×": 2.0, "1×": 1.0, "2×": 0.5}


@dataclass
class Step:
    line: int | None  # None = execution finished
    note: str = ""
    globals: dict[str, str] = field(default_factory=dict)
    locals: dict[str, str] = field(default_factory=dict)
    frame: str = "<module>"
    stack: list[str] = field(default_factory=list)
    stdout: str = ""
    frames: list[dict] = field(default_factory=list)  # [{"name", "locals"}], outermost first
    parts: list[tuple[str, str]] = field(default_factory=list)  # command anatomy
    theory: str = ""
    previews: dict[str, str] = field(default_factory=dict)  # full reprs of changed values


def statement_starts(code: str) -> dict[int, int]:
    """Continuation line -> first line of its statement (or of a compound header), so a
    statement written over several lines is one step instead of one per line."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}
    starts: dict[int, int] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.stmt):
            continue
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and isinstance(body[0], ast.stmt):
            last = body[0].lineno - 1  # only the header of if/for/def/with/...
        else:
            last = node.end_lineno or node.lineno
        for line in range(node.lineno + 1, last + 1):
            starts.setdefault(line, node.lineno)
    return starts


def steps_from_run(
    result: RunResult,
    notes: dict[int, str | CommandNote] | None = None,
    code: str | None = None,
) -> list[Step]:
    notes = notes or {}
    starts = statement_starts(code) if code else {}
    steps: list[Step] = []
    for s in result.trace.steps if result.trace else []:
        line = starts.get(s.line, s.line) if s.event == "line" else s.line
        if s.event == "line" and steps:
            last = steps[-1]
            same_state = (last.globals, last.locals, last.stdout) == (s.globals, s.locals, s.stdout)
            if last.line == line and last.frame == s.frame and same_state:
                continue  # another line of the statement already shown: nothing new
        if s.event == "call":
            args = ", ".join(f"{k}={v}" for k, v in s.locals.items())
            note = f"استدعاء `{s.frame}({args})`: يُنشأ call frame جديد."
        elif s.event == "return":
            note = f"`{s.frame}` تُعيد `{s.return_value}` إلى الـcaller ويُغلق الـframe."
        else:
            note = notes.get(line, "")
        parts: list[tuple[str, str]] = []
        theory = ""
        if isinstance(note, CommandNote):
            note, parts, theory = note.what, note.parts, note.theory
        steps.append(
            Step(
                line,
                note,
                s.globals,
                s.locals,
                s.frame,
                s.stack,
                s.stdout,
                s.frames,
                parts=list(parts),
                theory=theory,
                previews=s.previews,
            )
        )
    final_globals = {v.name: v.repr for v in result.variables}
    if result.exception:
        end_note = f"توقف التنفيذ بسبب `{result.exception.type}: {result.exception.message}`"
    else:
        end_note = "انتهى التنفيذ. هذه هي الحالة النهائية للأسماء."
    steps.append(Step(None, end_note, final_globals, stdout=result.stdout))
    return steps


def steps_from_authored(anim: Animation) -> list[Step]:
    return [
        Step(s.line, s.note, dict(s.state), stdout=s.stdout, parts=list(s.parts), theory=s.theory)
        for s in anim.steps
    ]


@st.cache_data(max_entries=256, show_spinner=False)
def _traced(code: str) -> RunResult:
    return run_code(code, trace=True)


def steps_for_animation(anim: Animation) -> list[Step]:
    if anim.source == "authored":
        return steps_from_authored(anim)
    return steps_from_run(_traced(anim.code), anim.notes, anim.code)


def _code_with_marker(code: str, line: int | None) -> str:
    lines = code.splitlines()
    if line is not None and 1 <= line <= len(lines):
        lines[line - 1] = f"{lines[line - 1]}    # ◀"
    return "\n".join(lines)


def _state_rows(current: dict[str, str], previous: dict[str, str]) -> list[dict]:
    rows = []
    for name, value in current.items():
        changed = previous.get(name) != value
        rows.append({"": "●" if changed else "", "Name": name, "Value": value})
    return rows


def _render_loop(loop: LoopState) -> None:
    """Three synced views of a for loop (§8.4): iterable, current item, body."""
    with st.container(border=True):
        st.markdown(f":material/loop: **حلقة for** في السطر {loop.header_line}")
        # The strip follows the code (LTR), like the list literal it mirrors.
        with st.container(horizontal=True, gap="small", wrap=True, key=f"loopstrip-{id(loop)}"):
            for n, item in enumerate(loop.items):
                if n < loop.index:
                    st.badge(ltr(item), icon=":material/check:", color="green")
                elif n == loop.index:
                    st.badge(ltr(item), icon=":material/arrow_downward:", color="orange")
                else:
                    st.badge(ltr(item), color="gray")
        if loop.index >= len(loop.items):
            st.caption("انتهت العناصر: الـiterator يرفع `StopIteration` فتخرج الحلقة.")
        elif loop.at_header:
            st.caption(f"الـheader يأخذ العنصر التالي ويربطه بـ`{loop.target}`.")
        else:
            st.caption(
                f"الدورة {loop.index + 1} من {len(loop.items)}: "
                f"`{loop.target}` = `{loop.items[loop.index]}`"
            )


def _render_frames(step: Step, prev: Step) -> None:
    """Call stack as stacked frames, newest on top (§8.6, §8.12)."""
    st.markdown(f"**Call stack** · {len(step.frames)} frame")
    previous = {f"{n}:{f['name']}": f["locals"] for n, f in enumerate(prev.frames)}
    for depth in range(len(step.frames) - 1, -1, -1):
        frame_info = step.frames[depth]
        top = depth == len(step.frames) - 1
        tone = "deepdive" if top else "neutral"
        with st.container(border=True, key=f"card-{tone}-frame-{id(step)}-{depth}"):
            label = "◀ الحالي" if top else f"ينتظر (depth {depth})"
            st.markdown(f"`{frame_info['name']}()` — {label}")
            rows = _state_rows(
                frame_info["locals"], previous.get(f"{depth}:{frame_info['name']}", {})
            )
            if rows:
                st.dataframe(rows, hide_index=True)


def _code_span(piece: str) -> str:
    fence = "``" if "`" in piece else "`"
    return f"{fence}{piece}{fence}" if fence == "`" else f"{fence} {piece} {fence}"


def _render_command(step: Step, key: str) -> None:
    """The explanation of the command about to run: what it does, its parts, the theory."""
    if not (step.note or step.parts or step.theory):
        return
    with st.container(border=True, key=f"card-concept-cmd-{key}"):
        with st.container(key=f"cardtitle-cmd-{key}"):
            where = f" · السطر {step.line}" if step.line is not None else ""
            label = "الأمر الحالي" if step.line is not None else "النهاية"
            st.markdown(f":material/terminal: {label}{where}")
        if step.note:
            st.markdown(step.note)
        if step.parts:
            st.markdown("**تشريح الأمر · Anatomy**")
            st.markdown("\n".join(f"- {_code_span(p)}: {m}" for p, m in step.parts))
    if step.theory:
        with st.container(border=True, key=f"card-theory-cmdtheory-{key}"):
            with st.container(key=f"cardtitle-cmdtheory-{key}"):
                st.markdown(":material/school: النظرية · لماذا يعمل هكذا؟")
            st.markdown(step.theory)


def _render_effect(step: Step, prev: Step, first: bool, key: str) -> None:
    """What the previous line did: the values it created or changed, and what it printed."""
    if first:
        return
    before = {**prev.globals, **prev.locals}
    now = {**step.globals, **step.locals}
    changed = [n for n, v in now.items() if before.get(n) != v or n in step.previews]
    printed = step.stdout[len(prev.stdout) :] if step.stdout.startswith(prev.stdout) else ""
    if not changed and not printed:
        return
    with st.container(border=True, key=f"card-practice-effect-{key}"):
        with st.container(key=f"cardtitle-effect-{key}"):
            what = f"ما فعله السطر {prev.line}" if prev.line is not None else "ما حدث"
            st.markdown(f":material/done_all: {what}")
        for name in changed[:4]:
            status = "جديد" if name not in before else "تغيّر"
            st.caption(f"`{name}` · {status}")
            st.code(step.previews.get(name) or now[name], language="text")
        if len(changed) > 4:
            st.caption(f"و{len(changed) - 4} أسماء أخرى في جدول Globals.")
        if printed:
            st.caption("طُبع على الشاشة:")
            st.code(printed, language="text")


def render_stepper(code: str, steps: list[Step], key: str, title: str | None = None) -> None:
    if not steps:
        st.caption("لا توجد خطوات لعرضها.")
        return
    idx_key, play_key, speed_key = f"{key}-idx", f"{key}-play", f"{key}-speed"
    st.session_state.setdefault(idx_key, 0)
    st.session_state.setdefault(play_key, False)
    total = len(steps)

    def go(delta: int | None = None, to: int | None = None) -> None:
        cur = st.session_state[idx_key]
        st.session_state[idx_key] = max(0, min(total - 1, to if to is not None else cur + delta))

    def toggle_play() -> None:
        if st.session_state[idx_key] >= total - 1:
            st.session_state[idx_key] = 0
        st.session_state[play_key] = not st.session_state[play_key]

    playing = st.session_state[play_key]
    speed = SPEEDS.get(st.session_state.get(speed_key) or "1×", 1.0)

    with st.container(border=True, key=f"card-example-{key}"):
        with st.container(key=f"cardtitle-{key}"):
            st.markdown(
                f":material/slideshow: تنفيذ خطوة بخطوة · Step Execution"
                f"{' — ' + title if title else ''}"
            )
        with st.container(horizontal=True, vertical_alignment="center", gap="small"):
            st.button(
                "إعادة",
                icon=":material/restart_alt:",
                key=f"{key}-reset",
                on_click=go,
                kwargs={"to": 0},
            )
            st.button(
                "السابق",
                icon=":material/chevron_right:",
                key=f"{key}-prev",
                on_click=go,
                kwargs={"delta": -1},
            )
            st.button(
                "إيقاف" if playing else "تشغيل تلقائي",
                icon=":material/pause:" if playing else ":material/play_arrow:",
                key=f"{key}-playbtn",
                type="primary",
                on_click=toggle_play,
            )
            st.button(
                "التالي",
                icon=":material/chevron_left:",
                key=f"{key}-next",
                on_click=go,
                kwargs={"delta": 1},
            )
            st.segmented_control(
                "السرعة",
                list(SPEEDS),
                default="1×",
                key=speed_key,
                format_func=ltr,
                label_visibility="collapsed",
            )

        @st.fragment(run_every=speed if playing else None)
        def frame() -> None:
            if st.session_state[play_key]:
                if st.session_state[idx_key] < total - 1:
                    st.session_state[idx_key] += 1
                else:
                    st.session_state[play_key] = False
                    st.rerun()
            i = st.session_state[idx_key]
            step, prev = steps[i], steps[i - 1] if i > 0 else Step(None)
            st.progress((i + 1) / total, text=f"الخطوة {i + 1} من {total}")
            code_col, state_col = st.columns([3, 2])
            with code_col:
                st.code(_code_with_marker(code, step.line), language="python", line_numbers=True)
                if step.line is not None:
                    st.caption(f"السطر {step.line} هو الذي **سيُنفَّذ الآن** (◀).")
                _render_effect(step, prev, i == 0, key)
            with state_col:
                _render_command(step, key)
                if (loop := loop_state(code, steps, i)) is not None:
                    _render_loop(loop)
                st.markdown("**Globals**")
                rows = _state_rows(step.globals, prev.globals)
                if rows:
                    st.dataframe(rows, hide_index=True)
                else:
                    st.caption("لا أسماء بعد.")
                if step.frames:
                    _render_frames(step, prev)
                st.markdown("**stdout**")
                st.code(step.stdout or " ", language="text")

        frame()
