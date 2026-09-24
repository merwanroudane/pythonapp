:::question
ملف سجلات حجمه 20 GB، وجهازك فيه 8 GB من الذاكرة. `lines = f.readlines()` سيفشل.
**كيف تمر على البيانات دون أن تحملها كلها في الذاكرة؟**
:::

:::theory title="التقييم الكسول مقابل التقييم الفوري"
- **Eager evaluation (فوري):** تُحسب كل القيم **الآن** وتُخزَّن: `[x * 2 for x in data]`. الذاكرة
  تنمو مع عدد العناصر، أي **O(n)**.
- **Lazy evaluation (كسول):** تُحسب القيمة **عند الطلب فقط**: `(x * 2 for x in data)`. الذاكرة
  شبه ثابتة، أي **O(1)**، ويمكن التعامل مع تدفقات (streams) لانهائية أو أكبر من الذاكرة.
- **بروتوكول التكرار (iterator protocol)** في Python اتفاق بسيط: الـiterable يملك method اسمها
  `__iter__()` تُعيد iterator، والـiterator يملك `__next__()` تُعيد العنصر التالي أو ترفع
  `StopIteration`. أي object يطبّق هذا الاتفاق يعمل مع `for`، وهذا مثال على **duck typing**: المهم
  ما يستطيع الـobject فعله، لا نوعه.
:::

:::concept
- **Iterable**: أي شيء يمكن المرور عليه: list، str، dict، ملف، `range`.
- **Iterator**: الـobject الذي يقوم بالمرور فعلًا؛ يتذكر أين وصل. `iter(x)` يعطيك iterator،
  و`next(it)` يعطيك العنصر التالي، وعند النهاية يرفع `StopIteration`.

حلقة `for` تفعل هذا كله نيابة عنك. والـ**generator** طريقة سهلة لصنع iterator بنفسك: دالة
فيها `yield` تُنتج القيم **واحدة واحدة عند الطلب (lazy)** بدل بناء قائمة كاملة.
:::

:::code mode="script" expect="StopIteration"
letters = ["a", "b"]
it = iter(letters)
print(next(it))
print(next(it))
print(next(it))     # StopIteration: nothing left
:::

:::syntax
```text
for x in items:            ≈      it = iter(items)
    body(x)                       while True:
                                      try:
                                          x = next(it)
                                      except StopIteration:
                                          break
                                      body(x)
```
هذا **conceptually equivalent** لما تفعله `for`، وليس الكود الحرفي في CPython.
:::

## Generators: yield يوقف الدالة ويستأنفها

:::quiz id="q-yield":::

:::animation id="anim-yield":::

:::compare title="return مقابل yield"
**`return`**

- تُنهي الدالة وتُغلق الـframe.
- قيمة واحدة (أو قائمة كاملة جاهزة).
- كل الحساب يحدث قبل أن تحصل على أي نتيجة.
|||
**`yield`**

- **توقف** الدالة وتحفظ حالتها (locals، الموضع).
- قيمة في كل مرة، عند الطلب.
- تبدأ بمعالجة أول قيمة فورًا، بذاكرة ثابتة تقريبًا.
:::

:::code mode="script"
def read_numbers(lines):
    for line in lines:
        line = line.strip()
        if line:
            yield float(line)

raw = ["3.5", "", "4", "  10 "]
total = 0
for x in read_numbers(raw):
    total += x
print(total)
:::

## الاستهلاك مرة واحدة

:::quiz id="q-exhaust":::

:::mistake
```python
values = (x * 2 for x in data)
print(max(values))
print(min(values))     # ValueError: min() iterable argument is empty
```
الـgenerator استُهلك في `max`. إن احتجت المرور أكثر من مرة، أنشئ قائمة: `values = [...]`.
:::

:::code mode="script" expect="ValueError"
data = [3, 1, 4]
values = (x * 2 for x in data)
print(max(values))
print(min(values))
:::

## الذاكرة: قائمة أم generator؟

:::code mode="script"
import sys
as_list = [n * n for n in range(1_000_000)]
as_gen = (n * n for n in range(1_000_000))
print("list     :", sys.getsizeof(as_list), "bytes")
print("generator:", sys.getsizeof(as_gen), "bytes")
print(sum(as_gen) == sum(as_list))
:::

:::rule
استخدم **generator expression** `(…)` عندما تمر على القيم مرة واحدة فقط وتمررها مباشرة إلى
`sum` أو `max` أو `for`. واستخدم **list** `[…]` عندما تحتاج `len`، أو indexing، أو المرور عدة مرات.
:::

:::research
قراءة ملف ضخم سطرًا سطرًا (`for line in open(path):`) هي iterator جاهز من Python. والـgenerators
تبني **pipelines** من مراحل صغيرة: قراءة ← تنظيف ← تصفية ← تجميع، كل مرحلة تمرر قيمة واحدة
في كل مرة. وستجد الفكرة نفسها في `pandas.read_csv(..., chunksize=...)` وفي Polars lazy API.
:::

:::exercise id="ex-countdown":::

:::under_the_hood
الـgenerator object يحتفظ بـ**frame** الدالة معلّقًا بين كل `next` والتالي: الـlocals وموضع
التنفيذ محفوظان. لهذا يرى المُتتبع (خطوة بخطوة) الدالة «تعود» إلى السطر نفسه. ويمكنك رؤية
الحالة: `inspect.getgeneratorstate(g)` تُعيد `GEN_CREATED` أو `GEN_SUSPENDED` أو `GEN_CLOSED`.
:::

:::sketchnote
```text
ITERABLE  →  iter()  →  ITERATOR  →  next() next() …  →  StopIteration
def f(): yield x      calling f() runs NOTHING, returns a generator
next(g)               run until the next yield, then pause
(x for x in data)     lazy, single pass        [x for x in data]  stored, reusable
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| iterator من iterable | `it = iter(xs)` |
| العنصر التالي | `next(it)` أو `next(it, default)` |
| generator function | `def g(): yield v` |
| generator expression | `(f(x) for x in xs)` |
| أول n قيم فقط | `itertools.islice(g, n)` |
:::

:::quiz id="q-exit":::

:::docs
- [Iterators — Python Tutorial](https://docs.python.org/3/tutorial/classes.html#iterators)
- [Generators — Python Tutorial](https://docs.python.org/3/tutorial/classes.html#generators)
- [Generator expressions](https://docs.python.org/3/reference/expressions.html#generator-expressions)
:::
