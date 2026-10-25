# 平台可靠性观察记录（field notes）

> **用途**：沉淀对各平台/搜索通道可靠性的**可复用结论**，供汇报标注置信度与后续更新 `platform-trust.md` 参考。
> **写入规则**：**不自动追加**。搜索中如发现值得沉淀的观察，先在汇报时提出，**经用户确认后**才写入本文件或 skill。
> **格式**：`- YYYY-MM-DD | <平台/通道> | <领域> | 结论`（日期为观察时间，用于判断时效）

## 搜索通道

- 2026-08-14 | anysearch | 通用 | 默认首选：通用/中文搜索质量好，能直接抓知乎长文、官方 FAQ、行业研报；extract 对 gov 站点与官方文档干净，对部分商业站（雪球等）返回噪声或 WAF 混淆
- 2026-09-08 | anysearch | 稳定性 | API endpoint 多次出现 Connection Error / SSL_ERROR_SYSCALL（匿名限流）；`batch_search` 上限 5 且不可靠，**串行单查询基本稳定**，失败后 sleep 3-8s 重试；曾整段时间不可用，需回退 exa + webfetch
- 2026-09-11 | anysearch | 数据质量 | 存在 URL 字段噪声（标题与链接错配）；核验以标题 + 独立来源为准，不可只信返回 URL
- 2026-08-17 | exa websearch | 通用 | 备用通道：对英文/niche 主题语义检索召回好，可直达 Reddit 原生帖；但 MCP 频繁 timeout、socket 故障，批量并发易失败，单发较稳
- 2026-09-08 | opencli google/duckduckgo | 通用 | opencli 通用搜索不稳定（google 返 NOT_FOUND 疑似 CAPTCHA、duckduckgo 超时/空）；垂直站点（zhihu/bilibili）可靠得多
- 2026-10-19 | anysearch | 垂直域 | `list_domains` 报服务端 `tool 'list_domains' not found`（单域/批量均失败）；`search --content_types academic` 不受影响，实测可召回期刊+产业研究院文章——垂直子域格式暂不可查，先用 content_types

## opencli 站点

- opencli zhihu | 搜索正常，命中高赞长文/回答；`answer-detail <id>` 取回答全文、`download --url` 导出专栏 Markdown；曾报 AUTH_REQUIRED（Chrome 登录态临时失效），复测恢复——再遇让用户确认 Chrome 中知乎登录态
- opencli 36kr | **hot 子命令已失效（NO_DATA，DOM 变更）**；资讯用 `news`、搜索用 `search`
- opencli v2ex | **无 search 子命令**（只有 daily/hot/latest/node/topic）；搜历史讨论用 anysearch `site:v2ex.com`，逛购物节点用 `opencli v2ex node shopping`
- opencli github | 适配器仅支持 login/whoami，**无 search**；GitHub 搜索用本机 `gh` CLI 或 anysearch `site:github.com`
- opencli jd | 价格数据可靠，但结果含"广告"前缀占位与大量无店铺名条目，偶有价格解析异常（如 ¥1983000）；多次会话返回空/失败，不稳定；可信卖家识别困难
- opencli taobao | search/detail 正常，detail 可核验特定商品实时价；"原装正品"声明普遍，真假需靠官方渠道判断
- opencli smzdm | 搜索正常（首次偶无输出，重试成功）
- opencli xianyu | 未登录会话直接 AUTH_REQUIRED，二手比价需先登录 Chrome goofish.com
- opencli bilibili | 搜索正常，测评/实操视频密度高且带播放量可排序；"绝不恰饭"类自证标题仍需甄别
- opencli weixin（搜狗） | 搜索正常，能命中大量公众号文；微信功能类话题有多篇互证，但时效偏旧
- opencli xiaohongshu | 对抽象商业概念（返佣/达人补贴等）搜索匹配差；种草内容软文多，只当线索
- opencli bbc | 正常，国际新闻可直取
- opencli reddit | 多次报 "Failed to fetch" / URL 解析错误，不稳定；Reddit 内容可改用 exa 直达
- opencli tieba | 报 EMPTY_RESULT（疑似 DOM 变更/封锁）
- opencli linux-do | 预导航 120s 超时

## 站点限定与内容源

- `site:sspai.com 关键词` | 高置信源有效：返回少数派专业测评（实测流程 + 数据），软文隔离效果好
- `site:reddit.com` / `site:v2ex.com` | reddit 能拿真实使用经验（含关键坑）；v2ex 对技术/购物话题有效，对极小众硬件（如 nRF52840）几乎无内容
- 英文测评 | exa 可一站式获取 Wirecutter / Consumer Reports / Serious Eats / Good Housekeeping 等权威横评；注意区分佣金链接媒体与会员制独立评测；英文源基本不覆盖国产品牌
- 中文一手证据 | 国内期刊（如《食品安全质量检测学报》）的一手研究可经 exa/anysearch 检索到，属高置信中文证据
- 官方一手源 | 厂商官网 FAQ / 官方 wiki / 官方分销商（Mouser/DigiKey）在售价是最可靠规格与价格源；NGC 网页（catalog.ngc.nvidia.com）可无登录抓全部 tag，驱动要求以官方 gitlab Dockerfile 的 NVIDIA_REQUIRE_CUDA 最准
- GitHub 数据 | `gh` CLI / GitHub API 为最高置信一手数据（版本/star/license/活跃度）；`gh search repos` 对 niche/口语短语召回差，可改用 API forks 列表 + raw 文件哈希比对

## 反爬与直连

- 直连反爬：zhihu.com / zhuanlan.zhihu.com 直连 403（webfetch 与 anysearch extract 均被拦）；reuters.com 受 DataDome 人机验证；dl.acm.org 正文被墙 → 可改走 Semantic Scholar API 取摘要；appbrain/apkpure 开发者页 curl 返空
- 代理：抓部分欧美机构站需显式 `--proxy http://127.0.0.1:7897`（en.wikipedia、bellingcat、datajournalism 等可抓）
- SPA 站点：Next.js 等客户端渲染页面 curl/webfetch 拿不到内容，需 playwright 取快照（如 themodernsoftware.dev 的 syllabus）
- 本机工具：yt-dlp 对 YouTube 报 format 错误不可用；web-content-guard 净化后正文可 grep 提取

## 内容生态（软文 / 噪音）

- 商品测评通用搜索软文污染高：中文家电/数码类"横评"大量为 AI 批量生成的营销稿（单一品牌强推 + 参数夸张 + 无实测 + 引流链接），按 credibility-framework 五级分类整体降为低置信
- 商家自营"指南"类内容立场天然偏向：如情趣用品商家博客的"过安检指南"一律"放心带"，须整体降为低置信
- 带佣推广文识别：外卖口令/领券类文章几乎全含推广（文末标广告或引流公众号）；机制性描述可当线索，数字/结论需多源印证
- 2026-10-19 | 知乎/微信 | 学术工具评测 | 搜"知网AI 实测"等关键词几乎全被 AIGC 检测/降重的论文产业链营销号污染，真实使用测评极少——此类工具的能力评估优先看官方文档、官网实测与高校图书馆试用公告，勿依赖知乎/微信UGC
- 2026-10-19 | Consensus/scite/沁言学术 | 学术搜索 | 厂商宣称互相打架：Consensus 语料数同一产品三处口径不一（博客200M+/帮助中心220M+/pricing页400M+）；scite 无真免费档仅 7 天试用；第三方"知网全文检索"类（沁言学术等）独立验证仅剩自家软文——知网 2024-08 曾向秘塔发侵权函，全文授权是硬门槛，无授权宣称一律降为宣传
