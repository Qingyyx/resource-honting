#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

EVAL = Path(__file__).resolve().parent
ROOT = EVAL.parents[1]
CASES = EVAL / "cases.json"
SUITE = EVAL / "suite.json"
REPORTS = EVAL / "reports"
RUNS = EVAL / "runs"
BASELINE = EVAL / "baseline.json"

sys.path.insert(0, str(EVAL))
import grade
import sut
import validate


def load() -> tuple[list[dict], dict]:
    return validate.load_cases(CASES), validate.load_suite(SUITE)


def offline() -> int:
    cases, suite = load()
    errors, warnings = validate.validate_cases(cases, suite)
    cell_counts = Counter((case["stratum"]["knowledge"], case["stratum"]["answer"]) for case in cases)
    domain_counts = Counter(case["domain"] for case in cases)
    tag_counts = Counter(tag for case in cases for tag in case.get("tags", []))

    print(f"[{'OK' if not errors else 'FAIL'}] cases {len(cases)}")
    print(f"[OK] cells {sum(1 for value in cell_counts.values() if value >= suite['min_per_cell'])}/{len(suite['cells'])} (min {suite['min_per_cell']})")
    print(f"[OK] domains {sum(1 for value in domain_counts.values() if value >= suite['min_per_domain'])}/{len(suite['domains'])} (min {suite['min_per_domain']})")
    print(f"[OK] tags smoke {tag_counts.get('smoke', 0)}, deep {tag_counts.get('deep', 0)}")
    print(f"[OK] seed {len(cases)}/{suite['seed_cases']}, target {len(cases)}/{suite['target_cases']}")
    for warning in warnings:
        print(f"[WARN] {warning}")
    for error in errors:
        print(f"[FAIL] {error}")
    return 0 if not errors else 1


def selftest() -> int:
    passed, failures = grade.selftest()
    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
    print(f"selftest {passed}/{passed + len(failures)}")
    return 0 if not failures else 1


def build_prompt(case: dict, route_only: bool) -> str:
    if route_only:
        return (
            "加载 resource-hunting skill，按它的 §1 领域划分与 §3 强度判定做路由判断。\n"
            "不要调用任何搜索工具，不要读取网页。\n"
            f"任务：{case['query']}\n"
            '只输出 JSON：{"domain":"...","effort":"...","channels":[],"queries":0}\n'
            "domain 必须取 skill 的九个领域之一；effort 取 quick/standard/deep。\n"
        )
    contract = (EVAL / "contract.md").read_text(encoding="utf-8")
    return (
        "你在执行 resource-hunting skill 的回归测试。请使用该 skill 完成下面的任务。\n\n"
        f"任务：{case['query']}\n"
        f"当前日期：{case['as_of']}\n"
        f"语言：{case['locale']}\n"
        f"检索预算：最多 {case['budget']['max_queries']} 次检索/抓取调用。\n\n"
        "先按 skill 正常检索与验证，最后只输出一个 JSON 对象，不要输出任何其他文字。\n\n"
        f"{contract}"
    )


def execute_once(case: dict, args, route_only: bool) -> dict:
    if date.today() > validate.parse_date(case["expires_at"]):
        return {"id": case["id"], "status": "STALE", "pass": False, "checks": [], "reasons": ["gold 已过期"], "needs_human": False}

    prompt = build_prompt(case, route_only)
    if args.dry_run:
        print(prompt)
        print("-" * 72)
        return {"id": case["id"], "status": "PENDING", "pass": False, "checks": [], "reasons": ["dry-run"], "needs_human": False}

    timeout = case["budget"]["max_wall_ms"] / 1000 + 120
    started = time.monotonic()
    try:
        output, meta = sut.run(prompt, case, args.sut, args.model, timeout, RUNS)
    except sut.SUTFormatError as exc:
        return {"id": case["id"], "status": "FORMAT_FAIL", "pass": False, "checks": [], "reasons": [str(exc)], "needs_human": False}
    except (sut.SUTError, ValueError) as exc:
        return {"id": case["id"], "status": "ERROR", "pass": False, "checks": [], "reasons": [str(exc)], "needs_human": False}

    elapsed = int((time.monotonic() - started) * 1000)
    if output is None:
        return {
            "id": case["id"],
            "status": "PENDING",
            "pass": False,
            "checks": [],
            "reasons": [f"等待回答: {meta.get('pending')}"],
            "needs_human": False,
        }

    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / f"{case['id']}.output.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    result = grade.grade_route(case, output) if route_only else grade.grade_case(case, output, elapsed)
    result["elapsed_ms"] = elapsed
    return result


def execute(case: dict, args, route_only: bool) -> dict:
    if not args.repeat:
        return execute_once(case, args, route_only)

    runs = [execute_once(case, args, route_only) for _ in range(case["repeat"]["runs"])]
    passes = sum(1 for result in runs if result["pass"])
    minimum = case["repeat"]["min_pass"]
    result = dict(runs[-1])
    result["repeat"] = {"runs": len(runs), "passes": passes, "min_pass": minimum, "ok": passes >= minimum}
    result["pass"] = passes >= minimum
    result["status"] = "PASS" if result["pass"] else "FAIL"
    if not result["pass"]:
        result["reasons"] = list(result.get("reasons", [])) + [f"repeat {passes}/{len(runs)} < {minimum}"]
    return result


def grouped(results: list[dict], cases: list[dict], key) -> dict:
    by_id = {case["id"]: case for case in cases}
    groups: dict[str, dict] = defaultdict(lambda: {"passed": 0, "total": 0})
    for result in results:
        if result["status"] not in {"PASS", "FAIL", "BLOCKED"}:
            continue
        name = key(by_id[result["id"]])
        groups[name]["total"] += 1
        if result["pass"]:
            groups[name]["passed"] += 1
    for value in groups.values():
        value["rate"] = value["passed"] / value["total"] if value["total"] else 0.0
    return dict(sorted(groups.items()))


def summarize(results: list[dict], cases: list[dict]) -> dict:
    counts = Counter(result["status"] for result in results)
    graded = [result for result in results if result["status"] in {"PASS", "FAIL", "BLOCKED", "FORMAT_FAIL"}]
    passed = sum(1 for result in graded if result["pass"])
    total = len(graded)
    low, high = grade.wilson(passed, total)
    return {
        "total": len(results),
        "graded": total,
        "passed": passed,
        "failed": sum(1 for result in graded if not result["pass"]),
        "pass_rate": passed / total if total else 0.0,
        "wilson": [low, high],
        "counts": dict(counts),
        "knowledge": grouped(results, cases, lambda case: case["stratum"]["knowledge"]),
        "answer_type": grouped(results, cases, lambda case: case["stratum"]["answer"]),
        "domain": grouped(results, cases, lambda case: case["domain"]),
        "cases": {result["id"]: result["status"] for result in results},
        "needs_human": [result["id"] for result in results if result.get("needs_human")],
    }


def write_report(mode: str, args, summary: dict, results: list[dict]) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": mode,
        "sut": getattr(args, "sut", "none"),
        **summary,
        "results": [{key: value for key, value in result.items() if key != "output"} for result in results],
    }
    json_path = REPORTS / f"report-{stamp}.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (REPORTS / "latest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# eval {mode} — {stamp}",
        "",
        f"- SUT: `{payload['sut']}`",
        f"- 通过: {summary['passed']}/{summary['graded']} ({summary['pass_rate'] * 100:.1f}%), 95% CI {summary['wilson'][0] * 100:.1f}–{summary['wilson'][1] * 100:.1f}%",
        f"- 状态: {summary['counts']}",
        f"- 需要人工: {', '.join(summary['needs_human']) or '无'}",
        "",
        "## 分层",
        "",
        "| 维度 | 分组 | 通过/总数 | 通过率 |",
        "|---|---|---:|---:|",
    ]
    for dimension in ("knowledge", "answer_type", "domain"):
        for name, value in summary[dimension].items():
            lines.append(f"| {dimension} | {name} | {value['passed']}/{value['total']} | {value['rate'] * 100:.1f}% |")
    lines += ["", "## 用例", "", "| 用例 | 状态 | 用时 | 原因 |", "|---|---|---:|---|"]
    for result in results:
        reason = "; ".join(result.get("reasons", []))[:160]
        elapsed = f"{result.get('elapsed_ms', 0) / 1000:.1f}s"
        lines.append(f"| {result['id']} | {result['status']} | {elapsed} | {reason} |")
    md_path = REPORTS / f"report-{stamp}.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (REPORTS / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path


def print_summary(summary: dict, md_path: Path) -> None:
    low, high = summary["wilson"]
    print("")
    print("Summary")
    print(f"  overall        {summary['passed']}/{summary['graded']}  {summary['pass_rate'] * 100:.1f}%  (95% CI {low * 100:.1f}–{high * 100:.1f}%)")
    for dimension in ("knowledge", "answer_type"):
        for name, value in summary[dimension].items():
            print(f"  {dimension:<14} {name:<14} {value['passed']}/{value['total']}  {value['rate'] * 100:.1f}%")
    print(f"  status         {summary['counts']}")
    if summary["needs_human"]:
        print(f"  needs_human    {', '.join(summary['needs_human'])}")
    print(f"  report         {md_path}")


def compare(summary: dict) -> list[str]:
    if not BASELINE.exists():
        return []
    old = json.loads(BASELINE.read_text(encoding="utf-8"))
    warnings = []
    delta = summary["pass_rate"] - old.get("pass_rate", 0.0)
    if delta < -0.05:
        warnings.append(f"整体通过率下降 {-delta * 100:.1f}pp")
    for case_id, status in summary["cases"].items():
        if old.get("cases", {}).get(case_id) == "PASS" and status in {"FAIL", "FORMAT_FAIL"}:
            warnings.append(f"{case_id}: PASS -> FAIL")
    return warnings


def save_baseline() -> int:
    latest = REPORTS / "latest.json"
    if not latest.exists():
        print("[FAIL] 没有 latest.json，先跑一次 eval")
        return 1
    data = json.loads(latest.read_text(encoding="utf-8"))
    payload = {
        "generated_at": data["generated_at"],
        "pass_rate": data["pass_rate"],
        "counts": data["counts"],
        "knowledge": data.get("knowledge", {}),
        "answer_type": data.get("answer_type", {}),
        "cases": data["cases"],
    }
    BASELINE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] baseline -> {BASELINE}")
    return 0


def run_suite(mode: str, cases: list[dict], all_cases: list[dict], args) -> int:
    route_only = mode == "route"
    results = []
    for index, case in enumerate(cases, 1):
        result = execute(case, args, route_only)
        results.append(result)
        elapsed = result.get("elapsed_ms", 0) / 1000
        print(f"[{index:>2}/{len(cases)}] {case['id']:<38} {result['status']:<11} {elapsed:>6.1f}s")

    if args.dry_run:
        return 0

    summary = summarize(results, all_cases)
    md_path = write_report(mode, args, summary, results)
    print_summary(summary, md_path)

    warnings = compare(summary)
    for warning in warnings:
        print(f"[WARN] {warning}")
    if args.strict and (summary["failed"] or warnings):
        return 1
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="eval")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("offline", "selftest", "route", "smoke", "core", "deep", "case", "baseline"):
        child = sub.add_parser(name)
        if name in {"route", "smoke", "core", "deep", "case"}:
            child.add_argument("--sut", choices=["opencode", "manual", "mock"], default=os.environ.get("EVAL_SUT", "opencode"))
            child.add_argument("--model", default=os.environ.get("EVAL_MODEL"))
            child.add_argument("--repeat", action="store_true")
            child.add_argument("--dry-run", action="store_true")
            child.add_argument("--limit", type=int, default=0)
            child.add_argument("--strict", action="store_true")
        if name == "case":
            child.add_argument("--id", required=True)

    args = parser.parse_args(argv)

    if args.command == "offline":
        return offline()
    if args.command == "selftest":
        return selftest()
    if args.command == "baseline":
        return save_baseline()

    cases, _suite = load()
    if args.command == "case":
        selected = [case for case in cases if case["id"] == args.id]
        if not selected:
            print(f"[FAIL] 找不到 case: {args.id}")
            return 1
    elif args.command == "smoke":
        selected = [case for case in cases if "smoke" in case.get("tags", [])]
    elif args.command == "deep":
        selected = [case for case in cases if "deep" in case.get("tags", [])]
    else:
        selected = cases

    if args.limit:
        selected = selected[: args.limit]
    if not selected:
        print("[FAIL] 没有匹配的 case")
        return 1
    return run_suite(args.command, selected, cases, args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
