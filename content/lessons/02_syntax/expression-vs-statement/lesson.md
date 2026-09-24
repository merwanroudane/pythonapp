:::question
في Jupyter كتبت `x` في آخر الخلية فظهرت قيمته. نسخت الكود نفسه إلى `analysis.py`
وشغّلته… **فلم يظهر شيء.** هل الكود معطّل؟
:::

:::theory title="قواعد اللغة: عبارات لها قيمة وجمل تنفّذ"
البرنامج في Python **سلسلة من الـstatements** تُنفَّذ بالترتيب، وكل statement قد يحتوي
**expressions**.

- **Expression** تشبه في العربية «العبارة» التي تُختصر إلى **قيمة**: `3 * 4` تساوي 12. تقييمها
  (evaluation) يتم من الداخل إلى الخارج، فالتعبير الكبير شجرة من تعابير أصغر.
- **Statement** تشبه «الجملة الفعلية» التي **تفعل شيئًا**: تربط اسمًا (`x = …`)، تتحكم في
  مسار التنفيذ (`if`، `for`)، أو تستورد (`import`).

قاعدة للتمييز: إن استطعت وضعه بعد `print(` أو على يمين `=` فهو expression.
:::

:::concept
في Python نوعان من الأسطر:

- **Expression**: شيء له **قيمة**: `2 + 3`، `len(name)`، `x`، `"a" * 3`.
  اختبار سريع: هل يمكن وضعه على يمين `=`؟
- **Statement**: **فعل** ينفّذ شيئًا: `x = 5`، `import math`، `if ...:`، `for ...:`.

الـexpression وحدها في سطر تُحسب قيمتها، ثم **تُهمل** إلا إذا كانت البيئة تعرضها لك.
:::

:::compare title="نفس الكود، بيئتان"
**Script `.py`**

```python
x = 5
x  # computed, then discarded
```
لا يظهر شيء. البرنامج لا يطبع إلا ما تطلب طباعته.
|||
**Notebook / REPL**

```python
x = 5
x  # last expression → displayed
```
يظهر `5` لأن الواجهة تعرض `repr` لآخر expression في الخلية.
:::

## جرّب بنفسك: بدّل وضع التنفيذ

اختر **Script mode** ثم **Notebook mode** وشغّل الكود نفسه. راقب تبويب *Result*.

:::code mode="script" switch="true"
price = 12.5
quantity = 4
price * quantity
:::

:::quiz id="q-script":::

:::quiz id="q-middle":::

:::code mode="notebook"
a = 1
a + 1
a + 2
:::

:::rule
في الـscripts وداخل الدوال: إن أردت أن **ترى** قيمة فاستخدم `print()`. العرض التلقائي
راحة في الـNotebook، وليس جزءًا من لغة Python.
:::

:::warning
لا تعتمد على العرض التلقائي لإثبات أن الحساب صحيح في تحليل حقيقي. خلية تعرض رقمًا
جميلًا في المنتصف قد تُخفي أن النتيجة لم تُخزَّن في متغير ولن تُستخدم لاحقًا.
:::

:::mistake
```python
total = price * quantity
total  # in a .py file: shows nothing, and people think the code "does nothing"
```
الكود يعمل؛ القيمة محسوبة ومخزنة في `total`. الذي ينقص هو `print(total)` فقط.
:::

:::exercise id="ex-classify":::

:::under_the_hood
عندما يقرأ Python الكود يبني منه **AST** (Abstract Syntax Tree). السطر الذي هو expression
وحدها يُمثَّل بعقدة `Expr`. الـNotebook (IPython) يفحص آخر عقدة في الخلية: إن كانت `Expr`
يحسبها بشكل خاص ويعرض `repr` نتيجتها ما لم تكن `None`. هذه المنصة تفعل الشيء نفسه في
Notebook mode.

```python
import ast

print(ast.dump(ast.parse("x * 2").body[0]))
```
:::

:::sketchnote
```text
EXPRESSION  → has a value      2 + 3    len(s)    x
STATEMENT   → does something   x = 5    import    for / if / def

.py file :  bare expression → computed, discarded
Notebook :  LAST bare expression → repr shown
```
:::

:::cheatsheet
| أريد أن… | في `.py` | في Notebook |
|---|---|---|
| أرى قيمة | `print(x)` | `x` في آخر الخلية |
| أرى عدة قيم | `print(a, b)` | `print` أو `display` |
| أخفي قيمة آخر سطر | — | أضف `;` في النهاية |
:::

:::docs
- [Expressions — The Python Language Reference](https://docs.python.org/3/reference/expressions.html)
- [Simple statements](https://docs.python.org/3/reference/simple_stmts.html)
- [ast — Abstract Syntax Trees](https://docs.python.org/3/library/ast.html)
:::
