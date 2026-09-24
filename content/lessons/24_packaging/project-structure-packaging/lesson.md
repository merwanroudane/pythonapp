:::question
بدأت بسكربت `analysis.py` واحد. بعد ستة أشهر: 15 ملفًا، ودوال منسوخة بين الملفات، وزميل لا يستطيع
تشغيل الكود على جهازه لأنه «لا يعرف أي مكتبات يثبّت». **كيف يصبح الكود مشروعًا منظمًا يمكن لأي شخص
تثبيته وتشغيله؟**
:::

:::theory title="من السكربت إلى المشروع"
المشروع الجيد يجيب عن أربعة أسئلة دون أن تسأل صاحبه:

1. **أين الكود؟** في **حزمة (package)**: مجلد فيه `__init__.py` ووحدات مقسمة حسب المسؤولية.
2. **ما الذي يحتاجه؟** في **`pyproject.toml`**: الملف القياسي (PEP 621) الذي يصف الاسم والإصدار وإصدار
   Python والتبعيات، وإعدادات الأدوات (ruff، pytest).
3. **كيف أشغّله؟** بـ**بيئة افتراضية (virtual environment)** معزولة، ثم تثبيت المشروع، ثم أمر CLI أو
   دالة `main()`.
4. **هل يعمل؟** بـ**اختبارات** في `tests/` تُشغَّل بأمر واحد.

و**الحزمة القابلة للتوزيع** تُبنى من هذا كله كملف **wheel** (`.whl`) يمكن رفعه إلى **PyPI** ليثبّته
الناس بـ`pip install`.
:::

:::diagram kind="text" title="src layout"
   survey-tools/                     ← the repository (Git)
   ├── pyproject.toml                ← metadata, dependencies, tool settings
   ├── README.md   LICENSE   .gitignore
   ├── src/
   │   └── survey_tools/             ← the importable package
   │       ├── __init__.py           ← __version__, public API
   │       ├── cleaning.py
   │       ├── models.py
   │       └── cli.py                ← main() for the command line
   ├── tests/
   │   └── test_cleaning.py
   ├── data/raw/    data/processed/  ← raw data is never edited by hand
   └── outputs/figures/              ← generated, reproducible from code
:::

:::quiz id="q-src":::

## pyproject.toml

:::code mode="script"
import tomllib

text = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "survey-tools"
version = "0.3.1"
description = "Cleaning and summarising survey data"
requires-python = ">=3.11"
dependencies = ["pandas>=2.2", "matplotlib>=3.9"]

[project.optional-dependencies]
dev = ["pytest", "ruff"]

[project.scripts]
survey = "survey_tools.cli:main"

[tool.ruff]
line-length = 100
"""
cfg = tomllib.loads(text)
print(cfg["project"]["name"], cfg["project"]["version"])
print("needs:", cfg["project"]["dependencies"])
print("command 'survey' runs:", cfg["project"]["scripts"]["survey"])
:::

:::syntax
| الجزء | الوظيفة |
|---|---|
| `[build-system]` | الأداة التي تبني الحزمة (hatchling، setuptools…) |
| `[project]` | الاسم، الإصدار، الوصف، `requires-python`، `dependencies` |
| `[project.optional-dependencies]` | تبعيات اختيارية: `pip install -e ".[dev]"` |
| `[project.scripts]` | أوامر سطر الأوامر: `اسم = "package.module:function"` |
| `[tool.<name>]` | إعدادات الأدوات: ruff، pytest، mypy |
:::

## البيئة والتثبيت (في الـterminal)

```text
python -m venv .venv                 # create an isolated environment
.venv\Scripts\activate               # Windows   (macOS/Linux: source .venv/bin/activate)
python -m pip install -e ".[dev]"    # install the project in editable mode + dev tools
pytest                               # run the tests
survey data/raw/survey.csv --sep ";" # the command declared in [project.scripts]

# the same with uv (fast, manages the venv and a lock file for you):
uv sync
uv run pytest
```

:::tip
**editable install** (`-e`) يربط البيئة بمجلد `src/` مباشرة: تعدّل الكود فيُستخدم فورًا دون إعادة تثبيت.
:::

## بناء حزمة حقيقية في المجلد والتحقق منها

:::code mode="script"
import importlib
import sys
from pathlib import Path

pkg = Path("src/survey_tools")
pkg.mkdir(parents=True, exist_ok=True)
(pkg / "__init__.py").write_text('__version__ = "0.3.1"\nfrom .cleaning import clean_age\n', encoding="utf-8")
(pkg / "cleaning.py").write_text(
    "def clean_age(value):\n"
    "    age = int(str(value).strip())\n"
    "    if not 0 <= age <= 120:\n"
    "        raise ValueError(f'impossible age: {age}')\n"
    "    return age\n",
    encoding="utf-8",
)
sys.path.insert(0, "src")          # what an install would arrange for you
survey_tools = importlib.import_module("survey_tools")
print(survey_tools.__version__, survey_tools.clean_age(" 42 "))
print(sorted(p.as_posix() for p in Path("src").rglob("*.py")))
:::

## CLI وحارس `__main__`

:::code mode="script"
import argparse


def build_parser():
    parser = argparse.ArgumentParser(prog="survey", description="Summarise a survey CSV")
    parser.add_argument("path", help="CSV file")
    parser.add_argument("--sep", default=",", help="field separator")
    parser.add_argument("--verbose", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    print(f"reading {args.path!r} with sep={args.sep!r} verbose={args.verbose}")
    return 0


if __name__ == "__main__":     # runs as a script, not when imported
    main(["survey.csv", "--sep", ";", "--verbose"])
:::

:::animation id="anim-cli":::

:::quiz id="q-semver":::

:::rule
- **كل التبعيات في `pyproject.toml`** مع حدود دنيا معقولة (`pandas>=2.2`)، وملف قفل (`uv.lock`) لإعادة
  إنتاج البيئة نفسها بالضبط.
- **Git من اليوم الأول:** commits صغيرة برسائل واضحة، و`.gitignore` يستبعد `.venv/` و`__pycache__/`
  و`.env` والبيانات الكبيرة أو الحساسة.
- **LICENSE** (MIT، Apache-2.0، GPL…) وإلا فالكود قانونيًا «كل الحقوق محفوظة».
- **README** يقول: ما هذا، كيف أثبّته، مثال تشغيل، كيف أستشهد به.
:::

:::mistake
- `pip install` مباشرة في Python النظام بدل بيئة افتراضية: تعارض إصدارات بين المشاريع.
- مسارات مطلقة في الكود (`C:\Users\me\...`) تعمل على جهازك فقط. استخدم `pathlib` ومسارات نسبية لجذر المشروع.
- وحدة باسم يطابق مكتبة (`pandas.py`، `random.py`) تحجب المكتبة الحقيقية.
- `requirements.txt` بلا إصدارات، ويتذكّره صاحبه بعد سنة بـ«كان يعمل».
:::

:::code mode="script" expect="SystemExit"
import argparse
parser = argparse.ArgumentParser(prog="survey")
parser.add_argument("path")
parser.parse_args([])           # the required argument is missing → usage error, exit code 2
:::

:::research
مشروع بحثي قابل لإعادة الإنتاج: كود في حزمة، `pyproject.toml` وملف قفل، بيانات خام لا تُعدَّل،
سكربت/أمر واحد يعيد كل الجداول والرسوم (`make all` أو `survey run`)، و`CITATION.cff` للاستشهاد،
وأرشفة إصدار بـDOI عبر Zenodo عند النشر. وهذا ما تطلبه مجلات كثيرة الآن في «replication package».
:::

:::exercise id="ex-cli":::

:::deep_dive
**البناء والنشر:** `python -m build` يُنتج `dist/*.whl` و`dist/*.tar.gz` (sdist)، ثم
`twine upload dist/*` يرفعها إلى PyPI (جرّب أولًا على TestPyPI). أو مع uv: `uv build` ثم `uv publish`.
الـwheel أرشيف zip جاهز للتثبيت دون بناء، فيه كودك وملف `METADATA` مستخرج من `pyproject.toml`.
:::

:::sketchnote
```text
repo/ pyproject.toml · README · LICENSE · .gitignore · src/pkg/ · tests/ · data/ · outputs/
pyproject: [build-system] [project] name version requires-python dependencies [project.scripts] [tool.*]
python -m venv .venv → activate → pip install -e ".[dev]" → pytest      (or: uv sync / uv run)
CLI: argparse + def main(argv=None) + if __name__ == "__main__"
SemVer MAJOR.MINOR.PATCH → breaking.feature.fix        secrets never in Git
```
:::

:::cheatsheet
| الحاجة | الأمر / الكود |
|---|---|
| بيئة افتراضية | `python -m venv .venv` |
| تثبيت قابل للتعديل | `pip install -e ".[dev]"` |
| مع uv | `uv init`، `uv add pandas`، `uv sync`، `uv run` |
| قراءة TOML | `tomllib.loads(text)` / `tomllib.load(f)` (وضع `"rb"`) |
| CLI | `argparse.ArgumentParser()`، `add_argument`، `parse_args` |
| بناء ونشر | `python -m build`، `twine upload dist/*` |
:::

:::quiz id="q-exit":::

:::docs
- [Packaging Python projects (PyPA tutorial)](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [argparse tutorial](https://docs.python.org/3/howto/argparse.html)
- [Semantic Versioning](https://semver.org/)
:::
