:::question
كم يساوي `2 + 3 * 4`؟ إن قلت 20 فقد حسبت من اليسار إلى اليمين. Python يقول 14.
**من يقرر أي جزء من التعبير يُحسب أولًا؟**
:::

:::theory title="التعبير شجرة، والمنطق جبر"
- عندما يقرأ الـparser تعبيرًا مثل `2 + 3 * 4`، يبني **شجرة تعبير (expression tree)** حسب الأولوية:
  `*` أعمق في الشجرة فتُحسب أولًا، ثم `+`. التقييم يبدأ من الأوراق نحو الجذر.
- عوامل `and` و`or` و`not` تطبيق لـ**جبر بول (Boolean algebra)**، الذي وضعه George Boole في
  القرن التاسع عشر:

| `a` | `b` | `a and b` | `a or b` | `not a` |
|---|---|---|---|---|
| True | True | True | True | False |
| True | False | False | True | False |
| False | True | False | True | True |
| False | False | False | False | True |

- **قوانين De Morgan** مفيدة لتبسيط الشروط: `not (a and b)` تساوي `(not a) or (not b)`، و
  `not (a or b)` تساوي `(not a) and (not b)`.
:::

:::concept
كل **expression** مكوّن من قيم وعوامل (operators). عندما يحوي التعبير أكثر من عامل، يحدد
**جدول الأولوية (precedence)** أيها يُحسب أولًا، وتحدد **الـassociativity** الاتجاه بين
عاملين من المستوى نفسه (غالبًا من اليسار إلى اليمين، إلا `**` فمن اليمين).
:::

:::syntax
| الأولوية (من الأعلى) | العوامل | مثال |
|---|---|---|
| 1 | `( )` الأقواس | `(2 + 3) * 4` |
| 2 | `**` الأس | `2 ** 3` |
| 3 | `+x` `-x` الإشارة | `-5` |
| 4 | `*` `/` `//` `%` | `7 // 2` |
| 5 | `+` `-` | `2 + 3` |
| 6 | `<` `<=` `==` `!=` `in` `is` … | `x in xs` |
| 7 | `not` | `not done` |
| 8 | `and` | `a and b` |
| 9 | `or` | `a or b` |
:::

:::quiz id="q-mix":::

:::code mode="script"
print(2 + 3 * 4)
print((2 + 3) * 4)
print(2 ** 3 ** 2)      # right to left: 2 ** 9
print(10 - 4 - 3)       # left to right: (10 - 4) - 3
:::

:::quiz id="q-power":::

## المقارنة والعضوية والهوية

:::code mode="script"
age = 34
print(18 <= age < 65)          # chained comparison
print("a" < "b", "10" < "9")   # strings compare character by character!

colors = ["red", "green"]
print("red" in colors, "blue" not in colors)

x = None
print(x is None, x == None)
:::

:::warning
`"10" < "9"` صحيح! النصوص تُقارن **حرفًا حرفًا** (`"1"` قبل `"9"`)، لا كأرقام. إن جاءت
الأرقام كنصوص من ملف، حوّلها قبل المقارنة.
:::

:::mistake
```python
if x == 1 or 2:      # always True!
```
Python يقرأها `(x == 1) or 2`، و`2` truthy دائمًا. الصحيح: `if x == 1 or x == 2:` أو
`if x in (1, 2):`.
:::

## and / or والأقواس

:::change id="ch-parens":::

:::animation id="anim-ops":::

:::rule
الأولوية مفيدة للحاسوب، والأقواس مفيدة **للبشر**. عندما تخلط `and` مع `or`، أو عوامل من
مستويات مختلفة، أضف أقواسًا حتى لو كانت النتيجة نفسها.
:::

:::research
شروط اختيار العينة في البحث (`18 <= age < 65 and (consent or guardian_consent)`) هي بالضبط
هذا النوع من التعابير. خطأ أولوية واحد يُدخل حالات غير مؤهلة إلى التحليل بصمت.
:::

:::exercise id="ex-eligible":::

:::deep_dive
عوامل الإسناد المركّبة (`+=`، `*=`، `//=`) اختصار: `total += x` تعني تقريبًا
`total = total + x`. ومع القوائم يختلف السلوك: `xs += [1]` تعدّل القائمة في مكانها (مثل
`extend`)، بينما `xs = xs + [1]` تنشئ قائمة جديدة. وعامل walrus `:=` يُسند ويُعيد القيمة
داخل تعبير: `if (n := len(data)) > 10:`.
:::

:::sketchnote
```text
()  >  **  >  -x  >  * / // %  >  + -  >  comparisons  >  not  >  and  >  or
-2 ** 2  = -4        2 ** 3 ** 2 = 512 (right to left)
1 < x < 10   ≡   1 < x and x < 10
x == 1 or 2   ✗      x in (1, 2)   ✓
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| مجال | `lo <= x < hi` |
| أحد عدة قيم | `x in (1, 2, 3)` |
| ليس None | `x is not None` |
| فرض الترتيب | أقواس `( )` |
| عكس شرط | `not cond` |
:::

:::quiz id="q-exit":::

:::docs
- [Operator precedence](https://docs.python.org/3/reference/expressions.html#operator-precedence)
- [Comparisons](https://docs.python.org/3/reference/expressions.html#comparisons)
:::
