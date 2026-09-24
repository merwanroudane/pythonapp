"""Application-wide settings."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"

APP_TITLE = "Python Learning Lab"
APP_TITLE_AR = "مختبر تعلّم Python"

AUTHOR = "Dr Merwan Roudane"
AUTHOR_URL = "https://github.com/merwanroudane"
REPO_URL = "https://github.com/merwanroudane/pythonapp"

RUNNER_TIMEOUT_S = 5.0
