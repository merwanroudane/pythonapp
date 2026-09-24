:::quiz id="q-box":::

:::theory title="نموذج البيانات: كل شيء object"
في Python **كل قيمة object**، ولكل object ثلاث صفات (Python Data Model):

1. **الهوية (identity):** ثابتة طوال حياته، وتعطيها `id()`؛ `is` يقارنها.
2. **النوع (type):** ثابت، ويحدد العمليات الممكنة؛ تعطيه `type()`.
3. **القيمة (value):** قد تتغير إن كان النوع **mutable** (مثل list)، ولا تتغير إن كان
   **immutable** (مثل int وstr).

أما **الأسماء** فتعيش في **namespace**: جدول يربط كل اسم بـobject. الإسناد `x = 10` يضيف أو
يحدّث سطرًا في هذا الجدول، ولا ينسخ أي object. وعندما لا يبقى أي اسم يشير إلى object، يحرر
Python ذاكرته تلقائيًا (garbage collection، عبر **reference counting** في CPython).
:::

:::concept
في Python، **الاسم لا يحتوي القيمة؛ الاسم يشير إليها**. عندما نكتب `x = 10`:

1. يُحسب الطرف الأيمن فينتج **object**: شيء في الذاكرة له نوع (`int`) وقيمة (`10`).
2. يُربط الاسم `x` بذلك الـobject. هذا الربط يسمى **name binding**.

الـ`=` في Python ليست «يساوي»، بل **«اربط الاسم الذي على اليسار بالقيمة التي على اليمين»**.
:::

:::diagram title="x = 10 ثم y = x: اسمان، object واحد"
flowchart LR
    X(["x"]) --> O["int: 10"]
    Y(["y"]) --> O
:::

:::code mode="script"
x = 10
y = x
print(x)
print(y)
:::

افتح تبويب **Variables** بعد التشغيل: عمود *Same object as* يوضح أن `x` و`y` يشيران
إلى الـobject نفسه في هذا المثال.

## ماذا يحدث عند `x = x + 1`؟

:::animation id="anim-rebind":::

:::concept
`x = x + 1` لا «تزيد» الرقم 10. الأعداد **immutable**: لا يمكن تعديلها. ما يحدث هو حساب
object جديد (11) ثم **إعادة ربط** الاسم `x` به. هذا يسمى **rebinding**، ولا يمس `y`.
:::

## والآن مع قائمة (mutable)

:::quiz id="q-alias":::

:::animation id="anim-mutate":::

:::compare title="Rebinding مقابل Mutation"
**Rebinding** — الاسم ينتقل

```python
x = x + 1
a = a + [3]
```
يُنشأ object جديد ويُنقل إليه **الاسم**. الأسماء الأخرى لا تتأثر.
|||
**Mutation** — الـobject يتغير

```python
a.append(3)
a[0] = 99
```
يتغير **الـobject نفسه**. كل الأسماء المرتبطة به ترى التغيير.
:::

:::change id="ch-copy":::

:::mistake
**«كل assignment يعني copy»** — غير صحيح. `b = a` يعطي الـobject نفسه اسمًا إضافيًا
(**alias**). إذا احتجت نسخة مستقلة فاطلبها صراحة: `a.copy()` أو `list(a)`.
(ونسخ القوائم المتداخلة موضوع مستقل: shallow copy مقابل deep copy.)
:::

## ثلاث علامات تُخلط كثيرًا

:::code mode="script"
a = [1, 2]
b = [1, 2]
c = a

print(a == b)   # same value?
print(a is b)   # same object?
print(a is c)
:::

:::rule
- `=` ربط (assignment).
- `==` مقارنة **القيمة**.
- `is` مقارنة **الهوية** (نفس الـobject؟). استخدمها أساسًا مع `None`: `if x is None`.
:::

:::research
أسماء المتغيرات جزء من قابلية قراءة البحث وإعادة إنتاجه:

```python
sample_size = 250
significance_level = 0.05
model_name = "OLS"
```

والانتباه إلى الـaliasing مهم عند تنظيف البيانات: إذا عدّلت «نسخة» من القائمة أو الجدول
وهي في الحقيقة alias، فقد تكون عدّلت البيانات الأصلية دون أن تنتبه.
:::

:::exercise id="ex-copy":::

:::under_the_hood
`id(obj)` يعطي رقمًا فريدًا للـobject طوال حياته، و`a is b` تعني عمليًا `id(a) == id(b)`.
يعيد CPython أحيانًا استخدام objects صغيرة (مثل الأعداد من -5 إلى 256)، لذلك قد يكون
`is` صحيحًا بين عددين متساويين. هذا **تفصيل تنفيذ** لا يُعتمد عليه؛ قارن القيم دائمًا بـ`==`.
:::

:::sketchnote
```text
VARIABLE ≠ BOX
VARIABLE = NAME → OBJECT

=    binding / assignment
==   value comparison
is   identity comparison

x = x + 1    → rebinding  (name moves)
a.append(3)  → mutation   (object changes, every alias sees it)
```
:::

:::cheatsheet
| الكود | ماذا يحدث؟ |
|---|---|
| `x = 10` | ربط `x` بـobject قيمته 10 |
| `y = x` | ربط `y` بالـobject نفسه (لا نسخ) |
| `x = x + 1` | object جديد + rebinding لـ`x` |
| `a.append(v)` | mutation للقائمة نفسها |
| `b = a.copy()` | قائمة جديدة مستقلة |
| `a is b` | هل هما نفس الـobject؟ |
:::

:::quiz id="q-exit":::

:::docs
- [Assignment statements](https://docs.python.org/3/reference/simple_stmts.html#assignment-statements)
- [Data model: objects, values and types](https://docs.python.org/3/reference/datamodel.html#objects-values-and-types)
:::
