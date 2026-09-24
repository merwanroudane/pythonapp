:::question
جدول استبيان: 5,000 صف و20 عمودًا فيه أرقام ونصوص وتواريخ وقيم مفقودة. تحتاج أن تصفّي وتجمع وتلخّص
حسب المدينة والفئة العمرية. **ما الأداة التي تجعل هذا بضعة أسطر؟**
:::

:::theory title="Series وDataFrame وindex"
**pandas** مكتبة الجداول في Python، مبنية فوق NumPy:

- **`Series`**: عمود واحد، أي مصفوفة أحادية البعد لها **dtype** و**index** (تسميات للصفوف).
- **`DataFrame`**: جدول من عدة Series تتشارك **index** واحدًا؛ لكل **عمود** نوعه الخاص (أرقام، نصوص،
  تواريخ، منطقي).
- **الـindex** ليس «رقم السطر» فقط: هو تسمية الصف، وتعتمد عليه عمليات كثيرة مثل المحاذاة (alignment)
  عند جمع جدولين، والدمج، والتجميع.

وأغلب عمليات pandas **vectorized** مثل NumPy: `df["price"] * 1.2` تعمل على العمود كله دون حلقة.
:::

:::diagram kind="text" title="تشريح DataFrame"
                 columns ─────────────────────────►
            ┌─────────┬───────┬─────────┬─────────┐
   index    │  name   │  age  │  city   │ income  │   ← each column is a Series
     │   0  │  Sara   │  30   │  Oran   │ 42000.0 │     with its own dtype
     │   1  │  Omar   │  17   │ Algiers │   NaN   │   ← missing value
     ▼   2  │  Lina   │  45   │  Oran   │ 58000.0 │
            └─────────┴───────┴─────────┴─────────┘
             str       int64   str       float64
:::

## الإنشاء والفحص

:::code mode="script"
import pandas as pd

df = pd.DataFrame({
    "name": ["Sara", "Omar", "Lina", "Adam", "Yasmine", "Rami"],
    "age": [30, 17, 45, 22, 38, 51],
    "city": ["Oran", "Algiers", "Oran", "Setif", "Algiers", "Oran"],
    "income": [42000, None, 58000, 31000, 47000, 61000],
})
print(df.head(3))
print(df.shape)
print(df.dtypes)
print(df.describe().round(1))
:::

:::tip
مع ملف حقيقي تبدأ بـ`df = pd.read_csv("data.csv")` (أو `read_excel` و`read_parquet`)، ثم مباشرة
`df.shape` و`df.dtypes` و`df.isna().sum()` و`df.head()`: أربع نظرات تكشف معظم مشاكل البيانات.
:::

## الاختيار والتصفية

:::code mode="script"
import pandas as pd

df = pd.DataFrame({
    "name": ["Sara", "Omar", "Lina", "Adam"],
    "age": [30, 17, 45, 22],
    "city": ["Oran", "Algiers", "Oran", "Setif"],
}).set_index("name")

print(df["age"])                          # one column → Series
print(df[["age", "city"]])                # several columns → DataFrame
print(df.loc["Lina", "city"])             # by label
print(df.iloc[0])                         # by position
print(df[(df["age"] >= 18) & (df["city"] == "Oran")])   # boolean filter
:::

:::quiz id="q-loc-iloc":::

:::quiz id="q-filter":::

## أعمدة جديدة، قيم مفقودة، تجميع

:::code mode="script"
import pandas as pd

df = pd.DataFrame({
    "city": ["Oran", "Algiers", "Oran", "Setif", "Algiers", "Oran"],
    "income": [42000, None, 58000, 31000, 47000, 61000],
    "age": [30, 17, 45, 22, 38, 51],
})
df["income_k"] = df["income"] / 1000                    # vectorized new column
df["age_group"] = pd.cut(df["age"], bins=[0, 17, 39, 120], labels=["<18", "18-39", "40+"])

print(df.isna().sum())                                  # missing per column
summary = df.groupby("city").agg(n=("income", "size"), mean_income=("income", "mean"))
print(summary.sort_values("mean_income", ascending=False))
:::

:::concept
**Split → Apply → Combine**: `groupby("city")` **يقسم** الصفوف إلى مجموعات، ثم تُطبَّق دالة تجميع
(`mean`، `sum`، `count`…) على كل مجموعة، ثم **تُجمع** النتائج في جدول جديد index-ه أسماء المجموعات.
وتتجاهل دوال التجميع القيم المفقودة `NaN` افتراضيًا، لكن `size` تعدّ كل الصفوف و`count` تعدّ غير
المفقودة فقط.
:::

:::mistake
- **`and` بدل `&`:** `df[df.age > 18 and df.city == "Oran"]` ترفع `ValueError`.
- **نسيان الأقواس:** `df[df.age > 18 & df.city == "Oran"]` تُحسب بترتيب خاطئ لأن `&` أعلى أولوية من `>`.
- **الأرقام المخزّنة نصوصًا:** عمود قيمه `"42,000"` نوعه `str`؛ `mean()` لن يعمل حتى تنظفه وتحوّله
  (`pd.to_numeric`).
- **عمود غير موجود:** `df["Income"]` مع أن الاسم `income` يرفع `KeyError`.
:::

:::code mode="script" expect="KeyError"
import pandas as pd
df = pd.DataFrame({"income": [1, 2]})
print(df["Income"])
:::

:::research
سير عمل تحليلي نموذجي بـpandas: `read_csv` ← فحص (`shape`، `dtypes`، `isna`) ← تنظيف (أنواع، قيم
مستحيلة، تكرار) ← أعمدة مشتقة ← `groupby` للجداول الوصفية ← تصدير (`to_csv`، `to_latex` للأوراق).
احتفظ بكل ذلك في سكربت أو دوال لا في خلايا متفرقة، حتى يمكن إعادة تشغيله على بيانات محدّثة.
:::

:::exercise id="ex-survey":::

:::deep_dive
منذ pandas 3.0 أصبح **Copy-on-Write** هو السلوك الافتراضي: الجدول الناتج عن اختيار أو تصفية يتصرف
كنسخة مستقلة، فلا يعدّل تعديلُه الجدولَ الأصلي بالخطأ، واختفى معظم تحذير `SettingWithCopyWarning` القديم.
وأصبح نوع الأعمدة النصية الافتراضي `str` بدل `object`. لإضافة عمود إلى جدول مصفّى، استخدم
`.assign(...)` أو اعمل على الجدول مباشرة بـ`.loc[شرط, "col"] = قيمة`.
:::

:::sketchnote
```text
Series = one labelled column      DataFrame = columns sharing an index
first look: shape · dtypes · head() · describe() · isna().sum()
df["col"] · df[["a","b"]] · df.loc[label, col] · df.iloc[row, col]
filter: df[(cond1) & (cond2)]      never  and / or
new column: df["x2"] = df["x"] * 2    (vectorized)
groupby("key").agg(name=("col", "mean"))   split → apply → combine
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| قراءة ملف | `pd.read_csv(path)` |
| نظرة سريعة | `df.head()`، `df.info()`، `df.describe()` |
| عمود / أعمدة | `df["a"]`، `df[["a", "b"]]` |
| بالتسمية / بالموضع | `df.loc[r, c]`، `df.iloc[i, j]` |
| تصفية | `df[df["age"] >= 18]` |
| مفقودات | `df.isna().sum()`، `df.dropna()`، `df.fillna(0)` |
| تجميع | `df.groupby("city")["x"].mean()` |
| ترتيب | `df.sort_values("x", ascending=False)` |
:::

:::quiz id="q-exit":::

:::docs
- [10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
- [Indexing and selecting data](https://pandas.pydata.org/docs/user_guide/indexing.html)
- [Group by: split-apply-combine](https://pandas.pydata.org/docs/user_guide/groupby.html)
:::
