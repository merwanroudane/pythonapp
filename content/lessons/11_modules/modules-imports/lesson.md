:::question
مشروعك وصل إلى 800 سطر في ملف واحد، وتريد استعمال دالة التنظيف نفسها في مشروع آخر. هل تنسخها
وتلصقها؟ **كيف يستعمل ملف Python كودًا مكتوبًا في ملف آخر؟**
:::

:::theory title="الـmodule والـnamespace"
**الـmodule** أي ملف `.py`. عندما تستورده يُنشئ Python **module object** له **namespace** خاص: جدول
بكل الأسماء المعرّفة في الملف (دوال، متغيرات، classes).

- `import math` يربط اسمًا واحدًا، `math`، بالـmodule كله، فتصل إلى محتواه بالنقطة: `math.sqrt`.
- الـnamespaces تمنع التصادم: `math.log` و`numpy.log` دالتان مختلفتان باسم واحد.
- **الـpackage** مجلد يجمع modules (غالبًا مع `__init__.py`)، مثل `collections` أو `pandas`.
- الأنواع ثلاثة: **المكتبة القياسية** (تأتي مع Python)، **حزم خارجية** (تُثبَّت بـpip)، و**modulesك
  أنت** (ملفات مشروعك).
:::

:::syntax
```python
import math                     # the whole module; use math.sqrt(2)
import numpy as np              # with a short alias
from pathlib import Path        # one name into your namespace
from math import pi, sqrt       # several names
from math import *              # everything — avoid: you cannot see where names come from
```
:::

:::code mode="script"
import math
import statistics as stats
from collections import Counter

print(math.sqrt(16), math.pi)
print(stats.median([3, 1, 4, 1, 5]))
print(Counter("hello"))
print(type(math).__name__, math.__name__)
:::

## كيف يجد Python الـmodule؟

:::theory title="sys.path وsys.modules"
عند `import name` يمر Python بخطوتين:

1. يبحث أولًا في **`sys.modules`**، ذاكرة الـmodules المستوردة مسبقًا. إن وجده أعاده فورًا، ولهذا
   **يُنفَّذ الـmodule مرة واحدة فقط** مهما تكرر الـimport.
2. وإلا يبحث في المجلدات المذكورة في **`sys.path` بالترتيب**: مجلد السكربت، ثم المكتبة القياسية، ثم
   `site-packages` للحزم المثبتة. أول ملف يطابق الاسم يُنفَّذ ويُخزَّن.

إذا لم يجده في أي مجلد ظهر **`ModuleNotFoundError`**.
:::

:::quiz id="q-once":::

:::code mode="script"
import sys
from pathlib import Path

Path("helpers.py").write_text(
    'print("loading helpers")\n'
    "def greet(name):\n"
    '    return f"Hello, {name}"\n',
    encoding="utf-8",
)
sys.path.insert(0, ".")          # the runner starts Python in isolated mode (-I)

import helpers
import helpers                   # already in sys.modules: nothing printed
from helpers import greet
print(greet("Sara"), "helpers" in sys.modules)
:::

:::note
في هذه المنصة يعمل Python في وضع معزول (`-I`) لا يضيف مجلد العمل إلى `sys.path`، لذلك نضيفه يدويًا.
في مشروعك العادي، مجلد السكربت الذي تشغّله موجود في `sys.path` تلقائيًا.
:::

:::animation id="anim-import":::

## `if __name__ == "__main__"`

:::code mode="script"
import sys
from pathlib import Path

Path("tools.py").write_text(
    "def double(x):\n"
    "    return 2 * x\n"
    "\n"
    'print("tools.__name__ =", __name__)\n'
    'if __name__ == "__main__":\n'
    '    print("running tools.py directly: demo", double(21))\n',
    encoding="utf-8",
)
sys.path.insert(0, ".")
import tools                     # imported: the demo block does NOT run
print(tools.double(5))
:::

:::quiz id="q-name":::

:::rule
ضع في آخر كل ملف يمكن تشغيله **وأيضًا** استيراده:

```python
def main():
    ...

if __name__ == "__main__":
    main()
```
هكذا يعمل الملف كبرنامج عند تشغيله مباشرة، وكمكتبة عند استيراده، دون أن يُنفّذ كود التجربة.
:::

:::mistake
- **ملف باسم مكتبة:** `random.py` أو `pandas.py` في مجلد مشروعك يُظلّل المكتبة الحقيقية.
- **`ModuleNotFoundError: No module named 'pandas'`:** المكتبة غير مثبتة في **الـinterpreter الذي
  يشغّل الكود** (راجع محاضرة «أي Python يعمل الآن؟»).
- **`from module import *`:** أسماء مجهولة المصدر، وقد تُظلّل أسماءك دون أن تنتبه.
:::

:::code mode="script" expect="ModuleNotFoundError"
import this_module_does_not_exist
:::

:::research
في مشروع بحثي، ضع الدوال القابلة لإعادة الاستعمال (القراءة، التنظيف، النماذج) في modules داخل مجلد
`src/`، واجعل الـnotebooks والسكربتات **تستوردها** بدل نسخها. هكذا يُصلَح الخطأ في مكان واحد، وتبقى
كل التحليلات متسقة.
:::

:::exercise id="ex-module":::

:::deep_dive
`importlib.reload(module)` يعيد تنفيذ module مستورد، وهو مفيد في الـnotebooks بعد تعديل الملف. وفي
Jupyter توجد الإضافة `%load_ext autoreload` ثم `%autoreload 2` لإعادة التحميل تلقائيًا. أما الـimports
النسبية داخل package (`from .utils import clean`) فتعمل فقط داخل package، لا في سكربت منفرد.
:::

:::sketchnote
```text
MODULE = a .py file → its own namespace           PACKAGE = folder of modules
import m · import m as alias · from m import x    avoid: from m import *
lookup: sys.modules (cache, run once) → sys.path (script dir, stdlib, site-packages)
not found → ModuleNotFoundError        your random.py shadows the real one
if __name__ == "__main__":  run as script, not when imported
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| استيراد module | `import math` |
| باسم مختصر | `import pandas as pd` |
| اسم واحد | `from pathlib import Path` |
| أين يبحث؟ | `import sys; sys.path` |
| هل استُورد؟ | `"name" in sys.modules` |
| كود التشغيل فقط | `if __name__ == "__main__":` |
:::

:::quiz id="q-exit":::

:::docs
- [Modules — Python Tutorial](https://docs.python.org/3/tutorial/modules.html)
- [The import system](https://docs.python.org/3/reference/import.html)
- [\_\_main\_\_ — Top-level code environment](https://docs.python.org/3/library/__main__.html)
:::
