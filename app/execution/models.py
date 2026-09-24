"""Typed result of one code execution (blueprint §85)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ExceptionInfo(BaseModel):
    type: str
    message: str
    traceback: str = ""
    lineno: int | None = None
    offset: int | None = None
    text: str | None = None
    missing_name: str | None = None
    frames: list[dict[str, Any]] = Field(default_factory=list)


class WarningInfo(BaseModel):
    category: str
    message: str
    lineno: int | None = None


class VariableInfo(BaseModel):
    name: str
    type: str
    module: str = "builtins"
    repr: str
    id: int
    mutable: bool | None = None
    length: int | None = None
    shape: list[int] | None = None
    dtype: str | None = None


class TraceStep(BaseModel):
    line: int
    event: str
    frame: str
    stack: list[str] = Field(default_factory=list)
    globals: dict[str, str] = Field(default_factory=dict)
    locals: dict[str, str] = Field(default_factory=dict)
    frames: list[dict[str, Any]] = Field(default_factory=list)
    stdout: str = ""
    return_value: str | None = None
    previews: dict[str, str] = Field(default_factory=dict)  # multi-line reprs that changed


class Trace(BaseModel):
    steps: list[TraceStep] = Field(default_factory=list)
    truncated: bool = False


class RunResult(BaseModel):
    status: Literal["ok", "error", "timeout", "runner_error"]
    stdout: str = ""
    stderr: str = ""
    stdout_truncated: bool = False
    result: dict[str, Any] | None = None
    warnings: list[WarningInfo] = Field(default_factory=list)
    exception: ExceptionInfo | None = None
    variables: list[VariableInfo] = Field(default_factory=list)
    figures: list[dict[str, str]] = Field(default_factory=list)
    trace: Trace | None = None
    timing_ms: float = 0.0
    inputs_used: list[str] = Field(default_factory=list)
    runner_message: str | None = None
    backend: str = "local"
    memory_peak_mb: float | None = None

    def alias_groups(self) -> dict[int, list[str]]:
        """Names bound to the same mutable object, e.g. {id: ["x", "y"]}."""
        groups: dict[int, list[str]] = {}
        for var in self.variables:
            groups.setdefault(var.id, []).append(var.name)
        return {k: v for k, v in groups.items() if len(v) > 1}
