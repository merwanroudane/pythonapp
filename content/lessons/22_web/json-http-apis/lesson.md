:::question
البنك الدولي، الإحصاءات الوطنية، الأرصاد الجوية: بيانات كثيرة متاحة على الإنترنت ومحدَّثة باستمرار.
بدل تنزيلها يدويًا كل شهر، **كيف يطلبها برنامجك مباشرة ويفهم ما يعود إليه؟**
:::

:::theory title="HTTP: طلب واستجابة"
الويب يعمل ببروتوكول **HTTP**: **العميل (client)**، سواء متصفحك أو برنامج Python، يرسل **طلبًا
(request)**، و**الخادم (server)** يعيد **استجابة (response)**.

- **الطلب:** **method** (غالبًا `GET` للقراءة و`POST` لإرسال بيانات)، و**URL** يحدد المورد، و**headers**
  (نوع المحتوى المقبول، مفتاح API…)، وأحيانًا **body**.
- **الاستجابة:** **رمز حالة (status code)** مثل `200` نجاح و`404` غير موجود، و**headers**، و**body**
  يكون HTML (للعرض في المتصفح) أو **JSON** (بيانات منظمة للبرامج).

**الـAPI** (Application Programming Interface) على الويب مجموعة URLs موثَّقة تعيد بيانات منظمة
(غالبًا JSON) بدل صفحات للعرض. وبما أن هذا الملعب يعمل **بلا شبكة** لأسباب أمنية، سنعمل هنا على
استجابات جاهزة، وهي الخطوة التي تستغرق معظم العمل الحقيقي على أي حال.
:::

:::diagram kind="text" title="دورة طلب HTTP"
   your program                                       server
  ┌─────────────┐   GET /v1/data?country=DZ&page=1   ┌────────────┐
  │   client    │ ─────────────────────────────────► │    API     │
  │             │   headers: Accept: application/json│            │
  │             │ ◄───────────────────────────────── │            │
  └─────────────┘   200 OK                           └────────────┘
                    Content-Type: application/json
                    {"meta": {...}, "data": [...]}   ← parse with json.loads
:::

## تشريح URL

:::code mode="script"
from urllib.parse import parse_qs, urlencode, urlparse

url = "https://api.example.org/v1/data?country=DZ&indicator=gdp_growth&page=2"
parts = urlparse(url)
print(parts.scheme, parts.netloc, parts.path)
print(parse_qs(parts.query))

params = {"q": "GDP growth", "from": 2010, "to": 2024}
print("https://api.example.org/search?" + urlencode(params))
:::

:::quiz id="q-urlencode":::

## الطلب الفعلي (للقراءة)

في برنامج على جهازك، الطلب بمكتبة **requests** (المعيار الفعلي) أو بـ`urllib.request` القياسية. الكود
أدناه للقراءة فقط لأن الملعب بلا شبكة:

:::code run="false"
import requests

resp = requests.get(
    "https://api.worldbank.org/v2/country/DZ/indicator/NY.GDP.MKTP.KD.ZG",
    params={"format": "json", "date": "2015:2024"},
    timeout=10,                      # never wait forever
)
resp.raise_for_status()              # turn 4xx/5xx into an exception
meta, data = resp.json()             # parse the JSON body
:::

:::quiz id="q-status":::

## تحليل JSON متداخل

:::code mode="script"
import json

import pandas as pd

raw = """{"data": [
  {"country": {"id": "DZ", "name": "Algeria"}, "year": 2023, "value": 4.1},
  {"country": {"id": "DZ", "name": "Algeria"}, "year": 2022, "value": 3.6},
  {"country": {"id": "MA", "name": "Morocco"}, "year": 2023, "value": null}
]}"""
payload = json.loads(raw)
print(type(payload), payload["data"][0]["country"]["name"])

df = pd.json_normalize(payload["data"])      # nested keys → "country.id", "country.name"
print(df)
print(df.dropna(subset=["value"]).groupby("country.name")["value"].mean())
:::

## استخراج بيانات من HTML

عندما لا يوجد API، تكون البيانات داخل HTML مصمم للعرض. المحلل القياسي `html.parser` يمر على الوسوم:

:::code mode="script"
from html.parser import HTMLParser

page = """<table id="rates">
  <tr><th>country</th><th>rate</th></tr>
  <tr><td>Algeria</td><td>4.1</td></tr>
  <tr><td>Tunisia</td><td>0.4</td></tr>
</table>"""


class CellCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self._row, self._in_td = [], [], False

    def handle_starttag(self, tag, attrs):
        self._in_td = tag == "td"

    def handle_endtag(self, tag):
        if tag == "tr" and self._row:
            self.rows.append(tuple(self._row))
            self._row = []
        self._in_td = False

    def handle_data(self, data):
        if self._in_td:
            self._row.append(data.strip())


parser = CellCollector()
parser.feed(page)
print(parser.rows)
:::

:::tip
في الممارسة استخدم **Beautiful Soup** (`soup.select("table#rates td")`) لأنه أبسط بكثير مع HTML
حقيقي فوضوي، و`pd.read_html` للجداول. `html.parser` هنا ليظهر ما يحدث تحت الغطاء.
:::

:::rule
**أخلاقيات جمع البيانات:** اقرأ شروط الاستخدام، واحترم `robots.txt`، وفضّل الـAPI الرسمي، وأضف
`timeout` وتأخيرًا بين الطلبات (`time.sleep`)، وخزّن ما نزّلته محليًا (cache) بدل إعادة الطلب، ولا تجمع
بيانات شخصية دون أساس قانوني. ولا تضع مفاتيح API في الكود: ضعها في متغيرات بيئة.
:::

:::mistake
- `json.loads` على نص ليس JSON (صفحة خطأ HTML مثلًا) يرفع `JSONDecodeError`: تحقق من الـstatus
  والـ`Content-Type` أولًا.
- طلب بلا `timeout` قد يعلّق البرنامج للأبد.
- افتراض أن كل الحقول موجودة دائمًا: استخدم `rec.get("value")` للحقول الاختيارية.
:::

:::code mode="script" expect="JSONDecodeError"
import json
json.loads("<html><body>502 Bad Gateway</body></html>")
:::

:::research
لبيانات البحث: API البنك الدولي، وSDMX للمؤسسات الإحصائية (مع مكتبة `sdmx1`)، وFRED لبيانات الاقتصاد
الكلي، وOpenAlex للبيانات الببليومترية. سجّل تاريخ التنزيل والـURL والمعاملات مع البيانات، لأن البيانات
عبر API تُحدَّث ويجب أن يعرف القارئ أي نسخة استخدمت.
:::

:::exercise id="ex-api":::

:::deep_dive
معظم الـAPIs **تقسّم النتائج إلى صفحات (pagination)**: تعطيك `page` و`pages` (أو `next`)، فتكرر الطلب
حتى آخر صفحة. وكثير منها له **حد للطلبات (rate limit)** ويعيد `429 Too Many Requests` عند تجاوزه، مع
header اسمه `Retry-After`. والنمط الجيد دالة `fetch_all(params)` هي generator تُنتج السجلات صفحة صفحة.
:::

:::sketchnote
```text
client ──request(method, URL, headers)──► server ──response(status, headers, body)──►
2xx ok · 3xx redirect · 4xx your request (404, 429) · 5xx the server
URL = scheme://host/path?query     build query with urlencode, parse with urlparse/parse_qs
JSON body → json.loads / resp.json()  → dicts & lists → pd.json_normalize
no API? HTML → Beautiful Soup / pd.read_html     be polite: ToS · robots.txt · timeout · sleep
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| طلب GET | `requests.get(url, params=..., timeout=10)` |
| فحص النجاح | `resp.raise_for_status()`، `resp.status_code` |
| JSON | `resp.json()`، `json.loads(text)` |
| بناء query | `urlencode(dict)` |
| تفكيك URL | `urlparse(url)`، `parse_qs(q)` |
| JSON متداخل → جدول | `pd.json_normalize(records)` |
| جداول HTML | `pd.read_html(html)` |
:::

:::quiz id="q-exit":::

:::docs
- [urllib.parse](https://docs.python.org/3/library/urllib.parse.html)
- [json](https://docs.python.org/3/library/json.html)
- [Requests: quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [HTTP response status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
:::
