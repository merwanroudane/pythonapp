"""Catalogue of lesson block types (blueprint §2.7, §81).

One place defines each block's label, icon, colour family and which lecture views
(Learn / Review / Reference, §2.9) it appears in. The renderer and the content
validator both read from here, so a new block type is added once.
"""

from __future__ import annotations

from dataclasses import dataclass

LEARN, REVIEW, REFERENCE = "learn", "review", "reference"
ALL_VIEWS = frozenset({LEARN, REVIEW, REFERENCE})


@dataclass(frozen=True)
class CardStyle:
    label: str
    icon: str
    tone: str  # CSS colour family, see app/ui/theme.py
    views: frozenset[str] = frozenset({LEARN})
    collapsible: bool = False


CARDS: dict[str, CardStyle] = {
    "question": CardStyle("سؤال البداية · Opening Question", ":material/help:", "highlight"),
    "concept": CardStyle("الفكرة · Intuition", ":material/lightbulb:", "concept"),
    "definition": CardStyle(
        "تعريف · Definition", ":material/menu_book:", "concept", frozenset({LEARN, REFERENCE})
    ),
    "theory": CardStyle(
        "الإطار النظري · Theory", ":material/school:", "theory", frozenset({LEARN, REFERENCE})
    ),
    "syntax": CardStyle(
        "تشريح الصياغة · Syntax Anatomy",
        ":material/data_object:",
        "example",
        frozenset({LEARN, REFERENCE}),
    ),
    "research": CardStyle("لماذا يهم الباحث؟ · Research Note", ":material/science:", "data"),
    "warning": CardStyle(
        "انتبه · Warning", ":material/warning:", "warning", frozenset({LEARN, REVIEW})
    ),
    "mistake": CardStyle(
        "خطأ شائع · Common Mistake", ":material/bug_report:", "error", frozenset({LEARN, REVIEW})
    ),
    "rule": CardStyle(
        "قاعدة سريعة · Rule of Thumb", ":material/rule:", "insight", frozenset({LEARN, REVIEW})
    ),
    "tip": CardStyle("نصيحة · Tip", ":material/tips_and_updates:", "insight"),
    "think": CardStyle("سؤال تفكير · Think", ":material/psychology:", "insight"),
    "try": CardStyle("جرّب بنفسك · Try It", ":material/edit_note:", "practice"),
    "note": CardStyle("ملاحظة · Note", ":material/sticky_note_2:", "neutral"),
    "deep_dive": CardStyle("تعمّق · Deep Dive", ":material/layers:", "deepdive", collapsible=True),
    "under_the_hood": CardStyle(
        "ما يحدث في الداخل · Under the Hood", ":material/memory:", "deepdive", collapsible=True
    ),
    "sketchnote": CardStyle(
        "بطاقة مراجعة · Sketchnote", ":material/draw:", "example", frozenset({LEARN, REVIEW})
    ),
    "cheatsheet": CardStyle("ملخص سريع · Cheat Sheet", ":material/summarize:", "data", ALL_VIEWS),
    "docs": CardStyle(
        "التوثيق الرسمي · Official Docs", ":material/link:", "data", frozenset({LEARN, REFERENCE})
    ),
}

# Interactive / structural blocks and the views they appear in.
INTERACTIVE: dict[str, frozenset[str]] = {
    "markdown": frozenset({LEARN}),
    "code": frozenset({LEARN}),
    "quiz": frozenset({LEARN}),
    "exercise": frozenset({LEARN}),
    "animation": frozenset({LEARN}),
    "change": frozenset({LEARN}),
    "diagram": frozenset({LEARN}),
    "compare": frozenset({LEARN, REVIEW, REFERENCE}),
    "property_lab": frozenset({LEARN, REFERENCE}),
}

# Which lesson.yaml collection each id-referencing block points into.
REFERENCES = {
    "quiz": "quizzes",
    "exercise": "exercises",
    "animation": "animations",
    "change": "changes",
}

KNOWN_TYPES = frozenset(CARDS) | frozenset(INTERACTIVE)


def views_for(block_type: str, attrs: dict[str, str]) -> frozenset[str]:
    if "views" in attrs:
        return frozenset(v.strip() for v in attrs["views"].split(","))
    if block_type in CARDS:
        return CARDS[block_type].views
    return INTERACTIVE.get(block_type, frozenset({LEARN}))
