#!/usr/bin/env python3
"""resource-hunting 结构门禁。

用法:
    python3 scripts/check.py          # 跑全部 gate
    python3 scripts/check.py --list   # 列出 gate

退出码: 0 = 全部通过, 1 = 有失败项。
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"
REFS = ROOT / "references"
FIELD_NOTES = REFS / "field-notes.md"

VERDICTS = {"可用", "部分可用", "不可用", "需登录", "高噪声", "仅线索"}

REQUIRED_SECTIONS = frozenset({
    "## 0｜参数",
    "## 1｜领域判定",
    "## 2｜领域路由",
    "## 3｜强度与预算",
    "## 4｜通道选择",
    "## 5｜执行流程",
    "## 6｜验证与汇报",
    "## 7｜经验回填",
    "## 8｜常见误区",
    "## 按需加载",
})

MAX_SKILL_LINES = 260


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end]


def gate_frontmatter() -> list[str]:
    errs: list[str] = []
    text = read(SKILL)
    fm = frontmatter(text)
    if fm is None:
        return ["SKILL.md 缺少 frontmatter"]
    for key in ("name:", "description:", "metadata:", "allowed-tools:"):
        if key not in fm:
            errs.append(f"frontmatter 缺少 {key}")
    m = re.search(r"version:\s*(\S+)", fm)
    if not m:
        errs.append("frontmatter 缺少 metadata.version")
    elif not re.fullmatch(r"\d+\.\d+\.\d+", m.group(1)):
        errs.append(f"version 不是 semver: {m.group(1)}")
    return errs


def gate_sections() -> list[str]:
    text = read(SKILL)
    return [f"缺少章节: {s}" for s in REQUIRED_SECTIONS if s not in text]


def gate_links() -> list[str]:
    errs: list[str] = []
    paths = [SKILL, ROOT / "AGENTS.md", *sorted(REFS.glob("*.md"))]
    for path in paths:
        text = read(path)
        for target in re.findall(r"\]\(([^)#]+?\.md)(?:#[^)]*)?\)", text):
            if target.startswith(("http://", "https://")):
                continue
            if not (path.parent / target).resolve().exists():
                errs.append(f"{path.relative_to(ROOT)} 引用了不存在的文件: {target}")
    return errs


def gate_all_references_listed() -> list[str]:
    text = read(SKILL)
    index_path = REFS / "README.md"
    index = read(index_path) if index_path.exists() else ""
    errs: list[str] = []
    if "references/README.md" not in text:
        errs.append("未被 SKILL.md 加载表引用: references/README.md")
    for path in sorted(REFS.glob("*.md")):
        if path.name == "README.md":
            continue
        if f"references/{path.name}" not in text:
            errs.append(f"未被 SKILL.md 加载表引用: references/{path.name}")
        if f"]({path.name})" not in index:
            errs.append(f"references/README.md 索引未链接: {path.name}")
    return errs


def gate_budget() -> list[str]:
    n = len(read(SKILL).splitlines())
    if n > MAX_SKILL_LINES:
        return [f"SKILL.md {n} 行，超过预算 {MAX_SKILL_LINES}"]
    return []


def gate_eval_cases() -> list[str]:
    validate_path = ROOT / "tests" / "eval" / "validate.py"
    cases_path = ROOT / "tests" / "eval" / "cases.json"
    suite_path = ROOT / "tests" / "eval" / "suite.json"
    for path in (validate_path, cases_path, suite_path):
        if not path.exists():
            return [f"缺少 {path.relative_to(ROOT)}"]
    spec = importlib.util.spec_from_file_location("eval_validate", validate_path)
    if spec is None or spec.loader is None:
        return ["无法加载 tests/eval/validate.py"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors, _ = module.validate_cases(module.load_cases(cases_path), module.load_suite(suite_path))
    return errors


def gate_field_notes_lines() -> list[str]:
    errs: list[str] = []
    for lineno, line in enumerate(read(FIELD_NOTES).splitlines(), 1):
        if not re.match(r"^- \d{4}-\d{2}-\d{2} \|", line):
            continue
        parts = [p.strip() for p in line[2:].split("|")]
        if len(parts) != 5:
            errs.append(f"field-notes.md:{lineno} 字段数 {len(parts)}，应为 5")
            continue
        if parts[-1] not in VERDICTS:
            errs.append(f"field-notes.md:{lineno} 判定值非法: {parts[-1]}")
    return errs


GATES = {
    "frontmatter": gate_frontmatter,
    "sections": gate_sections,
    "links": gate_links,
    "reference-index": gate_all_references_listed,
    "budget": gate_budget,
    "field-notes-format": gate_field_notes_lines,
    "eval-cases": gate_eval_cases,
}

GATE_DESC = {
    "frontmatter": "frontmatter 必备字段与 semver",
    "sections": "SKILL.md 章节锚点完整",
    "links": "SKILL/AGENTS/references 的相对 .md 链接可达",
    "reference-index": "references 每个文件都被 SKILL 加载表与索引覆盖",
    "budget": f"SKILL.md 不超过 {MAX_SKILL_LINES} 行",
    "field-notes-format": "field-notes 新条目 5 段且判定合法",
    "eval-cases": "分层回归用例的字段、覆盖与 gold 有效期",
}


def main(argv: list[str]) -> int:
    if "--list" in argv:
        for name, desc in GATE_DESC.items():
            print(f"{name:16} {desc}")
        return 0

    failed = 0
    for name, fn in GATES.items():
        errs = fn()
        if errs:
            failed += 1
            print(f"[FAIL] {name}")
            for e in errs:
                print(f"       - {e}")
        else:
            print(f"[ OK ] {name}")

    print(f"\n{len(GATES) - failed}/{len(GATES)} gates passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
