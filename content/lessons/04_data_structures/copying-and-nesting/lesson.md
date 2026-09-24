:::question
نسخت قاموس إعدادات تجربة بـ`.copy()` لتعدّل النسخة في تجربة ثانية… ثم اكتشفت أن نتائج التجربة
الأولى تغيرت أيضًا. **كيف تتغير «النسخة الأصلية» وأنت لم تلمسها؟**
:::

:::theory title="ثلاثة مستويات من «النسخ»"
عندما تحتوي البنية **بنى أخرى قابلة للتعديل**، هناك ثلاثة أشياء مختلفة جدًا نسميها كلها «نسخًا»:

1. **Alias (اسم إضافي):** `b = a`. لا نسخ إطلاقًا؛ اسمان لـobject واحد.
2. **Shallow copy (نسخة سطحية):** `a.copy()` أو `list(a)` أو `a[:]` أو `copy.copy(a)`. تُنشأ حاوية
   **خارجية جديدة**، لكنها تحتوي **المراجع نفسها** إلى العناصر الداخلية.
3. **Deep copy (نسخة عميقة):** `copy.deepcopy(a)`. تُنسخ الحاوية وكل ما بداخلها **بشكل متكرر**، حتى
   لا يبقى أي object قابل للتعديل مشتركًا.

الفرق يظهر فقط مع العناصر **القابلة للتعديل**: مشاركة رقم أو نص لا تضر لأنه لا يتغير أصلًا.
:::

:::diagram kind="text" title="a = [[1, 2], [3]] بعد كل نوع من النسخ"
alias:   a ─┐                         shallow:  a ──► [ • , • ]
            ├──► [ • , • ]                            │   │
         b ─┘      │   │                          b ──► [ • , • ]   (new outer list)
                   ▼   ▼                              │   │
                [1,2] [3]                             ▼   ▼
                                                   [1,2] [3]        (SHARED inner lists)

deep:    a ──► [ • , • ] ──► [1,2] [3]
         b ──► [ • , • ] ──► [1,2] [3]      (everything duplicated)
:::

## البنى المتداخلة

:::code mode="script"
grid = [[1, 2, 3], [4, 5, 6]]                       # list of lists (a matrix)
people = [{"name": "Sara", "langs": ["ar", "fr"]}]  # list of dicts (table rows)
by_city = {"Oran": ["Sara", "Adam"]}                # dict of lists (groups)

print(grid[1][2])              # row 1, column 2
print(people[0]["langs"][1])   # first person, second language
by_city["Oran"].append("Lina")
print(by_city)
:::

:::tip
اقرأ الوصول المتداخل من اليسار إلى اليمين خطوة خطوة: `people[0]` قاموس، ثم `["langs"]` قائمة، ثم
`[1]` نص. وإن ظهر خطأ فاطبع كل خطوة على حدة لترى أين تغيّر النوع.
:::

## النسخ خطوة بخطوة

:::animation id="anim-shallow":::

:::quiz id="q-shallow":::

:::change id="ch-copies":::

:::quiz id="q-deep":::

:::mistake
**الثقة في `.copy()` مع بيانات متداخلة**: `config2 = config.copy()` ثم `config2["params"].append(...)`
يعدّل `config["params"]` أيضًا. مع البنى المتداخلة القابلة للتعديل استخدم `copy.deepcopy()`.
:::

:::warning
`deepcopy` أبطأ ويستهلك ذاكرة أكثر لأنها تنسخ كل شيء. لا تستعملها بلا سبب على بيانات ضخمة، ولا حاجة
إليها إذا كانت العناصر كلها immutable. وفي pandas استخدم `df.copy()` (عميقة افتراضيًا للبيانات) عندما
تريد تعديل جدول دون المساس بالأصل.
:::

:::research
أخطاء النسخ السطحي من أخطر الأخطاء في خطوط التحليل لأنها **صامتة**: دالة «تنظيف» تعدّل البيانات
الخام بالخطأ، أو تجربتان تتشاركان قائمة إعدادات. القاعدة الآمنة: الدوال التي تُعيد بيانات «معدّلة»
تعمل على **نسخة عميقة** وتُعيدها، ولا تلمس ما مُرّر إليها.
:::

:::exercise id="ex-safe-update":::

:::under_the_hood
`copy.deepcopy` تحتفظ بقاموس داخلي (memo) للـobjects التي نسختها، فإذا ظهر الـobject نفسه مرتين أو
أشارت البنية إلى نفسها (مرجع دائري) لا تقع في حلقة لانهائية، وتحافظ على شكل المشاركة داخل النسخة.
ويمكن لأي class أن يحدد طريقة نسخه بتعريف `__copy__` و`__deepcopy__`.
:::

:::sketchnote
```text
b = a              alias        same object
b = a.copy()       shallow      new outer, SHARED inner
b = deepcopy(a)    deep         everything new
matters only for MUTABLE inner items (lists, dicts, sets)
nested read: people[0]["langs"][1]  → step by step
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| اسم آخر للـobject نفسه | `b = a` |
| نسخة سطحية | `a.copy()`، `list(a)`، `a[:]`، `dict(d)` |
| نسخة عميقة | `import copy; copy.deepcopy(a)` |
| هل هو الـobject نفسه؟ | `a is b` |
| هل الداخل مشترك؟ | `a[0] is b[0]` |
:::

:::quiz id="q-exit":::

:::docs
- [copy — Shallow and deep copy operations](https://docs.python.org/3/library/copy.html)
- [Programming FAQ: How do I copy an object?](https://docs.python.org/3/faq/programming.html#how-do-i-copy-an-object-in-python)
:::
