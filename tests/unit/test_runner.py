"""Code runner behaviour and safety limits (blueprint §5.5, §102.3, §129)."""

from app.execution.client import run_code


def test_stdout_and_variables_are_separated():
    r = run_code("x = 2\nprint('hi', x)")
    assert r.status == "ok"
    assert r.stdout == "hi 2\n"
    assert [(v.name, v.type, v.repr) for v in r.variables] == [("x", "int", "2")]


def test_notebook_mode_shows_last_expression_script_mode_does_not():
    code = "a = 3\na * 2"
    assert run_code(code, mode="notebook").result["text"] == "6"
    assert run_code(code, mode="script").result is None


def test_none_last_expression_is_not_displayed():
    assert run_code("print('x')", mode="notebook").result is None


def test_exception_is_structured_and_traceback_hides_harness():
    r = run_code("def f():\n    return 1 / 0\nf()")
    assert r.status == "error"
    assert r.exception.type == "ZeroDivisionError"
    assert r.exception.lineno == 2
    assert "harness" not in r.exception.traceback
    assert "return 1 / 0" in r.exception.traceback


def test_syntax_error_reports_position():
    r = run_code("if True\n    pass")
    assert r.exception.type == "SyntaxError"
    assert r.exception.lineno == 1


def test_warnings_are_captured():
    r = run_code("import warnings\nwarnings.warn('careful')")
    assert [(w.category, w.message) for w in r.warnings] == [("UserWarning", "careful")]


def test_library_deprecations_are_hidden_but_user_ones_kept():
    code = (
        "import warnings\n"
        "warnings.warn_explicit('old api', DeprecationWarning, 'somelib.py', 3)\n"
        "warnings.warn('mine is old', DeprecationWarning)\n"
        "warnings.warn_explicit('lib runtime', RuntimeWarning, 'somelib.py', 4)\n"
    )
    r = run_code(code)
    assert [w.message for w in r.warnings] == ["mine is old", "lib runtime"]


def test_aliases_are_detected():
    r = run_code("a = [1]\nb = a\nc = [1]")
    assert sorted(next(iter(r.alias_groups().values()))) == ["a", "b"]


def test_input_bridge_feeds_values_and_reports_exhaustion():
    ok = run_code("n = int(input('n? '))\nprint(n + 1)", inputs=["41"])
    assert ok.stdout == "n? 41\n42\n"
    short = run_code("input(); input()", inputs=["only one"])
    assert short.exception.type == "InputExhausted"


def test_infinite_loop_times_out():
    r = run_code("while True:\n    pass", timeout=1.5)
    assert r.status == "timeout"


def test_huge_output_is_capped():
    r = run_code("for _ in range(10**6):\n    print('xxxxxxxxxx')", timeout=10)
    assert r.stdout_truncated is True
    assert len(r.stdout) <= 20_000


def test_environment_is_stripped_and_cwd_starts_empty(monkeypatch):
    monkeypatch.setenv("PLL_FAKE_SECRET", "s3cr3t")
    r = run_code(
        "import os\nprint(os.environ.get('PLL_FAKE_SECRET'))\nprint(sorted(os.listdir('.')))"
    )
    assert r.stdout.splitlines() == ["None", "[]"]  # job/result files are outside the cwd


def test_memory_bomb_is_contained():
    r = run_code("x = bytearray(3 * 1024**3)")
    assert r.status in ("error", "runner_error")
    if r.exception:
        assert r.exception.type == "MemoryError"


def test_spawning_processes_is_blocked():
    r = run_code("import subprocess, sys\nsubprocess.run([sys.executable, '-c', 'print(1)'])")
    assert r.status == "error"
    assert r.exception.type in ("OSError", "PermissionError", "BlockingIOError")


def test_result_reports_backend_and_memory():
    r = run_code("x = list(range(1000))")
    assert r.backend == "local"
    assert r.memory_peak_mb is None or r.memory_peak_mb > 0


def test_trace_records_calls_returns_and_locals():
    r = run_code("def f(a):\n    b = a + 1\n    return b\ny = f(2)", trace=True)
    events = [(s.event, s.frame) for s in r.trace.steps]
    assert ("call", "f") in events and ("return", "f") in events
    ret = next(s for s in r.trace.steps if s.event == "return")
    assert ret.return_value == "3" and ret.locals == {"a": "2", "b": "3"}
