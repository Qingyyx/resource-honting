from __future__ import annotations

import math
import re
import unicodedata
from urllib.parse import urlparse

STATUSES = {"PASS", "FAIL", "FORMAT_FAIL", "ERROR", "BLOCKED", "STALE", "PENDING"}


def norm(value) -> str:
    text = unicodedata.normalize("NFKC", str(value)).lower()
    text = text.replace("％", "%").replace(",", "").replace("，", "")
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"(\d{4})年(\d{1,2})月(\d{1,2})日", lambda m: f"{m[1]}-{int(m[2]):02d}-{int(m[3]):02d}", text)
    text = re.sub(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", lambda m: f"{m[1]}-{int(m[2]):02d}-{int(m[3]):02d}", text)
    text = re.sub(r"(\d+)\.0+(?=%)", r"\1", text)
    return text


def host(url: str) -> str:
    try:
        return (urlparse(str(url)).hostname or "").lower().removeprefix("www.")
    except ValueError:
        return ""


def host_allowed(actual: str, allowed: list[str]) -> bool:
    if not actual:
        return False
    for item in allowed or []:
        expected = str(item).lower().removeprefix("www.")
        if actual == expected or actual.endswith("." + expected):
            return True
    return False


def wilson(passed: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 0.0)
    p = passed / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def check(name: str, ok: bool, detail: str = "", required: bool = True) -> dict:
    return {"name": name, "ok": bool(ok), "detail": detail, "required": required}


def _route_checks(case: dict, out: dict, include_channels: bool = True) -> list[dict]:
    route = out.get("route")
    if not isinstance(route, dict):
        return [check("route", False, "缺少 route 对象")]
    rule = case.get("expect", {}).get("route", {})
    checks = []

    domain = route.get("domain")
    domains = rule.get("domain_any") or [case.get("domain")]
    checks.append(check("route.domain", domain in domains, f"{domain!r} 不在 {domains}"))

    effort = route.get("effort")
    efforts = rule.get("effort_any") or ["quick", "standard", "deep"]
    checks.append(check("route.effort", effort in efforts, f"{effort!r} 不在 {efforts}"))

    channels = route.get("channels")
    if not include_channels:
        channels = []
    if not isinstance(channels, list):
        checks.append(check("route.channels", False, "channels 必须是数组"))
        channels = []
    if include_channels and rule.get("channels_any"):
        hit = [c for c in channels if c in rule["channels_any"]]
        checks.append(check("route.channels_any", bool(hit), f"{channels} 与 {rule['channels_any']} 无交集"))
    if include_channels and rule.get("channels_not"):
        bad = [c for c in channels if c in rule["channels_not"]]
        checks.append(check("route.channels_not", not bad, f"使用了禁用通道 {bad}"))

    queries = route.get("queries")
    max_queries = case.get("budget", {}).get("max_queries", 0)
    checks.append(check("route.queries", isinstance(queries, int) and 0 <= queries <= max_queries, f"{queries!r} > {max_queries}"))
    return checks


def _answer_checks(case: dict, out: dict) -> list[dict]:
    text = out.get("answer")
    if not isinstance(text, str):
        return [check("answer", False, "answer 必须是字符串")]
    body = norm(text)
    rule = case.get("expect", {}).get("answer", {})
    checks = []

    for key, required_all in (("must_contain", True), ("must_contain_all", True)):
        values = rule.get(key) or []
        if values:
            missing = [v for v in values if norm(v) not in body]
            checks.append(check(f"answer.{key}", not missing, f"缺少 {missing}"))

    values = rule.get("must_contain_any") or []
    if values:
        hit = [v for v in values if norm(v) in body]
        checks.append(check("answer.must_contain_any", bool(hit), f"{values} 一个都没出现"))

    groups = rule.get("must_contain_groups") or []
    for index, group in enumerate(groups):
        hit = [v for v in group if norm(v) in body]
        checks.append(check(f"answer.group_{index}", bool(hit), f"{group} 一个都没出现"))

    banned = rule.get("must_not_contain") or []
    if banned:
        bad = [v for v in banned if norm(v) in body]
        checks.append(check("answer.must_not_contain", not bad, f"出现禁用表述 {bad}"))
    return checks


def _fact_matches(expected: dict, fact: dict) -> bool:
    if not isinstance(fact, dict):
        return False
    if not host_allowed(host(fact.get("source_url", "")), expected.get("source_hosts", [])):
        return False
    if expected.get("value"):
        wanted = norm(expected["value"])
        actual = norm(fact.get("value", ""))
        if expected.get("match", "contains") == "exact":
            if wanted != actual:
                return False
        elif wanted not in actual:
            return False
    if expected.get("claim_contains"):
        claim = norm(fact.get("claim", ""))
        if not all(norm(keyword) in claim for keyword in expected["claim_contains"]):
            return False
    return True


def _fact_checks(case: dict, out: dict) -> list[dict]:
    expected_facts = case.get("expect", {}).get("facts") or []
    if not expected_facts:
        return []
    actual = out.get("facts")
    if not isinstance(actual, list):
        return [check("facts", False, "facts 必须是数组")]
    checks = []
    for index, expected in enumerate(expected_facts):
        ok = any(_fact_matches(expected, fact) for fact in actual)
        checks.append(check(f"facts.{index}", ok, f"没有匹配到 {expected}"))
    return checks


def _source_checks(case: dict, out: dict) -> list[dict]:
    rule = case.get("expect", {}).get("sources") or {}
    if not rule:
        return []
    sources = out.get("sources")
    if not isinstance(sources, list):
        return [check("sources", False, "sources 必须是数组")]
    urls = [item.get("url") for item in sources if isinstance(item, dict) and item.get("url")]
    unique = set(urls)
    checks = [check("sources.min", len(unique) >= rule.get("min", 0), f"{len(unique)} < {rule.get('min', 0)}")]
    primary_hosts = rule.get("primary_hosts") or []
    if primary_hosts:
        ok = any(host_allowed(host(url), primary_hosts) for url in unique)
        checks.append(check("sources.primary", ok, f"没有落在主源 {primary_hosts} 的 URL"))
    return checks


def grade_route(case: dict, out: dict) -> dict:
    if isinstance(out, dict) and not isinstance(out.get("route"), dict):
        out = {"route": out}
    checks = _route_checks(case, out, include_channels=False)
    passed = all(item["ok"] for item in checks if item["required"])
    return {
        "id": case["id"],
        "status": "PASS" if passed else "FAIL",
        "pass": passed,
        "checks": checks,
        "reasons": [item["detail"] for item in checks if not item["ok"]],
        "needs_human": False,
    }


def grade_case(case: dict, out, elapsed_ms: int = 0) -> dict:
    if out is None:
        return {"id": case["id"], "status": "PENDING", "pass": False, "checks": [], "reasons": ["没有回答文件"], "needs_human": False}
    if not isinstance(out, dict):
        return {"id": case["id"], "status": "FORMAT_FAIL", "pass": False, "checks": [], "reasons": ["输出不是 JSON 对象"], "needs_human": False}

    missing = [key for key in ("status", "answer", "route", "facts", "sources") if key not in out]
    if missing:
        return {"id": case["id"], "status": "FORMAT_FAIL", "pass": False, "checks": [], "reasons": [f"缺少字段 {missing}"], "needs_human": False}

    allowed = case.get("expect", {}).get("status_any") or ["answered"]
    status = out.get("status")
    status_check = check("status", status in allowed, f"{status!r} 不在 {allowed}")

    if status == "blocked" and "blocked" in allowed:
        passed = case.get("expect", {}).get("on_block", "fail") == "pass"
        return {
            "id": case["id"],
            "status": "BLOCKED",
            "pass": passed,
            "checks": [status_check],
            "reasons": [] if passed else ["用例要求可访问，但返回 blocked"],
            "needs_human": False,
            "elapsed_ms": elapsed_ms,
        }

    checks = [status_check]
    checks += _route_checks(case, out)
    checks += _answer_checks(case, out)
    checks += _fact_checks(case, out)
    checks += _source_checks(case, out)

    if case.get("expect", {}).get("notes_required"):
        checks.append(check("notes", bool(str(out.get("notes", "")).strip()), "notes 为空"))

    wall = case.get("budget", {}).get("max_wall_ms", 0)
    checks.append(check("budget.wall_ms", elapsed_ms <= wall or elapsed_ms == 0, f"{elapsed_ms}ms > {wall}ms", required=False))

    passed = all(item["ok"] for item in checks if item["required"])
    return {
        "id": case["id"],
        "status": "PASS" if passed else "FAIL",
        "pass": passed,
        "checks": checks,
        "reasons": [item["detail"] for item in checks if not item["ok"]],
        "needs_human": bool(case.get("expect", {}).get("needs_human")),
        "elapsed_ms": elapsed_ms,
    }


def selftest() -> tuple[int, list[str]]:
    case = {
        "id": "selftest-001",
        "domain": "general",
        "as_of": "2026-10-31",
        "stratum": {"knowledge": "public", "answer": "deterministic"},
        "grading": "deterministic",
        "expect": {
            "status_any": ["answered"],
            "route": {"domain_any": ["general"], "effort_any": ["quick"]},
            "answer": {"must_contain": ["42"]},
            "facts": [{"value": "42", "source_hosts": ["example.com"], "match": "contains"}],
            "sources": {"min": 1, "primary_hosts": ["example.com"]},
        },
        "budget": {"max_queries": 3, "max_wall_ms": 30000},
    }
    good = {
        "status": "answered",
        "answer": "答案是 42",
        "route": {"domain": "general", "effort": "quick", "channels": ["ddgs"], "queries": 1},
        "facts": [{"claim": "答案是 42", "value": "42", "source_url": "https://example.com/a"}],
        "sources": [{"url": "https://example.com/a", "title": "x", "primary": True}],
        "as_of": "2026-10-31",
        "confidence": "high",
        "notes": "",
    }
    failures = []

    def expect(label, result, status):
        if result["status"] != status:
            failures.append(f"{label}: 期望 {status}，得到 {result['status']} ({result['reasons']})")

    expect("good", grade_case(case, good), "PASS")

    wrong = dict(good, answer="答案是 41")
    expect("wrong answer", grade_case(case, wrong), "FAIL")

    expect("prose", grade_case(case, "答案是 42"), "FORMAT_FAIL")

    bad_route = dict(good, route={"domain": "legal", "effort": "quick", "channels": ["ddgs"], "queries": 1})
    expect("bad route", grade_case(case, bad_route), "FAIL")

    bad_source = dict(good, facts=[{"claim": "答案是 42", "value": "42", "source_url": "https://evil.example/b"}])
    expect("bad source", grade_case(case, bad_source), "FAIL")

    over_budget = dict(good, route={"domain": "general", "effort": "quick", "channels": ["ddgs"], "queries": 9})
    expect("budget", grade_case(case, over_budget), "FAIL")

    blocked_case = dict(case, expect=dict(case["expect"], status_any=["blocked"], on_block="pass"))
    expect("blocked", grade_case(blocked_case, dict(good, status="blocked")), "BLOCKED")

    flat_route = {"domain": "general", "effort": "quick", "channels": ["ddgs"], "queries": 1}
    expect("flat route", grade_route(case, flat_route), "PASS")

    date_case = dict(case, expect=dict(case["expect"], answer={"must_contain": ["2021-11-01"]}, facts=[]))
    date_out = dict(good, answer="2021 年 11 月 1 日", facts=[])
    expect("spaced date", grade_case(date_case, date_out), "PASS")

    return (9 - len(failures), failures)
