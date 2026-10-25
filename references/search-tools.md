# 搜索工具与方法参考

> 本文件收录搜索技巧、搜索工具和 AI 深度研究工具的用法参考。
> 来源：2026-08-14 网络调研 + opencli/anysearch 实际能力。

## 一、高级搜索操作符（Google/通用搜索引擎）

2026 年仍可靠的操作符（cache: 已于 2024 移除）：

| 操作符 | 作用 | 示例 |
|---|---|---|
| `"精确短语"` | 只搜完全匹配的短语 | `"kernel panic" "unable to mount root fs"` |
| `-词` | 排除词 | `jaguar -car` |
| `OR` | 任一匹配（需大写） | `docker OR podman` |
| `()` | 分组逻辑 | `(docker OR podman) (tutorial OR guide)` |
| `site:域名` | 限定站点搜索 | `site:v2ex.com 产品名` |
| `intitle:词` | 标题含词 | `intitle:"write for us"` |
| `inurl:词` | URL 含词 | `inurl:contribute` |
| `filetype:格式` | 限定文件类型 | `filetype:pdf` |
| `*` | 通配符 | `"best * in new york"` |
| `AROUND(n)` | 邻近度搜索 | `"zero trust" AROUND(5) networking` |

**组合示例**（SEO/深度研究常用）：
```
site:.edu intitle:"SEO" filetype:pdf
(intitle:"write for us" OR inurl:contribute) "目标关键词" -site:medium.com
```

**注意**：操作符行为可能随搜索引擎更新变化，关键场景先验证再依赖。

## 二、opencli 搜索补充技巧

- 各站点命令签名以 `opencli <site> -h` 实时输出为准，不要凭记忆硬编码
- 搜索前用 `opencli list -f yaml` 确认站点存在和 strategy
- 部分站点有垂直子命令（如 `opencli zhihu question`、`opencli reddit subreddit`），比通用 search 更精准
- 失败重试：报错/验证码/登录态问题计 1 次调用，不要无限重试；换用同类站点或 anysearch

## 三、AI 深度研究工具（何时用）

普通搜索是"秒级回答"，深度研究是"分钟级报告"（AI 自动跑多轮搜索、读数百页、交叉验证、产出带引用的报告）。适合重要、复杂、需要穷尽的研究任务。

| 工具 | 特点 | 最佳用途 |
|---|---|---|
| Perplexity | 快（2-4 分钟/报告），每条论断带引用 | 日常研究、实时数据 |
| ChatGPT Deep Research | 最长（30 分钟），报告结构最完整 | 需要深度长报告的复杂课题 |
| Gemini Deep Research | 异步长跑，Google 生态 | 长时研究流程 |
| Grok DeepSearch | 唯一能拉 X 实时数据 | 突发新闻、社交动态 |
| Consensus | **只用同行评议学术源** | 学术证据综合 |
| Elicit | 系统性论文分析 | 文献综述、结构化论文研究 |
| NotebookLM | 文档问答 | 基于你自己的文档做研究 |
| Brave Search / DuckDuckGo Assist | 免费 AI 搜索 | 隐私优先的日常搜索 |

> **本机关联**：opencli 已有 AI 站点适配（grok/doubao/gemini/kimi/qwen/chatgpt/claude/deepseek），如需 AI 问答可用 `opencli <site>` 直连。深度研究场景可作为 anysearch + opencli 的补充手段。

**注意**：AI 搜索/深度研究本身有幻觉率（2026 年调研：部分 AI 搜索幻觉率 67-94%），**其输出必须按 credibility-framework.md 的 SIFT 方法验证**，不能直接采信。

## 四、垂直/学术搜索增强

- **学术/深度调研**：学科专属库映射、引文滚雪球、研报/播客源库与深研工作流 → 见 `deep-research-sources.md`（本文件不重复收录）
- **代码**：GitHub 高级搜索（按语言/star数/更新时间筛选）、StackOverflow
- **图像来源验证**：TinEye、Google 反向图片搜索
- **专利/标准**：对应垂直库（anysearch 的垂直域支持 stock:/patent:/CVE: 等）
- **anysearch 学术类型**：`search "关键词" --content_types academic`（2026-10 实测可用）；`list_domains` 接口当时报服务端错误，垂直域子格式以实测为准

## 五、工具选择决策速查

| 场景 | 用哪个 |
|---|---|
| 快速找信息（默认） | anysearch 优先 |
| 已登录站点 | opencli <site> |
| 深度研究（重要课题） | Perplexity/ChatGPT Deep Research（或 opencli AI 站点） |
| 学术证据 | Consensus / Elicit / opencli 学科专属库 |
| 行业深度调研（系统报告级） | 按 deep-research-sources.md 分层取证，AI 深度研究仅作广度扫描 |
| 验证图片/媒体 | TinEye / MBFC / 腾讯朱雀检测 |
| 判断软文 | credibility-framework.md 五级分类 |
