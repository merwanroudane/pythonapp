:::question
في المسار السابق تعلمت الأنواع الأساسية: قيم مفردة. لكن البيانات الحقيقية مجموعات: درجات فصل
كامل، أسماء دول، جدول سكان. **لماذا تعطي Python أكثر من طريقة لتجميع القيم؟**
:::

:::theory title="ما بنية البيانات؟"
**بنية البيانات (data structure)** طريقة لتنظيم مجموعة من القيم في الذاكرة بحيث تصبح **عمليات
معينة** سهلة وسريعة. لا توجد بنية «أفضل» مطلقًا؛ كل بنية تحسّن شيئًا وتدفع ثمنًا في شيء آخر:

- **list**: مرتبة وقابلة للتعديل، ممتازة للإضافة في النهاية والوصول بالموضع، لكن البحث فيها بطيء.
- **tuple**: مرتبة وثابتة، مناسبة لـ«سجل» حقوله معروفة، وتصلح مفتاحًا في dict.
- **set**: بلا ترتيب وبلا تكرار، والبحث فيها سريع جدًا، لكن لا يمكن الوصول بالموضع.
- **dict**: من مفتاح إلى قيمة، والبحث بالمفتاح سريع جدًا.

اختيار البنية الصحيحة يجعل الكود **أقصر وأسرع وأوضح معنى** في آن واحد.
:::

:::syntax
| | `list` | `tuple` | `set` | `dict` |
|---|---|---|---|---|
| الكتابة | `[1, 2]` | `(1, 2)` | `{1, 2}` | `{"a": 1}` |
| الفارغة | `[]` | `()` | `set()` | `{}` |
| مرتّبة؟ | نعم | نعم | لا | ترتيب الإدخال |
| قابلة للتعديل؟ | نعم | لا | نعم | نعم |
| التكرار | مسموح | مسموح | ممنوع | مفاتيح فريدة |
| الوصول | `xs[i]` | `t[i]` | `x in s` | `d[key]` |
| سرعة `x in …` | O(n) بطيء | O(n) بطيء | O(1) سريع | O(1) على المفاتيح |
| تصلح مفتاحًا في dict؟ | لا | نعم* | لا | لا |

\* إذا كانت كل عناصرها hashable.
:::

:::diagram title="أسئلة القرار: أي بنية أختار؟"
flowchart TD
    Q1{"Do you look values up by a key/name?"} -- yes --> D["dict"]
    Q1 -- no --> Q2{"Must items be unique, order irrelevant?"}
    Q2 -- yes --> S["set"]
    Q2 -- no --> Q3{"Will the collection change?"}
    Q3 -- yes --> L["list"]
    Q3 -- no --> T["tuple"]
:::

:::code mode="script"
grades = [14, 9, 17, 14]                  # ordered, may repeat, will grow
point = (36.75, 3.06)                     # fixed record
subjects = {"math", "physics", "math"}    # unique
ages = {"Sara": 30, "Omar": 25}           # name → value

for s in (grades, point, subjects, ages):
    print(f"{type(s).__name__:<6} {s!r:<30} len={len(s)}")
:::

:::quiz id="q-choose-set":::

:::quiz id="q-empty":::

:::mistake
**`{}` ليست مجموعة فارغة.** هي dict فارغ، فإن كتبت `s = {}` ثم `s.add(1)` ظهر
`AttributeError: 'dict' object has no attribute 'add'`. المجموعة الفارغة: `s = set()`.
:::

:::code mode="script" expect="AttributeError"
s = {}
s.add(1)
:::

## البنى المتداخلة

:::concept
البنى يمكن أن تحتوي بنى أخرى. أشهر شكل في تحليل البيانات: **قائمة من القواميس**؛ كل قاموس
**صف** (سجل) وكل مفتاح **عمود**. هذا هو شكل JSON تقريبًا، ويتحول مباشرة إلى جدول pandas.
:::

:::code mode="script"
students = [
    {"name": "Sara", "age": 30, "courses": ["math", "stats"]},
    {"name": "Omar", "age": 25, "courses": ["physics"]},
]
print(students[0]["name"], students[0]["courses"][1])
print(len(students), "rows,", len(students[0]), "columns")
:::

:::research
عندما تصمم بيانات مشروعك (قبل pandas)، البنية تعكس المعنى: قائمة المشاهدات `list`، معرّفات فريدة
للمشاركين `set`، إعدادات النموذج `dict`، وإحداثيات أو (سنة، دولة) كمفتاح مركّب `tuple`:
`gdp[("DZ", 2024)]`.
:::

:::exercise id="ex-pick":::

:::sketchnote
```text
list   [ ]   ordered · mutable · duplicates      → a sequence that changes
tuple  ( )   ordered · FIXED · duplicates        → a record
set    { }   unordered · unique · fast `in`      → membership / dedupe
dict  {k:v}  key → value · fast lookup           → find by name
empty set = set()      {} = empty dict
```
:::

:::cheatsheet
| أريد… | البنية |
|---|---|
| تسلسلًا مرتبًا يكبر | `list` |
| سجلًا ثابتًا / مفتاحًا مركّبًا | `tuple` |
| عناصر فريدة / فحص وجود سريع | `set` |
| البحث بالاسم أو المفتاح | `dict` |
| جدولًا صغيرًا | `list` من `dict` |
:::

:::quiz id="q-exit":::

:::docs
- [Data Structures — Python Tutorial](https://docs.python.org/3/tutorial/datastructures.html)
- [TimeComplexity (Python Wiki)](https://wiki.python.org/moin/TimeComplexity)
:::
