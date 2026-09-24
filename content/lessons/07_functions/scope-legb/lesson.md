:::question
عرّفت `tax` داخل دالة، ثم حاولت طباعته بعد الاستدعاء فظهر `NameError`. لكن الدالة نفسها
استطاعت قراءة `rate` المعرّف خارجها. **من يقرر أي اسم «مرئي» في أي مكان؟**
:::

:::theory title="الـnamespaces والنطاق المعجمي"
- **Namespace** جدول يربط الأسماء بالـobjects، وفي CPython هو فعلًا قاموس في أغلب الحالات: جرّب
  `globals()`. لكل namespace **عمر**: الـbuilt-ins تعيش ما دام الـinterpreter يعمل، والـglobals حتى
  نهاية الـmodule، والـlocals لمدة استدعاء واحد فقط.
- **النطاق المعجمي (lexical / static scoping)**: ما يراه الكود يتحدد بمكان **كتابته** في الملف،
  لا بمكان **استدعائه**. الدالة الداخلية ترى متغيرات الدالة التي كُتبت داخلها (Enclosing)، مهما كان
  من استدعاها.
- ويقرر Python نطاق كل اسم داخل دالة **عند تحويلها إلى bytecode**: وجود إسناد إلى الاسم في الجسم
  يجعله local في الجسم كله.
:::

:::concept
الـ**scope** هو المنطقة التي يكون فيها الاسم مرئيًا. كل استدعاء دالة ينشئ **local scope**
جديدًا يختفي عند انتهاء الاستدعاء. وعندما يقرأ الكود اسمًا، يبحث Python بترتيب **LEGB** ويتوقف
عند أول مكان يجده فيه:

1. **L**ocal — داخل الدالة الحالية.
2. **E**nclosing — داخل الدوال التي تحيط بها (دوال متداخلة).
3. **G**lobal — على مستوى الـmodule (الملف).
4. **B**uilt-in — أسماء Python الجاهزة: `print`، `len`، `sum`…
:::

:::diagram title="LEGB: من الأقرب إلى الأبعد"
flowchart LR
    L["Local"] -->|not found| E["Enclosing"]
    E -->|not found| G["Global"]
    G -->|not found| B["Built-in"]
    B -->|not found| X["NameError"]
:::

:::animation id="anim-legb":::

:::code mode="script" expect="NameError"
def outer():
    message = "from outer"        # enclosing for inner()

    def inner():
        print(message)            # found in Enclosing
        print(len(message))       # len found in Built-in

    inner()

outer()
print(message)                    # NameError: not visible here
:::

## القراءة سهلة، الإسناد شيء آخر

:::quiz id="q-unbound":::

:::code mode="script" expect="UnboundLocalError"
count = 0

def increment():
    count = count + 1
    return count

increment()
:::

:::concept
Python يقرر نطاق الاسم **عند قراءة الدالة**، لا أثناء التنفيذ: إن وُجد إسناد إلى الاسم في أي
مكان داخل جسمها فهو local في الجسم كله. الحل الواضح ليس `global` بل تمرير القيمة وإعادتها.
:::

:::compare title="global مقابل parameter + return"
**`global` — يعمل لكنه هش**

```python
total = 0
def add(x):
    global total
    total += x
```
الدالة تعتمد على حالة مخفية، ونتيجتها تتغير حسب ما حدث قبلها. صعبة الاختبار.
|||
**parameter + return — نقية**

```python
def add(total, x):
    return total + x

total = add(total, 5)
```
كل ما تحتاجه يدخل كـargument، وكل ما تنتجه يخرج بـ`return`.
:::

:::quiz id="q-shadow":::

:::mistake
**تظليل (shadowing) أسماء built-in**:

```python
list = [1, 2, 3]
list("abc")          # TypeError: 'list' object is not callable
```
في Notebook يبقى هذا الاسم «مكسورًا» حتى تحذفه (`del list`) أو تعيد تشغيل الـkernel.
:::

:::research
الدوال النقية (كل المدخلات parameters، وكل المخرجات `return`) هي أساس التحليل القابل لإعادة
الإنتاج: يمكن اختبارها منفردة، وتشغيلها بالترتيب نفسه يعطي النتيجة نفسها دائمًا، بلا اعتماد على
متغير عام عدّلته خلية أخرى في الـnotebook.
:::

:::exercise id="ex-noglobal":::

:::deep_dive
للدوال المتداخلة كلمة `nonlocal`: تسمح لدالة داخلية بإعادة ربط اسم في الـEnclosing scope.
هذا أساس **closures** (دالة تتذكر متغيرات الدالة التي أنشأتها)، وهي بدورها أساس
**decorators**، وسنصل إليها في مسار Functions المتقدم.
:::

:::sketchnote
```text
LEGB   Local → Enclosing → Global → Built-in → NameError
assignment inside a def  ⇒  the name is LOCAL in the whole def
                            read before assign → UnboundLocalError
prefer:  parameters in, return out      avoid:  global
never name a variable  list / sum / max / id / type
```
:::

:::cheatsheet
| الحالة | ما يحدث |
|---|---|
| قراءة اسم عام داخل دالة | مسموح (Global) |
| إسناد لاسم داخل دالة | ينشئ local |
| قراءة قبل الإسناد في الدالة | `UnboundLocalError` |
| تعديل عام من الداخل | `global x` (تجنّبه) |
| تعديل Enclosing | `nonlocal x` |
| اسم غير موجود في أي مكان | `NameError` |
:::

:::quiz id="q-exit":::

:::docs
- [Resolution of names — Execution model](https://docs.python.org/3/reference/executionmodel.html#resolution-of-names)
- [Python Scopes and Namespaces — Tutorial](https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces)
:::
