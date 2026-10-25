# 深度调研源库与工作流

> 用途：当任务是**对某行业/话题做系统性深度调研**（要权威结论、一手数据、专家观点、从业者叙事）时读本文件。
> 与通用搜索的区别：深度调研不是"搜一条答案"，而是**分层取证、交叉印证、追溯原始出处**后产出一份带证据等级的结论。
> 置信度总表见 `platform-trust.md`，核验方法见 `credibility-framework.md`，AI 深度研究工具见 `search-tools.md`。
> 本文件的 opencli 命令均已对照 live registry（2026-10 核实）；新站点用前先 `opencli <site> -h`。

## 一、分层取证模型（先定层级，再找源）

深度调研的每条结论必须能落到某个证据层级，汇报时标注：

| 层级 | 内容 | 用途 | 置信基调 |
|---|---|---|---|
| **L1 一手数据** | 官方统计、公司披露（年报/公告/招股书）、同行评议论文、监管文件、央行/海关数据 | 数字和事实的**唯一合格出处** | 高 |
| **L2 机构分析** | 券商研报、咨询机构、智库、行业协会报告、学术综述 | 分析框架、行业测算、趋势判断 | 中高（注意立场） |
| **L3 从业者叙事** | 深度播客访谈、长视频访谈、从业者长文复盘、创始人/高管演讲 | 行业内幕、因果链、"纸面数据背后发生了什么" | 观点级；其中**数据必须回溯 L1** 才可用 |
| **L4 社区舆情** | 知乎/Reddit/V2EX/小红书等（见 platform-trust.md） | 线索、情绪、个体体验 | 低-中，不作调研结论依据 |

**铁律**：
- 调研结论至少由 L1+L2 支撑；只有 L3 撑场的结论必须降级表述为"据从业者 X 所述"
- 播客/访谈里出现的关键数字（市场规模、增速、渗透率），SIFT-T 追到原始研报/统计口径才算成立
- 利益审查照常：卖方研报天然偏乐观、行业协会护本行业、咨询报告带营销性质——"谁付钱给作者"三问不变

## 二、学术 / 论文通道（L1/L2）

### 学科专属库（比通用学术搜索重要得多——先判断话题属于哪个学科）

| 学科 | 首选源 | 说明 |
|---|---|---|
| 计算机/AI | `opencli arxiv search/recent/author`、`opencli dblp search/venue`、`opencli openreview search/reviews`、`opencli hf`（论文详情） | dblp 查会议/期刊谱系；**openreview reviews 能看到 ICLR/NeurIPS 等公开评审全文**（审稿人质疑=免费的批判性同行评审）；arxiv `recent cs.LG` 扫最新风向 |
| 生物医学 | `opencli pubmed search/review/clinical-trial/mesh/journal/related/citations` | **review 子命令直接筛综述文**；clinical-trial 筛试验；mesh 用主题词表精确检索 |
| 经济/金融 | NBER（nber.org 工作论文）、RePEc/IDEAS（经济学期刊聚合）、SSRN（预印） | 中文经济政策看《经济研究》《金融研究》（知网/万方） |
| 中文社科/综合 | `opencli cnki search`（oversea 站）、`opencli wanfang search`、维普 cqvip | 付费墙重；**国家哲学社会科学文献中心 ncpssd.org 免费**，中文论文优先试它 |
| 跨学科综合 | `opencli semanticscholar search/paper/citations/recommendations`、`opencli openalex search/work`、`opencli google-scholar search/cite/profile`、`opencli baidu-scholar search` | Semantic Scholar/OpenAlex 走 API 无验证码，abstract+tldr+引用图 |

### 文献深挖方法（新手 vs 老手的差别）

1. **综述优先**：进入新领域先搜 review/survey/meta-analysis/系统综述，一篇顶二十篇散论文（pubmed 有现成 `review` 子命令）
2. **引文滚雪球**：找到一篇关键论文后，向后看参考文献（backward 追溯源头），向前看"被引"（forward 找最新进展）：`opencli semanticscholar citations <id>`、`opencli pubmed citations <pmid>`、google-scholar `cite`
3. **质量分级**（医学证据等级推广到一般）：系统综述/Meta分析 > RCT > 队列/观察研究 > 专家意见/个案；预印本一律降一档
4. **看钱从哪来**：论文末尾 funding/COI 声明——药企资助的研究结论方向性偏向是实证现象
5. **AI 学术助手**：Consensus（只用同行评议源回答"学界共识是什么"）、Elicit（批量结构化文献综述）——用法见 `search-tools.md` 第三章
6. anysearch 备用：`anysearch search "关键词" --content_types academic`（已实测可用，能召回期刊+产业研究院文章）

### 结论级 AI 学术工具（直接搜"结论+证据句"，不是搜链接）

| 需求 | 工具 | 关键事实（2026-10 多源核实） |
|---|---|---|
| "学界对某问题是支持还是反对"（yes/no/mixed） | **Consensus** | Meter 对 top20 命中论文逐字抽取证据分类，非生成；官方承认 ~10% 误判；语料宣称 200M–400M 口径不一致，按宣传数字打折 |
| 多篇论文特征对比成表（样本/干预/结局/结论） | **Elicit** | 138M（S2+OpenAlex+PubMed+临床试验）；独立评估抽取 F1 81–92%（有编造条目记录）；**官方自认中文语料弱**——中文课题勿用 |
| 某结论后来被支持还是被反驳 | **scite** | 1.6B Smart Citations（supporting/contrasting/mentioning），有同行评议方法论文；医学/生科覆盖最强；无真免费档 |
| 全文级证据问答（生物医学，免费） | FutureHouse 平台（Crow）/ Ai2 Asta | 句级引用+沿引文链追证；评测基准用训练截止后的论文防背题 |
| 对自己上传的论文问答 | NotebookLM | 仅基于给定源作答，引用接地最好（研究显示幻觉率 13% vs 通用 AI 40%） |
| 中文题的结论级问答 | **CNKI AI**（ai.cnki.net）/ 万方智研 / 维普科创助手 / 知乎直答 | 知网自家"华知大模型"，支持段落检索+文献回溯；知+会员付费 |

- **授权硬约束**：知网全文不允许第三方索引（2024-08 知网向秘塔发侵权函后秘塔即下架知网题录摘要）——凡第三方 AI 产品声称"检索知网全文"，先查授权，无授权即降为宣传
- **底层真相**：上述商业工具大多长在同一批开放库上——Semantic Scholar 学术图谱（2.25 亿论文/28 亿引文边）与 OpenAlex（2 亿 work，日更）。深研脚本直接调 `opencli semanticscholar` / `opencli openalex` 即可拿同层原料，不必绕道产品
- 通用 AI Deep Research（Perplexity 学术模式等）**没有自建论文库**，只是限定域名的网页搜索，实证幻觉引文率最高——仅当开局广度扫描用，产出必须回原文核对

## 三、行业研报与数据平台（L1/L2）

### 官方数据（L1，行业数字的原始出处）

- **国家统计局** stats.gov.cn：宏观、分行业产值、居民收支
- **部委口径**：工信部（ICT/制造）、海关总署（进出口额）、国家能源局、央行/金融监管总局（金融数据）
- **政府文件/法律**：`opencli gov-law` / `opencli gov-policy`（opencli 已有适配）
- **公司一手披露**：A股公告 `opencli eastmoney announcement`、`cninfo 巨潮资讯`（年报/招股书）；港股披露易；美股 SEC EDGAR；财报电话会纪要（earnings call）搜公众号/雪球文本版
- **行情/财务聚合**：`opencli xueqiu search/stock`（雪球，含财报日期）、`opencli eastmoney quote/kline/holders`、`opencli ths`（同花顺）、美股 `opencli yahoo-finance/barchart/bloomberg`
- **国际组织开放数据**：World Bank Open Data、OECD Data、IMF、UN Data、Our World in Data、IEA（能源）、Statista（付费，媒体转引时注意追原报告）

### 研报 / 机构分析（L2）

- **中文研报聚合**：发现报告 fxbaogao、慧博投研 hibor、199IT（互联网数据中心，收录免费报告）、前瞻产业研究院（anysearch 实测可命中其报告页）
- **垂直研究机构**：艾瑞（消费/互联网）、QuestMobile（移动互联网数据）、易观、亿欧（产业）、EqualOcean 亿欧出海、GGII 高工产业研究院（锂电/汽车产业链）、中国信通院 CAICT（ICT 白皮书，免费，质量高）
- **咨询/智库**：McKinsey MGI、BCG、贝恩、Gartner/IDC/Counterpoint/Canalys（TMT 份额数据）、Nielsen/Kantar（消费品）、Pew（美国社会）、RAND
- **融资/公司库**：IT桔子（中文一级市场）、Crunchbase、天眼查/企查查（工商股权穿透）
- **使用纪律**：研报的**数据表格**可信度尚可（多引自 L1），**评级和预测**（"目标价""明年翻倍"）一律低置信；引用报告先记"机构+报告名+发布年月+原始数据出处"再落笔

### 行业垂直社区（L3-L4 混合，按 platform-trust 定级）

- **付费行业圈**：`opencli zsxq search/groups`（知识星球，行业大V私密圈，需登录，内容付费筛选有一定质量但立场极强）；`opencli substack search`（海外行业 newsletter）
- **就业/行业内部**：`opencli 1point3acres`（一亩三分地，留学/海外就业）、`opencli nowcoder`（牛客，国内求职）、`opencli linkedin`、maimai（脉脉，内容接口有限）
- **垂直领域**：autohome 汽车之家/dongchedi（汽车）、steam（游戏）+ Newzoo（游戏产业）、coingecko/defillama/binance（加密）、imdb/tvmaze（影视）、dianping/ctrip/booking（食酒旅）、hltv（电竞）
- **技术风向**：hackernews、github-trending、juejin、lobsters、devto、medium（opencli 均有适配）；行业年度 survey：Stack Overflow Developer Survey、State of JS、GitHub Octoverse、DB-Engines（数据库份额）

## 四、深度播客与访谈（L3，从业者叙事层）

**价值**：论文和研报给"数字"，深度访谈给"因果链和行业内幕"——从业者的第一人称叙事是任何纸面源替代不了的；但它是**观点源不是数据源**。

### 检索路径（opencli 已核实）

```
1. 找节目：opencli apple-podcasts search/top <领域关键词>（苹果播客全库含小宇宙节目）
   或 anysearch "行业 播客 访谈" / 小宇宙网页搜索
2. 列单集：opencli xiaoyuzhou podcast <id> → podcast-episodes <id>
3. 取文本：opencli xiaoyuzhou transcript <eid>（转文字稿，需本地小宇宙登录凭证）
   英文视频访谈：opencli youtube search → opencli youtube transcript <url>
4. 处理：文字稿落盘后 grep 关键词定位观点段落，只引用原文，不转述加工
```

### 已知高质量节目（示例性清单，非穷尽——新节目用上面路径现搜）

- **中文商业/科技**：晚点聊 LateTalk（公司深度）、硅谷101（科技产业）、商业就是这样（第一财经，经济学人解读）、忽左忽右（文化/历史/社科）、声东击西（跨学科对谈）
- **英文**：Acquired（公司史深度长谈）、Hard Fork（NYT 科技）、Odd Lots（Bloomberg 金融/经济）、Planet Money/The Indicator（NPR 经济学）、Lex Fridman（理工/行业大佬长访谈）、The Journal（WSJ）、20VC / This Week in Startups（VC/创投）、a16z Podcast
- **视频长访谈**：十三邀（人文）、B站/YouTube 行业峰会演讲+对谈（`opencli bilibili search`）

### 引用纪律（L3 专用）

- 标注格式：**"嘉宾 X（自述身份 Y）在《节目名》第 N 期（日期）表示……"**；自述身份按 credibility-framework.md 第三章核验（嘉宾头衔=自称，尤其匿名/无背书场合）
- 播客提到的数据：回到 L1/L2 找原始出处后才可作为"事实"引用；找不到原始出处就保留"据其说法"模态
- 优先有文字版/show notes 附引用来源的节目（可验证性高一档）
- 时效：播客观点是录制时刻的行业认知，两年以上的访谈当"历史截面"用，不当现状

## 五、深度调研工作流（收到"帮我深度调研 X"时按此执行）

1. **拆题**：把"调研 X"拆成可检索的维度——市场规模与增速（L1）、竞争格局（L1 公司数据）、技术/政策变量（L2）、从业者判断（L3）；先向用户复述维度框架
2. **建数字骨架**：官方统计 + 上市公司披露 + 2-3 家机构口径互证市场规模；机构间数字打架时**如实列分歧和口径差异**，不取平均
3. **文献层**：判断学科归属 → 进专属库搜综述 → 引文滚雪球补两端（源头+最新）
4. **叙事层**：搜 2-4 个深度访谈（播客优先文字稿），提炼从业者共识与分歧
5. **回溯核验**：每个将写入结论的数字/事实标注层级与出处；L3 关键说法追 L1；陌生机构查背景（SIFT-I）
6. **汇报**：结论逐条带【L1/L2/L3+出处】标签；附"未解决的分歧"和"信息缺口"清单；**缺口明说，不编**

**频率豁免**：分支内"每站最多 2 次"限制针对检索类调用；深度调研中"逐篇取论文/逐期取文字稿"属于不同资源抓取，不计入重试次数，但单站批量仍节流（间隔调用，失败即换源，不死磕）。

## 六、AI 深度研究工具的位置

Perplexity / ChatGPT Deep Research / Gemini Deep Research 可作**广度扫描加速器**（快速建立领域地图、找线索），但产出**不自动获得任何层级**——逐条引文核实后才归档；幻觉引文率参考 credibility-framework.md 第三章"AI 输出纪律"。opencli 已有 chatgpt/gemini 的 deep research 报告读取适配（`opencli chatgpt -h` 查实时签名）。
