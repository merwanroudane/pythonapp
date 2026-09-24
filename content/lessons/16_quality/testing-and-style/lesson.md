:::question
الكود «يعمل» اليوم. بعد ثلاثة أشهر تعدّل سطرًا فينكسر حساب في مكان آخر دون أن تنتبه، ولا تفهم ما
كتبته أنت نفسك. **ما الذي يجعل الكود قابلًا للقراءة والثقة والتعديل بأمان؟**
:::

:::theory title="ثلاث طبقات للجودة"
- **القراءة (readability):** الكود يُقرأ أكثر مما يُكتب. أسماء واضحة، دوال قصيرة بمسؤولية واحدة،
  وأسلوب موحد (PEP 8) تفرضه أدوات آلية مثل **Ruff** (linter + formatter).
- **الصحة (correctness):** **الاختبارات الآلية** تثبت أن الدالة تعطي النتيجة المتوقعة، وتنبّهك فورًا
  عندما يكسر تعديل ما سلوكًا قديمًا (regression). هذه «شبكة أمان» تسمح بالتعديل بثقة.
- **القابلية للتشخيص (observability):** **logging** يسجل ما حدث ومتى وبأي مستوى خطورة، بدل `print`
  المتناثرة التي تُحذف ثم تحتاجها من جديد.

ويضيف **الـtype hints** و**الـdocstrings** طبقة توثيق تقرؤها الأدوات والبشر معًا.
:::

## الأسلوب: PEP 8 بإيجاز

:::compare title="قبل وبعد"
**صعب القراءة**

```python
def f(L,t):
  r=[]
  for x in L:
    if x>t:r.append(x*1.2)
  return r
```
|||
**واضح**

```python
def add_tax(prices: list[float], threshold: float) -> list[float]:
    """Apply 20% tax to prices above the threshold."""
    return [p * 1.2 for p in prices if p > threshold]
```
:::

:::quiz id="q-naming":::

:::rule
- `snake_case` للدوال والمتغيرات، `CapWords` للـclasses، `UPPER_CASE` للثوابت.
- 4 مسافات للإزاحة، ومسافة حول `=` و`+` و`==`، وسطر فارغ بين الدوال.
- دع **formatter** يرتّب الشكل آليًا (`ruff format`) و**linter** يكشف الأخطاء الشائعة (`ruff check`).
:::

## الاختبارات: assert ودوال test_

:::code mode="script"
def mean(values: list[float]) -> float:
    """Arithmetic mean. Raises ValueError on an empty list."""
    if not values:
        raise ValueError("mean of an empty list")
    return sum(values) / len(values)

def test_mean_basic():
    assert mean([2, 4, 6]) == 4

def test_mean_single():
    assert mean([7]) == 7

def test_mean_empty_raises():
    try:
        mean([])
    except ValueError:
        return
    raise AssertionError("expected ValueError")

for test in (test_mean_basic, test_mean_single, test_mean_empty_raises):
    test()
    print("PASSED", test.__name__)
:::

:::animation id="anim-tests":::

:::concept
أداة **pytest** تبحث تلقائيًا عن الملفات `test_*.py` والدوال `test_*` وتشغّلها كلها وتلخّص النتيجة،
وتعرض عند الفشل القيم الفعلية مقابل المتوقعة. الشكل الذي كتبناه هنا هو بالضبط ما يقرؤه pytest:
`assert` عادية داخل دوال تبدأ بـ`test_`. في مشروعك: `pip install pytest` ثم `pytest`.
:::

:::quiz id="q-test":::

## doctest: أمثلة الـdocstring كاختبارات

:::code mode="script"
import doctest

def celsius_to_f(c: float) -> float:
    """Convert Celsius to Fahrenheit.

    >>> celsius_to_f(0)
    32.0
    >>> celsius_to_f(100)
    212.0
    """
    return c * 9 / 5 + 32

doctest.run_docstring_examples(celsius_to_f, {"celsius_to_f": celsius_to_f}, verbose=True)
:::

## logging بدل print

:::code mode="script"
import logging
import sys

logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format="%(levelname)s | %(funcName)s | %(message)s"
)
log = logging.getLogger("analysis")

def load(rows):
    log.info("loaded %d rows", len(rows))
    bad = [r for r in rows if r is None]
    if bad:
        log.warning("%d missing rows dropped", len(bad))
    log.debug("this DEBUG line is hidden at level INFO")
    return [r for r in rows if r is not None]

print(load([1, None, 3]))
:::

:::mistake
- **اختبار يطبع ولا يتحقق:** `print(mean([2, 4]))` ليس اختبارًا؛ لا شيء يفشل إذا تغيرت النتيجة.
- **مقارنة float بـ`==` في الاختبارات:** استخدم `math.isclose` أو `pytest.approx`.
- **`except: pass` لإسكات خطأ في اختبار:** يجعل الاختبار ينجح دائمًا ولا يختبر شيئًا.
:::

:::code mode="script" expect="AssertionError"
import math

def test_float_sum():
    assert 0.1 + 0.2 == 0.3          # fails: use math.isclose instead

test_float_sum()
:::

:::research
في البحث التجريبي، اختبر **دوال التحويل** التي تمس البيانات: هل التنظيف يحافظ على عدد الصفوف
المتوقع؟ هل لا تبقى قيم سالبة لعمر؟ هل مجموع النسب يساوي 1؟ اختبارات صغيرة كهذه تمنع أخطاء صامتة كانت
ستصل إلى الجداول المنشورة.
:::

:::exercise id="ex-tests":::

:::deep_dive
الـ**type hints** لا تُفرض عند التشغيل؛ تستعملها أدوات مثل **mypy** أو **Pyright** لاكتشاف أخطاء الأنواع
**قبل** التشغيل (مثل تمرير `str` لدالة تنتظر `float`). ومقياس **coverage** يخبرك أي أسطر لم يمر بها أي
اختبار. و**pre-commit** يشغّل الـformatter والـlinter والاختبارات تلقائيًا قبل كل commit.
:::

:::sketchnote
```text
READABLE  PEP 8 · snake_case functions · CapWords classes · ruff format / ruff check
CORRECT   tests = functions test_*() with assert · edge cases · pytest runs them all
DOCUMENTED docstrings (+ doctest examples) · type hints (mypy / pyright)
OBSERVABLE logging levels DEBUG < INFO < WARNING < ERROR   instead of scattered print
```
:::

:::cheatsheet
| الحاجة | الكود / الأداة |
|---|---|
| تنسيق آلي | `ruff format .` |
| فحص الأخطاء الشائعة | `ruff check .` |
| اختبار | `def test_x(): assert f(1) == 2` |
| تشغيل الاختبارات | `pytest` |
| أمثلة كاختبارات | `doctest.testmod()` |
| تسجيل | `logging.getLogger(__name__).info(...)` |
:::

:::quiz id="q-exit":::

:::docs
- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [doctest — Test interactive Python examples](https://docs.python.org/3/library/doctest.html)
- [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [pytest documentation](https://docs.pytest.org/)
:::
