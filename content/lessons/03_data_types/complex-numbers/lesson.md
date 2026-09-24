:::question
ما جذر العدد `-4`؟ لا يوجد عدد حقيقي مربّعه سالب. ومع ذلك يحتاج المهندسون والإحصائيون هذه
«الجذور المستحيلة» كل يوم. **كيف تتعامل Python معها؟**
:::

:::theory title="ما العدد المركّب؟"
العدد المركّب (complex number) له جزءان: **حقيقي (real)** و**تخيلي (imaginary)**، ويُكتب
`a + b·i` حيث `i² = −1`. يمكن تصوره كنقطة في مستوى: المحور الأفقي للجزء الحقيقي والعمودي
للتخيلي.

- **الـmodulus** `|z| = √(a² + b²)`: المسافة من الصفر.
- **الـconjugate** (المرافق) `a − b·i`: انعكاس النقطة حول المحور الأفقي.
- **الصيغة القطبية**: `z = r·(cos θ + i·sin θ)` حيث `r = |z|` وθ الزاوية.

تستعمل Python الحرف **`j`** بدل `i`، وهو الاصطلاح المعتاد في الهندسة الكهربائية. ويُخزَّن كل عدد
مركّب كعددين `float` (الجزء الحقيقي والتخيلي)، فيرث دقتهما وحدودهما.
:::

:::code mode="script"
z = 3 + 4j
w = complex(1, -2)
print(type(z).__name__, z, w)
print(z.real, z.imag)
print(abs(z), z.conjugate())
print(z + w, z * w)
print(1j ** 2)
:::

:::quiz id="q-abs":::

## math مقابل cmath

:::quiz id="q-sqrt":::

:::code mode="script" expect="ValueError"
import math, cmath
print(cmath.sqrt(-4))
print(cmath.polar(-1))
print(math.sqrt(-4))
:::

:::change id="ch-polar":::

:::mistake
```python
z = 3 + j          # NameError: name 'j' is not defined
z = 3 + 1j         # correct: the j is glued to a number
```
`j` وحده **اسم متغير**، أما `1j` أو `4j` فـliteral لعدد مركّب. ولا يمكن ترتيب الأعداد المركّبة:
`(1 + 2j) < (2 + 1j)` يرفع `TypeError`.
:::

:::code mode="script" expect="TypeError"
print((1 + 2j) < (2 + 1j))
:::

:::research
الجذور المركّبة تظهر كثيرًا في الاقتصاد القياسي: جذور المعادلة المميزة لنموذج **AR** أو **VAR** تحدد
**الاستقرارية (stationarity)**، وإذا كانت الجذور مركّبة فالسلسلة **تتذبذب** (cycles). والشرط: modulus
كل جذر أقل من 1 (أي داخل «دائرة الوحدة»). ونفس الفكرة وراء تحويل Fourier (`numpy.fft`) في تحليل
الإشارات والسلاسل الزمنية.
:::

:::code mode="script"
import cmath

phi1, phi2 = 0.5, -0.7                       # AR(2) coefficients
disc = cmath.sqrt(phi1 ** 2 + 4 * phi2)
for root in ((phi1 + disc) / 2, (phi1 - disc) / 2):
    print(f"root = {root:.4f}   |root| = {abs(root):.4f}")
:::

:::exercise id="ex-ar2":::

:::deep_dive
`complex` نوع أساسي **immutable** مثل `int` و`float`، والعمليات بين الأنواع الرقمية «ترتقي» إلى
الأوسع: `int` ← `float` ← `complex`. لذلك `2 + 1j` تعطي complex، و`(2 + 0j) == 2` تعطي `True`.
الدالة `cmath.isclose` تقارن الأعداد المركّبة ضمن هامش خطأ، تمامًا مثل `math.isclose`.
:::

:::sketchnote
```text
z = a + bj        j² = −1      stored as two floats
z.real  z.imag    abs(z) = √(a²+b²)    z.conjugate() = a − bj
math.sqrt(-4) ✗ ValueError       cmath.sqrt(-4) = 2j
cmath.polar(z) → (r, θ)          cmath.rect(r, θ) → z
no ordering: z1 < z2 ✗           compare abs(z1) < abs(z2)
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| إنشاء | `3 + 4j` أو `complex(3, 4)` |
| الأجزاء | `z.real`, `z.imag` |
| الـmodulus | `abs(z)` |
| المرافق | `z.conjugate()` |
| جذر عدد سالب | `cmath.sqrt(-4)` |
| الصيغة القطبية | `cmath.polar(z)`, `cmath.rect(r, θ)` |
:::

:::quiz id="q-exit":::

:::docs
- [Numeric Types — int, float, complex](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)
- [cmath — Mathematical functions for complex numbers](https://docs.python.org/3/library/cmath.html)
:::
