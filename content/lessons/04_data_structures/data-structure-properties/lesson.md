:::question
`[3, 1, 3]` و`(3, 1, 3)` و`{3, 1, 3}` تبدو متشابهة، لكن الأولى تقبل `append` والثانية لا، والثالثة
تُطبع `{1, 3}`. **ما «الخصائص» التي تميّز كل بنية عن الأخرى؟ وكيف تعرفها دون حفظ؟**
:::

:::theory title="ما خاصية النوع؟"
**خاصية النوع (property)** سلوك **مضمون** لكل قيمة من ذلك النوع: «كل list يمكن تعديلها»، «كل set لا
تحتوي تكرارًا». الخصائص لا تُحفظ كقائمة عشوائية؛ هي نتيجة **لتصميم** البنية داخليًا:

- الـlist **مصفوفة من المراجع** ← لها مواضع (مرتبة)، ويمكن تبديل أي موضع (mutable).
- الـset **جدول hash** ← لا مواضع (غير مرتبة)، ولا يمكن لعنصر أن يُخزَّن مرتين (بلا تكرار).
- الـtuple مثل list لكن **مُقفلة** ← مرتبة وثابتة، ولذلك يمكن حساب hash لها.

وتصف Python أغلب هذه الخصائص رسميًا في الوحدة **`collections.abc`** كـ«بروتوكولات»: `Iterable`،
`Sized`، `Sequence`، `MutableSequence`، `Set`، `Mapping`، `Hashable`…
:::

## الخصائص الإحدى عشرة

:::theory title="أ. خصائص البنية: الترتيب، التكرار، الوصول"
1. **مرتّبة (ordered):** لكل عنصر موضع ثابت، فيوجد «الأول» و«الثاني». الترتيب هنا يعني **حفظ
   الموضع**، لا «مرتبة تصاعديًا». `list` و`tuple` و`str` و`range` مرتبة، وdict يحفظ **ترتيب الإدخال**،
   وset **غير مرتبة**.
2. **تسمح بالتكرار (duplicates):** هل يمكن أن تظهر القيمة نفسها مرتين؟ نعم في sequences، ولا في set،
   ومفاتيح dict فريدة (أما قيمه فيمكن أن تتكرر).
3. **الوصول بـ[] (subscriptable):** بالموضع `xs[0]` في sequences، أو بالمفتاح `d["a"]` في mapping،
   ولا يوجد في set.
:::

:::theory title="ب. خصائص الهوية والذاكرة: التعديل والـhash"
4. **قابلية التعديل (mutability):** هل يتغير الـobject **نفسه** بعد إنشائه؟ list وset وdict وbytearray
   وdeque قابلة للتعديل؛ وكل الأنواع الأساسية وtuple وfrozenset وrange وbytes ثابتة.
5. **قابلية الـhash (hashability):** هل يمكن حساب رقم hash **ثابت** للقيمة؟ هذا شرط لتكون مفتاحًا في
   dict أو عنصرًا في set. القاعدة في الأنواع المدمجة: **القابل للتعديل ليس hashable**، والثابت
   hashable **إذا كانت عناصره كلها hashable**.
:::

:::theory title="ج. البروتوكولات: المرور، الطول، الكسل"
6. **قابلة للمرور (iterable):** يمكن استعمالها في `for`: كل البنى، وكذلك `str`، أما `int` فلا.
7. **لها طول (sized):** تعمل معها `len()`. كل البنى المخزّنة لها طول، أما الـgenerator فلا طول له.
8. **كسولة (lazy):** تحسب العناصر **عند الطلب** بدل تخزينها: `range` والـgenerators والـiterators.
:::

:::theory title="د. خصائص القيم: التجانس، المقارنة، القيمة المنطقية"
9. **تجانس العناصر:** **متجانسة (homogeneous)** إن كانت كل العناصر من نوع واحد، و**مختلطة
   (heterogeneous)** إن اختلفت. list وtuple تقبلان الخلط، أما str (حروف فقط) وbytes (أعداد 0–255)
   وrange (أعداد صحيحة) فمتجانسة بطبيعتها.
10. **قابلة للمقارنة بالترتيب (orderable):** هل تعمل `<` و`>`؟ نعم للأرقام الحقيقية والنصوص (أبجديًا)
    والـlists والـtuples (عنصرًا عنصرًا)، ولا لـcomplex وNone وdict. وفي set تعني `<` «مجموعة جزئية»!
11. **القيمة المنطقية (truthiness):** كل حاوية **فارغة** falsy، وكل حاوية فيها عناصر truthy.
:::

## الجدول الكامل

:::syntax
| النوع | فئته | قابل للتعديل | مرتّب | تكرار | الوصول بـ[] | hashable | iterable | len | كسول | `<` |
|---|---|---|---|---|---|---|---|---|---|---|
| `int` | أساسي | ✗ | — | — | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| `float` | أساسي | ✗ | — | — | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| `complex` | أساسي | ✗ | — | — | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| `bool` | أساسي | ✗ | — | — | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| `None` | أساسي | ✗ | — | — | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| `str` | أساسي (sequence) | ✗ | ✓ | ✓ | موضع | ✓ | ✓ | ✓ | ✗ | ✓ |
| `list` | sequence | ✓ | ✓ | ✓ | موضع | ✗ | ✓ | ✓ | ✗ | ✓ |
| `tuple` | sequence | ✗ | ✓ | ✓ | موضع | ✓* | ✓ | ✓ | ✗ | ✓ |
| `range` | sequence | ✗ | ✓ | ✗ | موضع | ✓ | ✓ | ✓ | ✓ | ✗ |
| `bytes` | sequence | ✗ | ✓ | ✓ | موضع | ✓ | ✓ | ✓ | ✗ | ✓ |
| `bytearray` | sequence | ✓ | ✓ | ✓ | موضع | ✗ | ✓ | ✓ | ✗ | ✓ |
| `deque` | sequence | ✓ | ✓ | ✓ | موضع | ✗ | ✓ | ✓ | ✗ | ✓ |
| `set` | set | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | subset |
| `frozenset` | set | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ | subset |
| `dict` | mapping | ✓ | إدخال | مفاتيح فريدة | مفتاح | ✗ | ✓ | ✓ | ✗ | ✗ |
| generator | iterator | — | ✓ | — | ✗ | ✓† | ✓ | ✗ | ✓ | ✗ |

\* tuple قابلة للـhash فقط إذا كانت كل عناصرها hashable. † بالهوية فقط (كل generator مختلف).
«—» تعني أن الخاصية لا تنطبق (لا عناصر، أو تتغير الحالة مع الاستهلاك).
:::

## افحص الخصائص بنفسك

اختر مثالًا أو اكتب أي قيمة، واضغط **افحص الخصائص**. يُقيَّم الكود داخل المشغّل المعزول.

:::property_lab
[1, "2", 3.5, None, True, "missing"]
:::

## الفحص البرمجي بدل الحفظ

:::code mode="script"
import collections.abc as abc

def describe(x):
    try:
        hash(x)
        hashable = True
    except TypeError:
        hashable = False
    return {
        "type": type(x).__name__,
        "mutable": isinstance(x, (abc.MutableSequence, abc.MutableSet, abc.MutableMapping)),
        "ordered": isinstance(x, abc.Sequence),
        "hashable": hashable,
        "sized": isinstance(x, abc.Sized),
        "iterable": isinstance(x, abc.Iterable),
    }

for value in ([3, 1], (3, 1), {3, 1}, {"a": 1}, "ab", range(3), 42):
    print(describe(value))
:::

:::quiz id="q-hash-tuple":::

:::under_the_hood
`isinstance(x, collections.abc.Hashable)` تسأل فقط «هل للنوع method اسمها `__hash__`؟»، ولا تفحص
المحتوى. لذلك تُرجع `True` للـtuple `(1, [2])` مع أن `hash((1, [2]))` يرفع `TypeError`. **الاختبار
الحقيقي هو استدعاء `hash()` نفسه.**

```python
import collections.abc as abc
t = (1, [2])
print(isinstance(t, abc.Hashable))   # True  (the type defines __hash__)
hash(t)                              # TypeError: unhashable type: 'list'
```
:::

:::animation id="anim-props":::

## العلاقة بين التعديل والـhash

:::quiz id="q-mutable-hash":::

:::concept
تخيّل قائمة `[1, 2]` استُخدمت مفتاحًا في dict، ثم أضفت إليها `3`: الـhash يتغير، والقاموس يبحث في
الخانة الخطأ، فيضيع المفتاح داخل الجدول. لذلك تفرض Python القاعدة: **ما يمكن تعديله لا يُحسب له
hash**. وإن احتجت «قائمة كمفتاح» فحوّلها إلى tuple، و«مجموعة كمفتاح» إلى frozenset.
:::

:::code mode="script" expect="TypeError"
index = {}
index[(36.75, 3.06)] = "Algiers"      # tuple key: fine
index[frozenset({"a", "b"})] = 1      # frozenset key: fine
print(index)
index[[36.75, 3.06]] = "Algiers"      # list key: TypeError
:::

## التحويل بين البنى: ماذا يُحفظ وماذا يضيع؟

:::syntax
| التحويل | الترتيب | التكرار | النتيجة |
|---|---|---|---|
| `list(x)` | يُحفظ | يُحفظ | قابلة للتعديل |
| `tuple(x)` | يُحفظ | يُحفظ | ثابتة، hashable |
| `set(x)` | **يضيع** | **يُزال** | عضوية سريعة |
| `frozenset(x)` | يضيع | يُزال | ثابتة، hashable |
| `sorted(x)` | ترتيب **جديد** | يُحفظ | list |
| `dict.fromkeys(x)` | يُحفظ | يُزال | مفاتيح فريدة بترتيب الظهور |
| `dict(zip(keys, values))` | يُحفظ | المفاتيح المكررة: الأخيرة تفوز | mapping |
:::

:::quiz id="q-convert":::

:::change id="ch-convert":::

:::mistake
- استخدام list مفتاحًا في dict أو عنصرًا في set: `TypeError: unhashable type: 'list'`.
- الاعتقاد أن `set` يحفظ ترتيب الإدخال، ثم تفاجؤ الترتيب في التقرير.
- الاعتقاد أن tuple «مجمّدة بالكامل»: ما بداخلها من lists يبقى قابلًا للتعديل.
- الخلط بين «مرتّبة (ordered)» و«مفروزة (sorted)»: `[3, 1, 2]` مرتبة (لها مواضع) لكنها غير مفروزة.
:::

:::research
اختيار البنية بخصائصها يمنع أخطاء صامتة في التحليل: معرّفات المشاركين في **set** تضمن عدم التكرار،
ومفتاح الـpanel **tuple** `(id, wave)` ثابت وقابل للـhash، وقائمة المشاهدات **list** تحفظ ترتيب الزمن.
وعند تحويل عمود إلى `set` لعدّ القيم الفريدة تذكّر أنك خسرت الترتيب والتكرار عمدًا.
:::

:::exercise id="ex-matrix":::

:::sketchnote
```text
STRUCTURE   ordered · duplicates · access by [] (position / key / none)
IDENTITY    mutable?  → hashable only if immutable (and contents hashable)
PROTOCOLS   iterable (for) · sized (len) · lazy (range, generators)
VALUES      homogeneous vs mixed · orderable (<) · truthiness (empty = False)
test, don't memorise:  hash(x) · len(x) · isinstance(x, collections.abc.Sequence)
ordered ≠ sorted       set(x) loses order+dups     dict.fromkeys(x) keeps order
```
:::

:::cheatsheet
| السؤال | الفحص |
|---|---|
| قابلة للـhash؟ | `hash(x)` (ترفع TypeError إن لم تكن) |
| لها طول؟ | `isinstance(x, collections.abc.Sized)` |
| مرتبة بمواضع؟ | `isinstance(x, collections.abc.Sequence)` |
| قابلة للتعديل؟ | `isinstance(x, (abc.MutableSequence, abc.MutableSet, abc.MutableMapping))` |
| كسولة؟ | `isinstance(x, collections.abc.Iterator)` أو `range` |
| فريدة مع الترتيب | `list(dict.fromkeys(xs))` |
:::

:::quiz id="q-exit":::

:::docs
- [collections.abc — Abstract Base Classes for Containers](https://docs.python.org/3/library/collections.abc.html)
- [Glossary: hashable, mutable, immutable, iterable, sequence](https://docs.python.org/3/glossary.html)
- [Built-in Types](https://docs.python.org/3/library/stdtypes.html)
:::
