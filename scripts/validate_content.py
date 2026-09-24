"""Validate curriculum content (blueprint §101.3). Exit code 1 on any issue.

python scripts/validate_content.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.material_icon_names import ALL_MATERIAL_ICONS  # noqa: E402

from app.config import CONTENT_DIR  # noqa: E402
from app.curriculum.loader import load_curriculum  # noqa: E402
from app.curriculum.validation import validate  # noqa: E402


def icon_issues() -> list[str]:
    bad = []
    for path in [CONTENT_DIR / "tracks.yaml", *CONTENT_DIR.glob("lessons/*/*/lesson.*")]:
        for name in re.findall(r":material/([a-z0-9_]+):", path.read_text(encoding="utf-8")):
            if name not in ALL_MATERIAL_ICONS:
                bad.append(f"{path.relative_to(CONTENT_DIR)}: unknown icon '{name}'")
    return bad


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # Arabic / symbols on Windows consoles
    curriculum = load_curriculum()
    issues = [str(i) for i in validate(curriculum)] + icon_issues()
    for issue in issues:
        print("✗", issue)
    print(
        f"{len(curriculum.lessons)} lessons, {len(curriculum.tracks)} tracks, "
        f"{len(issues)} issue(s)"
    )
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
