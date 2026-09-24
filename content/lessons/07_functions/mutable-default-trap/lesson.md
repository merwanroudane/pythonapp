:::question
دالة بسيطة تضيف عنصرًا إلى قائمة وتُعيدها. في الاستدعاء الأول تعمل، وفي الثاني تظهر عناصر
من الاستدعاء السابق. **كيف «تتذكر» دالة ما حدث في استدعاء انتهى؟**
:::

:::theory title="زمن التعريف مقابل زمن الاستدعاء"
في Python، `def` **statement تُنفَّذ** مثل أي سطر آخر: عند الوصول إليها يُنشأ **function object**
ويُربط بالاسم. في تلك اللحظة (**definition time**) تُحسب تعابير القيم الافتراضية مرة واحدة وتُخزَّن
في `f.__defaults__`.

أما **جسم الدالة** فيُنفَّذ من جديد في كل استدعاء (**call time**)، وينشئ في كل مرة frame جديدًا
بـlocals جديدة. الفرق بين هذين الزمنين هو أصل الفخ: ما يُكتب بعد `=` في سطر `def` ينتمي إلى زمن
التعريف، وما يُكتب داخل الجسم ينتمي إلى زمن الاستدعاء.
:::

:::quiz id="q-trap":::

:::concept
التعبير الذي يلي `=` في `def add(item, bucket=[])` يُحسب **مرة واحدة**، لحظة تنفيذ سطر
`def`، وتُخزَّن نتيجته مع الدالة نفسها (في `add.__defaults__`). كل استدعاء لا يمرر `bucket`
يأخذ **الـobject نفسه**. مع الأنواع immutable لا مشكلة، أما القائمة فتعديلها يبقى.
:::

:::animation id="anim-trap":::

:::code mode="script"
def add(item, bucket=[]):
    bucket.append(item)
    return bucket

print(add.__defaults__)
add(1)
add(2)
print(add.__defaults__)   # the default object itself has changed
:::

:::change id="ch-fix":::

:::rule
**لا تستخدم object قابلًا للتعديل (list, dict, set) كقيمة افتراضية.** استخدم `None` وأنشئ
الـobject داخل الدالة:

```python
def add(item, bucket=None):
    if bucket is None:
        bucket = []
    ...
```
:::

:::warning
لماذا `is None` وليس `if not bucket:`؟ لأن قائمة فارغة **يمررها المستدعي عمدًا** falsy
أيضًا، فستستبدلها الدالة بقائمة جديدة وتضيع إضافاتك إليها.
:::

:::research
الفخ نفسه يظهر في إعدادات التحليل: `def fit(data, options={}):` ثم تعديل `options` داخل الدالة
يسرّب الإعدادات من نموذج إلى النموذج التالي، فتتغير النتائج حسب **ترتيب** الاستدعاءات.
هذا النوع من الأخطاء يكسر قابلية إعادة الإنتاج بصمت.
:::

:::exercise id="ex-fix":::

:::deep_dive
أحيانًا يُستغل هذا السلوك عمدًا كـcache بسيط (`def f(x, _cache={})`)، لكنه أسلوب غامض؛
الأوضح `functools.lru_cache`. وفي `dataclasses` يمنعك Python من هذا الفخ: `items: list = []`
يرفع `ValueError`، والصحيح `field(default_factory=list)`.
:::

:::sketchnote
```text
def f(x, items=[]):     default created ONCE, at def time
    items.append(x)     → shared by every call  ✗

def f(x, items=None):   ✓
    if items is None:
        items = []      → fresh list per call
```
:::

:::cheatsheet
| القيمة الافتراضية | آمنة؟ |
|---|---|
| `0`, `""`, `None`, `()` | نعم (immutable) |
| `[]`, `{}`, `set()` | لا — استخدم `None` |
| `datetime.now()` | تُحسب مرة واحدة أيضًا! |
:::

:::quiz id="q-exit":::

:::docs
- [Default Argument Values — Python Tutorial](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values)
- [dataclasses.field(default_factory=...)](https://docs.python.org/3/library/dataclasses.html#dataclasses.field)
:::
