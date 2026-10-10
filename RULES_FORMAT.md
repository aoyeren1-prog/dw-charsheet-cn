# 规则 JSON 格式详解

面向想**导入 / 定制整套规则**的进阶用法。只想改几个字段的，直接看 `houserule-test.json` 即可。

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
  "compendium":   [ /* 概略职业 / 新种族，见第六节 */ ]
}
```

`classes` 是**必需**的（至少一个）。`basicMoves` / `specialMoves` / `spells` / `customMoves` / `compendium` 可为空数组或省略。

---

## 二、`meta` —— 规则配置

| 键 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `stats` | `string[]` | 六项属性名 | `["力量","敏捷","体质","智力","睿知","魅力"]` |
| `statsMode` | `string` | `"scores"`（3–18 数值，查 `modTable` 得调整值）或 `"modifiers"`（直接填调整值，隐藏 HP/负载公式） | `"scores"` |
| `modTable` | `object` | 数值区间 → 调整值 | `{"1-3":-3,"4-5":-2,"6-8":-1,"9-12":0,"13-15":1,"16-17":2,"18":3}` |
| `debilities` | `object` | 属性 → 异常状态名 | `{"力量":"虚弱","敏捷":"颤抖",...}` |
| `labels` | `object` | 所有界面文案（板块名、按钮、占位符） | 见下 |
| `advancedTiers` | `array` | 进阶动作分段，角色等级低于 `minLevel` 时该段隐藏 | `[{"key":"2-5","label":"进阶 · 2~5 级","minLevel":1},{"key":"6-10","label":"进阶 · 6~10 级","minLevel":6}]` |
| `spellSections` | `object` | 法术板块定义 | 见下 |
| `refSections` | `array` | 资料边栏页签与内容组织 | 见下 |
| `prepareCapFormula` | `string` | 准备上限公式 | `"施法等级+1"` |
| `statDistribution` | `array` | 初始属性分配（`"scores"` 模式） | `[16,15,13,12,9,8]` |
| `source` / `license` | `string` | 来源 / 许可元信息（可选，仅记录） | — |

### `labels` 常用键

`look`（外观）、`race`（种族动作）、`raceName`（种族）、`alignment`（阵营动作）、`alignmentNote`（动机）、`alignmentName`（阵营）、`starting`（起始动作）、`advanced`（进阶动作）、`customAdvanced`（自定义/其他动作组）、`gear`（装备）、`bonds`（羁绊）、`notes`（笔记）、`load`（负载上限）、`hpMax`（最大生命）、`hpCur`（当前生命）、`armor`（护甲）、`damage`（伤害）、`name`（姓名）、`level`（等级）、`xp`（XP）、`defaultFormula`（默认公式按钮）、`blank`（空占位）、`casterLevel`（施法等级）、`prepareCap`（准备上限）、`statDist`（初始分配）。

### `spellSections`

```jsonc
"spellSections": {
  "spellbook": {
    "title": "法术书",        // 角色卡里的板块标题
    "source": "法师法术",     // 资料边栏的来源标签
    "trigger": "法术书",      // 触发动作名：角色拥有该动作才显示此板块
    "spellClass": "wizard",   // 对应 spells 里的职业键
    "groups": ["戏法","等级1","等级3","等级5","等级7","等级9"]  // 分组顺序
  }
}
```

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

- `type:"groups"`：动作分类展示。`groups` 里 `key` 指向顶层某个动作数组，`label` 是分类标题（**`null` 则无标题、直接平铺**）。
- `type:"extension"`：扩展页 = 动作类别（`groups`，用法同 `type:"groups"`）+ 概略职业 / 新种族（`articles` 指向顶层某个 `compendium` 数组）。
- `type:"spells"`：法术列表（可导入到角色法术板块）。
- `type:"search"`：全库搜索。

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
    "intro": "你的负载上限是...",   // 可选
    "groups": [
      { "prompt": "选择你的武器：", "options": ["斧头 (近身, 1 重量)", "..."] }
    ]
  },
  "bonds": [                    // 羁绊模板（下划线是填空处）
    "_______________ 弱小而愚昧，但他也让我觉得有趣。"
  ],
  "advancedMoves": {            // 进阶动作，键对应 advancedTiers 的 key
    "2-5":  [ { "name":"如饥似渴", "text":"...", "requires":null, "replaces":null } ],
    "6-10": [ ]
  }
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
