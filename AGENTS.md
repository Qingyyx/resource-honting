# AGENTS.md

本仓库把 skill 提示词当生产代码维护。运行时入口是 [SKILL.md](SKILL.md)，唯一事实源如下。

## 命令

| 命令 | 作用 |
|---|---|
| `make check` | 跑全部 7 个结构门禁（`python3 scripts/check.py`），改完必跑 |
| `make list` | 列出 gate 与说明 |
| `make eval-offline` | 校验分层回归用例库（不调模型、不联网） |
| `make eval-selftest` | 验证判分器本身（9 个断言） |
| `make eval-route` / `eval-smoke` / `eval-core` / `eval-deep` | 分层回归，需要 opencode 或网络 |
| `make eval-case ID=<case>` | 跑单条用例 |
| `make eval-baseline` | 认可当前报告为基线 |
| `python3 scripts/zhipu_search.py "关键词"` | 智谱搜狗通道的冒烟验证 |

## 唯一事实源

| 事实 | 家 |
|---|---|
| 参数语义、路由表、预算、停止门、输出要求 | [SKILL.md](SKILL.md) |
| 参考文档索引（找 / 判 / 记） | [references/README.md](references/README.md) |
| 各领域的一手源、端点、检索顺序、坑 | [references/routing.md](references/routing.md) |
| 通道与站点的实测结论（可复用） | [references/field-notes.md](references/field-notes.md) |
| 分层回归测试的用例、契约与运行方式 | [tests/eval/README.md](tests/eval/README.md) |
| 版本与变更 | [VERSION](VERSION)、[CHANGELOG.md](CHANGELOG.md) |

同一事实只写一处，其他位置只链接。

## 硬规则

1. 改 `domain` / `effort` 的语义、章节编号或停止门，必须同步改 `scripts/check.py` 的 `REQUIRED_SECTIONS`，否则 `make check` 会拦下。
2. 新增或改名 `references/*.md` 必须同步 SKILL.md 加载表与 `references/README.md` 索引，否则 `reference-index` gate 失败。
3. `field-notes.md` 的新条目只能是 5 段，判定值只能取 6 个枚举之一。
4. SKILL.md 不超过 260 行；超了先压缩，不要先扩预算。
5. 台账写入需用户确认，一次失败不得推广成平台整体不可靠。
6. 版本号：只在用户明确要求时升 major，其余变更升 minor/patch。
7. **每次修改后必须提交**：`make check` 通过即 `git add -A && git commit`，不等用户催。提交信息用 `<type>: <摘要>`，type 取 `feat` / `fix` / `docs` / `chore`。一次改动涉及 2 个以上不相关主题时拆成多个提交；单个提交只做一件事。
8. 不许为了通过检查而绕过 gate（改 `check.py` 放宽条件、删章节、删测试）。先修内容，再跑检查。
