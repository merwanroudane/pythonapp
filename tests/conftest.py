"""Test-wide settings."""

import os

# AppTest cannot render custom components; the editor falls back to st.text_area.
os.environ.setdefault("PLL_EDITOR", "textarea")
os.environ.setdefault("PLL_EXECUTOR", "local")
