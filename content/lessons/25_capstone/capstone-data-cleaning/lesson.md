:::question
وصلك ملف استبيان من فريق ميداني: أسماء مدن بتهجئات مختلفة، أعمار مثل `"n/a"` و`151`، دخل بفواصل،
تواريخ مستحيلة، وصفوف مكررة. المطلوب: جدول وصفي ورسم لورقة بحثية. **كيف تنتقل من الفوضى إلى نتائج
يثق بها المراجع؟**
:::

:::theory title="سير العمل البحثي الكامل"
هذا المشروع يجمع ما تعلمته: الملفات، والنصوص، والدوال، وpandas، والرسوم، والاختبار. والفكرة المركزية
**خط معالجة (pipeline)** واضح المراحل، كل مرحلة دالة:

1. **القراءة:** الملف الخام كما هو، **لا يُعدَّل أبدًا**.
2. **الفحص:** الشكل، الأنواع، القيم الفريدة، المفقودات. ماذا يوجد فعلًا؟
3. **التنظيف:** توحيد النصوص، تحويل الأنواع، القيم المستحيلة تصبح مفقودة، حذف التكرار.
4. **التحقق (validation):** شروط يجب أن تصح بعد التنظيف (`assert`) وإلا يتوقف البرنامج.
5. **التحليل:** جداول وصفية وتجميع.
6. **المخرجات:** جدول ورسم يُنتَجان من الكود نفسه، مع **سجل** بكل قرار (كم صفًا حُذف ولماذا).

**قابلية إعادة الإنتاج (reproducibility)** تعني أن أي شخص يشغّل الكود على الملف الخام نفسه يحصل على
الأرقام نفسها بالضبط.
:::

:::diagram kind="text" title="الخط من البداية إلى النهاية"
  raw.csv ──► load ──► inspect ──► clean ──► validate ──► summarise ──► table.csv
  (read-only)            │           │           │                     figure.pdf
                         └───────────┴───────────┴──► cleaning log  ("2 impossible ages → NaN")
:::

## 1. القراءة والفحص

:::code mode="script"
import io

import pandas as pd

RAW_CSV = """id,age,city,income,date
1,34, oran ,"42,000",2024-03-01
2,n/a,ALGIERS,38000,2024-03-02
3,29,Alger,,2024-13-40
3,29,Alger,,2024-13-40
4,-3,setif,"51,500",2024-03-05
5,151,Oran,"47,250",2024-03-06
6,41,Constantine,"39,900",2024-03-07
7,38,oran,"55,100",2024-03-08
"""
raw = pd.read_csv(io.StringIO(RAW_CSV), dtype=str, keep_default_na=False)   # read everything as text first

print(raw.shape)
print(raw.dtypes)
print(raw["city"].value_counts())
print("duplicated ids:", raw["id"].duplicated().sum())
:::

:::tip
القراءة بـ`dtype=str` أولًا تمنع pandas من تخمين الأنواع بصمت. أنت من يقرر لاحقًا، عمودًا عمودًا، كيف
يُحوَّل كل واحد.
:::

:::quiz id="q-raw":::

## 2. التنظيف بدوال صغيرة مع سجل

:::code mode="script"
import io

import pandas as pd

RAW_CSV = """id,age,city,income,date
1,34, oran ,"42,000",2024-03-01
2,n/a,ALGIERS,38000,2024-03-02
3,29,Alger,,2024-13-40
3,29,Alger,,2024-13-40
4,-3,setif,"51,500",2024-03-05
5,151,Oran,"47,250",2024-03-06
6,41,Constantine,"39,900",2024-03-07
7,38,oran,"55,100",2024-03-08
"""
raw = pd.read_csv(io.StringIO(RAW_CSV), dtype=str, keep_default_na=False)
log = []

CITY_FIXES = {"Alger": "Algiers"}


def clean_city(s):
    return s.str.strip().str.title().replace(CITY_FIXES)


def clean_age(s):
    age = pd.to_numeric(s, errors="coerce")
    impossible = ~age.between(0, 120) & age.notna()
    log.append(f"age: {int(age.isna().sum())} unreadable, {int(impossible.sum())} impossible → NaN")
    return age.where(age.between(0, 120))


def clean_income(s):
    return pd.to_numeric(s.str.replace(",", "", regex=False), errors="coerce")


def clean_date(s):
    d = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    log.append(f"date: {int(d.isna().sum())} invalid → NaT")
    return d


df = raw.assign(
    id=pd.to_numeric(raw["id"]),
    city=clean_city(raw["city"]),
    age=clean_age(raw["age"]),
    income=clean_income(raw["income"]),
    date=clean_date(raw["date"]),
)
before = len(df)
df = df.drop_duplicates(subset="id").reset_index(drop=True)
log.append(f"duplicates: {before - len(df)} row(s) removed")

print(df)
print(*log, sep="\n")
:::

:::quiz id="q-missing":::

## 3. التحقق ثم التلخيص والرسم

:::code mode="script"
import matplotlib.pyplot as plt
import pandas as pd

df = pd.DataFrame({
    "id": [1, 2, 3, 4, 5, 6, 7],
    "age": [34, None, 29, None, None, 41, 38],
    "city": ["Oran", "Algiers", "Algiers", "Setif", "Oran", "Constantine", "Oran"],
    "income": [42000, 38000, None, 51500, 47250, 39900, 55100],
})

# validate: stop loudly instead of publishing wrong numbers
assert df["id"].is_unique, "ids must be unique"
assert df["age"].dropna().between(0, 120).all(), "ages out of range"
assert (df["income"].dropna() > 0).all(), "incomes must be positive"

table = (
    df.groupby("city")
    .agg(n=("id", "size"), mean_income=("income", "mean"), missing_income=("income", lambda s: s.isna().sum()))
    .sort_values("mean_income", ascending=False)
    .round(0)
)
print(table)

fig, ax = plt.subplots(figsize=(6, 3.2))
ax.barh(table.index, table["mean_income"] / 1000)
ax.invert_yaxis()
ax.set_xlabel("Mean income (thousand DZD)")
ax.set_title(f"Mean income by city (n = {len(df)})")
fig.tight_layout()
# table.to_csv("outputs/table1.csv"); fig.savefig("outputs/figure1.pdf")
:::

:::rule
- **الخام للقراءة فقط.** والمخرجات تُولَّد من الكود دائمًا.
- **لا تحذف بصمت:** كل حذف أو تحويل إلى مفقود يُسجَّل بعدده وسببه، ويُذكر في قسم البيانات في الورقة.
- **أبلغ عن `n`** لكل خلية في الجدول، ولا تخفِ المفقودات.
- **اختبر دوال التنظيف** بحالات صغيرة مكتوبة يدويًا (كما في درس الاختبار).
:::

:::mistake
- `pd.read_csv` يحوّل `"n/a"` و`""` إلى NaN ويخمّن الأنواع، فتضيع معلومة ما كان في الملف أصلًا.
- التنظيف في Excel ثم نسيان ما تغيّر.
- `df.dropna()` على الجدول كله يحذف صفًا كاملًا بسبب عمود واحد لا تحتاجه.
- حساب المتوسطات **قبل** حذف المكررات فيُحسب الشخص نفسه مرتين.
:::

:::code mode="script" expect="AssertionError"
import pandas as pd
ages = pd.Series([34, 29, 151])
assert ages.between(0, 120).all(), f"ages out of range: {ages[~ages.between(0, 120)].tolist()}"
:::

:::research
حوّل هذا الدرس إلى مشروع حقيقي كما في درس الحزم: `src/survey_tools/cleaning.py` للدوال،
و`tests/test_cleaning.py` لاختباراتها، وأمر `survey run data/raw/survey.csv` يُنتج
`outputs/table1.csv` و`outputs/figure1.pdf` و`outputs/cleaning_log.txt`. ضع كل ذلك في Git، وأرفق
`README` يشرح خطوات إعادة الإنتاج. هذا بالضبط ما يُسمى replication package.
:::

:::exercise id="ex-pipeline":::

:::deep_dive
**مكتبات التحقق من المخطط (schema validation)** مثل **pandera** تصف شكل الجدول المتوقع تصريحيًا
(الأعمدة، الأنواع، النطاقات، التفرد) وتتحقق منه بسطر واحد، مع رسائل خطأ مفصلة. وللبيانات الكبيرة
يمكن تشغيل الخط نفسه بـ**polars** أو **DuckDB**. تبقى الفكرة واحدة: مراحل صغيرة، وشروط صريحة، وسجل.
:::

:::sketchnote
```text
raw (read-only) → load(dtype=str) → inspect → clean → VALIDATE → summarise → outputs
clean = small functions: clean_city · clean_age · clean_income · clean_date
impossible → NaN (never guess) · duplicates → drop by id · log every decision
assert conditions before publishing · report n and missing
same raw + same code ⇒ same numbers   (reproducibility)
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| قراءة كنصوص | `pd.read_csv(p, dtype=str, keep_default_na=False)` |
| توحيد نص | `s.str.strip().str.title().replace(fixes)` |
| رقم آمن | `pd.to_numeric(s, errors="coerce")` |
| نطاق مقبول | `s.where(s.between(0, 120))` |
| تاريخ | `pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")` |
| مكررات | `df.drop_duplicates(subset="id")` |
| تحقق | `assert df["id"].is_unique` |
:::

:::quiz id="q-exit":::

:::docs
- [pandas: working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [pandas: working with text data](https://pandas.pydata.org/docs/user_guide/text.html)
- [The Turing Way: reproducible research](https://book.the-turing-way.org/reproducible-research/reproducible-research)
:::
