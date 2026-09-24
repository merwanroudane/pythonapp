"""Property probe for the Type Lab (blueprint §117).

The learner's code is *parsed* here (ast.parse never executes anything) only to split
off its last expression; the code itself — and the probe — run inside the isolated
runner like every other execution. The probe prints one JSON line after a marker.
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass

from app.execution.client import run_code
from app.execution.models import RunResult

MARKER = "__PLL_PROBE__"
MAX_SOURCE_CHARS = 4000

# Runs inside the runner, standard library only.
PROBE_SOURCE = r"""
import collections.abc as _abc, json as _json, sys as _sys

_MUTATING = {
    "append", "extend", "insert", "remove", "pop", "clear", "sort", "reverse", "add",
    "discard", "update", "setdefault", "popitem", "appendleft", "popleft", "extendleft",
    "rotate", "difference_update", "intersection_update", "symmetric_difference_update",
}
_IMMUTABLE = (int, float, complex, bool, str, bytes, tuple, frozenset, range, type(None))
_BASIC = (int, float, complex, bool, str, type(None))


def _pll_probe(v):
    t = type(v)
    out = {"type": t.__name__, "module": t.__module__, "repr": repr(v)[:200]}
    out["basic"] = isinstance(v, _BASIC)
    try:
        hash(v)
        out["hashable"] = True
    except TypeError:
        out["hashable"] = False
    out["iterable"] = isinstance(v, _abc.Iterable)
    out["sized"] = isinstance(v, _abc.Sized)
    out["length"] = len(v) if out["sized"] else None
    seq = isinstance(v, _abc.Sequence)
    mapping = isinstance(v, _abc.Mapping)
    setlike = isinstance(v, _abc.Set)
    iterator = isinstance(v, _abc.Iterator)
    out["kind"] = ("sequence" if seq else "mapping" if mapping else "set" if setlike
                   else "iterator" if iterator else "scalar" if out["basic"] else "other")
    if isinstance(v, _IMMUTABLE):
        out["mutable"] = False
    elif isinstance(v, (_abc.MutableSequence, _abc.MutableSet, _abc.MutableMapping)):
        out["mutable"] = True
    else:
        out["mutable"] = None
    out["indexable"] = "position" if seq else "key" if mapping else None
    if seq or iterator:
        out["ordered"] = True
    elif mapping:
        out["ordered"] = "insertion"
    elif setlike:
        out["ordered"] = False
    else:
        out["ordered"] = None
    if isinstance(v, range):
        out["duplicates"] = False
    elif seq:
        out["duplicates"] = True
    elif setlike or mapping:
        out["duplicates"] = False
    else:
        out["duplicates"] = None
    out["lazy"] = isinstance(v, range) or iterator
    try:
        v < v
        out["orderable"] = True
    except TypeError:
        out["orderable"] = False
    try:
        out["truthy"] = bool(v)
    except Exception:
        out["truthy"] = None
    elem_types = None
    if (seq or setlike or mapping) and not isinstance(v, (str, bytes, bytearray)):
        items = list(v.values()) if mapping else list(v)
        if len(items) <= 1000:
            elem_types = sorted({type(x).__name__ for x in items})
    elif isinstance(v, str):
        elem_types = ["str"] if len(v) else []
    elif isinstance(v, (bytes, bytearray)):
        elem_types = ["int"] if len(v) else []
    out["element_types"] = elem_types
    methods = sorted(n for n in dir(t) if not n.startswith("_") and callable(getattr(t, n, None)))
    out["methods_mutating"] = [m for m in methods if m in _MUTATING]
    out["methods_other"] = [m for m in methods if m not in _MUTATING][:40]
    out["size_bytes"] = _sys.getsizeof(v)
    return out


print("__PLL_PROBE__" + _json.dumps(_pll_probe(__pll_value), ensure_ascii=False))
"""


@dataclass
class ProbeOutcome:
    properties: dict | None
    run: RunResult | None
    error: str | None = None  # a message for the learner (Arabic)


def build_program(source: str) -> str:
    """Split the learner's code into statements + the final expression to probe."""
    if len(source) > MAX_SOURCE_CHARS:
        raise ValueError("الكود أطول من المسموح في مختبر الأنواع.")
    tree = ast.parse(source)  # parsing only — nothing is executed here
    if not tree.body or not isinstance(tree.body[-1], ast.Expr):
        raise ValueError("اجعل آخر سطر **قيمة** (expression) مثل `[1, 2, 2]` أو اسم متغير.")
    last = tree.body[-1]
    lines = source.splitlines()
    prefix = "\n".join(lines[: last.lineno - 1])
    expr = ast.get_source_segment(source, last) or ast.unparse(last.value)
    return f"{prefix}\n__pll_value = (\n{expr}\n)\n{PROBE_SOURCE}"


def probe(source: str) -> ProbeOutcome:
    try:
        program = build_program(source)
    except SyntaxError as exc:
        return ProbeOutcome(None, None, f"خطأ صياغي في السطر {exc.lineno}: {exc.msg}")
    except ValueError as exc:
        return ProbeOutcome(None, None, str(exc))
    result = run_code(program)
    if result.exception or result.status != "ok":
        return ProbeOutcome(None, result)
    line = next((ln for ln in reversed(result.stdout.splitlines()) if ln.startswith(MARKER)), None)
    if line is None:
        return ProbeOutcome(None, result, "لم يُنتج الفحص نتيجة.")
    result.stdout = "\n".join(ln for ln in result.stdout.splitlines() if not ln.startswith(MARKER))
    return ProbeOutcome(json.loads(line[len(MARKER) :]), result)
