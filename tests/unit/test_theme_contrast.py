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


@pytest.mark.parametrize("colour", ["red", "orange", "yellow", "green", "blue", "violet"])
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


def test_no_pink_hues_in_the_palette():
    """User requirement: multicolour, not pink (hues ~300°-350° are excluded)."""
    import colorsys

    for name, tone in TONES.items():
        r, g, b = (int(tone.base[i : i + 2], 16) / 255 for i in (1, 3, 5))
        hue, _, sat = colorsys.rgb_to_hls(r, g, b)
        assert not (sat > 0.25 and 0.83 <= hue <= 0.97), f"{name} base {tone.base} is pink"


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
