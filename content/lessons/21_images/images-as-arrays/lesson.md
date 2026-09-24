:::question
صورة فوتوغرافية على شاشتك تبدو شيئًا متصلًا. لكن الحاسوب لا يرى «وجهًا» أو «سماء». **ماذا تكون
الصورة فعلًا في الذاكرة، وكيف تعدّلها بالكود؟**
:::

:::theory title="الصورة الرقمية شبكة أرقام"
الصورة **النقطية (raster)** شبكة مستطيلة من **pixels** (picture elements). لكل pixel قيمة أو أكثر:

- **رمادي (grayscale):** قيمة واحدة للإضاءة، عادةً من 0 (أسود) إلى 255 (أبيض).
- **ملون (RGB):** ثلاث **قنوات (channels)**: أحمر، أخضر، أزرق. واختلاط شدّاتها يعطي كل الألوان:
  `(255, 0, 0)` أحمر، `(255, 255, 0)` أصفر، `(255, 255, 255)` أبيض. وقد توجد قناة رابعة **A (alpha)**
  للشفافية.
- **النوع المعتاد `uint8`:** عدد صحيح بلا إشارة من 8 bits = 256 قيمة (0 إلى 255).

إذن الصورة الملونة **مصفوفة ثلاثية الأبعاد** بشكل `(الارتفاع، العرض، 3)`، وكل ما تعلمته في NumPy
(slicing، broadcasting، masks) يصبح أدوات معالجة صور. أما ملفات PNG وJPEG فهي **ترميز مضغوط** لهذه
الشبكة: PNG بلا فقد (lossless)، وJPEG بفقد (lossy) يناسب الصور الفوتوغرافية.
:::

:::diagram kind="text" title="من الصورة إلى المصفوفة"
      width (columns, x) ─────────►
   ┌─────┬─────┬─────┐
   │ px  │ px  │ px  │        a.shape = (height, width, 3)
 h ├─────┼─────┼─────┤        a[row, col]      → one pixel [R, G, B]
 e │ px  │ px  │ px  │        a[:, :, 0]       → the red channel (height, width)
 i ├─────┼─────┼─────┤        a[10:50, 20:80]  → a crop
 g │ px  │ px  │ px  │
 h └─────┴─────┴─────┘        each value: uint8, 0 … 255
 t (rows, y) ▼
:::

## إنشاء صورة من الأرقام

:::code mode="script"
import matplotlib.pyplot as plt
import numpy as np

h, w = 120, 200
a = np.zeros((h, w, 3), dtype=np.uint8)
a[:, :, 0] = np.linspace(0, 255, w).astype(np.uint8)          # red grows left → right
a[:, :, 2] = np.linspace(255, 0, h).astype(np.uint8)[:, None]  # blue fades top → bottom
a[40:80, 70:130] = [255, 255, 255]                             # a white rectangle

print(a.shape, a.dtype, a[0, 0], a[60, 100])
fig, ax = plt.subplots(figsize=(5, 3))
ax.imshow(a)
ax.set_title("An image is an array")
ax.axis("off")
:::

:::quiz id="q-shape":::

## Pillow ⇄ NumPy

**Pillow** (الاسم عند الاستيراد `PIL`) مكتبة فتح الصور وحفظها وتحويلها. والانتقال بينها وبين NumPy بسطر واحد.

:::code mode="script"
import numpy as np
from PIL import Image, ImageFilter

a = np.zeros((100, 160, 3), dtype=np.uint8)
a[:, :80] = [30, 120, 200]
a[:, 80:] = [240, 180, 40]
img = Image.fromarray(a)                  # array → Pillow Image
print(img.size, img.mode)                 # (width, height)  and  'RGB'

small = img.resize((80, 50))
gray = img.convert("L")                   # L = luminance (grayscale)
blurred = img.filter(ImageFilter.GaussianBlur(4))
back = np.asarray(gray)                   # Pillow Image → array
print(small.size, gray.mode, back.shape, back.dtype, back[0, 0], back[0, -1])
:::

:::tip
مع ملف حقيقي: `img = Image.open("photo.jpg")` ثم `img.save("out.png")`. الصيغة تُستنتج من الامتداد.
:::

## عمليات على المصفوفة

:::code mode="script"
import matplotlib.pyplot as plt
import numpy as np

rng = np.random.default_rng(3)
a = rng.integers(0, 256, size=(60, 90, 3), dtype=np.uint8)
a[20:40, 30:60] = [250, 200, 30]

fig, ax = plt.subplots(1, 4, figsize=(10, 2.6))
views = {"original": a, "crop": a[15:45, 25:65], "flip": a[:, ::-1], "red only": a * np.array([1, 0, 0], dtype=np.uint8)}
for axis, (title, img) in zip(ax, views.items()):
    axis.imshow(img)
    axis.set_title(title)
    axis.axis("off")
fig.tight_layout()
:::

:::animation id="anim-image":::

:::quiz id="q-overflow":::

:::mistake
- **الحساب مباشرة على `uint8`:** `a + 50` يلتف فتظهر ألوان غريبة. حوّل إلى `float`، احسب، ثم `np.clip`
  و`astype(np.uint8)`.
- **خلط (width, height) مع (rows, cols):** `img.size` في Pillow = (عرض، ارتفاع)، و`a.shape` = (ارتفاع، عرض، قنوات).
- **`imshow` لصورة float خارج [0, 1]:** Matplotlib تتوقع float بين 0 و1 أو uint8 بين 0 و255.
:::

:::code mode="script" expect="TypeError"
import numpy as np
from PIL import Image
Image.fromarray(np.zeros((10, 10, 3), dtype=np.float64))   # RGB images need uint8
:::

:::research
معالجة الصور في البحث: قياس المساحات الخضراء من صور الأقمار الصناعية (نسبة pixels الخضراء بقناع
منطقي)، عدّ الخلايا في صور المجهر، أو تجهيز صور لنماذج التعلم العميق (توحيد الحجم، التطبيع إلى [0, 1]).
للعمليات المتقدمة: **scikit-image** (خوارزميات علمية) و**OpenCV** (رؤية حاسوبية سريعة، وانتبه أن
ترتيب قنواتها BGR لا RGB).
:::

:::exercise id="ex-brighten":::

:::deep_dive
لماذا أوزان الرمادي `0.299, 0.587, 0.114` لا المتوسط البسيط؟ لأن العين البشرية أكثر حساسية للأخضر وأقل
حساسية للأزرق، وهذه الأوزان (من معيار الفيديو BT.601) تحافظ على الإضاءة المُدرَكة. وهي نفسها التي يستخدمها
`img.convert("L")` في Pillow.
:::

:::sketchnote
```text
image = grid of pixels → array (height, width, channels)     uint8: 0 … 255
RGB: a[:, :, 0] red · 1 green · 2 blue       (alpha = 4th channel)
crop a[y0:y1, x0:x1] · flip a[:, ::-1] · mask a[cond] = colour
Image.fromarray(a) ⇄ np.asarray(img)       img.size = (w, h) ≠ a.shape = (h, w, 3)
uint8 wraps (250 + 10 = 4) → astype(float), compute, clip(0, 255), astype(uint8)
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| فتح / حفظ | `Image.open(p)`، `img.save(p)` |
| إلى array / من array | `np.asarray(img)`، `Image.fromarray(a)` |
| رمادي | `img.convert("L")` |
| تغيير الحجم / تدوير | `img.resize((w, h))`، `img.rotate(90)` |
| قص | `a[y0:y1, x0:x1]` |
| عرض | `ax.imshow(a)` |
| حساب آمن | `np.clip(a.astype(float) + k, 0, 255).astype(np.uint8)` |
:::

:::quiz id="q-exit":::

:::docs
- [Pillow tutorial](https://pillow.readthedocs.io/en/stable/handbook/tutorial.html)
- [NumPy: images as arrays (tutorial)](https://numpy.org/numpy-tutorials/content/tutorial-svd.html)
- [Matplotlib: image tutorial](https://matplotlib.org/stable/tutorials/images.html)
:::
