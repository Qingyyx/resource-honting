# 搜索工具与方法参考

按缺口选择工具。来源优先顺序见 SKILL.md；资源覆盖方法见 [resource-discovery.md](resource-discovery.md)，专业入口见 [source-directory.md](source-directory.md)。

## 一、通道选择与降级

| 当前需求 | 先考虑 | 何时升级或切换 |
|---|---|---|
| 找官方/专业来源、通用网页 | AnySearch；已知 URL 则直接访问 | 空结果、结果重复、服务故障或领域覆盖不足时换可用搜索通道/垂直库 |
| 读取已知公开页面 | 现有网页读取、连接器、官方 API | 正文不完整时换正文提取；确实需要渲染时用浏览器 |
| 指定站点 | 站内搜索、域名限定、对应 API/连接器 | 通用索引遗漏、登录态或结构化结果有实际价值时用 OpenCLI |
| 腾讯新闻/企鹅号、知乎相关内容 | 已配置的智谱搜狗脚本，见 [zhipu-search.md](zhipu-search.md) | 域名不匹配、摘要不足或调用失败时换当前可用入口；原文与发布者仍须核验 |
| 编号、元数据、引用关系 | 对应专业库/API/CLI | 跨库补全、引文追踪或缺失字段 |
| 小众长尾、英文研究或语义相近资料 | 原名/编号 + 垂直源；当前搜索通道 | 可选 Exa 或其他语义检索通道，实际比较新增相关来源 |
| 文字稿与登录后内容 | 发布者提供的正文、字幕、show notes | 需要站点特有能力时用 OpenCLI 或浏览器，不假设任何视频都有文字稿 |
| 多维度系统研究 | 官方数据、学科库和专业机构 | AI 深度研究可辅助发现线索；结论仍逐条回溯原始证据 |

工具故障与资料缺失分开判断。AnySearch 不可用时，直接使用当前已提供且权限允许的搜索能力；没有替代工具则报告限制。普通只读替代检索不必重新询问许可。新服务的账号、凭据、付费调用与安装按实际授权处理。

不要把同一引擎不同包装当成索引互补；也不要推测 AnySearch 或其他服务未公开的底层索引。

## 二、AnySearch 的日常使用

使用本机已有配置；读取 anysearch skill 及其 `runtime.conf`，将其中命令替换下列 `<cmd>`。配置缺失或签名不确定时才查本地说明/帮助。

```bash
<cmd> search "关键词" --max_results 5
<cmd> search "site:目标域名 关键词" --max_results 5
<cmd> search "关键词" --content_types academic
<cmd> extract "https://目标页面"
```

- 首批数量按任务调整；通用检索、摘要与全文提取是不同能力，不保证搜索命中就能提取全文。
- `list_domains` 等域发现能力以当前实测为准；接口失效时普通检索或域名限定仍可尝试，不重复探测同一个已知故障。
- `extract` 不附加不存在的格式选项；参数错误先查子命令帮助。
- 并发、结果 URL 和正文质量根据当前返回判断；既往故障见 field-notes.md，不将历史观察当服务当前状态。

## 三、OpenCLI 按需补充

选择 OpenCLI 的理由应明确，例如通用搜索未收录的站内结果、已有登录态、结构化价格字段、文字稿或专有查询。

- 决定使用后加载 opencli-usage，按任务加载 smart-search 或 opencli-browser。
- 会话中首次使用时用 `opencli list -f yaml` 确认 live registry；签名不明查 `opencli <site> -h`，按支持情况加 `-f json`。
- 适配器存在、命令支持、服务可访问、已登录是四件不同的事，不靠静态清单推断。
- 可按需查 field-notes.md 的历史异常（如某站没有 search）；当前帮助与实际结果优先。
- 签名/适配器故障依 opencli-autofix 排查；如任务只需结果，可先换现有可用来源。登录或验证码阻塞不反复重试。

## 四、是否增加 GLM 等搜索 API

**当前配置：AnySearch 继续作为通用默认通道；腾讯新闻/企鹅号、知乎相关检索按需使用智谱 `search_pro_sogou`。** 脚本、凭据读取、参数与调用方式见 [zhipu-search.md](zhipu-search.md)。其他候选在出现明确缺口时再评估。

智谱独立搜索 API 已提供本地脚本与凭据配置；其他条目为文档层面的候选能力，未由本项目接入。各通道尚未完成效果对比。官方能力说明核查于 2026-10-25；价格、配额、引擎枚举和账号权益使用前查当前文档。

| 候选 | 官方公开的能力 | 值得评估的缺口 | 限制 / 入口 |
|---|---|---|---|
| 智谱 Web Search API | 已配置 `search_pro_sogou`，结构化标题/链接/摘要，域名与时间筛选 | 腾讯新闻/企鹅号、知乎相关内容按需检索 | 运行 `scripts/zhipu_search.py`；配置就绪与 API 实测成功分别判断。[官方说明](https://docs.bigmodel.cn/cn/guide/tools/web-search) |
| GLM Coding Plan 搜索 MCP | `webSearchPrime` 远程搜索工具，面向 Coding Plan 用户 | 已有对应套餐与可用权益时复用搜索能力 | 套餐 Key、独立 API Key、权限及额度分别核查，不推断可互换，[官方文档](https://docs.bigmodel.cn/cn/coding-plan/mcp/search-mcp-server) |
| Brave Search API | 官方说明使用自有独立索引，提供网页及新闻/图片/视频等搜索 | 增加不同索引路径，验证当前引擎遗漏 | 自有索引不保证对目标更好；用实际缺口比较，[官方文档](https://api-dashboard.search.brave.com/documentation) |
| Exa | 搜索与 Contents 接口，搜索可返回正文片段；支持搜索类型与过滤 | 语义查询、英文长尾、正文获取 | 与现有通道的相关结果增益需对比，[官方文档](https://exa.ai/docs/reference/search) |
| Tavily | Search/Extract 等接口，域名与时间过滤，可返回原始内容 | 把检索与正文获取组合用于研究 | 内容提取质量和增量覆盖需实测，[官方文档](https://docs.tavily.com/documentation/api-reference/endpoint/search) |

### 接入决策

1. **先写清缺口**：连接失败、中文长尾不足、站内未收录、正文取不到、时效不够各需不同措施。只是想多一个供应商，不足以证明需要接入。
2. **用代表性任务对比**：取实际遇到的约 10–20 个问题，覆盖不同资源形态、熟悉与陌生领域、不同语种/地区、原始内容获取、时敏目标和失败案例。各通道使用相同约束，允许合理语言变体。方法与指标见 [retrieval-evaluation.md](retrieval-evaluation.md)。
3. **看有效增益**：目标是否找到、是否新增相关原始域名、匹配版本的可用入口数、官方/专业源比例、链接和正文一致性、失败率、耗时、单次与月度成本。API 返回条数和 AI 摘要长度不等于召回质量。
4. **再接一个候选**：某候选持续解决具体缺口，且凭据、权限、成本可接受时才纳入调用；普通问题仍无需多通道齐跑。本文不设统一胜出阈值，按用户任务优先级判断。
5. **保留来源字段**：接入后至少保留标题、原始 URL、摘要/正文、提供方、查询词、获取时间和可得的发布时间；错误要区分网络、认证、限流与空结果，支持后续换路和去重。评分只用于该提供方内部排序。

优先复用已经连接的工具或官方接口，不为单次搜索引入新依赖。需要新凭据时使用环境变量或既有凭据存储，不写入 skill 文档或提交内容；未配置的候选不可假装调用成功。

## 五、高级搜索与研究工具

常用操作符：`"精确短语"`、`site:域名`、`-排除词`、`OR`、`filetype:pdf`、`intitle:词`、`inurl:词`。各引擎支持程度不同；参数和操作符未生效时检查结果域名/时间，不假设已过滤。

```text
site:stats.gov.cn 行业名 统计公报
site:开发者域名 "游戏原名" patch
"专辑目录号" soundtrack
"论文题目" filetype:pdf
```

精确匹配无结果时移除引号、换原名或编号，不一味叠加限制。深度资源检索的完整方法见 resource-discovery.md。

AI 研究产品按所需能力选择：跨站研究可用当前可访问的 Perplexity/ChatGPT Deep Research/Gemini Deep Research 等；文献问题可评估 Consensus/Elicit/scite，给定文档问答可用 NotebookLM。具体学术限制见 deep-research-sources.md。它们的可用性、语料、额度与运行时间不作静态保证。

AI 回答和生成引用均作为线索，回到原文核验；不要用一个固定“幻觉率”概括不同产品、版本与评测任务。
