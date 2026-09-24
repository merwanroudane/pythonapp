"""Python Learning Lab — entry point (blueprint §79.1)."""

import streamlit as st

from app.config import APP_TITLE, APP_TITLE_AR, AUTHOR, AUTHOR_URL
from app.curriculum.registry import get_curriculum
from app.storage import progress
from app.ui.lesson_renderer import render_lesson
from app.ui.navigation import build_navigation
from app.ui.theme import inject_css

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=":material/school:",
    menu_items={"About": f"{APP_TITLE} — {AUTHOR}"},
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

page = st.navigation(build_navigation(render_lesson), position="sidebar", expanded=True)

with st.sidebar:
    lessons = get_curriculum().ordered_lessons()
    done = sum(progress.status(les) == "demonstrated" for les in lessons)
    st.markdown(f"**:material/school: {APP_TITLE_AR}**")
    st.progress(
        done / len(lessons) if lessons else 0.0, text=f"أتقنت {done} من {len(lessons)} محاضرات"
    )
    st.caption(f":material/person: إعداد وتطوير · [{AUTHOR}]({AUTHOR_URL})")

page.run()
