"""Playground (blueprint §97.2): free code + inspector."""

import streamlit as st

from app.execution.client import backend_name, is_sandboxed
from app.execution.limits import Limits
from app.ui.code_cell import render_code_cell

st.title("ساحة التجريب · Playground")
st.markdown(
    "اكتب أي كود Python وشغّله. جرّب **Notebook mode** لترى قيمة آخر expression تُعرض "
    "تلقائيًا، و**خطوة بخطوة** لترى كيف تتغير الأسماء مع كل سطر. اختصار التشغيل: "
    "`Ctrl` + `Enter`."
)

limits = Limits.from_env()
if is_sandboxed():
    st.info(
        f"يعمل الكود داخل sandbox معزول (`{backend_name()}`): بلا شبكة، بنظام ملفات للقراءة "
        f"فقط، وحدود {limits.memory_mb} MB و{limits.timeout_s:g} ثوانٍ.",
        icon=":material/shield:",
    )
else:
    st.warning(
        f"المشغّل المحلي: process مستقلة لكل تشغيل، بحد ذاكرة {limits.memory_mb} MB ومهلة "
        f"{limits.timeout_s:g} ثوانٍ ومنع إنشاء processes أخرى، لكنه لا يحجب الشبكة ولا "
        "يعزل نظام الملفات. للاستخدام العام شغّل `PLL_EXECUTOR=docker` (§103).",
        icon=":material/shield:",
    )

STARTER = """names = ["Sara", "Omar", "Lina"]
for i, name in enumerate(names, start=1):
    print(f"{i}. {name}")

total = len(names)
total
"""

render_code_cell(STARTER, key="playground-main", mode="notebook", allow_mode_switch=True, inputs="")
