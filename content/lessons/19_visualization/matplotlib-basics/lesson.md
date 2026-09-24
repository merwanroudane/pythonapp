:::question
جدول من 5,000 صف لن يقرأه أحد. رسم واحد جيد قد يُظهر في ثانيتين ما تخفيه الأرقام. لكن رسمًا سيئًا قد
يُضلّل. **كيف تختار الرسم الصحيح وترسمه بوضوح؟**
:::

:::theory title="ابدأ بالسؤال لا بالرسم"
الرسم البياني **ترميز (encoding)** للبيانات في خصائص بصرية: الموضع، الطول، الحجم، اللون. والعين تقرأ
**الموضع والطول** بدقة أكبر بكثير من الزاوية أو المساحة أو اللون (نتائج دراسات Cleveland وMcGill في
الإدراك البصري)، لذلك تتفوق الأعمدة والنقاط على المخطط الدائري غالبًا.

اختر الرسم من السؤال:

| السؤال | الرسم |
|---|---|
| كيف تتوزع قيم متغير؟ | histogram، boxplot |
| هل يرتبط متغيران؟ | scatter |
| كيف يتغير شيء عبر الزمن؟ | line |
| مقارنة فئات | bar (يبدأ من الصفر) |
| مصفوفة قيم | heatmap (`imshow`) |
:::

:::theory title="Figure وAxes"
في Matplotlib: **`Figure`** هي «الصفحة» كلها، و**`Axes`** منطقة رسم واحدة داخلها لها محوراها وعنوانها
وعناصرها (خطوط، نقاط، أعمدة). الأسلوب الموصى به هو **الواجهة الكائنية**:
`fig, ax = plt.subplots()` ثم تستدعي methods على `ax`. هذا أوضح من `plt.plot` المباشر عندما تكون هناك
عدة رسوم.
:::

:::quiz id="q-choose":::

## أول رسم

كل رسم تُنشئه يظهر في تبويب **Figures** تحت الكود بعد التشغيل.

:::code mode="script"
import matplotlib.pyplot as plt

years = [2020, 2021, 2022, 2023, 2024]
growth = [-5.1, 3.4, 3.6, 4.1, 3.8]

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.plot(years, growth, marker="o", label="Algeria")
ax.axhline(0, color="gray", linewidth=0.8)
ax.set_title("Real GDP growth")
ax.set_xlabel("Year")
ax.set_ylabel("Growth (%)")
ax.set_xticks(years)
ax.legend()
fig.tight_layout()
:::

## أربعة أنواع أساسية في Figure واحدة

:::code mode="script"
import matplotlib.pyplot as plt
import numpy as np

rng = np.random.default_rng(7)
ages = rng.normal(35, 10, 500)
x = rng.uniform(0, 10, 80)
y = 2 * x + rng.normal(0, 3, 80)

fig, ax = plt.subplots(2, 2, figsize=(8, 6))
ax[0, 0].hist(ages, bins=25)
ax[0, 0].set_title("Distribution (hist)")
ax[0, 1].scatter(x, y, s=14)
ax[0, 1].set_title("Relationship (scatter)")
ax[1, 0].bar(["DZ", "MA", "TN"], [45.6, 37.8, 12.3])
ax[1, 0].set_title("Comparison (bar)")
ax[1, 1].plot(np.arange(12), np.cumsum(rng.normal(0, 1, 12)))
ax[1, 1].set_title("Trend (line)")
fig.tight_layout()
:::

:::quiz id="q-fig-ax":::

## من pandas مباشرة

:::code mode="script"
import matplotlib.pyplot as plt
import pandas as pd

df = pd.DataFrame({"city": ["Oran", "Algiers", "Setif", "Annaba"],
                   "income_k": [53.7, 47.0, 31.0, 39.5]})
fig, ax = plt.subplots(figsize=(5, 3))
df.sort_values("income_k").plot.barh(x="city", y="income_k", ax=ax, legend=False)
ax.set_xlabel("Mean income (thousand DZD)")
fig.tight_layout()
:::

:::rule
- **كل محور له تسمية ووحدة** (`"Growth (%)"`)، وكل رسم له عنوان يقول ما يُظهره.
- **الأعمدة تبدأ من الصفر.** والمحور المقطوع مسموح فقط في الخطوط، مع توضيحه.
- **اللون يحمل معنى** (فئة، قيمة) أو لا يُستعمل. تجنب قوس قزح بلا سبب وتجنب الـ3D غير الضروري.
- احفظ للأوراق بصيغة vector: `fig.savefig("fig1.pdf")` أو `.svg`، وبـ`dpi=300` لصيغ PNG.
:::

:::mistake
- رسم مخطط خطي لفئات لا ترتيب بينها (مدن) بدل الأعمدة.
- `plt.plot` ثم `plt.title` على عدة رسوم فيذهب العنوان إلى الرسم الخطأ؛ استخدم `ax.set_title`.
- نسيان الوحدات: «Income» بلا عملة ولا مقياس لا يمكن تفسيره.
:::

:::code mode="script" expect="ValueError"
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5])          # x and y must have the same length
:::

:::research
الرسم البحثي الجيد **قابل لإعادة الإنتاج**: يُولَّد من سكربت (لا من تعديل يدوي)، ويُحفظ في
`outputs/figures/` بصيغة vector. احرص على خطوط مقروءة عند حجم الطباعة، وعلى أن يفهم القارئ الرسم مع
تعليقه (caption) دون الرجوع إلى النص.
:::

:::exercise id="ex-figure":::

:::deep_dive
توجد مكتبات أعلى مستوى فوق Matplotlib أو بجانبها: **Seaborn** للرسوم الإحصائية بسطر واحد
(`sns.histplot`، `sns.regplot`)، و**Plotly** و**Altair** للرسوم التفاعلية على الويب (والأخيرة هي التي
يعتمدها Streamlit في `st.line_chart`). تعلّم Figure/Axes أولًا: هو الأساس الذي يسمح بضبط أي تفصيل.
:::

:::sketchnote
```text
QUESTION first → distribution: hist · relation: scatter · time: line · compare: bar(from 0)
fig, ax = plt.subplots(rows, cols)      Figure = page   Axes = one plot
ax.plot / scatter / bar / hist          ax.set_title · set_xlabel · set_ylabel (+ units!)
fig.tight_layout()   fig.savefig("fig.pdf")   vector for papers
position & length > area > colour     colour must mean something
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| Figure ورسم واحد | `fig, ax = plt.subplots()` |
| شبكة رسوم | `fig, ax = plt.subplots(2, 2)` |
| خط / نقاط | `ax.plot(x, y)`، `ax.scatter(x, y)` |
| أعمدة / توزيع | `ax.bar(cats, vals)`، `ax.hist(xs, bins=20)` |
| نصوص | `ax.set_title()`، `ax.set_xlabel()`، `ax.legend()` |
| حفظ | `fig.savefig("fig.pdf", bbox_inches="tight")` |
:::

:::quiz id="q-exit":::

:::docs
- [Matplotlib quick start guide](https://matplotlib.org/stable/users/explain/quick_start.html)
- [Plot types gallery](https://matplotlib.org/stable/plot_types/index.html)
- [pandas plotting](https://pandas.pydata.org/docs/user_guide/visualization.html)
:::
