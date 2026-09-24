:::question
ملفات CSV تكفي لجدول واحد. لكن ماذا لو كانت لديك ملايين الصفوف، وعدة جداول مرتبطة (زبائن، طلبات،
منتجات)، وعدة مستخدمين يكتبون في الوقت نفسه؟ **أين تُخزَّن البيانات بأمان، وكيف تسألها؟**
:::

:::theory title="قاعدة البيانات العلائقية"
**قاعدة البيانات** برنامج متخصص في تخزين البيانات واسترجاعها بكفاءة وأمان. أشهر نوع هو **العلائقي
(relational)**، حيث تُنظَّم البيانات في **جداول**:

- **الجدول (table):** أعمدة لها أنواع ثابتة، وصفوف (records) هي البيانات.
- **المفتاح الأساسي (primary key):** عمود يعرّف كل صف تعريفًا فريدًا، مثل `id`.
- **المفتاح الأجنبي (foreign key):** عمود يشير إلى المفتاح الأساسي لجدول آخر، وبه **تُربط** الجداول
  بدل تكرار البيانات.

**SQL** (Structured Query Language) لغة **تصريحية (declarative)**: تصف **ماذا** تريد
(«المدن التي متوسط دخلها فوق كذا») لا **كيف** تبحث. ومحرك القاعدة هو من يختار خطة التنفيذ (فهارس،
ترتيب). و**SQLite** قاعدة كاملة داخل ملف واحد، ومدمجة في Python عبر الوحدة القياسية `sqlite3`.
:::

:::diagram kind="text" title="جدولان مرتبطان بمفتاح"
   countries                          cities
   ┌────┬──────────┐                  ┌────┬──────────┬────────────┬──────┐
   │ id │ name     │                  │ id │ name     │ country_id │ pop  │
   ├────┼──────────┤                  ├────┼──────────┼────────────┼──────┤
   │ 1  │ Algeria  │ ◄──────────────  │ 1  │ Algiers  │     1      │ 3.0  │
   │ 2  │ Tunisia  │ ◄───────┐        │ 2  │ Oran     │     1      │ 1.6  │
   └────┴──────────┘         └──────  │ 3  │ Tunis    │     2      │ 0.7  │
     primary key                      └────┴──────────┴────────────┴──────┘
                                         foreign key → countries.id
:::

## الإنشاء والإدخال والاستعلام

:::code mode="script"
import sqlite3

con = sqlite3.connect(":memory:")        # a throwaway database in RAM; use "data.db" for a file
cur = con.cursor()
cur.execute("CREATE TABLE countries (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
cur.execute("""CREATE TABLE cities (
    id INTEGER PRIMARY KEY, name TEXT, country_id INTEGER REFERENCES countries(id), pop REAL)""")
cur.executemany("INSERT INTO countries VALUES (?, ?)", [(1, "Algeria"), (2, "Tunisia")])
cur.executemany("INSERT INTO cities (name, country_id, pop) VALUES (?, ?, ?)",
                [("Algiers", 1, 3.0), ("Oran", 1, 1.6), ("Tunis", 2, 0.7), ("Setif", 1, 0.3)])
con.commit()

for row in cur.execute("SELECT name, pop FROM cities WHERE pop > 1 ORDER BY pop DESC"):
    print(row)
:::

:::syntax
```sql
SELECT   columns / expressions        -- what to return
FROM     table  JOIN other ON ...     -- where from
WHERE    row condition                -- filter rows (before grouping)
GROUP BY column                       -- split into groups
HAVING   group condition              -- filter groups (after grouping)
ORDER BY column DESC                  -- sort
LIMIT    n                            -- first n rows
```
الترتيب المكتوب ثابت، لكن التنفيذ المنطقي هو: FROM ← WHERE ← GROUP BY ← HAVING ← SELECT ← ORDER BY.
:::

## JOIN وGROUP BY

:::code mode="script"
import sqlite3

con = sqlite3.connect(":memory:")
con.executescript("""
CREATE TABLE countries (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE cities (id INTEGER PRIMARY KEY, name TEXT, country_id INTEGER, pop REAL);
INSERT INTO countries VALUES (1, 'Algeria'), (2, 'Tunisia');
INSERT INTO cities (name, country_id, pop) VALUES
  ('Algiers', 1, 3.0), ('Oran', 1, 1.6), ('Tunis', 2, 0.7), ('Setif', 1, 0.3);
""")
query = """
SELECT co.name AS country, COUNT(*) AS n_cities, ROUND(SUM(ci.pop), 1) AS total_pop
FROM cities AS ci
JOIN countries AS co ON co.id = ci.country_id
GROUP BY co.name
ORDER BY total_pop DESC
"""
for row in con.execute(query):
    print(row)
:::

:::quiz id="q-where-having":::

## الأمان: الاستعلامات ذات المعاملات

:::warning
**لا تبنِ استعلام SQL بدمج نصوص من المستخدم أبدًا.** هذا يفتح باب **SQL injection**: مدخل خبيث يغيّر
معنى الاستعلام فيقرأ أو يحذف ما لا يجب. استخدم دائمًا العلامة `?` وأعطِ القيم في tuple منفصلة.
:::

:::code mode="script"
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE users (name TEXT, secret TEXT)")
con.executemany("INSERT INTO users VALUES (?, ?)", [("sara", "s1"), ("omar", "o2")])

evil = "nobody' OR '1'='1"
unsafe = f"SELECT * FROM users WHERE name = '{evil}'"
print("unsafe:", con.execute(unsafe).fetchall())                                # leaks every row
print("safe:  ", con.execute("SELECT * FROM users WHERE name = ?", (evil,)).fetchall())  # nothing
:::

:::quiz id="q-injection":::

## من SQL إلى pandas

:::code mode="script"
import sqlite3
import pandas as pd

con = sqlite3.connect(":memory:")
pd.DataFrame({"city": ["Oran", "Algiers", "Setif"], "pop": [1.6, 3.0, 0.3]}).to_sql("cities", con, index=False)
df = pd.read_sql_query("SELECT city, pop FROM cities WHERE pop > ? ORDER BY pop", con, params=(1,))
print(df)
:::

:::mistake
- **نسيان `commit()`** بعد الكتابة في ملف: التغييرات لا تُحفظ. أو استخدم `with con:` لتنفيذ commit تلقائي.
- **`WHERE` مع دالة تجميع:** `WHERE COUNT(*) > 2` خطأ؛ مكانها `HAVING`.
- **مقارنة مع NULL بـ`=`:** `WHERE income = NULL` لا تُرجع شيئًا؛ الصحيح `WHERE income IS NULL`.
:::

:::code mode="script" expect="OperationalError"
import sqlite3
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE t (city TEXT, pop REAL)")
con.execute("SELECT city FROM t WHERE COUNT(*) > 2 GROUP BY city")
:::

:::research
في البحث تفيد قواعد البيانات عندما تكبر البيانات أو تتعدد الجداول (مسوح متكررة، سجلات إدارية).
**DuckDB** قاعدة تحليلية سريعة جدًا تقرأ CSV وParquet مباشرة بـSQL، و**SQLAlchemy** طبقة موحدة
للاتصال بـPostgreSQL وMySQL وغيرهما. تبقى SQL نفسها المهارة المشتركة بين كل هذه الأدوات.
:::

:::exercise id="ex-sales":::

:::deep_dive
**الفهارس (indexes)**: `CREATE INDEX idx_city ON cities(country_id)` يبني بنية (B-tree) تجعل البحث
والـJOIN على هذا العمود أسرع بكثير على الجداول الكبيرة، مقابل مساحة إضافية وكتابة أبطأ قليلًا. استخدم
`EXPLAIN QUERY PLAN SELECT ...` لترى هل يستخدم المحرك الفهرس.
و**المعاملات (transactions)** تضمن أن مجموعة تعديلات إما تُطبَّق كلها أو لا شيء منها (ACID).
:::

:::sketchnote
```text
table = typed columns + rows     primary key = unique id     foreign key = link
SQL is declarative: say WHAT, the engine decides HOW
SELECT … FROM … JOIN … ON … WHERE … GROUP BY … HAVING … ORDER BY … LIMIT
WHERE filters rows · HAVING filters groups · NULL → IS NULL
ALWAYS  execute(sql, (value,))  with ?   never f-strings → SQL injection
con.commit() / with con:    pd.read_sql_query(sql, con, params=...)
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| اتصال | `con = sqlite3.connect("data.db")` |
| تنفيذ بمعاملات | `con.execute(sql, (a, b))` |
| إدخال كثير | `con.executemany(sql, rows)` |
| قراءة النتائج | `cur.fetchall()`، أو التكرار على `cur` |
| حفظ | `con.commit()` |
| إلى pandas | `pd.read_sql_query(sql, con)` |
| من pandas | `df.to_sql("t", con, index=False)` |
:::

:::quiz id="q-exit":::

:::docs
- [sqlite3: DB-API 2.0 interface for SQLite](https://docs.python.org/3/library/sqlite3.html)
- [SQLite: SELECT](https://www.sqlite.org/lang_select.html)
- [pandas.read_sql_query](https://pandas.pydata.org/docs/reference/api/pandas.read_sql_query.html)
:::
