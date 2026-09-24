"""Docker backend: an ephemeral, locked-down container per run (blueprint §103.2).

    docker run --rm -i --network none --read-only --user 65534:65534 --cap-drop ALL
               --security-opt no-new-privileges --memory … --pids-limit … --cpus …
               --tmpfs /work … <image> python -I -X utf8 /opt/pll/harness.py -

The job goes in on stdin and the result comes back on stdout after a random boundary.
Nothing from the host is mounted except (optionally, for development) the harness file,
read-only. Build the runtime images from executor_service/docker/ (see README).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from app.execution.limits import Limits, parse_stdout_result, runner_error, timeout_result
from app.execution.models import RunResult

BACKEND = "docker"
HARNESS = Path(__file__).with_name("harness.py")
DEFAULT_IMAGE = "pll-runner:scientific"


def docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    probe = subprocess.run(
        ["docker", "info", "--format", "{{.ServerVersion}}"], capture_output=True, timeout=15
    )
    return probe.returncode == 0


def build_command(name: str, limits: Limits, image: str, mount_harness: bool) -> list[str]:
    cmd = [
        "docker", "run", "--rm", "-i",
        "--name", name,
        "--network", "none",
        "--read-only",
        "--user", "65534:65534",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--memory", f"{limits.memory_mb}m",
        "--memory-swap", f"{limits.memory_mb}m",
        "--pids-limit", str(limits.pids),
        "--cpus", str(limits.cpus),
        "--ulimit", f"fsize={limits.max_file_mb * 1024 * 1024}",
        "--tmpfs", f"/work:rw,size={limits.max_file_mb}m,mode=1777",
        "--tmpfs", "/tmp:rw,size=16m,mode=1777",
        "--workdir", "/work",
        "--env", "HOME=/work",
        "--env", "MPLBACKEND=Agg",
        "--env", "MPLCONFIGDIR=/tmp",
        "--env", "PYTHONDONTWRITEBYTECODE=1",
    ]  # fmt: skip
    if mount_harness:
        cmd += ["--volume", f"{HARNESS}:/opt/pll/harness.py:ro"]
    cmd += [image, "python", "-I", "-X", "utf8", "/opt/pll/harness.py", "-"]
    return cmd


def run(job: dict, limits: Limits) -> RunResult:
    image = os.environ.get("PLL_DOCKER_IMAGE", DEFAULT_IMAGE)
    mount = os.environ.get("PLL_DOCKER_MOUNT_HARNESS", "1") == "1"
    name = f"pll-{uuid.uuid4().hex[:12]}"
    cmd = build_command(name, limits, image, mount)
    try:
        proc = subprocess.run(
            cmd,
            input=json.dumps(job, ensure_ascii=False).encode("utf-8"),
            capture_output=True,
            # container start-up time is not the learner's fault
            timeout=limits.timeout_s + 10,
        )
    except FileNotFoundError:
        return runner_error("Docker CLI not found.", BACKEND)
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "kill", name], capture_output=True, timeout=15)
        return timeout_result(limits, BACKEND)
    result = parse_stdout_result(proc.stdout, job["boundary"])
    if result is None:
        if proc.returncode == 137:
            return runner_error("The container was killed (memory limit exceeded).", BACKEND)
        return runner_error(proc.stderr.decode("utf-8", "replace") or "No result.", BACKEND)
    result.backend = BACKEND
    return result
