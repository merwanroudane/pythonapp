"""Type Lab (blueprint §117): type any value, see every property it has."""

from __future__ import annotations

import streamlit as st

from app.components.code_editor import code_editor, reset_editor
from app.execution.probe import probe
from app.storage import progress
from app.ui.bidi import ltr
from app.ui.output_panel import render_error

PRESETS = {
    "list": "[3, 1, 3]",
    "tuple": '(36.75, 3.06, "Algiers")',
    "set": "{3, 1, 3}",
    "dict": '{"Sara": 30, "Omar": 25}',
    "range": "range(0, 10, 2)",
    "str": '"مرحبا"',
    "int": "42",
    "float": "0.1 + 0.2",
    "complex": "3 + 4j",
    "bool": "True",
    "None": "None",
    "frozenset": "frozenset({1, 2})",
    "bytes": '"ب".encode("utf-8")',
    "deque": "from collections import deque\ndeque([1, 2, 3])",
    "generator": "(n * n for n in range(3))",
    "tuple+list": "([1, 2], 3)",
    "mixed": '[1, "2", 3.5, None, True, "missing"]',
}

KIND_LABELS = {
    "scalar": "نوع أساسي (قيمة مفردة)",
    "sequence": "بنية بيانات · Sequence",
    "set": "بنية بيانات · Set",
    "mapping": "بنية بيانات · Mapping",
    "iterator": "Iterator (يُنتج القيم عند الطلب)",
    "other": "object آخر",
}


def _mark(value) -> str:
    if value is True:
        return "✓ نعم"
    if value is False:
        return "✗ لا"
    if value is None:
        return "— لا ينطبق"
    return str(value)


def property_rows(p: dict) -> list[tuple[str, str, str]]:
    """(property, result, explanation) rows for a probe result."""
    rows = []
    mutable_note = {
        True: "يمكن تغييره في مكانه (append / add / تعديل مفتاح)؛ كل alias يرى التغيير.",
        False: "لا يتغير بعد إنشائه؛ أي «تعديل» يُنشئ object جديدًا.",
        None: "لا تحدده الأنواع المدمجة؛ حالة الـiterator تتغير كلما استُهلك.",
    }
    rows.append(("قابلية التعديل · `mutable`", _mark(p["mutable"]), mutable_note[p["mutable"]]))
    ordered = p["ordered"]
    if ordered == "insertion":
        rows.append(
            (
                "مرتّبة · `ordered`",
                "✓ ترتيب الإدخال",
                "يحفظ ترتيب إضافة المفاتيح (منذ Python 3.7)، لكن لا وصول بالموضع.",
            )
        )
    else:
        rows.append(
            (
                "مرتّبة · `ordered`",
                _mark(ordered),
                {
                    True: "للعناصر مواضع ثابتة: الأول والثاني…",
                    False: "لا ترتيب مضمون؛ لا يوجد عنصر «أول».",
                    None: "قيمة مفردة، لا عناصر لترتيبها.",
                }[ordered],
            )
        )
    rows.append(
        (
            "تسمح بالتكرار · `duplicates`",
            _mark(p["duplicates"]),
            {
                True: "القيمة نفسها يمكن أن تظهر أكثر من مرة.",
                False: "كل عنصر (أو مفتاح) يظهر مرة واحدة فقط."
                + (" (في range بحكم طريقة البناء)" if p["type"] == "range" else ""),
                None: "لا ينطبق.",
            }[p["duplicates"]],
        )
    )
    access = {"position": "✓ بالموضع `x[0]`", "key": "✓ بالمفتاح `d[key]`", None: "✗ لا"}
    rows.append(
        (
            "الوصول بالأقواس `x[…]` · `subscriptable`",
            access[p["indexable"]],
            {
                "position": "يمكن الوصول بالـindex والـslicing.",
                "key": "الوصول بالمفتاح لا بالموضع.",
                None: "لا يمكن كتابة `x[0]`.",
            }[p["indexable"]],
        )
    )
    rows.append(
        (
            "قابلة للتجزئة · `hashable`",
            _mark(p["hashable"]),
            "تصلح مفتاحًا في dict وعنصرًا في set."
            if p["hashable"]
            else "لا تصلح مفتاحًا في dict ولا عنصرًا في set (قيمتها قد تتغير).",
        )
    )
    rows.append(
        (
            "قابلة للمرور · `iterable`",
            _mark(p["iterable"]),
            "يمكن المرور عليها بـ`for`." if p["iterable"] else "لا يمكن المرور عليها بـ`for`.",
        )
    )
    rows.append(
        (
            "لها طول · `sized`",
            _mark(p["sized"]) + (f" (`len = {p['length']}`)" if p["sized"] else ""),
            "تعمل معها `len()`." if p["sized"] else "`len()` ترفع `TypeError`.",
        )
    )
    rows.append(
        (
            "كسولة · `lazy`",
            _mark(p["lazy"]),
            "تحسب العناصر عند الطلب ولا تخزّنها كلها."
            if p["lazy"]
            else "كل عناصرها مخزّنة في الذاكرة الآن.",
        )
    )
    orderable_note = "تدعم < و> (ترتيب طبيعي)."
    if p["kind"] == "set":
        orderable_note = "انتبه: < بين مجموعتين تعني «مجموعة جزئية» لا «أصغر»."
    elif not p["orderable"]:
        orderable_note = "لا يوجد ترتيب طبيعي: < ترفع TypeError."
    rows.append(("قابلة للمقارنة بالترتيب · `orderable`", _mark(p["orderable"]), orderable_note))
    rows.append(
        (
            "قيمتها المنطقية · `truthiness`",
            _mark(p["truthy"]),
            "`bool(x)` = `True`" if p["truthy"] else "`bool(x)` = `False`: قيمة «فارغة» أو صفرية.",
        )
    )
    types = p.get("element_types")
    if types is not None:
        mixed = len(types) > 1
        rows.append(
            (
                "أنواع العناصر",
                ", ".join(f"`{t}`" for t in types) or "(فارغة)",
                "مختلطة (heterogeneous): عناصر من أنواع مختلفة."
                if mixed
                else "متجانسة (homogeneous): عناصر من نوع واحد.",
            )
        )
    return rows


def render_property_lab(*, key: str, lesson_id: str | None = None, initial: str = "[3, 1, 3]"):
    editor_key, result_key = f"code-{key}", f"lab-{key}"

    def load_preset() -> None:
        choice = st.session_state.get(f"preset-{key}")
        if choice:
            reset_editor(editor_key, PRESETS[choice])
            st.session_state.pop(result_key, None)

    with st.container(key=f"card-data-{key}", border=True):
        with st.container(key=f"cardtitle-{key}"):
            st.markdown(":material/biotech: مختبر الأنواع والخصائص · Type Lab")
        st.caption("اكتب أي قيمة (أو عدة أسطر آخرها قيمة)، أو اختر مثالًا، ثم افحص خصائصها.")
        st.pills(
            "أمثلة",
            list(PRESETS),
            key=f"preset-{key}",
            on_change=load_preset,
            label_visibility="collapsed",
        )
        with st.container(key=f"cell-{key}"):
            editor = code_editor(initial, key=editor_key, min_lines=2, max_lines=10)
        clicked = st.button(
            "افحص الخصائص", icon=":material/search:", type="primary", key=f"probe-{key}"
        )
        if clicked or editor.run_requested:
            with st.spinner("يُفحص داخل المشغّل المعزول…"):
                st.session_state[result_key] = probe(editor.code)
            if lesson_id:
                progress.mark_ran(lesson_id)

        outcome = st.session_state.get(result_key)
        if outcome is None:
            return
        if outcome.error:
            st.warning(outcome.error, icon=":material/info:")
            return
        if outcome.properties is None:
            if outcome.run and outcome.run.exception:
                render_error(outcome.run, f"laberr-{key}")
            elif outcome.run:
                st.warning(outcome.run.runner_message or "تعذّر الفحص.", icon=":material/error:")
            return

        p = outcome.properties
        with st.container(horizontal=True, gap="small"):
            st.badge(ltr(p["type"]), icon=":material/category:", color="violet")
            st.badge(
                KIND_LABELS[p["kind"]],
                icon=":material/label:",
                color="orange" if p["basic"] else "blue",
            )
            st.badge(ltr(f"{p['size_bytes']} bytes"), icon=":material/memory:", color="gray")
        st.code(p["repr"], language="python")
        table = "| الخاصية | النتيجة | المعنى |\n|---|---|---|\n" + "\n".join(
            f"| {name} | {value} | {note} |" for name, value, note in property_rows(p)
        )
        st.markdown(table)
        if p["methods_mutating"] or p["methods_other"]:
            with st.expander(":material/build: الـmethods المتاحة"):
                if p["methods_mutating"]:
                    st.markdown(
                        "**تعدّل الـobject في مكانه:** "
                        + " ".join(f"`{m}()`" for m in p["methods_mutating"])
                    )
                if p["methods_other"]:
                    st.markdown(
                        "**لا تعدّله (تُعيد نتيجة):** "
                        + " ".join(f"`{m}()`" for m in p["methods_other"])
                    )
        if outcome.run and outcome.run.stdout.strip():
            st.caption("stdout")
            st.code(outcome.run.stdout, language="text")
