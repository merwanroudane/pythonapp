// Python Learning Lab — CodeMirror 6 editor as a Streamlit CCv2 component (blueprint §6).
//
// Contract with app/components/code_editor/__init__.py
//   data:    { code, nonce, readOnly, minLines, maxLines }
//   state:   "code"  — committed on blur and before a run (like st.text_area)
//   trigger: "run"   — Ctrl/Cmd+Enter or Shift+Enter; payload is the current code
// The Python side bumps `nonce` to replace the document (Reset button); otherwise the
// editor keeps its own document so typing never fights with re-renders.

import { autocompletion, closeBrackets, closeBracketsKeymap, completionKeymap } from "@codemirror/autocomplete"
import { defaultKeymap, history, historyKeymap, indentWithTab } from "@codemirror/commands"
import { python } from "@codemirror/lang-python"
import { bracketMatching, HighlightStyle, indentOnInput, indentUnit, syntaxHighlighting } from "@codemirror/language"
import { Compartment, EditorState } from "@codemirror/state"
import {
  drawSelection,
  EditorView,
  highlightActiveLine,
  highlightActiveLineGutter,
  keymap,
  lineNumbers,
} from "@codemirror/view"
import { tags as t } from "@lezer/highlight"

// Syntax colours = the palette's text-safe inks (all >= 4.5:1 on white).
const pllHighlight = HighlightStyle.define([
  { tag: t.keyword, color: "#2469CE", fontWeight: "600" },
  { tag: [t.string, t.special(t.string)], color: "#2D7B4B" },
  { tag: [t.number, t.integer, t.float], color: "#A7580A" },
  { tag: [t.bool, t.null, t.atom], color: "#177874", fontWeight: "600" },
  { tag: t.comment, color: "#6B665C", fontStyle: "italic" },
  { tag: [t.function(t.variableName), t.function(t.propertyName)], color: "#1B72A9" },
  { tag: t.definition(t.variableName), color: "#2B2A27", fontWeight: "600" },
  { tag: [t.className, t.definition(t.className)], color: "#8B6700", fontWeight: "600" },
  { tag: t.operator, color: "#A7580A" },
  { tag: t.self, color: "#2469CE", fontStyle: "italic" },
])

const pllTheme = EditorView.theme({
  "&": {
    backgroundColor: "#FFFFFF",
    color: "#2B2A27",
    fontSize: "0.92rem",
    border: "1px solid var(--st-border-color, #E4DDCF)",
    borderRadius: "var(--st-base-radius, 10px)",
  },
  "&.cm-focused": { outline: "2px solid #A7580A", outlineOffset: "1px" },
  ".cm-scroller": {
    fontFamily: '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
    lineHeight: "1.6",
  },
  ".cm-content": { caretColor: "#A7580A", padding: "8px 0" },
  ".cm-gutters": {
    backgroundColor: "#F6F3EA",
    color: "#6B665C",
    border: "none",
    borderRight: "1px solid #E4DDCF",
    borderTopLeftRadius: "var(--st-base-radius, 10px)",
    borderBottomLeftRadius: "var(--st-base-radius, 10px)",
  },
  ".cm-activeLine": { backgroundColor: "#FEF5DC80" },
  ".cm-activeLineGutter": { backgroundColor: "#FEF5DC", color: "#2B2A27" },
  "&.cm-focused .cm-selectionBackground, .cm-selectionBackground, ::selection": {
    backgroundColor: "#CFE6F7 !important",
  },
  ".cm-matchingBracket": { backgroundColor: "#ECF4E7", outline: "1px solid #3FAE6A" },
  ".cm-tooltip": { border: "1px solid #E4DDCF", backgroundColor: "#FFFFFF" },
})

const editors = new WeakMap()

function heightTheme(minLines, maxLines) {
  const line = 1.6 * 0.92 * 16
  return EditorView.theme({
    ".cm-scroller": { minHeight: `${Math.round(minLines * line + 16)}px`, maxHeight: `${Math.round(maxLines * line + 16)}px`, overflow: "auto" },
  })
}

export default function (component) {
  const { data, parentElement, setStateValue, setTriggerValue } = component
  const host = parentElement.querySelector(".pll-editor")
  if (!host) return

  const code = typeof data?.code === "string" ? data.code : ""
  const nonce = data?.nonce ?? 0
  const readOnly = Boolean(data?.readOnly)
  let entry = editors.get(parentElement)

  if (!entry) {
    const readOnlyConf = new Compartment()
    let committed = code

    const commit = (view) => {
      const doc = view.state.doc.toString()
      if (doc !== committed) {
        committed = doc
        setStateValue("code", doc)
      }
      return doc
    }
    const run = (view) => {
      const doc = commit(view)
      setTriggerValue("run", doc)
      return true
    }

    const view = new EditorView({
      root: parentElement,
      parent: host,
      state: EditorState.create({
        doc: code,
        extensions: [
          lineNumbers(),
          highlightActiveLineGutter(),
          highlightActiveLine(),
          drawSelection(),
          history(),
          indentOnInput(),
          indentUnit.of("    "),
          EditorState.tabSize.of(4),
          bracketMatching(),
          closeBrackets(),
          autocompletion({ activateOnTyping: false }), // Ctrl+Space only: never write the answer
          python(),
          syntaxHighlighting(pllHighlight),
          pllTheme,
          heightTheme(data?.minLines ?? 4, data?.maxLines ?? 24),
          keymap.of([
            { key: "Mod-Enter", run },
            { key: "Shift-Enter", run },
            indentWithTab,
            ...closeBracketsKeymap,
            ...completionKeymap,
            ...historyKeymap,
            ...defaultKeymap,
          ]),
          readOnlyConf.of(EditorState.readOnly.of(readOnly)),
          EditorView.domEventHandlers({ blur: (_event, v) => { commit(v) } }),
          EditorView.contentAttributes.of({ "aria-label": "Python code editor", dir: "ltr" }),
        ],
      }),
    })
    entry = { view, nonce, readOnlyConf, setCommitted: (v) => { committed = v } }
    editors.set(parentElement, entry)
  } else {
    const { view } = entry
    if (entry.nonce !== nonce) {
      // Python asked for a new document (Reset / starter code).
      entry.nonce = nonce
      entry.setCommitted(code)
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: code } })
    }
    view.dispatch({ effects: entry.readOnlyConf.reconfigure(EditorState.readOnly.of(readOnly)) })
  }

  return () => {
    const current = editors.get(parentElement)
    if (current) {
      current.view.destroy()
      editors.delete(parentElement)
    }
  }
}
