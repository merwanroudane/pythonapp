:::question
كتبت في الـterminal `pip install pandas` ونجح التثبيت. ثم في الـnotebook كتبت
`import pandas` فظهر `ModuleNotFoundError: No module named 'pandas'`.
**هل كذب عليك pip؟**
:::

:::theory title="الـinterpreter والبيئة والمتغير PATH"
- **الـinterpreter** برنامج (`python.exe`) ينفّذ كود Python. يمكن أن توجد منه نسخ كثيرة على الجهاز.
- **البيئة (environment)** = interpreter + الحزم المثبتة له (في مجلد `site-packages`) + إعداداته.
  تثبيت حزمة يعني نسخها إلى `site-packages` لبيئة **واحدة**.
- عندما تكتب `python` في الـterminal، يبحث نظام التشغيل في المجلدات المذكورة في المتغير
  **PATH** بالترتيب، ويشغّل **أول** `python` يجده. لذلك قد يختلف ما يشغّله الـterminal عمّا يشغّله
  الـIDE أو الـnotebook.
- **الـvirtual environment** مجلد صغير يشير إلى interpreter أساسي لكنه يملك `site-packages`
  خاصًا به، فتبقى مكتبات كل مشروع معزولة عن غيره.
:::

:::concept
«Python» على جهازك ليس شيئًا واحدًا. قد توجد عدة **interpreters**: نسخة من python.org،
وأخرى من Anaconda، وثالثة داخل `.venv` لمشروع معيّن. **كل interpreter له مكتباته الخاصة**
(مجلد `site-packages`).

عندما تكتب `pip install` فالتثبيت يذهب إلى interpreter واحد فقط، وعندما يعمل الـnotebook
فهو يستخدم **kernel** مرتبطًا بـinterpreter قد يكون مختلفًا.
:::

:::diagram title="مشروعان، ثلاثة interpreters"
flowchart LR
    T["Terminal: pip install pandas"] --> P1["Python A (system)"]
    P1 --> S1["site-packages: pandas ✓"]
    NB["Notebook kernel"] --> P2["Python B (.venv)"]
    P2 --> S2["site-packages: no pandas ✗"]
    IDE["VS Code interpreter"] --> P3["Python C (conda)"]
:::

## اسأل Python نفسه

أفضل تشخيص هو أن تسأل الكود الذي يعمل: **من أنت، وأين تعيش؟**

:::code mode="script"
import sys

print("executable:", sys.executable)
print("version   :", sys.version.split()[0])
print("prefix    :", sys.prefix)
print("in a venv?:", sys.prefix != sys.base_prefix)
:::

:::rule
عند أي مشكلة `ModuleNotFoundError`: شغّل `import sys; print(sys.executable)` في المكان
الذي فشل فيه الـimport، ثم ثبّت المكتبة لذلك الـinterpreter تحديدًا:
`"<المسار>" -m pip install pandas`.
:::

## أوامر الـshell ليست كود Python

:::quiz id="q-where-pip":::

شغّل هذا «الكود» لترى ماذا يحدث عندما نخلط العالمين:

:::code mode="script" expect="syntax_error"
pip install pandas
:::

:::mistake
كتابة أوامر الـshell (`pip`، `cd`، `python file.py`) داخل REPL أو داخل ملف `.py`.
الـparser يرى كلمتين متتاليتين بلا عامل بينهما فيرفع `SyntaxError` قبل تنفيذ أي سطر.
:::

:::compare title="أين يُكتب كل أمر؟"
**Terminal / Shell**

```text
python --version
python -m pip install pandas
python analysis.py
```
|||
**Python (REPL / .py / cell)**

```python
import sys

print(sys.version)
import pandas as pd
```
|||
**Jupyter cell (magic)**

```text
%pip install pandas
%pwd
```
:::

:::tip
`python -m pip` أوضح من `pip` وحده: فهو يضمن أن pip يعمل مع **نفس** الـpython الذي
كتبته، خصوصًا عند وجود عدة interpreters.
:::

:::research
لكل مشروع بحثي بيئة مستقلة (`.venv` أو `uv`) وملف يوثق المكتبات ونسخها. هكذا يعيد
زميلك تشغيل التحليل بعد سنة ويحصل على النتائج نفسها.
:::

:::exercise id="ex-env":::

:::under_the_hood
`sys.prefix` هو مجلد البيئة الحالية، و`sys.base_prefix` هو مجلد تثبيت Python الأصلي.
عند إنشاء `.venv` يُنشأ مجلد خفيف يشير إلى الـinterpreter الأصلي لكنه يملك
`site-packages` خاصًا به؛ لذلك يختلف الـprefix عن الـbase_prefix داخل البيئة.
:::

:::cheatsheet
| السؤال | الأمر |
|---|---|
| أي Python يعمل؟ | `import sys; sys.executable` |
| ما نسخته؟ | `python --version` |
| ثبّت لهذا الـinterpreter | `python -m pip install <pkg>` |
| ثبّت من داخل notebook | `%pip install <pkg>` |
| هل أنا في venv؟ | `sys.prefix != sys.base_prefix` |
:::

:::quiz id="q-exit":::

:::docs
- [sys.executable](https://docs.python.org/3/library/sys.html#sys.executable)
- [venv — Creation of virtual environments](https://docs.python.org/3/library/venv.html)
- [Installing packages (Python Packaging User Guide)](https://packaging.python.org/en/latest/tutorials/installing-packages/)
:::
