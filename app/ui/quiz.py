"""Predict-first and concept checks (blueprint §2.1 "Predict First", §2.13 Exit Ticket)."""

from __future__ import annotations

import streamlit as st

from app.curriculum.schema import Quiz
from app.storage import progress

_KIND_LABEL = {
    "predict": (":material/online_prediction:", "توقّع قبل التشغيل · Predict First", "highlight"),
    "concept": (":material/quiz:", "تحقق من الفهم · Check", "insight"),
    "exit": (":material/logout:", "بطاقة الخروج · Exit Ticket", "insight"),
}


def render_quiz(quiz: Quiz, *, quiz_id: str, lesson_id: str, key: str) -> None:
    icon, label, tone = _KIND_LABEL[quiz.kind]
    answer_key = f"quizans-{key}"
    with st.container(key=f"card-{tone}-{key}", border=True):
        with st.container(key=f"cardtitle-{key}"):
            st.markdown(f"{icon} {label}")
        st.markdown(quiz.question)
        if quiz.code:
            st.code(quiz.code, language="python", line_numbers=True)
        choice = st.radio(
            "اختر إجابة",
            range(len(quiz.options)),
            index=None,
            key=f"quizradio-{key}",
            format_func=lambda i: quiz.options[i],
            label_visibility="collapsed",
        )
        if st.button(
            "تحقّق", icon=":material/fact_check:", key=f"quizbtn-{key}", disabled=choice is None
        ):
            st.session_state[answer_key] = choice
        answered = st.session_state.get(answer_key)
        if answered is not None:
            if answered == quiz.answer:
                progress.mark_quiz(lesson_id, quiz_id)
                st.success(f"**إجابة صحيحة.** {quiz.explanation}", icon=":material/check_circle:")
            else:
                st.error(
                    f"**ليست هذه.** الإجابة الصحيحة: {quiz.options[quiz.answer]}\n\n"
                    f"{quiz.explanation}",
                    icon=":material/cancel:",
                )
