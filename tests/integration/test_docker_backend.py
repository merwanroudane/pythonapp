"""Docker sandbox checks. Skipped unless a Docker engine is running and the runtime
image exists (docker build -f executor_service/docker/Dockerfile --target scientific
-t pll-runner:scientific .)."""

import os
import subprocess

import pytest

from app.execution.client import run_code
from app.execution.docker_backend import DEFAULT_IMAGE, build_command, docker_available
from app.execution.limits import Limits


def _image_present() -> bool:
    image = os.environ.get("PLL_DOCKER_IMAGE", DEFAULT_IMAGE)
    probe = subprocess.run(["docker", "image", "inspect", image], capture_output=True)
    return probe.returncode == 0


needs_docker = pytest.mark.skipif(
    not (docker_available() and _image_present()), reason="Docker engine or image unavailable"
)


def test_command_is_locked_down():
    cmd = " ".join(build_command("x", Limits(), "img", mount_harness=False))
    for flag in (
        "--network none",
        "--read-only",
        "--cap-drop ALL",
        "--user 65534:65534",
        "no-new-privileges",
        "--pids-limit 64",
        "--memory 512m",
    ):
        assert flag in cmd


@needs_docker
def test_docker_runs_code():
    r = run_code("print(6 * 7)", backend="docker", timeout=10)
    assert r.status == "ok" and r.stdout == "42\n" and r.backend == "docker"


@needs_docker
def test_docker_has_no_network():
    r = run_code(
        "import socket\nsocket.create_connection(('1.1.1.1', 53), timeout=2)",
        backend="docker",
        timeout=10,
    )
    assert r.status == "error"


@needs_docker
def test_docker_filesystem_is_read_only_outside_work():
    r = run_code("open('/etc/pwned', 'w')", backend="docker", timeout=10)
    assert r.status == "error"
