:::question
10,000 سطر نصي فيها تواريخ ومعرّفات وأرقام هواتف مكتوبة بأشكال مختلفة. `split` و`find` لا تكفي.
**كيف تصف «شكل» ما تبحث عنه، لا قيمته؟**
:::

:::theory title="لغة صغيرة لوصف الأنماط"
**التعبير النمطي (regular expression, regex)** نص قصير يصف **نمطًا**: «أربعة أرقام ثم شرطة ثم رقمان»
بدل قيمة محددة مثل `2024-03`. الفكرة جاءت من نظرية اللغات الشكلية (Stephen Kleene، خمسينيات القرن
العشرين)، وصارت أداة في كل لغة برمجة ومحرر نصوص تقريبًا.

يتكون النمط من:

- **حروف عادية** تطابق نفسها: `cat`.
- **فئات (classes)** تطابق حرفًا واحدًا من نوع: `\d` رقم، `\w` حرف أو رقم أو `_`، `\s` مسافة،
  `[aeiou]` واحد من هذه، `[^0-9]` أي شيء ليس رقمًا، `.` أي حرف.
- **مُكمِّمات (quantifiers)** تحدد التكرار: `*` صفر أو أكثر، `+` واحد أو أكثر، `?` اختياري،
  `{3}` ثلاث مرات، `{2,4}` من 2 إلى 4.
- **مرتكزات (anchors):** `^` بداية النص، `$` نهايته، `\b` حدّ كلمة.
- **مجموعات `( )`** تحدد ما تريد **استخراجه**.
:::

:::syntax
| النمط | المعنى | يطابق |
|---|---|---|
| `\d{4}` | أربعة أرقام | `2024` |
| `[A-Z]\d+` | حرف كبير ثم أرقام | `A17` |
| `\w+@\w+\.\w+` | بريد إلكتروني مبسّط | `sara@lab.org` |
| `^\s+\|\s+$` | مسافات في الطرفين | |
| `(\d+)-(\d+)` | مجموعتان من الأرقام | `12-45` ← `('12', '45')` |
| `(?P<year>\d{4})` | مجموعة مسماة | `m["year"]` |
:::

## الدوال الأساسية في `re`

:::code mode="script"
import re

text = "Survey wave 2 (2024): n=350, response rate 61.5%"
m = re.search(r"\d{4}", text)            # first match or None
print(m.group(), m.start(), m.end())

print(re.findall(r"\d+(?:\.\d+)?", text))  # all numbers, decimals included
print(re.sub(r"\s+", " ", "too    many   spaces"))
print(re.split(r"[,;]\s*", "Oran, Algiers;Setif"))
:::

:::quiz id="q-findall":::

## المجموعات: استخراج الأجزاء

:::code mode="script"
import re

line = "2024-03-15 ID=A17 score=14.5"
m = re.search(r"(?P<date>\d{4}-\d{2}-\d{2}) ID=(?P<id>\w+) score=(?P<score>[\d.]+)", line)
print(m.groups())
print(m["id"], float(m["score"]))
print(m.groupdict())
:::

:::quiz id="q-greedy":::

:::rule
- اكتب الأنماط دائمًا بـ**raw strings**: `r"\d+"`.
- ابدأ بنمط بسيط واختبره على أمثلة حقيقية، ثم أضف التعقيد تدريجيًا.
- إن كان `str.split` أو `startswith` أو `in` يكفي، فهي أوضح وأسرع من الـregex.
:::

:::mistake
- `re.match` لا تبحث في كل النص: تطابق **من البداية فقط**. للبحث في أي مكان استخدم `re.search`.
- نسيان أن `re.search` قد تُعيد `None`، ثم `m.group()` ترفع `AttributeError`.
- `.` تطابق أي حرف؛ لمطابقة نقطة حقيقية اكتب `\.`.
:::

:::code mode="script" expect="AttributeError"
import re
m = re.search(r"\d{4}", "no year here")
print(m.group())
:::

:::research
الـregex أداة يومية لتنظيف النصوص: توحيد أشكال التواريخ، استخراج رموز البلدان أو الشركات، حذف
المسافات الزائدة، وإخفاء البيانات الشخصية (أرقام هواتف أو معرّفات) قبل مشاركة البيانات. وستجدها في
pandas عبر `df["col"].str.extract(r"...")` و`str.replace(..., regex=True)`.
:::

:::exercise id="ex-parse":::

:::deep_dive
`re.compile(pattern)` ينشئ object نمط يمكن إعادة استعماله بسرعة في حلقة. والـflags تغيّر السلوك:
`re.IGNORECASE` لتجاهل حالة الأحرف، و`re.MULTILINE` لجعل `^` و`$` تعمل على كل سطر، و`re.VERBOSE`
لكتابة نمط طويل على عدة أسطر مع تعليقات. وانتبه: بعض الأنماط المتداخلة مثل `(a+)+` قد تستغرق وقتًا
هائلًا على نصوص معينة (catastrophic backtracking).
:::

:::sketchnote
```text
\d digit · \w word char · \s space · . any · [abc] one of · [^0-9] not
*  0+   +  1+   ?  optional   {m,n}  between      ^ start  $ end  \b word edge
( ) capture    (?P<name> ) named    (?: ) group without capture
re.search first · re.findall all · re.sub replace · re.split
r"raw strings"   greedy .+  vs  lazy .+?     search may return None!
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| هل يوجد؟ | `re.search(p, s) is not None` |
| كل التطابقات | `re.findall(p, s)` |
| استبدال | `re.sub(p, new, s)` |
| تقسيم بعدة فواصل | `re.split(r"[,;]\s*", s)` |
| مجموعة مسماة | `m["name"]` مع `(?P<name>...)` |
| تجاهل حالة الأحرف | `re.search(p, s, re.IGNORECASE)` |
:::

:::quiz id="q-exit":::

:::docs
- [Regular Expression HOWTO](https://docs.python.org/3/howto/regex.html)
- [re — Regular expression operations](https://docs.python.org/3/library/re.html)
:::
