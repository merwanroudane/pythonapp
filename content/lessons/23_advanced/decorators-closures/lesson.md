:::question
عشر دوال في مشروعك، وتريد أن تقيس زمن تنفيذ كل واحدة، أو تسجّل كل استدعاء، أو تعيد المحاولة عند
الفشل. نسخ الكود نفسه عشر مرات فكرة سيئة. **كيف تضيف سلوكًا إلى دالة دون أن تلمس كودها؟**
:::

:::theory title="الدوال objects من الدرجة الأولى"
في Python الدالة **object** كأي قيمة أخرى (first-class): يمكن **تخزينها** في متغير أو قائمة،
و**تمريرها** إلى دالة أخرى (كما في `sorted(xs, key=len)`)، و**إعادتها** من دالة. والدالة التي تأخذ
دالة أو تُعيد دالة تسمى **دالة عليا (higher-order function)**.

من هنا فكرتان:

- **الـclosure:** دالة معرَّفة داخل دالة أخرى، **تتذكر** متغيرات النطاق المحيط (Enclosing في LEGB) حتى
  بعد انتهاء الدالة الخارجية. تُخزَّن هذه المتغيرات في «خلايا» مرتبطة بالدالة (`__closure__`).
- **الـdecorator:** دالة تأخذ دالة وتُعيد دالة **غلافًا (wrapper)** تضيف سلوكًا قبلها أو بعدها. وصيغة
  `@deco` فوق التعريف اختصار لـ`f = deco(f)`.
:::

## الدوال كقيم

:::code mode="script"
def shout(text):
    return text.upper() + "!"


def whisper(text):
    return text.lower() + "..."


def greet(style, name):          # takes a function as an argument
    return style(f"Hello {name}")


for style in [shout, whisper]:   # functions stored in a list
    print(style.__name__, "→", greet(style, "Sara"))
:::

## Closures

:::code mode="script"
def make_counter():
    count = 0

    def increment():
        nonlocal count            # rebind the enclosing variable, not a new local one
        count += 1
        return count

    return increment


a = make_counter()
b = make_counter()
print(a(), a(), a(), b())
print(a.__closure__[0].cell_contents)     # the remembered value lives in a cell
:::

:::quiz id="q-closure":::

## أول decorator

:::code mode="script"
import time


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)          # call the original
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed * 1000:.2f} ms")
        return result

    return wrapper


@timer                          # same as: slow_sum = timer(slow_sum)
def slow_sum(n):
    return sum(i * i for i in range(n))


print(slow_sum(200_000))
print(slow_sum.__name__)        # 'wrapper'! the identity was lost
:::

:::animation id="anim-decorator":::

:::quiz id="q-sugar":::

## functools.wraps وdecorators بمعاملات

:::code mode="script"
import functools


def log_calls(prefix):                      # 1) takes the decorator's arguments
    def decorator(func):                    # 2) takes the function
        @functools.wraps(func)              #    keep __name__, __doc__
        def wrapper(*args, **kwargs):       # 3) replaces the function
            print(f"{prefix} {func.__name__}{args} {kwargs}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


@log_calls("[call]")
def area(w, h=1):
    """Rectangle area."""
    return w * h


print(area(3, h=4))
print(area.__name__, "|", area.__doc__)
:::

:::diagram kind="text" title="ثلاث طبقات"
   @log_calls("[call]")          log_calls("[call]")  ──► decorator
   def area(...): ...            decorator(area)      ──► wrapper
                                 area = wrapper
   area(3, h=4)  ──►  wrapper(3, h=4)  ──►  print(...)  ──►  original area(3, h=4)
:::

## Decorators جاهزة في المكتبة القياسية

:::code mode="script"
import functools


@functools.lru_cache(maxsize=None)          # memoization: remember results by arguments
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print(fib(80))
print(fib.cache_info())


class Circle:
    def __init__(self, r):
        self.r = r

    @property                               # a method read like an attribute
    def area(self):
        return round(3.14159 * self.r**2, 2)


print(Circle(2).area)
:::

:::mistake
- **نسيان `return result`** في الـwrapper: الدالة المغلّفة تُعيد `None` فجأة.
- **استدعاء الدالة بدل تمريرها:** `timer(slow_sum(10))` يمرّر **النتيجة** لا الدالة.
- **نسيان `*args, **kwargs`:** الغلاف يكسر أي دالة لها معاملات.
- **نسيان `nonlocal`** عند تعديل متغير الـclosure يرفع `UnboundLocalError`.
:::

:::code mode="script" expect="UnboundLocalError"
def make_counter():
    count = 0

    def increment():
        count += 1          # assignment makes count local → read before assignment
        return count

    return increment


make_counter()()
:::

:::research
في الكود البحثي تفيد الـdecorators في: **التخزين المؤقت** لحسابات مكلفة (`lru_cache` أو `joblib.Memory`
على القرص)، **تسجيل** المعاملات والزمن لكل تجربة، **التحقق** من المدخلات قبل التقدير. وستراها في كل
مكتبة: `@pytest.fixture` و`@st.cache_data` في Streamlit و`@app.get` في FastAPI و`@njit` في Numba.
:::

:::exercise id="ex-retry":::

:::deep_dive
تُطبَّق عدة decorators **من الأسفل إلى الأعلى**: `@a` فوق `@b` فوق `def f` تعني `f = a(b(f))`.
ويمكن أن يكون الـdecorator **class** لها `__call__`، ويمكن تزيين **class** كاملة (كما يفعل
`@dataclass` الذي يولّد `__init__` و`__repr__` و`__eq__`). ولا يحفظ الـclosure **قيمة** المتغير بل
**المتغير نفسه**، لذلك تُطبع `[2, 2, 2]` في `[lambda: i for i in range(3)]` عند الاستدعاء. الحل
`lambda i=i: i`.
:::

:::sketchnote
```text
functions are objects → store · pass · return
closure = inner function + remembered enclosing variables (nonlocal to rebind)
decorator = function(func) → wrapper        @deco  ≡  f = deco(f)
wrapper(*args, **kwargs): before → result = func(...) → after → return result
@functools.wraps(func) keeps __name__/__doc__     deco(args) → decorator → wrapper (3 layers)
built-in: @lru_cache · @property · @staticmethod · @classmethod · @dataclass
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| closure يعدّل متغيرًا | `nonlocal x` |
| decorator بسيط | `def deco(func): def wrapper(*a, **k): ...; return wrapper` |
| حفظ الهوية | `@functools.wraps(func)` |
| decorator بمعاملات | `def deco(arg): def decorator(func): ...` |
| تخزين النتائج | `@functools.lru_cache(maxsize=None)` |
| method كخاصية | `@property` |
:::

:::quiz id="q-exit":::

:::docs
- [Glossary: decorator](https://docs.python.org/3/glossary.html#term-decorator)
- [Function definitions (decorators)](https://docs.python.org/3/reference/compound_stmts.html#function-definitions)
- [functools](https://docs.python.org/3/library/functools.html)
:::
