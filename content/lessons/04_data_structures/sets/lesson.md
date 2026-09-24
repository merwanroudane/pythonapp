:::question
قائمة 50,000 مشارك فيها أسماء مكررة. كم مشاركًا **فريدًا** لدينا؟ ومن شارك في الموجتين؟ ومن
انسحب؟ **أي بنية تجيب عن هذه الأسئلة بسطر واحد؟**
:::

:::theory title="المجموعة في الرياضيات وفي Python"
**المجموعة (set)** مفهوم رياضي أسسه Georg Cantor: تجمّع **عناصر مختلفة** لا ترتيب لها، والسؤال
الأساسي عنها «هل هذا العنصر **ينتمي** إليها؟».

وفي Python تُبنى الـset على **جدول تجزئة (hash table)** مثل مفاتيح dict تمامًا، والنتيجة:

- **لا تكرار:** إضافة عنصر موجود لا تغيّر شيئًا.
- **لا ترتيب ولا indexing:** لا يوجد `s[0]`.
- **فحص العضوية `x in s` سريع جدًا** (O(1) في المتوسط) مهما كبرت المجموعة.
- **العناصر يجب أن تكون hashable:** أرقام، نصوص، tuples ثابتة. لا يمكن وضع list داخل set.
:::

:::code mode="script"
s = {3, 1, 3, 2, 1}
print(s, len(s))              # duplicates vanish
s.add(4)
s.discard(10)                 # no error if missing
s.remove(1)                   # KeyError if missing
print(s, 2 in s, 10 in s)
print(set("banana"))          # unique letters
:::

:::quiz id="q-order":::

## عمليات المجموعات

:::diagram kind="text" title="A = {1, 2, 3, 4}   B = {3, 4, 5}"
        A                     B
   ┌──────────┬──────────┬──────────┐
   │  1   2   │   3  4   │    5     │
   └──────────┴──────────┴──────────┘
     A - B        A & B       B - A
   A | B = {1, 2, 3, 4, 5}      A ^ B = {1, 2, 5}
:::

:::syntax
| العملية | العامل | الـmethod | المعنى |
|---|---|---|---|
| الاتحاد | `a \| b` | `a.union(b)` | في أيٍّ منهما |
| التقاطع | `a & b` | `a.intersection(b)` | في الاثنين |
| الفرق | `a - b` | `a.difference(b)` | في a فقط |
| الفرق التماثلي | `a ^ b` | `a.symmetric_difference(b)` | في واحدة فقط |
| الاحتواء | `a <= b` | `a.issubset(b)` | كل a داخل b |
:::

:::quiz id="q-ops":::

:::change id="ch-ops":::

## السرعة: in على list مقابل set

:::code mode="script"
import timeit

ids_list = list(range(100_000))
ids_set = set(ids_list)
t_list = timeit.timeit(lambda: 99_999 in ids_list, number=200)
t_set = timeit.timeit(lambda: 99_999 in ids_set, number=200)
print(f"list: {t_list * 1000:.2f} ms   set: {t_set * 1000:.3f} ms")
:::

:::mistake
- `s = {}` ثم `s.add(1)`: `{}` **dict** فارغ، والمجموعة الفارغة `set()`.
- `{[1, 2], [3]}`: `TypeError: unhashable type: 'list'`؛ استخدم tuples: `{(1, 2), (3,)}`.
- الاعتماد على ترتيب الطباعة: الـset غير مرتبة، استخدم `sorted(s)` للعرض.
:::

:::code mode="script" expect="TypeError"
groups = {[1, 2], [3]}
:::

:::tip
إزالة التكرار **مع** الحفاظ على الترتيب: `list(dict.fromkeys(xs))`. أما `list(set(xs))` فتزيل
التكرار لكنها قد تغيّر الترتيب.
:::

:::research
عمليات المجموعات هي لغة **تتبّع العينة** في البحوث الطولية: من بقي (`&`)، من انسحب (`-`)، من انضم
(`-` بالاتجاه المعاكس)، ومعدل الانسحاب (attrition). وهي أيضًا أداة سريعة للتحقق من البيانات:
`set(df_a["id"]) - set(df_b["id"])` تكشف المعرّفات التي لن تجد مطابقة عند دمج جدولين.
:::

:::exercise id="ex-waves":::

:::deep_dive
**frozenset** هي نسخة immutable من set: لا `add` ولا `remove`، لكنها **hashable**، فيمكن
استخدامها مفتاحًا في dict أو عنصرًا داخل set أخرى: `{frozenset({"a", "b"}): 3}`. وتوجد أيضًا
**set comprehension**: `{w.lower() for w in words}` لبناء مجموعة كلمات فريدة بلا تمييز لحالة الأحرف.
:::

:::sketchnote
```text
SET = unordered · UNIQUE · hashable items · fast `x in s`
add  discard  remove(KeyError)        no s[0]
|  union     &  intersection     -  difference     ^  symmetric    <=  subset
dedupe: set(xs)        keep order: list(dict.fromkeys(xs))
empty: set()   ({} is a dict)         frozenset → immutable, hashable
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| إنشاء | `{1, 2}`، `set(xs)`، `set()` |
| إضافة / حذف | `s.add(x)`، `s.discard(x)` |
| عضوية | `x in s` |
| مشترك / فرق | `a & b`، `a - b` |
| عدد العناصر الفريدة | `len(set(xs))` |
| نسخة ثابتة | `frozenset(s)` |
:::

:::quiz id="q-exit":::

:::docs
- [Set Types — set, frozenset](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
- [Sets — Python Tutorial](https://docs.python.org/3/tutorial/datastructures.html#sets)
:::
