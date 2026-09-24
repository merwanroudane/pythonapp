:::question
`42` و`"Sara"` و`[42, "Sara"]` و`{"age": 42}`: كلها «بيانات». لكن هل هي من الصنف نفسه؟
**ما الفرق بين قيمة واحدة، وحاوية تجمع قيمًا كثيرة؟**
:::

:::theory title="نوع البيانات مقابل بنية البيانات"
**نوع البيانات (data type)** يحدد **ماذا تكون القيمة** وما العمليات الممكنة عليها: عدد صحيح؟
نص؟ منطقي؟ وكل object في Python له نوع واحد ثابت، تعطيه `type()`.

ونقسم الأنواع المدمجة إلى عائلتين كبيرتين:

1. **الأنواع الأساسية (basic / scalar types):** كل قيمة منها **قيمة واحدة** غير قابلة للتجزئة
   إلى عناصر: `int`، `float`، `complex`، `bool`، `NoneType`، ومعها `str` للنص.
2. **بنى البيانات (data structures / collections):** **حاويات** تجمع قيمًا كثيرة وتنظّمها بطريقة
   معيّنة تجعل عمليات محددة سريعة: `list`، `tuple`، `range`، `set`، `frozenset`، `dict`… وعناصرها
   قد تكون أنواعًا أساسية أو بنى أخرى.

القاعدة السريعة: إذا كان للقيمة **عناصر** يمكن عدّها بـ`len()` والمرور عليها، فهي بنية بيانات
(مع استثناء `str` الذي نشرحه أدناه).
:::

:::diagram title="خريطة الأنواع المدمجة في Python"
flowchart TD
    T["Built-in types"] --> B["Basic data types: one value"]
    T --> S["Data structures: many values"]
    B --> N["Numbers: int · float · complex"]
    B --> L["Logic: bool"]
    B --> E["Absence: None (NoneType)"]
    B --> X["Text: str"]
    S --> Q["Sequences: list · tuple · range"]
    S --> ST["Sets: set · frozenset"]
    S --> M["Mapping: dict"]
    S --> BY["Binary: bytes · bytearray"]
    S --> C["More: deque · Counter · defaultdict · namedtuple"]
:::

## الأنواع الأساسية

:::compare title="ست قيم مفردة"
**الأرقام**

- `int` — عدد صحيح: `42`، `-7`، `1_000_000`
- `float` — عدد حقيقي تقريبي: `3.14`، `1e-9`
- `complex` — عدد مركّب: `3 + 4j`
|||
**المنطق والغياب والنص**

- `bool` — منطقي: `True` أو `False`
- `NoneType` — قيمة واحدة فقط: `None` («لا قيمة»)
- `str` — نص: `"Sara"`، `'مرحبا'`
:::

:::code mode="script"
values = [42, 3.14, 3 + 4j, True, None, "Sara"]
for v in values:
    print(f"{v!r:<10} → {type(v).__name__}")
:::

## بنى البيانات

:::syntax
| البنية | مثال | مرتّبة؟ | قابلة للتعديل؟ | تكرار العناصر؟ | الوصول |
|---|---|---|---|---|---|
| `list` | `[3, 1, 3]` | نعم | نعم | مسموح | بالموضع `xs[0]` |
| `tuple` | `(3, 1, 3)` | نعم | لا | مسموح | بالموضع `t[0]` |
| `range` | `range(5)` | نعم | لا | لا | بالموضع |
| `set` | `{3, 1}` | لا | نعم | ممنوع | فحص العضوية `in` |
| `frozenset` | `frozenset({3, 1})` | لا | لا | ممنوع | فحص العضوية |
| `dict` | `{"a": 1}` | ترتيب الإدخال | نعم | مفاتيح فريدة | بالمفتاح `d["a"]` |
:::

:::code mode="script"
structures = [[3, 1, 3], (3, 1, 3), range(3), {3, 1}, {"a": 1}]
for s in structures:
    print(f"{type(s).__name__:<6} len={len(s)}  items={list(s)}")
:::

:::quiz id="q-which":::

## أين يقع str؟

:::concept
`str` حالة حدّية: تقنيًا هو **sequence غير قابلة للتعديل** من الحروف، فيمكنك كتابة `len("Sara")`
و`"Sara"[0]` والمرور على حروفه. لكن في الاستعمال الفعلي نعامل الاسم أو الجملة **كقيمة واحدة**،
ولا نغيّر حروفه واحدًا واحدًا. لذلك يُصنَّف مع الأنواع الأساسية في هذه المنصة، كما في أغلب المراجع.
:::

:::animation id="anim-types":::

## بعدٌ ثانٍ: قابلية التعديل (mutability)

:::theory title="كل نوع إما mutable أو immutable"
- **Immutable** (لا تتغير قيمته بعد إنشائه): `int`، `float`، `complex`، `bool`، `None`، `str`،
  `tuple`، `frozenset`، `range`. أي «تعديل» ينتج object جديدًا.
- **Mutable** (يمكن تعديله في مكانه): `list`، `set`، `dict`، `bytearray`.

كل الأنواع الأساسية immutable. أما بنى البيانات فمنها النوعان، وهذا ما يحدد مثلًا أيها يصلح
**مفتاحًا في dict** (الـimmutable فقط) وأيها يتأثر بالـaliasing.
:::

:::code mode="script"
x = 10
before = id(x)
x += 1
print("int   same object after change?", id(x) == before)

xs = [10]
before = id(xs)
xs.append(11)
print("list  same object after change?", id(xs) == before)
:::

:::quiz id="q-bool-int":::

## فحص النوع: type() وisinstance()

:::code mode="script"
value = True
print(type(value) is bool, type(value) is int)   # exact type only
print(isinstance(value, bool), isinstance(value, int))   # respects subclasses
print(isinstance(3.0, (int, float)))             # several types at once
:::

:::rule
استخدم `isinstance(x, T)` للسؤال «هل يتصرف x كـT؟» لأنه يحترم الأنواع الفرعية، واستخدم `type(x)` حين
تريد **عرض** النوع أو تحتاج النوع **بالضبط**. ولـNone استخدم دائمًا `x is None`.
:::

:::mistake
**الخلط بين الحاوية ومحتواها**: `[5]` ليست `5`. الأولى list فيها عنصر واحد، والثانية int. لذلك
`[5] + 1` يرفع `TypeError`، و`len(5)` يرفع `TypeError` لأن الـint لا عناصر له.
:::

:::code mode="script" expect="TypeError"
print(len(5))
:::

:::research
في جداول البيانات، **كل خلية** تحمل قيمة من نوع أساسي (رقم، نص، منطقي، مفقود)، و**العمود** أو
**الصف** بنية بيانات تجمع هذه القيم. تنظيف البيانات يبدأ دائمًا بسؤالين: ما نوع كل قيمة؟ وهل كل قيم
العمود من النوع نفسه؟ عمود أرقام فيه نص واحد `"N/A"` يتحول كله إلى نص.
:::

:::exercise id="ex-classify":::

:::sketchnote
```text
BASIC TYPES  = one value            DATA STRUCTURES = containers of values
int  float  complex                 list  tuple  range      (sequences)
bool  None  str                     set   frozenset         (sets)
                                    dict                    (mapping)
all basic types: immutable          structures: mutable (list set dict) or not (tuple…)
isinstance(x, (int, float))         x is None
```
:::

:::cheatsheet
| السؤال | الكود |
|---|---|
| ما نوعه؟ | `type(x).__name__` |
| هل هو رقم؟ | `isinstance(x, (int, float, complex))` |
| هل هو None؟ | `x is None` |
| كم عنصرًا فيه؟ (للحاويات) | `len(x)` |
| هل هو mutable؟ | جرّب: هل له `append` / `add` / تعديل بالمفتاح؟ |
:::

:::quiz id="q-exit":::

:::docs
- [Built-in Types](https://docs.python.org/3/library/stdtypes.html)
- [Data model — objects, values and types](https://docs.python.org/3/reference/datamodel.html#objects-values-and-types)
- [isinstance()](https://docs.python.org/3/library/functions.html#isinstance)
:::
