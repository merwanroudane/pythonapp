"""Content schema (blueprint §80): tracks, lessons, and the interactive items they use."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

Level = Literal["beginner", "intermediate", "advanced", "expert", "beginner_to_intermediate"]
RunMode = Literal["script", "notebook"]


class Track(BaseModel):
    id: str
    order: int
    code: str  # "00" .. "24"
    title_ar: str
    title_en: str
    icon: str
    level: Level = "beginner"
    summary_ar: str = ""
    prerequisites: list[str] = Field(default_factory=list)


class Quiz(BaseModel):
    kind: Literal["predict", "concept", "exit"] = "concept"
    question: str
    code: str | None = None
    options: list[str]
    answer: int
    explanation: str

    @model_validator(mode="after")
    def _answer_in_range(self) -> Quiz:
        if not 0 <= self.answer < len(self.options):
            raise ValueError("answer index out of range")
        return self


class Exercise(BaseModel):
    title: str
    prompt: str
    starter: str
    solution: str
    tests: str
    hints: list[str] = Field(default_factory=list)
    mode: RunMode = "script"


class CommandNote(BaseModel):
    """Step-by-step explanation of one command (the line about to run in an animation)."""

    what: str  # what this command does, in one or two sentences
    parts: list[tuple[str, str]] = Field(default_factory=list)  # anatomy: (code piece, meaning)
    theory: str = ""  # the concept behind it: why it works this way


class AnimationStep(BaseModel):
    line: int
    note: str = ""
    parts: list[tuple[str, str]] = Field(default_factory=list)
    theory: str = ""
    state: dict[str, str] = Field(default_factory=dict)
    stdout: str = ""


class Animation(BaseModel):
    title: str
    code: str
    source: Literal["trace", "authored"] = "trace"
    steps: list[AnimationStep] = Field(default_factory=list)
    # line -> explanation (trace mode): a sentence, or a CommandNote with anatomy and theory
    notes: dict[int, str | CommandNote] = Field(default_factory=dict)


class Variant(BaseModel):
    label: str
    code: str
    explain: str


class ChangeObserve(BaseModel):
    title: str
    base: str
    base_label: str = "قبل Before"
    variants: list[Variant]
    mode: RunMode = "script"


class LessonMeta(BaseModel):
    id: str
    track: str
    order: int
    title_ar: str
    title_en: str
    # "theory": a conceptual lecture before code (no exercise required); "practice": default
    kind: Literal["practice", "theory"] = "practice"
    level: Level = "beginner"
    estimated_minutes: int = 20
    prerequisites: list[str] = Field(default_factory=list)
    objectives: list[str] = Field(default_factory=list)
    docs_url: str | None = None
    last_verified: str | None = None
    python_min: str = "3.11"
    tags: list[str] = Field(default_factory=list)
    quizzes: dict[str, Quiz] = Field(default_factory=dict)
    exercises: dict[str, Exercise] = Field(default_factory=dict)
    animations: dict[str, Animation] = Field(default_factory=dict)
    changes: dict[str, ChangeObserve] = Field(default_factory=dict)


class Block(BaseModel):
    type: str
    attrs: dict[str, str] = Field(default_factory=dict)
    body: str = ""
    line: int = 0  # 1-based line in lesson.md, for validation messages


class Lesson(BaseModel):
    meta: LessonMeta
    blocks: list[Block]
    source_dir: str
