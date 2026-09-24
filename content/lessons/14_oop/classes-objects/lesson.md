:::question
لديك حسابات بنكية: لكل حساب مالك ورصيد، وعمليات إيداع وسحب بقواعد (لا سحب أكثر من الرصيد). قاموس
لكل حساب ودوال منفصلة تعمل، لكن لا شيء يمنع تعديل الرصيد مباشرة. **كيف نجمع البيانات والقواعد التي
تحكمها في شيء واحد؟**
:::

:::theory title="البرمجة كائنية التوجه (OOP)"
في **البرمجة كائنية التوجه (Object-Oriented Programming)** نصمم البرنامج حول **كائنات (objects)**
تجمع **حالة (state)**: بياناتها، و**سلوكًا (behaviour)**: العمليات المسموحة عليها.

- **الـclass** قالب أو مخطط: «ما شكل الحساب وما يستطيع فعله».
- **الـinstance / object** نسخة ملموسة من القالب: حساب Sara وحساب Omar، لكل منهما رصيده.
- **attributes** بيانات الـobject (`acc.balance`)، و**methods** دواله (`acc.deposit(50)`).

ثلاث أفكار مركزية:

1. **Encapsulation (التغليف):** تغيير الحالة يمر عبر methods تطبق القواعد.
2. **Inheritance (الوراثة):** class جديد يبني على class موجود ويضيف أو يعدّل.
3. **Polymorphism (تعدد الأشكال):** objects مختلفة تستجيب للاستدعاء نفسه، كل بطريقته.

وتذكّر: في Python **كل شيء object** أصلًا؛ `"abc".upper()` استدعاء method على instance من class `str`.
:::

:::syntax
```python
class Account:                          # the blueprint
    bank = "PLL Bank"                   # class attribute: shared by all instances

    def __init__(self, owner, balance=0):   # runs when an instance is created
        self.owner = owner              # instance attributes: one copy per object
        self.balance = balance

    def deposit(self, amount):          # a method: first parameter is self
        self.balance += amount

acc = Account("Sara", 100)              # create an instance
acc.deposit(50)                         # ≈ Account.deposit(acc, 50)
```
:::

:::animation id="anim-instance":::

:::code mode="script"
class Account:
    bank = "PLL Bank"

    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount

    def __repr__(self):
        return f"Account({self.owner!r}, {self.balance})"

sara = Account("Sara", 100)
omar = Account("Omar")
sara.deposit(50)
print(sara, omar, sara.bank)
print(type(sara).__name__, isinstance(sara, Account))
:::

:::quiz id="q-self":::

:::quiz id="q-class-attr":::

:::concept
**`__repr__`** method خاصة (dunder = double underscore) يستدعيها Python عندما يعرض الـobject في الـREPL
أو داخل قائمة أو في `print` إن لم يوجد `__str__`. من دونها ترى نصًا غامضًا مثل
`<__main__.Account object at 0x7f…>`. وهناك methods خاصة كثيرة: `__len__` لـ`len()`، و`__eq__` لـ`==`،
و`__add__` لـ`+`.
:::

## dataclass: حاويات بيانات بأقل كود

:::code mode="script"
from dataclasses import dataclass, field

@dataclass
class Country:
    code: str
    population_m: float
    cities: list[str] = field(default_factory=list)

    def density_label(self) -> str:
        return "large" if self.population_m > 40 else "small"

dz = Country("DZ", 45.6, ["Algiers", "Oran"])
print(dz)                                   # generated __repr__
print(dz == Country("DZ", 45.6, ["Algiers", "Oran"]))   # generated __eq__
print(dz.density_label())
:::

## Inheritance: البناء على class موجود

:::code mode="script"
class Account:
    def __init__(self, owner, balance=0):
        self.owner, self.balance = owner, balance

    def monthly_fee(self):
        return 2.0

class StudentAccount(Account):              # inherits everything from Account
    def monthly_fee(self):                   # overrides one behaviour
        return 0.0

for acc in (Account("Sara"), StudentAccount("Lina")):
    print(type(acc).__name__, acc.owner, acc.monthly_fee())   # polymorphism
:::

:::mistake
- نسيان `self` في تعريف الـmethod: `def deposit(amount):` ثم
  `TypeError: deposit() takes 1 positional argument but 2 were given`.
- كتابة `balance = balance` بدل `self.balance = balance` داخل `__init__`: متغير local يختفي.
- وضع قائمة كـclass attribute (`history = []`) فتشاركها كل الـinstances. ضعها في `__init__`.
:::

:::code mode="script" expect="TypeError"
class Broken:
    def greet():
        return "hi"

Broken().greet()
:::

:::research
الـclasses مفيدة لتمثيل «كيانات» لها بيانات وقواعد: مجموعة بيانات بميتاداتها، نموذج تقدير له إعدادات
ونتائج، أو تجربة لها معاملات ومخرجات. لكن ليس كل شيء يحتاج class: دالة نقية تكفي غالبًا للتحويلات.
والمكتبات التي ستستعملها مبنية بالـOOP: `DataFrame` class، و`model.fit()` method.
:::

:::exercise id="ex-account":::

:::deep_dive
Python لا تفرض «خصوصية» صارمة: الاسم الذي يبدأ بـ`_` (`self._balance`) **اصطلاح** يقول «داخلي، لا
تلمسه». و`@property` تحوّل method إلى attribute محسوب أو محمي بالتحقق. وعند الوراثة المتعددة يحدد
**MRO** (Method Resolution Order) ترتيب البحث عن الـmethod، ويمكنك رؤيته بـ`ClassName.__mro__`.
:::

:::sketchnote
```text
CLASS = blueprint        INSTANCE = one concrete object       everything in Python is an object
__init__(self, …)  fills the new object          self = the instance itself
obj.method(x)  ≈  Class.method(obj, x)
instance attribute (self.x) = per object      class attribute = shared
__repr__ for display     @dataclass → __init__ / __repr__ / __eq__ for free
inheritance: class Child(Parent)   override a method   → polymorphism
```
:::

:::cheatsheet
| الحاجة | الكود |
|---|---|
| تعريف class | `class Name:` |
| البناء | `def __init__(self, a):` |
| حالة الـobject | `self.a = a` |
| method | `def act(self, x):` |
| عرض واضح | `def __repr__(self):` |
| حاوية بيانات | `@dataclass` |
| وراثة | `class Child(Parent):` |
:::

:::quiz id="q-exit":::

:::docs
- [Classes — Python Tutorial](https://docs.python.org/3/tutorial/classes.html)
- [dataclasses — Data Classes](https://docs.python.org/3/library/dataclasses.html)
- [Data model: special method names](https://docs.python.org/3/reference/datamodel.html#special-method-names)
:::
