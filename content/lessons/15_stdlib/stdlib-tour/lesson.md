:::question
قبل أن تثبّت مكتبة خارجية أو تكتب 30 سطرًا لحساب انحراف معياري أو فرق بين تاريخين، اسأل: **هل هذا
موجود أصلًا مع Python؟**
:::

:::theory title="«Batteries included»"
**المكتبة القياسية (standard library)** مئات الـmodules تأتي مع كل تثبيت لـPython، مختبرة ومدعومة
ومتاحة دون `pip`. ميزتها: لا تبعيات إضافية، تعمل في كل بيئة، ومستقرة عبر الإصدارات. لا أحد يحفظها
كلها؛ المهم أن تعرف **خريطتها حسب المهمة** لتعرف أين تبحث:

| المهمة | الـmodules |
|---|---|
| أرقام وإحصاء | `math`، `statistics`، `random`، `decimal`، `fractions` |
| تواريخ وأوقات | `datetime`، `zoneinfo`، `time`، `calendar` |
| بنى بيانات | `collections`، `heapq`، `array` |
| أدوات وظيفية | `itertools`، `functools`، `operator` |
| ملفات ونظام | `pathlib`، `os`، `shutil`، `tempfile`، `sys` |
| صيغ بيانات | `json`، `csv`، `sqlite3`، `tomllib`، `zipfile` |
| نصوص | `re`، `string`، `textwrap`، `unicodedata` |
| جودة وتشخيص | `logging`، `unittest`، `doctest`، `timeit`، `pdb` |
| ويب وشبكة | `urllib`، `http`، `html`، `email` |
:::

## الأرقام والإحصاء والعشوائية

:::code mode="script"
import math
import random
import statistics

print(math.sqrt(2), math.log(100, 10), math.comb(5, 2), math.isclose(0.1 + 0.2, 0.3))

sample = [12, 15, 11, 18, 14]
print(statistics.mean(sample), statistics.median(sample), round(statistics.stdev(sample), 3))

random.seed(2024)                     # reproducible simulation
print([random.randint(1, 6) for _ in range(5)], round(random.gauss(0, 1), 4))
print(random.sample(["A", "B", "C", "D"], 2))
:::

:::quiz id="q-seed":::

## التواريخ والأوقات

:::code mode="script"
from datetime import date, datetime, timedelta

start = date(2026, 9, 24)
print(start + timedelta(days=30), start.strftime("%A %d %B %Y"))

d = datetime.strptime("15/03/2024 14:30", "%d/%m/%Y %H:%M")
print(d, d.year, d.isoformat())
print((date(2026, 12, 31) - start).days, "days left in the year")
:::

:::quiz id="q-dates":::

:::syntax
| الرمز | المعنى | مثال |
|---|---|---|
| `%Y` / `%m` / `%d` | سنة / شهر / يوم | `2026` / `09` / `24` |
| `%H` / `%M` / `%S` | ساعة / دقيقة / ثانية | `14` / `30` / `05` |
| `%A` / `%B` | اسم اليوم / الشهر | `Thursday` / `September` |
| `strptime` | نص ← تاريخ (parse) | |
| `strftime` | تاريخ ← نص (format) | |
:::

## itertools وfunctools والقياس

:::code mode="script"
import functools
import itertools
import timeit

print(list(itertools.combinations("ABC", 2)))
print(list(itertools.product([0, 1], repeat=2)))
print(list(itertools.accumulate([1, 2, 3, 4])))           # running totals

@functools.lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(80))

print(round(timeit.timeit("sum(range(1000))", number=2000), 4), "seconds")
:::

:::rule
قبل أي `pip install` لمهمة صغيرة: ابحث في المكتبة القياسية. وقبل كتابة خوارزمية معروفة (تباديل،
توافيق، cache، عدّ): غالبًا موجودة في `itertools` أو `functools` أو `collections`.
:::

:::mistake
- حساب الفروق بين التواريخ يدويًا (30 يومًا لكل شهر) بدل `datetime`.
- استخدام `random` لتوليد كلمات مرور أو tokens: تسلسله قابل للتوقع؛ استخدم `secrets`.
- تسمية ملفك `statistics.py` أو `datetime.py` فيُظلّل الـmodule الحقيقي.
:::

:::code mode="script" expect="ValueError"
from datetime import datetime
datetime.strptime("2024-03-15", "%d/%m/%Y")      # format does not match the text
:::

:::research
`random.seed(...)` (أو `numpy.random.default_rng(seed)`) **إلزامي** في أي محاكاة أو bootstrap أو
تقسيم عينات تنشره: بدونه لا يستطيع أحد (ولا أنت بعد شهر) إعادة إنتاج أرقامك بالضبط. وثّق البذرة في
الكود وفي الورقة.
:::

:::exercise id="ex-toolbox":::

:::deep_dive
`datetime` البسيطة **naive**: لا تعرف منطقتها الزمنية. للتطبيقات التي تعبر مناطق زمنية أو تتعامل مع
التوقيت الصيفي استخدم تواريخ **aware**: `datetime.now(ZoneInfo("Africa/Algiers"))` من الـmodule
`zoneinfo`، وخزّن الأوقات بتوقيت UTC.
:::

:::sketchnote
```text
BATTERIES INCLUDED: no pip needed
math · statistics · random(seed!) · secrets (security)
datetime: date, datetime, timedelta   strptime text→date   strftime date→text
itertools: combinations product accumulate     functools: lru_cache partial
collections · pathlib · json · csv · re · logging · timeit
search the stdlib before writing or installing
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| متوسط / انحراف | `statistics.mean(xs)`، `statistics.stdev(xs)` |
| عشوائية قابلة للإعادة | `random.seed(42)` |
| تاريخ بعد n يوم | `d + timedelta(days=n)` |
| نص ← تاريخ | `datetime.strptime(s, "%d/%m/%Y")` |
| توافيق | `itertools.combinations(xs, 2)` |
| تخزين النتائج | `@functools.lru_cache` |
| قياس الزمن | `timeit.timeit(stmt, number=n)` |
:::

:::quiz id="q-exit":::

:::docs
- [The Python Standard Library](https://docs.python.org/3/library/index.html)
- [datetime — Basic date and time types](https://docs.python.org/3/library/datetime.html)
- [statistics — Mathematical statistics functions](https://docs.python.org/3/library/statistics.html)
- [itertools — Functions creating iterators](https://docs.python.org/3/library/itertools.html)
:::
