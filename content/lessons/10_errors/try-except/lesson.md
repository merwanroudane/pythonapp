:::question
برنامجك يقرأ 10,000 سطر، وفي السطر 7,431 قيمة `"N/A"` بدل رقم، فيتوقف كل شيء برسالة حمراء
طويلة. **ماذا تقول هذه الرسالة فعلًا؟ وكيف تجعل البرنامج يتعامل مع الحالة بدل أن ينهار؟**
:::

:::theory title="نماذج معالجة الأخطاء: رموز الخطأ مقابل الاستثناءات"
- **رموز الخطأ (error codes)**: في لغة مثل C تُعيد الدالة قيمة خاصة (`-1` أو `NULL`) عند الفشل،
  وعلى المستدعي فحصها بعد **كل** استدعاء. نسيان فحص واحد يعني استمرار البرنامج بقيم خاطئة.
- **الاستثناءات (exceptions)**: عند الفشل تُرفع (raise) إشارة تقطع التنفيذ و**تصعد في سلسلة
  الاستدعاءات (call stack)**، إطارًا بعد إطار، حتى تجد `except` مناسبًا. إن لم تجده يتوقف البرنامج
  ويطبع الـtraceback. هذا يسمى **stack unwinding**، ويعني أن الخطأ لا يمر بصمت.
- أسلوبان للتفكير: **LBYL** (Look Before You Leap): افحص قبل أن تفعل (`if key in d:`)، و**EAFP**
  (Easier to Ask Forgiveness than Permission): افعل ثم التقط الاستثناء (`try: d[key]`).
  ثقافة Python تميل كثيرًا إلى EAFP.
:::

:::concept
أربعة أنواع من «المشاكل» مختلفة تمامًا:

- **Syntax error**: لا يستطيع Python قراءة الكود؛ لا يُنفَّذ أي سطر.
- **Runtime exception**: الكود صحيح الصياغة لكن عملية فشلت أثناء التنفيذ (`ValueError`،
  `KeyError`…). يمكن **التقاطها ومعالجتها**.
- **Logical error**: لا رسالة أبدًا، لكن النتيجة خاطئة. أخطرها.
- **Warning**: البرنامج يستمر، لكن هناك سلوك يحتاج انتباهك.
:::

## اقرأ الـtraceback من الأسفل

:::code mode="script" expect="ValueError"
def parse_age(text):
    return int(text)

def load(rows):
    return [parse_age(r) for r in rows]

load(["30", "N/A", "25"])
:::

:::quiz id="q-read":::

:::syntax
```text
Traceback (most recent call last):
  File "<lesson>", line 7, in <module>        ← 3. how we got there (outermost call)
    load(["30", "N/A", "25"])
  File "<lesson>", line 5, in load            ← 2. the call chain
    return [parse_age(r) for r in rows]
  File "<lesson>", line 2, in parse_age       ← 1. WHERE it happened
    return int(text)
ValueError: invalid literal for int() with base 10: 'N/A'    ← 0. WHAT happened — start here
```
:::

## try / except / else / finally

:::syntax
```python
try:
    risky()                 # code that may raise
except ValueError as err:   # runs only for this exception type
    handle(err)
else:
    on_success()            # runs only if try raised nothing
finally:
    cleanup()               # runs ALWAYS, error or not
```
:::

:::animation id="anim-try":::

:::quiz id="q-flow":::

:::code mode="script"
def ratio(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("b is zero → returning None")
        return None
    else:
        print("ok")
        return result
    finally:
        print("finally always runs")

print(ratio(6, 3))
print(ratio(1, 0))
:::

## ارفع استثناء بنفسك

:::code mode="script" expect="ValueError"
def set_age(age):
    if age < 0:
        raise ValueError(f"age must be >= 0, got {age}")
    return age

print(set_age(30))
print(set_age(-2))
:::

:::rule
- التقط **أضيق** نوع تتوقعه (`ValueError`، لا `Exception`).
- اجعل الـ`try` صغيرًا: السطر الذي قد يفشل فقط.
- إن لم تكن تعرف كيف تعالج الخطأ **فلا تلتقطه**؛ دعه يظهر.
- ارفع استثناءً برسالة تذكر القيمة الفعلية المخالفة.
:::

:::mistake
```python
try:
    total = compute(data)
except:
    pass            # swallows NameError, KeyError, even Ctrl+C… silently
print(total)        # NameError later, far from the real cause
```
:::

:::warning
الـ`try/except` ليس بديلًا عن فحص صحة البيانات. إن كانت 30% من القيم `"N/A"` فالمشكلة في
البيانات وتحتاج قرارًا واعيًا (قيمة مفقودة؟ حذف؟ إبلاغ؟)، لا تجاهلًا صامتًا داخل `except`.
:::

:::research
في تنظيف البيانات: التقط الخطأ، لكن **سجّل** ما تخطيته (أي صف، أي قيمة، لماذا). عدد الصفوف
المستبعدة وسببها جزء من تقرير منهجي شفاف، ويسمح لغيرك بإعادة إنتاج قرارك.
:::

:::exercise id="ex-safe-int":::

:::deep_dive
`raise NewError(...) from err` يربط استثناءً جديدًا بالأصلي (exception chaining) فيظهر الاثنان
في الـtraceback: «The above exception was the direct cause…». ويمكن تعريف استثناءاتك الخاصة
بـ`class DataError(ValueError): pass` لتلتقطها طبقة أعلى بدقة.
:::

:::sketchnote
```text
TRACEBACK → read BOTTOM-UP:  type+message → where → how we got there
try:      risky line only
except X: the narrowest expected type        never:  except: pass
else:     only if no exception
finally:  always (cleanup)
raise ValueError(f"... got {value}")
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| التقاط نوع محدد | `except ValueError:` |
| عدة أنواع | `except (ValueError, TypeError):` |
| الوصول للرسالة | `except ValueError as err:` |
| كود عند النجاح | `else:` |
| تنظيف دائم | `finally:` |
| رفع خطأ | `raise ValueError("...")` |
:::

:::quiz id="q-exit":::

:::docs
- [Errors and Exceptions — Python Tutorial](https://docs.python.org/3/tutorial/errors.html)
- [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
- [traceback module](https://docs.python.org/3/library/traceback.html)
:::
