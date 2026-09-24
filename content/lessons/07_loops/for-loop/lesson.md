:::question
لديك 10,000 سطر من البيانات. لن تكتب 10,000 سطر كود. **كيف تقول لـPython «افعل هذا
لكل عنصر»؟**
:::

:::theory title="التكرار المحدد ونمط المُراكِم"
- **التكرار المحدد (definite iteration)**: عدد الدورات معروف من المجموعة التي نمر عليها. هذا ما
  تفعله `for`، على عكس **التكرار غير المحدد** (`while`) الذي يعتمد على شرط.
- كثير من اللغات تمر على **المواضع**: `for (i = 0; i < n; i++) … a[i]`. أما Python فتمر على
  **العناصر** مباشرة: `for x in a`. هذا تجريد أعلى يقلل أخطاء الـindex.
- **نمط المُراكِم (accumulator pattern)** هو أشهر استخدام للحلقات: ابدأ بقيمة ابتدائية (`total = 0`،
  `count = 0`، `result = []`)، ثم حدّثها في كل دورة، واقرأ النتيجة بعد الحلقة. ستراه في الجمع والعدّ
  والتصفية وبناء القوائم.
:::

:::concept
الـ`for` في Python لا تعدّ أرقامًا بل **تمر على عناصر**: تأخذ من الـ**iterable**
(قائمة، نص، `range`، ملف…) عنصرًا تلو الآخر، وتربط كل عنصر باسم (**loop variable**)،
ثم تنفّذ الجسم المُزاح. عندما تنتهي العناصر تخرج الحلقة من تلقاء نفسها.
:::

:::diagram title="دورة for"
flowchart LR
    I["iterable: [12, 5, 8]"] --> N{"next item?"}
    N -- yes --> B["p = item → run body"]
    B --> N
    N -- no more --> E(["continue after the loop"])
:::

:::syntax
```python
for name in iterable:  # name is re-bound on every iteration
    body  # indented = repeated
after_loop()  # runs once, when items are exhausted
```
:::

:::animation id="anim-sum":::

## المرور على أنواع مختلفة

:::code mode="script"
for letter in "Sara":
    print(letter, end=" ")
print()

scores = {"math": 17, "physics": 14}
for subject, mark in scores.items():
    print(subject, "→", mark)
:::

## range: عندما تحتاج أرقامًا

:::quiz id="q-range":::

:::code mode="script"
print(list(range(5)))
print(list(range(2, 10, 3)))
for i in range(3):
    print("attempt", i)
:::

:::rule
`range(stop)` يعطي **stop عنصرًا** تمامًا: من `0` إلى `stop - 1`. «النهاية غير مشمولة»
هي القاعدة نفسها في الـslicing: `s[0:3]` ثلاثة حروف.
:::

## enumerate: العنصر وموقعه معًا

:::code mode="script"
names = ["Sara", "Omar", "Lina"]
for i, name in enumerate(names, start=1):
    print(f"{i}. {name}")
:::

:::tip
بدل `for i in range(len(names)): name = names[i]` استخدم `enumerate`: أقصر، وأوضح،
وبلا خطر الخطأ في الـindex.
:::

## break وcontinue وelse

:::code mode="script"
for n in [4, 8, 15, 16, 23]:
    if n % 2 == 0:
        continue        # skip even numbers
    print("first odd:", n)
    break               # stop at the first odd one
:::

:::quiz id="q-else":::

:::mistake
**تعديل القائمة أثناء المرور عليها**:

```python
nums = [1, 2, 2, 3]
for n in nums:
    if n == 2:
        nums.remove(n)
print(nums)  # [1, 2, 3] — one 2 survived!
```
الحذف يزيح العناصر فيتخطى الـiterator بعضها. أنشئ قائمة جديدة بدلًا من ذلك:
`[n for n in nums if n != 2]`.
:::

:::code mode="script"
nums = [1, 2, 2, 3]
for n in nums:
    if n == 2:
        nums.remove(n)
print(nums)
:::

:::research
حلقة على ملفات مجلد كامل هي نمط بحثي يومي:

```python
from pathlib import Path

for csv_file in sorted(Path("data/raw").glob("*.csv")):
    print("processing", csv_file.name)
```
ومع الجداول الكبيرة ستتعلم لاحقًا أن عمليات NumPy وpandas الـvectorized أسرع كثيرًا من
حلقة Python على كل صف.
:::

:::exercise id="ex-scan":::

:::under_the_hood
`for x in obj` تستدعي `iter(obj)` للحصول على **iterator**، ثم `next()` مرة بعد مرة حتى
يرفع `StopIteration`؛ عندها تخرج الحلقة بهدوء. هذا **iterator protocol** هو سبب عمل
`for` مع القوائم والنصوص والملفات والـgenerators بالطريقة نفسها.
:::

:::sketchnote
```text
for item in iterable:      take next → bind name → run body → repeat
    ...
range(3)       → 0 1 2          (stop excluded)
enumerate(xs)  → (0, x0) (1, x1) ...
break          → leave the loop now
continue       → skip to the next item
for … else     → runs only if NO break happened
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| كل عنصر | `for x in items:` |
| أرقام 0..n-1 | `for i in range(n):` |
| العنصر وموقعه | `for i, x in enumerate(items):` |
| قائمتان معًا | `for a, b in zip(xs, ys):` |
| مفاتيح وقيم | `for k, v in d.items():` |
| إيقاف مبكر | `break` |
:::

:::quiz id="q-exit":::

:::docs
- [for Statements — Python Tutorial](https://docs.python.org/3/tutorial/controlflow.html#for-statements)
- [range](https://docs.python.org/3/library/stdtypes.html#range)
- [enumerate](https://docs.python.org/3/library/functions.html#enumerate)
:::
