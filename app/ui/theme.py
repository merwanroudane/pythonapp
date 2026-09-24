"""Design tokens and the app-wide stylesheet (blueprint §3, §123).

Colours for Streamlit's own widgets live in .streamlit/config.toml. This module holds
the same palette for the parts config.toml cannot reach: RTL direction, the right-hand
sidebar (§123.2), the colour identity of lesson cards (§2.7), and the multicolour page
background: soft colour "blobs" over the cream canvas, tinted by each page's track.

The sidebar/RTL selectors were verified against Streamlit 1.63's DOM. Streamlit's
internal data-testid names can change between releases, so re-check the layout after
upgrading (tests/integration/test_app.py asserts the stylesheet is injected).
"""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

CANVAS = "#FFFCF5"
RAISED = "#FFFFFF"
SOFT = "#F6F3EA"
BORDER = "#E4DDCF"
TEXT = "#2B2A27"
MUTED = "#6B665C"

# Strength of the background colour blobs at their centre (share of the tone's base
# colour mixed into the canvas). At 0.16 body text, muted text, links and the primary
# colour all stay >= 4.5:1 — tests/unit/test_theme_contrast.py checks every blob.
BLOB_STRENGTH = 0.16


@dataclass(frozen=True)
class Tone:
    base: str  # stripes, icons, chart marks — never text
    tint: str  # light card background
    ink: str  # text-safe colour: >= 4.5:1 on CANVAS, RAISED, SOFT and tint


TONES: dict[str, Tone] = {
    "concept": Tone("#F4B400", "#FEF5DC", "#8B6700"),  # amber
    "example": Tone("#F28C28", "#FEF1E0", "#A7580A"),  # orange
    "practice": Tone("#3FAE6A", "#ECF4E7", "#2D7B4B"),  # green
    "insight": Tone("#1FA5A0", "#E9F3EC", "#177874"),  # teal
    "deepdive": Tone("#8B6FE0", "#F3EEF3", "#7352DA"),  # violet
    "data": Tone("#3AA0E0", "#EBF3F3", "#1B72A9"),  # sky
    "theory": Tone("#5B7FE0", "#EFF0F3", "#3763D9"),  # indigo
    "highlight": Tone("#F5D547", "#FEF8E4", "#826C07"),  # yellow
    "warning": Tone("#E0A526", "#FCF3E0", "#8C6614"),  # gold
    "error": Tone("#E0524A", "#FCEBE4", "#CA2C23"),  # red
    "neutral": Tone("#B5AC9C", SOFT, MUTED),
}

# One hue per track, in track order; used by the roadmap cards and the lesson pages.
TRACK_TONES = ["concept", "example", "practice", "insight", "deepdive", "data", "theory"]
HOME_BLOBS = ["concept", "data", "practice", "deepdive", "example", "insight"]


def mix(a: str, b: str, t: float) -> str:
    pa = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    channels = (round(x * (1 - t) + y * t) for x, y in zip(pa, pb, strict=True))
    return "#" + "".join(f"{c:02X}" for c in channels)


def blob(tone: str) -> str:
    return mix(CANVAS, TONES[tone].base, BLOB_STRENGTH)


def track_tone(track_order: int) -> str:
    return TRACK_TONES[track_order % len(TRACK_TONES)]


def track_blobs(track_order: int) -> list[str]:
    """Six background tones for a lesson page: led by its track's hue, then the others."""
    n = len(TRACK_TONES)
    return [TRACK_TONES[(track_order + k) % n] for k in (0, 2, 4, 0, 1, 3)]


def _tone_rules() -> str:
    rules = []
    for name, tone in TONES.items():
        rules.append(
            f'[class*="st-key-card-{name}-"]{{--tone:{tone.base};--tone-tint:{tone.tint};'
            f"--tone-ink:{tone.ink};}}"
        )
    return "\n".join(rules)


def _blob_vars(tones: list[str]) -> str:
    return ";".join(f"--blob-{i + 1}:{blob(t)}" for i, t in enumerate(tones))


STYLESHEET = f"""
<style>
:root {{
  --bg-canvas: {CANVAS}; --bg-raised: {RAISED}; --bg-soft: {SOFT};
  --border-soft: {BORDER}; --text-main: {TEXT}; --text-muted: {MUTED};
  {_blob_vars(HOME_BLOBS)};
}}

/* Multicolour background: six soft blobs over the cream canvas (§3.2). Overlaps blend
   between already-tested light colours, so they are never darker than one blob. */
[data-testid="stApp"] {{
  background-color: var(--bg-canvas);
  background-image:
    radial-gradient(ellipse 75% 60% at 100% 0%, var(--blob-1) 0%, transparent 72%),
    radial-gradient(ellipse 70% 60% at 0% 20%, var(--blob-2) 0%, transparent 72%),
    radial-gradient(ellipse 80% 60% at 20% 100%, var(--blob-3) 0%, transparent 72%),
    radial-gradient(ellipse 65% 55% at 100% 85%, var(--blob-4) 0%, transparent 72%),
    radial-gradient(ellipse 55% 45% at 55% 45%, var(--blob-5) 0%, transparent 70%),
    radial-gradient(ellipse 50% 40% at 30% 55%, var(--blob-6) 0%, transparent 70%);
  background-attachment: fixed;
}}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stSidebar"] > div:first-child {{
  background-image: linear-gradient(180deg, var(--blob-1) 0%, {SOFT} 45%, var(--blob-2) 100%);
}}
/* Working surfaces stay white so code and output read calmly on the colour. */
[class*="st-key-cell-"], [class*="st-key-diagram-"] {{
  background: var(--bg-raised); border-radius: 12px;
}}
[data-testid="stMetric"] {{ background: rgba(255, 255, 255, 0.72); border-radius: 10px; }}

/* §123.2 option 2 — Streamlit sidebar moved to the right. */
[data-testid="stAppViewContainer"] {{ flex-direction: row-reverse; }}
/* Collapsed: Streamlit shrinks the sidebar to width 0 and slides it left; clip it instead
   so its 300px content cannot overflow back over the page. */
[data-testid="stSidebar"][aria-expanded="false"] {{
  transform: none !important; overflow: hidden; visibility: hidden;
}}
@media (max-width: 767.98px) {{
  [data-testid="stSidebar"] {{ left: auto !important; right: 0 !important; }}
}}
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {{ transform: scaleX(-1); }}

/* §3.3 — RTL interface, LTR technical islands. */
[data-testid="stMain"], [data-testid="stSidebar"], [data-testid="stHeader"] {{ direction: rtl; }}
[data-testid="stMarkdownContainer"] {{ text-align: right; }}
/* Streamlit indents list items with margin-left; mirror it for RTL. */
[data-testid="stMarkdownContainer"] li {{
  margin-left: 0; margin-right: 1.2rem; padding-left: 0; padding-right: 0.3rem;
}}
[data-testid="stMarkdownContainer"] code {{ direction: ltr; unicode-bidi: isolate; }}
pre, textarea, [data-testid="stCode"], [data-testid="stDataFrame"], [data-testid="stTable"],
[data-testid="stSlider"], [data-testid="stMermaidChart"], [data-testid="stException"],
.ltr {{ direction: ltr; text-align: left; unicode-bidi: isolate; }}
[class*="st-key-code-"] textarea {{
  font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 0.9rem; line-height: 1.55;
  background: var(--bg-raised); tab-size: 4;
}}

/* §2.7 — lesson cards: tinted body, coloured stripe on the reading-start (right) edge. */
{_tone_rules()}
[class*="st-key-card-"] {{
  background: var(--tone-tint);
  border: 1px solid color-mix(in srgb, var(--tone) 35%, transparent) !important;
  border-right: 6px solid var(--tone) !important;
}}
[class*="st-key-cardtitle-"] p, [class*="st-key-cardtitle-"] span {{
  color: var(--tone-ink) !important; font-weight: 700;
}}
[class*="st-key-loopstrip-"] {{ direction: ltr; justify-content: flex-start; }}
</style>
"""


def inject_css() -> None:
    st.html(STYLESHEET)


def page_background(tones: list[str]) -> None:
    """Re-colour the background blobs for the current page (e.g. a lesson's track)."""
    st.html(f"<style>:root {{ {_blob_vars(tones)}; }}</style>")
