from __future__ import annotations

import json
import re
import unicodedata
from datetime import date
from pathlib import Path

DOMAINS = {
    "academic",
    "engineering",
    "product",
    "business",
    "legal",
    "local",
    "media",
    "data",
    "general",
}
KNOWLEDGE = {"public", "professional", "niche"}
ANSWER_TYPES = {"deterministic", "multihop", "analysis", "negative"}
LOCALES = {"zh-CN", "en-US", "mixed"}
STATUSES = {"answered", "abstained", "blocked", "partial"}
GRADINGS = {"deterministic", "source_only", "rubric"}
CHANNELS = {"ddgs", "anysearch", "exa", "zhipu", "opencli", "direct-primary", "none"}
EFFORTS = {"quick", "standard", "deep"}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_json(path: Path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def load_cases(path: Path) -> list[dict]:
    data = load_json(path)
    if not isinstance(data, list):
        raise ValueError(f"{path} 顶层必须是数组")
    return data


def load_suite(path: Path) -> dict:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"{path} 顶层必须是对象")
    return data


def parse_date(value: str) -> date:
    if not isinstance(value, str) or not DATE_RE.match(value):
        raise ValueError(f"不是 YYYY-MM-DD: {value!r}")
    return date.fromisoformat(value)


def norm(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value)).lower()
    text = text.replace("％", "%").replace(",", "").replace("，", "")
    text = re.sub(r"(\d{4})年(\d{1,2})月(\d{1,2})日", lambda m: f"{m[1]}-{int(m[2]):02d}-{int(m[3]):02d}", text)
    text = re.sub(r"\s+", "", text)
    return text


def _as_list(value) -> list:
    return value if isinstance(value, list) else []


def validate_cases(cases: list[dict], suite: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    cells = {
        (cell.get("knowledge"), cell.get("answer"))
        for cell in _as_list(suite.get("cells"))
        if isinstance(cell, dict)
    }
    domain_list = _as_list(suite.get("domains")) or sorted(DOMAINS)
    min_per_cell = int(suite.get("min_per_cell", 1))
    min_per_domain = int(suite.get("min_per_domain", 1))
    seed_cases = int(suite.get("seed_cases", 0))
    target_cases = int(suite.get("target_cases", seed_cases))

    seen: set[str] = set()
    cell_counts: dict[tuple[str, str], int] = {}
    domain_counts: dict[str, int] = {}
    today = date.today()

    for index, case in enumerate(cases):
        where = f"case[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{where} 不是对象")
            continue

        case_id = case.get("id")
        if not isinstance(case_id, str) or not ID_RE.match(case_id):
            errors.append(f"{where} id 非法: {case_id!r}")
            continue
        where = case_id
        if case_id in seen:
            errors.append(f"{where} id 重复")
        seen.add(case_id)

        stratum = case.get("stratum")
        if not isinstance(stratum, dict):
            errors.append(f"{where} 缺少 stratum")
            stratum = {}
        knowledge = stratum.get("knowledge")
        answer = stratum.get("answer")
        if knowledge not in KNOWLEDGE:
            errors.append(f"{where} stratum.knowledge 非法: {knowledge!r}")
        if answer not in ANSWER_TYPES:
            errors.append(f"{where} stratum.answer 非法: {answer!r}")
        if knowledge in KNOWLEDGE and answer in ANSWER_TYPES:
            cell = (knowledge, answer)
            cell_counts[cell] = cell_counts.get(cell, 0) + 1
            if cells and cell not in cells:
                errors.append(f"{where} 不在 suite.cells 中: {cell}")

        domain = case.get("domain")
        if domain not in DOMAINS:
            errors.append(f"{where} domain 非法: {domain!r}")
        else:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if domain_list and domain not in domain_list:
            errors.append(f"{where} domain 不在 suite.domains 中: {domain!r}")

        if case.get("locale") not in LOCALES:
            errors.append(f"{where} locale 非法: {case.get('locale')!r}")
        query = case.get("query")
        if not isinstance(query, str) or len(query.strip()) < 6:
            errors.append(f"{where} query 缺失或过短")
        if case.get("grading") not in GRADINGS:
            errors.append(f"{where} grading 非法: {case.get('grading')!r}")

        for key in ("as_of", "verified_at", "expires_at"):
            try:
                parse_date(case.get(key))
            except (TypeError, ValueError) as exc:
                errors.append(f"{where} {key}: {exc}")
        try:
            as_of = parse_date(case.get("as_of"))
            verified = parse_date(case.get("verified_at"))
            expires = parse_date(case.get("expires_at"))
            if expires <= verified:
                errors.append(f"{where} expires_at 必须晚于 verified_at")
            if as_of > expires:
                errors.append(f"{where} as_of 晚于 expires_at（已过期）")
            if expires < today:
                warnings.append(f"{where} 已过期，运行时会标记 STALE")
        except (TypeError, ValueError):
            pass

        expect = case.get("expect")
        if not isinstance(expect, dict):
            errors.append(f"{where} 缺少 expect")
            continue

        status_any = expect.get("status_any", ["answered"])
        if not isinstance(status_any, list) or not status_any:
            errors.append(f"{where} expect.status_any 必须是非空数组")
        else:
            for status in status_any:
                if status not in STATUSES:
                    errors.append(f"{where} status 非法: {status!r}")
        if expect.get("on_block") not in (None, "pass", "fail"):
            errors.append(f"{where} on_block 只能是 pass/fail")

        route = expect.get("route")
        if not isinstance(route, dict):
            errors.append(f"{where} 缺少 expect.route")
        else:
            domain_any = route.get("domain_any")
            if not isinstance(domain_any, list) or not domain_any:
                errors.append(f"{where} route.domain_any 必须是非空数组")
            else:
                for item in domain_any:
                    if item not in DOMAINS:
                        errors.append(f"{where} route.domain_any 非法: {item!r}")
            effort_any = route.get("effort_any")
            if not isinstance(effort_any, list) or not effort_any:
                errors.append(f"{where} route.effort_any 必须是非空数组")
            else:
                for item in effort_any:
                    if item not in EFFORTS:
                        errors.append(f"{where} route.effort_any 非法: {item!r}")
            for key in ("channels_any", "channels_not"):
                values = route.get(key)
                if values is None:
                    continue
                if not isinstance(values, list):
                    errors.append(f"{where} route.{key} 必须是数组")
                    continue
                for item in values:
                    if item not in CHANNELS:
                        errors.append(f"{where} route.{key} 非法: {item!r}")

        text_rules = expect.get("answer", {})
        if text_rules and not isinstance(text_rules, dict):
            errors.append(f"{where} expect.answer 必须是对象")
        elif isinstance(text_rules, dict):
            for key in ("must_contain", "must_contain_any", "must_contain_all", "must_not_contain"):
                values = text_rules.get(key)
                if values is not None and not isinstance(values, list):
                    errors.append(f"{where} answer.{key} 必须是数组")
            groups = text_rules.get("must_contain_groups")
            if groups is not None:
                if not isinstance(groups, list) or not all(isinstance(g, list) and g for g in groups):
                    errors.append(f"{where} answer.must_contain_groups 必须是非空数组的数组")
            if not any(
                text_rules.get(key)
                for key in ("must_contain", "must_contain_any", "must_contain_all", "must_contain_groups")
            ) and not expect.get("facts") and not expect.get("sources"):
                errors.append(f"{where} 没有任何答案或来源断言")

        facts = expect.get("facts", [])
        if not isinstance(facts, list):
            errors.append(f"{where} expect.facts 必须是数组")
            facts = []
        for fact_index, fact in enumerate(facts):
            fwhere = f"{where}.facts[{fact_index}]"
            if not isinstance(fact, dict):
                errors.append(f"{fwhere} 不是对象")
                continue
            hosts = fact.get("source_hosts")
            if not isinstance(hosts, list) or not hosts:
                errors.append(f"{fwhere} 缺少 source_hosts")
            grading = case.get("grading")
            if grading == "source_only":
                if not fact.get("claim_contains"):
                    errors.append(f"{fwhere} source_only 需要 claim_contains")
            else:
                if not fact.get("value"):
                    errors.append(f"{fwhere} 需要 value")
            if fact.get("match") not in (None, "contains", "exact"):
                errors.append(f"{fwhere} match 只能是 contains/exact")

        sources = expect.get("sources")
        if sources is not None:
            if not isinstance(sources, dict):
                errors.append(f"{where} expect.sources 必须是对象")
            else:
                minimum = sources.get("min", 0)
                if not isinstance(minimum, int) or minimum < 0:
                    errors.append(f"{where} sources.min 必须是非负整数")
                primary = sources.get("primary_hosts", [])
                if not isinstance(primary, list):
                    errors.append(f"{where} sources.primary_hosts 必须是数组")

        budget = case.get("budget")
        if not isinstance(budget, dict):
            errors.append(f"{where} 缺少 budget")
        else:
            queries = budget.get("max_queries")
            if not isinstance(queries, int) or not (1 <= queries <= 20):
                errors.append(f"{where} budget.max_queries 必须是 1..20")
            wall = budget.get("max_wall_ms")
            if not isinstance(wall, int) or not (1000 <= wall <= 600000):
                errors.append(f"{where} budget.max_wall_ms 必须是 1000..600000")

        repeat = case.get("repeat")
        if not isinstance(repeat, dict):
            errors.append(f"{where} 缺少 repeat")
        else:
            runs = repeat.get("runs")
            min_pass = repeat.get("min_pass")
            if not isinstance(runs, int) or not (1 <= runs <= 5):
                errors.append(f"{where} repeat.runs 必须是 1..5")
            if not isinstance(min_pass, int) or not isinstance(runs, int) or not (1 <= min_pass <= runs):
                errors.append(f"{where} repeat.min_pass 必须是 1..runs")

        tags = case.get("tags")
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            errors.append(f"{where} tags 必须是字符串数组")

        raw = json.dumps(case, ensure_ascii=False)
        if "TODO" in raw or "FIXME" in raw:
            errors.append(f"{where} 含 TODO/FIXME")

        if case.get("grading") == "deterministic" and isinstance(query, str):
            for fact in facts:
                value = fact.get("value") if isinstance(fact, dict) else None
                if value and norm(value) and norm(value) in norm(query):
                    errors.append(f"{where} query 泄漏了 gold 值: {value!r}")

    for cell in sorted(cells):
        count = cell_counts.get(cell, 0)
        if count < min_per_cell:
            errors.append(f"格子 {cell[0]}/{cell[1]} 只有 {count} 条，至少 {min_per_cell} 条")

    for domain in sorted(domain_list):
        count = domain_counts.get(domain, 0)
        if count < min_per_domain:
            errors.append(f"领域 {domain} 只有 {count} 条，至少 {min_per_domain} 条")

    total = len(cases)
    if total < seed_cases:
        errors.append(f"用例总数 {total} 少于 seed_cases={seed_cases}")
    if total < target_cases:
        warnings.append(f"seed 阶段：{total}/{target_cases} 条")
    for domain in sorted(domain_list):
        count = domain_counts.get(domain, 0)
        if target_cases >= 72 and count < 6:
            warnings.append(f"领域 {domain} 只有 {count} 条，最终目标 ≥6")

    return errors, warnings
