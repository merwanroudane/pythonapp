:::question
list وtuple وset وdict تغطي معظم الحالات. لكن ماذا عن تسلسل من مليار رقم؟ أو طابور ضخم؟ أو عدّ
تكرارات آلاف الكلمات؟ **هل نكتب ذلك يدويًا في كل مرة؟**
:::

:::theory title="البنى المتخصصة"
إلى جانب البنى الأربع الأساسية، توفر Python بنى **متخصصة** لمشاكل محددة، بعضها مدمج في اللغة
وبعضها في الوحدة القياسية **`collections`**:

| البنية | من أين؟ | ما مشكلتها المحددة؟ |
|---|---|---|
| `range` | مدمجة | تسلسل أعداد بلا تخزين (lazy) |
| `bytes` / `bytearray` | مدمجة | بيانات ثنائية خام (ملفات، شبكة، صور) |
| `deque` | `collections` | إضافة وحذف سريعان من الطرفين |
| `Counter` | `collections` | عدّ تكرار العناصر |
| `defaultdict` | `collections` | قاموس ينشئ قيمة افتراضية للمفتاح الجديد |
| `namedtuple` | `collections` | tuple بأسماء حقول |

والقاعدة: قبل أن تكتب 10 أسطر لعدّ أو تجميع أو طابور، اسأل «هل توجد بنية جاهزة لذلك؟».
:::

## range: تسلسل بلا تخزين

:::quiz id="q-range":::

:::code mode="script"
import sys
r = range(0, 1_000_000, 5)
print(r, len(r), r[-1], list(r[:4]))
print("range bytes:", sys.getsizeof(r), "| list bytes:", sys.getsizeof(list(r)))
:::

## bytes وbytearray: بيانات ثنائية

:::code mode="script"
text = "مرحبا"
data = text.encode("utf-8")       # str → bytes (immutable)
print(type(data).__name__, data[:4], len(data))
buf = bytearray(data)             # mutable copy
buf[0] = 0xD9
print(type(buf).__name__, buf.decode("utf-8"))
:::

:::concept
`str` نص (code points)، و`bytes` بايتات خام **immutable**، و`bytearray` نسختها **mutable**. تقرأ
الملفات الثنائية (صور، PDF) كـbytes، والنصوص كـstr بعد الـdecode بترميز صحيح.
:::

## deque: طابور من الطرفين

:::code mode="script"
from collections import deque

queue = deque(["task1", "task2"])
queue.append("task3")            # add at the right
queue.appendleft("urgent")       # add at the left, O(1)
print(queue.popleft(), queue)    # take from the left, O(1)

recent = deque(maxlen=3)         # keeps only the last 3 items
for reading in [21, 23, 19, 25, 22]:
    recent.append(reading)
print(list(recent))
:::

## Counter: العدّ الجاهز

:::quiz id="q-counter":::

:::code mode="script"
from collections import Counter

answers = ["yes", "no", "yes", "maybe", "yes", "no"]
counts = Counter(answers)
print(counts)
print(counts["yes"], counts["unknown"])    # missing key → 0, no KeyError
print(counts.most_common(1))
:::

## defaultdict: قاموس بقيمة افتراضية

:::code mode="script"
from collections import defaultdict

grades = [("math", 14), ("physics", 12), ("math", 17)]
by_subject = defaultdict(list)
for subject, grade in grades:
    by_subject[subject].append(grade)      # no need to check if the key exists
print(dict(by_subject))
:::

:::mistake
```python
by_subject = {}
by_subject["math"].append(14)     # KeyError: 'math'
```
القاموس العادي لا ينشئ المفتاح تلقائيًا. الحلول: `by_subject.setdefault("math", []).append(14)`،
أو `defaultdict(list)` التي تنشئ القائمة الفارغة عند أول استعمال.
:::

:::code mode="script" expect="KeyError"
by_subject = {}
by_subject["math"].append(14)
:::

## namedtuple: tuple بأسماء

:::code mode="script"
from collections import namedtuple

Country = namedtuple("Country", ["code", "population_m", "gdp_growth"])
dz = Country("DZ", 45.6, 3.8)
print(dz.code, dz.gdp_growth, dz[1])
print(dz._asdict())
:::

:::animation id="anim-other":::

:::research
`Counter` هو أسرع طريق لجدول تكرارات متغير فئوي (frequency table) قبل pandas، و`defaultdict(list)`
هو نمط «group by» اليدوي. وستجد الفكرتين نفسيهما في pandas: `value_counts()` و`groupby()`.
:::

:::exercise id="ex-group":::

:::deep_dive
توجد بنى أخرى تستحق المعرفة: **`heapq`** لقائمة أولويات (أصغر عنصر أولًا بسرعة)، و**`array.array`**
لمصفوفة أرقام من نوع واحد أخف من list، و**`OrderedDict`** (أقل أهمية منذ أصبح dict يحفظ الترتيب في
Python 3.7). وللحسابات العددية الكبيرة ستنتقل إلى **`numpy.ndarray`** وللجداول إلى **`pandas.DataFrame`**:
بنى بيانات خارجية مصممة للتحليل.
:::

:::sketchnote
```text
range(a, b, s)  lazy numbers, O(1) memory      bytes / bytearray  raw binary
deque           fast both ends, maxlen         Counter            counting, most_common
defaultdict     auto default value per key     namedtuple         tuple with field names
before writing 10 lines: is there a ready-made structure?
```
:::

:::cheatsheet
| الحاجة | الأداة |
|---|---|
| أرقام متتالية بلا ذاكرة | `range(a, b, step)` |
| بيانات ثنائية | `bytes` / `bytearray` |
| طابور / آخر n عناصر | `deque`, `deque(maxlen=n)` |
| جدول تكرارات | `Counter(xs).most_common(k)` |
| تجميع حسب مفتاح | `defaultdict(list)` |
| سجل بأسماء حقول | `namedtuple` |
:::

:::quiz id="q-exit":::

:::docs
- [collections — Container datatypes](https://docs.python.org/3/library/collections.html)
- [range](https://docs.python.org/3/library/stdtypes.html#range)
- [Binary Sequence Types](https://docs.python.org/3/library/stdtypes.html#binary-sequence-types-bytes-bytearray-memoryview)
:::
