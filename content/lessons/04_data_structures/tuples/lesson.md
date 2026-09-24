:::question
الإحداثيات `(36.75, 3.06)`، التاريخ `(2026, 9, 24)`، والسجل `("Sara", 30, "Algiers")`: قيم مرتبة
**لا يجب أن تتغير**. هل نحفظها في list يمكن لأي سطر أن يعدّلها بالخطأ؟
:::

:::theory title="الـtuple: sequence ثابتة"
الـ**tuple** بنية بيانات **مرتبة وغير قابلة للتعديل (immutable)**. مثل list تمامًا في الوصول
بالموضع والـslicing و`len` و`in`، لكن **لا يمكن** إضافة عنصر أو حذفه أو استبداله بعد إنشائه.

لماذا نريد بنية «أضعف» من list؟

- **الأمان:** بيانات لا يجب أن تتغير لا يمكن تغييرها بالخطأ.
- **المعنى:** tuple تقول للقارئ «هذا **سجل** ثابت، كل موضع فيه له معنى»، أما list فتقول «مجموعة
  عناصر متشابهة قد تكبر».
- **الـhashability:** tuple من عناصر ثابتة يمكن استخدامها **مفتاحًا في dict** وعنصرًا في set،
  والـlist لا.
- **الخفة:** أصغر قليلًا في الذاكرة من list بالعناصر نفسها.
:::

:::code mode="script"
point = (36.75, 3.06)
record = ("Sara", 30, "Algiers")
print(point[0], record[-1], record[1:], len(record))
print("Sara" in record, record.count(30), record.index("Algiers"))
:::

## الفاصلة هي التي تصنع الـtuple

:::quiz id="q-comma":::

:::change id="ch-comma":::

## Packing وunpacking

:::concept
- **Packing:** `record = "Sara", 30, "Algiers"` تجمع القيم في tuple تلقائيًا.
- **Unpacking:** `name, age, city = record` تفكّ الـtuple في أسماء، بشرط تطابق العدد.
- **Starred unpacking:** `first, *rest = (1, 2, 3, 4)` تجمع الباقي في list.
:::

:::code mode="script"
record = "Sara", 30, "Algiers"          # packing
name, age, city = record                 # unpacking
print(name, age, city)

first, *rest = (10, 20, 30, 40)
print(first, rest)

def stats(values):
    return min(values), max(values)      # return several values = return one tuple

low, high = stats([12, 7, 18])
print(low, high)
:::

:::animation id="anim-swap":::

## عدم قابلية التعديل وحدودها

:::mistake
```python
point = (36.75, 3.06)
point[0] = 40.0     # TypeError: 'tuple' object does not support item assignment
```
لتغيير قيمة أنشئ tuple جديدًا: `point = (40.0, point[1])`.
:::

:::code mode="script" expect="TypeError"
point = (36.75, 3.06)
point[0] = 40.0
:::

:::quiz id="q-inner":::

:::warning
tuple تحوي list **ليست hashable**: `hash(([1, 2], 3))` يرفع `TypeError: unhashable type: 'list'`،
ولا تصلح مفتاحًا في dict. الـtuple تكون مفتاحًا فقط إذا كانت **كل** عناصرها immutable.
:::

## tuple كمفتاح مركّب

:::code mode="script"
gdp_growth = {("DZ", 2023): 4.1, ("DZ", 2024): 3.8, ("TN", 2024): 1.4}
print(gdp_growth[("DZ", 2024)])
print(("TN", 2024) in gdp_growth)
:::

:::research
في بيانات panel (دولة × سنة) يكون المفتاح الطبيعي **tuple** `(country, year)`. وهذا ما تفعله pandas
مع `MultiIndex`. كما أن كثيرًا من الدوال الإحصائية تُعيد نتائجها كـtuple: `statistic, p_value = test(...)`.
:::

:::exercise id="ex-minmax":::

:::deep_dive
لسجلات بأسماء حقول واضحة استخدم **namedtuple** من `collections`: tuple عادية يمكن الوصول إلى
حقولها بالاسم أيضًا.

```python
from collections import namedtuple
City = namedtuple("City", ["name", "lat", "lon"])
algiers = City("Algiers", 36.75, 3.06)
print(algiers.lat, algiers[1])
```
وللسجلات القابلة للتعديل مع أنواع واضحة ستتعلم لاحقًا `dataclasses`.
:::

:::sketchnote
```text
TUPLE = ordered + IMMUTABLE        (36.75, 3.06)
the COMMA makes it:  (5) → int     (5,) → tuple     5, 6 → tuple
pack:   t = a, b, c                unpack:  a, b, c = t      first, *rest = t
swap:   a, b = b, a                return x, y  → one tuple
hashable (if items are) → dict key: gdp[("DZ", 2024)]
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| إنشاء | `(1, 2)`، `1, 2`، `(1,)` |
| من iterable | `tuple(xs)` |
| فكّ | `a, b = t` |
| الباقي | `first, *rest = t` |
| تبديل | `a, b = b, a` |
| سجل بأسماء | `collections.namedtuple` |
:::

:::quiz id="q-exit":::

:::docs
- [Tuples and Sequences — Python Tutorial](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences)
- [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple)
:::
