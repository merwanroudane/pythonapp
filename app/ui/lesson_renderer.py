"""Generic Lesson Renderer (blueprint §79.1, §81, §2.9).

Every lesson page is produced from content/ by this one renderer, in one of three
views built from the same blocks: Learn (full lecture), Review, Reference.
"""

from __future__ import annotations

import html

import streamlit as st

from app.config import AUTHOR, AUTHOR_URL
from app.curriculum.blocks import CARDS, LEARN, REFERENCE, REVIEW, views_for
from app.curriculum.registry import get_curriculum
from app.curriculum.schema import Block, Lesson
from app.storage import progress
from app.ui.bidi import ltr
from app.ui.cards import render_card, render_compare
from app.ui.change import render_change
from app.ui.code_cell import render_code_cell
from app.ui.exercise import render_exercise
from app.ui.navigation import page_for
from app.ui.quiz import render_quiz
from app.ui.stepper import render_stepper, steps_for_animation
from app.ui.theme import page_background, track_blobs

LEVEL_LABELS = {
    "beginner": "مبتدئ · Beginner",
    "beginner_to_intermediate": "مبتدئ ← متوسط",
    "intermediate": "متوسط · Intermediate",
    "advanced": "متقدم · Advanced",
    "expert": "خبير · Expert",
}
VIEWS = {
    LEARN: ":material/school: تعلّم · Learn",
    REVIEW: ":material/replay: مراجعة · Review",
    REFERENCE: ":material/menu_book: مرجع · Reference",
}


def _header(lesson: Lesson) -> str:
    curriculum = get_curriculum()
    meta = lesson.meta
    track = curriculum.track(meta.track)
    state = progress.status(lesson)

    page_background(track_blobs(track.order))
    st.caption(f":material/route: المسار {track.code} · {track.title_ar}")
    st.title(meta.title_ar)
    st.markdown(
        f'<p class="ltr" style="color:var(--text-muted);margin-top:-0.8rem">'
        f"{html.escape(track.title_en)} › {html.escape(meta.title_en)}</p>",
        unsafe_allow_html=True,
    )
    with st.container(horizontal=True, gap="small", vertical_alignment="center"):
        if meta.kind == "theory":
            st.badge("محاضرة نظرية · Theory", icon=":material/school:", color="blue")
        st.badge(LEVEL_LABELS[meta.level], icon=":material/signal_cellular_alt:", color="violet")
        st.badge(f"{meta.estimated_minutes} دقيقة", icon=":material/schedule:", color="blue")
        st.badge(ltr(f"Python ≥ {meta.python_min}"), icon=":material/code:", color="orange")
        st.badge(progress.STATUS_LABELS[state], icon=progress.STATUS_ICONS[state], color="green")
        st.space("stretch")
        st.button(
            "إعادة الدرس",
            icon=":material/restart_alt:",
            key=f"reset-lesson-{meta.id}",
            on_click=progress.reset_lesson,
            args=(meta.id,),
            help="يمسح تقدّمك وتعديلاتك في هذا الدرس",  # noqa: E501
        )
    if meta.prerequisites:
        with st.container(horizontal=True, gap="small", vertical_alignment="center"):
            st.caption("المتطلبات السابقة:")
            for prereq in meta.prerequisites:
                target = page_for(prereq)
                if target is not None:
                    st.page_link(target, icon=":material/arrow_back:")
    if meta.objectives:
        with st.container(key=f"card-concept-objectives-{meta.id}", border=True):
            with st.container(key=f"cardtitle-objectives-{meta.id}"):
                st.markdown(":material/flag: أهداف المحاضرة · Learning Objectives")
            st.markdown("\n".join(f"- {goal}" for goal in meta.objectives))

    view = st.segmented_control(
        "طريقة العرض",
        list(VIEWS),
        default=LEARN,
        format_func=VIEWS.get,
        key=f"view-{meta.id}-mode",
        label_visibility="collapsed",
        required=True,
    )
    return view or LEARN


def _render_block(lesson: Lesson, block: Block, index: int) -> None:
    meta = lesson.meta
    key = f"{meta.id}-b{index}"
    attrs = block.attrs
    kind = block.type

    if kind == "markdown":
        st.markdown(block.body)
    elif kind in CARDS:
        render_card(kind, block.body, key, attrs.get("title"))
    elif kind == "compare":
        render_compare(block.body, key, attrs.get("title"))
    elif kind == "code":
        inputs = attrs.get("inputs")
        render_code_cell(
            block.body,
            key=key,
            lesson_id=meta.id,
            mode=attrs.get("mode", "script"),
            allow_mode_switch=attrs.get("switch") == "true",
            inputs=inputs.replace("\\n", "\n") if inputs is not None else None,
            runnable=attrs.get("run", "true") != "false",
        )
    elif kind == "diagram":
        with st.container(border=True, key=f"diagram-{key}"):
            if attrs.get("title"):
                st.markdown(f":material/schema: **{attrs['title']}**")
            if attrs.get("kind", "mermaid") == "mermaid":
                st.mermaid_chart(block.body)
            else:
                st.code(block.body, language="text")
    elif kind == "quiz":
        quiz_id = attrs["id"]
        render_quiz(meta.quizzes[quiz_id], quiz_id=quiz_id, lesson_id=meta.id, key=key)
    elif kind == "exercise":
        ex_id = attrs["id"]
        render_exercise(meta.exercises[ex_id], exercise_id=ex_id, lesson_id=meta.id, key=key)
    elif kind == "animation":
        anim = meta.animations[attrs["id"]]
        with st.spinner("تجهيز التتبّع…"):
            steps = steps_for_animation(anim)
        render_stepper(anim.code, steps, key=f"anim-{key}", title=anim.title)
    elif kind == "change":
        render_change(meta.changes[attrs["id"]], key=key)


def _footer(lesson: Lesson) -> None:
    meta = lesson.meta
    st.divider()
    prev_lesson, next_lesson = get_curriculum().neighbours(meta.id)
    with st.container(horizontal=True, vertical_alignment="center"):
        if prev_lesson and (target := page_for(prev_lesson.meta.id)):
            st.page_link(
                target,
                label=f"السابق: {prev_lesson.meta.title_ar}",
                icon=":material/arrow_forward:",
            )
        st.space("stretch")
        if next_lesson and (target := page_for(next_lesson.meta.id)):
            st.page_link(
                target, label=f"التالي: {next_lesson.meta.title_ar}", icon=":material/arrow_back:"
            )
    notes = []
    if meta.docs_url:
        notes.append(f"[التوثيق الرسمي]({meta.docs_url})")
    if meta.last_verified:
        notes.append(f"آخر تحقق: {meta.last_verified}")
    notes.append(f"Python ≥ {meta.python_min}")
    notes.append(f"إعداد: [{AUTHOR}]({AUTHOR_URL})")
    st.caption(" · ".join(notes))


def render_lesson(lesson_id: str) -> None:
    lesson = get_curriculum().lessons[lesson_id]
    progress.mark_viewed(lesson_id)
    view = _header(lesson)
    shown = 0
    for index, block in enumerate(lesson.blocks):
        if view in views_for(block.type, block.attrs):
            _render_block(lesson, block, index)
            shown += 1
    if shown == 0:
        st.info("لا توجد عناصر لهذا العرض في هذا الدرس بعد.", icon=":material/info:")
    if view == REVIEW:
        st.caption("وضع المراجعة: البطاقات، القواعد، الأخطاء الشائعة، والملخص فقط.")
    elif view == REFERENCE:
        st.caption("وضع المرجع: الصياغة، الملخص، والتوثيق الرسمي.")
    _footer(lesson)
