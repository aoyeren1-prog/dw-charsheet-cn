# 规则 JSON 格式详解

面向想**导入 / 定制整套规则**的进阶用法。只想改几个字段的，直接看 `DW-HouseRuleTest.json` 即可。

---

## 一、顶层结构

```jsonc
{
  "meta":         { /* 规则配置，见第二节 */ },
  "classes":      [ /* 职业数组，见第三节 */ ],
  "basicMoves":   [ /* 基本动作，见第四节 */ ],
  "specialMoves": [ /* 特殊动作，见第四节 */ ],
  "spells":       { /* 法术，见第五节 */ },
  "customMoves":  [ /* 自定义动作，见第六节 */ ],
  "compendium":   [ /* 概略职业 / 新种族，见第六节 */ ],
  "tags":         [ /* 标签定义，见第七节 */ ]
}
```

`classes` 是**必需**的（至少一个）。`basicMoves` / `specialMoves` / `spells` / `customMoves` / `compendium` / `tags` 可为空数组或省略。

除上述固定键外，顶层还可加**任意自定义动作数组**（如 `"wizardDomains": [...]`），只要在 `meta.refSections` 里用 `type:"groups"` 的 `groups[].key` 指向它，就能作为资料边栏的一个分类展示。

---

## 二、`meta` —— 规则配置

| 键 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `stats` | `string[]` | 六项属性名 | `["力量","敏捷","体质","智力","睿知","魅力"]` |
| `statsMode` | `string` | `"scores"`（3–18 数值，查 `modTable` 得调整值）或 `"modifiers"`（直接填调整值，隐藏 HP/负载公式） | `"scores"` |
| `modTable` | `object` | 数值区间 → 调整值 | `{"1-3":-3,"4-5":-2,"6-8":-1,"9-12":0,"13-15":1,"16-17":2,"18":3}` |
| `debilities` | `object` | 属性 → 异常状态名 | `{"力量":"虚弱","敏捷":"颤抖",...}` |
| `labels` | `object` | 所有界面文案（板块名、按钮、占位符） | 见下 |
| `advancedTiers` | `array` | 进阶动作分段，角色等不在 `minLevel` 和 `maxLevel` 之间时该段置灰且不可交互 | `[{"key": "2only", "label": "仅第一次升级", "minLevel":2, "maxLevel":2}{"key":"2-5","label":"进阶 · 2~5 级","minLevel":2},{"key":"6-10","label":"进阶 · 6~10 级","minLevel":6}]` |
| `spellSections` | `object` | 法术板块定义 | 见下 |
| `refSections` | `array` | 资料边栏页签与内容组织 | 见下 |
| `prepareCapFormula` | `string` | 准备上限公式 | `"施法等级+1"` |
| `statDistribution` | `array` | 初始属性分配（`"scores"` 模式） | `[16,15,13,12,9,8]` |
| `statMin` / `statMax` | `number` | 属性输入框上下限（可选，覆盖模式默认值） | `-1` / `3` |
| `debilityPenalty` | `string` | 异常状态是否扣减显示调整值：`"on"`（扣 1）或 `"off"`（不扣） | `"off"` |
| `coins` | `string` | 金币字段开关：`"on"` / `"off"`（`"off"` 时不显示金币） | `"off"` |
| `heritage` | `object` | 血统区块配置（可选） | 见下 |
| `source` / `license` | `string` | 来源 / 许可元信息（可选，仅记录） | — |

### `labels` 常用键

`look`（外观）、`race`（种族动作）、`raceName`（种族）、`alignment`（阵营动作）、`alignmentNote`（动机）、`alignmentName`（阵营）、`starting`（起始动作）、`advanced`（进阶动作）、`customAdvanced`（自定义/其他动作组）、`gear`（装备）、`bonds`（羁绊）、`notes`（笔记）、`load`（负载上限）、`hpMax`（最大生命）、`hpCur`（当前生命）、`armor`（护甲）、`damage`（伤害）、`name`（姓名）、`level`（等级）、`xp`（XP）、`defaultFormula`（默认公式按钮）、`blank`（空占位）、`casterLevel`（施法等级）、`prepareCap`（准备上限）、`statDist`（初始分配）、`coins`（金币）。

### `spellSections`

```jsonc
"spellSections": {
  "spellbook": {
    "title": "法术书",        // 角色卡里的板块标题
    "source": "法师法术",     // 资料边栏的来源标签
    "trigger": "法术书",      // 触发动作名：角色拥有该动作才显示此板块
    "spellClass": "wizard",   // 对应 spells 里的职业键
    "groups": ["戏法","等级1","等级3","等级5","等级7","等级9"],  // 分组顺序
    "color": "#4a7fd4"        // 可选：该板块法术卡片左侧色条的颜色（CSS 颜色），不写则无色条
  }
}
```

`color` 是可选字段，用于给该法术板块的动作卡片着上左侧色条——这样不同职业的法术可以有不同颜色（如法师蓝、牧师橙）。

### `refSections`（资料边栏页签）

每个元素一个页签，`type` 决定渲染方式：

```jsonc
"refSections": [
  { "id": "moves", "title": "通用动作", "type": "groups", "groups": [
      { "key": "basicMoves",   "label": "基本动作" },
      { "key": "specialMoves", "label": "特殊动作" }
  ]},
  { "id": "extension", "title": "扩展", "type": "extension", "groups": [
      { "key": "customMoves", "label": "自定义动作" }
  ], "articles": "compendium" },
  { "id": "spells", "title": "法术列表", "type": "spells" },
  { "id": "search", "title": "资料速查", "type": "search" }
]
```

- `type:"groups"`：动作分类展示。`groups` 里 `key` 指向顶层某个动作数组，`label` 是分类标题（**`null` 则无标题、直接平铺**）。组可加 `importable:true`，为该组每个动作显示「＋导入」按钮（导入为角色的自定义/导入动作）。
- `type:"extension"`：扩展页 = 动作类别（`groups`，用法同 `type:"groups"`）+ 概略职业 / 新种族（`articles` 指向顶层某个 `compendium` 数组）。
- `type:"tags"`：标签列表。显示顶层 `tags` 数组中定义的所有标签，按 `category` 分组，展示标签颜色和描述。
- `type:"spells"`：法术列表（可导入到角色法术板块）。
- `type:"search"`：全库搜索。

### `heritage`（血统区块）

可选。配置一个「血统」区块：标题 + 可标记格 + 可写动作 + 规则说明（含可选的「升级」解锁开关）。

```jsonc
"heritage": {
  "title": "血统",                                   // 区块标题
  "note": "每次聚会开始时……标记一个血统格……",      // 规则说明（markdown，不含升级段）
  "upgradePrompt": "当你升级时……你可以选择：",        // 升级开关的提示（可选）
  "upgradeEffect": "获得第三个血统格……"               // 升级开关勾选后的效果文本（可选）
}
```

- 区块默认渲染 **2 个可标记格 + 2 条可写动作**；勾选 `upgradePrompt`/`upgradeEffect` 定义的「升级」开关后，显示第 3 格 + 第 3 条动作。
- 查看模式下，可标记格仍可标记/擦除；「升级」开关仅编辑模式可改。

---

## 三、职业 `classes[]`

```jsonc
{
  "id": "barbarian",            // 必需，唯一标识，英文小写
  "name": "野蛮人",             // 必需，职业名
  "intro": "简介（可省略）",
  "hp": "6+体质",               // 生命公式（见第八节）
  "damage": "d6",
  "load": "9+力量",             // 负载公式
  "statNote": "16 (+2), 15 (+1), ...",   // 属性分配提示（可选，纯展示）
  "names": [                    // 名字/称号建议（可选）
    { "race": "",     "names": ["戈姆","西易",...] },
    { "race": "称号", "names": ["光荣的","饥饿的",...] }
  ],
  "look": [                     // 外观选项，二维数组，每组一组选项
    ["痛苦的眼神","着魔的眼神","狂野的眼神","被遮蔽的双眼"],
    ["强壮肌肉","长腿","骨瘦如柴的身躯","柔软的身躯"]
  ],
  "racialMoves": [              // 种族动作
    { "race": "化外之民", "moves": [ { "name":"化外之民", "text":"..." } ] }
  ],
  "startingMoves": [            // 起始动作
    { "name":"重装上阵", "text":"...", "replaces":"无拘无束" }
  ],
  "alignment": [                // 阵营 / 动机
    { "name":"混乱", "text":"你远离文明世界的习俗常规。" }
  ],
  "gear": {
    "groups": [
      { "prompt": "你起始拥有……（装备说明；无 options 的组只显示这段提示）", "options": [] },
      { "prompt": "选择你的武器：", "options": ["斧头 (近身, 1 重量)", "..."] }
    ]
  },
  "bonds": [                    // 羁绊模板（下划线是填空处）
    "_______________ 弱小而愚昧，但他也让我觉得有趣。"
  ],
  "advancedMoves": {            // 进阶动作，键对应 advancedTiers 的 key
    "2-5":  [ { "name":"如饥似渴", "text":"...", "requires":null, "replaces":null } ],
    "6-10": [ ]
  },
  "questions": [                // 「问自己的问题」（可选）：笔记栏下方的角色塑造提示
    "你身上的哪种举止习惯，最明显地让你显得像个外来者？"
  ]
}
```

---

## 四、动作（move）

动作对象（出现在 `startingMoves` / `racialMoves[].moves` / `advancedMoves` / `basicMoves` / `specialMoves`）：

```jsonc
{
  "name": "重装上阵",
  "text": "你可以无视你所穿戴防具的{笨重}标签。",   // 支持标记语法（见第七节）
  "requires": "某前置动作",        // 可选：前置动作名，字符串或数组
  "replaces": "某被替换动作"       // 可选：互斥动作名，字符串或数组
}
```

- `requires`：声明「必须先有某动作」。
- `replaces`：声明「与某动作互斥」，选这个会取消那个（如野蛮人「重装上阵 ↔ 无拘无束」）。

---

## 五、法术 `spells`

按职业分页，每页是法术数组：

```jsonc
{
  "wizard": [ { "group":"戏法", "name":"光亮术", "text":"..." } ],
  "cleric": [ { "group":"祷念", "name":"圣疗", "text":"..." } ]
}
```

`group` 对应 `meta.spellSections` 里的 `groups`；`spellClass` 对应页键（`"wizard"` / `"cleric"`）。

---

## 六、扩展内容 `customMoves` / `compendium`

房规常用的三种「额外动作」都进「扩展」页签。

### `customMoves` —— 自定义动作

普通动作数组，作为「扩展」页的一个类别展示：

```jsonc
"customMoves": [
  { "name":"摆荡突袭", "text":"当你嘴里咬着弯刀…掷+敏捷。\n✴掷出10+…" }
]
```

要在「扩展」页加更多类别，就往 `meta.refSections` 里那个 `type:"extension"` 的 `groups` 数组加 `{ "key":"顶层键", "label":"类别名" }`。

### `compendium` —— 概略职业 / 新种族

两者共用同一结构：一个「条目」= 标题 + 若干**块**，块按 `kind` 区分，可按任意顺序排列：

```jsonc
"compendium": [
  {
    "id": "automaton-tinkerer",          // 唯一标识
    "title": "概略职业：机关人修补匠",
    "blocks": [
      { "kind":"text", "text":"如果你身为机关人…" },
      { "kind":"move", "name":"模组化机壳", "text":"当你扎营…" },
      { "kind":"text", "text":"一旦你获得…视为进阶动作：" },
      { "kind":"move", "name":"集成武装", "text":"…" },
      { "kind":"bond", "text":"________ 帮助我维持…" }
    ]
  }
]
```

| `kind` | 含义 | 渲染 |
|---|---|---|
| `text` | 段落说明 | 普通文本（支持标记语法） |
| `move` | 一个动作 | 动作卡片，带「＋导入」——点导入会进角色卡的**自定义进阶动作** |
| `bond` | 羁绊模板 | 纯文本展示，**不提供导入**（羁绊由玩家自己写） |

新种族和概略职业的区别只在 `title` 前缀和块内容，结构完全一致。

---

## 七、文本标记语法

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

可在顶层定义 `tags` 对象，按分类组织标签并指定颜色。未定义的标签使用默认灰色背景 + 黑色文字。指定的颜色会沿用到角色卡内的同名标签中（换句话说，如果你想在角色卡让某个标签显示成自定义颜色，就必须在这里定义这个标签）。

```jsonc
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

资料边栏新增"标签"页签，按分类折叠展示所有标签及其颜色。

---

## 八、公式语法

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

## 九、分层合并（规则栈）

工具内规则是**有序的规则栈**：第一份导入的是底层，之后导入的是规则包，上层覆盖下层。合并语义：

- 对象字段：上层覆盖下层同名键。
- 数组：按 `id` / `name` 匹配合并（同键覆盖、新键追加）。
- 对象字段值为 `null` → **删除**该字段。
- 数组条目 `{"id"/"name": "...", "$delete": true}` → **删除**匹配条目。

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

---

## 十、最小可用示例

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

---

## 十一、实验性功能（为 DW2 适配准备）

> ⚠️ **本节所有字段均为实验性功能**，是为适配未来的《地城世界 2》（DW2）规则而预先加入的。DW2 仍是 beta，这些字段的语义、命名、结构随时可能调整，请勿在要长期使用的正式规则里依赖它们。

### 1. Conditions 多态状态（取代 debilities）

| 键 | 类型 | 说明 |
|---|---|---|
| `meta.conditions` | `array` | 状态列表 `[{key, label, stat}]`，`stat` 是该状态对应的受损属性 |
| `meta.conditionStates` | `array` | 状态列表，**长度决定状态数**（`["clear","marked"]` 二态、`["clear","marked","locked"]` 三态） |

```jsonc
"conditions": [
  { "key":"exhausted",  "label":"力竭", "stat":"STR" },
  { "key":"frightened", "label":"受惊", "stat":"DEX" }
],
"conditionStates": ["clear","marked","locked"]
```

- 当 `meta.conditions` 存在时，角色卡异常状态改用这套多态状态（每个属性格子下方一个可循环点击的状态钮），**取代**旧的 `meta.debilities`（属性→状态名映射）。
- 状态数由 `conditionStates` 数组长度决定：DW1 二态、DW2 三态，未来四/五态也可扩。

### 2. Treasure Track（财富轨道）

| 键 | 类型 | 说明 |
|---|---|---|
| `meta.treasureTiers` | `array` | 阶层列表 `[{key, label, slots}]`，`slots` 是该阶层格数（`0` = 无格） |

```jsonc
"treasureTiers": [
  { "key":"broke", "label":"破产", "slots":4 },
  { "key":"poor",  "label":"贫穷", "slots":6 },
  { "key":"aristocratic", "label":"贵族", "slots":0 }
]
```

渲染为一条分段轨道：**点某格直接填充到该格、点已填充格清到该格**（双向），当前财富等级（已填满的最高阶层）标签高亮。格数、阶层全由数据决定。

### 3. Advancement（升级）

| 键 | 类型 | 说明 |
|---|---|---|
| `meta.advancement` | `string` | 一段**纯文本**（含 `[ ]` 勾选框），渲染成角色卡里的「升级」动作区域 |

```jsonc
"advancement": "当你升级时，HP +1，并选择以下一项：\n\n[ ] +1 任意属性（max +2）\n[ ] 获得一个 Path（含起始动作）\n\n从 5 级起，你还可以选择：\n[ ] Multiclass — 获得其他职业的 Path"
```

- 就是一个固定放着的「升级」动作（类似起始动作区域），文本里写升级规则和选项，勾选框复用动作文本的 `[ ]` 机制（`[x]` 表示勾选）。
- 「从 5 级起…」这类等级说明直接写进文本即可，**不做按等级的置灰 / 禁用**。

### 4. XP 轨道

| 键 | 类型 | 说明 |
|---|---|---|
| `meta.xpTrackSize` | `number` | XP 格数（配了才启用轨道，否则用数字输入框） |

```jsonc
"xpTrackSize": 5
```

XP 改为轨道（点击填充），**不自动归零、不自动升级**——升级由玩家自行决定。

### 5. Relationship Depth（关系深度）

| 键 | 类型 | 说明 |
|---|---|---|
| `meta.relationshipDepthMax` | `number` | 关系深度上限（默认 3） |

角色数据 `char.relationships` 是 `[{target, description, depth}]`，在羁绊（bonds）区域上方渲染：每条关系 = 目标输入框 + 描述输入框 + 一条 Depth 轨道（点击填充/清空）。

### 6. Origins（起源）

| 键 | 类型 | 说明 |
|---|---|---|
| `meta.origins` | `array` | **可选**。字段列表 `[{key, label, prefix, hint}]`；不配置则完全不显示起源板块 |

```jsonc
"origins": [
  { "key":"ancestry",  "label":"血缘", "prefix":"我是",   "hint":"如：矮人、精灵、人类……" },
  { "key":"community", "label":"社群", "prefix":"我来自", "hint":"如：佣兵团、商队……" }
]
```

- `prefix`：输入框预填文字（如「我是」），可编辑，未填写时显示。
- `hint`：输入框下方的灰色示例文字。
- 缺省 `prefix`/`hint` 时输入框为空、无示例。

### 7. 伤害开关

| 键 | 类型 | 说明 |
|---|---|---|
| `meta.showDamage` | `bool` | `false` 时属性栏不显示伤害（DW2 伤害由武器定义） |

### 8. 公式显示开关

| 键 | 类型 | 说明 |
|---|---|---|
| `meta.showFormula` | `bool` | `false` 时不显示 HP/负载的公式提示（DW2 的 HP/负重是写死的数字，非公式） |

公式支持 **`等级`** 关键词（取角色当前等级），如 `"hp":"10+等级"`。缺省（`true`）时公式提示照常显示。

### 9. 职业内覆盖进阶分段

`classes[].advancedTiers` 可覆盖全局 `meta.advancedTiers`（道途 / Path 是职业独有的）：

```jsonc
"advancedTiers": [
  { "key":"guardian", "label":"守护者 Path", "note":"以血肉之躯挡在同伴身前", "minLevel":1 }
],
"advancedMoves": { "guardian": [ ... ] }
```

`note` 是分组名下方的灰色说明文字（可选）。

### 10. Struggle（心结）

顶层 `struggles`（可导入的心结列表）+ `struggleHelp`（规则说明），在 `refSections` 里加一个 `type:"groups"` 页签：

```jsonc
"refSections": [
  { "id":"struggles", "title":"心结", "type":"groups", "groups":[
    { "key":"struggleHelp", "label":"怎么处理心结" },
    { "key":"struggles", "label":"心结列表", "importable":true, "kind":"struggle" }
  ]}
]
```

- `struggles` 里的每个心结是动作（`{name, text}`），`importable:true` 使其可导入。
- `kind:"struggle"` 让导入进角色卡的「心结」板块（而非自定义动作）。
