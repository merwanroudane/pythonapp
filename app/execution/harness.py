"""Child-process harness for the development code runner.

Runs in a separate interpreter (``python -I``), never inside the Streamlit process. It
reads one job as JSON from ``argv[1]``, executes the learner's code, and writes a
structured result (blueprint §85) to ``argv[2]``. It deliberately imports only the
standard library so it works in any interpreter the runner is pointed at.
"""

from __future__ import annotations

import ast
import base64
import builtins
import io
import json
import linecache
import reprlib
import sys
import time
import traceback
import warnings
from contextlib import redirect_stderr, redirect_stdout

FILENAME = "<lesson>"
MAX_STREAM_CHARS = 20_000
MAX_TRACE_STEPS = 300
MAX_VARIABLES = 40
MAX_FRAMES = 12
PREVIEW_LINES = 16
PREVIEW_WIDTH = 110
PREVIEW_MAX_ITEMS = 200

MUTABLE_TYPES = (list, dict, set, bytearray)
IMMUTABLE_TYPES = (int, float, complex, bool, str, bytes, tuple, frozenset, range, type(None))
SIZED_BUILTINS = (str, bytes, bytearray, list, tuple, dict, set, frozenset, range)

_repr = reprlib.Repr()
_repr.maxstring = 80
_repr.maxother = 80
_repr.maxlist = 8
_repr.maxtuple = 8
_repr.maxdict = 6
_repr.maxset = 8
_repr.maxlevel = 3


class InputExhausted(EOFError):
    """Raised when code calls input() more times than inputs were provided."""


class _CappedIO(io.StringIO):
    """StringIO that stops growing after MAX_STREAM_CHARS (endless print loops)."""

    truncated = False

    def write(self, s: str) -> int:
        room = MAX_STREAM_CHARS - self.tell()
        if room <= 0:
            self.truncated = True
            return len(s)
        if len(s) > room:
            self.truncated = True
            super().write(s[:room])
            return len(s)
        return super().write(s)


def safe_repr(obj: object) -> str:
    try:
        return _repr.repr(obj)
    except Exception as exc:  # a user __repr__ can raise anything
        return f"<repr failed: {type(exc).__name__}>"


def describe(name: str, obj: object) -> dict:
    """Describe a value without calling arbitrary user properties (blueprint §87.4)."""
    tp = type(obj)
    info: dict = {
        "name": name,
        "type": tp.__name__,
        "module": tp.__module__,
        "repr": safe_repr(obj),
        "id": id(obj),
    }
    if isinstance(obj, MUTABLE_TYPES):
        info["mutable"] = True
    elif isinstance(obj, IMMUTABLE_TYPES):
        info["mutable"] = False
    if isinstance(obj, SIZED_BUILTINS):
        info["length"] = len(obj)
    if tp.__module__.startswith(("numpy", "pandas")):
        shape = getattr(obj, "shape", None)
        if isinstance(shape, tuple):
            info["shape"] = list(shape)
        dtype = getattr(obj, "dtype", None)
        if dtype is not None:
            info["dtype"] = str(dtype)
    return info


def user_names(namespace: dict) -> dict:
    hidden = {"__builtins__", "__name__", "__doc__", "__file__", "__loader__", "__spec__"}
    out = {}
    for name, value in namespace.items():
        if name in hidden or name.startswith("__"):
            continue
        if type(value).__name__ == "module":
            continue
        out[name] = value
    return out


def snapshot(namespace: dict) -> dict[str, str]:
    return {name: safe_repr(value) for name, value in user_names(namespace).items()}


def preview_repr(obj: object, short: str) -> str | None:
    """A bounded multi-line repr for values the one-line snapshot cuts off (DataFrames,
    arrays, nested lists...). None when the short repr already says everything."""
    if isinstance(obj, SIZED_BUILTINS) and len(obj) > PREVIEW_MAX_ITEMS:
        return None  # keep tracing big containers cheap; the short repr summarises them
    try:
        text = repr(obj)
    except Exception:
        return None
    if text == short:
        return None
    lines = text.splitlines() or [""]
    if len(lines) > PREVIEW_LINES:
        lines = [*lines[:PREVIEW_LINES], "…"]
    lines = [ln if len(ln) <= PREVIEW_WIDTH else ln[: PREVIEW_WIDTH - 1] + "…" for ln in lines]
    return "\n".join(lines)


def format_exception(exc: BaseException) -> dict:
    tbe = traceback.TracebackException.from_exception(exc, capture_locals=False)
    frames = [
        {"filename": f.filename, "lineno": f.lineno, "name": f.name, "line": f.line}
        for f in tbe.stack
        if f.filename == FILENAME
    ]
    lines = list(tbe.format())
    # Hide the harness's own frames so the traceback matches what the learner wrote.
    text = "".join(line for line in lines if "harness.py" not in line)
    info = {
        "type": type(exc).__name__,
        "message": str(exc),
        "frames": frames,
        "traceback": text,
        "lineno": frames[-1]["lineno"] if frames else None,
    }
    if isinstance(exc, SyntaxError):
        info["lineno"] = exc.lineno
        info["offset"] = exc.offset
        info["text"] = exc.text
    if isinstance(exc, NameError):
        info["missing_name"] = getattr(exc, "name", None)
    return info


def collect_figures() -> list[dict]:
    plt = sys.modules.get("matplotlib.pyplot")
    if plt is None:
        return []
    figures = []
    for num in plt.get_fignums()[:6]:
        buf = io.BytesIO()
        plt.figure(num).savefig(buf, format="png", dpi=110, bbox_inches="tight")
        figures.append({"format": "png", "base64": base64.b64encode(buf.getvalue()).decode()})
    plt.close("all")
    return figures


class Tracer:
    """Line-level trace used to build step-by-step animations (blueprint §90)."""

    def __init__(self, stdout: io.StringIO, module_ns: dict) -> None:
        self.stdout = stdout
        self.module_ns = module_ns
        self.steps: list[dict] = []
        self.stack: list[str] = []
        self.truncated = False
        self._last_previews: dict[str, str | None] = {}

    def _record(self, frame, event: str, extra: dict | None = None) -> None:
        if len(self.steps) >= MAX_TRACE_STEPS:
            self.truncated = True
            sys.settrace(None)
            return
        is_module = frame.f_code.co_name == "<module>"
        local_vars = snapshot(frame.f_locals) if not is_module else {}
        # Every active user-code function frame, outermost first (call-stack view, §8.12).
        frames = []
        walker = frame
        while walker is not None and walker.f_code.co_filename == FILENAME:
            if walker.f_code.co_name != "<module>":
                frames.append({"name": walker.f_code.co_name, "locals": snapshot(walker.f_locals)})
            walker = walker.f_back
        frames = frames[:MAX_FRAMES][::-1]
        global_vars = snapshot(self.module_ns)
        step = {
            "line": frame.f_lineno,
            "event": event,
            "frame": frame.f_code.co_name,
            "stack": list(self.stack),
            "globals": global_vars,
            "locals": local_vars,
            "frames": frames,
            "stdout": self.stdout.getvalue(),
            "previews": self._changed_previews(frame, is_module, {**global_vars, **local_vars}),
        }
        if extra:
            step.update(extra)
        self.steps.append(step)

    def _changed_previews(self, frame, is_module: bool, shorts: dict[str, str]) -> dict[str, str]:
        """Full-looking reprs of the visible values that changed since the previous step.
        Compared on the full text, so an in-place change hidden by the short repr (a new
        DataFrame column) still shows up."""
        visible = user_names(self.module_ns)
        if not is_module:
            visible.update(user_names(frame.f_locals))
        current = {name: preview_repr(visible[name], short) for name, short in shorts.items()}
        changed = {
            name: text
            for name, text in current.items()
            if text is not None and self._last_previews.get(name) != text
        }
        self._last_previews = current
        return changed

    def __call__(self, frame, event, arg):
        if frame.f_code.co_filename != FILENAME:
            return None
        if event == "call":
            name = frame.f_code.co_name
            if name != "<module>":
                self.stack.append(name)
                self._record(frame, "call")
            return self._local
        return None

    def _local(self, frame, event, arg):
        if event == "line":
            self._record(frame, "line")
        elif event == "return" and frame.f_code.co_name != "<module>":
            self._record(frame, "return", {"return_value": safe_repr(arg)})
            if self.stack:
                self.stack.pop()
        return self._local


def run(job: dict) -> dict:
    code: str = job["code"]
    mode: str = job.get("mode", "script")
    trace_enabled: bool = bool(job.get("trace"))
    pending_inputs = list(job.get("inputs", []))

    stdout = _CappedIO()
    stderr = _CappedIO()
    namespace: dict = {"__name__": "__main__"}
    result: dict = {
        "status": "ok",
        "stdout": "",
        "stderr": "",
        "result": None,
        "warnings": [],
        "exception": None,
        "variables": [],
        "figures": [],
        "trace": None,
        "timing_ms": 0.0,
        "inputs_used": [],
    }

    def fake_input(prompt: object = "") -> str:
        stdout.write(str(prompt))
        if not pending_inputs:
            raise InputExhausted(
                "input() was called but no more inputs were provided in the Inputs box"
            )
        value = str(pending_inputs.pop(0))
        stdout.write(value + "\n")
        result["inputs_used"].append(value)
        return value

    builtins.input = fake_input
    linecache.cache[FILENAME] = (len(code), None, code.splitlines(True), FILENAME)

    tracer = Tracer(stdout, namespace) if trace_enabled else None
    start = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            tree = ast.parse(code, filename=FILENAME)
            last_expr = None
            if mode == "notebook" and tree.body and isinstance(tree.body[-1], ast.Expr):
                last_expr = ast.Expression(tree.body.pop().value)
            body = compile(tree, FILENAME, "exec")
            with redirect_stdout(stdout), redirect_stderr(stderr):
                if tracer:
                    sys.settrace(tracer)
                try:
                    exec(body, namespace)
                    if last_expr is not None:
                        value = eval(compile(last_expr, FILENAME, "eval"), namespace)
                        if value is not None:
                            result["result"] = {
                                "kind": "python_repr",
                                "text": safe_repr(value),
                                "type": type(value).__name__,
                            }
                finally:
                    sys.settrace(None)
        except BaseException as exc:  # includes SystemExit / KeyboardInterrupt from user code
            result["status"] = "error"
            result["exception"] = format_exception(exc)
    result["timing_ms"] = round((time.perf_counter() - start) * 1000, 2)

    # Like Python's default filters: deprecations raised inside libraries (e.g. matplotlib
    # calling old pyparsing names) are noise for the learner; keep them only for user code.
    shown = [
        w
        for w in caught
        if w.filename == FILENAME
        or not issubclass(w.category, (DeprecationWarning, PendingDeprecationWarning))
    ]
    result["warnings"] = [
        {
            "category": w.category.__name__,
            "message": str(w.message),
            "lineno": w.lineno if w.filename == FILENAME else None,
        }
        for w in shown[:20]
    ]
    result["stdout"] = stdout.getvalue()
    result["stderr"] = stderr.getvalue()
    result["stdout_truncated"] = stdout.truncated
    names = user_names(namespace)
    result["variables"] = [describe(n, v) for n, v in list(names.items())[:MAX_VARIABLES]]
    try:
        result["figures"] = collect_figures()
    except Exception:
        result["figures"] = []
    if tracer:
        result["trace"] = {"steps": tracer.steps, "truncated": tracer.truncated}
    try:  # POSIX only: peak resident memory of this run's process
        import resource

        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        per_mb = 1024 * 1024 if sys.platform == "darwin" else 1024  # macOS reports bytes
        result["memory_peak_mb"] = round(peak / per_mb, 1)
    except ImportError:
        pass
    return result


def main() -> None:
    """Two transports:

    * ``harness.py JOB.json RESULT.json`` — local backend, files outside the sandbox cwd.
    * ``harness.py -`` — Docker/remote: job on stdin, result on stdout after job["boundary"].
    """
    real_stdout = sys.stdout
    if sys.argv[1] == "-":
        job = json.load(sys.stdin)
        result = run(job)
        real_stdout.write("\n" + job["boundary"] + "\n")
        real_stdout.write(json.dumps(result, ensure_ascii=False, default=str))
        real_stdout.flush()
        return
    job_path, result_path = sys.argv[1], sys.argv[2]
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    result = run(job)
    with open(result_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, default=str)


if __name__ == "__main__":
    main()
