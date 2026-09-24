:::question
لماذا أستطيع **رؤية** نتيجة `print()` لكنني لا أستطيع **تخزينها** في متغير؟
:::

:::theory title="الدالة كتجريد: الواجهة والتنفيذ"
- الدالة في الرياضيات **تحويل** من مدخلات إلى مخرج: `f(x) = 2x`. في البرمجة، `return` هو ما يجعل
  الدالة قريبة من هذا المعنى: تعطي **قيمة** يمكن استعمالها في حساب آخر: `f(g(x))`.
- **التجريد (abstraction)**: من يستدعي الدالة يحتاج فقط **واجهتها (interface)**: اسمها، ما تستقبله،
  وما تُعيده. أما **تنفيذها (implementation)** الداخلي فيمكن تغييره دون أن يتأثر أحد.
- **الدالة النقية (pure function)** تعتمد على مدخلاتها فقط وتُعيد نتيجة دون آثار جانبية. هي الأسهل
  في الفهم والاختبار وإعادة الاستخدام. أما `print` داخل الدالة فهو **أثر جانبي**: مفيد للعرض، لكنه
  لا يعطي الكود أي قيمة.
:::

:::quiz id="q-result":::

:::concept
للدالة طريقتان مختلفتان تمامًا لـ«إخراج» شيء:

- **`print(value)`** يرسل **نصًا** إلى stdout. هو موجَّه **للإنسان** الذي ينظر إلى الشاشة.
- **`return value`** يرسل **object** إلى الـ**caller**، أي إلى السطر الذي استدعى الدالة.
  هو موجَّه **لبقية البرنامج**.

في مثال بسيط قد يبدو الاثنان متشابهين لأن كليهما «يُظهر» 10. لكن واحدًا فقط يعطي
الكود قيمة يستطيع استخدامها.
:::

## شاهد call frame خطوة بخطوة

:::animation id="anim-print":::

:::diagram kind="text" title="print: النص يذهب إلى الشاشة، والـcaller يستلم None"
Caller
  │ double(5)
  ▼
Function frame   x = 5
  │ print(10)
  ├────────────► stdout: 10
  │
  └────────────► implicit return None

result = None
:::

:::animation id="anim-return":::

:::diagram kind="text" title="return: الـobject يعود إلى الـcaller"
Function frame   x = 5
  │
  └────────────► return object 10
                        │
                        ▼
                   result = 10
:::

:::compare title="print مقابل return"
| الخاصية | `print()` |
|---|---|
| يعرض للمستخدم | نعم |
| يعطي قيمة للـcaller | لا (`None`) |
| يمكن تخزين الناتج | لا |
| ينهي الدالة | لا |
| الاستخدام | عرض / تشخيص |
|||
| الخاصية | `return` |
|---|---|
| يعرض للمستخدم | ليس بالضرورة |
| يعطي قيمة للـcaller | نعم |
| يمكن تخزين الناتج | نعم |
| ينهي الدالة | نعم، فورًا |
| الاستخدام | منطق قابل لإعادة الاستخدام |
:::

:::change id="ch-print-return":::

:::quiz id="q-after-return":::

:::mistake
```python
x = print(5)
print(x + 1)  # TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
```
`print(5)` عرضت 5 ثم أعادت `None`، فأصبح `x` هو `None`. رسالة فيها `NoneType` بعد
استدعاء دالة كتبتها أنت تعني غالبًا: **نسيت `return`**.
:::

:::code mode="script"
x = print(5)
print(x + 1)
:::

:::research
افصل **الحساب** عن **العرض**. دالة تنظف متغيرًا أو تحسب إحصاءات تُعيد النتيجة، ودالة
أخرى (أو الـcaller) تقرر كيف تعرضها:

```python
def summary(values):
    n = len(values)
    mean = sum(values) / n
    return {"n": n, "mean": mean, "min": min(values), "max": max(values)}


stats = summary([12, 15, 11, 18])  # reusable: report, test, next pipeline step
print(f"n={stats['n']}, mean={stats['mean']:.2f}")
```
:::

:::code mode="notebook"
def summary(values):
    n = len(values)
    mean = sum(values) / n
    return {"n": n, "mean": mean, "min": min(values), "max": max(values)}

stats = summary([12, 15, 11, 18])
stats
:::

:::exercise id="ex-mean":::

:::under_the_hood
عند الاستدعاء يُنشئ Python **call frame** جديدًا فيه الـlocal names (هنا `x`). `return`
يأخذ قيمة الـexpression، يُغلق الـframe، ويسلّم الـobject إلى المكان الذي حدث فيه
الاستدعاء؛ فيحل `double(5)` في السطر `result = double(5)` محل القيمة 10. وإن وصل التنفيذ
إلى نهاية الدالة بلا `return` فكأنه نفّذ `return None`.
:::

:::sketchnote
```text
print(value)  → stdout → the HUMAN sees text      → returns None
return value  → caller → the PROGRAM gets object  → function ends

no return  ⇒  return None
"NoneType" error after your own function?  → forgot return
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| أعِد قيمة | `return result` |
| أعِد عدة قيم | `return a, b` (tuple) |
| إنهاء مبكر | `if bad: return None` |
| عرض للمستخدم | `print(...)` خارج دالة الحساب |
:::

:::quiz id="q-exit":::

:::docs
- [The return statement](https://docs.python.org/3/reference/simple_stmts.html#the-return-statement)
- [Defining Functions — Python Tutorial](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
:::
