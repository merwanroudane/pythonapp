"""Single entry point for running learner code.

The backend is chosen with the PLL_EXECUTOR environment variable:

    local   (default) hardened child process — development and single-user use
    docker  ephemeral locked-down container per run — isolation for shared machines
    remote  HTTP call to executor_service — UI and sandbox on different hosts

All three speak the same job/result contract (app/execution/limits.py, harness.py).
"""

from __future__ import annotations

import os

from app.execution import docker_backend, local_backend, remote_backend
from app.execution.limits import Limits, make_job
from app.execution.models import RunResult

BACKENDS = {
    "local": local_backend.run,
    "docker": docker_backend.run,
    "remote": remote_backend.run,
}


def backend_name() -> str:
    name = os.environ.get("PLL_EXECUTOR", "local").strip().lower()
    return name if name in BACKENDS else "local"


def is_sandboxed() -> bool:
    return backend_name() in ("docker", "remote")


def run_code(
    code: str,
    *,
    mode: str = "script",
    trace: bool = False,
    inputs: list[str] | None = None,
    timeout: float | None = None,
    backend: str | None = None,
) -> RunResult:
    job = make_job(code, mode, trace, inputs or [])
    return BACKENDS[backend or backend_name()](job, Limits.from_env(timeout))
