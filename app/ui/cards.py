"""Visual note blocks (blueprint §2.7): one consistent card per knowledge type."""

from __future__ import annotations

import streamlit as st

from app.curriculum.blocks import CARDS


def render_card(block_type: str, body: str, key: str, title: str | None = None) -> None:
    style = CARDS[block_type]
    label = f"{style.label} — {title}" if title else style.label
    if style.collapsible:
        # Deep layers stay folded so beginners can finish without them (§2.2).
        with st.container(key=f"card-{style.tone}-{key}", border=True):
            with st.expander(f"{style.icon} {label}"):
                st.markdown(body)
        return
    with st.container(key=f"card-{style.tone}-{key}", border=True):
        with st.container(key=f"cardtitle-{key}"):
            st.markdown(f"{style.icon} {label}")
        st.markdown(body)


def render_compare(body: str, key: str, title: str | None = None) -> None:
    """Two-sided A vs B card. Sides are separated by a line containing only ``|||``."""
    sides = [part.strip() for part in body.split("\n|||\n")]
    with st.container(key=f"card-data-{key}", border=True):
        with st.container(key=f"cardtitle-{key}"):
            st.markdown(
                f":material/compare_arrows: مقارنة · Compare{' — ' + title if title else ''}"
            )
        cols = st.columns(len(sides))
        for col, side in zip(cols, sides, strict=True):
            with col:
                st.markdown(side)
