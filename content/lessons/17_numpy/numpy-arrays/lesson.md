:::question
مليون قياس، وتريد طرح المتوسط من كل واحد وقسمته على الانحراف. حلقة Python على مليون عنصر بطيئة.
**كيف تُجري حسابًا على مليون رقم «دفعة واحدة»؟**
:::

:::theory title="لماذا NumPy؟"
الـ`list` في Python مرنة: كل عنصر **مرجع** إلى object مستقل قد يكون من أي نوع. هذه المرونة مكلفة: كل
عملية حسابية تمر بالـinterpreter عنصرًا عنصرًا.

**NumPy** توفر بنية أخرى: **`ndarray`**، مصفوفة **n-dimensional**:

- **متجانسة (homogeneous):** كل العناصر من **dtype** واحد (`int64`، `float64`، `bool`…).
- **متجاورة في الذاكرة:** كتلة واحدة من الأرقام الخام، لا مراجع متفرقة.
- **العمليات تُنفَّذ بكود C مُصرَّف** على الكتلة كلها دفعة واحدة: هذا ما يسمى **vectorization**.

النتيجة: سرعة أكبر بعشرات أو مئات المرات، وكود أقصر يشبه الرياضيات: `(x - x.mean()) / x.std()`.
وهي الأساس الذي بُنيت عليه pandas وSciPy وscikit-learn وmatplotlib.
:::

:::quiz id="q-list-vs-array":::

## الإنشاء والخصائص

:::code mode="script"
import numpy as np

a = np.array([3, 1, 4, 1, 5])
m = np.arange(12).reshape(3, 4)          # 0..11 as 3 rows × 4 columns
print(a, a.dtype, a.shape)
print(m)
print("ndim:", m.ndim, "shape:", m.shape, "size:", m.size, "dtype:", m.dtype)
print(np.linspace(0, 1, 5), np.zeros((2, 3)).shape, np.ones(3))
:::

:::syntax
| الخاصية | المعنى | مثال لـ`m` أعلاه |
|---|---|---|
| `ndim` | عدد الأبعاد | `2` |
| `shape` | الطول في كل بعد | `(3, 4)` |
| `size` | عدد العناصر الكلي | `12` |
| `dtype` | نوع العناصر | `int64` |
| `m[1, 2]` | صف 1، عمود 2 | `6` |
| `m[:, 0]` | العمود الأول كله | `[0 4 8]` |
:::

## Vectorization: عمليات بلا حلقات

:::code mode="script"
import numpy as np

prices = np.array([10.0, 25.0, 8.0, 40.0])
print(prices * 1.2)                     # every element
print(prices + np.array([1, 2, 3, 4]))  # elementwise, same shape
print(np.sqrt(prices), np.round(np.log(prices), 3))
print(prices.mean(), prices.std(), prices.max(), prices.argmax())
:::

:::code mode="script"
import timeit
import numpy as np

xs = list(range(100_000))
arr = np.arange(100_000)
t_list = timeit.timeit(lambda: [x * 2 for x in xs], number=20)
t_np = timeit.timeit(lambda: arr * 2, number=20)
print(f"list comprehension: {t_list:.3f}s   numpy: {t_np:.4f}s   → ~{t_list / t_np:.0f}× faster")
:::

## Broadcasting: أشكال مختلفة معًا

:::theory title="قاعدة الـbroadcasting"
عند عملية بين مصفوفتين بشكلين مختلفين، تقارن NumPy الأبعاد **من اليمين إلى اليسار**. يتوافق البعدان
إذا كانا **متساويين** أو كان **أحدهما 1**، فيُمدَّد البعد الذي طوله 1 منطقيًا (دون نسخ فعلي). مثال:
`(5, 3) - (3,)`: الـ`(3,)` تُعامل كـ`(1, 3)` ثم تُمدد على الصفوف الخمسة. أما `(5, 3) + (5,)` فتفشل،
لأن 3 و5 غير متوافقين.
:::

:::code mode="script"
import numpy as np

scores = np.array([[12, 15, 9], [14, 11, 16], [18, 13, 12]], dtype=float)
col_means = scores.mean(axis=0)          # shape (3,)
print(col_means)
print(scores - col_means)                # (3, 3) - (3,) → broadcast over rows
:::

:::code mode="script" expect="ValueError"
import numpy as np
np.ones((5, 3)) + np.ones(5)             # trailing dimensions 3 and 5 do not match
:::

:::animation id="anim-numpy":::

:::quiz id="q-axis":::

## الأقنعة المنطقية (boolean masks)

:::code mode="script"
import numpy as np

ages = np.array([23, 17, 45, 15, 31, 68])
adult = ages >= 18
print(adult)                  # an array of bools
print(ages[adult])            # keep only True positions
print(adult.sum(), adult.mean())      # count and share
print(np.where(ages >= 65, "senior", "other"))
:::

:::mistake
- **خلط الأنواع:** `np.array([1, "2", 3])` تحوّل كل شيء إلى نصوص.
- **`and`/`or` مع المصفوفات:** `(a > 0) and (a < 5)` ترفع `ValueError`. استخدم `&` و`|` مع الأقواس:
  `(a > 0) & (a < 5)`.
- **التعديل عبر view:** `b = a[:3]` ليست نسخة؛ تعديل `b` يعدّل `a`. استخدم `a[:3].copy()`.
:::

:::code mode="script" expect="ValueError"
import numpy as np
a = np.array([1, 4, 7])
print((a > 0) and (a < 5))
:::

:::research
معظم الحسابات الإحصائية الأساسية تكتب بـNumPy في سطر: التوحيد القياسي، مصفوفة الارتباط
(`np.corrcoef`)، جداء المصفوفات (`X.T @ X`)، وحل المعادلات (`np.linalg.solve`). ولمحاكاة Monte Carlo
أو bootstrap استخدم مولّدًا له بذرة: `rng = np.random.default_rng(42)` ثم `rng.normal(size=1000)`.
:::

:::exercise id="ex-standardize":::

:::deep_dive
الـslicing في NumPy يُعيد **view** (نظرة على الذاكرة نفسها) لا نسخة، وهذا سبب سرعته وسبب مفاجآته.
أما الـ«fancy indexing» (بقائمة أو قناع) فيُعيد **نسخة**. استخدم `np.shares_memory(a, b)` للتحقق.
وجداء المصفوفات هو `@` (`A @ B`)، لا `*` الذي يضرب عنصرًا بعنصر.
:::

:::sketchnote
```text
ndarray = ONE dtype · shape · contiguous memory · operations in compiled C
list * 2 → repeat           array * 2 → multiply every element
axis=0 → down the rows (per column)     axis=1 → across columns (per row)
broadcasting: compare shapes right→left, equal or 1 → OK
mask:  a[a > 0]     combine with & |  (never and/or)     A @ B matrix product
slice = view (shares memory)   .copy() for an independent array
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| إنشاء | `np.array(xs)`، `np.arange(n)`، `np.linspace(a, b, k)` |
| إعادة تشكيل | `a.reshape(3, 4)` |
| إحصاءات | `a.mean()`، `a.std()`، `a.sum(axis=0)` |
| تصفية | `a[a > 0]` |
| شرط عنصرًا عنصرًا | `np.where(cond, x, y)` |
| جداء مصفوفات | `A @ B` |
| عشوائية بذرة | `np.random.default_rng(42)` |
:::

:::quiz id="q-exit":::

:::docs
- [NumPy: the absolute basics for beginners](https://numpy.org/doc/stable/user/absolute_beginners.html)
- [Broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html)
- [Indexing on ndarrays](https://numpy.org/doc/stable/user/basics.indexing.html)
:::
