"""Output Inspector (blueprint §5.1, §5.2, §87): every stream in its own tab."""

from __future__ import annotations

import base64

import streamlit as st

from app.execution.explain import explain
from app.execution.models import RunResult
from app.ui.bidi import ltr

_MUTABILITY = {True: "mutable", False: "immutable", None: "—"}


def _status_row(result: RunResult) -> None:
    with st.container(horizontal=True, gap="small"):
        if result.status == "ok":
            st.badge("نجح التنفيذ · OK", icon=":material/check_circle:", color="green")
        elif result.status == "error" and result.exception:
            st.badge(result.exception.type, icon=":material/error:", color="red")
        elif result.status == "timeout":
            st.badge("انتهت المهلة · Timeout", icon=":material/timer_off:", color="orange")
        else:
            st.badge("خطأ في المشغّل · Runner", icon=":material/build:", color="gray")
        if result.warnings:
            st.badge(
                ltr(f"{len(result.warnings)} Warning"), icon=":material/warning:", color="yellow"
            )
        st.badge(ltr(f"{result.timing_ms:.1f} ms"), icon=":material/speed:", color="gray")
        if result.memory_peak_mb:
            st.badge(ltr(f"{result.memory_peak_mb:.0f} MB"), icon=":material/memory:", color="gray")
        sandboxed = result.backend.startswith(("docker", "remote"))
        st.badge(
            ltr(result.backend),
            icon=":material/shield:" if sandboxed else ":material/computer:",
            color="blue" if sandboxed else "gray",
            help="الـbackend الذي نفّذ الكود (PLL_EXECUTOR)",
        )


def variables_table(result: RunResult) -> list[dict]:
    aliases = result.alias_groups()
    rows = []
    for var in result.variables:
        others = [n for n in aliases.get(var.id, []) if n != var.name]
        size = ""
        if var.shape is not None:
            size = str(tuple(var.shape))
        elif var.length is not None:
            size = str(var.length)
        rows.append(
            {
                "Name": var.name,
                "Type": var.type,
                "Value": var.repr,
                "Len / Shape": size,
                "dtype": var.dtype or "",
                "Mutability": _MUTABILITY[var.mutable],
                "Same object as": ", ".join(others),
            }
        )
    return rows


def render_error(result: RunResult, key: str) -> None:
    exc = result.exception
    if exc is None:
        return
    known = [v.name for v in result.variables]
    info = explain(exc, known)
    with st.container(key=f"card-error-{key}", border=True):
        with st.container(key=f"cardtitle-{key}"):
            where = f" · السطر {exc.lineno}" if exc.lineno else ""
            st.markdown(f":material/bug_report: {exc.type}{where} — {info.category}")
        st.markdown(f"**ماذا حدث؟** {info.what}")
        st.markdown(f"**أين تنظر؟** {info.hint}")
        st.code(exc.traceback.strip() or f"{exc.type}: {exc.message}", language="text")


def render_output(result: RunResult, *, notebook_mode: bool, key: str) -> None:
    _status_row(result)
    if result.status in ("timeout", "runner_error"):
        st.warning(result.runner_message or "Runner failed.", icon=":material/timer_off:")
        return
    if result.exception:
        render_error(result, key)

    labels = ["stdout"]
    if notebook_mode:
        labels.insert(0, "Result")
    labels.append(f"Variables ({len(result.variables)})")
    if result.warnings:
        labels.append(f"Warnings ({len(result.warnings)})")
    if result.stderr:
        labels.append("stderr")
    if result.figures:
        labels.append(f"Figures ({len(result.figures)})")
    tabs = dict(zip(labels, st.tabs(labels), strict=True))

    for label, tab in tabs.items():
        with tab:
            if label == "Result":
                if result.result:
                    st.code(result.result["text"], language="python")
                    st.caption(
                        f"قيمة آخر expression من نوع `{result.result['type']}` — تُعرض تلقائيًا "
                        "في Notebook mode فقط."
                    )
                else:
                    st.caption("آخر سطر ليس expression له قيمة، فلا شيء يُعرض تلقائيًا.")
            elif label == "stdout":
                if result.stdout:
                    st.code(result.stdout, language="text")
                    if result.stdout_truncated:
                        st.caption("قُصّ الناتج لأنه تجاوز الحد المسموح.")
                else:
                    st.caption("لم يُطبع شيء إلى stdout. هل استخدمت `print()`؟")
            elif label.startswith("Variables"):
                rows = variables_table(result)
                if rows:
                    st.dataframe(rows, hide_index=True)
                    if result.alias_groups():
                        st.caption("الأسماء في عمود *Same object as* مرتبطة بنفس الـobject.")
                else:
                    st.caption("لا توجد متغيرات جديدة.")
            elif label.startswith("Warnings"):
                for warning in result.warnings:
                    where = f" (line {warning.lineno})" if warning.lineno else ""
                    st.warning(f"**{warning.category}**{where}: {warning.message}")
            elif label == "stderr":
                st.code(result.stderr, language="text")
            elif label.startswith("Figures"):
                for fig in result.figures:
                    st.image(base64.b64decode(fig["base64"]))
