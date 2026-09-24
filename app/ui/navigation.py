"""Navigation shell (blueprint §3.4, §79.1): one st.Page per lesson, grouped by track."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from app.config import ROOT
from app.curriculum.registry import get_curriculum
from app.storage import progress


def page_for(key: str) -> st.Page | None:
    """Page object for a lesson id, "home" or "playground" (for st.page_link)."""
    return st.session_state.get("_pages", {}).get(key)


def _lesson_page(lesson_id: str, render: Callable[[str], None]) -> Callable[[], None]:
    def page() -> None:
        render(lesson_id)

    page.__name__ = f"lesson_{lesson_id.replace('-', '_')}"
    return page


def build_navigation(render_lesson: Callable[[str], None]) -> dict[str, list[st.Page]]:
    curriculum = get_curriculum()
    pages_by_key: dict[str, st.Page] = {}
    pages_by_key["home"] = st.Page(
        ROOT / "app_pages" / "home.py", title="الرئيسية", icon=":material/home:", default=True
    )
    pages_by_key["playground"] = st.Page(
        ROOT / "app_pages" / "playground.py",
        title="ساحة التجريب",
        icon=":material/code:",
        url_path="playground",
    )
    pages_by_key["type_lab"] = st.Page(
        ROOT / "app_pages" / "type_lab.py",
        title="مختبر الأنواع",
        icon=":material/biotech:",
        url_path="type-lab",
    )
    sections: dict[str, list[st.Page]] = {
        "": [pages_by_key["home"], pages_by_key["playground"], pages_by_key["type_lab"]]
    }
    for track in curriculum.tracks:
        lessons = curriculum.lessons_in(track.id)
        if not lessons:
            continue
        pages = []
        for lesson in lessons:
            state = progress.status(lesson)
            page = st.Page(
                _lesson_page(lesson.meta.id, render_lesson),
                title=lesson.meta.title_ar,
                icon=progress.STATUS_ICONS[state],
                url_path=lesson.meta.id,
            )
            pages_by_key[lesson.meta.id] = page
            pages.append(page)
        sections[f"{track.code} · {track.title_ar}"] = pages
    st.session_state["_pages"] = pages_by_key
    return sections
