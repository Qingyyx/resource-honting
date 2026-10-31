# Resource Hunting

> 先定领域和强度，再选源，最后判断证据。

一个给 AI agent 用的跨领域资源搜寻 skill。它不只负责"多搜几个 API"，而是把检索拆成两件事：**找到**（源覆盖 × 可达性 × 命中率）和**判断**（这条能不能信、放在一起说明什么）。只做前者，会把搜到的内容当结论。

适用于找资料、数据、软件、作品、素材、商品、服务和专业信息，也覆盖陌生领域、小众目标与深度调研；不用于本地代码、文件或系统配置调查。

## 它解决什么问题

| 问题 | 对应能力 |
|---|---|
| 该去哪找 | 9 个领域的一手源、端点、检索顺序与常见坑 |
| 不知道入口时怎么找 | 来源地图（角色 / 资源形态）+ 失败原因驱动的检索路线 |
| 搜到的东西能不能信 | 平台置信度分档 + 单条核验 + 多证据合成 |
| 什么时候停 | 匹配门 / 覆盖门 / 回拨门 / 预算门 |

## 核心设计

- **两个参数**：`domain`（`auto` / `academic` / `engineering` / `product` / `business` / `legal` / `local` / `media` / `data` / `general`）决定去哪找；`effort`（`auto` / `quick` / `standard` / `deep`）决定通道数、查询上限、是否交叉验证。
- **一手源优先**：有官方或专业入口时直接访问；通用搜索只用来定位入口。
- **通道分工**：默认 `ddgs` 铺面；AnySearch 取证；Exa 溯源；OpenCLI 处理登录态；智谱搜狗补腾讯新闻 / 企鹅号 / 知乎。
- **搜索 API 是通道，不是证据**：多一个 API 不等于多一个独立来源。
- **查不到时的写法**：写"在已覆盖的 X 范围未找到"，不写"不存在"。
- **台账写入需确认**：一次访问失败不会被推广成平台整体不可靠。

完整参数、路由表、预算与停止门见 [SKILL.md](SKILL.md)。

## 安装

仓库名是 `resource-honting`；克隆到本地时请把目录命名为 `resource-hunting`，与 `SKILL.md` 的 `name` 保持一致。

```bash
# opencode
git clone https://github.com/Qingyyx/resource-honting.git ~/.agents/skills/resource-hunting

# Claude Code
git clone https://github.com/Qingyyx/resource-honting.git ~/.claude/skills/resource-hunting
```

也可以把仓库放到任意 skills 目录，只要目录名是 `resource-hunting`。安装后重启会话，让运行时重新扫描 skills。

安装完 skill 后，还需要至少装一个搜索通道；见下一节。`scripts/` 只用 Python 3 标准库，回归测试需要 Python 3.11+。

## 依赖与搜索工具

本仓库只包含 skill 的提示词、参考文档和脚本，**不包含搜索服务本身**。至少装一个通用通道；其余按需，缺了会按降级规则换路。

| 工具 | 是否必需 | 用途 | 安装 / 配置 |
|---|---|---|---|
| `ddgs` | 必需（默认通道） | 通用检索、来源发现 | `pipx install ddgs`，验证 `ddgs version` |
| AnySearch | 推荐 | 正文提取、结构化 / 垂直检索 | 独立 skill：`git clone https://github.com/anysearch-ai/anysearch-skill.git ~/.agents/skills/anysearch`；API Key 可选 |
| Exa | 可选 | 语义检索、一手源溯源 | 按 [Exa 官方文档](https://exa.ai/docs/reference/search) 接入 MCP / API，需要 `EXA_API_KEY` |
| OpenCLI | 可选 | 登录态站内检索、结构化字段 | `npm install -g @jackwener/opencli`（Node >= 21）；登录态场景需 Chrome 扩展，`opencli doctor` 检查 |
| 智谱搜狗 | 可选 | 腾讯新闻 / 企鹅号、知乎 | 本仓库自带 `scripts/zhipu_search.py`；配置 `ZHIPU_API_KEY` 或 `ZHIPUAI_API_KEY` |

### 最小安装

```bash
# 1) 默认通用通道
pipx install ddgs
ddgs version

# 2) 正文 / 取证（可选，推荐）
git clone https://github.com/anysearch-ai/anysearch-skill.git ~/.agents/skills/anysearch
python3 ~/.agents/skills/anysearch/scripts/anysearch_cli.py doc

# 3) 登录态站内检索（可选）
npm install -g @jackwener/opencli
opencli doctor

# 4) 腾讯 / 知乎补充（可选）
export ZHIPU_API_KEY="..."
python3 <skill_dir>/scripts/zhipu_search.py "测试" --count 10
```

- `pipx` 安装后如果找不到命令，运行 `pipx ensurepath` 并重开 shell；没有 `pipx` 时用 `python3 -m pip install --user ddgs`。
- AnySearch 的 API Key 可选，匿名访问有较低限额；配置 `ANYSEARCH_API_KEY`，详见其 `README.md`。Python CLI 需要 `requests`；没有就用其 Node 或 Shell 版本。
- OpenCLI 的 `PUBLIC` 适配器不需要浏览器；`COOKIE` / `INTERCEPT` / `UI` 才需要 Chrome 登录态和扩展。
- 智谱通道没有 key 时跳过，不影响 `ddgs`；`<skill_dir>` 替换为实际安装目录（例如 `~/.agents/skills/resource-hunting`），脚本只读环境变量或技能目录 `.env`，不会打印密钥。
- Exa 不是必需项；没有配置时，skill 用 ddgs / AnySearch 继续，不会假装调用成功。

## 使用

自然语言触发即可，skill 会自动判定领域与强度：

```text
帮我快速查一下《中华人民共和国个人信息保护法》的施行日期
用 academic 深挖一下扩散模型在蛋白质结构预测中的进展
standard 强度对比这三款扫拖机器人，重点看硬地板和毛发
```

也可以显式指定参数：

```text
domain=legal effort=quick 查《个人信息保护法》施行日期
domain=product effort=standard 对比这三款扫拖机器人
```

日常输出是自然语言：结论、可点击出处、信心标注、未解决缺口，以及本次使用的通道和 domain/effort 判定。进入回归测试时，按 [tests/eval/contract.md](tests/eval/contract.md) 的 JSON 契约输出。

## 目录结构

```text
.
├── SKILL.md                  # 运行时入口：参数、路由、预算、停止门、汇报
├── references/               # 按需加载的检索与判断知识
│   ├── README.md             # 索引：找 / 判 / 记
│   ├── routing.md
│   ├── discovery.md
│   ├── search-tools.md
│   ├── deep-research-sources.md
│   ├── platform-trust.md
│   ├── credibility-framework.md
│   ├── evidence-synthesis.md
│   └── field-notes.md
├── scripts/
│   ├── check.py              # 7 个结构门禁
│   └── zhipu_search.py       # 智谱搜狗通道
├── tests/
│   ├── test_zhipu_search.py
│   └── eval/                 # 分层回归测试
├── AGENTS.md                 # 维护规则与命令
├── CHANGELOG.md
├── VERSION
└── Makefile
```

## 参考文档

按任务取用，不要全读。索引与常用组合见 [references/README.md](references/README.md)。

| 文档 | 作用 |
|---|---|
| [routing.md](references/routing.md) | 9 个领域的一手源、端点、检索顺序与常见坑 |
| [discovery.md](references/discovery.md) | 来源地图（角色 / 资源形态）+ 陌生领域、空结果、身份不明的检索路线 |
| [search-tools.md](references/search-tools.md) | 通道选择与降级、AnySearch / OpenCLI / 智谱搜狗、操作符、AI 研究工具 |
| [deep-research-sources.md](references/deep-research-sources.md) | 深度调研的分层取证（L1–L4）、学科库、研报、播客与工作流 |
| [platform-trust.md](references/platform-trust.md) | 平台 / 来源置信度分档、领域 × 平台速查、购买前查证 |
| [credibility-framework.md](references/credibility-framework.md) | 单条信息核验：SIFT、五支柱、CRAAP、身份声称、软文与 AI 内容检测 |
| [evidence-synthesis.md](references/evidence-synthesis.md) | 多证据合成：断言分解、竞争假设、独立性、信心与可能性分轴 |
| [field-notes.md](references/field-notes.md) | 跨任务实测台账：通道 / 站点可用性、反爬、软文噪声 |

## 回归测试

`make check` 不联网、秒级；`eval-*` 需要模型或网络，单独运行。

| 命令 | 作用 |
|---|---|
| `make check` | 7 个结构门禁：frontmatter、章节、链接、索引、预算、台账格式、用例 |
| `make eval-offline` | 校验 24 条用例、12 格覆盖、gold 有效期，不调模型 |
| `make eval-selftest` | 验证判分器本身（9 个断言） |
| `make eval-route` | 只判 domain / effort / channel |
| `make eval-smoke` | 14 条真实联网冒烟 |
| `make eval-core` | 24 条 × 3 次，按 min-pass 判定 |
| `make eval-deep` | 6 条 × 3 次，配合 rubrics 人工评审 |

当前是 24 条种子集，目标 72 条；通过率只用于抓大回归，不能给模型排名，也不能对单格下结论。用例、判分与基线见 [tests/eval/README.md](tests/eval/README.md)，方法与指标见 [tests/eval/methodology.md](tests/eval/methodology.md)。

## 维护

- 改 `SKILL.md`、`references/` 或用例后先跑 `make check`。
- 维护规则、命令与唯一事实源见 [AGENTS.md](AGENTS.md)。
- 台账条目按 5 段格式追加，判定只取固定枚举；写入前需用户确认。
- 版本变更记录见 [CHANGELOG.md](CHANGELOG.md)，当前版本见 [VERSION](VERSION)。

## 说明

这是一个 prompt 型 skill：`SKILL.md` 是运行时入口，`references/` 是按需加载的参考资料，`tests/eval/` 是可重复运行的分层回归测试。它不包含模型权重，也不绑定某个搜索供应商；通道不可用时按降级规则换路，而不是假设某个 API 永远可用。
