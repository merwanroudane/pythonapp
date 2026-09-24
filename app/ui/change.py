"""Change & Observe (blueprint §2.10): run a base example and a variant side by side."""

from __future__ import annotations

import streamlit as st

from app.curriculum.schema import ChangeObserve
from app.execution.client import run_code
from app.execution.models import RunResult


@st.cache_data(max_entries=256, show_spinner=False)
def _run(code: str, mode: str) -> RunResult:
    return run_code(code, mode=mode)


def _summary(result: RunResult) -> None:
    if result.exception:
        st.error(f"`{result.exception.type}: {result.exception.message}`", icon=":material/error:")
    if result.result:
        st.markdown(f"آخر expression: `{result.result['text']}`")
    st.code(result.stdout or "(لا يوجد stdout)", language="text")


def render_change(change: ChangeObserve, *, key: str) -> None:
    with st.container(key=f"card-insight-{key}", border=True):
        with st.container(key=f"cardtitle-{key}"):
            st.markdown(f":material/difference: غيّر وشاهد · Change & Observe — {change.title}")
        labels = [v.label for v in change.variants]
        picked = st.segmented_control(
            "اختر التغيير",
            labels,
            default=labels[0],
            key=f"variant-{key}",
            label_visibility="collapsed",
        )
        variant = next(v for v in change.variants if v.label == (picked or labels[0]))
        before, after = st.columns(2)
        with before:
            st.markdown(f"**{change.base_label}**")
            st.code(change.base, language="python")
            _summary(_run(change.base, change.mode))
        with after:
            st.markdown(f"**بعد · After:** {variant.label}")
            st.code(variant.code, language="python")
            _summary(_run(variant.code, change.mode))
        st.markdown(f":material/lightbulb: **لماذا تغيّر الناتج؟** {variant.explain}")
