:::question
برنامجك يجب أن «يقرر»: هل الطالب ناجح؟ هل الملف موجود؟ هل القيمة مفقودة؟
**كيف يختار البرنامج طريقًا واحدًا من عدة طرق؟**
:::

:::theory title="هياكل التحكم: التسلسل، الاختيار، التكرار"
أثبت Böhm وJacopini عام 1966 أن **أي خوارزمية** يمكن كتابتها بثلاثة هياكل تحكم فقط:

1. **التسلسل (sequence):** نفّذ الخطوات واحدة تلو الأخرى.
2. **الاختيار (selection):** اختر مسارًا حسب شرط، وهذا هو `if / elif / else`.
3. **التكرار (iteration):** كرر خطوات، وهذا هو `for` و`while`.

هذا أساس **البرمجة المهيكلة (structured programming)**. وسلسلة `if / elif / else` تمثل **فروعًا
متنافية (mutually exclusive)**: فرع واحد بالضبط يُنفَّذ. عند تصميمها، تأكد أن الفروع **تغطي كل
الحالات** (ولهذا `else`)، وأن **ترتيبها** صحيح لأن أول شرط صحيح يفوز.
:::

:::concept
الـ`if` تفحص **شرطًا** (expression تُعطي `True` أو `False`). إن كان صحيحًا يُنفَّذ
الـblock المُزاح تحتها، وإلا يُتخطى. `elif` تعني «وإلا إذا…»، و`else` تلتقط كل ما تبقى.
**فرع واحد فقط** من السلسلة يُنفَّذ، وهو أول فرع يصح شرطه.
:::

:::diagram title="مسار التنفيذ في if / elif / else"
flowchart TD
    S([start]) --> C1{"score >= 90 ?"}
    C1 -- True --> A["grade = 'A'"]
    C1 -- False --> C2{"score >= 70 ?"}
    C2 -- True --> B["grade = 'B'"]
    C2 -- False --> C["grade = 'C'"]
    A --> E([print grade])
    B --> E
    C --> E
:::

:::syntax
```python
if condition:  # colon ends the header
    block  # 4-space indentation = inside the if
elif other_condition:
    block
else:
    block
next_line()  # back at the left margin = after the if
```
الإزاحة (indentation) **جزء من الصياغة**: هي التي تحدد أي أسطر داخل الفرع.
:::

:::animation id="anim-grade":::

:::quiz id="q-order":::

:::code mode="script"
score = 95
if score >= 90:
    print("excellent")
elif score >= 50:
    print("pass")
else:
    print("fail")
:::

:::rule
في سلسلة `elif` رتّب الشروط من **الأضيق إلى الأوسع**. عندما يُفحص `score >= 90` أولًا،
يصبح `elif score >= 50` معناه ضمنيًا «بين 50 و89».
:::

## Truthiness: ليس كل شرط True/False صريحًا

:::quiz id="q-truthy":::

:::code mode="script"
for value in [0, 1, "", "hi", [], [0], None, 0.0]:
    print(repr(value), "→", bool(value))
:::

:::tip
`if items:` أوضح من `if len(items) > 0:`. لكن لفحص `None` تحديدًا اكتب
`if x is None:`، لأن `0` و`""` falsy أيضًا وقد تكون قيمًا صالحة.
:::

## and / or وshort-circuit

:::code mode="script"
x = 0
safe = x != 0 and 10 / x > 1
print(safe)

name = ""
display = name or "Anonymous"
print(display)
:::

:::concept
`and` تتوقف عند أول قيمة falsy، و`or` تتوقف عند أول قيمة truthy. لذلك لا يُحسب
`10 / x` عندما يكون `x` صفرًا. وتُعيد `or` القيمة نفسها لا `True`/`False`، ولهذا يُستخدم
`name or "Anonymous"` لقيمة افتراضية.
:::

:::mistake
```python
if score >= 50
    print("pass")          # SyntaxError: expected ':'

if score >= 50:
print("pass")              # IndentationError: expected an indented block
```
:::

:::code mode="script" expect="syntax_error"
score = 60
if score >= 50
    print("pass")
:::

:::research
في تنظيف البيانات تُستخدم الشروط لتصنيف الحالات: قيمة مفقودة، قيمة مستحيلة (عمر سالب)،
أو قيمة صالحة. رتّب الفحوص بحيث يُكشف المفقود أولًا قبل أي عملية حسابية عليه.
:::

:::exercise id="ex-label":::

:::deep_dive
للاختيار بين قيمتين في سطر واحد يوجد **conditional expression**:
`label = "adult" if age >= 18 else "minor"`. هي expression تُنتج قيمة، فتصلح داخل
`print` أو على يمين `=`، لكنها لا تناسب المنطق الطويل. ولحالات كثيرة على شكل قيمة ثابتة
توجد `match/case` (structural pattern matching) في مسار متقدم.
:::

:::sketchnote
```text
if   A:  ─ first True wins ─►  run ONE block
elif B:                        skip the rest
else:    ─ nothing matched

falsy:  False  None  0  0.0  ""  []  {}  set()
and → stops at first falsy     or → stops at first truthy
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| فرعان | `if c: ... else: ...` |
| عدة حالات | `if / elif / elif / else` |
| قيمة في سطر | `a if c else b` |
| فحص None | `if x is None:` |
| قيمة افتراضية | `x or default` |
| شرطان معًا | `if a and b:` |
:::

:::quiz id="q-exit":::

:::docs
- [if Statements — Python Tutorial](https://docs.python.org/3/tutorial/controlflow.html#if-statements)
- [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
- [Boolean operations](https://docs.python.org/3/reference/expressions.html#boolean-operations)
:::
