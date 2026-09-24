:::question
المعالج لا يفهم إلا أرقامًا ثنائية. فلماذا نكتب `print("مرحبا")` ولا نكتب
`10110000 01100001`؟ **ولماذا توجد مئات لغات البرمجة بدل لغة واحدة؟**
:::

محاضرة نظرية: خريطة لعالم لغات البرمجة، حتى تعرف أين تقف Python ولماذا تتصرف كما تتصرف.

## 1. ما لغة البرمجة؟

:::theory title="لغة صورية: صياغة ومعنى"
**لغة البرمجة (programming language)** لغة **صورية (formal)**: قواعدها دقيقة تمامًا، على عكس
اللغات البشرية التي تحتمل الغموض. لها جانبان:

- **Syntax (الصياغة):** شكل الكود المقبول. هل الأقواس مغلقة؟ هل النقطتان `:` في مكانها؟
  كسرها يعطي `SyntaxError` قبل تنفيذ أي شيء.
- **Semantics (المعنى):** ماذا يفعل الكود الصحيح صياغيًا عند تنفيذه. `"1" + 1` صحيح الصياغة،
  لكن معناه في Python «خطأ نوع».

الجملة «الفكرة الخضراء تنام بغضب» سليمة نحويًا وبلا معنى؛ والكود كذلك قد يكون صحيح الصياغة
وخاطئ المعنى.
:::

## 2. مستويات اللغات

:::theory title="من لغة الآلة إلى لغة الإنسان"
1. **Machine code (لغة الآلة):** أرقام ثنائية ينفّذها المعالج مباشرة. خاصة بكل نوع معالج
   (x86، ARM…)، ولا يكتبها أحد تقريبًا يدويًا.
2. **Assembly (لغة التجميع):** أسماء مختصرة لتعليمات الآلة (`MOV`، `ADD`، `JMP`). ما زالت
   مرتبطة بمعالج معيّن، وتُستعمل في أجزاء صغيرة جدًا تحتاج تحكمًا كاملًا.
3. **High-level languages (لغات عالية المستوى):** قريبة من تفكير الإنسان، مستقلة عن المعالج:
   C، Java، Python، R… سطر واحد منها يقابل عشرات أو مئات تعليمات الآلة.

كلما ارتفع المستوى زادت **الإنتاجية وقابلية القراءة**، وقلّ **التحكم المباشر** بالعتاد.
:::

:::diagram title="من أعلى إلى أسفل: كل مستوى يُترجم إلى الذي تحته"
flowchart TD
    H["High-level: total = price * qty"] --> A["Assembly: MOV / IMUL / MOV"]
    A --> M["Machine code: 10001011 01000101 ..."]
    M --> C["CPU executes"]
:::

## 3. كيف تُترجم اللغة إلى تعليمات؟

:::theory title="Compiler, Interpreter, Bytecode VM, JIT"
- **Compiler (المُصرِّف):** يترجم البرنامج **كاملًا مسبقًا** إلى machine code في ملف تنفيذي.
  التشغيل سريع، والأخطاء الصياغية تُكتشف قبل التشغيل. أمثلة: C، C++، Rust، Go.
- **Interpreter (المُفسِّر):** يقرأ البرنامج وينفّذه مباشرة دون إنتاج ملف machine code. تجربة
  تفاعلية سريعة، لكن التنفيذ أبطأ عادة.
- **Bytecode + Virtual Machine:** مرحلة وسطى: الكود يُترجم إلى **bytecode** (تعليمات مبسطة
  لآلة افتراضية)، ثم تنفّذه **VM**. أمثلة: Java (JVM)، C# (.NET)، و**CPython**.
- **JIT (Just-In-Time):** الـVM تراقب الأجزاء التي تتكرر كثيرًا وتترجمها إلى machine code أثناء
  التشغيل. أمثلة: محركات JavaScript، PyPy، Julia.

هذه صفات **التطبيقات (implementations)** وليست صفات مطلقة للغة: لـPython نفسها تطبيقات مختلفة
(CPython، PyPy…).
:::

:::quiz id="q-compiled":::

## 4. نظام الأنواع (Type System)

:::theory title="محوران مستقلان"
**متى تُفحص الأنواع؟**

- **Static typing:** قبل التشغيل، وللمتغير نوع ثابت يُعلن عنه غالبًا (`int x = 5;` في C/Java).
- **Dynamic typing:** أثناء التشغيل؛ **القيمة** لها نوع، والاسم يمكن أن يشير لاحقًا إلى قيمة من
  نوع آخر. Python ديناميكية.

**هل تُحوَّل الأنواع ضمنيًا؟**

- **Strong typing:** لا تحويل ضمني بين أنواع غير متوافقة: `"1" + 1` خطأ. Python قوية.
- **Weak typing:** تحويل ضمني متساهل: `"1" + 1` تعطي `"11"` في JavaScript.
:::

:::code mode="script"
x = 5
print(type(x).__name__)
x = "five"                  # dynamic: the same name now points to a str
print(type(x).__name__)
print(int("1") + 1, "1" + str(1))   # strong: you convert explicitly
:::

:::quiz id="q-typing":::

:::code mode="script" expect="TypeError"
print("1" + 1)
:::

## 5. الأنماط البرمجية (Paradigms)

:::theory title="طرق مختلفة لتنظيم التفكير"
- **Imperative / Procedural:** سلسلة أوامر تغيّر الحالة خطوة بخطوة، مجمّعة في دوال (C، Python).
- **Object-Oriented (OOP):** البرنامج مجموعة **objects** تجمع البيانات والسلوك (Java، Python).
- **Functional:** البرنامج تركيب **دوال** بلا تعديل للحالة قدر الإمكان (Haskell، وأدوات في Python).
- **Declarative:** تصف **ما** تريد، لا **كيف** (SQL، HTML، الـformulas في R).

Python **متعددة الأنماط (multi-paradigm)**: ستكتب بها إجرائيًا أولًا، ثم ستتعلم الـclasses،
وأدوات functional مثل `map` والـcomprehensions.
:::

:::quiz id="q-declarative":::

## 6. أين تقف Python بين اللغات؟

:::theory title="مقارنة سريعة"
| اللغة | الأنواع | التنفيذ الشائع | الاستخدام الأبرز |
|---|---|---|---|
| C | static، weak | compiled | أنظمة التشغيل، الأجهزة المدمجة |
| Java | static، strong | bytecode + JVM (JIT) | تطبيقات المؤسسات، Android |
| JavaScript | dynamic، weak | JIT في المتصفح | الويب التفاعلي |
| R | dynamic | interpreted | الإحصاء والرسوم |
| Julia | dynamic | JIT (LLVM) | الحوسبة العلمية السريعة |
| SQL | declarative | محرك قاعدة البيانات | الاستعلام عن البيانات |
| **Python** | **dynamic، strong** | **bytecode + VM (CPython)** | **البيانات، الذكاء الاصطناعي، الأتمتة، الويب، البحث** |
:::

:::mistake
**«لغة X هي الأفضل لكل شيء»** و**«اللغات المفسَّرة بطيئة دائمًا»**: كلاهما تبسيط. الأداء يعتمد على
التطبيق والمكتبات: عمليات NumPy في Python تُنفَّذ بكود C محسّن فتكون سريعة جدًا، بينما حلقة
Python عادية على مليون عنصر أبطأ بكثير. اختر اللغة حسب المهمة والنظام البيئي والفريق.
:::

:::research
الباحث يتعامل غالبًا مع عدة لغات: Python للبيانات والأتمتة، R أو Stata أو EViews للاقتصاد
القياسي، SQL لقواعد البيانات، وLaTeX للكتابة. فهم المفاهيم المشتركة (الأنواع، الدوال، الحلقات)
يجعل الانتقال بينها أسهل بكثير من حفظ صياغة كل واحدة.
:::

:::deep_dive
لماذا تهم «strong typing»؟ لأن التحويل الضمني يُخفي الأخطاء: في لغة weak قد يصبح
`"10" + 5` النص `"105"` ويستمر التحليل بقيم خاطئة بصمت. Python تفضل أن تتوقف بـ`TypeError`
وتجبرك على قرار صريح. هذا مثال مبكر على مبدأ من «Zen of Python»: *Errors should never pass
silently*.
:::

:::sketchnote
```text
LANGUAGE = syntax (form) + semantics (meaning)
machine code ← assembly ← high-level      (each level translated to the one below)
compiler: all at once → executable        interpreter: run directly
bytecode + VM: Java, CPython              JIT: hot code → machine code at run time
typing:  static | dynamic     ×     strong | weak
Python = high-level · dynamic + strong · bytecode VM · multi-paradigm
```
:::

:::cheatsheet
| المصطلح | المعنى |
|---|---|
| Syntax / Semantics | الشكل / المعنى |
| Compiler | يترجم البرنامج كاملًا مسبقًا |
| Interpreter | ينفّذ الكود مباشرة |
| Bytecode | تعليمات وسيطة لآلة افتراضية |
| JIT | ترجمة إلى machine code أثناء التشغيل |
| Dynamic typing | الأنواع تُفحص أثناء التنفيذ |
| Strong typing | لا تحويل ضمني بين أنواع غير متوافقة |
| Paradigm | أسلوب تنظيم البرنامج |
:::

:::quiz id="q-exit":::

:::docs
- [The Python Language Reference — Introduction](https://docs.python.org/3/reference/introduction.html)
- [Glossary: bytecode, interpreted, dynamic typing](https://docs.python.org/3/glossary.html)
:::
