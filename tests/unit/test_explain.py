from app.execution.client import run_code
from app.execution.explain import explain


def test_name_error_suggests_the_close_builtin():
    r = run_code("pritn('hi')")
    info = explain(r.exception, [v.name for v in r.variables])
    assert "print" in info.hint and "pritn" in info.hint


def test_name_error_suggests_user_variable():
    r = run_code("total_price = 3\nprint(total_prise)")
    info = explain(r.exception, [v.name for v in r.variables])
    assert "total_price" in info.hint


def test_none_type_error_points_to_missing_return():
    r = run_code("def f():\n    print(1)\nf() + 1")
    assert "return" in explain(r.exception).hint


def test_unknown_exception_gets_generic_explanation():
    r = run_code("raise LookupError('x')")
    info = explain(r.exception)
    assert "LookupError" in info.what
