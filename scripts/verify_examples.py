"""Run every executable example in the curriculum (blueprint §101.1).

Checks that:
  * code blocks run (or fail exactly the way ``expect=...`` says),
  * animations, quizzes' code and Change & Observe variants execute,
  * every exercise's reference solution passes its checks,
  * every exercise's starter code does NOT pass (otherwise the exercise is trivial).

    python scripts/verify_examples.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.curriculum.loader import load_curriculum  # noqa: E402
from app.execution.client import run_code  # noqa: E402

# Code blocks that intentionally raise at runtime, identified by their exception type.
# (Change & Observe "before" snippets often demonstrate one of these on purpose.)
RUNTIME_ERROR_OK = {"NameError", "TypeError", "ValueError", "ZeroDivisionError", "KeyError"}


def check_code(
    label: str, code: str, mode: str, expect: str | None, inputs: list[str] | None = None
) -> str | None:
    """``expect`` is "syntax_error", "timeout", an exception class name, or None."""
    result = run_code(code, mode=mode, inputs=inputs)
    raised = result.exception.type if result.exception else None
    if expect == "syntax_error":
        if raised not in ("SyntaxError", "IndentationError"):
            return f"{label}: expected a SyntaxError"
        return None
    if expect == "timeout":
        return None if result.status == "timeout" else f"{label}: expected a timeout"
    if expect:
        return None if raised == expect else f"{label}: expected {expect}, got {raised}"
    if result.status == "timeout":
        return f"{label}: timed out"
    if raised and raised not in RUNTIME_ERROR_OK:
        return f"{label}: {raised}: {result.exception.message}"
    return None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # Arabic / symbols on Windows consoles
    curriculum = load_curriculum()
    failures: list[str] = []
    checked = 0
    for lesson in curriculum.ordered_lessons():
        meta = lesson.meta
        for block in lesson.blocks:
            if block.type == "code" and block.attrs.get("run", "true") != "false":
                label = f"[{meta.id}] code @ line {block.line}"
                raw_inputs = block.attrs.get("inputs")
                failure = check_code(
                    label,
                    block.body,
                    block.attrs.get("mode", "script"),
                    block.attrs.get("expect"),
                    raw_inputs.split("\\n") if raw_inputs else None,  # same as the UI
                )
                checked += 1
                if failure:
                    failures.append(failure)
        for anim_id, anim in meta.animations.items():
            checked += 1
            result = run_code(anim.code, trace=True)
            if result.status != "ok" or not result.trace or not result.trace.steps:
                failures.append(f"[{meta.id}] animation '{anim_id}' did not trace cleanly")
            elif result.trace.truncated:
                failures.append(f"[{meta.id}] animation '{anim_id}' exceeds the trace step limit")
            elif anim.source == "trace":
                # A note on a line the tracer never stops at (a continuation line, a
                # branch not taken) would silently never be shown.
                executed = {s.line for s in result.trace.steps}
                for line_no in sorted(set(anim.notes) - executed):
                    failures.append(
                        f"[{meta.id}] animation '{anim_id}': note on line {line_no} never runs"
                    )
        for ch_id, change in meta.changes.items():
            for code in [change.base, *(v.code for v in change.variants)]:
                checked += 1
                if failure := check_code(f"[{meta.id}] change '{ch_id}'", code, change.mode, None):
                    failures.append(failure)
        for ex_id, ex in meta.exercises.items():
            checked += 2
            solved = run_code(f"{ex.solution}\n{ex.tests}", mode=ex.mode)
            if solved.status != "ok":
                detail = solved.exception.message if solved.exception else solved.status
                failures.append(f"[{meta.id}] exercise '{ex_id}': solution fails ({detail})")
            starter = run_code(f"{ex.starter}\n{ex.tests}", mode=ex.mode)
            if starter.status == "ok":
                failures.append(f"[{meta.id}] exercise '{ex_id}': starter already passes")
    for failure in failures:
        print("✗", failure)
    print(f"{checked} executions checked, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
