# Python Learning Lab — مختبر تعلّم Python

An Arabic-first, interactive Streamlit platform for learning Python, built from the
author's platform blueprint (the § numbers in the code refer to it). Roadmap status (§130):
**Phase A — Foundation** done; **Phase B — Core Python MVP** done (isolated execution,
code editor, loop/function animations). 51 lectures covering all 26 tracks (00–25), from
"Before Python" through NumPy, pandas, visualization, SQL, images, web data, decorators and
packaging to a capstone data-cleaning project. Basic data types (`int`, `float`, `complex`,
`bool`, `None`, `str`) and data structures (`list`, `tuple`, `set`, `dict`, `range`, `deque`,
`Counter`, …) are taught as two separate tracks.

Author: **Dr Merwan Roudane** — <https://github.com/merwanroudane>

## Run

```bash
git clone https://github.com/merwanroudane/pythonapp.git
cd pythonapp
pip install -r requirements-dev.txt
streamlit run streamlit_app.py
```

## Features

| Blueprint | Where |
|---|---|
| Right-hand sidebar, RTL text with LTR code islands (§3.1, §3.3, §123.2) | `app/ui/theme.py` |
| Bright multicolour light palette, no pink, WCAG AA inks (§3.2, §123) | `.streamlit/config.toml`, `app/ui/theme.py` |
| Content as data: `lesson.yaml` + `lesson.md` with `:::directives` (§80) | `content/`, `app/curriculum/` |
| Generic lesson renderer, Learn / Review / Reference views (§2.9, §81) | `app/ui/lesson_renderer.py` |
| CodeMirror 6 editor: Python highlighting, brackets, Tab indent, `Ctrl+Enter` (§6) | `app/components/code_editor/` |
| Code runner: output tabs, Script vs Notebook mode, `input()` bridge (§5) | `app/execution/`, `app/ui/code_cell.py` |
| Three execution backends: local / docker / remote API (§5.6, §103) | `app/execution/*_backend.py`, `executor_service/` |
| Variable inspector with aliasing / mutability, memory and backend badges (§5.2, §87) | `app/ui/output_panel.py` |
| Rule-based Arabic error explanations (§86) | `app/execution/explain.py` |
| Step-by-step execution: loop panel, call-stack frames, Play/Pause/Speed (§7.2, §8.4, §8.12, §90) | `app/ui/stepper.py`, `app/ui/loop_view.py` |
| Command-by-command explanations in every lecture: what the line does, its anatomy, the theory behind it, and what it changed (full DataFrame / array previews) | `app/ui/stepper.py`, `lesson.yaml` `animations` |
| Predict-first quizzes, exercises with hidden checks and graded hints (§76) | `app/ui/quiz.py`, `app/ui/exercise.py` |
| Change & Observe before/after (§2.10) | `app/ui/change.py` |
| Dashboard: progress, continue, search, 26-track roadmap, errors faced (§4) | `app_pages/home.py` |
| Type Lab: every property of any value, probed inside the runner (§117) | `app/ui/property_lab.py`, `app/execution/probe.py` |
| Content validation + example verification (§101) | `scripts/` |

## Execution backends

Choose with `PLL_EXECUTOR` (limits: `PLL_TIMEOUT_S`, `PLL_MEMORY_MB`):

| Backend | Isolation | Use for |
|---|---|---|
| `local` (default) | Separate process, empty temp cwd, stripped env, timeout that kills the tree, memory cap, **no child processes** (Windows Job Object / POSIX rlimits). No network block or filesystem jail. | Development, single user |
| `docker` | Fresh container per run: `--network none`, read-only root, uid 65534, all capabilities dropped, `no-new-privileges`, memory / CPU / pids limits, tmpfs workdir | Shared machines |
| `remote` | Streamlit calls `executor_service` over HTTP (token auth, size and concurrency caps, server-side limit clamping), which runs the Docker backend | Public deployment |

```bash
# Docker runtime image (§103.3 profiles: core-python, scientific)
docker build -f executor_service/docker/Dockerfile --target scientific -t pll-runner:scientific .

# Execution API + point the app at it
PLL_EXECUTOR_TOKEN=change-me python -m executor_service.server --backend docker --port 8765
PLL_EXECUTOR=remote PLL_EXECUTOR_URL=http://127.0.0.1:8765 PLL_EXECUTOR_TOKEN=change-me streamlit run streamlit_app.py
```

Put the execution API behind TLS when it is not on localhost.

## Code editor

`app/components/code_editor/editor.bundle.js` is a local CodeMirror 6 bundle (no CDN at
runtime), loaded as a Streamlit Custom Components v2 inline component. Rebuild it after
changing `frontend/src/index.js`:

```bash
cd app/components/code_editor/frontend
npm install
npm run build
```

`PLL_EDITOR=textarea` switches back to `st.text_area` (the test suite does this, because
AppTest cannot render custom components).

## Authoring a lesson

Create `content/lessons/<NN_track>/<lesson-id>/` with:

- `lesson.yaml` — metadata, objectives, and the data for `quizzes`, `exercises`,
  `animations`, `changes`.
- `lesson.md` — the lecture. Plain Markdown plus directives:

```text
:::concept title="optional"          card types: question concept definition theory syntax
Markdown body                         research warning mistake rule tip think try note
:::                                   deep_dive under_the_hood sketchnote cheatsheet docs

:::code mode="notebook" switch="true" runnable cell; expect="syntax_error" | "timeout" |
x = 1                                 "<ExceptionName>", run="false", inputs="a\nb"
x
:::

:::diagram title="..."                Mermaid (kind="text" for ASCII diagrams)
flowchart LR
  A --> B
:::

:::compare title="..."                columns separated by a line containing only |||
left
|||
right
:::

:::quiz id="q1":::    :::exercise id="ex1":::    :::animation id="a1":::    :::change id="c1":::

:::property_lab                       Type Lab block; the body is the starting value
[1, "2", None]
:::
```

An animation traces real code and explains the commands line by line. A note is either a
sentence or a command explanation with anatomy and theory:

```yaml
animations:
  a1:
    title: "..."
    code: |
      df = pd.read_csv("data.csv")
    notes:
      1:
        what: "What this command does."
        parts:
          - ["pd.read_csv(...)", "what this piece means"]
        theory: "Why it works this way."
```

Then check it:

```bash
python scripts/validate_content.py
python scripts/verify_examples.py
python -m pytest
```

`verify_examples.py` runs every example, animation and variant (feeding `inputs=` to
`input()`), checks each `expect=`, checks that every animation note sits on a line that
actually runs, and checks that each exercise's reference solution passes while its
starter code does not.

## Next (Phase C)

More lectures per track, notebook simulator, debugger visualizer, API explorer.
