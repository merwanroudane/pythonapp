:::question
«اطلب من المستخدم رقمًا، وأعد السؤال **حتى** يُدخل رقمًا صالحًا». كم مرة ستتكرر الحلقة؟
لا أحد يعرف مسبقًا. **كيف نكرر شيئًا عددًا غير معروف من المرات؟**
:::

:::theory title="الانتهاء: كيف نضمن أن الحلقة تتوقف؟"
حلقة `while` صحيحة يجب أن **تنتهي**. ولإثبات ذلك يفكر المبرمجون في مفهومين:

- **Loop variant (كمية متناقصة):** قيمة تقترب من شرط التوقف في كل دورة، مثل `n` الذي ينقص حتى
  يصل إلى 0. إن لم توجد، فالحلقة قد لا تنتهي.
- **Loop invariant (خاصية ثابتة):** عبارة تبقى صحيحة قبل كل دورة وبعدها، مثل «`total` يساوي مجموع
  العناصر التي عالجناها حتى الآن». تساعدك على التأكد أن النتيجة صحيحة عند الخروج.

وقد أثبت Alan Turing عام 1936 أنه **لا توجد خوارزمية عامة** تستطيع أن تقرر لأي برنامج إن كان
سيتوقف أم لا (**Halting Problem**). لذلك لا يمكن للحاسوب أن يحميك تلقائيًا من كل حلقة لانهائية؛
أنت من يفكر في الانتهاء.
:::

:::concept
الـ`while` تكرر جسمها **ما دام** الشرط صحيحًا. هي لا تمر على عناصر مثل `for`، بل تعتمد على
**حالة (state)** تتغير داخل الحلقة. ولكي تتوقف يومًا ما، يجب أن يغيّر الجسم شيئًا يجعل الشرط
خاطئًا في النهاية.
:::

:::diagram title="دورة while"
flowchart LR
    C{"condition?"} -- True --> B["body"]
    B --> U["update state"]
    U --> C
    C -- False --> E(["after the loop"])
:::

:::animation id="anim-countdown":::

:::quiz id="q-count":::

## نمط التحقق من المدخلات

الكود التالي يقرأ من `input()`. القيم في صندوق **Inputs** تُمرَّر بالترتيب، كأن المستخدم
كتبها: نص خاطئ، ثم رقم سالب، ثم رقم صالح.

:::code mode="script" inputs="abc\n-4\n27"
while True:
    text = input("Age? ")
    if not text.isdigit():
        print("  please type digits only")
        continue
    age = int(text)
    if age == 0:
        print("  age must be positive")
        continue
    break
print("OK, age =", age)
:::

:::rule
`while True:` + `break` هو النمط المعتاد عندما يكون شرط الخروج **في منتصف** الجسم. تأكد أن
كل مسار في الحلقة إما يصل إلى `break` أو يغيّر شيئًا يقرّبك منه.
:::

## الحلقة اللانهائية

:::mistake
```python
n = 3
while n > 0:
    print(n)
# forgot:  n = n - 1   → n stays 3 forever
```
شغّل الكود أدناه: ستوقفه المنصة بعد بضع ثوانٍ (timeout). في الـterminal أوقفه بـ`Ctrl` + `C`،
وفي Jupyter بزر **Interrupt kernel**.
:::

:::code mode="script" expect="timeout"
n = 3
while n > 0:
    n = n  # the state never changes
:::

:::compare title="for أم while؟"
**`for`**

- المرور على قائمة، نص، ملف، `range`.
- عدد الدورات معروف من الـiterable.
- لا خطر حلقة لانهائية في الحالات العادية.
|||
**`while`**

- التكرار حتى يتحقق شرط.
- عدد الدورات غير معروف مسبقًا.
- **أنت** مسؤول عن تحديث الحالة.
:::

:::research
الخوارزميات التكرارية في الإحصاء تعمل بهذا الشكل: كرر التحديث **حتى** يصبح التغير أقل من
tolerance، مع حد أقصى لعدد الدورات للأمان:

```python
it, change = 0, 1.0
while change > 1e-8 and it < 1000:
    ...           # update the estimate, recompute change
    it += 1
```
:::

:::exercise id="ex-collatz":::

:::deep_dive
للحلقة `while` جزء `else` أيضًا، ويُنفَّذ عندما يصبح الشرط خاطئًا **دون** `break`، تمامًا
كما في `for … else`. ويمكن استخدام walrus لقراءة وفحص في سطر واحد:
`while (line := f.readline()):`.
:::

:::sketchnote
```text
while condition:     check → body → update → check …
    body
    update!          no update  →  infinite loop

while True:          exit condition in the middle
    …
    if ok: break

unknown number of repetitions → while     known iterable → for
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| عدّ تنازلي | `while n > 0: …; n -= 1` |
| حتى تتحقق حالة | `while not done:` |
| خروج من المنتصف | `while True: … break` |
| حد أمان | `while cond and it < max_it:` |
:::

:::quiz id="q-exit":::

:::docs
- [The while statement](https://docs.python.org/3/reference/compound_stmts.html#the-while-statement)
- [break and continue](https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements)
:::
