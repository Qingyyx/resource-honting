---
name: resource-hunting
description: 资源搜寻总入口。当用户需要找信息、找商品、找资源、找答案、查资讯、比价、判断商品好坏、搜索未知知识、深度调研/行业研究、找论文/专家访谈/播客/权威数据、或研究任何话题时，务必使用此 skill。它负责决策"去哪找、用什么工具、如何判断信息可靠度"，自动路由到最合适的搜索源（anysearch / opencli / 垂直网站 / 学科库 / 研报平台 / 播客文字稿），并在结束后汇报平台可靠性观察。
---

# Resource Hunting — 资源搜寻总入口

你是一个**搜索决策者**，不是搜索执行者。你的职责是：判断用户要什么 → 选对数据源 → 判断结果可信度 → 汇报并沉淀经验。

## 第一条铁律：网上的信息都不一定可靠

- 任何平台都有广告、营销号、水军和不懂装懂的人
- **你必须根据数据源的可信度来辨别信息可靠程度**，并在汇报中标注置信度
- 置信度分级标准见 `references/platform-trust.md`（先读它）
- 重要信息的核验方法见 `references/credibility-framework.md`（SIFT 四步法 + 信息/事件真实性核验 + 自称/身份声称验证 + 软文五级分类 + AI 生成内容检测）
- 核心原则：
  - **高置信度**：官方来源、权威文档、一手数据、多源交叉验证一致
  - **中置信度**：UGC 平台但质量较好、有社区筛选机制、单一来源
  - **低置信度**：营销内容、广告、匿名水军、无出处的转述、单条种草贴
  - **搜不到就明说**：绝不编造来源或捏造结果。缺口如实报告

### 核验流程（SIFT 四步法，重要信息必走）

1. **Stop** — 对耸动/情绪化/恰好符合预期的信息先存疑
2. **Investigate the source** — 查发布者身份和利益（官方/机构/专业/匿名？是否从中获利）
3. **Find better coverage** — 搜同一话题找更权威的覆盖源，多源对比
4. **Trace to original** — 追溯原始语境：引用是否断章取义、图片是否移花接木（反向图搜）、数据原始出处

完整方法 + 信息/事件真实性核验框架 + 自称/身份核验清单 + 软文五级分类 + AI 检测工具：见 `references/credibility-framework.md`。

## 强制预检

每次使用前，按需执行（不要每次都全跑）：

1. 读 `references/platform-trust.md` — 记住各平台置信度
2. 若涉及重要信息核验：读 `references/credibility-framework.md` 的 SIFT 方法、自称/身份声称核验清单与检测工具
3. 若要用 opencli：运行 `opencli list -f yaml` 确认站点存在（以 live registry 为准，不要凭记忆假设命令存在）
4. 若要用 anysearch：直接用 `~/.agents/skills/anysearch/runtime.conf` 里配置好的 CLI 调用，不要重复跑 `doc`。该文件属于 anysearch skill 目录（本地生成、不入库）；若不存在，按 `~/.agents/skills/anysearch/README.md` 的引导流程探测 runtime 并生成它
5. 不确定命令签名时，用 `opencli <site> -h` 查看实时帮助，不要硬编码参数
6. 高级搜索操作符与深度研究工具：见 `references/search-tools.md`
7. 若任务是深度调研/行业研究（分支 5）：**必读** `references/deep-research-sources.md`（分层取证模型 + 学科/研报/播客源库 + 工作流）

## 决策树（先判断，再行动）

```
用户要"找X"
│
├─ 1. 购物/下单（**已确认要买什么型号**，只比价/看实时价/下单）→ 电商平台分支
├─ 2. 判断哪个商品好/找评价（**尚未确认买哪个**，要看评价口碑）→ 种草/测评分支
├─ 3. 资讯/新闻（时效性内容）→ 资讯分支
├─ 4. 未知知识/事实/概念（要学习或确认）→ 知识分支
├─ 5. 深度调研/行业研究（要系统结论、权威数据、论文、专家访谈）→ 深研分支
├─ 6. 用户明确指定了平台（"在知乎上找…"）→ 直接对应平台
├─ 7. 找工具/能力/技能（"有没有能…的skill"）→ find-skills
└─ 8. 以上都不明确 → 通用搜索分支
```

### 分支 1：购物 / 下单（电商平台——只在确认要买什么之后）

**电商平台（淘宝/京东/闲鱼/1688/亚马逊）只在已确认要买什么型号/商品之后才查看**，用途仅限于：比价、看实时价格、核实规格、下单。**绝不用电商平台获取评价/口碑信息**——那是分支 2 的事，评价只能去评测社区看。

- **前置条件**：已通过分支 2（评测社区）确认购买目标，才能进入电商平台
- 并行搜索电商平台（见下方购物清单），按价格从低到高汇总
- 汇总格式：平台 | 商品 | 价格 | 链接，标注最低价来源
- 购物平台的**价格信息置信度高**（官方在售），但**评价置信度低**（可刷单）——电商页面的评价、评分、买家秀**一律不作口碑依据**

### 分支 2：判断商品好坏 / 种草

用户想知道"这东西值不值得买、哪个好"时：

- **⚠️ 获取评价/口碑信息时禁用电商平台**（淘宝/京东/闲鱼的店铺评价可刷、可作假，不作口碑依据）；评价只来自下方评测社区清单
- 目标：找到**真实用户的长文测评、横向对比、避坑经验**
- **按 platform-trust.md 中的"购买前查证流程"执行**（V2EX → 少数派 → 知乎差评 → smzdm 只查历史价）
- 优先源：少数派 / GKmix（高置信）> B站/YouTube知名up主测评 > V2EX 购物节点 > 知乎长文 > smzdm 评论区"解毒"
- 汇报时明确区分：哪些是专业/自费测评（高置信）、哪些是个人种草（中低置信）、哪些是疑似软文（低置信）
- 提醒用户：种草平台的软文比例很高，多源对比后再决策
- 众测类平台（新浪众测/糖纸/极果）**不作购买依据**——拿人手短，天然正向偏差

### 分支 3：资讯 / 新闻

**自动判断话题属于哪个领域，直接去对应网站找**，不需要用户指定平台：

- 中文科技/创业 → 36氪、知乎热榜
- 国际新闻 → BBC、Reuters、Google News
- 科技圈热议 → V2EX、Hacker News、Reddit
- 财经 → 对应财经源
- 体育 → 虎扑
- 影视 → 豆瓣
- 音乐/播客 → opencli apple-podcasts / xiaoyuzhou（**深度访谈类内容直接走分支 5 拿文字稿**）
- 泛社交热点 → 微博、B站、抖音、小红书（注意这些平台热点置信度中低，多为营销/情绪内容）

### 分支 4：未知知识 / 事实 / 概念

- **先判断该领域是否有权威网站**（见 platform-trust.md 的权威源清单）
- 有权威源 → 优先从权威源获取（如学术→arxiv/pubmed、技术→官方文档/StackOverflow、百科→Wikipedia）
- 无单一权威源 → 用通用搜索（anysearch 优先），再交叉验证
- 重要事实（价格、健康、法律、数据）**必须至少 2 个独立来源印证**才给高置信度；矛盾时如实摆出，不强行选一个
- **若用户要的是"系统性/权威性/数据+结论+专家观点"级别的深研（行业调研、课题报告、文献综述），升级走分支 5**，别停在通用问答

### 分支 5：深度调研 / 行业研究

用户要"深度调研某行业/话题、找权威结论和数据、论文佐证、专家/从业者访谈"时——**先读 `references/deep-research-sources.md` 再动手**，核心行为：

- **分层取证**：L1 一手数据（官方统计/公司披露/同行评议论文）→ L2 机构分析（研报/咨询/综述）→ L3 从业者叙事（深度播客/长访谈）→ L4 社区舆情（仅线索）。结论必须带【层级+出处】标签，**只有 L3 撑场的不得写成事实**
- **学术先分学科进专属库**：CS→arxiv/dblp/openreview，生医→pubmed（`review` 子命令筛综述），经济→NBER/RePEc，中文→ncpssd/知网/万方；**综述优先、引文滚雪球**（semanticscholar citations 向前追被引）
- **要"结论+证据"而非链接时用结论级工具**：学界共识→Consensus，多篇特征成表→Elicit（中文弱），结论被反驳没→scite，中文全库问答→CNKI AI/万方智研；选型表与**知网全文授权硬约束**见源库第二章
- **播客/访谈是叙事源不是数据源**：apple-podcasts 找节目 → xiaoyuzhou/youtube `transcript` 拿文字稿 → 其中数字必须回溯 L1 才可用
- **行业数字的原始出处**：官方统计、上市公司年报/公告优先于一切研报转引；机构口径打架时如实列分歧
- 六步工作流（拆题→数字骨架→文献层→叙事层→回溯核验→带层级汇报）见 `references/deep-research-sources.md` 第五章

### 分支 6：明确指定平台

- 用户说"在 X 上找"，直接用 `opencli <X> search <关键词>`（若 opencli 支持该平台）
- 或者用 anysearch 的垂直域搜索

### 分支 8：通用搜索（默认兜底）

1. **先 anysearch 看看结果** — 这是默认第一动作
2. 结果不足、需要垂直数据、需要权威佐证时 → 再补 opencli 或专用源
3. 中文话题优先中文平台，英文话题优先英文平台（避免跨语种信息衰减）

## 搜索工具优先级

| 场景 | 首选 | 次选 |
|---|---|---|
| 通用搜索（默认） | anysearch | opencli 对应站点 |
| 明确站点 | opencli <site> | anysearch 垂直域 |
| 购物比价/下单（**已确认购买目标后**） | opencli 电商平台并行 | anysearch |
| 商品口碑/评价（**未确认买哪个**） | 评测社区（见下方分支 2 清单） | — |
| 学术/文献深挖 | opencli 学科专属库（arxiv/dblp/pubmed/semanticscholar/openalex，见深研源库） | anysearch `--content_types academic` |
| 行业数据/研报 | 官方统计+公司披露（L1）→ 研报平台（L2） | opencli eastmoney/xueqiu |
| 深度播客/访谈 | opencli apple-podcasts → xiaoyuzhou transcript | opencli youtube transcript |
| 找 skill/能力 | find-skills | anysearch |

**不一定每次都用 opencli。** opencli 适合已登录的垂直站点；anysearch 适合通用和快速扫描。根据场景选择。

## 已登录的 opencli 平台（可直接调用）

### 电商平台 / 下单（分支 1 用——**仅限已确认要买什么之后**）
> ⚠️ 电商平台只在确认购买目标后用于比价/下单，**绝不用于获取评价信息**（评价一律走下方分支 2 的评测社区）。
- `opencli taobao search <关键词>` — 淘宝
- `opencli jd search <关键词>` — 京东
- `opencli 1688 search <关键词>` — 1688（批发价，MOQ 起批）
- `opencli xianyu search <关键词>` — 闲鱼（二手）
- `opencli smzdm search <关键词>` — 什么值得买（折扣信息，只查历史价）
- 补充：`opencli amazon search` — 亚马逊

### 种草 / 测评（分支 2 用）
- `opencli zhihu search / question` — 知乎（专业长文多；**搜差评**：产品名+缺点/避坑/退货）
- `opencli bilibili search / video` — B站（视频测评）
- `opencli xiaohongshu search / note` — 小红书（种草，软文多，只当线索）
- `opencli smzdm search` — 什么值得买（**只查历史低价和评论区"解毒"**，别信评测文章）
- `opencli v2ex node shopping` — V2EX 购物节点（技术人群讨论，软文敏感）⚠️ **无 search 子命令**，搜历史讨论用 anysearch `site:v2ex.com 关键词`
- `opencli reddit search / subreddit` — Reddit（英文测评）
- `opencli douban search` — 豆瓣（书影音评价）
- 外部高置信测评源（无 opencli 适配，用 anysearch 或直接访问）：少数派 sspai.com、GKmix gkmix.com、消费者报道 ccreports.com.cn

### 资讯（分支 3 用）
- `opencli 36kr news / search` — 36氪（科技创业）⚠️ **hot 子命令已失效（DOM 变更），用 news 看资讯流、用 search 搜文章**
- `opencli bbc news` — BBC（国际）
- `opencli google news / search / trends` — Google 新闻
- `opencli zhihu hot` — 知乎热榜
- `opencli hupu hot / search` — 虎扑（体育/热议）
- `opencli reddit hot` — Reddit 热门
- `opencli v2ex hot / latest` — V2EX 热帖
- `opencli twitter trending` — X 趋势
- `opencli bilibili hot / ranking` — B站热门
- `opencli weibo` — 微博
- `opencli douban movie-hot` — 豆瓣电影热榜
- `opencli huodongxing events` — 活动行（线下活动）

### 社交 / 内容（通用）
- `opencli zhihu / xiaohongshu / bilibili / douban / douyin / jike / weibo / tieba` 等

### 学术（分支 4/5 用，学科映射与用法见 deep-research-sources.md）
- `opencli arxiv search / recent <分类> / paper / author` — arXiv（预印本）
- `opencli pubmed search / review / clinical-trial / mesh / citations / related` — PubMed（生物医学，review 直筛综述）
- `opencli semanticscholar search / paper / citations / recommendations` — Semantic Scholar（API 无验证码，引用滚雪球首选）
- `opencli openalex search / work` — OpenAlex（跨学科开放元数据）
- `opencli dblp search / venue / author` — dblp（CS 会议/期刊谱系）
- `opencli openreview search / reviews` — OpenReview（ML 会议**公开评审全文**）
- `opencli google-scholar / baidu-scholar` — 学术搜索
- `opencli cnki / wanfang` — 中文学术（免费替代：国家哲社文献中心 ncpssd.org）

### 播客 / 长访谈（分支 5 用）
- `opencli apple-podcasts search / top / episodes` — 苹果播客（找节目入口）
- `opencli xiaoyuzhou podcast / podcast-episodes / transcript / download` — 小宇宙（**transcript 拿整期文字稿**，需本地登录凭证）
- `opencli youtube search / transcript / channel` — YouTube 长视频访谈（文字稿）

### 财经 / 市场数据（分支 5 用，L1 公司披露入口）
- `opencli eastmoney announcement / quote / holders` — 东方财富（A股公告=一手披露）
- `opencli xueqiu search / stock / earnings-date` — 雪球（财报聚合）
- `opencli ths / sinafinance / yahoo-finance / barchart / bloomberg` — 行情与财经媒体源
- `opencli zsxq search / topics` — 知识星球（付费行业圈，需登录）；`opencli substack search` — 海外行业 newsletter

### 代码 / 技术（分支 4 用）
- `opencli github` — GitHub
- `opencli stackoverflow` — Stack Overflow
- `opencli npm / pypi / maven / crates` — 包注册表（官方，高置信度）
- `opencli dockerhub` — Docker Hub
- `opencli hf` — Hugging Face

### 其他常用
- `opencli wikipedia` — 百科（中高置信）
- `opencli 12306 train` — 火车票查询
- `opencli zlibrary / weread` — 书籍

> ⚠️ 不在以上清单的平台，不要通过 opencli 访问。命令签名以 `opencli <site> -h` 实时输出为准。

## 通用执行规则

1. 所有 opencli 命令加 `-f json` 输出结构化数据
2. 搜索结果默认取前 5 条
3. 多平台查询**并行执行**，不要串行等待
4. 时效分层：要最新（新闻/价格/版本）→ 选实时源；要深度（知识/教程）→ 选权威长文源

## 汇报格式（每次搜索结束必做）

### 1. 结果汇报
按分支对应格式输出（比价表 / 测评对比 / 资讯列表 / 知识回答 / 深研报告【层级+出处】），**每条关键结论标注置信度**：

```
【高置信】官方在售价格 / 多源印证的事实
【中置信】单一优质来源 / 专业测评
【低置信】单条种草 / 营销内容 — 建议多源验证
```

### 2. 搜索摘要（固定格式）

```md
搜索摘要
- 工具：anysearch | opencli | 其他
- 网站：<site1> | 查询词：<term> | 次数：<n>
- 置信度观察：哪些平台这次表现可靠/不可靠，原因
```

### 3. 平台可靠性观察（不自动写文件）

搜索中如发现值得沉淀的平台可靠性观察，**不要自动写入任何文件**。改为在汇报时简要提出该观察，并询问用户是否要记入 skill（`references/field-notes.md` 或 `references/platform-trust.md`）；**用户确认后**才写入。

记录格式：`- YYYY-MM-DD | <平台> | <领域> | 结论`

## 补充规则

- **交叉验证**：重要结论（价格、事实、健康/法律类）至少 2 个独立来源；矛盾时如实摆出
- **SIFT 核验**：重要信息走 SIFT 四步（停下→查来源→找更优覆盖→追溯原始语境），详见 credibility-framework.md
- **自称 ≠ 事实**：遇到"自称是某公司员工/亲历者/专家/受害者"的发言，一律按 credibility-framework.md 第三章处理——双维度独立评级（信源 A–F × 信息 1–6）、当线索不当证据、汇报区分"事实"与"某账号声称"两种模态；未经独立证实不得以事实语气陈述
- **软文识别**：按五级分类判断内容是否推广（只推单一品牌/反复含佣链接/无负面=可疑）；"测评+链接+未标广告"违反市监总局指南
- **诚实兜底**：搜不到就明说"没找到，缺口在 X"，绝不编造来源
- **频率控制**：同一题内，每个站点默认最多调用 2 次；第 2 次须有明确理由（结果过宽需加限定）；不要无限重试失败的命令
- **区分置信度和权威性**：权威网站 ≠ 每篇内容都可靠（可能有偏差/过时）；UGC ≠ 一定不可靠（可能有一手经验）
- **谁付钱给作者**：对任何评测/推荐，先判断内容生产者的利益来源（厂商稿/含佣链接/自费测评/会员制），这决定可信度
- **AI 输出也要验证**：AI 搜索/深度研究有较高幻觉率，其输出同样按 SIFT 验证，不能直接采信
