"""Code editor component (blueprint §6): CodeMirror 6 through Streamlit CCv2.

Falls back to ``st.text_area`` when the JS bundle is missing or when
``PLL_EDITOR=textarea`` (used by the headless AppTest suite, which cannot render
custom components). Rebuild the bundle with ``npm install && npm run build`` in
``frontend/``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

BUNDLE = Path(__file__).with_name("editor.bundle.js")

_CSS = """
:host { display: block; }
.pll-editor { direction: ltr; text-align: left; }
"""


@dataclass(frozen=True)
class EditorValue:
    code: str
    run_requested: bool  # Ctrl/Cmd+Enter or Shift+Enter inside the editor


def _use_codemirror() -> bool:
    return os.environ.get("PLL_EDITOR", "codemirror") != "textarea" and BUNDLE.exists()


@st.cache_resource(show_spinner=False)
def _component():
    return st.components.v2.component(
        "pll_code_editor",
        html='<div class="pll-editor" dir="ltr"></div>',
        css=_CSS,
        js=BUNDLE.read_text(encoding="utf-8"),
    )


def _nonce_key(key: str) -> str:
    return f"{key}__nonce"


def reset_editor(key: str, code: str) -> None:
    """Replace the editor's document. Call from a callback, before the editor mounts."""
    st.session_state[_nonce_key(key)] = st.session_state.get(_nonce_key(key), 0) + 1
    if _use_codemirror():
        st.session_state.setdefault(key, {})
        st.session_state[key]["code"] = code
    else:
        st.session_state[key] = code


def code_editor(
    initial: str,
    *,
    key: str,
    min_lines: int = 4,
    max_lines: int = 22,
    read_only: bool = False,
    label: str = "الكود",
) -> EditorValue:
    if not _use_codemirror():
        st.session_state.setdefault(key, initial)
        height = min(420, max(110, 26 * (min_lines + 1)))
        code = st.text_area(
            label, key=key, height=height, label_visibility="collapsed", disabled=read_only
        )
        return EditorValue(code=code or "", run_requested=False)

    state = st.session_state.get(key) or {}
    code = state.get("code", initial) if isinstance(state, dict) else initial
    result = _component()(
        key=key,
        data={
            "code": code,
            "nonce": st.session_state.get(_nonce_key(key), 0),
            "readOnly": read_only,
            "minLines": min_lines,
            "maxLines": max_lines,
        },
        default={"code": initial},
        on_code_change=lambda: None,
        on_run_change=lambda: None,
    )
    run_payload = result.run
    if isinstance(run_payload, str):
        return EditorValue(code=run_payload, run_requested=True)
    return EditorValue(code=result.code if result.code is not None else code, run_requested=False)
