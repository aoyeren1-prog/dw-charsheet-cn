# 规则 JSON 写作提示词（草稿）

> 给 AI 或自己用，生成符合「地城世界车卡工具」格式的规则 JSON。
> **草稿**：此文档尚未进行实测，定稿后应随代码更新保持维护，上次更新时间：**26.11.12**

## 任务

[在此填写具体规则，例如：把某套 PbtA 规则写成规则 JSON，含 N 个 playbook……]

## 写作步骤

**两步走**：

1. 先定布局：在编写新规则时，确定 meta 框架（header 有哪些字段）、区域配布（areas 有哪些区域、areaLayout 左右栏怎么分）、refSections 有哪些类别；当为某个已有规则编写上层规则（如添加一个新 playbook）时，确认该 playbook 是否有必要对原布局进行修改。将你的布局安排清晰、完整地向用户描述并征求其确认。
2. 经用户指正、修改并最终确认后，再正式动手写完整 json。

## 写作原则

- **简洁**：用层级最简单、行数最少的格式，整合 Playbook 内涵盖的所有内容。
- **可改**：使用户无法编辑的内容（如 plain 区域里的硬编码 text）占比降到最低。

## 参考资料说明

- `rule-empty-template.json`：空规则模板，结构最权威，当从头编写一个规则 json 或添加新区域时，以其中示例为母本改写。
- `rules-format.md`：字段完整参考，查具体语法（字段、文本标记、合并规则）。
- 相关规则 json ：当为某个已有规则编写上层规则时，参阅当前任务所依赖的规则，并按照分层合并机制写作。

**你不应阅读此范围之外的无关资料。**

## rules_format 摘要

- 顶层三块：`meta`（全局）、`classes`（playbook 数组，覆盖 meta 的 header/areas）、`reference`（边栏内容）。
- `meta.header`：`charInfo`（字段）、`stats`（`items`+`flags`+`modTable`+`prompt`）、`metrics`（`fields`+`columns`）；字段/属性带 `id`/`type`/`default`。
- `meta.areas`：常用 `plain`/`moveList`/`fillbox` 三种，通用字段 `title`/`note`/`rightStats`/`resetOnClassChange`。
- `plain` 元素：`text`/`hint`/`choices`/`input`/`track`/`inputGroup`，有键元素用 `key` 存值。
- `moveList`：`groups`（`key`/`label`/`minLevel`/`moves`）与 `moves`（`name`/`text`/`requires`/`replaces`/`importArea`/`importGroup`）。
- `meta.areaLayout`：`{left,right}`，列全所有区域。
- `meta.refSections`：`{id,title,type}`（`moves`/`tags`/`search`），`reference[id]` 放内容。
- 合并：对象深合并；有键数组按键合并（`$delete` 删、新键追加）；无键数组整体覆盖；`null` 删字段。
- 文本标记：`**粗体**`、`*斜体*`、`{标签}`、`[ ]`/`[x]`、`[[key:占位]]` 内联填空位。

## 常见 PbtA 要素 → 组件映射

| 要素 | 推荐映射 |
|---|---|
| 名字 | `charInfo` 的 text 字段 |
| 属性 | `stats.items`（通常用 `modifier`，`score` 为 DND 风格特化） |
| 外观 | `plain` 的 `choices` |
| 物品栏 | `fillbox` + `rightStats`（负载）+ `counters`（货币） |
| 升级选项 | `moveList`（把升级本身做成一个动作） |
| 关系 | `plain` 的 `inputGroup` |
| 笔记 | `fillbox`，即使规则没要求，也必须添加这个区域 |
| 行动列表 | `moveList` |

## 约束

### 1. areaLayout 全局定义

**应在 meta 里列全所有区域**。原则上 playbook 可以覆盖它（整体覆盖），但通常不会被使用，尤其**不要用于添加任何新区域**。

*常见错误：将一个“默认”仅被某 playbook 使用的区域写死在该 playbook 层，导致其他 playbook 兼职时，可以获得该 playbook 的动作，却无法因此获得对应的区域（正确做法是写入 meta 并用 boundMove 控制，或编写为 refSection）。*

*例外：当某规则明确规定某 playbook **绝对**不会用到某区域，可以用它来隐藏**确定**用不到的区域。*

### 2. moveList 优先，慎用 plain

一切以独立文本块形式存在的区域都可以被做成 moveList，不限于它是否被称为“动作”。复杂、难表达的东西直接塞进动作 text。

*常见错误：把“升级选项”区域做成一个有 10+ 元素的巨大 plain。*

plain 用于结构化各 playbook 通用的简单结构化内容，对任何复杂结构和新机制的适配都非常糟糕，因此：
- 非必要不使用plain
- 不写复杂 plain
- 不把任何 playbook 专属机制写成 plain。

*常见错误：将一个明显应写为动作形式的文本块写成区域，并援引规则书中“此机制在排版时采用动作的形式，但它不是动作”的原文和用户抬杠。*

### 3. 严禁自编内容

不要写入任何原 Playbook 中没有的内容。

*常见错误：当填写 “外观” 选项时，给原本无标签的 choices 元素添加标签。*

## 输出要求

- 输出完整可导入的 JSON。
- 所有 `id`/`key` 全局唯一、稳定。
- 自查：每个 `reference[id]` 都有对应 refSections；areaLayout 列的 key 都在 areas 里；choices/input/track 都带 key。
