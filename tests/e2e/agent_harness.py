from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_RUN_TIMEOUT_SECONDS = 120.0


def _resolve_runner() -> str:
    runner = os.environ.get("SKILL_AGENT_RUNNER")
    if not runner:
        raise RuntimeError("SKILL_AGENT_RUNNER must point to an executable runner path")

    runner_path = Path(runner).expanduser()
    if not runner_path.exists():
        raise RuntimeError(f"SKILL_AGENT_RUNNER path does not exist: {runner_path}")
    if not runner_path.is_file() or not os.access(runner_path, os.X_OK):
        raise RuntimeError(f"SKILL_AGENT_RUNNER path is not executable: {runner_path}")
    return str(runner_path)


def run_agent_prompt(prompt: str) -> subprocess.CompletedProcess[str]:
    runner = _resolve_runner()
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    try:
        return subprocess.run(
            [runner],
            input=prompt,
            text=True,
            capture_output=True,
            cwd=REPO_ROOT,
            env=env,
            check=False,
            timeout=AGENT_RUN_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Agent runner timed out after {AGENT_RUN_TIMEOUT_SECONDS}s\n"
            f"stdout:\n{exc.stdout or ''}\n"
            f"stderr:\n{exc.stderr or ''}"
        ) from exc
