:::question
كتبت ملفًا نصيًا اسمه `analysis.py`. هو مجرد حروف. **ماذا يحدث بالضبط بين لحظة كتابة
`python analysis.py` وظهور النتيجة؟**
:::

محاضرة نظرية عن **آلة التنفيذ** نفسها. فهمها يفسّر أسئلة ستواجهها لاحقًا: لماذا يمنع خطأ صياغي
واحد تشغيل كل شيء؟ ما `__pycache__`؟ لماذا يتصرف الـnotebook بشكل مختلف عن الـscript؟

## 1. اللغة، الـinterpreter، والتطبيق

:::theory title="ثلاث كلمات تُخلط كثيرًا"
- **Python (اللغة):** مواصفات: ما الصياغة الصحيحة وما معناها.
- **Implementation (التطبيق):** برنامج حقيقي ينفّذ هذه المواصفات. الأشهر **CPython**، المكتوب
  بلغة C، وهو ما تحصل عليه من python.org وما تستخدمه هذه المنصة.
- **Interpreter executable:** الملف الذي تشغّله فعلًا (`python.exe` أو `python3`).

تطبيقات أخرى: **PyPy** (مع JIT وأسرع في الحلقات الطويلة)، **MicroPython** (للمتحكمات الدقيقة)،
**Pyodide** (Python داخل المتصفح عبر WebAssembly).
:::

## 2. مراحل التنفيذ في CPython

:::theory title="من النص إلى النتيجة"
1. **Tokenizer:** يقسّم النص إلى وحدات صغيرة (tokens): أسماء، أرقام، عوامل، أقواس، إزاحة.
2. **Parser:** يتحقق من الصياغة ويبني **AST** (Abstract Syntax Tree): شجرة تمثل بنية البرنامج.
   **هنا** يُكتشف `SyntaxError`، قبل تنفيذ أي شيء.
3. **Compiler:** يحوّل الـAST إلى **bytecode**: تعليمات بسيطة لآلة افتراضية، محفوظة في
   **code object**.
4. **Python Virtual Machine (PVM):** حلقة داخل CPython تقرأ تعليمات الـbytecode وتنفّذها
   واحدة تلو الأخرى، باستخدام **stack**. **هنا** تحدث الـruntime errors مثل `ZeroDivisionError`.
:::

:::diagram title="Pipeline التنفيذ"
flowchart LR
    S["source: analysis.py"] --> T["tokenizer → tokens"]
    T --> P["parser → AST"]
    P --> C["compiler → bytecode"]
    C --> V["Python Virtual Machine"]
    V --> R["result / output"]
    P -. "SyntaxError: nothing runs" .-> X(["stop"])
    V -. "runtime error: earlier lines already ran" .-> Y(["stop"])
:::

شاهد كل مرحلة على السطر `total = price * 2`:

:::code mode="script"
import ast
import dis
import io
import tokenize

source = "total = price * 2"

print("1) tokens:")
for tok in tokenize.generate_tokens(io.StringIO(source).readline):
    if tok.string.strip():
        print("  ", tokenize.tok_name[tok.type], repr(tok.string))

print("\n2) AST:")
print(ast.dump(ast.parse(source).body[0], indent=2))

print("\n3) bytecode:")
dis.dis(compile(source, "<demo>", "exec"))
:::

:::note
شكل الـbytecode الدقيق **يختلف بين نسخ Python**، وهو تفصيل داخلي لـCPython وليس جزءًا من
اللغة. المهم هو الفكرة: سطرك تحوّل إلى تعليمات بسيطة مثل «حمّل `price`»، «حمّل الثابت 2»،
«اضرب»، «خزّن في `total`».
:::

## 3. متى يظهر كل نوع من الأخطاء؟

:::quiz id="q-when":::

:::code mode="script" expect="syntax_error"
print("start")
if True print("inside")
:::

قارن مع خطأ **أثناء التنفيذ**: السطر الأول يعمل فعلًا، ثم يتوقف البرنامج عند الثاني.

:::code mode="script" expect="ZeroDivisionError"
print("start")
print(1 / 0)
print("never reached")
:::

:::compare title="Syntax error مقابل Runtime error"
**SyntaxError**

- يُكتشف في مرحلة الـparser.
- **لا يُنفَّذ أي سطر** من الملف.
- السبب: الشكل (قوس، `:`، علامة تنصيص، إزاحة).
|||
**Runtime error (exception)**

- يحدث في الـVM أثناء التنفيذ.
- الأسطر **قبله نُفّذت** وربما طبعت أو كتبت ملفات.
- السبب: المعنى (قسمة على صفر، مفتاح غير موجود، نوع غير مناسب).
:::

:::quiz id="q-pyc":::

## 4. طرق تشغيل Python

:::theory title="أربعة أوضاع"
- **REPL** (Read–Eval–Print Loop): اكتب `python` في الـterminal فيظهر `>>>`. كل سطر يُقرأ ويُنفَّذ
  ويُعرض ناتجه فورًا. ممتاز للتجربة السريعة.
- **Script:** `python analysis.py` ينشئ process جديدة، ينفّذ الملف من الأعلى إلى الأسفل مرة واحدة،
  ثم تنتهي وتختفي كل المتغيرات.
- **Module:** `python -m pip install pandas` أو `python -m pytest` يشغّل module باسمه من
  بيئة الـinterpreter الحالي.
- **Notebook (Jupyter):** مستند فيه خلايا؛ كل خلية تُرسل إلى **kernel** (process لـPython تبقى
  حية) فتشترك الخلايا في الذاكرة نفسها، ويمكن تشغيلها بأي ترتيب.
:::

:::quiz id="q-exit":::

## 5. أين تكتب الكود؟

:::theory title="Text editor، Code editor، IDE، Notebook"
| الأداة | ماذا تقدم | أمثلة |
|---|---|---|
| **Text editor** | تحرير نص فقط، وربما تلوين بسيط | Notepad، TextEdit |
| **Code editor** | تلوين، إكمال تلقائي، extensions، terminal مدمج | VS Code، Sublime Text |
| **IDE** | بيئة متكاملة: debugger، إدارة مشروع، refactoring، اختبارات | PyCharm، Spyder |
| **Notebook** | خلايا كود ونص ورسوم ونتائج في مستند واحد | JupyterLab، Google Colab |

الحدود بينها ليست صارمة: VS Code مع extensions يقترب من IDE، ويفتح notebooks أيضًا. الاختيار
حسب المهمة: notebook للاستكشاف، و`.py` في محرر أو IDE للخطوات التي يجب أن تعاد كما هي.
:::

:::mistake
**«الـnotebook يعمل، إذن الكود صحيح»**: قد يعتمد الـnotebook على خلية حُذفت أو شُغّلت بترتيب
مختلف، وما زالت نتيجتها في ذاكرة الـkernel. قبل مشاركة notebook: **Restart kernel & Run All**.
إن نجح، فهو صحيح فعلًا.
:::

:::research
قاعدة عملية لمشروع بحثي: استكشف في **notebook**، ثم انقل الخطوات المستقرة (القراءة، التنظيف،
التقدير) إلى ملفات **`.py`** تُشغَّل من الأعلى إلى الأسفل في process جديدة. هكذا تضمن أن النتائج
لا تعتمد على حالة مخفية في ذاكرة kernel.
:::

:::under_the_hood
الـVM في CPython **stack-based**: لحساب `price * 2` تدفع قيمة `price` إلى الـstack، ثم الثابت 2،
ثم تنفّذ تعليمة الضرب التي تسحب القيمتين وتدفع الناتج، ثم تخزّنه في الاسم `total`. منذ Python
3.11 أصبح الـinterpreter **متخصصًا تكيفيًا (adaptive)**: يستبدل بعض التعليمات العامة بنسخ أسرع
حسب الأنواع التي يراها أثناء التشغيل، وهذا من أسباب تحسن سرعة الإصدارات الحديثة.
:::

:::sketchnote
```text
source → tokens → AST → bytecode → VM → result
            └ SyntaxError here: NOTHING runs
                                    └ runtime errors here: earlier lines DID run
CPython (C, reference) · PyPy (JIT) · MicroPython · Pyodide (browser)
REPL >>>  ·  script (fresh process, top→bottom)  ·  -m module  ·  notebook (shared kernel state)
```
:::

:::cheatsheet
| المصطلح | المعنى |
|---|---|
| Token | أصغر وحدة في الكود |
| AST | شجرة بنية البرنامج |
| Bytecode | تعليمات للآلة الافتراضية |
| PVM | حلقة تنفيذ الـbytecode |
| `__pycache__/*.pyc` | bytecode مخزّن للـmodules |
| REPL | جلسة تفاعلية `>>>` |
| Kernel | process تنفّذ خلايا الـnotebook وتحفظ حالتها |
:::

:::docs
- [dis — Disassembler for Python bytecode](https://docs.python.org/3/library/dis.html)
- [ast — Abstract Syntax Trees](https://docs.python.org/3/library/ast.html)
- [Using Python — command line and environment](https://docs.python.org/3/using/cmdline.html)
- [JupyterLab: Notebooks](https://jupyterlab.readthedocs.io/en/stable/user/notebook.html)
:::
