"""WCAG AA contrast guard for the colour system (blueprint §3.2, §95, §123)."""

import tomllib

import pytest

from app.config import ROOT
from app.ui.theme import CANVAS, MUTED, RAISED, SOFT, TEXT, TONES, TRACK_TONES, blob

AA = 4.5


def _luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    hi, lo = sorted([_luminance(a), _luminance(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


THEME = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8"))["theme"]
SURFACES = [CANVAS, RAISED, SOFT]


@pytest.mark.parametrize("name", list(TONES))
def test_tone_ink_is_readable_on_every_surface_and_its_tint(name):
    tone = TONES[name]
    for surface in [*SURFACES, tone.tint]:
        assert contrast(tone.ink, surface) >= AA, f"{name} ink on {surface}"


@pytest.mark.parametrize(
    "colour", ["red", "orange", "yellow", "green", "blue", "violet"]
)  # violet slot = lime
def test_streamlit_text_colours_readable_on_their_tints(colour):
    text, tint = THEME[f"{colour}TextColor"], THEME[f"{colour}BackgroundColor"]
    for surface in [tint, THEME["backgroundColor"], THEME["secondaryBackgroundColor"]]:
        assert contrast(text, surface) >= AA, f"{colour}TextColor on {surface}"


def test_body_text_and_primary_button():
    assert contrast(TEXT, SOFT) >= AA and contrast(MUTED, SOFT) >= AA
    assert contrast("#FFFFFF", THEME["primaryColor"]) >= AA  # white label on primary button


def test_python_palette_matches_config():
    assert THEME["backgroundColor"] == CANVAS
    assert THEME["secondaryBackgroundColor"] == SOFT
    assert THEME["textColor"] == TEXT


def _is_pinkish(hex_colour: str) -> bool:
    """Purple / magenta / pink hues, and light reds (which read as pink)."""
    import colorsys

    r, g, b = (int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5))
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    deg = hue * 360
    if sat > 0.15 and 245 <= deg <= 345:  # violet, purple, magenta, pink
        return True
    return (deg <= 22 or deg >= 345) and light >= 0.8 and sat >= 0.25  # salmon too


def _all_colours() -> dict[str, str]:
    import re

    found = {}
    for name, tone in TONES.items():
        found.update(
            {f"{name}.base": tone.base, f"{name}.tint": tone.tint, f"{name}.ink": tone.ink}
        )
    for tone in TRACK_TONES:
        found[f"blob:{tone}"] = blob(tone)
    sources = [
        ROOT / ".streamlit" / "config.toml",
        ROOT / "app" / "ui" / "theme.py",
        ROOT / "app" / "components" / "code_editor" / "frontend" / "src" / "index.js",
    ]
    for path in sources:
        for match in re.findall(r"#[0-9A-Fa-f]{6}", path.read_text(encoding="utf-8")):
            found[f"{path.name}:{match}"] = match
    return found


def test_no_pink_purple_or_magenta_anywhere():
    """User requirement: multicolour, never pink (also no violet / lavender / light red)."""
    offenders = {k: v for k, v in _all_colours().items() if _is_pinkish(v)}
    assert not offenders, f"pink-looking colours found: {offenders}"


def test_pink_detector_catches_the_old_colours():
    for old in ("#E78FB3", "#8B6FE0", "#F3EEF3", "#FCEBE4", "#7352DA"):
        assert _is_pinkish(old), old
    for fine in ("#F4B400", "#3AA0E0", "#7CB518", "#E0524A", "#F7F6F2", "#FFFCF5"):
        assert not _is_pinkish(fine), fine


@pytest.mark.parametrize("tone", sorted(set(TRACK_TONES)))
def test_page_text_stays_readable_on_every_background_blob(tone):
    """The multicolour background must not cost legibility (§95)."""
    colour = blob(tone)
    for text, role in [
        (TEXT, "body"),
        (MUTED, "muted"),
        (THEME["linkColor"], "link"),
        (THEME["primaryColor"], "primary"),
    ]:
        assert contrast(text, colour) >= AA, f"{role} text on the {tone} blob {colour}"
