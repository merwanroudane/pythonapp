:::question
الباحث الاقتصادي، ومطوّر مواقع الويب، ومهندس الذكاء الاصطناعي، ومدير الأنظمة، يستعملون كلهم
Python. **ما الذي يجعل لغة واحدة مناسبة لكل هذه العوالم المختلفة؟**
:::

محاضرة نظرية عن اللغة نفسها: من أين جاءت، بأي فلسفة صُممت، وأين تتفوق وأين تُحدّها طبيعتها.

## 1. قصة قصيرة

:::theory title="من مشروع هواية إلى لغة عالمية"
- **ديسمبر 1989:** بدأ **Guido van Rossum** العمل على Python في معهد CWI بأمستردام كمشروع
  خلال عطلة، مستلهمًا من لغة تعليمية اسمها ABC.
- **فبراير 1991:** أول إصدار عام، النسخة 0.9.0.
- **1994:** Python 1.0.
- **2000:** Python 2.0 (ومعها list comprehensions).
- **ديسمبر 2008:** Python 3.0، وكسرت التوافق مع Python 2 عمدًا لإصلاح قرارات تصميم قديمة
  (مثل جعل `print` دالة، وجعل النصوص Unicode افتراضيًا).
- **1 يناير 2020:** نهاية دعم Python 2 نهائيًا.

منذ Python 3.9 تصدر **نسخة رئيسية جديدة كل أكتوبر** (PEP 602)، وتُدعم كل نسخة نحو **خمس
سنوات**. لذلك تحمل كل محاضرة هنا شارة `Python ≥ 3.11` توضح النسخة المفترضة.
:::

:::quiz id="q-name":::

:::theory title="من يطوّر Python؟"
Python **مفتوحة المصدر** وتملك حقوقها **Python Software Foundation (PSF)**، وهي منظمة غير ربحية
تأسست عام 2001. تُقترح التغييرات عبر وثائق علنية اسمها **PEP** (Python Enhancement Proposal):
PEP 8 مثلًا دليل أسلوب الكتابة، وPEP 20 هي «Zen of Python».

قاد Guido المشروع لسنوات كـ«BDFL» (القائد مدى الحياة)، ثم تنحى عام 2018، ومنذ 2019 يقود اللغة
**Steering Council** من خمسة أعضاء يُنتخبون من المطورين الأساسيين.
:::

:::quiz id="q-py2":::

## 2. الفلسفة: Zen of Python

:::theory title="اللغة مصممة لتُقرأ"
المبدأ المركزي: **الكود يُقرأ أكثر بكثير مما يُكتب**. لذلك تفضّل Python الوضوح على الاختصار
الذكي، وتجعل الإزاحة (indentation) جزءًا من الصياغة حتى يبدو الكود مرتبًا بالضرورة. هذه
المبادئ جُمعت في قصيدة قصيرة كتبها Tim Peters (PEP 20)، ويمكنك قراءتها من داخل Python نفسها:
:::

:::code mode="script"
import this
:::

:::compare title="البرنامج نفسه: قراءة أعداد وطباعة متوسطها"
**C**

```c
#include <stdio.h>
int main(void) {
    double v[] = {12, 15, 18};
    int n = 3;
    double total = 0;
    for (int i = 0; i < n; i++) {
        total += v[i];
    }
    printf("%.1f\n", total / n);
    return 0;
}
```
|||
**Python**

```python
values = [12, 15, 18]
print(sum(values) / len(values))
```

القراءة أقرب إلى وصف المشكلة نفسها. لكن C تمنحك تحكمًا أكبر وأداءً أعلى في الحلقات الخام.
:::

## 3. ثلاث طبقات: اللغة، المكتبة القياسية، النظام البيئي

:::theory title="ما الذي تحصل عليه عند تثبيت Python؟"
1. **اللغة (the language):** الصياغة والقواعد: `if`، `for`، `def`، الأنواع الأساسية.
2. **المكتبة القياسية (standard library):** مئات الـmodules الجاهزة مع كل تثبيت: الرياضيات،
   التواريخ، الملفات، JSON، الشبكات… ولهذا يقال إن Python **«batteries included»**.
3. **النظام البيئي (ecosystem):** مستودع **PyPI** يضم أكثر من نصف مليون مشروع يمكن تثبيتها
   بـ`pip`: NumPy وpandas للبيانات، Matplotlib للرسوم، scikit-learn وPyTorch للتعلم الآلي،
   Django وFastAPI للويب، وstatsmodels للاقتصاد القياسي.
:::

:::code mode="script"
import sys
import statistics
import datetime

print("Python", sys.version_info.major, sys.version_info.minor)
print(statistics.mean([12, 15, 18]), statistics.stdev([12, 15, 18]))
print(datetime.date(2026, 10, 1) - datetime.date(2026, 9, 24))
:::

:::animation id="anim-batteries":::

:::quiz id="q-exit":::

## 4. أين تُستعمل Python؟

:::theory title="المجالات الرئيسية"
- **علم البيانات والإحصاء:** تنظيف البيانات، التحليل، الرسوم (pandas، NumPy، Matplotlib).
- **الذكاء الاصطناعي والتعلم الآلي:** معظم الأبحاث والأدوات الحديثة (scikit-learn، PyTorch).
- **البحث العلمي والاقتصاد القياسي:** محاكاة، تقدير نماذج، معالجة بيانات كبيرة (SciPy، statsmodels).
- **الأتمتة (automation):** معالجة آلاف الملفات، تقارير دورية، جمع البيانات من الويب.
- **الويب والخدمات الخلفية:** Django، Flask، FastAPI.
- **التعليم:** كثير من الجامعات تعلّم البرمجة بها أولًا بسبب وضوحها.
:::

## 5. الحدود الحقيقية

:::warning
Python ليست الخيار الأمثل لكل شيء، ومعرفة حدودها جزء من إتقانها:

- **سرعة الحلقات الخام:** حلقة Python على ملايين العناصر أبطأ بكثير من C. الحل المعتاد:
  مكتبات مثل NumPy التي تنفّذ العمل الثقيل بكود مُصرَّف (vectorization).
- **الـGIL:** في CPython التقليدي لا تنفّذ أكثر من thread واحد كود Python في اللحظة نفسها.
  بدأت الإصدارات الحديثة (منذ 3.13) بتوفير نسخة اختيارية بلا GIL (free-threaded)، والموضوع
  ما زال يتطور.
- **الأخطاء أثناء التشغيل:** لأن الأنواع ديناميكية، بعض الأخطاء لا تظهر إلا عند تنفيذ السطر؛
  الاختبارات وأدوات الـtype checking تعوّض ذلك.
- **تطبيقات الهاتف والمتصفح:** ليست المجال الأقوى لـPython (JavaScript وSwift وKotlin أشهر هناك).
:::

:::mistake
**«تعلّمت Python من فيديو قديم»**: دروس كثيرة على الإنترنت ما زالت بـPython 2
(`print "x"`، `raw_input()`، قسمة `5 / 2 = 2`). إذا رأيت هذه العلامات فالمصدر قديم.
:::

:::research
للباحث، قوة Python الحقيقية ليست في اللغة وحدها بل في **سلسلة العمل الكاملة**: قراءة البيانات
من أي صيغة، تنظيفها، تحليلها، رسمها، وتصدير الجداول، كل ذلك في سكربت واحد قابل لإعادة التشغيل
والمشاركة. وهي تتكامل مع أدواتك الأخرى (R، Stata، MATLAB، EViews، LaTeX) بدل أن تستبدلها.
:::

:::sketchnote
```text
1989 idea · 1991 v0.9 · 2000 Py2 · 2008 Py3 · 2020 Py2 ends · a new 3.x every October
PSF + PEPs + Steering Council   ·   Zen of Python (PEP 20): readability counts
LANGUAGE  +  STANDARD LIBRARY ("batteries included")  +  PyPI ecosystem (pip)
strong at: data · AI · research · automation · web      limits: raw-loop speed, GIL, mobile
```
:::

:::cheatsheet
| المصطلح | المعنى |
|---|---|
| PSF | المؤسسة المالكة لـPython |
| PEP | وثيقة اقتراح/معيار رسمية |
| Standard library | الـmodules المرفقة مع Python |
| PyPI | مستودع الحزم الخارجية |
| pip | أداة تثبيت الحزم |
| CPython | التطبيق المرجعي لـPython (مكتوب بـC) |
:::

:::docs
- [General Python FAQ](https://docs.python.org/3/faq/general.html)
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/)
- [PEP 602 — Annual Release Cycle](https://peps.python.org/pep-0602/)
- [The Python Standard Library](https://docs.python.org/3/library/index.html)
:::
