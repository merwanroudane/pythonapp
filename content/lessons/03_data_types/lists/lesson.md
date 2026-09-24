:::question
درجات 30 طالبًا: هل تنشئ 30 متغيرًا `score1` و`score2`…؟ **ما البنية التي تحفظ مجموعة
مرتبة من القيم، ويمكن أن تكبر وتصغر؟**
:::

:::theory title="بنى البيانات والمصفوفة الديناميكية"
**بنية البيانات (data structure)** طريقة لتنظيم البيانات في الذاكرة بحيث تكون عمليات معينة سريعة.
الـ`list` في CPython **مصفوفة ديناميكية (dynamic array)** من **المراجع** إلى objects.

ولقياس «سرعة» العملية نستعمل ترميز **Big-O**: كيف يزداد الوقت عندما يزداد عدد العناصر `n`:

| العملية | التكلفة | لماذا؟ |
|---|---|---|
| `xs[i]` | O(1) ثابتة | الموضع يُحسب مباشرة |
| `xs.append(v)` | O(1) في المتوسط | توجد مساحة احتياطية في النهاية |
| `xs.insert(0, v)` | O(n) | يجب إزاحة كل العناصر |
| `v in xs` | O(n) | بحث عنصرًا عنصرًا |

لا تحتاج حفظ الجدول الآن، لكن تذكّر الفكرة: **اختيار بنية البيانات يحدد سرعة البرنامج.**
:::

:::concept
الـ`list` **تسلسل مرتب وقابل للتعديل (mutable)**. العناصر لها مواضع مثل النصوص تمامًا
(`[0]`، `[-1]`، slicing)، لكن على عكس النصوص يمكنك **تغيير** القائمة نفسها: إضافة عناصر،
حذفها، أو استبدال عنصر في موضعه.
:::

:::code mode="script"
scores = [12, 7, 18]
print(scores[0], scores[-1], scores[1:])

scores[1] = 8          # replace in place
scores.append(15)      # add at the end
scores.insert(0, 20)   # add at position 0
print(scores, len(scores))

last = scores.pop()    # remove and return the last item
scores.remove(8)       # remove the first 8 (ValueError if missing)
print(last, scores, 18 in scores)
:::

## append أم extend؟

:::quiz id="q-append":::

:::change id="ch-append-extend":::

## sort() أم sorted()؟

:::quiz id="q-sort":::

:::compare title="ترتيب في المكان أم نسخة جديدة؟"
**`xs.sort()`**

```python
xs = [3, 1, 2]
xs.sort()          # modifies xs
print(xs)          # [1, 2, 3]
```
تعدّل القائمة نفسها وتُعيد `None`. للقوائم فقط.
|||
**`sorted(xs)`**

```python
xs = [3, 1, 2]
ys = sorted(xs)    # xs unchanged
print(xs, ys)      # [3, 1, 2] [1, 2, 3]
```
تُعيد قائمة جديدة، وتعمل مع أي iterable (نص، tuple، dict…).
:::

:::rule
الـmethods التي **تعدّل** القائمة (`append`، `extend`، `sort`، `reverse`، `insert`، `remove`)
تُعيد `None`. لا تكتب أبدًا `xs = xs.sort()`.
:::

:::code mode="script"
names = ["omar", "Sara", "lina"]
print(sorted(names))
print(sorted(names, key=str.lower))
print(sorted(names, key=len, reverse=True))
:::

## الفخ الأشهر: القوائم المتداخلة

:::animation id="anim-grid":::

:::note
السطر `[[0] * 3 for _ in range(3)]` هو **list comprehension**: طريقة مختصرة لبناء قائمة
بحلقة. يكفي الآن أن تعرف أنه ينشئ قائمة جديدة في كل دورة؛ ستتعلم `for` والـcomprehensions
بالتفصيل في مسار **06 · الحلقات**.
:::

:::mistake
```python
grid = [[0] * 3] * 3
grid[0][0] = 1
print(grid)   # [[1, 0, 0], [1, 0, 0], [1, 0, 0]]
```
الضرب `* 3` يكرر **المراجع** لا الـobjects. استخدم comprehension لإنشاء صفوف مستقلة:
`[[0] * 3 for _ in range(3)]`.
:::

:::tip
لنسخ قائمة بسيطة: `xs.copy()` أو `xs[:]` أو `list(xs)`. هذه **shallow copy**: القائمة
الخارجية جديدة لكن العناصر الداخلية (إن كانت قوائم) مشتركة. للبنى المتداخلة: `copy.deepcopy`.
:::

:::research
القوائم مناسبة لجمع النتائج أثناء الحلقات (`results.append(...)`)، لكن للجداول الرقمية الكبيرة
سننتقل إلى NumPy arrays وpandas DataFrames: أسرع بكثير، ولكل عمود نوع واحد.
:::

:::exercise id="ex-top3":::

:::under_the_hood
الـ`list` في CPython مصفوفة من **المراجع** (pointers) إلى objects، مع مساحة احتياطية تجعل
`append` سريعًا في المتوسط. لهذا يمكن أن تحتوي القائمة أنواعًا مختلطة، ولهذا أيضًا يُنسخ
المرجع وليس الـobject في `[row] * 3`. أما `insert(0, x)` فيحتاج إزاحة كل العناصر، فهو أبطأ
على القوائم الطويلة.
:::

:::sketchnote
```text
LIST = ordered + MUTABLE      [12, 7, 18]
append(x)   one item          extend(xs)   many items
xs.sort()   in place → None   sorted(xs)   new list
[[0]*3]*3   ✗ shared rows     [[0]*3 for _ in range(3)]  ✓
```
:::

:::cheatsheet
| المهمة | الكود |
|---|---|
| إضافة في النهاية | `xs.append(x)` |
| إضافة عدة عناصر | `xs.extend(ys)` |
| حذف بالقيمة / بالموضع | `xs.remove(v)` / `xs.pop(i)` |
| ترتيب جديد | `sorted(xs, reverse=True)` |
| نسخة | `xs.copy()` |
| هل موجود؟ | `v in xs` |
:::

:::quiz id="q-exit":::

:::docs
- [More on Lists — Python Tutorial](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)
- [Sorting HOW TO](https://docs.python.org/3/howto/sorting.html)
:::
