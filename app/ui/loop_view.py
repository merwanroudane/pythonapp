"""For-loop progress for the step-through view (blueprint §8.4).

Given the source and the trace, work out — for a step inside a ``for`` loop — which
element of the iterable is current. Only the AST and ``ast.literal_eval`` of value
*reprs* are used; learner code is never evaluated here.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class LoopState:
    header_line: int
    target: str
    items: list[str]  # repr of each element
    index: int  # current element; == len(items) means "exhausted"
    at_header: bool  # the header is fetching the next item right now


@dataclass(frozen=True)
class _Loop:
    header: int
    end: int
    target: str
    iter_node: ast.expr


def _loops(code: str) -> list[_Loop]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            found.append(
                _Loop(
                    node.lineno, node.end_lineno or node.lineno, ast.unparse(node.target), node.iter
                )
            )
    return found


def _literal(text: str):
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
        return None


def _range_items(call: ast.Call, names: dict[str, str]) -> list | None:
    args = []
    for arg in call.args:
        value = (
            _literal(ast.unparse(arg))
            if not isinstance(arg, ast.Name)
            else _literal(names.get(arg.id, ""))
        )
        if not isinstance(value, int):
            return None
        args.append(value)
    if not 1 <= len(args) <= 3:
        return None
    values = range(*args)
    return list(values) if len(values) <= 50 else None


def _items(node: ast.expr, names: dict[str, str]) -> list | None:
    """Elements of the iterable, when they can be known without running code."""
    if isinstance(node, ast.Name):
        value = _literal(names.get(node.id, ""))
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id == "range":
            return _range_items(node, names)
        if node.func.id == "enumerate" and node.args:
            inner = _items(node.args[0], names)
            start = 0
            for kw in node.keywords:
                if kw.arg == "start" and isinstance(_literal(ast.unparse(kw.value)), int):
                    start = _literal(ast.unparse(kw.value))
            return None if inner is None else list(enumerate(inner, start))
        return None
    elif isinstance(node, ast.Attribute) and node.attr in ("items", "keys", "values"):
        return None
    else:
        value = _literal(ast.unparse(node))
    if isinstance(value, (list, tuple, str)) and len(value) <= 50:
        return list(value)
    if isinstance(value, dict) and len(value) <= 50:
        return list(value)
    return None


def loop_state(code: str, steps: list, index: int) -> LoopState | None:
    """steps: objects with ``line``, ``frame``, ``globals``, ``locals`` attributes."""
    step = steps[index]
    if step.line is None:
        return None
    containing = [lp for lp in _loops(code) if lp.header <= step.line <= lp.end]
    if not containing:
        return None
    loop = max(containing, key=lambda lp: lp.header)  # innermost
    hits = 0
    for j in range(index, -1, -1):
        other = steps[j]
        if other.line is None or other.frame != step.frame:
            continue
        if not loop.header <= other.line <= loop.end:
            break  # reached the statement before this loop activation
        if other.line == loop.header:
            hits += 1
    names = {**step.globals, **step.locals}
    items = _items(loop.iter_node, names)
    if items is None or hits == 0:
        return None
    at_header = step.line == loop.header
    current = hits - 1
    return LoopState(
        loop.header, loop.target, [repr(v) for v in items], min(current, len(items)), at_header
    )
