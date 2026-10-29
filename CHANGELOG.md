# Changelog

## 2.1.0 — 2026-10-30

### Changed

- **`effort` 的语义从"查询次数"改为"覆盖维度"**：表格列改为 `覆盖维度` / `查询上限（防失控）`，并写明"先用完维度，再用完次数"。查询数是防止失控的上限，不是分配额度。
- **通道表新增"角色"列**：ddgs = 扫描，AnySearch = 取证，Exa = 溯源。三个通用通道索引几乎不重叠，是分工不是排序。

### Evidence

同一小众目标实测：8 次同义改写 → 22 个独立 URL；4 次换维度（英文术语 / 代码源 / 官方文档 / 实操踩坑）→ 23 个，交集仅 4。换维度单位产出约为同义改写的两倍。

跨通道对照（5 组查询 × 3 通道）：30 对结果中仅 2 条 URL 重复。同一法律问题 ddgs 命中搜狐攻略与知乎，Exa 命中省级疾控批复与条例原文；同一内核问题 ddgs 命中 DeepWiki 与 Reddit，Exa 命中内核 commit 与邮件列表原文。

## 2.0.0 — 2026-10-30

### Added

- **参数层**：`domain`（9 个领域 + auto）与 `effort`（quick/standard/deep + auto），支持用户显式指定，未指定时按信号自动判定。
- **`references/routing.md`**：8 个领域的专科检索策略——一手源、端点、检索顺序、常见坑。
- **预算表与四道停止门**：effort 决定通道数与查询上限；匹配门 / 覆盖门 / 回拨门 / 预算门。
- **经验台账结构化**：`field-notes.md` 改为 5 字段格式（日期｜通道｜领域｜观察｜判定）与 6 个判定枚举，并写明读/写时机。
- **`scripts/check.py`**：6 个结构门禁（frontmatter、章节、链接、引用索引、篇幅、台账格式）。
- `VERSION`、`CHANGELOG.md`、`AGENTS.md`、`Makefile`。

### Changed

- 默认通用检索通道改为 `ddgs`（多引擎扇出、去重、频次共识排序，不依赖浏览器）。
- OpenCLI 通道明确要求 `--site-session persistent --keep-tab true`，并记录其失效根因。
- SKILL.md 重组为 §0–§8 编号章节，加载表保留。

### Migration

旧调用方式无需改动：不写 `domain`/`effort` 时行为等同旧版的自动判断。想要确定行为时显式指定，例如 `domain=academic effort=deep`。

### Known gaps

- 四道停止门与预算表尚未在真实任务上校准，数值可能偏松或偏紧。
- `references/routing.md` 的端点可用性来自 2026-10 探测，未做定期复验。
