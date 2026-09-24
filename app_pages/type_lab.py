"""Type Lab page (blueprint §117)."""

import streamlit as st

from app.ui.property_lab import render_property_lab

st.title("مختبر الأنواع · Type Lab")
st.markdown(
    "اكتب أي قيمة في Python لترى **كل خصائصها** دفعة واحدة: نوعها، وهل هي نوع أساسي أم بنية "
    "بيانات، وهل هي قابلة للتعديل، مرتبة، تسمح بالتكرار، قابلة للـhash، كسولة… مع شرح كل خاصية. "
    "يُقيَّم الكود داخل المشغّل المعزول، لا داخل التطبيق."
)
render_property_lab(key="typelab-page", initial='[1, "2", 3.5, None, True, "missing"]')
