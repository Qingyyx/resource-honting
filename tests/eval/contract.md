# 评测输出契约

被测系统在评测模式下，先按 `resource-hunting` 正常执行检索与验证，最后**只输出一个 JSON 对象**。不要输出解释性前后文，不要用 Markdown 代码块包裹。

## 字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `status` | string | 是 | `answered` / `abstained` / `blocked` / `partial` |
| `answer` | string | 是 | 最终答案；`abstained` 时说明查了什么、为什么没有答案 |
| `route.domain` | string | 是 | 本次采用的领域 |
| `route.effort` | string | 是 | `quick` / `standard` / `deep` |
| `route.channels` | string[] | 是 | 实际用到的通道，取值见下 |
| `route.queries` | int | 是 | 实际检索/抓取调用次数 |
| `facts` | object[] | 是 | 答案中每个可验证事实一条；无事实时为空数组 |
| `facts[].claim` | string | 是 | 该事实的自然语言陈述 |
| `facts[].value` | string | 是 | 关键值（日期、数字、编号、名称） |
| `facts[].source_url` | string | 是 | 支撑该事实的 URL |
| `sources` | object[] | 是 | 去重后的来源列表 |
| `sources[].url` | string | 是 | 来源 URL |
| `sources[].title` | string | 否 | 页面标题 |
| `sources[].primary` | bool | 是 | 是否为官方/一手源 |
| `as_of` | string | 是 | 本次判断所依据的日期，ISO 格式 |
| `confidence` | string | 是 | `high` / `medium` / `low` |
| `notes` | string | 否 | 缺口、受限原因、改判说明 |

## 通道取值

`ddgs` / `anysearch` / `exa` / `zhipu` / `opencli` / `direct-primary` / `none`

## 约束

- 只输出 JSON。不要用 ```json 包裹，不要加“以下是结果”之类的前后文。
- `facts` 必须覆盖 `answer` 中所有可验证陈述；每条都要有 `source_url`。
- `sources` 必须去重；`primary=true` 只给官方、原始披露、一手文档。
- 无法访问时 `status=blocked`，并在 `notes` 写明 login / paywall / 403 / robots。
- 没有答案时 `status=abstained`，`answer` 必须说明检查范围，不能编造。
- 不要编造 URL；不确定的链接不要放进 `sources`。

## 示例

```json
{
  "status": "answered",
  "answer": "示例：某标准自 2001-01-01 起生效。",
  "route": {
    "domain": "general",
    "effort": "quick",
    "channels": ["direct-primary"],
    "queries": 1
  },
  "facts": [
    {
      "claim": "某标准自 2001-01-01 起生效",
      "value": "2001-01-01",
      "source_url": "https://example.com/spec"
    }
  ],
  "sources": [
    {
      "url": "https://example.com/spec",
      "title": "示例来源",
      "primary": true
    }
  ],
  "as_of": "2026-10-31",
  "confidence": "high",
  "notes": ""
}
```
