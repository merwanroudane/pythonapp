:::question
`print("Hello, Python")` — سطر واحد يكتبه الجميع أولًا. لكن **ما الذي يراه Python
فعلًا في هذا السطر؟** كم «قطعة» فيه، وما دور كل واحدة؟
:::

:::theory title="الدالة، الاستدعاء، والأثر الجانبي"
- **الدالة (function)** عملية لها اسم يمكن تنفيذها مرات كثيرة. تخيلها **صندوقًا أسود**: تعطيه
  مدخلات (arguments)، فيقوم بعمل، وقد يُعيد قيمة.
- **الاستدعاء (call)** هو تنفيذ الدالة الآن، ويُكتب بالأقواس: `print(...)`. الاسم وحده `print`
  يشير إلى الدالة دون تشغيلها.
- **الدوال المدمجة (built-in functions)** مثل `print` و`len` متاحة دائمًا دون `import`.
- للدالة نوعان من النتائج: **قيمة مُعادة (return value)** يستلمها الكود، و**أثر جانبي (side
  effect)** يغيّر شيئًا في العالم الخارجي. وظيفة `print` كلها أثر جانبي: الكتابة في قناة **stdout**،
  أما قيمتها المُعادة فهي `None`.
:::

:::code mode="script"
print("Hello, Python")
:::

:::syntax
```text
print   (   "Hello, Python"   )
└─┬─┘   │   └──────┬──────┘   │
 name   │    string literal   │
        └── call ── argument ─┘
```

| القطعة | ما هي؟ | ماذا تفعل؟ |
|---|---|---|
| `print` | **name** يشير إلى built-in function | يحدد *ماذا* نستدعي |
| `( )` | **call syntax** | يأمر بتنفيذ الدالة الآن |
| `"Hello, Python"` | **string literal** | يُنشئ object من نوع `str` |
| داخل الأقواس | **argument** | القيمة التي نمررها للدالة |
:::

:::concept
`print` ليست كلمة سحرية في اللغة، بل **اسم** لدالة جاهزة. الأقواس هي التي تستدعيها.
والنص بين علامتي التنصيص قيمة (object) تُمرَّر إليها، فتحولها `print` إلى نص وتكتبه في
**stdout**: القناة التي تظهر لك في الـterminal أو تحت الخلية.
:::

## عدة قيم في استدعاء واحد

:::code mode="script"
name = "Sara"
age = 30
print("Name:", name, "Age:", age)
:::

لاحظ أن `print` وضعت مسافة بين القيم تلقائيًا، وحوّلت الرقم `30` إلى نص. هذه المسافة
ليست سحرًا؛ إنها قيمة parameter اسمه `sep`.

:::syntax
```python
print(*objects, sep=" ", end="\n", file=None, flush=False)
```
- `*objects`: أي عدد من القيم.
- `sep`: ما يوضع **بين** القيم (الافتراضي مسافة).
- `end`: ما يُكتب **بعد** آخر قيمة (الافتراضي سطر جديد `\n`).
:::

:::quiz id="q-sep-end":::

:::change id="ch-sep-end":::

## الأخطاء الأولى

:::mistake
```python
Print("Hello")      # NameError: name 'Print' is not defined
print "Hello"       # SyntaxError: Missing parentheses in call to 'print'
```
Python يفرّق بين الحروف الكبيرة والصغيرة (case-sensitive)، فـ`Print` اسم غير موجود.
والصيغة بلا أقواس كانت في Python 2 فقط.
:::

جرّب بنفسك: شغّل الكود، ثم اقرأ بطاقة الخطأ. هل تقترح عليك المنصة الاسم الصحيح؟

:::code mode="script"
pritn("Hello")
:::

:::exercise id="ex-date":::

:::under_the_hood
`print` تستدعي `str()` على كل قيمة، تضم النتائج بـ`sep`، تضيف `end`، ثم تكتب الناتج
إلى `sys.stdout`. وبعد ذلك **تُعيد `None`**. لهذا `x = print("hi")` يطبع `hi` لكن
قيمة `x` تكون `None`.
:::

:::sketchnote
```text
print( A , B , C , sep="-" , end="!" )
       │   │   │
       A - B - C !
         └─sep─┘  └─end
stdout  ←  text for humans
return  →  None
```
:::

:::cheatsheet
| الهدف | الكود | الناتج |
|---|---|---|
| قيم متعددة | `print("a", 1)` | `a 1` |
| فاصل مخصص | `print("a", "b", sep=",")` | `a,b` |
| بلا سطر جديد | `print("a", end="")` | `a` |
| سطر فارغ | `print()` | |
:::

:::quiz id="q-exit":::

:::docs
- [print() — Built-in Functions](https://docs.python.org/3/library/functions.html#print)
:::
