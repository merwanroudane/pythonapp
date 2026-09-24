"""Command explanations and value previews in the step-by-step view (§90)."""

from app.curriculum.schema import Animation, CommandNote
from app.execution.client import run_code
from app.ui.stepper import steps_for_animation, steps_from_run


def test_rich_notes_reach_the_step_with_anatomy_and_theory():
    anim = Animation(
        title="t",
        code="x = 2\ny = x * 3\n",
        notes={
            1: "plain note",
            2: CommandNote(what="multiply", parts=[("x * 3", "product")], theory="why"),
        },
    )
    steps = steps_from_run(run_code(anim.code, trace=True), anim.notes)
    by_line = {s.line: s for s in steps}
    assert by_line[1].note == "plain note" and by_line[1].parts == []
    assert by_line[2].note == "multiply"
    assert by_line[2].parts == [("x * 3", "product")]
    assert by_line[2].theory == "why"


def test_authored_steps_keep_parts_and_theory():
    anim = Animation(
        title="t",
        code="x = 1",
        source="authored",
        steps=[{"line": 1, "note": "n", "parts": [["x", "a name"]], "theory": "th"}],
    )
    (step,) = steps_for_animation(anim)
    assert step.parts == [("x", "a name")] and step.theory == "th"


def test_trace_previews_show_values_the_short_repr_cuts_off():
    code = "rows = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]] * 3\nrows[0][0] = 99\nn = 1\n"
    steps = run_code(code, trace=True).trace.steps
    # step 2 (before line 2) sees `rows` for the first time; its short repr is truncated
    assert "rows" in steps[1].previews
    assert "[10, 11, 12]" in steps[1].previews["rows"]
    # an in-place change the short repr would hide is still reported
    assert "99" in steps[2].previews["rows"]
    # values whose short repr already says everything get no preview
    assert all("n" not in s.previews for s in steps)


def test_big_builtin_containers_are_not_previewed():
    steps = run_code("big = list(range(5000))\nx = 1\n", trace=True).trace.steps
    assert all("big" not in s.previews for s in steps)


def test_a_statement_over_several_lines_is_one_step():
    code = 'd = dict(\n    a=1,\n    b=2,\n)\nif (d["a"] > 0\n        and d["b"] > 0):\n    n = 2\n'
    steps = steps_from_run(run_code(code, trace=True), code=code)
    assert [s.line for s in steps] == [1, 5, 7, None]


def test_repeated_loop_lines_are_kept():
    code = "t = 0\nfor i in range(3):\n    t += i\n"
    lines = [s.line for s in steps_from_run(run_code(code, trace=True), code=code)]
    assert lines == [1, 2, 3, 2, 3, 2, 3, 2, None]
