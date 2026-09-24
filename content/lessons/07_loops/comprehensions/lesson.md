:::question
ثلاثة أسطر لبناء قائمة: قائمة فارغة، حلقة، و`append`. هذا النمط يتكرر في كل مكان. **ألا توجد طريقة
تقول مباشرة «أريد قائمة من هذه القيم بعد تحويلها»؟**
:::

:::theory title="من صياغة المجموعات في الرياضيات إلى Python"
في الرياضيات نكتب مجموعة بوصف خاصيتها بدل سرد عناصرها: «{ x² | x ∈ ℕ ، x زوجي }». هذه تسمى
**set-builder notation**. استلهمت لغات برمجة كثيرة (Haskell أولًا ثم Python) هذه الفكرة فيما يسمى
**comprehension**: وصف **تصريحي** للمجموعة الناتجة («ماذا أريد») بدل وصف خطوات بنائها («كيف»).

الـcomprehension ليست سحرًا: هي **حلقة for مختصرة** تبني بنية جديدة. أجزاؤها بالترتيب:

1. **التعبير (expression):** ما يُضاف لكل عنصر.
2. **جملة `for`:** من أين تأتي العناصر.
3. **شرط `if` اختياري:** أي العناصر تُقبل (تصفية).
:::

:::syntax
```text
[ expression   for item in iterable   if condition ]
    what to add    where from            which ones (optional)

[x * 2 for x in xs]                 list      (ordered, duplicates)
{x * 2 for x in xs}                 set       (unique)
{k: v for k, v in pairs}            dict      (key → value)
(x * 2 for x in xs)                 generator (lazy, one pass)
```
:::

:::animation id="anim-equivalent":::

:::compare title="الحلقة والـcomprehension: المعنى نفسه"
**حلقة for**

```python
squares = []
for n in range(5):
    if n % 2 == 0:
        squares.append(n * n)
```
|||
**list comprehension**

```python
squares = [n * n for n in range(5) if n % 2 == 0]
```
أقصر، ويقول مباشرة إن النتيجة **قائمة**، ولا يوجد متغير مؤقت يتسرب خارجها.
:::

:::quiz id="q-read":::

:::code mode="script"
nums = [3, -2, 7, 0, -5]
print([n for n in nums if n > 0])            # filter
print([abs(n) for n in nums])                # transform
print([n if n > 0 else 0 for n in nums])     # transform with a choice
:::

:::quiz id="q-where-if":::

## dict وset وgenerator

:::change id="ch-forms":::

:::code mode="script"
grades = {"Sara": 14, "Omar": 8, "Lina": 17}
passed = {name: g for name, g in grades.items() if g >= 10}
print(passed)
total = sum(g for g in grades.values())      # generator: no list is built
print(total)
:::

:::rule
استخدم الـcomprehension عندما **تبني بنية جديدة** من أخرى بتحويل أو تصفية بسيطين. أما إذا احتاج
المنطق عدة أسطر، أو `try/except`، أو آثارًا جانبية مثل `print`، فالحلقة العادية أوضح.
:::

:::mistake
```python
[print(x) for x in xs]          # a list of None, built only for the side effect
[[r * c for c in range(9) if c % 2] for r in range(9) if r > 2 and r % 3]   # hard to read
```
الـcomprehension لبناء قيم، لا لتنفيذ أفعال. وإن احتجت قراءتها مرتين لتفهمها، فاكتبها حلقة.
:::

:::research
تنظيف أعمدة البيانات قبل pandas كثيرًا ما يكون comprehension واحدة: `[float(x) for x in col if x
not in ("", "NA")]`. وفي pandas ستجد الفكرة نفسها بشكل vectorized أسرع: `df[df["x"] > 0]` للتصفية
و`df["x"] * 2` للتحويل.
:::

:::exercise id="ex-clean":::

:::deep_dive
متغير الحلقة داخل الـcomprehension له **نطاق خاص**: لا يتسرب إلى الخارج (على عكس حلقة for التي
يبقى متغيرها بعد انتهائها). ويمكن تداخل أكثر من `for`: `[(r, c) for r in range(2) for c in range(3)]`
تُقرأ من اليسار كحلقتين متداخلتين، الخارجية أولًا.
:::

:::sketchnote
```text
[ expr  for x in xs  if cond ]      transform + filter → new list
{ expr  for x in xs }               set          { k: v for … }  dict
( expr  for x in xs )               generator: lazy, feed it to sum/max/any
if AFTER for   → filter (drop items)
a if c else b BEFORE for → transform (keep all)
long logic / side effects → use a normal loop
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| تحويل كل عنصر | `[f(x) for x in xs]` |
| تصفية | `[x for x in xs if ok(x)]` |
| قاموس من أزواج | `{k: v for k, v in pairs}` |
| قيم فريدة | `{x.lower() for x in words}` |
| مجموع بلا قائمة | `sum(x for x in xs)` |
:::

:::quiz id="q-exit":::

:::docs
- [List Comprehensions — Python Tutorial](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
- [Displays for lists, sets and dictionaries](https://docs.python.org/3/reference/expressions.html#displays-for-lists-sets-and-dictionaries)
:::
