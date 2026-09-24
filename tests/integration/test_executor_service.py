"""The execution API (executor_service/server.py) and the remote client, end to end."""

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from app.execution.client import run_code
from executor_service.server import clamp, make_handler

TOKEN = "test-token-123"


@pytest.fixture(scope="module")
def service_url():
    handler = make_handler("local", TOKEN, threading.BoundedSemaphore(2))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


def test_remote_backend_round_trip(service_url, monkeypatch):
    monkeypatch.setenv("PLL_EXECUTOR_URL", service_url)
    monkeypatch.setenv("PLL_EXECUTOR_TOKEN", TOKEN)
    r = run_code("x = 21\nx * 2", mode="notebook", backend="remote")
    assert r.status == "ok"
    assert r.result["text"] == "42"
    assert r.backend == "remote:local"


def test_wrong_token_is_rejected(service_url, monkeypatch):
    monkeypatch.setenv("PLL_EXECUTOR_URL", service_url)
    monkeypatch.setenv("PLL_EXECUTOR_TOKEN", "wrong")
    r = run_code("print(1)", backend="remote")
    assert r.status == "runner_error" and "401" in r.runner_message


def test_malformed_job_is_rejected(service_url):
    body = json.dumps({"job": {"code": 1}}).encode()
    req = urllib.request.Request(
        f"{service_url}/run",
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with pytest.raises(urllib.error.HTTPError) as err:
        urllib.request.urlopen(req, timeout=10)
    assert err.value.code == 400


def test_client_cannot_raise_limits_above_server_maxima():
    limits = clamp({"timeout_s": 10_000, "memory_mb": 10**6, "pids": "lots"})
    assert limits.timeout_s == 30.0 and limits.memory_mb == 1024
    assert limits.pids == 64
