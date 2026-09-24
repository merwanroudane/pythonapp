"""Cached access to the curriculum. Reloads automatically when a content file changes."""

from __future__ import annotations

import streamlit as st

from app.curriculum.loader import Curriculum, content_signature, load_curriculum


@st.cache_resource(max_entries=2, show_spinner=False)
def _load(signature: tuple) -> Curriculum:  # signature only drives cache invalidation
    return load_curriculum()


def get_curriculum() -> Curriculum:
    return _load(content_signature())
