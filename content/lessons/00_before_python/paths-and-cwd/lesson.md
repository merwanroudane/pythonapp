:::question
كتبت `pd.read_csv("data.csv")` فظهر `FileNotFoundError`، مع أن الملف موجود أمامك
في المجلد نفسه الذي فيه ملف الكود. **كيف يمكن أن يكون الملف «موجودًا» و«غير موجود» معًا؟**
:::

:::theory title="نظام الملفات شجرة"
نظام الملفات مبني على شكل **شجرة (tree)**: في القمة **الجذر (root)** (`C:\` في Windows أو `/` في
Linux وmacOS)، وتحته مجلدات تتفرع إلى مجلدات أخرى، والملفات هي **الأوراق (leaves)**.

- **المسار (path)** هو الطريق من نقطة في الشجرة إلى عنصر آخر.
- **المسار المطلق** يبدأ دائمًا من الجذر، فهو عنوان كامل وفريد.
- **المسار النسبي** يبدأ من نقطة أخرى هي **current working directory** للـprocess، وهي قيمة
  يحتفظ بها نظام التشغيل لكل برنامج قيد التشغيل. لذلك: *المسار النسبي = cwd + المسار*.
- `..` تعني «المجلد الأب»، و`.` تعني «المجلد الحالي».
:::

قبل أن نكتب Python، نحتاج أن نفهم أين يعيش الكود. كثير من أخطاء المبتدئين ليست
أخطاء Python أصلًا، بل سوء فهم لـ**أين** يبحث البرنامج عن الملفات.

:::concept
كل برنامج يعمل (process) له **current working directory (cwd)**: مجلد «يقف فيه» أثناء
التنفيذ. عندما تعطيه مسارًا **نسبيًا** مثل `data.csv`، فهو يبحث عنه داخل هذا المجلد،
**وليس** داخل المجلد الذي يوجد فيه ملف `.py`.

أما المسار **المطلق** مثل `C:\Users\sara\project\data.csv` فيبدأ من جذر القرص، ولا
يتغير معناه مهما كان مجلد العمل.
:::

:::diagram title="المسار النسبي يُفسَّر انطلاقًا من cwd"
flowchart LR
    CWD["cwd = C:/Users/sara/project"] --> REL["data/raw.csv (relative)"]
    REL --> FULL["C:/Users/sara/project/data/raw.csv"]
    ABS["C:/Users/sara/project/data/raw.csv (absolute)"] --> FULL
:::

:::quiz id="q-relative":::

## تشريح المسار

:::syntax
```text
C:\Users\sara\project\data\raw.csv
└┬┘ └──────────┬─────────┘ └──┬───┘
anchor       parent          name
                              ├─ stem   = raw
                              └─ suffix = .csv
```

| الجزء | المعنى | في `pathlib` |
|---|---|---|
| anchor | بداية المسار (القرص في Windows) | `p.anchor` |
| parent | المجلد الذي يحتوي العنصر | `p.parent` |
| name | الاسم الكامل للعنصر الأخير | `p.name` |
| stem | الاسم بدون آخر امتداد | `p.stem` |
| suffix | آخر امتداد مع النقطة | `p.suffix` |
:::

شغّل الكود التالي. نستخدم `PureWindowsPath` حتى تكون النتيجة نفسها على أي نظام تشغيل.

:::code mode="script"
from pathlib import PureWindowsPath

p = PureWindowsPath(r"C:\Users\sara\project\data\raw.csv")

print("anchor :", p.anchor)
print("parent :", p.parent)
print("name   :", p.name)
print("stem   :", p.stem)
print("suffix :", p.suffix)
print("absolute?", p.is_absolute())
:::

والآن: أين يعمل الكود الذي تشغّله في هذه المنصة؟

:::code mode="script"
from pathlib import Path

print("cwd:", Path.cwd())
print("data.csv exists here?", Path("data.csv").exists())
:::

:::note
كل تشغيل في هذه المنصة يبدأ في مجلد مؤقت فارغ، لذلك `data.csv` غير موجود فيه. هذا بالضبط
ما يحدث عندما تشغّل script من مجلد مختلف عن مجلد بياناتك.
:::

:::animation id="anim-paths":::

## مشكلة الشرطة المائلة العكسية `\` في Windows

:::quiz id="q-escape":::

:::change id="ch-separators":::

:::mistake
```python
open("C:\new\results.csv")  # \n أصبحت newline، والمسار لم يعد كما كتبته
```
الرسالة قد تكون `OSError` أو `FileNotFoundError` ويبدو المسار في الرسالة غريبًا.
الإصلاح: `r"C:\new\results.csv"` أو `Path("C:/new/results.csv")`.
:::

:::warning
الـraw string لها حد مهم: لا يمكن أن تنتهي بشرطة عكسية واحدة. `r"C:\data\"` خطأ
syntax، لأن `\"` ما زالت تمنع إغلاق النص. استخدم `r"C:\data"` أو `pathlib`.
:::

:::research
في مشروع بحثي، اجعل كل المسارات مبنية من مجلد جذر واحد للمشروع، لا من مجلد العمل الحالي:

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "survey_2024.csv"
```

بهذا يعمل التحليل نفسه على جهازك وجهاز زميلك، سواء شُغّل من terminal أو من IDE.
:::

:::exercise id="ex-parts":::

:::deep_dive
`Path` مقابل `PurePath`: الـ`PurePath` تتعامل مع المسار كنص منظم فقط (تفكيك وتركيب)
ولا تلمس القرص. أما `Path` فتضيف عمليات حقيقية على الملفات: `exists()`، `read_text()`،
`mkdir()`، `glob()`. لذلك تصلح `PureWindowsPath` لتعليم مسارات Windows حتى على Linux.
:::

:::sketchnote
```text
RELATIVE  →  depends on cwd        data/raw.csv
ABSOLUTE  →  starts at the root    C:/Users/sara/project/data/raw.csv

"\n" inside "..."  = newline!      use  r"..."  or  "/"  or  pathlib
```
:::

:::cheatsheet
| أريد أن… | الكود |
|---|---|
| أعرف مجلد العمل | `Path.cwd()` |
| أبني مسارًا | `Path("data") / "raw.csv"` |
| أحوله إلى مطلق | `p.resolve()` |
| أفحص وجوده | `p.exists()` |
| أفككه | `p.parent`, `p.name`, `p.stem`, `p.suffix` |
:::

:::quiz id="q-exit":::

:::docs
- [pathlib — Object-oriented filesystem paths](https://docs.python.org/3/library/pathlib.html)
- [String and bytes literals (raw strings)](https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals)
:::
