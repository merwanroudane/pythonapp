"""Local backend: a fresh, resource-limited child interpreter per run.

Isolation it provides:
  * separate process, never the Streamlit process (§5.6);
  * empty temporary working folder; job/result files live *outside* it;
  * stripped environment — no app secrets or tokens are inherited;
  * wall-clock timeout that kills the whole process tree;
  * memory cap and a ban on spawning further processes:
      - Windows: a Job Object (process memory limit, active-process limit 1,
        kill-on-close), the child is created suspended and resumed only once inside it;
      - POSIX: RLIMIT_AS / RLIMIT_FSIZE / RLIMIT_CPU / RLIMIT_CORE in its own session.

What it does NOT provide: a network block or a filesystem jail. Use the Docker backend
(or the remote execution service backed by it) for anything public (§103.2).
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from app.execution.limits import Limits, runner_error, timeout_result
from app.execution.models import RunResult

HARNESS = Path(__file__).with_name("harness.py")
BACKEND = "local"
# Matplotlib builds a font cache on first import; keep it outside the per-run sandbox so
# it is built once per machine instead of on every run (which would hit the timeout).
MPL_CACHE = Path(tempfile.gettempdir()) / "pll-mplconfig"
_ENV_ALLOWLIST = ("SYSTEMROOT", "WINDIR", "PATH", "LANG", "LC_ALL")


def _child_env(workdir: str) -> dict[str, str]:
    MPL_CACHE.mkdir(exist_ok=True)
    env = {k: os.environ[k] for k in _ENV_ALLOWLIST if k in os.environ}
    env.update(
        {
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "MPLBACKEND": "Agg",
            "MPLCONFIGDIR": str(MPL_CACHE),
            # One thread for BLAS/OpenMP: predictable memory under the address-space cap.
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "TEMP": workdir,
            "TMP": workdir,
            "HOME": workdir,
            "USERPROFILE": workdir,
        }
    )
    return env


# --------------------------------------------------------------------------- Windows
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _ntdll = ctypes.WinDLL("ntdll")

    _JOB_EXTENDED_LIMIT_INFORMATION = 9
    _LIMIT_ACTIVE_PROCESS = 0x0008
    _LIMIT_PROCESS_MEMORY = 0x0100
    _LIMIT_DIE_ON_UNHANDLED_EXCEPTION = 0x0400
    _LIMIT_KILL_ON_JOB_CLOSE = 0x2000
    _CREATE_SUSPENDED = 0x0004
    _CREATE_NO_WINDOW = 0x08000000

    class _IoCounters(ctypes.Structure):
        _fields_ = [
            (name, ctypes.c_ulonglong)
            for name in (
                "ReadOperationCount",
                "WriteOperationCount",
                "OtherOperationCount",
                "ReadTransferCount",
                "WriteTransferCount",
                "OtherTransferCount",
            )
        ]

    class _BasicLimits(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class _ExtendedLimits(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _BasicLimits),
            ("IoInfo", _IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    _kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    _kernel32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    _kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        wintypes.LPVOID,
        wintypes.DWORD,
    ]
    _kernel32.QueryInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.LPVOID,
    ]
    _kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    _kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    _ntdll.NtResumeProcess.argtypes = [wintypes.HANDLE]

    def _create_job(limits: Limits) -> int:
        job = _kernel32.CreateJobObjectW(None, None)
        if not job:
            raise ctypes.WinError(ctypes.get_last_error())
        info = _ExtendedLimits()
        info.BasicLimitInformation.LimitFlags = (
            _LIMIT_ACTIVE_PROCESS
            | _LIMIT_PROCESS_MEMORY
            | _LIMIT_DIE_ON_UNHANDLED_EXCEPTION
            | _LIMIT_KILL_ON_JOB_CLOSE
        )
        info.BasicLimitInformation.ActiveProcessLimit = 1
        info.ProcessMemoryLimit = limits.memory_mb * 1024 * 1024
        ok = _kernel32.SetInformationJobObject(
            job, _JOB_EXTENDED_LIMIT_INFORMATION, ctypes.byref(info), ctypes.sizeof(info)
        )
        if not ok:
            _kernel32.CloseHandle(job)
            raise ctypes.WinError(ctypes.get_last_error())
        return job

    def _peak_mb(job: int) -> float | None:
        info = _ExtendedLimits()
        ok = _kernel32.QueryInformationJobObject(
            job, _JOB_EXTENDED_LIMIT_INFORMATION, ctypes.byref(info), ctypes.sizeof(info), None
        )
        return round(info.PeakProcessMemoryUsed / 2**20, 1) if ok else None

    def _launch(cmd, workdir, env, limits):
        job = _create_job(limits)
        proc = subprocess.Popen(
            cmd,
            cwd=workdir,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=_CREATE_SUSPENDED | _CREATE_NO_WINDOW,
        )
        handle = int(proc._handle)  # noqa: SLF001 - documented CPython attribute on Windows
        if not _kernel32.AssignProcessToJobObject(job, handle):
            proc.kill()
            _kernel32.CloseHandle(job)
            raise ctypes.WinError(ctypes.get_last_error())
        _ntdll.NtResumeProcess(handle)
        return proc, job

    def _kill(proc, job) -> None:
        _kernel32.TerminateJobObject(job, 1)
        proc.wait()

    def _finish(proc, job) -> float | None:
        peak = _peak_mb(job)
        _kernel32.CloseHandle(job)
        return peak

# ----------------------------------------------------------------------------- POSIX
else:
    import resource

    def _launch(cmd, workdir, env, limits):
        mem = limits.memory_mb * 1024 * 1024
        fsize = limits.max_file_mb * 1024 * 1024
        cpu = int(limits.timeout_s) + 1

        def apply_limits() -> None:
            for which, value in (
                (resource.RLIMIT_AS, mem),
                (resource.RLIMIT_FSIZE, fsize),
                (resource.RLIMIT_CPU, cpu),
                (resource.RLIMIT_CORE, 0),
            ):
                # Never ask for more than the host's hard limit (e.g. inside containers),
                # otherwise setrlimit fails and no run could ever start.
                _, hard = resource.getrlimit(which)
                capped = value if hard == resource.RLIM_INFINITY else min(value, hard)
                resource.setrlimit(which, (capped, capped))

        proc = subprocess.Popen(
            cmd,
            cwd=workdir,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=apply_limits,  # noqa: PLW1509 - single-threaded child setup only
            start_new_session=True,
        )
        return proc, None

    def _kill(proc, job) -> None:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()

    def _finish(proc, job) -> float | None:
        return None  # the harness reports its own peak (RUSAGE_SELF) on POSIX


def run(job: dict, limits: Limits) -> RunResult:
    with tempfile.TemporaryDirectory(prefix="pll-run-") as root:
        workdir = Path(root) / "work"  # the learner's cwd: starts empty
        workdir.mkdir()
        job_path, result_path = Path(root) / "job.json", Path(root) / "result.json"
        job_path.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
        cmd = [sys.executable, "-I", "-X", "utf8", str(HARNESS), str(job_path), str(result_path)]
        try:
            proc, handle = _launch(cmd, str(workdir), _child_env(str(workdir)), limits)
        except (OSError, subprocess.SubprocessError) as exc:
            return runner_error(f"Could not start the runner: {exc}", BACKEND)
        try:
            _, stderr = proc.communicate(timeout=limits.timeout_s)
        except subprocess.TimeoutExpired:
            _kill(proc, handle)
            _finish(proc, handle)
            return timeout_result(limits, BACKEND)
        peak = _finish(proc, handle)
        if not result_path.exists():
            detail = stderr.decode("utf-8", "replace")
            if proc.returncode and not detail:
                detail = f"Runner exited with code {proc.returncode} (memory limit?)"
            return runner_error(detail or "Runner produced no result.", BACKEND)
        data = json.loads(result_path.read_text(encoding="utf-8"))
    result = RunResult.model_validate(data)
    result.backend = BACKEND
    if peak is not None:
        result.memory_peak_mb = peak
    return result
