"""Editor component: bundle present, v2-only, safe fallback (blueprint §6)."""

from app.components import code_editor


def test_bundle_is_built_and_multiline():
    assert code_editor.BUNDLE.exists(), "run `npm install && npm run build` in frontend/"
    text = code_editor.BUNDLE.read_text(encoding="utf-8")
    assert "\n" in text[:200], "CCv2 needs a multi-line string to treat it as inline JS"
    assert "export default" in text or "export{" in text.replace(" ", "")


def test_no_components_v1_patterns():
    source = (code_editor.BUNDLE.parent / "frontend" / "src" / "index.js").read_text(
        encoding="utf-8"
    )
    for banned in ("Streamlit.setComponentValue", "setFrameHeight", "window.parent.postMessage"):
        assert banned not in source


def test_textarea_fallback_is_selected_by_env(monkeypatch):
    monkeypatch.setenv("PLL_EDITOR", "textarea")
    assert code_editor._use_codemirror() is False
    monkeypatch.setenv("PLL_EDITOR", "codemirror")
    assert code_editor._use_codemirror() is True
