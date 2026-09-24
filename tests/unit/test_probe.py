"""Type Lab probe (blueprint §117): the property matrix must match Python's real behaviour."""

import pytest

from app.execution.probe import build_program, probe
from app.ui.property_lab import PRESETS, property_rows

# (source, expected subset of properties) — mirrors the table in the properties lesson.
MATRIX = [
    ("42", dict(basic=True, mutable=False, hashable=True, iterable=False, orderable=True)),
    ("3 + 4j", dict(basic=True, mutable=False, hashable=True, orderable=False)),
    ("None", dict(basic=True, hashable=True, orderable=False, truthy=False)),
    ('"ab"', dict(basic=True, mutable=False, ordered=True, duplicates=True, hashable=True)),
    ("[3, 1, 3]", dict(mutable=True, ordered=True, duplicates=True, hashable=False)),
    ("(3, 1, 3)", dict(mutable=False, ordered=True, duplicates=True, hashable=True)),
    ("([1], 2)", dict(mutable=False, hashable=False)),
    ("range(5)", dict(mutable=False, duplicates=False, hashable=True, lazy=True, orderable=False)),
    ("{3, 1}", dict(mutable=True, ordered=False, duplicates=False, hashable=False)),
    ("frozenset({1})", dict(mutable=False, ordered=False, hashable=True)),
    ('{"a": 1}', dict(mutable=True, ordered="insertion", indexable="key", hashable=False)),
    ('b"ab"', dict(mutable=False, hashable=True, indexable="position")),
    ('bytearray(b"ab")', dict(mutable=True, hashable=False)),
    ("from collections import deque\ndeque([1])", dict(mutable=True, ordered=True)),
    ("(n for n in range(3))", dict(lazy=True, sized=False, indexable=None)),
]


@pytest.mark.parametrize(("source", "expected"), MATRIX)
def test_probe_matches_the_property_table(source, expected):
    outcome = probe(source)
    assert outcome.error is None and outcome.properties is not None
    for prop, value in expected.items():
        assert outcome.properties[prop] == value, f"{source}: {prop}"


def test_element_types_detect_mixed_collections():
    props = probe('[1, "2", 3.5, None, True]').properties
    assert props["element_types"] == ["NoneType", "bool", "float", "int", "str"]


def test_multi_line_input_probes_the_last_expression_and_keeps_stdout():
    outcome = probe('print("hi")\nxs = [1, 2]\nxs')
    assert outcome.properties["type"] == "list"
    assert outcome.run.stdout.strip() == "hi"  # probe marker line is stripped


def test_invalid_input_gives_a_learner_message_without_running():
    assert "قيمة" in probe("x = 1").error
    assert "صياغي" in probe("[1,").error
    with pytest.raises(ValueError):
        build_program("x" * 5000)


def test_parsing_does_not_execute_code_in_the_app_process(tmp_path, monkeypatch):
    marker = tmp_path / "ran.txt"
    source = f"open({str(marker)!r}, 'w').write('x')\n1"
    build_program(source)  # parse + rewrite only
    assert not marker.exists()


def test_runtime_errors_are_reported_as_run_results():
    outcome = probe("1 / 0")
    assert outcome.properties is None and outcome.run.exception.type == "ZeroDivisionError"


def test_every_preset_probes_cleanly_and_renders_rows():
    for name, source in PRESETS.items():
        outcome = probe(source)
        assert outcome.properties is not None, name
        rows = property_rows(outcome.properties)
        assert len(rows) >= 10, name
        assert all(isinstance(cell, str) and cell for row in rows for cell in row), name
