"""Execution limits and the job contract shared by every backend (blueprint §5.7, §103)."""

from __future__ import annotations

import json
import os
import secrets
from dataclasses import asdict, dataclass

from app.execution.models import RunResult


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default


@dataclass(frozen=True)
class Limits:
    timeout_s: float = 5.0
    memory_mb: int = 512
    max_file_mb: int = 16  # size of any file the code writes (POSIX / Docker)
    cpus: float = 1.0  # Docker only
    pids: int = 64  # Docker only; the local backend allows a single process

    @classmethod
    def from_env(cls, timeout_s: float | None = None) -> Limits:
        return cls(
            timeout_s=timeout_s if timeout_s is not None else _env_float("PLL_TIMEOUT_S", 5.0),
            memory_mb=int(_env_float("PLL_MEMORY_MB", 512)),
        )

    def as_dict(self) -> dict:
        return asdict(self)


def make_job(code: str, mode: str, trace: bool, inputs: list[str]) -> dict:
    """The JSON job every backend feeds to harness.py."""
    return {
        "code": code,
        "mode": mode,
        "trace": trace,
        "inputs": inputs,
        # Marks where the harness's JSON result starts on stdout (Docker / stdin mode), so
        # anything the learner writes straight to the real stdout cannot be mistaken for it.
        "boundary": f"==PLL-RESULT-{secrets.token_hex(8)}==",
    }


def parse_stdout_result(stdout: bytes, boundary: str) -> RunResult | None:
    text = stdout.decode("utf-8", "replace")
    marker = text.rfind(boundary)
    if marker < 0:
        return None
    payload = text[marker + len(boundary) :].strip()
    try:
        return RunResult.model_validate(json.loads(payload))
    except (ValueError, TypeError):
        return None


def timeout_result(limits: Limits, backend: str) -> RunResult:
    return RunResult(
        status="timeout",
        backend=backend,
        runner_message=f"Stopped after {limits.timeout_s:g} s (possible infinite loop).",
    )


def runner_error(message: str, backend: str) -> RunResult:
    return RunResult(status="runner_error", backend=backend, runner_message=message[-2000:])
