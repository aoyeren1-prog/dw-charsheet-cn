# 规则 JSON 参考

面向**导入 / 定制整套规则**的进阶用法。只想改几个字段的，直接看 `DW-HouseRuleTest.json` 即可。

---

## 总览

### 顶层结构

```jsonc
{
  "meta": { /* 全局配置 */ },
  "classes": [ /* 职业数组 */ ],
  "reference": { /* 资料边栏内容 */ }
}
```

**三类顶层字段**：

1. **`meta`**：全局配置（属性、区域、资料边栏定义）
2. **`classes`**：职业数组，除 `id`/`name` 外，其余字段覆盖 `meta`
3. **`reference`**：资料边栏内容对象，键名由 `meta.refSections[].id` 定义

### 规则栈合并

规则 JSON 可分层叠加：底层规则 + 房规包 → 最终规则。

- 对象字段：上层覆盖下层同名键
- 数组（有 `id`/`name`/`key` 时）：按键匹配深合并，新键追加
- 数组（无键或部分无键）：上层整体覆盖
- 字段值为 `null`：删除该字段
- 数组条目 `{"id": "...", "$delete": true}`：删除该条目

详见「公共语法 · 分层合并」一节。

---

## meta

全局配置对象，定义角色卡的头部结构、区域布局、资料边栏组织。

### meta.classLabel

修改“职业”的名称，例如：

```jsonc
{
  "meta": {
    "classLabel": "Playbook"
  }
}
```

### meta.header

角色卡顶部结构，包含三个子部分。

#### header.charInfo

角色基本信息字段数组（姓名、等级、XP 等）。

**字段配置**：

| 键 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 存储键，存入 `char.fields[id]` |
| `label` | string | 否 | 显示名，省略时显示 `id` |
| `type` | string | 是 | `text` / `number` / `select` / `track` |
| `min` / `max` | number | 否 | `number` 的范围，只约束步进箭头，手输不拦 |
| `default` | any | 否 | 初值；省略时 number/track 为 0，text/select 为空串 |
| `view` | string | 否 | `"editable"` 时查看模式下仍可改（常用于当前生命、XP） |
| `flex` | number | 否 | 基准宽 `--info-w` 的倍数（**注意**：不是 CSS flex 权重） |
| `slots` | number | 否 | 仅 `track` 类型：格数 |
| `options` | string[] | 否 | 仅 `select` 类型：候选项，下拉不限制输入任意值 |
| `tip` | string | 否 | 输入框 placeholder |

**示例**：

```json
"charInfo": [
  {"id": "name", "label": "姓名", "type": "text", "flex": 2},
  {"id": "level", "label": "等级", "type": "number", "min": 1, "max": 10, "default": 1},
  {"id": "xp", "label": "XP", "type": "track", "slots": 7, "view": "editable"}
]
```

#### header.stats

属性系统配置，包含 `items`（属性列表）和 `conditions`（状态条件）。

##### stats 顶层配置

| 键 | 类型 | 说明 |
|---|---|---|
| `prompt` | string | 初始属性分配提示文本（纯展示，职业级可覆盖） |
| `modTable` | object | 属性值 → 调整值映射表（仅 `type: "score"` 时使用） |
| `items` | array | 属性项数组（见下节） |
| `conditions` | array | 状态条件数组（见下节） |

**modTable 示例**：

```json
"modTable": {
  "1-3": -3,
  "4-5": -2,
  "6-8": -1,
  "9-12": 0,
  "13-15": 1,
  "16-17": 2,
  "18": 3
}
```

区间键写法 `"1-3"`、单值键 `"18"` 按 `lo=18, hi=∞` 处理。

##### stats.items

属性项配置。

| 键 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 存储键，存入 `char.stats[id]` |
| `label` | string | 是 | 显示名 |
| `type` | string | 是 | `score`（显示数值 + 调整值，查 `modTable`）/ `modifier`（自身即调整值） |
| `min` / `max` | number | 否 | 范围限制（只约束步进箭头） |
| `default` | number | 否 | 初值 |

**公式引用**：`id` 或 `label` 均可在公式中引用，返回**属性当前值**（`score` 模式下是原值，不是调整值）。

**示例**：

```json
"items": [
  {"id": "STR", "label": "力量", "type": "score", "min": 1, "max": 18, "default": 10},
  {"id": "DEX", "label": "敏捷", "type": "modifier", "min": -1, "max": 3, "default": 0}
]
```

##### stats.conditions

状态条件配置（如虚弱、颤抖）。

| 键 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 存储键，存入 `char.states[id]`，值是档位下标（0 为初始档） |
| `label` | string | 是 | 按钮文字 |
| `states` | number | 是 | 档数，最少 2 |
| `boundStat` | string | 否 | 绑定属性 id/label，有则显示在该属性格下方，无则独立一行 |
| `effect` | string | 否 | 机制效果：`"modPenalty"`（离开初始档则该属性调整值 −1）；省略或其他值无效果 |
| `symbols` | string[] | 否 | 自定义符号数组（长度须 ≥ `states`）；不写则画圆，填充比例 = 档位 /(档数−1) |

**示例**：

```json
"conditions": [
  {"id": "weak", "label": "虚弱", "states": 2, "boundStat": "STR", "effect": "modPenalty"},
  {"id": "exhausted", "label": "力竭", "states": 3, "symbols": ["0/2", "1/2", "2/2"]}
]
```

#### header.metrics

生命、护甲、伤害等指标字段配置。

| 键 | 类型 | 说明 |
|---|---|---|
| `columns` | number | 网格列数（默认 2） |
| `fields` | array | 指标字段数组 |

**fields 配置**：

| 键 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 存储键，存入 `char.fields[id]` |
| `label` | string | 否 | 显示名 |
| `type` | string | 是 | `text` / `number` / `select` / `track` |
| `min` / `max` | number | 否 | `number` 的范围限制 |
| `default` | any | 否 | 初值 |
| `view` | string | 否 | `"editable"` 时查看模式下仍可改 |
| `formula` | string | 否 | **仅 metrics**：显示公式提示与 ⟳ 按钮 |
| `slots` | number | 否 | 仅 `track` 类型：格数 |
| `options` | string[] | 否 | 仅 `select` 类型：候选项 |
| `tip` | string | 否 | 输入框 placeholder |

**与 charInfo 的差异**：metrics 空值回退到 `formula` / `default` 算出的默认值，charInfo 只回退到 `default`。

**示例**：

```json
"metrics": {
  "columns": 2,
  "fields": [
    {"id": "hpCur", "label": "当前生命", "type": "number", "min": 0, "view": "editable"},
    {"id": "hpMax", "label": "最大生命", "type": "number", "min": 0, "formula": "基础生命+体质"},
    {"id": "armor", "label": "护甲", "type": "number", "min": 0},
    {"id": "damage", "label": "伤害", "type": "text"}
  ]
}
```

### meta.areas

区域定义对象，键为区域 key，值为区域配置。支持五种类型。

**通用字段**：

| 键 | 类型 | 说明 |
|---|---|---|
| `type` | string | 区域类型：`plain` / `moveList` / `fillbox` / `bonds` / `heritage` |
| `title` | string | 区域标题 |
| `note` | string | 区域标题右侧的小字说明（可选） |
| `rightStats` | array | 右侧统计字段（如负载、伤害骰） |
| `resetOnClassChange` | boolean | 切换职业时清空该区域数据（默认 false） |

**rightStats 配置**：

| 键 | 类型 | 说明 |
|---|---|---|
| `key` | string | 存储键，存入 `char.fields[key]` |
| `label` | string | 显示名 |
| `formula` | string | 显示公式提示与 ⟳ 按钮（可选） |

#### type: plain

最灵活的区域类型，支持多种元素混排（文本、提示、选项、输入框、轨道）。

| 键 | 类型 | 说明 |
|---|---|---|
| `elements` | array | 元素配置数组 |

**elements 配置**（支持 5 种类型）：

**通用字段**：

| 键 | 类型 | 说明 |
|---|---|---|
| `type` | string | 元素类型：`text` / `hint` / `choices` / `input` / `track` |
| `key` | string | 存储键（仅 choices/input/track），存入 `char.areaData[areaKey][key]` |
| `label` | string | 标签文本（仅 choices/input/track），在左边显示为“**label：**”（可选） |
| `view` | string | 视图控制（可选） |

**view 视图控制值**：

| 值 | 行为说明 |
|---|---|
| `"editable"` | 查看模式下仍可编辑 |
| `"hide"` | 查看模式下隐藏该元素 |
| `"grey"` | 查看模式下置灰显示 |
| `"hideUnselect"` | 查看模式下只显示已选中项（仅 choices） |
| `"greyUnselect"` | 查看模式下未选中项置灰（仅 choices） |
| 未定义 | 查看模式下只读显示（默认） |

**type: text** —— 纯文本显示

| 键 | 类型 | 说明 |
|---|---|---|
| `value` | string | 显示的文本内容 |

**type: hint** —— 提示文本

| 键 | 类型 | 说明 |
|---|---|---|
| `value` | string | 提示内容 |

**type: choices** —— 多选项按钮组

| 键 | 类型 | 说明 |
|---|---|---|
| `value` | string[] | 候选项列表 |
| `layout` | string | 布局模式（可选，如 `line`） |

**type: input** —— 文本输入框

| 键 | 类型 | 说明 |
|---|---|---|
| `tip` | string | 输入框 placeholder |
| `prefix` | string | 默认值：该键尚无存储值时显示的回退值（可选） |
| `hint` | string | 编辑模式下输入框下方的提示文本（可选） |

**type: track** —— 分段轨道

| 键 | 类型 | 说明 |
|---|---|---|
| `value` | array | 段落配置数组：`[{label: "标签名"}, {slots: 格数}, ...]` |

轨道由标签和格子段交替组成，点击格子填充到该位置，当前段落的标签高亮显示。

**内联填空位 `[[键名]]` / `[[键名:占位内容]]`**

`text` 的 `value`、`choices` 的选项文本与 `label`、`input` 的 `label`、`track` 的段落 label 与 `label` 支持内联填空位，绑定 `char.areaData[areaKey][键名]`。

- 编辑模式为输入框，`占位内容` 作 placeholder（纯文本）；查看模式显示已存值并**按 markdown 渲染**。
- `:占位内容` 可省略；按第一个冒号切开，占位内容可含冒号，键名不能含冒号或 `]`；同名同区共享，宽度约 5～10 个汉字自适应。

**示例**：

```json
{
  "type": "plain",
  "elements": [
    {"type": "text", "text": "选择你的外观："},
    {"type": "choices", "key": "eyes", "label": "眼睛", "options": ["炯炯有神", "疲惫不堪"], "layout": "line"},
    {"type": "input", "key": "custom", "tip": "自定义外观"},
    {"type": "track", "key": "wealth", "value": [
      {"label": "穷"}, {"slots": 3}, {"label": "还行"}, {"slots": 2}, {"label": "富"}
    ]}
  ]
}
```

#### type: moveList

动作列表区域（如起始动作、进阶动作）。

| 键 | 类型 | 说明 |
|---|---|---|
| `groups` | array | 动作分组数组 |
| `selectGroups` | boolean | 分组是否带勾选框（默认 false） |
| `selectMoves` | boolean | 动作是否带勾选框（默认 false） |
| `buttons` | array | 自定义按钮配置（可选） |
| `viewSelect` | boolean | 若为true，该区域内的动作在查看模式下亦可勾选和取消勾选，且在不勾选时置灰而非隐藏（可选） |
| `boundMove` | array | 绑定动作，当角色卡没有同名动作时，该区域不渲染（可选） |

> viewSelect 和 boundMove 都是为地城世界的法术规则特化的键，目的是实现“获得动作时获得法术区域”，“法术可随时遗忘/重新准备”的效果。

**groups 配置**：

| 键 | 类型 | 说明 |
|---|---|---|
| `minLevel` / `maxLevel` | number | 等级锁定范围，对照 charInfo 里的 `level` 字段（id 或 label 均可），不满足等级条件时置灰 |
| `levelField` | string | 指定对照的字段 id/label（默认 `level`，可选） |
| `label` | string | 分组标题 |
| `note` | string | 分组说明文本（显示在标题下方） |
| `items` | array | 动作列表 |

**items 配置**：

| 键 | 类型 | 说明 |
|---|---|---|
| `name` | string | 动作名 |
| `text` | string | 动作描述（支持文本标记，见「公共语法」） |
| `requires` | string/array | 前置动作名（未满足时禁用该动作） |
| `replaces` | string/array | 替代动作名（勾选时移除被替代的动作） |
| `selectable` | boolean | 显式控制是否带勾选框（可选） |

**重要行为**：
- 带 `requires` 或 `replaces` 的动作会**自动显示勾选框**，即使 `area.selectMoves` 为 false
- `requires` 按动作名引用，前置动作未取得时该动作禁用（置灰）
- `replaces` 按动作名引用，勾选时自动移除被替代的动作（用于升级替换）

**buttons 配置**：

| 键 | 类型 | 说明 |
|---|---|---|
| `label` | string | 按钮文字 |
| `position` | string | `global`（区域级）/ `inGroup`（分组级） |
| `action` | string | `addGroup` 创建一个动作组别，`addMove` 创建一个动作 |
| `targetGroup` | string | 仅 `inGroup`：`addMove` 时的目标分组 key，可以往现有的组里追加动作（可选） |

#### type: fillbox

大文本框区域，可附带计数器、装备选项、提示文本。

| 键 | 类型 | 说明 |
|---|---|---|
| `counters` | array | 计数器配置（如金币） |
| `addCounter` | boolean | 是否显示「+ 计数器」按钮（默认 false） |
| `options` | array | 装备选项分组（点击 + 可追加到文本框） |
| `hints` | string[] | 提示文本数组（支持 markdown） |

**counters 配置**：

| 键 | 类型 | 说明 |
|---|---|---|
| `key` | string | 存储键，存入 `char.areaData[areaKey].counters[key]` |
| `label` | string | 显示名 |
| `value` | number | 初值（可选，默认 0） |

**options 配置**：

| 键 | 类型 | 说明 |
|---|---|---|
| `prompt` | string | 分组提示文本（支持 markdown） |
| `options` | string[] | 选项列表，每项显示「+ 按钮」，点击追加到文本框 |

**示例**：

```json
{
  "type": "fillbox",
  "counters": [
    {"key": "coins", "label": "金币", "value": 0}
  ],
  "options": [
    {
      "prompt": "选择你的武器（选择一项）：",
      "options": ["长剑 (近身, 1 重量)", "战斧 (近身, 挥舞, 1 重量)"]
    }
  ],
  "hints": ["你的武器外观有什么与众不同之处？请大胆想象并追加描述。"]
}
```

#### type: bonds

羁绊区域。

> TODO：relations 为 DW2 实验性内容，待形式固定下来后，可能连带 bonds 这一类别一起并入 plain 类型。


| 键 | 类型 | 说明 |
|---|---|---|
| `lines` | string[] | 羁绊模板数组 |
| `relations` | boolean | 是否启用关系功能（DW2 实验性功能） |
| `relationDepth` | number | 关系深度档数 |

关系数据存入 `char.areaData[areaKey].relations`，格式：`[{target, description, depth}]`。

#### type: heritage

血统区域（UD 专用：一组血统格 + 等量文本行 + 一张说明卡，可整区折叠）。

> TODO：为 UD 特别适配，由于过于特殊暂时未并入 plain 类型，后续可能也会并入。

| 键 | 类型 | 说明 |
|---|---|---|
| `boxes` | number | 血统格数量 |
| `boxesUpgraded` | number | 升级后的血统格数量（勾选「升级」后生效，可选） |
| `movePlaceholder` | string | 文本行输入框 placeholder（可选） |
| `description` | string | 说明卡正文（支持文本标记，可选） |
| `upgradePrompt` | string | 升级提示文本（支持文本标记，可选） |
| `upgradeEffect` | string | 升级效果说明，渲染为带「升级」勾选框的行（支持文本标记，可选） |

数据存入 `char.areaData[areaKey]`，格式：`{boxes: boolean[], moves: string[], upgraded: boolean, hidden: boolean}`。

### meta.areaLayout

区域布局配置，指定哪些区域渲染及其左右栏归属。

| 键 | 类型 | 说明 |
|---|---|---|
| `left` | string[] | 左栏区域 key 数组 |
| `right` | string[] | 右栏区域 key 数组 |

对 `meta.areas` **只渲染列入的区域**，未列入的不渲染

**合并规则**：上层定义 `areaLayout` 时**完全覆盖**下层，未写的一侧视为空。

**示例**：

```json
"areaLayout": {
  "left": ["look", "race", "gear", "bonds"],
  "right": ["starting", "advanced"]
}
```

### meta.refSections

资料边栏的页签定义数组。

**页签配置**：

| 键 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 页签 ID，对应 `reference[id]` |
| `title` | string | 是 | 页签标题 |
| `type` | string | 是 | 页签类型：`moves` / `tags` / `search` |
| `importArea` | string | 否 | 仅 `moves` 类型：默认导入目标区域 |
| `importGroup` | string | 否 | 仅 `moves` 类型：默认导入分组 key |

**type 说明**：

- `moves`：动作列表，支持导入到角色卡
- `tags`：标签库
- `search`：搜索页签

**示例**：

```jsonc
"refSections": [
  {
    "id": "basicMoves",
    "title": "基本动作",
    "type": "moves"
  },
  {
    "id": "wizard_spells",
    "title": "法师法术",
    "type": "moves",
    "importArea": "wizard",
    "importGroup": "wizard-spells"
  },
  {
    "id": "tags",
    "title": "标签",
    "type": "tags"
  },
  {
    "id": "search",
    "title": "搜索",
    "type": "search"
  }
]
```

### reference 对象

资料边栏的实际内容，键名对应 `refSections[].id`。

#### moves 类型

**结构**：

```jsonc
"reference": {
  "basicMoves": {
    "moves": [
      "纯文本说明，支持 Markdown。",
      {
        "name": "砍劈",
        "text": "动作描述...",
        "importArea": "starting",
        "importGroup": "combat"
      }
    ],
    "groups": [
      {
        "key": "advanced",
        "title": "进阶动作",
        "importArea": "advanced",
        "importGroup": "special",
        "moves": [...]
      }
    ]
  }
}
```

**moves 数组元素**：字符串（纯文本）或动作对象。

**动作对象字段**：

| 键 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 动作名称 |
| `text` | string | 是 | 动作描述 |
| `importArea` | string | 否 | 导入目标区域（move 级） |
| `importGroup` | string | 否 | 导入分组 key（move 级） |

**groups 数组**：

`groups` 是折叠块分组，渲染为 `<details>` 折叠元素。

| 键 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `key` | string | 是 | 分组 key |
| `title` | string | 是 | 分组标题 |
| `importArea` | string | 否 | 导入目标区域（group 级） |
| `importGroup` | string | 否 | 导入分组 key（group 级） |
| `moves` | array | 是 | 动作数组 |

**导入控制优先级**（从高到低）：

1. move 级：`move.importArea` / `move.importGroup`
2. group 级：`group.importArea` / `group.importGroup`
3. section 级：`refSection.importArea` / `refSection.importGroup`

**importGroup 说明**：

- 填写的是目标区域 group 的 **key**（不是 label）
- 如果目标职业没有该 group，导入时会自动创建（key 和 label 都等于 importGroup 的值）

#### tags 类型

**结构**：

```jsonc
"reference": {
  "tags": {
    "tags": [
      {
        "name": "近战",
        "color": "#e74c3c",
        "textColor": "#fff",
        "description": "需要近距离接触敌人"
      }
    ],
    "groups": [
      {
        "key": "weapon_tags",
        "title": "武器标签",
        "tags": [...]
      }
    ]
  }
}
```

**tag 对象字段**：

| 键 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 标签名称 |
| `color` | string | 否 | 背景色（CSS 颜色值） |
| `textColor` | string | 否 | 文字颜色 |
| `description` | string | 否 | 标签说明 |

**groups 数组**：

tags 的 `groups` 也是折叠块分组。

| 键 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `key` | string | 是 | 分组 key |
| `title` | string | 是 | 分组标题 |
| `tags` | array | 是 | 标签数组 |

#### search 类型

search 类型不需要 `reference` 数据，只是一个搜索界面页签。

---

## classes

职业数组，每个职业对象包含职业特有字段和对 `meta` 的覆盖。

**职业特有字段**（不能在 `meta` 中定义）：

| 键 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 职业 id |
| `name` | string | 是 | 职业名称 |
| `intro` | string | 否 | 职业简介（支持文本标记），仅资料边栏搜索命中该职业时显示 |

**覆盖字段**：职业可定义 `header`、`areas`、`areaLayout` 等字段，按分层合并规则覆盖 `meta` 中的同名配置。

### classes[].header

职业级头部覆盖，结构同 `meta.header`，按深度合并。

**示例**：覆盖属性分配提示

```json
{
  "id": "wizard",
  "name": "法师",
  "header": {
    "stats": {
      "prompt": "智力最高，体质最低"
    }
  }
}
```

### classes[].areas

职业级区域覆盖，结构同 `meta.areas`，按键深度合并。

**示例**：修改职业负载公式

```json
{
  "id": "fighter",
  "name": "战士",
  "areas": {
    "gear": {
      "rightStats": [
        {"key": "load", "formula": "12+力量"}
      ]
    }
  }
}
```

---

## 资料内容顶层键

由 `meta.refSections[].groups[].key` 指向的顶层字段，存储资料边栏的实际内容。

**数据格式**：根据对应 `refSection.type` 而定，见「meta.refSections」一节。

---

## 公共语法

### 公式语法

公式字符串用于 `formula` 字段，按以下顺序查找：

1. **整数字面量**：如 `"8"` 返回 8
2. **stats.items 的 id 或 label**：返回**属性当前值**（`score` 模式下是原值，不是调整值）
3. **charInfo + metrics.fields 的 id 或 label**：返回字段值
4. **rightStats 的 label**：返回该统计字段值

任一项查不到则整个公式求值失败，不显示结果。

**特殊说明**：`等级` 不再特判——它只是 charInfo 的一个普通字段。

**示例**：

- `"8+体质"`：查找 stats.items 中 id 或 label 为 "体质" 的属性值，加 8
- `"6+等级"`：查找 charInfo 中 id 或 label 为 "等级" 的字段值，加 6

### 文本标记语法

用于动作描述、文章内容等 `text` / `body` 字段。

| 语法 | 渲染效果 |
|---|---|
| `**粗体**` | 粗体文本 |
| `*斜体*` | 斜体文本 |
| `{标签名}` | 高亮标签样式 |
| 连续两个换行 | 段落分隔 |
| `[[键名]]` / `[[键名:占位内容]]` | 内联填空位（仅 plain 区域，详见“type: plain”说明） |

**注意**：装备（gear）和笔记（notes）区域是 textarea 直出，**不做标记渲染**。

### 分层合并

规则 JSON 可分层叠加，合并规则如下：

#### 对象字段

上层覆盖下层同名键。

```jsonc
// 下层
{"meta": {"source": "DW", "license": "CC-BY"}}

// 上层
{"meta": {"license": "Custom"}}

// 结果
{"meta": {"source": "DW", "license": "Custom"}}
```

#### 数组（有键）

每一项都能取到 `id` / `name` / `key` 时，按该键匹配合并（同键深合并、新键追加）。

适用于：`classes`、动作列表、`groups`、`elements` 等。

```jsonc
// 下层
{"items": [{"id": "sword", "damage": "d8"}, {"id": "axe", "damage": "d10"}]}

// 上层
{"items": [{"id": "sword", "damage": "d10"}]}

// 结果
{"items": [{"id": "sword", "damage": "d10"}, {"id": "axe", "damage": "d10"}]}
```

#### 数组（无键或部分无键）

存在取不到键的项（字符串、数字、嵌套数组、无键对象）时，上层**整体覆盖**下层。

适用于：`look`、`bonds.lines`、`gear.options`、`symbols` 等。

```jsonc
// 下层
{"bonds": {"lines": ["___ 欠我人情", "___ 是我导师"]}}

// 上层
{"bonds": {"lines": ["___ 是我队友"]}}

// 结果（整体覆盖）
{"bonds": {"lines": ["___ 是我队友"]}}
```

#### 删除操作

- 字段值为 `null`：删除该字段
- 数组条目 `{"id": "...", "$delete": true}`：删除匹配条目

```jsonc
// 删除字段
{"meta": {"classLabel": null}}

// 删除数组条目
{"classes": [{"id": "barbarian", "$delete": true}]}
```

#### 空数组

空数组 `[]` 视为「无改动」，不会清空下层。要清空请用 `null`。

#### areaLayout 特殊规则

`areaLayout` 的 `left` / `right` 不像普通对象那样深度合并，而是**整体覆盖**：上层一旦定义 `areaLayout`，就完全替换下层的整个对象，未写的一侧视为空。

```jsonc
// 下层
{"areaLayout": {"left": ["look", "gear", "bonds"], "right": ["starting"]}}

// 上层
{"areaLayout": {"left": ["heritage", "look"]}}

// 结果（right 被清空）
{"areaLayout": {"left": ["heritage", "look"]}}
```

---

## 附录

### 最小可用示例

```json
{
  "meta": {
    "header": {
      "charInfo": [
        {"id": "level", "label": "等级", "type": "number", "default": 1}
      ],
      "stats": {
        "modTable": {"1-8": -1, "9-12": 0, "13-18": 1},
        "items": [
          {"id": "STR", "label": "力量", "type": "score", "default": 10}
        ],
        "conditions": []
      },
      "metrics": {
        "fields": [
          {"id": "hp", "label": "生命", "type": "number", "default": 10}
        ]
      }
    },
    "areas": {
      "description": {
        "title": "描述",
        "type": "plain"
      }
    },
    "areaLayout": {
      "left": ["description"],
      "right": []
    }
  },
  "classes": [
    {
      "id": "warrior",
      "name": "战士",
      "areas": {
        "description": {
          "elements": [
            {"type": "text", "value": "你是**战士**。"}
          ]
        }
      }
    }
  ]
}
```

### 常见模式

#### 修改调整值罚款

```json
{
  "meta": {
    "header": {
      "stats": {
        "conditions": [
          {
            "id": "weak",
            "label": "虚弱",
            "states": 2,
            "boundStat": "STR",
            "effect": "modPenalty"
          }
        ]
      }
    }
  }
}
```

#### 自定义状态符号

```json
{
  "id": "exhausted",
  "label": "力竭",
  "states": 5,
  "symbols": ["□", "◔", "◐", "◕", "■"]
}
```

#### 等级锁定动作

```json
{
  "type": "moveList",
  "groups": [
    {
      "minLevel": 2,
      "maxLevel": 5,
      "label": "2-5级进阶动作",
      "items": [
        {"name": "猛攻", "text": "造成额外伤害"}
      ]
    }
  ]
}
```

#### 房规示例：删除职业

```json
{
  "classes": [
    {"id": "barbarian", "$delete": true}
  ]
}
```

#### 房规示例：修改职业负载

```json
{
  "classes": [
    {
      "id": "fighter",
      "areas": {
        "gear": {
          "rightStats": [
            {"key": "load", "formula": "15+力量"}
          ]
        }
      }
    }
  ]
}
```

#### 添加边栏资料章节

```json
{
  "meta": {
    "refSections": [
      {
        "id": "wizard_spells",
        "title": "法师法术书",
        "type": "moves",
        "importArea": "wizard"
      }
    ]
  },
  "reference": {
    "wizard_spells": {
      "moves": [],
      "groups": [
        {
          "key": "cantrips",
          "title": "戏法",
          "importGroup": "wizard-0",
          "moves": [
            {"name": "光亮术", "text": "创造光源"}
          ]
        },
        {
          "key": "level1",
          "title": "一环法术",
          "importGroup": "wizard-1",
          "moves": [
            {"name": "魔法飞弹", "text": "自动命中"}
          ]
        }
      ]
    }
  }
}
```