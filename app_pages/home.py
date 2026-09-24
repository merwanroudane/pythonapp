"""Dashboard (blueprint §4): where am I, what have I learned, what do I do next?"""

import streamlit as st

from app.config import APP_TITLE_AR, AUTHOR, AUTHOR_URL, REPO_URL
from app.curriculum.registry import get_curriculum
from app.storage import progress
from app.ui.navigation import page_for
from app.ui.theme import track_tone


def _lectures(n: int) -> str:
    """Arabic count agreement: 1 محاضرة، 2 محاضرتان، 3-10 محاضرات، 11+ محاضرة."""
    if n == 1:
        return "محاضرة واحدة"
    if n == 2:
        return "محاضرتان"
    return f"{n} محاضرات" if n <= 10 else f"{n} محاضرة"


curriculum = get_curriculum()
lessons = curriculum.ordered_lessons()
statuses = {les.meta.id: progress.status(les) for les in lessons}

st.title(APP_TITLE_AR)
st.markdown(f":material/person: إعداد وتطوير **[{AUTHOR}]({AUTHOR_URL})**")
st.markdown(
    "منصة لتعلّم Python بالتجربة: لكل مفهوم شرح، ثم نموذج ذهني، ثم كود تشغّله بنفسك "
    "وترى ما يحدث خطوة بخطوة، ثم خطأ شائع وتمرين."
)

with st.container(horizontal=True, gap="medium"):
    counts = {s: sum(v == s for v in statuses.values()) for s in progress.STATUS_LABELS}
    st.metric("محاضرات متاحة", len(lessons), border=True)
    st.metric("تعرّفت عليها", len(lessons) - counts["not_started"], border=True)
    st.metric("تدرّبت عليها", counts["practiced"] + counts["demonstrated"], border=True)
    st.metric("أتقنتها", counts["demonstrated"], border=True)

# Continue learning: last opened lesson, otherwise the first one not yet mastered.
last = progress.last_lesson()
upcoming = next((les for les in lessons if statuses[les.meta.id] != "demonstrated"), None)
target = curriculum.lessons.get(last) if last else upcoming
with st.container(key="card-concept-continue", border=True):
    with st.container(key="cardtitle-continue"):
        st.markdown(":material/play_circle: تابع التعلّم · Continue Learning")
    if target is not None and (page := page_for(target.meta.id)):
        track = curriculum.track(target.meta.track)
        st.markdown(f"**{target.meta.title_ar}** — {track.code} · {track.title_ar}")
        st.page_link(page, label="افتح المحاضرة", icon=":material/arrow_back:")
    else:
        st.markdown("أتقنت كل المحاضرات المتاحة حاليًا.")

st.subheader("ابحث · Search")
query = st.text_input(
    "ابحث عن مفهوم أو دالة أو خطأ",
    placeholder="مثال: print، float، KeyError، loop",
    label_visibility="collapsed",
)
if query:
    q = query.strip().lower()
    hits = [
        les
        for les in lessons
        if q in les.meta.title_ar.lower()
        or q in les.meta.title_en.lower()
        or any(q in tag.lower() for tag in les.meta.tags)
        or any(q in block.body.lower() for block in les.blocks)
    ]
    if hits:
        for les in hits:
            if page := page_for(les.meta.id):
                st.page_link(
                    page,
                    label=f"{les.meta.title_ar} · {les.meta.title_en}",
                    icon=progress.STATUS_ICONS[statuses[les.meta.id]],
                )
    else:
        st.caption("لا نتائج في المحاضرات المتاحة حاليًا.")

st.subheader("خريطة المسار · Roadmap")
pending = sum(not curriculum.lessons_in(track.id) for track in curriculum.tracks)
st.caption(
    f"{len(curriculum.tracks)} مسارًا من «ما قبل Python» حتى المشاريع الختامية."
    + (" المسارات الرمادية قيد الإنشاء." if pending else "")
)
cols = st.columns(3)
for i, track in enumerate(curriculum.tracks):
    track_lessons = curriculum.lessons_in(track.id)
    tone = track_tone(track.order) if track_lessons else "neutral"
    with cols[i % 3], st.container(key=f"card-{tone}-track-{track.id}", border=True):
        with st.container(key=f"cardtitle-track-{track.id}"):
            st.markdown(f"{track.icon} {track.code} · {track.title_ar}")
        st.caption(f"{track.title_en} — {track.summary_ar}")
        if track_lessons:
            mastered = sum(statuses[les.meta.id] == "demonstrated" for les in track_lessons)
            st.progress(
                mastered / len(track_lessons),
                text=f"{_lectures(len(track_lessons))} · أتقنت {mastered}",
            )
            if page := page_for(track_lessons[0].meta.id):
                st.page_link(page, label="ابدأ المسار", icon=":material/arrow_back:")
        else:
            st.badge("قريبًا · Coming soon", icon=":material/construction:", color="gray")

errors = progress.errors_faced()
if errors:
    st.subheader("أخطاء واجهتها · Common errors I faced")
    st.caption("تُجمع من تشغيلك للكود في هذه الجلسة؛ كل خطأ فرصة لفهم أعمق.")
    st.bar_chart({"errors": dict(errors.most_common(8))}, horizontal=True)

st.divider()
st.caption(
    f"{APP_TITLE_AR} · إعداد وتطوير [{AUTHOR}]({AUTHOR_URL}) · "
    f"[الكود المصدري على GitHub]({REPO_URL})"
)
