from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import tempfile
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


class SUTError(Exception):
    pass


class SUTFormatError(ValueError):
    pass


def extract_json(text: str) -> dict:
    cleaned = ANSI.sub("", text).strip()
    start = cleaned.find("{")
    while start != -1:
        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(cleaned)):
            char = cleaned[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
            else:
                if char == '"':
                    in_string = True
                elif char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(cleaned[start : index + 1])
                        except json.JSONDecodeError:
                            break
        start = cleaned.find("{", start + 1)
    raise SUTFormatError("输出中没有合法 JSON 对象")


def _manual(prompt: str, case: dict, runs_dir: Path) -> tuple[dict | None, dict]:
    runs_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = runs_dir / f"{case['id']}.prompt.md"
    answer_path = runs_dir / f"{case['id']}.answer.json"
    prompt_path.write_text(prompt, encoding="utf-8")
    if answer_path.exists():
        return json.loads(answer_path.read_text(encoding="utf-8")), {"source": str(answer_path)}
    return None, {"pending": str(prompt_path)}


def _opencode(prompt: str, case: dict, model: str | None, timeout_s: float) -> tuple[dict, dict]:
    command = shlex.split(os.environ.get("EVAL_SUT_CMD", "opencode run --auto --format default"))
    if model:
        command += ["--model", model]
    workdir = tempfile.mkdtemp(prefix=f"eval-{case['id']}-", dir="/tmp")
    command += ["--dir", workdir, prompt]
    try:
        proc = subprocess.run(command, cwd=workdir, capture_output=True, text=True, timeout=timeout_s)
    except FileNotFoundError as exc:
        raise SUTError("找不到 opencode；设置 EVAL_SUT=manual 或安装 opencode") from exc
    except subprocess.TimeoutExpired as exc:
        raise SUTError(f"超时 {timeout_s:.0f}s") from exc
    if proc.returncode != 0:
        raise SUTError(f"退出码 {proc.returncode}: {proc.stderr[-500:]}")
    return extract_json(proc.stdout), {"source": "opencode", "stderr": proc.stderr[-1000:]}


def _mock(case: dict) -> tuple[dict, dict]:
    expect = case.get("expect", {})
    facts = []
    for item in expect.get("facts", []):
        source = (item.get("source_hosts") or ["example.com"])[0]
        facts.append(
            {
                "claim": " ".join(item.get("claim_contains", [])) or "mock",
                "value": item.get("value", ""),
                "source_url": f"https://{source}/",
            }
        )
    answer_rule = expect.get("answer", {})
    answer = " ".join(answer_rule.get("must_contain", [])) or " ".join(answer_rule.get("must_contain_any", [])) or "mock"
    route_rule = expect.get("route", {})
    return (
        {
            "status": (expect.get("status_any") or ["answered"])[0],
            "answer": answer,
            "route": {
                "domain": (route_rule.get("domain_any") or [case["domain"]])[0],
                "effort": (route_rule.get("effort_any") or ["quick"])[0],
                "channels": ["ddgs"],
                "queries": 1,
            },
            "facts": facts,
            "sources": [{"url": fact["source_url"], "title": "mock", "primary": True} for fact in facts],
            "as_of": case.get("as_of"),
            "confidence": "high",
            "notes": "",
        },
        {"source": "mock"},
    )


def run(
    prompt: str,
    case: dict,
    mode: str,
    model: str | None,
    timeout_s: float,
    runs_dir: Path,
) -> tuple[dict | None, dict]:
    if mode == "mock":
        return _mock(case)
    if mode == "manual":
        return _manual(prompt, case, runs_dir)
    if mode == "opencode":
        return _opencode(prompt, case, model, timeout_s)
    raise SUTError(f"未知 SUT: {mode}")
