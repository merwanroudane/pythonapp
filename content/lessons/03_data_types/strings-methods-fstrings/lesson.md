:::question
وصلك عمود أسماء من استبيان: `"  sara AHMED "` و`"Omar  "` و`"LINA"`. ثم طُلب منك تقرير
أرقامه بمنزلتين عشريتين ومحاذاة مرتبة. **ما الأدوات التي يعطيك إياها `str` لذلك؟**
:::

:::theory title="الـsequence وعدم القابلية للتغيير"
- **Sequence** مفهوم مجرد: مجموعة **مرتبة** من العناصر، لكل عنصر موضع، وتدعم `len()`
  والـindexing والـslicing و`in`. `str` و`list` و`tuple` و`range` كلها sequences، لذلك ما تتعلمه
  عن الـslicing هنا يعمل عليها جميعًا.
- الـ`str` **immutable** لأسباب تصميمية: يمكن استعمال النص **مفتاحًا في dict** (يجب ألا يتغير
  مفتاح بعد تخزينه)، ويمكن مشاركة النص نفسه بين أجزاء كثيرة من البرنامج بأمان.
- الثمن: كل «تعديل» ينشئ نصًا جديدًا. لبناء نص كبير من أجزاء كثيرة، اجمع الأجزاء في قائمة ثم
  استخدم `"".join(parts)` مرة واحدة بدل `+=` في حلقة طويلة.
:::

:::concept
الـ`str` **sequence** من الحروف: لكل حرف موضع (index) يبدأ من **0**، ويمكن العدّ من
النهاية بأرقام سالبة (`-1` آخر حرف). والنصوص **immutable**: لا يمكن تعديل حرف داخلها.
كل method مثل `upper()` أو `replace()` **تُعيد نصًا جديدًا** وتترك الأصل كما هو.
:::

:::syntax
```text
 index:   0   1   2   3   4   5
          P   y   t   h   o   n
 neg:    -6  -5  -4  -3  -2  -1

s[start:stop:step]     stop is excluded
s[1:4]   → "yth"       s[:2]  → "Py"      s[-3:] → "hon"
s[::2]   → "Pto"       s[::-1] → "nohtyP"
```
:::

:::quiz id="q-slice":::

:::code mode="script"
s = "Python"
print(s[0], s[-1])
print(s[1:4], s[:2], s[-3:])
print(s[::2], s[::-1])
print(len(s), "th" in s)
:::

:::warning
`s[10]` يرفع `IndexError`، لكن `s[2:10]` **لا** يرفع خطأ: الـslicing يقف بهدوء عند نهاية النص.
:::

## Methods حسب المهمة

:::compare title="اختر الأداة حسب ما تريد"
**تنظيف وحالة الأحرف**

- `strip()` / `lstrip()` / `rstrip()`
- `lower()` / `upper()` / `title()`
- `casefold()` للمقارنة بلا حساسية للحالة
- `removeprefix()` / `removesuffix()`
|||
**بحث وفحص**

- `find()` (يُعيد -1) و`index()` (يرفع خطأ)
- `count()`
- `startswith()` / `endswith()`
- `isdigit()` / `isalpha()` / `isspace()`
|||
**تحويل وتقسيم**

- `replace(old, new)`
- `split(sep)` → list
- `sep.join(items)` → str
- `splitlines()`
:::

:::code mode="script"
raw = "  sara AHMED  "
print(repr(raw.strip()))
print(raw.strip().title())

csv_line = "Sara,30,Algiers"
parts = csv_line.split(",")
print(parts)
print(" | ".join(parts))

print("data_2024.csv".endswith(".csv"), "report".find("x"))
:::

:::quiz id="q-upper":::

:::mistake
```python
name = "sara"
name.upper()        # the new string is created… and thrown away
print(name)         # sara
```
الإصلاح: `name = name.upper()`. القاعدة نفسها لكل methods الـ`str`.
:::

## f-strings: تنسيق للعرض

:::syntax
```text
f"{value:[fill][align][width][,][.precision][type]}"

f"{x:.2f}"    two decimals            f"{x:,.2f}"   thousands separator
f"{s:<12}"    left-align, width 12    f"{n:>6}"     right-align, width 6
f"{r:.1%}"    percentage              f"{x=}"       debug: prints  x=…
```
:::

:::change id="ch-format":::

:::code mode="script"
rows = [("Sara", 17.456), ("Omar", 9.5), ("Lina", 14.25)]
print(f"{'Name':<8}{'Score':>7}")
for name, score in rows:
    print(f"{name:<8}{score:>7.2f}")
:::

:::rule
التنسيق يحوّل القيمة إلى **نص للعرض**. احتفظ بالأرقام كأرقام في الحسابات، ولا تنسّقها إلا
في لحظة الطباعة أو التصدير.
:::

:::research
تنظيف الأسماء والفئات (`strip`، `casefold`، `replace`) خطوة أولى في أي dataset حقيقي:
`"Algiers "` و`"algiers"` و`"ALGIERS"` ثلاث فئات مختلفة بالنسبة للحاسوب حتى تنظّفها.
وستجد هذه الـmethods نفسها في pandas عبر `.str`.
:::

:::exercise id="ex-clean":::

:::deep_dive
`split()` بلا arguments تقسّم على **أي** مسافات متتالية وتتجاهل الأطراف:
`"  a   b ".split()` → `['a', 'b']`، بينما `"  a   b ".split(" ")` تُنتج عناصر فارغة.
و`casefold()` أقوى من `lower()` للمقارنات متعددة اللغات (مثل `"ß".casefold()` = `"ss"`).
:::

:::sketchnote
```text
STR = immutable sequence        s[i]  s[a:b]  (b excluded)  s[::-1]
method → NEW string             name = name.strip().title()
split(",")  str → list          ", ".join(list)  list → str
f"{x:,.2f}"  f"{s:<12}"  f"{r:.1%}"      format only for display
```
:::

:::cheatsheet
| المهمة | الكود |
|---|---|
| أول/آخر حرف | `s[0]`, `s[-1]` |
| جزء | `s[a:b]` |
| تنظيف | `s.strip()` |
| استبدال | `s.replace("a", "b")` |
| تقسيم / دمج | `s.split(",")`, `",".join(xs)` |
| منزلتان | `f"{x:.2f}"` |
| محاذاة | `f"{s:<10}"`, `f"{n:>6}"` |
:::

:::quiz id="q-exit":::

:::docs
- [String Methods](https://docs.python.org/3/library/stdtypes.html#string-methods)
- [Format Specification Mini-Language](https://docs.python.org/3/library/string.html#format-specification-mini-language)
- [f-strings (formatted string literals)](https://docs.python.org/3/reference/lexical_analysis.html#f-strings)
:::
