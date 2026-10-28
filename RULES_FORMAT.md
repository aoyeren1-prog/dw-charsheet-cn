# 规则 JSON 格式详解

面向想**导入 / 定制整套规则**的进阶用法。只想改几个字段的，直接看 `DW-HouseRuleTest.json` 即可。

---

## 一、顶层结构

```jsonc
{
  "meta": { /* 全局配置，见第二节 */ },
  "classes": [ /* 职业数组，见第四节 */ ],
  
  // 资料边栏内容，键名由 meta.refSections 定义
  "basicMoves": [...],
  "spells": {...},
  "tags": [...]
}
```

**三类顶层字段**：

1. **`meta`**：全局配置（属性、区域、资料边栏定义、界面文案）
2. **`classes`**：职业数组，每个职业除 `id`/`name`/`hp`/`damage`/`load` 外，其余字段都是对 `meta` 的覆盖
3. **`refName`**：资料边栏内容，键名由 `meta.refSections[].groups[].key` 定义

> **TODO**：当前 `refName` 直接放在顶层，结构不够明确。后续可能会添加 `"reference"` 对象将所有资料内容框起来，如 `{"meta":{...}, "classes":[...], "reference":{"basicMoves":[...]}}`，但需考虑向后兼容。

> **TODO**：`classes` 字段名和 UI 中的"职业"文案是为《地城世界》硬编码的。不同 PbtA 规则对角色类别有不同命名。代码层面保持简洁的 `classes` 不变，但应在 `meta` 中增加可配置字段（如 `classLabel`、`classLabelPlural`），允许规则 JSON 自定义该术语在 UI 中的显示名称。

---

## 二、`meta` —— 规则配置

| 键 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `stats` | `string[]` | 六项属性名 | `["力量","敏捷","体质","智力","睿知","魅力"]` |
| `statsMode` | `string` | `"scores"`（3–18 数值，查 `modTable` 得调整值）或 `"modifiers"`（直接填调整值，隐藏 HP/负载公式） | `"scores"` |
| `modTable` | `object` | 数值区间 → 调整值 | `{"1-3":-3,"4-5":-2,"6-8":-1,"9-12":0,"13-15":1,"16-17":2,"18":3}` |
| `debilities` | `object` | 属性 → 异常状态名 | `{"力量":"虚弱","敏捷":"颤抖",...}` |
| `labels` | `object` | 界面文案 | 见下 |
| `areas` | `object` | **角色卡区域定义**（标题、栏位、内容模板） | 见第三节 |
| `areaLayout` | `object` | 区域的顺序与左右栏归属 | 见第三节 |
| `refSections` | `array` | 资料边栏页签与内容组织 | 见下 |
| `statNote` | `string` | 初始属性分配提示（纯展示文本，职业级可覆盖） | `"16(+2), 15(+1), ..."` |
| `statMin` / `statMax` | `number` | 属性输入框上下限（可选，覆盖模式默认值） | `-1` / `3` |
| `debilityPenalty` | `string` | 异常状态是否扣减显示调整值：`"on"`（扣 1）或 `"off"`（不扣） | `"off"` |
| `source` / `license` | `string` | 来源 / 许可元信息（可选，仅记录） | — |

### `labels` 常用键

目前共 8 个：`name`（姓名）、`level`（等级）、`xp`（XP）、`hpMax`（最大生命）、`hpCur`（当前生命）、`armor`（护甲）、`damage`（伤害）、`statDist`（初始分配提示的前缀）。

其他 labels 为旧结构弃用键，可无损删除。

### `refSections`

资料边栏页签定义。详见「资料边栏」章节（待补充）。

---

## 三、区域系统 `areas` / `areaLayout`

### 概述

#### 数据层级

配置分两层：`meta.areas` 定义通用结构，`classes[].areas` 按职业覆盖。

`meta.areaLayout` 显式声明哪些区域渲染及其顺序和栏位：
- **未定义 `areaLayout`**：渲染所有 `areas` 中的区域（按声明顺序放到左栏）
- **定义了 `areaLayout`**：只渲染列入的区域，未列入的不渲染（可用于房规隐藏某个区域）

**areaLayout 的合并行为**：职业层定义 `areaLayout` 时**完全覆盖**通用层，不定义时继承通用层。因此职业层若要改布局必须定义完整布局。

#### 合并规则

`meta.areas` 和 `classes[].areas` 按键深度合并。示例：

```jsonc
// meta.areas.gear
{"title": "装备", "rightStats": [{"key": "load", "label": "负载", "formula": "9+力量"}]}

// classes[0].areas.gear
{"rightStats": [{"key": "load", "formula": "8+力量"}]}

// 合并结果
{"title": "装备", "rightStats": [{"key": "load", "label": "负载", "formula": "8+力量"}]}
```

完整的合并规则见第十节「分层合并」。

### 区域定义 (`meta.areas`)

#### 结构

```jsonc
{
  "meta": {
    "areaLayout": {"left": ["look", "race", "gear"], "right": ["starting", "advanced"]},
    "areas": {
      "<areaKey>": {
        "title": "区域标题",
        "note": "可选说明",
        "color": "#c8a24b",
        "type": "plain",
        "rightStats": [...]
      }
    }
  }
}
```

#### 字段说明

| 字段 | 说明 |
|------|------|
| `title` | 区域标题，显示为粗体 |
| `note` | 标题后的小字说明 |
| `color` | 动作卡左侧色条颜色（CSS 颜色值），不写则无色条 |
| `type` | 模板类型：`plain` / `moveList` / `fillbox` / `bonds` / `heritage` |
| `rightStats` | 右对齐属性数组，见下节 |

其他字段（如 `elements` / `groups` / `moves`）由 `type` 决定，见各模板节。

### rightStats 详解

右对齐属性（负载、HP、施法等级等）。

```jsonc
"rightStats": [
  {"key": "load", "label": "负载", "type": "number", "formula": "9+力量", "min": 0}
]
```

| 字段 | 说明 |
|------|------|
| `key` | 存储键，对应 `char[key]` |
| `label` | 显示标签 |
| `type` | `"number"` / `"text"` / `"display"`（只读） |
| `formula` | 公式，如 `"9+力量"`；有此字段时显示公式提示和「默认」按钮 |
| `min` / `max` | `type="number"` 时的范围 |

**公式语法**：`+` 分隔的项，可以是整数、属性名（取调整值）、`等级`、其他 rightStat 的 `label`

### 内容模板总览

| type | 说明 | 主要字段 |
|------|------|---------|
| `plain` | 基础元素拼装（外观、起源、财富等） | `elements` |
| `moveList` | 动作区域（起始动作、进阶动作、法术等） | `groups`, `moves`, `buttons`, `selectMoves` |
| `fillbox` | 大文本框 + 计数器 + 选项（装备、笔记） | `counters`, `options`, `hints` |
| `bonds` | 可增删的文本行 + 关系（羁绊） | `lines`, `relations` |
| `heritage` | 格子 + 文本行 + 说明卡（血统） | `boxes`, `movePlaceholder` |

渲染时，`AREA_RENDERERS[area.type]` 选择对应函数。

### plain 模板

#### 概述

`type = "plain"` 用于外观、起源、财富等区域，通过 `elements` 数组声明式定义。

#### 结构

```jsonc
{
  "type": "plain",
  "elements": [
    {"type": "text", "value": "**外观**"},
    {"type": "choices", "key": "group0", "value": ["魁梧", "精瘦"]},
    {"type": "input", "key": "ancestry", "label": "血统", "prefix": "我是"},
    {"type": "track", "key": "treasure", "value": [{"label": "破产"}, {"slots": 4}]}
  ]
}
```

#### 元素类型

| type | 说明 | 主要字段 |
|------|------|---------|
| `text` | 纯文本，支持 Markdown | `value` |
| `hint` | 灰色小字 | `value` |
| `choices` | 选项组（多选） | `key`, `value`（数组）, `layout: "break"` |
| `input` | 输入框 | `key`, `label`, `prefix`, `hint` |
| `track` | 轨道（格子 + 标签） | `key`, `value`（节点数组） |

**公共字段**：
- `view`：控制查看模式下的行为
  - 省略：默认只读，所有可交互组件变为不可交互
  - `"editable"`：查看模式下仍可编辑
  - `"hide"`：查看模式下隐藏不渲染
  - `"grey"`：查看模式下整个元素置灰（opacity: 0.5）
  - `"hideUnselect"`：仅 `choices` 可用，查看模式下隐藏未选择的选项
  - `"greyUnselect"`：仅 `choices` 可用，查看模式下置灰未选择的选项

**track 节点**：`{"label": "标签"}` 或 `{"slots": N}`，轮流组成轨道。点击格子时后续格子自动清空。

### moveList 模板

#### 概述

`type = "moveList"` 用于起始动作、进阶动作、种族动作、法术等。支持分组、勾选、前置关系、自定义动作。

#### 结构

```jsonc
{
  "type": "moveList",
  "selectMoves": true,
  "groups": [
    {
      "key": "2-5",
      "label": "当你的等级升至2~5，从下列动作中选择：",
      "minLevel": 2,
      "moves": [
        {"name": "铁意志", "text": "..."},
        {"name": "强化防御", "text": "...", "requires": "铁意志"}
      ]
    }
  ],
  "moves": [...],
  "buttons": [{"label": "动作", "position": "global", "action": "addMove"}]
}
```

#### 字段说明

| 字段 | 说明 |
|------|------|
| `groups` | 分组数组 |
| `moves` | 无分组的动作数组 |
| `buttons` | 按钮数组 |
| `selectGroups` | 分组带勾选框 |
| `selectMoves` | 动作带勾选框 |
| `viewSelect` | 查看模式仍可勾选，未勾选置灰（用于 DW 的法术卡片） |
| `boundMove` | 绑定动作名，该动作未取得时整区不渲染 |

##### group

| 字段 | 说明 |
|------|------|
| `key` | 分组标识（勾选与覆盖的键） |
| `label` | 分组标题 |
| `minLevel` / `maxLevel` | 等级范围，超出则灰显禁用 |
| `selectable` | 覆盖 `selectGroups` |
| `moves` | 该分组下的动作 |

##### move

| 字段 | 说明 |
|------|------|
| `name` | 动作名（勾选键，`requires` / `replaces` / `boundMove` 按它引用） |
| `text` | 正文，支持 Markdown、`{标签}`、`[ ]` |
| `requires` | 前置动作名（字符串或数组），未满足时禁用 |
| `replaces` | 被替代动作名，勾选本动作时自动取消对方 |
| `selectable` | 覆盖 `selectMoves` / `viewSelect` |

##### button

| 字段 | 说明 |
|------|------|
| `label` | 按钮文字，渲染为 `＋ {label}` |
| `position` | `global`（区域末尾）/ `inGroup`（分组内） |
| `action` | `addMove` / `addGroup` |
| `targetGroup` | `addMove` 的落点分组，不存在时自动创建 |

### 职业层覆盖 (`classes[].areas`)

```jsonc
{
  "classes": [{
    "id": "barbarian",
    "areas": {
      "gear": {"rightStats": [{"key": "load", "formula": "8+力量"}]},
      "customArea": {"title": "怒气", "type": "plain", "elements": [...]}
    }
  }]
}
```

职业可以：
1. 覆盖通用区域的部分字段（如只改 `formula`）
2. 覆盖整个区域（如改 `title` 和 `note`）
3. 添加职业特有区域

### fillbox / bonds / heritage 模板

#### fillbox

一个大文本框 + 计数器 + 选项 + 提示。替代装备区与笔记区。

```jsonc
{
  "type": "fillbox",
  "resetOnClassChange": true,
  "counters": [{"key": "coins", "label": "金币", "value": 0}],
  "addCounter": true,
  "options": [{"prompt": "选择防具：", "options": ["皮甲", "链甲"]}],
  "hints": ["你为什么离开家乡？"]
}
```

#### bonds

若干可增删的文本行 + 关系。

```jsonc
{
  "type": "bonds",
  "resetOnClassChange": true,
  "lines": ["____ 曾与我并肩作战，我信任他。"],
  "relations": true,
  "relationDepth": 3
}
```

#### heritage

一组格子 + 文本行 + 说明卡，可折叠。

```jsonc
{
  "type": "heritage",
  "boxes": 2,
  "boxesUpgraded": 3,
  "movePlaceholder": "血统动作",
  "description": "每次聚会开始时…",
  "upgradePrompt": "当你升级时…",
  "upgradeEffect": "获得第三个格子…"
}
```

---

## 四、职业 `classes[]`

**职业自有字段**（不是覆盖行为）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 必需，唯一标识，英文小写 |
| `name` | string | 必需，职业名 |
| `intro` | string | 简介（可省略） |
| `hp` | string | 生命公式，如 `"6+体质"` |
| `damage` | string | 伤害骰，如 `"d6"` |
| `load` | string | 负载公式，如 `"9+力量"` |

**覆盖全局配置的字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `statNote` | string | 覆盖 `meta.statNote`，属性分配提示 |
| `names` | array | 覆盖全局名字列表（如果 `meta.names` 存在） |
| `areas` | object | 覆盖 `meta.areas` 中的特定区域，见第三节 |

**示例**：

```jsonc
{
  "id": "barbarian",
  "name": "野蛮人",
  "intro": "在荒野中长大的野蛮人...",
  "hp": "6+体质",
  "damage": "d10",
  "load": "8+力量",
  "statNote": "16 (+2), 15 (+1), 13 (+1), 12 (+0), 9 (+0), 8 (-1)",
  "names": [
    { "race": "", "names": ["戈姆", "西易", "斯德莫", "阿克蒂"] },
    { "race": "称号", "names": ["光荣的", "饥饿的", "坚定的"] }
  ],
  "areas": {
    "gear": {
      "rightStats": [
        {"key": "load", "formula": "8+力量"}
      ]
    },
    "starting": {
      "moves": [
        {"name": "重装上阵", "text": "...", "replaces": "无拘无束"}
      ]
    }
  }
}
```

**字段说明**：

职业定义中，`id`、`name`、`intro`、`hp`、`damage`、`load` 是职业自有的字段。

其他字段如 `statNote`、`names`、`areas` 都是对全局配置（`meta` 中对应字段）的覆盖行为：
- `statNote` 覆盖 `meta.statNote`
- `names` 覆盖 `meta.names`（如果全局定义了的话）
- `areas` 覆盖 `meta.areas` 中的特定区域

`areas` 字段用于职业特定的区域定制。职业可以：
1. 修改区域的部分字段（如改变负载公式）
2. 添加职业特有的动作或选项
3. 完全覆盖某个区域的内容

详见第三节的「职业层覆盖」小节。

---

## 五、动作（move）

动作对象（`areas[].moves` / `areas[].groups[].moves` / `refSections`自定义组别）：

```jsonc
{
  "name": "重装上阵",
  "text": "你可以无视你所穿戴防具的{笨重}标签。",   // 支持标记语法（见第八节）
  "requires": "某前置动作",        // 可选：前置动作名，字符串或数组
  "replaces": "某被替换动作"       // 可选：互斥动作名，字符串或数组
}
```

- `requires`：声明「必须先有某动作」。
- `replaces`：声明「与某动作互斥」，选这个会取消那个（如野蛮人「重装上阵 ↔ 无拘无束」）。

详见第三节的「moveList 模板」。

---

## 六、资料边栏 `refSections`

`meta.refSections` 定义资料边栏的页签结构。每个元素一个页签，`type` 决定渲染方式。

### 四种类型

```jsonc
"refSections": [
  { "id": "moves", "title": "通用动作", "type": "moves", "groups": [
      { "key": "basicMoves",   "label": "基本动作", "kind": "starting" },
      { "key": "specialMoves", "label": "特殊动作" }
  ]},
  { "id": "extension", "title": "扩展", "type": "extension", 
    "groups": [{ "key": "customMoves", "label": "自定义动作" }],
    "articles": "compendium" 
  },
  { "id": "tags",   "title": "标签",     "type": "tags" },
  { "id": "search", "title": "资料速查", "type": "search" }
]
```

| type | 说明 |
|------|------|
| `moves` | 动作分类展示，内容来自 `groups` |
| `extension` | `groups` + `articles` 的混合展示 |
| `tags` | 顶层 `tags` 的全部标签，按分类折叠 |
| `search` | 全库搜索 |

### `type: "moves"` —— 动作分类

通过 `groups` 数组组织动作内容。

**groups 字段**：

| 字段 | 说明 |
|------|------|
| `key` | 指向顶层的动作数组。支持**点分路径**，如 `"spells.wizard"` 取 `spells.wizard` |
| `label` | 分类标题。省略则无标题、直接平铺 |
| `kind` | **导入目标区域的 areaKey**。省略则该组只能看、不能导入 |

**导入机制**：
- `kind` 的值是 `meta.areas` 里的键
- 导入按钮出现的条件：该 areaKey 存在，且其 `type` 为 `moveList`
- 指向 `bonds`、`look` 等非 moveList 区域不会出现导入按钮
- 导入时将会检查该区域 `type` 是否为 `moveList`，以及 `boundMove` 是否已满足。

**自动分组**：
- 动作对象若带 `group` 字段（如法术的 `"戏法"`、`"等级1"`），会在该分类下自动分小节
- 导入时 `group` 会作为目标区域的分组 key

### `type: "extension"` —— 扩展内容

混合展示 `groups`（动作数组）和 `articles`（文章列表）。

**结构**：

```jsonc
{
  "type": "extension",
  "groups": [
    { "key": "customMoves", "label": "自定义动作", "kind": "starting" }
  ],
  "articles": "compendium"  // 指向顶层的文章数组
}
```

**groups**：普通动作数组，与 `type:"moves"` 的 `groups` 字段相同。

**articles**：指向顶层的文章数组（如 `compendium`）。每篇文章结构：

```jsonc
{
  "id": "undead",
  "title": "亡灵化",
  "importGroup": "亡灵化",  // 可选：导入后落进哪个分组
  "blocks": [
    { "kind": "text",  "text": "**说明文字**（纯文本块，不可导入）" },
    { "kind": "race",  "name": "不死之躯", "text": "你不需要进食…" },
    { "kind": "bonds", "text": "______ 承载着我生前的一段重要记忆。" }
  ]
}
```

**blocks 字段**：

| 字段 | 说明 |
|------|------|
| `kind` | 目标区域的 areaKey。`"text"` 为纯文本块，不可导入 |
| `name` / `text` | 动作内容（`kind` 不为 `"text"` 时） |
| `importGroup` | 可选，块级覆盖文章级的 `importGroup` |

**importGroup**：
- 导入动作时，指定落进目标区域的哪个分组
- 分组不存在时自动创建，排在已有分组**之后**
- 只对 `kind` 指向 `moveList` 区域的块有效
- 可写在文章级（所有块共用）或块级（覆盖文章级）

### `type: "tags"` —— 标签

按分类折叠展示标签。页签不写指向字段，数据取**与页签 `id` 同名的顶层键**：

```jsonc
"meta": {
  "refSections": [
    { "id": "tags", "title": "标签", "type": "tags" }   // 读顶层 tags
  ]
},
"tags": {
  "距离": [                   // 分类名（作为折叠组标题）
    {
      "name": "触及",         // 必需：标签名（与 {标签名} 匹配）
      "color": "#ecacac",    // 可选：背景色（CSS 颜色值）
      "textColor": "#fff",   // 可选：文字色（未设置则为黑色）
      "description": "需要接触到目标才能使用"  // 可选：说明文字
    }
  ],
  "通用": [
    { "name": "笨重", "description": "该装备笨重难用" }
  ]
}
```

可以有多个 tags 页签，各读各的数据块：`{"id": "gearTags", "type": "tags"}` 读顶层 `gearTags`。

**颜色生效范围**：所有 tags 页签的颜色定义汇总成一张**按标签名索引的全局表**，沿用到角色卡内的同名标签。详见第八节「文本标记语法」。

**同名冲突**：全局表只认标签名，不分页签也不分分类。两个页签给同名标签配了不同颜色时，以**后声明的页签**为准；该标签在两个页签的边栏里都显示这一个颜色。同一数据块内的同名标签在规则栈合并阶段就已按 `name` 归并，不会走到这一步。未写 `color` 的同名标签不会清掉已有颜色。

### `type: "search"` —— 搜索

全库搜索，可搜范围由数据决定：
- 职业动作
- 所有 `refSections` 的内容（`groups` 条目、`articles` 的每个块、纯文本块）
- 顶层 `tags`

能导入的内容在搜索结果里同样带导入按钮。

---

## 七、扩展内容 `customMoves` / `article`

### `customMoves` —— 自定义动作数组

普通动作数组，在 refSections 中通过 `type:"extension"` 的 `groups` 引用：

```jsonc
"customMoves": [
  { "name":"摆荡突袭", "text":"当你嘴里咬着弯刀…掷+敏捷。\n✴掷出10+…" }
]
```

### `article` —— 文章数组

文章列表，在 refSections 中通过 `type:"extension"` 的 `articles` 引用。每篇文章包含标题和若干块：

```jsonc
"compendium": [
  {
    "id": "undead",
    "title": "亡灵化",
    "importGroup": "亡灵化",
    "blocks": [
      { "kind": "text",  "text": "**说明文字**" },
      { "kind": "race",  "name": "不死之躯", "text": "你不需要进食…" },
      { "kind": "bonds", "text": "______ 承载着我生前的一段重要记忆。" }
    ]
  }
]
```

**字段说明**：

| 字段 | 说明 |
|------|------|
| `id` | 文章唯一标识 |
| `title` | 文章标题 |
| `importGroup` | 可选，导入后落进的分组名 |
| `blocks` | 块数组 |

**blocks 字段**：

| 字段 | 说明 |
|------|------|
| `kind` | 目标区域的 areaKey，或 `"text"`（纯文本块） |
| `name` | 动作名（`kind` 不为 `"text"` 时） |
| `text` | 内容 |
| `importGroup` | 可选，块级覆盖文章级 |

详见第六节「资料边栏」。

### 当前 moves 与 extension 的行为差异

| 项目 | `moves` | `extension` |
|------|---------|-------------|
| `kind` 定义位置 | 仅 `meta.refSections[].groups[].kind`，动作内不可定义 | 可在 `groups[].kind` 定义，也可在 `blocks[].kind` 覆盖 |
| 导入目的地分组 | 由动作内的 `group` 决定（强制创建同名组） | 由 `importGroup` 决定（文章级 / 块级） |
| 边栏内分组 | 由动作内的 `group` 决定（与导入分组同一个字段） | 由 `groups[].label` 决定，与 `importGroup` 分离 |
| `kind` 的其他作用 | 无 | 同时决定 block 的渲染样式：按导入目的地区域的 `type` 反推；目的地不存在时退化为纯文本 |

两种类别的 `kind` / `group` / `importGroup` 语义不一致，容易造成困惑。

> **TODO：计划中的重构**
>
> `extension` 本质上是 `moves` 的扩展，后续应合并进 `moves`，并全面修改 `refSections` 数据结构：
>
> 1. **`meta` 只定义页签**：`refSections[]` 仅保留 `id` / `title` / `type`，不再用 `groups` 划分页签内部区块。
> 2. **分组逻辑下移到内容侧**（届时位于 `reference` 内）：一个页签内可分多个 group，每个 group 内既可放动作（move）也可放文章（article）。
> 3. **动作的 `kind`**：支持 group 级定义 + 动作级覆盖；并把 `group` 与 `importGroup` 分离——`group` 只控制边栏内分组，`importGroup` 只控制导入目的地所在组（与现在的文章行为一致）。
> 4. **文章的 `kind`**：不再用同一个字段兼管导入目的地和 block 渲染类别。现在的逻辑是从角色卡区域定义反推边栏样式，依赖外部内容定义，不可靠。
>
> 重构后这一章可整体废弃。

---

## 八、文本标记语法

动作 / 羁绊 / 外观备注等**做渲染**的文本里可用：

| 语法 | 效果 |
|---|---|
| `{标签名}` | 高亮标签（如 `{笨重}`、`{远程}`） |
| `**粗体**` | 加粗 |
| `*斜体*` | 斜体 |
| 行首 `- ` 或 `* ` | 无序列表项 |
| 空行 | 分段 |
| `[ ]` / `[x]` | 勾选框（查看模式可点击切换） |

> 装备（gear）和笔记（notes）栏当前**不做渲染**，是纯文本，`{标签名}` 会原样显示——一个不好修的缺陷（README「待办事项」）。

### 标签颜色定义

未定义的标签使用默认灰色背景 + 黑色文字。资料边栏 `tags` 类别内容里指定的颜色会沿用到角色卡内的同名标签——想让某个标签显示成自定义颜色，就必须在那里定义它。结构见第六节的 `type: "tags"`。

---

## 九、公式语法

`hp` / `load` / `prepareCapFormula` 用 `+` 连接若干项：

- **数字**：直接相加。
- **属性名**（`meta.stats` 里的）：加该属性当前值。
- **`施法等级`**（`labels.casterLevel`）：加施法等级（用于 `prepareCapFormula`）。

```jsonc
"hp": "6+体质"            // → 6 + 体质值
"prepareCapFormula": "施法等级+1"   // → 施法等级 + 1
```

`statsMode:"modifiers"` 时，`hp` / `load` 只取 `+` 前的数字（属性调整值直接手填）。

---

## 十、分层合并（规则栈）

工具内规则是**有序的规则栈**：第一份导入的是底层，之后导入的是规则包，上层覆盖下层。合并语义：

- 对象字段：上层覆盖下层同名键。
- 对象字段值为 `null` → **删除**该字段。
- 数组，**每一项都能取到 `id` / `name` / `key`** 时：按该键匹配合并（同键深合并、新键追加）。`classes`、`basicMoves`、区域的 `groups` / `elements` 走这条。
- 数组，**存在取不到键的项**时（字符串、数字、嵌套数组、无键对象）：上层**整体覆盖**下层。`stats`、`look`、`bonds.lines`、`gear.options`、`buttons` 走这条——这类数组没有「同一项」的概念，逐项追加会导致上层每叠一次就翻倍。
- 数组条目 `{"id"/"name"/"key": "...", "$delete": true}` → **删除**匹配条目。
- 空数组 `[]` 视为「无改动」，不会清空下层。要清空请用 `null`。

`meta.areaLayout` 的 `left` / `right` 是例外：它们是**顺序声明**，条目指向别处定义的区域 key，而不是值列表。所以按序列合并——保留下层顺序，只把上层新增的 key 插进去（插在「它后面第一个两边都有的 key」之前，没有这种锚点则接到末尾）。

这样房规只想插一个区域时，不必重抄整份布局：

```jsonc
"areaLayout": { "left": ["heritage", "gear", "bonds", "notes"] }
```

上面这段的实际含义是「把 heritage 插到 gear 之前」，其余区域的顺序沿用下层。要彻底重排，先用 `null` 删掉该侧再重写。

一个「只改少数字段 + 删一个职业」的房规包示例：

```jsonc
{
  "meta": { "statsMode": "modifiers", "labels": { "race": "背景" } },
  "classes": [ { "id": "barbarian", "$delete": true } ]
}
```

也可用脚本把组合固化成一份稳定规则：

```powershell
python builder\merge_rules.py data.json my-classpack.json -o merged.json
```

> TODO：已过时，需重写，此外 merge_rules.py 未经过测试，可能现在也已不能用了……

---

## 十一、最小可用示例

```jsonc
{
  "meta": {
    "stats": ["力量","敏捷","体质","智力","睿知","魅力"],
    "statsMode": "scores",
    "modTable": {"1-3":-3,"4-5":-2,"6-8":-1,"9-12":0,"13-15":1,"16-17":2,"18":3},
    "debilities": {"力量":"虚弱","敏捷":"颤抖","体质":"患病","智力":"晕眩","睿知":"困惑","魅力":"疤痕"}
  },
  "classes": [
    {
      "id": "warrior", "name": "战士", "hp": "6+体质", "damage": "d6", "load": "9+力量",
      "look": [["炯炯有神","疲惫不堪"]],
      "startingMoves": [ { "name":"挥砍", "text":"对近身敌人造成伤害。" } ],
      "alignment": [ { "name":"善良", "text":"保护弱者。" } ],
      "gear": { "groups": [ { "prompt":"选择武器：", "options":["长剑","战斧"] } ] },
      "bonds": ["_______________ 与我并肩作战。"],
      "advancedMoves": { "2-5": [ { "name":"猛攻", "text":"造成额外 1d4 伤害。" } ], "6-10": [] }
    }
  ],
  "basicMoves": [ { "name":"砍劈", "text":"对敌人造成伤害。" } ],
  "specialMoves": [ { "name":"临死一息", "text":"濒死时掷一骰。" } ],
  "spells": {}
}
```

> TODO：结构早就不是这样子了，这一节需重写

---

## 十二、实验性功能

> ⚠️ 为适配未来的《地城世界 2》（DW2）规则而预先加入的功能。DW2 仍是 beta，这些字段的语义、命名、结构随时可能调。

### Relationship 关系

在 Areas 的 bonds 类型中：

```jsonc
{
  "type": "bonds",
  "resetOnClassChange": true,
  "lines": ["____ 曾与我并肩作战，我信任他。"],
  "relations": true, // 打开“关系”功能
  "relationDepth": 3 // 关系深度
}
```

角色数据 `char.relationships` 是 `[{target, description, depth}]`，在羁绊（bonds）区域上方渲染：每条关系 = 目标输入框 + 描述输入框 + 一条 Depth 轨道（点击填充/清空）。