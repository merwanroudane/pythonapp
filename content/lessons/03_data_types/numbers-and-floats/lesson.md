:::question
حاسوب يحسب مليارات العمليات في الثانية… فكيف يخطئ في `0.1 + 0.2`؟
:::

:::theory title="كيف تُخزَّن الأرقام في الذاكرة؟"
- **`int`** في Python ذو **دقة غير محدودة (arbitrary precision)**: يكبر عدد الأرقام المخزّنة داخليًا
  حسب الحاجة، فـ`2 ** 1000` يُحسب بدقة كاملة. الثمن: العمليات على الأعداد الضخمة أبطأ.
- **`float`** يتبع معيار **IEEE 754 double precision**: **64 بت** مقسمة إلى 1 بت للإشارة،
  و11 بتًا للأس (exponent)، و52 بتًا للكسر (fraction). النتيجة: نحو **15 إلى 17 رقمًا عشريًا
  معنويًا**، ومدى يصل إلى حوالي `1.8e308`.
- كسر عشري بسيط مثل `0.1` هو في النظام الثنائي كسر **لا نهائي** (`0.0001100110011…`)، فيُقطع عند
  52 بتًا. هذا **خطأ التمثيل (representation error)**، وليس خطأً في Python، ويحدث في كل لغة تستخدم
  المعيار نفسه (C، Java، JavaScript، R…).

يمكنك رؤية حدود `float` على جهازك: `import sys; sys.float_info`.
:::

:::quiz id="q-float":::

## نوعان أساسيان

:::concept
- **`int`**: عدد صحيح بلا حد أقصى عمليًا: `-3`، `0`، `2**100`.
- **`float`**: عدد بفاصلة عشرية مخزَّن بتمثيل ثنائي **تقريبي**: `3.5`، `0.1`، `1e-9`.

أي عملية فيها `float` تُنتج `float`، والقسمة `/` تُنتج `float` دائمًا.
:::

:::code mode="script"
a = 7
b = 2.0
print(type(a), type(b))
print(type(a + 1), type(a + b), type(4 / 2))
print(1_000_000 * 3)   # underscores make big numbers readable
:::

:::quiz id="q-div":::

:::code mode="script"
print(7 / 2, 7 // 2, 7 % 2)
print(-7 // 2)   # floor → toward minus infinity
print(divmod(17, 5))
:::

:::warning
`//` تقرّب نحو **سالب ما لا نهاية** (floor)، لذلك `-7 // 2` تساوي `-4` وليس `-3`.
أما `int(-3.5)` فتقطع نحو **الصفر** وتعطي `-3`.
:::

## لماذا 0.1 + 0.2 ليست 0.3؟

:::concept
كما أن `1/3` لا يمكن كتابتها بدقة في النظام العشري (`0.333…`)، فإن `0.1` لا يمكن
كتابتها بدقة في **النظام الثنائي** الذي يستخدمه الحاسوب. يُخزَّن أقرب رقم ممكن، والفرق
الضئيل يظهر أحيانًا بعد العمليات.
:::

:::code mode="script"
print(0.1 + 0.2)
print(f"{0.1:.20f}")   # the value actually stored for 0.1
:::

:::change id="ch-compare":::

:::rule
لا تقارن أعداد float بـ`==` أبدًا تقريبًا. استخدم `math.isclose(a, b)`. وللمبالغ المالية
الدقيقة استخدم `decimal.Decimal` أو خزّن المبالغ كأعداد صحيحة (بالسنتيم مثلًا).
:::

## التحويل بين الأنواع (casting)

:::code mode="script"
print(int("42") + 1)
print(float("3.5") * 2)
print(int(3.99))       # truncates, does not round
print(round(3.5), round(4.5))   # banker's rounding: to the nearest even
:::

:::mistake
```python
age = input("Age? ")  # always a str!
print(age + 1)  # TypeError: can only concatenate str (not "int") to str
```
ما يأتي من `input()` أو من ملف CSV قد يكون **نصًا** يشبه رقمًا. حوّله صراحة:
`int(age) + 1`. وتوقّع `ValueError` إذا كان النص غير صالح (`int("3.7")` أو `int("abc")`).
:::

:::code mode="script"
print(int("3.7"))
:::

:::research
في البيانات الحقيقية تأتي الأرقام أحيانًا كنصوص: `"1,234.5"` أو `" 42 "` أو `"NA"`.
قبل أي تحليل: افحص الأنواع، نظّف النصوص، ثم حوّل. وعند مقارنة نتائج نموذجين إحصائيين
استخدم tolerance (`isclose`، `numpy.allclose`) لا `==`.
:::

:::exercise id="ex-prices":::

:::deep_dive
`round(2.5)` يعطي `2` و`round(3.5)` يعطي `4`: هذا **banker's rounding** (التقريب إلى
أقرب زوجي) لتقليل الانحياز في المجاميع الكبيرة. وقد يفاجئك `round(2.675, 2)` = `2.67` لأن
`2.675` مخزن فعلًا كـ`2.67499999…`.
:::

:::sketchnote
```text
int    exact, unlimited          7   -3   2**100
float  binary approximation      0.1 → 0.1000000000000000055…

/   → always float     7 / 2  = 3.5
//  → floor            -7 // 2 = -4
%   → remainder        7 % 2  = 1

compare floats → math.isclose(a, b)   never  a == b
```
:::

:::cheatsheet
| المهمة | الكود |
|---|---|
| نص → عدد صحيح | `int("42")` |
| نص → عشري | `float("3.5")` |
| عشري → صحيح (قطع) | `int(3.9)` → `3` |
| تقريب للعرض | `round(x, 2)` أو `f"{x:.2f}"` |
| مقارنة عشرية | `math.isclose(a, b)` |
| قسمة وباقي | `divmod(a, b)` |
:::

:::quiz id="q-exit":::

:::docs
- [Floating-Point Arithmetic: Issues and Limitations](https://docs.python.org/3/tutorial/floatingpoint.html)
- [Numeric types — int, float, complex](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)
- [math.isclose](https://docs.python.org/3/library/math.html#math.isclose)
:::
