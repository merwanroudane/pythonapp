:::question
`sorted(names, key=len, reverse=True)`: لماذا بعض القيم تُكتب مباشرة وبعضها باسم ومساواة؟
**وكيف تقبل `print` أي عدد من القيم؟**
:::

:::theory title="كيف تُمرَّر القيم؟ call by sharing"
اللغات تختلف في طريقة تمرير الـarguments:

- **Call by value** (مثل C للأنواع البسيطة): الدالة تستلم **نسخة**؛ تعديلها لا يؤثر في الأصل.
- **Call by reference** (مثل `&` في C++): الدالة تستلم **المتغير نفسه**؛ إعادة إسناده تغيّر متغير
  المستدعي.
- **Python: call by sharing (call by object reference)**: الـparameter اسم جديد مربوط **بالـobject
  نفسه** الذي مرّره المستدعي.

```python
def f(items):
    items.append(99)   # mutation → the caller SEES it (same object)
    items = [0]        # rebinding → only the local name moves; caller unaffected
```
لذلك: الدالة التي **تعدّل** list أو dict مُمرّرًا إليها تغيّر بيانات المستدعي. وضّح ذلك في اسمها
وتوثيقها، أو اعمل على نسخة.
:::

:::concept
- **Parameter**: الاسم الذي يظهر في **تعريف** الدالة: `def area(width, height)`.
- **Argument**: القيمة التي تُمرَّر عند **الاستدعاء**: `area(3, 4)`.

عند الاستدعاء يربط Python كل argument بـparameter: إما **بالموضع (positional)** أو
**بالاسم (keyword)**. وما لم يُمرَّر يأخذ **القيمة الافتراضية** إن وُجدت، وإلا يظهر `TypeError`.
:::

:::syntax
```python
def f(a, b=2, *args, c, d=4, **kwargs):
#     │  │     │     │  │     └─ extra keyword args → dict
#     │  │     │     └──┴─ keyword-only (after *args or a bare *)
#     │  │     └─ extra positional args → tuple
#     │  └─ has a default
#     └─ required positional-or-keyword
```
:::

:::animation id="anim-binding":::

:::quiz id="q-bind":::

:::code mode="script"
def greet(name, greeting="Hello", punct="!"):
    return f"{greeting}, {name}{punct}"

print(greet("Sara"))
print(greet("Omar", "Marhaba"))
print(greet("Lina", punct="?"))
print(greet(punct=".", name="Adam"))
:::

:::rule
الـkeyword arguments تجعل الاستدعاء **قابلًا للقراءة** (`plot(x, y, color="red")`) وتسمح
بتخطي القيم الافتراضية. استخدمها لكل parameter لا يتضح معناه من موضعه، خصوصًا القيم المنطقية:
`load(path, header=True)` أوضح من `load(path, True)`.
:::

## عدد متغير من القيم

:::quiz id="q-args":::

:::code mode="script"
def total(*numbers):
    return sum(numbers)

def tag(text, **attrs):
    extras = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    return f"<p {extras}>{text}</p>"

print(total(), total(1, 2, 3))
print(tag("hi", id="intro", lang="ar"))

values = [4, 5, 6]
print(total(*values))            # unpack a list into positional args
options = {"id": "x", "lang": "en"}
print(tag("ok", **options))      # unpack a dict into keyword args
:::

:::mistake
```python
def area(width, height): ...

area(3)               # TypeError: area() missing 1 required positional argument: 'height'
area(3, 4, 5)         # TypeError: area() takes 2 positional arguments but 3 were given
area(width=3, 4)      # SyntaxError: positional argument follows keyword argument
```
اقرأ رسالة `TypeError` بدقة: هي تذكر اسم الدالة واسم الـparameter المفقود أو عدد القيم.
:::

:::code mode="script" expect="TypeError"
def area(width, height):
    return width * height

print(area(3))
:::

:::warning
لا تستخدم قائمة أو قاموسًا كقيمة افتراضية (`def add(x, items=[])`): القيمة الافتراضية تُنشأ
**مرة واحدة** عند تعريف الدالة. هذا فخ كامل له محاضرة مستقلة تالية.
:::

:::research
الدوال التحليلية الجيدة تجعل الإعدادات keyword-only بقيم افتراضية معقولة:

```python
def bootstrap_ci(data, *, n_boot=999, level=0.95, seed=None):
    ...
bootstrap_ci(sample, n_boot=4999, seed=42)   # every setting is visible at the call site
```
:::

:::exercise id="ex-report":::

:::deep_dive
الـ`/` في التعريف تجعل ما قبلها **positional-only**: `def pow(base, exp, /)` لا تقبل
`pow(base=2, exp=3)`. كثير من built-ins هكذا، ويمكنك فحص أي دالة بـ
`inspect.signature(f)` لترى نوع كل parameter.
:::

:::sketchnote
```text
PARAMETER = name in def       ARGUMENT = value in the call
f(1, 2)          positional   → by order
f(b=2, a=1)      keyword      → by name
def f(a, b=2)    default      → used when missing
*args  → tuple   **kwargs → dict     f(*xs, **opts) → unpack
after *  → keyword-only
```
:::

:::cheatsheet
| الحاجة | التعريف |
|---|---|
| قيمة افتراضية | `def f(x, n=10)` |
| عدد متغير | `def f(*items)` |
| خيارات مسماة إضافية | `def f(**opts)` |
| إجبار الاسم | `def f(x, *, flag=False)` |
| تمرير قائمة كقيم | `f(*xs)` |
| تمرير dict كخيارات | `f(**opts)` |
:::

:::quiz id="q-exit":::

:::docs
- [More on Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions)
- [Function definitions (reference)](https://docs.python.org/3/reference/compound_stmts.html#function-definitions)
:::
