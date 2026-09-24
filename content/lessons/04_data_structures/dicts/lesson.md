:::question
لديك أسماء الطلاب وأعمارهم. بالقوائم تحتاج قائمتين متوازيتين وتبحث عن موضع الاسم كل مرة.
**ألا توجد بنية تقول مباشرة: «أعطني عمر Sara»؟**
:::

:::theory title="جدول التجزئة (hash table)"
الـ`dict` مبني على **جدول تجزئة (hash table)**:

1. دالة **hash** تحوّل المفتاح إلى عدد صحيح: `hash("Sara")`.
2. هذا العدد يحدد **الخانة (slot)** التي تُخزَّن فيها القيمة داخل جدول في الذاكرة.
3. عند البحث عن المفتاح، يُحسب الـhash نفسه فيُعرف مكان القيمة مباشرة.

النتيجة: البحث بالمفتاح **O(1) في المتوسط**، سواء كان في القاموس عشرة عناصر أو عشرة ملايين، بينما
البحث في قائمة **O(n)**. ولهذا يجب أن يكون المفتاح **hashable**: قيمته لا تتغير، وإلا تغيّر الـhash
وضاع مكانه. وعندما يعطي مفتاحان الخانة نفسها (**collision**) يعالج Python ذلك داخليًا. ومنذ
Python 3.7 يحافظ الـdict رسميًا على **ترتيب الإدخال**.
:::

:::concept
الـ`dict` **mapping**: كل **مفتاح (key)** يشير إلى **قيمة (value)**. المفاتيح **فريدة**
ويجب أن تكون hashable (نصوص، أرقام، tuples…)، أما القيم فيمكن أن تكون أي شيء. البحث
بالمفتاح مباشر وسريع مهما كبر القاموس، ويحفظ Python ترتيب الإدخال.
:::

:::diagram title="dict: مفاتيح فريدة ← قيم"
flowchart LR
    K1(["'Sara'"]) --> V1["30"]
    K2(["'Omar'"]) --> V2["25"]
    K3(["'Lina'"]) --> V3["28"]
:::

:::code mode="script"
ages = {"Sara": 30, "Omar": 25}
print(ages["Sara"])

ages["Lina"] = 28        # add
ages["Omar"] = 26        # update
del ages["Sara"]         # delete
print(ages, len(ages))

for name, age in ages.items():
    print(f"{name} is {age}")
:::

:::quiz id="q-in":::

:::quiz id="q-overwrite":::

## القراءة الآمنة: [] أم get؟

:::change id="ch-get":::

:::mistake
```python
scores = {"math": 17}
print(scores["physics"])     # KeyError: 'physics'
```
رسالة `KeyError` تذكر المفتاح المفقود نفسه. تحقق من الكتابة، أو من وجوده بـ`"physics" in scores`،
أو قرر أن له قيمة افتراضية منطقية فاستخدم `get`.
:::

:::code mode="script" expect="KeyError"
scores = {"math": 17}
print(scores["physics"])
:::

## نمط العدّ

:::note
نستخدم هنا حلقة `for` بسيطة: «لكل كلمة في القائمة، نفّذ السطر المُزاح». تفاصيلها الكاملة في
مسار **07 · الحلقات**.
:::

:::code mode="script"
words = ["apple", "kiwi", "apple", "fig", "kiwi", "apple"]
counts = {}
for w in words:
    counts[w] = counts.get(w, 0) + 1
print(counts)
:::

:::tip
المكتبة القياسية فيها أداة جاهزة لهذا: `from collections import Counter` ثم
`Counter(words).most_common(2)`. لكن افهم النمط اليدوي أولًا، فهو يتكرر في كل مكان.
:::

:::research
القواميس هي الشكل الطبيعي لإعدادات التحليل (`{"alpha": 0.05, "n_boot": 999}`) ولنتائج
دالة إحصائية (`{"mean": …, "sd": …}`)، وهي البنية التي يتحول إليها JSON مباشرة. وسطر
`pd.DataFrame({"x": [...], "y": [...]})` هو dict أعمدة.
:::

:::exercise id="ex-count":::

:::deep_dive
لماذا يجب أن تكون المفاتيح hashable؟ الـdict يحسب `hash(key)` ليعرف أين يخزّن القيمة،
فلو تغيّر المفتاح بعد التخزين لضاع مكانه. لذلك `list` لا تصلح مفتاحًا لكن `tuple` تصلح:
`{(36.7, 3.0): "Algiers"}`. وفي Python 3.9+ يمكن دمج قاموسين بـ`a | b`.
:::

:::sketchnote
```text
DICT = key → value       keys unique & hashable
d[k]        KeyError if missing   (required key)
d.get(k, x) default if missing    (optional key)
k in d      searches KEYS
for k, v in d.items():
counts[w] = counts.get(w, 0) + 1
```
:::

:::cheatsheet
| المهمة | الكود |
|---|---|
| قراءة / كتابة | `d[k]`, `d[k] = v` |
| قراءة بقيمة افتراضية | `d.get(k, default)` |
| حذف | `del d[k]` أو `d.pop(k)` |
| مفاتيح / قيم / أزواج | `d.keys()`, `d.values()`, `d.items()` |
| هل المفتاح موجود؟ | `k in d` |
| دمج | `a \| b` |
:::

:::quiz id="q-exit":::

:::docs
- [Dictionaries — Python Tutorial](https://docs.python.org/3/tutorial/datastructures.html#dictionaries)
- [Mapping Types — dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
- [collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter)
:::
