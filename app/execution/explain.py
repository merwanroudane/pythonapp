"""Rule-based error explanation engine (blueprint §86).

Turns a structured exception into a short Arabic diagnosis plus a hint that asks the
learner to look before handing over a fix.
"""

from __future__ import annotations

import builtins
import difflib
import keyword
from dataclasses import dataclass

from app.execution.models import ExceptionInfo


@dataclass(frozen=True)
class Explanation:
    category: str
    what: str
    hint: str


_RULES: dict[str, tuple[str, str, str]] = {
    "SyntaxError": (
        "Syntax error",
        "لم يستطع Python قراءة البرنامج أصلًا؛ لم يُنفَّذ أي سطر.",
        "انظر إلى السهم `^` في الـtraceback: هل تنقص نقطتان `:` أو قوس أو علامة تنصيص؟",
    ),
    "IndentationError": (
        "Syntax error",
        "الإزاحة indentation جزء من syntax في Python، وهنا لا تطابق البنية المتوقعة.",
        "هل السطر بعد `:` مُزاح بأربع مسافات؟ وهل كل أسطر الـblock على المستوى نفسه؟",
    ),
    "TabError": (
        "Syntax error",
        "خُلطت Tabs مع Spaces في الإزاحة نفسها.",
        "استخدم أربع مسافات فقط، ولا تخلطها مع Tab.",
    ),
    "NameError": (
        "Runtime exception",
        "استُخدم اسم لا يعرفه Python في هذه اللحظة من التنفيذ.",
        "هل الاسم مكتوب بشكل صحيح؟ وهل عُرّف قبل هذا السطر؟",
    ),
    "TypeError": (
        "Runtime exception",
        "العملية لا تناسب نوع (type) القيمة التي وصلت إليها.",
        "اطبع `type()` للقيم المشاركة في السطر. هل تجمع `str` مع `int` مثلًا؟",
    ),
    "ValueError": (
        "Runtime exception",
        "النوع مقبول لكن القيمة نفسها غير صالحة لهذه العملية.",
        "مثال شائع: `int('3.5')` أو `int('abc')`. ما القيمة الفعلية التي وصلت؟",
    ),
    "ZeroDivisionError": (
        "Runtime exception",
        "حدثت قسمة على صفر.",
        "من أين أتى المقام؟ هل يجب فحصه قبل القسمة؟",
    ),
    "IndexError": (
        "Runtime exception",
        "طُلب موضع غير موجود في sequence.",
        "آخر index صالح هو `len(x) - 1`. هل هذا خطأ off-by-one؟",
    ),
    "KeyError": (
        "Runtime exception",
        "المفتاح غير موجود في الـdictionary.",
        "اطبع `d.keys()`. هل المفتاح مطلوب فعلًا، أم يناسبك `d.get(key)`؟",
    ),
    "AttributeError": (
        "Runtime exception",
        "هذا الـobject لا يملك attribute أو method بهذا الاسم.",
        "ما نوع الـobject فعلًا؟ جرّب `type(obj)` و`dir(obj)`.",
    ),
    "ModuleNotFoundError": (
        "Environment",
        "لم يجد Python الـmodule في الـinterpreter الذي يشغّل الكود.",
        "هل المكتبة مثبتة في نفس interpreter؟ قارن `sys.executable` بمسار بيئتك.",
    ),
    "FileNotFoundError": (
        "Environment",
        "المسار لا يشير إلى ملف موجود بالنسبة إلى current working directory.",
        "اطبع `Path.cwd()` و`Path(p).resolve()` وتأكد أين يبحث Python.",
    ),
    "RecursionError": (
        "Runtime exception",
        "استدعاء ذاتي بلا نهاية: الـbase case لا يتحقق أبدًا.",
        "ما الشرط الذي يوقف الـrecursion؟ هل تقترب المدخلات منه في كل استدعاء؟",
    ),
    "InputExhausted": (
        "Runner",
        "استدعى الكود `input()` أكثر من عدد القيم الموجودة في صندوق Inputs.",
        "أضف قيمة لكل استدعاء `input()`، كل قيمة في سطر مستقل.",
    ),
    "AssertionError": (
        "Check failed",
        "شرط `assert` لم يتحقق.",
        "اقرأ رسالة الـassert؛ هي تصف ما كان متوقعًا.",
    ),
}


def _typo_suggestion(name: str | None, known: list[str]) -> str | None:
    if not name:
        return None
    candidates = list(known) + dir(builtins) + keyword.kwlist
    match = difflib.get_close_matches(name, candidates, n=1, cutoff=0.75)
    return match[0] if match and match[0] != name else None


def explain(exc: ExceptionInfo, known_names: list[str] | None = None) -> Explanation:
    category, what, hint = _RULES.get(
        exc.type,
        (
            "Runtime exception",
            f"حدث استثناء من نوع `{exc.type}` أثناء التنفيذ.",
            "اقرأ آخر سطر في الـtraceback أولًا، ثم ارجع إلى السطر المشار إليه.",
        ),
    )
    if exc.type in ("TypeError", "AttributeError") and "NoneType" in exc.message:
        hint = (
            "إحدى القيم هنا هي `None`. هل جاءت من دالة كتبتها أنت؟ "
            "الدالة التي لا تحتوي `return` تُعيد `None` ضمنيًا."
        )
    if exc.type == "NameError":
        guess = _typo_suggestion(exc.missing_name, known_names or [])
        if guess:
            hint = f"قارن الاسم `{exc.missing_name}` مع `{guess}` حرفًا بحرف. ما الفرق؟"
    return Explanation(category=category, what=what, hint=hint)
