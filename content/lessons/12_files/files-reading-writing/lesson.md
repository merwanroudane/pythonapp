:::question
كل ما في المتغيرات يختفي عند انتهاء البرنامج. **كيف تحفظ النتائج، وتقرأ بيانات أعدّها غيرك، وتتبادل
الجداول مع Excel وR وStata؟**
:::

:::theory title="الملف والتيار (stream)"
**الملف** بايتات محفوظة على القرص الدائم باسم ومسار. للتعامل معه يطلب البرنامج من نظام التشغيل **فتحه**
فيحصل على **file object** يمثل تيارًا (stream) نقرأ منه أو نكتب إليه، ثم **نغلقه** لتحرير المورد والتأكد
أن كل ما كُتب وصل فعلًا إلى القرص.

- **الملف النصي (text mode):** Python يحوّل البايتات إلى `str` حسب **الترميز**. استخدم دائمًا
  `encoding="utf-8"`، وإلا اختار النظام ترميزه الافتراضي (قد يكون cp1252 على Windows) فتفسد العربية.
- **الملف الثنائي (binary mode `"b"`):** بايتات خام `bytes`: صور، PDF، ملفات مضغوطة.
- **صيغ منظمة:** **CSV** جدول نصي تفصله فواصل، و**JSON** بيانات متداخلة (قواميس وقوائم) بصيغة نصية.
:::

:::syntax
| الوضع | المعنى | إن لم يوجد الملف | إن وُجد |
|---|---|---|---|
| `"r"` | قراءة (الافتراضي) | `FileNotFoundError` | يُقرأ |
| `"w"` | كتابة | يُنشأ | **يُمسح** ثم يُكتب |
| `"a"` | إضافة للنهاية | يُنشأ | يُضاف إليه |
| `"x"` | إنشاء حصري | يُنشأ | `FileExistsError` |
| `+ "b"` | ثنائي (`"rb"`، `"wb"`) | | بايتات بدل نص |
:::

## الكتابة والقراءة مع `with`

:::code mode="script"
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("السطر الأول\n")
    f.write("second line\n")

with open("notes.txt", "a", encoding="utf-8") as f:
    f.write("third line\n")

with open("notes.txt", encoding="utf-8") as f:
    content = f.read()
print(content)

with open("notes.txt", encoding="utf-8") as f:
    for number, line in enumerate(f, start=1):   # line by line, memory friendly
        print(number, line.rstrip("\n"))
:::

:::animation id="anim-files":::

:::quiz id="q-mode":::

:::concept
`with` هو **context manager**: يفتح الملف عند الدخول ويضمن `f.close()` عند الخروج من الـblock، **حتى
لو حدث خطأ** في المنتصف. وللملفات الصغيرة توفر `pathlib` اختصارًا من سطر واحد: `Path(p).read_text()`
و`Path(p).write_text(...)`.
:::

## CSV

:::code mode="script"
import csv

rows = [{"name": "Sara", "city": "Oran", "age": 30}, {"name": "Omar", "city": "Algiers", "age": 25}]
with open("people.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "city", "age"])
    writer.writeheader()
    writer.writerows(rows)

with open("people.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row, type(row["age"]).__name__)
:::

:::warning
كل ما يُقرأ من CSV **نص**: `"30"` وليس `30`. حوّل الأعمدة الرقمية صراحة. ومرّر `newline=""` عند فتح
ملفات CSV حتى لا تظهر أسطر فارغة إضافية على Windows.
:::

## JSON

:::code mode="script"
import json

config = {"model": "OLS", "alpha": 0.05, "vars": ["gdp", "inflation"], "robust": True, "note": None}
text = json.dumps(config, ensure_ascii=False, indent=2)
print(text)

back = json.loads(text)
print(back == config, back["vars"][1])
:::

:::quiz id="q-json":::

:::compare title="Python مقابل JSON"
**Python**

`dict` · `list` · `str` · `int`/`float` · `True`/`False` · `None`
|||
**JSON**

`object {}` · `array []` · `string` · `number` · `true`/`false` · `null`

الـtuple يصبح array، ومفاتيح القاموس يجب أن تكون نصوصًا.
:::

:::mistake
- نسيان `encoding="utf-8"` ثم ظهور `UnicodeDecodeError` أو نص عربي مشوّه.
- فتح ملف بالوضع `"w"` لإضافة سطر: يمحو كل ما سبق. استخدم `"a"`.
- مسار نسبي خاطئ: `FileNotFoundError` لأن مجلد العمل ليس ما تظن (راجع محاضرة المسارات).
:::

:::code mode="script" expect="FileNotFoundError"
with open("missing_data.csv", encoding="utf-8") as f:
    print(f.read())
:::

:::research
اجعل البيانات الخام **للقراءة فقط**: لا تكتب أبدًا فوق `data/raw/`. اكتب النتائج في مجلد آخر
(`data/processed/`، `outputs/`) بأسماء واضحة. وللجداول الكبيرة ستستعمل pandas (`read_csv`،
`to_parquet`)، لكن الوحدتين `csv` و`json` تبقيان الأداة الأخف للملفات الصغيرة والإعدادات.
:::

:::exercise id="ex-csv":::

:::deep_dive
`f.read()` يحمّل الملف كله في الذاكرة، بينما `for line in f` يقرأ سطرًا سطرًا (iterator)، وهو ما
تحتاجه للملفات الضخمة. وللملفات الثنائية: `Path("img.png").read_bytes()[:8]` يعطيك «التوقيع» الذي يعرّف
صيغة الملف. ويمكنك كتابة context manager خاص بك بالـdecorator `contextlib.contextmanager`.
:::

:::sketchnote
```text
with open(path, mode, encoding="utf-8") as f:   → closes itself, even on errors
"r" read · "w" overwrite! · "a" append · "x" create-only · "b" binary
f.read() all · for line in f: streaming          Path(p).read_text() small files
csv.DictReader / DictWriter(newline="")          values arrive as STRINGS
json.dump(obj, f) / json.load(f)                 dumps / loads ↔ text
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| قراءة كاملة | `Path(p).read_text(encoding="utf-8")` |
| سطرًا سطرًا | `for line in open(p, encoding="utf-8"):` |
| إضافة | `open(p, "a", encoding="utf-8")` |
| CSV كقواميس | `csv.DictReader(f)` |
| حفظ JSON | `json.dump(obj, f, ensure_ascii=False, indent=2)` |
| قراءة JSON | `json.load(f)` |
:::

:::quiz id="q-exit":::

:::docs
- [Reading and Writing Files — Python Tutorial](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
- [csv — CSV File Reading and Writing](https://docs.python.org/3/library/csv.html)
- [json — JSON encoder and decoder](https://docs.python.org/3/library/json.html)
:::
