:::question
«هل الطالب ناجح؟» «هل الملف موجود؟» «هل القيمة مفقودة؟» كل سؤال له جوابان فقط. **ما النوع الذي
يحمل جوابًا من هذا الصنف؟**
:::

:::theory title="النوع bool"
الـ`bool` نوع أساسي له **قيمتان فقط**: `True` و`False` (بحرف كبير في أولهما). سمي نسبة إلى
**George Boole** الذي أسس الجبر المنطقي في القرن التاسع عشر.

ثلاث حقائق تفسر معظم سلوكه:

1. **المقارنات تُنتج bool:** `5 > 3` ليست «جملة» بل **قيمة** `True` يمكن تخزينها في متغير.
2. **bool نوع فرعي من int:** `True == 1` و`False == 0`، ولذلك يمكن جمع القيم المنطقية.
3. **كل قيمة لها «قيمة منطقية» (truthiness):** `bool(x)` يُرجع `False` للقيم «الفارغة» أو
   الصفرية، و`True` لكل ما عداها.
:::

:::code mode="script"
age = 20
is_adult = age >= 18          # a comparison produces a value
print(is_adult, type(is_adult).__name__)
print(True == 1, False == 0, isinstance(True, int))
print(True + True, True * 10)
:::

## truthiness: ماذا تعتبره Python «خاطئًا»؟

:::syntax
| القيم falsy (تعطي `False`) | أمثلة truthy |
|---|---|
| `False`، `None` | `True` |
| `0`، `0.0`، `0j` | `-1`، `0.001` |
| `""` نص فارغ | `" "`، `"0"`، `"False"` |
| `[]`، `()`، `{}`، `set()`، `range(0)` | `[0]`، `(None,)`، `{"a": 0}` |
:::

:::code mode="script"
for value in [0, 1, "", "0", "False", [], [0], None, 0.0, 0j]:
    print(f"{value!r:>8} → {bool(value)}")
:::

:::quiz id="q-false-string":::

:::animation id="anim-bool":::

:::mistake
```python
answer = input("Continue? ")     # the user types: no
if answer:                       # "no" is a non-empty string → True!
    continue_process()
```
النص غير الفارغ truthy دائمًا مهما كان معناه. قارن بالقيم المقصودة صراحة:
`if answer.strip().lower() in {"yes", "y"}:`.
:::

## العدّ والنسب بجمع القيم المنطقية

:::quiz id="q-sum":::

:::code mode="script"
scores = [12, 7, 18, 10, 9, 15]
passed = [s >= 10 for s in scores]
print(passed)
print("passed:", sum(passed), "of", len(scores))
print(f"pass rate: {sum(passed) / len(scores):.0%}")
:::

:::rule
- لا تكتب `if x == True:`؛ اكتب `if x:`، وللنفي `if not x:`.
- لكن حين تريد التمييز بين `False` و`None` و`0` فافحص صراحة (`x is None`، `x == 0`).
- للعدّ: `sum(condition for x in data)` أوضح وأسرع من عدّاد يدوي.
:::

:::research
«قناع منطقي (boolean mask)» هو أساس التصفية في NumPy وpandas: `df[df["age"] >= 18]` يعني «احتفظ
بالصفوف التي قيمة شرطها True». ومتوسط عمود منطقي هو **نسبة** الحالات: `(df["passed"]).mean()`
تعطي معدل النجاح مباشرة.
:::

:::exercise id="ex-yesno":::

:::deep_dive
`and` و`or` لا تُعيدان بالضرورة `True`/`False`، بل تُعيدان **أحد الطرفين**: `"" or "N/A"` تعطي
`"N/A"`، و`0 and 5` تعطي `0`. أما `not` فتُعيد دائمًا bool حقيقيًا. وأي class يمكنه تحديد قيمته
المنطقية بتعريف `__bool__` (أو `__len__`)؛ هكذا تعرف Python أن القائمة الفارغة falsy.
:::

:::sketchnote
```text
bool = True | False            comparisons → bool    5 > 3 → True
bool ⊂ int:  True == 1, False == 0      sum(bools) = count, mean = share
falsy: False None 0 0.0 0j "" [] () {} set() range(0)
bool("False") → True  (non-empty!)      compare text explicitly
if x:   not   if x == True:
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| قيمة منطقية | `True`, `False` |
| من مقارنة | `ok = x >= 10` |
| truthiness | `bool(x)` |
| عدّ الحالات | `sum(x > 0 for x in xs)` |
| نص ← منطقي | `s.strip().lower() in {"yes", "y"}` |
| نفي | `not ok` |
:::

:::quiz id="q-exit":::

:::docs
- [Boolean Type — bool](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool)
- [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
:::
