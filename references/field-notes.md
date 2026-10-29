# 检索经验台账

> **用途**：跨任务沉淀通道与站点的可复用观察。选路前读，任务后写。
>
> **读时机**：SKILL.md §2 定领域、§4 选通道之前，查本文件中该 `domain` 与该通道的近期记录。标 `不可用 / 需登录 / 高噪声` 的，直接换路，不重复试错。
>
> **写时机**：任务结束出现新的、可复用的观察时。**不自动追加**——先在汇报里提出，经用户确认后落盘。一次访问失败不得推广成平台整体不可靠。
>
> **格式**：`- YYYY-MM-DD | 通道/站点 | 领域 | 观察 | 判定`
>
> **判定枚举**：`可用` / `部分可用` / `不可用` / `需登录` / `高噪声` / `仅线索`
>
> 早期条目缺日期或判定字段的，用 `—` 占位，按原文保留，不改写事实。

## 通用通道

- 2026-10-29 | ddgs | general | 7 引擎扇出 + 去重 + 频次共识排序，不碰浏览器。中英查询实测均 5–6 条高质量结果。`-o` 是输出文件名不是格式；`bing`/`google` 后端在本机禁用，实际可用 brave、duckduckgo、grokipedia、mojeek、startpage、wikipedia、yahoo | 可用
- 2026-08-14 | anysearch | general | 通用/中文搜索质量好，能直接抓知乎长文、官方 FAQ、行业研报；extract 对 gov 站点与官方文档干净，对部分商业站（雪球等）返回噪声或 WAF 混淆 | 可用
- 2026-09-08 | anysearch | general | API endpoint 多次出现 Connection Error / SSL_ERROR_SYSCALL（匿名限流）；`batch_search` 上限 5 且不可靠，串行单查询基本稳定，失败后 sleep 3–8s 重试；曾整段时间不可用，需回退 exa + webfetch | 部分可用
- 2026-09-11 | anysearch | general | 存在 URL 字段噪声（标题与链接错配）；核验以标题 + 独立来源为准，不可只信返回 URL | 部分可用
- 2026-10-19 | anysearch | academic | `list_domains` 报服务端 `tool 'list_domains' not found`（单域/批量均失败）；`--content_types academic` 只是网页类型过滤，不等于垂直库检索 | 部分可用
- 2026-10-29 | anysearch | academic | `--domain academic --sub_domain academic.paper` 走 OpenAlex + Crossref，返回 DOI、authors、citation_count、citation_doi、journal，可做引文滚雪球。`list_domains` 仍不可用，`academic.search`/`legal.case`/`ip.patent` 均为 Invalid tag，tag 表只能试 | 可用
- 2026-08-17 | exa websearch | general | 对英文/niche 主题语义召回好，可直达 Reddit 原生帖；但 MCP 频繁 timeout、socket 故障，批量并发易失败，单发较稳 | 部分可用
- 2026-09-08 | opencli google/duckduckgo | general | 曾判定为不稳定（google 返 NOT_FOUND 疑似 CAPTCHA、duckduckgo 超时/空）；2026-10-29 复测确认真实根因是浏览器无可用普通 tab，与反爬无关 | 部分可用
- 2026-10-29 | opencli google | general | 加 `--site-session persistent --keep-tab true` 后 6/6 成功（0.8–4.8s）；默认 ephemeral 时 0/5，报 "Navigation rejected"，实为 `Cannot access a chrome:// URL`。前置条件：Chrome 在运行且扩展已连接（`opencli doctor`） | 可用
- 2026-08-20 | zhipu search_pro_sogou | general | 腾讯新闻/企鹅号与知乎覆盖是其他通道拿不到的；索引偏旧，公众号非全量收录 | 可用

## 垂直源与 API

- 2026-10-29 | OpenAlex / Crossref / DataCite / PatentsView | academic, data, legal | 无凭据 HTTP 探测全部 200 可达，免费额度接近无限（OpenAlex 约每日 10 万次）。学术、数据集、专利三类不必消耗 AnySearch 配额 | 可用
- `site:sspai.com 关键词` | 中文测评 | 返回少数派专业测评（实测流程 + 数据），软文隔离效果好 | 可用
- `site:reddit.com` / `site:v2ex.com` | general | reddit 能拿真实使用经验（含关键坑）；v2ex 对技术/购物话题有效，对极小众硬件（如 nRF52840）几乎无内容 | 仅线索
- 英文测评 | product | exa 可一站式获取 Wirecutter / Consumer Reports / Serious Eats / Good Housekeeping 等权威横评；注意区分佣金链接媒体与会员制独立评测；英文源基本不覆盖国产品牌 | 可用
- 中文一手证据 | academic | 国内期刊（如《食品安全质量检测学报》）的一手研究可经 exa/anysearch 检索到，属高置信中文证据 | 可用
- 官方一手源 | engineering | 厂商官网 FAQ / 官方 wiki / 官方分销商（Mouser/DigiKey）是最可靠规格与价格源；NGC 网页（catalog.ngc.nvidia.com）可无登录抓全部 tag，驱动要求以官方 gitlab Dockerfile 的 NVIDIA_REQUIRE_CUDA 最准 | 可用
- GitHub 数据 | engineering | `gh` CLI / GitHub API 为最高置信一手数据（版本/star/license/活跃度）；`gh search repos` 对 niche/口语短语召回差，可改用 API forks 列表 + raw 文件哈希比对 | 可用

## 站内（OpenCLI）

- opencli zhihu | academic, general | 搜索正常，命中高赞长文/回答；`answer-detail <id>` 取回答全文、`download --url` 导出专栏 Markdown；曾报 AUTH_REQUIRED（Chrome 登录态临时失效），复测恢复 | 需登录
- opencli 36kr | business | **hot 子命令已失效（NO_DATA，DOM 变更）**；资讯用 `news`、搜索用 `search` | 部分可用
- opencli v2ex | engineering | **无 search 子命令**（只有 daily/hot/latest/node/topic）；搜历史讨论用 anysearch `site:v2ex.com`，逛购物节点用 `opencli v2ex node shopping` | 部分可用
- opencli github | engineering | 适配器仅支持 login/whoami，**无 search**；GitHub 搜索用本机 `gh` CLI 或 anysearch `site:github.com` | 不可用
- opencli jd | product | 价格数据可靠，但结果含"广告"前缀占位与大量无店铺名条目，偶有价格解析异常（如 ¥1983000）；多次会话返回空/失败；可信卖家识别困难 | 部分可用
- opencli taobao | product | search/detail 正常，detail 可核验特定商品实时价；"原装正品"声明普遍，真假需靠官方渠道判断 | 部分可用
- opencli smzdm | product | 搜索正常（首次偶无输出，重试成功） | 可用
- opencli xianyu | product | 未登录会话直接 AUTH_REQUIRED，二手比价需先登录 Chrome goofish.com | 需登录
- opencli bilibili | media, product | 搜索正常，测评/实操视频密度高且带播放量可排序；"绝不恰饭"类自证标题仍需甄别 | 可用
- opencli weixin（搜狗） | media, general | 搜索正常，能命中大量公众号文；微信功能类话题有多篇互证，但时效偏旧 | 可用
- opencli xiaohongshu | product, business | 对抽象商业概念（返佣/达人补贴等）搜索匹配差；种草内容软文多 | 高噪声
- opencli bbc | media | 正常，国际新闻可直取 | 可用
- opencli reddit | general | 多次报 "Failed to fetch" / URL 解析错误，不稳定；Reddit 内容可改用 exa 直达 | 部分可用
- opencli tieba | general | 报 EMPTY_RESULT（疑似 DOM 变更/封锁） | 不可用
- opencli linux-do | engineering | 预导航 120s 超时 | 不可用

## 反爬与访问

- 直连反爬：zhihu.com / zhuanlan.zhihu.com 直连 403（webfetch 与 anysearch extract 均被拦）；reuters.com 受 DataDome 人机验证；dl.acm.org 正文被墙 → 可改走 Semantic Scholar API 取摘要；appbrain/apkpure 开发者页 curl 返空 | 不可用
- 代理：抓部分欧美机构站需显式 `--proxy http://127.0.0.1:7897`（en.wikipedia、bellingcat、datajournalism 等可抓） | 可用
- SPA 站点：Next.js 等客户端渲染页面 curl/webfetch 拿不到内容，需 playwright 取快照（如 themodernsoftware.dev 的 syllabus） | 部分可用
- 本机工具：yt-dlp 对 YouTube 报 format 错误不可用；web-content-guard 净化后正文可 grep 提取 | 部分可用

## 内容生态（软文 / 噪音）

- 商品测评通用搜索软文污染高：中文家电/数码类"横评"大量为 AI 批量生成的营销稿（单一品牌强推 + 参数夸张 + 无实测 + 引流链接），按 credibility-framework 五级分类整体降为低置信 | 高噪声
- 商家自营"指南"类内容立场天然偏向：如情趣用品商家博客的"过安检指南"一律"放心带"，须整体降为低置信 | 高噪声
- 带佣推广文识别：外卖口令/领券类文章几乎全含推广（文末标广告或引流公众号）；机制性描述可当线索，数字/结论需多源印证 | 仅线索
- 2026-10-19 | 知乎/微信 | academic | 搜"知网AI 实测"等关键词几乎全被 AIGC 检测/降重的论文产业链营销号污染，真实使用测评极少——此类工具的能力评估优先看官方文档、官网实测与高校图书馆试用公告 | 高噪声
- 2026-10-19 | Consensus/scite/沁言学术 | academic | 厂商宣称互相打架：Consensus 语料数同一产品三处口径不一（博客 200M+/帮助中心 220M+/pricing 页 400M+）；scite 无真免费档仅 7 天试用；第三方"知网全文检索"类独立验证仅剩自家软文——知网 2024-08 曾向秘塔发侵权函，全文授权是硬门槛 | 高噪声

## 维护规则

1. 新增条目前先搜本文件是否已有同通道同领域的记录；有则更新该行日期与判定，不重复堆叠。
2. 判定只能取枚举值，不写"可能""部分情况下"这类模糊词——模糊的判断无法用于选路。
3. 观察里必须包含可复现的触发条件（查询式、参数、错误码），否则下次无法复用。
4. 超过 12 个月未复测的条目，视为"待复测"，不直接当作当前结论。
