"""Remote backend: the Streamlit UI calls the execution API (blueprint §5.6).

    Browser / Streamlit UI  ->  POST {PLL_EXECUTOR_URL}/run  ->  isolated worker

The shared secret is read from the environment (PLL_EXECUTOR_TOKEN), never from code.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from app.execution.limits import Limits, runner_error
from app.execution.models import RunResult

BACKEND = "remote"


def run(job: dict, limits: Limits) -> RunResult:
    url = os.environ.get("PLL_EXECUTOR_URL", "http://127.0.0.1:8765").rstrip("/") + "/run"
    body = json.dumps({"job": job, "limits": limits.as_dict()}, ensure_ascii=False).encode()
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('PLL_EXECUTOR_TOKEN', '')}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=limits.timeout_s + 20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return runner_error(f"Execution service returned HTTP {exc.code}.", BACKEND)
    except (urllib.error.URLError, TimeoutError) as exc:
        return runner_error(f"Execution service unreachable: {exc}", BACKEND)
    result = RunResult.model_validate(data)
    result.backend = f"{BACKEND}:{result.backend}"
    return result
