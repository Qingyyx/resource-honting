# 分层搜索回归测试

这套测试检查 `resource-hunting` 的检索行为，不代替 `make check` 的结构门禁。`make check` 仍然不联网、秒级；`eval-*` 需要模型或网络，单独运行。

## 为什么分两层

`SKILL.md` 是 prompt，不是可调用的函数。测试必须分两段：

- **静态契约**：不调用模型、不联网，校验用例库、覆盖率和 gold 有效期。
- **真实执行**：调用 agent，让它加载 skill，按 `contract.md` 输出 JSON，再按 gold 判分。

把两者混在一起，会得到“网络抖动就关 CI”或“缓存把模型退化永久掩盖”的流水线。

## 目录

```text
tests/eval/
  cases.json          # 24 条种子用例，12 格 × 2
  suite.json          # 覆盖目标：target 72，seed 24
  contract.md         # 被测系统的输出契约
  validate.py         # 用例校验，标准库
  grade.py            # 判分与 selftest
  sut.py              # opencode / manual / mock 三种执行方式
  run.py              # CLI
  rubrics/            # 分析型用例的人工评分卡
  reports/            # 运行报告，gitignore
  runs/               # 原始输出与 manual 提示，gitignore
  baseline.json       # 上一次认可的基线，提交进仓库
```

## 快速开始

```bash
make check            # 结构门禁，不联网
make eval-offline     # 校验用例库，不需要模型
make eval-selftest    # 验证判分器本身
make eval-route       # 24 条路由判断，模型调用，禁止检索
make eval-smoke       # 14 条真实联网冒烟
make eval-core        # 24 条完整回归
```

单条调试：

```bash
make eval-case ID=pub-legal-pipl-date
```

`make eval-core` / `eval-deep` 默认带 `--repeat`，按用例的 `repeat.runs` / `min_pass` 判定；`run.py` 直接调用时默认只跑一次。

## 五层

| 层 | 命令 | 调模型 | 联网 | 规模 | 用途 |
|---|---|---|---|---|---|
| L0 静态契约 | `make eval-offline` | 否 | 否 | 全部 | 每次改用例或 skill 结构后必跑 |
| L0.5 判分自检 | `make eval-selftest` | 否 | 否 | 9 个断言 | 改 `grade.py` 后必跑 |
| L1 路由 | `make eval-route` | 是 | 否 | 全部 | 只判 domain/effort/channel |
| L2 冒烟 | `make eval-smoke` | 是 | 是 | 14 条 | 每日或发版前 |
| L3 核心 | `make eval-core` | 是 | 是 | 24 条 × 3 次 | 每周或改检索策略后，按 min-pass 判定 |
| L4 深研 | `make eval-deep` | 是 | 是 | 6 条 × 3 次 | 每月，配合 rubrics 人工评审 |

## 输出契约

被测系统必须只输出一个 JSON 对象，字段见 [contract.md](contract.md)。判分器按字段判，不解析自然语言：

- `status` 决定 answered / abstained / blocked。
- `route` 判领域、强度、通道、查询次数。
- `facts[].value` + `source_url` 判关键值与来源域名。
- `sources` 判来源数量与是否落在一手源。
- `answer` 只做 must / must-not 的确定性断言。

这样同一个回答既能判对错，也能判“引用是否来自主源”，不需要一个全能 judge。

## 用例字段

```json
{
  "id": "pub-legal-pipl-date",
  "stratum": {"knowledge": "public", "answer": "deterministic"},
  "domain": "legal",
  "locale": "zh-CN",
  "query": "《中华人民共和国个人信息保护法》自哪一天起施行？",
  "as_of": "2026-10-31",
  "verified_at": "2026-10-31",
  "expires_at": "2027-10-31",
  "grading": "deterministic",
  "expect": {
    "status_any": ["answered"],
    "route": {"domain_any": ["legal"], "effort_any": ["quick", "standard"]},
    "answer": {"must_contain": ["2021-11-01"]},
    "facts": [{"value": "2021-11-01", "source_hosts": ["flk.npc.gov.cn"], "match": "contains"}],
    "sources": {"min": 1, "primary_hosts": ["flk.npc.gov.cn", "npc.gov.cn"]}
  },
  "budget": {"max_queries": 3, "max_wall_ms": 30000},
  "repeat": {"runs": 3, "min_pass": 2},
  "tags": ["smoke", "legal"]
}
```

`grading` 三种：

- `deterministic`：关键值 + 来源域名，最严格。
- `source_only`：只要求事实出现在允许的主源上，不锁死数值；适合年报、地方政策等会变的数字。
- `rubric`：确定性断言 + 来源数量，质量由 `rubrics/` 人工评审；报告会标 `needs_human`。

## Gold 规则

- 每条 gold 必须有 `source_hosts`；`deterministic` 还要有 `value`。
- `verified_at` 是作者核验日期，`expires_at` 到期后运行时标记 `STALE`，不判失败。
- 用例的 `query` 不得出现 gold 值；`eval-offline` 会拦。
- 公开基准的问答页可能被搜索引擎收录，不要直接抄 SimpleQA/BrowseComp 原题；用私有题并定期轮换。
- 24 条种子用例的 gold 在 authoring 时填写；首次 live 运行后应抽样复核，尤其是 `source_only` 的数字。

## 运行方式

```bash
# 默认：调用本机 opencode
make eval-core

# 指定模型
EVAL_MODEL=provider/model make eval-core

# 不调模型，只打印 prompt
python3 tests/eval/run.py core --dry-run --limit 2

# 人工模式：生成 prompt，填 runs/<id>.answer.json 后再判分
python3 tests/eval/run.py case --id pub-legal-pipl-date --sut manual
```

`opencode` 模式会在 `/tmp` 下建临时工作目录，避免加载本仓库的 `AGENTS.md`。skill 本身在 `~/.agents/skills/` 全局可见。

## 报告与基线

每次运行写 `reports/report-<timestamp>.json|md` 和 `reports/latest.*`。报告包含：

- 总通过率与 Wilson 95% 区间
- 按 knowledge / answer_type / domain 分层
- 每条的 status、耗时、失败原因
- `needs_human` 列表

认可当前结果后：

```bash
make eval-baseline
```

之后 `eval-core` 会和 `baseline.json` 比；整体下降超过 5pp 或某条 PASS→FAIL 会打印警告，`--strict` 时退出码 1。

## 统计限制

24 条、通过率 0.8 时，95% 区间约 ±15pp；整体扩到 72 条约 ±9–12pp。**这套测试只能抓大回归，不能给模型排名，也不能对单格下结论。** 需要更细的结论时，增加重复次数或用配对比较，不要靠加总样本。

## 已知限制

- `route.queries` 由被测系统自报；当前没有从工具轨迹独立计数，预算断言是契约约束，不是硬监控。
- `opencode` 模式是黑盒调用，无法回放搜索响应；L1–L3 是真实执行，不做 cassette 回放。要回放，需要把工具层收进 runner。
- 分析型用例只做确定性断言 + 人工评分卡，尚未接入 LLM judge。
- 24 条种子集的 gold 需要首次 live 运行后抽样复核，尤其是 `source_only` 的数字。

## 依赖

- `make eval-offline` / `eval-selftest`：Python 3.11+，标准库。
- `eval-route` / `eval-core`：`opencode` 已配置模型；`eval-core` 另需 `ddgs`、AnySearch，走智谱通道时需 `ZHIPU_API_KEY`。
- 不新增 Python 包依赖，避免污染 `make check`。
