# references 索引

> 先按任务选一组，不要全读。SKILL.md 的"按需加载"是入口；本页补充分组与常用组合。

## 找：去哪找、怎么找

| 文件 | 解决什么 |
|---|---|
| [routing.md](routing.md) | 已知领域的一手源、端点、检索顺序与坑；9 个领域各一节 |
| [discovery.md](discovery.md) | 来源地图（角色 / 资源形态）+ 陌生领域、空结果、身份不明的检索路线 |
| [search-tools.md](search-tools.md) | 通道选择与降级、AnySearch / OpenCLI / 智谱搜狗、操作符、AI 研究工具 |
| [deep-research-sources.md](deep-research-sources.md) | 深度调研的分层取证、学科库、研报、播客与工作流 |

## 判：这条能不能信、放在一起说明什么

| 文件 | 解决什么 |
|---|---|
| [platform-trust.md](platform-trust.md) | 平台置信度分档、领域 × 平台速查、购买前查证流程 |
| [credibility-framework.md](credibility-framework.md) | 单条信息核验：SIFT、CRAAP、身份声称、软文与 AI 内容检测 |
| [evidence-synthesis.md](evidence-synthesis.md) | 多条证据合成：断言分解、竞争假设、独立性、信心与可能性分轴 |

## 记：跨任务经验

| 文件 | 解决什么 |
|---|---|
| [field-notes.md](field-notes.md) | 通道与站点的实测台账；选路前读，任务后按格式写 |

## 评测

| 文件 | 解决什么 |
|---|---|
| [../tests/eval/README.md](../tests/eval/README.md) | 分层回归测试集：用例、运行方式、判分与基线 |
| [../tests/eval/methodology.md](../tests/eval/methodology.md) | 评测方法与指标：成功条件、规则检查 vs 真实检索、结果记录 |

## 常用组合

- **快速事实**：SKILL.md §2 → [routing.md](routing.md)；来源不确定时加 [platform-trust.md](platform-trust.md)。
- **陌生领域 / 多次空结果**：[discovery.md](discovery.md) → [search-tools.md](search-tools.md) → [field-notes.md](field-notes.md)。
- **商品比价**：[routing.md](routing.md) 的 `product` → [platform-trust.md](platform-trust.md) 的购买前查证 → [field-notes.md](field-notes.md)。
- **深度调研**：[deep-research-sources.md](deep-research-sources.md) → [evidence-synthesis.md](evidence-synthesis.md)；平台档位查 [platform-trust.md](platform-trust.md)。
- **多源冲突**：[credibility-framework.md](credibility-framework.md) 定单条强弱 → [evidence-synthesis.md](evidence-synthesis.md) 裁冲突。
- **评测检索能力**：[../tests/eval/README.md](../tests/eval/README.md) 跑套件；指标口径见 [../tests/eval/methodology.md](../tests/eval/methodology.md)。
