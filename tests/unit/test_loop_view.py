"""For-loop panel and call-stack capture for the step-through view (§8.4, §8.12)."""

from app.execution.client import run_code
from app.ui.loop_view import loop_state
from app.ui.stepper import steps_from_run


def _states(code: str):
    steps = steps_from_run(run_code(code, trace=True))
    return steps, [loop_state(code, steps, i) for i in range(len(steps))]


def test_loop_progress_over_a_named_list():
    code = "xs = [12, 5, 8]\nt = 0\nfor p in xs:\n    t += p\nprint(t)"
    steps, states = _states(code)
    body = [(s.index, s.at_header) for s in states if s is not None]
    assert body == [(0, True), (0, False), (1, True), (1, False), (2, True), (2, False), (3, True)]
    assert states[-1] is None  # final "finished" step
    assert next(s for s in states if s).items == ["12", "5", "8"]


def test_range_and_enumerate_are_resolved_without_running_code():
    code = "for i, c in enumerate('ab', start=1):\n    pass\nfor k in range(2):\n    pass"
    _, states = _states(code)
    loops = {s.target: s.items for s in states if s is not None}
    assert loops["(i, c)"] == ["(1, 'a')", "(2, 'b')"]
    assert loops["k"] == ["0", "1"]


def test_unknown_iterable_gives_no_panel():
    code = "def gen():\n    yield 1\nfor v in gen():\n    pass"
    _, states = _states(code)
    assert all(s is None for s in states)


def test_call_stack_shows_every_recursive_frame():
    code = "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\nfact(3)"
    steps = steps_from_run(run_code(code, trace=True))
    deepest = max(steps, key=lambda s: len(s.frames))
    assert [f["locals"]["n"] for f in deepest.frames] == ["3", "2", "1"]
