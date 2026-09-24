:::question
كيف تكتب نصًا يحتوي علامة تنصيص، مثل `It's`، إذا كانت علامات التنصيص نفسها هي التي
تحدد بداية النص ونهايته؟
:::

:::theory title="الـliteral والمحددات وحرف الهروب"
- **الـliteral** طريقة لكتابة قيمة ثابتة مباشرة في الكود: `42` literal لعدد، و`"hi"` literal لنص.
- علامات التنصيص **محددات (delimiters)**: تخبر الـtokenizer أين يبدأ النص وأين ينتهي، وليست جزءًا
  من القيمة المخزّنة.
- **حرف الهروب (escape character)** `\` حرف «خاص» يغيّر معنى الحرف الذي يليه: `\n` لا تعني
  «شرطة ثم n» بل حرف سطر جديد واحد. الفكرة موروثة من لغة C وتستعملها لغات كثيرة.
- هناك دائمًا فرق بين **التمثيل (representation)** كما يُكتب في الكود (`repr`) و**العرض
  (display)** كما يراه المستخدم (`str` / `print`).
:::

:::concept
الـ**string literal** هو نص تكتبه في الكود فيصنع منه Python object من نوع `str`.
علامات التنصيص **ليست جزءًا من القيمة**، بل حدود لها. لذلك يحتاج Python طريقة ليعرف
أين ينتهي النص، وطريقة لكتابة حروف خاصة داخله: هذه هي الـ**escape sequences**.
:::

## أربع طرق لكتابة string

:::code mode="script"
a = 'single quotes'
b = "double quotes"
c = "It's easy"            # مزدوجة من الخارج، فتصبح ' حرفًا عاديًا
d = """triple quotes
can span
several lines"""

print(a)
print(b)
print(c)
print(d)
:::

:::rule
اختر العلامة الخارجية التي **لا** تظهر داخل النص: `"It's"` أو `'He said "hi"'`.
واترك الـescaping للحالات التي يحتوي فيها النص النوعين معًا.
:::

## Escape sequences

:::syntax
| تكتب في الكود | يصبح داخل النص | الاستخدام |
|---|---|---|
| `\n` | سطر جديد newline | فصل الأسطر |
| `\t` | مسافة tab | محاذاة بسيطة |
| `\\` | شرطة عكسية واحدة `\` | المسارات |
| `\'` | علامة `'` | داخل `'...'` |
| `\"` | علامة `"` | داخل `"..."` |
:::

:::quiz id="q-len":::

:::code mode="script"
s = "col1\tcol2\nvalue1\tvalue2"
print(s)
print("length:", len(s))
:::

## ما تراه مقابل ما هو موجود

:::change id="ch-print-repr":::

:::concept
`print(s)` يعرض النص **للبشر**: الـnewline يصبح سطرًا جديدًا فعلًا.
`repr(s)` يعرض النص **للمبرمج**: كما يُكتب في الكود، فترى `'\n'` صريحة.
عندما تكتب اسم متغير في آخر خلية Notebook، ترى الـ`repr`.
:::

جرّب ذلك في Notebook mode: آخر سطر expression، فيُعرض الـ`repr` تلقائيًا.

:::code mode="notebook"
s = "line 1\nline 2"
print(s)
s
:::

:::mistake
```python
msg = 'It's broken'
```
`SyntaxError: unterminated string literal`: العلامة `'` بعد `It` أغلقت النص، فبقي
`s broken'` بلا معنى. الإصلاح: `"It's broken"` أو `'It\'s broken'`.
:::

:::code mode="script" expect="syntax_error"
msg = 'It's broken'
print(msg)
:::

:::warning
الـraw string `r"..."` لا تستطيع أن تنتهي بشرطة عكسية واحدة: `r"C:\folder\"` خطأ syntax.
ولأن `r` تلغي كل escapes، لا يمكن كتابة newline بـ`\n` داخلها.
:::

:::exercise id="ex-quote":::

:::deep_dive
توجد escapes أخرى: `\r` (carriage return)، `\0`، و`\u0627` لكتابة حرف Unicode برقمه
(`"\u0627"` هو «ا»). وفي Python 3.12+ يعطي escape غير معروف مثل `"\d"` تحذير
`SyntaxWarning`، وهو سبب إضافي لاستخدام raw strings مع الـregex: `r"\d+"`.
:::

:::sketchnote
```text
SOURCE CODE        VALUE IN MEMORY      print()     repr()
"a\nb"         →   a ⏎ b (3 chars)   →  a        →  'a\nb'
                                        b
r"a\nb"        →   a \ n b (4 chars) →  a\nb     →  'a\\nb'
```
:::

:::cheatsheet
| الحالة | الكتابة الأنسب |
|---|---|
| نص فيه `'` | `"It's"` |
| نص فيه `"` | `'Say "hi"'` |
| نص فيه النوعان | `"""It's "ok" """` أو escaping |
| عدة أسطر | `"""..."""` أو `\n` |
| مسار Windows / regex | `r"C:\data"` أو `r"\d+"` |
:::

:::quiz id="q-exit":::

:::docs
- [String and bytes literals](https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals)
- [repr()](https://docs.python.org/3/library/functions.html#repr)
:::
