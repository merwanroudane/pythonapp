:::question
طالب لم يُجرِ الامتحان: هل درجته `0`؟ لا، الصفر يعني أنه أجراه وحصل على صفر. **كيف نمثّل «لا توجد
قيمة» دون أن نخترع رقمًا مضللًا؟**
:::

:::theory title="None والنوع NoneType"
`None` هي القيمة **الوحيدة** للنوع `NoneType`، وتعني **غياب القيمة**: «لا شيء هنا»، «لم يُحسب
بعد»، «غير معروف».

- None **singleton**: يوجد object واحد فقط اسمه None في كل البرنامج؛ كل `None` تكتبها هي هو
  نفسه. لذلك نفحصه بالهوية: `x is None`.
- None **ليست** `0` ولا `""` ولا `False` ولا `[]`: تلك قيم موجودة (صفر، نص فارغ، خطأ منطقي، قائمة
  فارغة)، بينما None عدم وجود قيمة. كلها falsy، لكنها ليست متساوية.
- لغات أخرى لها مفهوم مشابه: `null` في Java وJavaScript، و`NULL` في SQL، و`NA` في R. وصف Tony
  Hoare مخترع «null reference» اختراعه بأنه «خطأ المليار دولار»، لأن نسيان احتمال الغياب مصدر أخطاء
  لا يحصى، وهذا ما تجعله Python ظاهرًا بأخطاء `NoneType`.
:::

:::code mode="script"
x = None
print(x, type(x).__name__)
print(x is None, bool(x))
print(id(None) == id(x))      # one single None object
:::

:::quiz id="q-equal":::

## أين تظهر None دون أن تكتبها؟

:::code mode="script"
def greet(name):
    print("Hello", name)          # no return statement

result = greet("Sara")
print("result:", result)

scores = [14, 9, 17]
sorted_in_place = scores.sort()   # methods that modify return None
print("sort() returned:", sorted_in_place, "| scores:", scores)

ages = {"Sara": 30}
print("get missing key:", ages.get("Omar"))
:::

:::quiz id="q-sort":::

:::mistake
**`'NoneType' object has no attribute …`** و**`unsupported operand type(s) … 'NoneType'`** تعنيان
أن متغيرًا توقعت أن يحمل قيمة يحمل `None`. ابحث عن **مصدره**: دالة بلا `return`؟ method تعدّل في
المكان (`sort`، `append`)؟ `dict.get` لمفتاح مفقود؟
:::

:::code mode="script" expect="AttributeError"
scores = [14, 9, 17].sort()
scores.append(20)
:::

:::animation id="anim-none":::

## None كقيمة افتراضية وكقيمة مفقودة

:::code mode="script"
def describe(score=None):
    if score is None:
        return "not taken"
    return f"score = {score}"

print(describe(), "|", describe(0), "|", describe(15))
:::

:::warning
لا تكتب `if not score:` عندما تقصد «مفقود»: الدرجة `0` falsy أيضًا وستُعامل كأنها مفقودة. الفحص
الصحيح للغياب هو `if score is None:`.
:::

:::research
تمثيل القيم المفقودة قرار منهجي. رمز مثل `-999` أو `99` داخل بيانات استبيان **خطير**: إن نُسي، دخل
المتوسطات كقيمة حقيقية وشوّه النتائج. في Python الخالصة استخدم `None`؛ وفي الحسابات العددية ستجد
`float("nan")` (NumPy)، وفي pandas `NaN` و`pd.NA` و`NaT`، ولكل منها قواعد نتعلمها في مسار pandas.
:::

:::exercise id="ex-safe-mean":::

:::deep_dive
None ليست NaN: `float("nan")` **رقم** من نوع float («ليس رقمًا صالحًا») ينتج من عمليات مثل
`0.0 * float("inf")`، وله خاصية غريبة: `nan == nan` يعطي `False`. أما `None == None` فيعطي `True`
دائمًا. الأول قيمة رقمية معطوبة، والثاني غياب قيمة.
:::

:::sketchnote
```text
None  = the only value of NoneType = "no value here"
singleton → test with   x is None / x is not None
None ≠ 0 ≠ "" ≠ False ≠ []      (all falsy, none equal)
sources: function without return · list.sort() · dict.get(missing)
'NoneType' has no attribute …  → find where the None came from
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| لا قيمة | `x = None` |
| هل مفقود؟ | `if x is None:` |
| هل موجود؟ | `if x is not None:` |
| قيمة افتراضية آمنة | `def f(items=None):` |
| تجاهل المفقود | `[v for v in xs if v is not None]` |
:::

:::quiz id="q-exit":::

:::docs
- [None — Built-in Constants](https://docs.python.org/3/library/constants.html#None)
- [PEP 8 — Programming Recommendations (comparisons to None)](https://peps.python.org/pep-0008/#programming-recommendations)
:::
