# 区域（Areas）格式规范

本文档描述区域的数据格式，包括区域标题和区域内容模板。

---

## 一、概述

区域系统允许通过 JSON 配置控制：
- **标题栏**：标题文本、说明文字、右对齐属性
- **内容模板**：plain 模板用于基础元素拼装（外观、起源、财富等）

### 数据层级

```jsonc
{
  "meta": {
    "areaLayout": {
      "left": ["look", "origins", "race", ...],
      "right": ["starting", "advanced", "advancement"]
    },
    "areas": {
      "origins": {
        "title": "起源",
        "body": {
          "type": "plain",
          "elements": [...]
        }
      },
      "gear": {
        "title": "装备",
        "rightStats": [...]
      }
    }
  },
  "classes": [
    {
      "id": "barbarian",
      "areas": {
        "look": {
          "title": "外观",
          "body": { "type": "plain", "elements": [...] }
        },
        "gear": {
          "rightStats": [{"key": "load", "formula": "8+力量"}]
        }
      }
    }
  ]
}
```

**合并规则**：
- 职业的 `areas[areaKey]` 会与 `meta.areas[areaKey]` **深度合并**
- `title`、`note`：职业值优先，不存在时使用通用值
- `body`、`rightStats`：递归合并，数组按 `key` 字段逐项合并
  - 职业元素覆盖同 `key` 的通用元素（浅合并字段）
  - 新 `key` 追加到数组末尾
  - 无 `key` 的元素直接追加
- 职业可以只写部分字段（如 `{body: {elements: [...]}}`），未写的字段继承通用定义

**合并示例**：
```jsonc
// meta.areas.look
{
  "title": "外观",
  "body": {
    "type": "plain",
    "elements": [
      {"type": "choices", "key": "group0", "value": []},
      {"type": "input", "key": "custom0", "tip": "自定义"}
    ]
  }
}

// classes[0].areas.look
{
  "body": {
    "elements": [
      {"key": "group0", "value": ["魁梧", "精瘦"]}
    ]
  }
}

// 合并结果
{
  "title": "外观",  // 继承 meta
  "body": {
    "type": "plain",  // 继承 meta
    "elements": [
      {"type": "choices", "key": "group0", "value": ["魁梧", "精瘦"]},  // value 被覆盖
      {"type": "input", "key": "custom0", "tip": "自定义"}  // 完全继承
    ]
  }
}
```

**渲染顺序**：
- `meta.areaLayout` 定义左右分栏和区域顺序
- 未列入 `areaLayout` 的区域不渲染
- 缺省时使用内置默认顺序

---

## 二、区域标题（meta.areas）

### 结构

```jsonc
{
  "meta": {
    "areas": {
      "<areaKey>": {
        "title": "区域标题",
        "note": "可选的说明文字",
        "rightStats": [
          {
            "key": "statKey",
            "label": "属性标签",
            "type": "number",
            "formula": "9+力量",
            "min": 0,
            "max": 100
          }
        ]
      }
    }
  }
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|-----|------|-----|------|
| `title` | string | 是 | 区域标题文本，显示为粗体大写 |
| `note` | string | 否 | 说明文字，紧跟在标题后，灰色小字显示 |
| `color` | string | 否 | 该区域动作卡左侧色条的颜色（任意 CSS 颜色值）；不写则不显示色条 |
| `rightStats` | array | 否 | 右对齐属性数组，详见下节 |

### 标准区域 key

以下是当前支持的标准区域（按在角色卡中的出现顺序）：

| areaKey | 说明 | 示例 title |
|---------|-----|-----------|
| `look` | 外观 | "外观" |
| `race` | 种族动作 | "种族动作" |
| `alignment` | 阵营动作 | "阵营动作" |
| `gear` | 装备 | "装备" |
| `bonds` | 羁绊 | "羁绊" |
| `notes` | 笔记 | "笔记" |
| `starting` | 起始动作 | "起始动作" |
| `advanced` | 进阶动作 | "进阶动作" |

---

## 三、rightStats 字段详解

### 结构

```jsonc
"rightStats": [
  {
    "key": "load",
    "label": "负载上限",
    "type": "number",
    "formula": "9+力量",
    "min": 0,
    "max": 100
  }
]
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|-----|------|-----|------|
| `key` | string | 是 | 数据绑定键，对应 `char[key]`，如 `load`、`hpMax` |
| `label` | string | 是 | 显示标签，如 "负载上限" |
| `type` | string | 是 | 输入类型：`"number"` / `"text"` / `"display"` |
| `formula` | string | 否 | 公式表达式，如 `"9+力量"`。有此字段时显示公式提示和「默认」按钮 |
| `min` | number | 否 | `type="number"` 时的最小值 |
| `max` | number | 否 | `type="number"` 时的最大值 |

### type 说明

| type 值 | 编辑模式 | 查看模式 |
|---------|---------|---------|
| `"number"` | 显示 `<input type="number">` | 显示数值（粗体） |
| `"text"` | 显示 `<input type="text">` | 显示文本（粗体） |
| `"display"` | 显示文本（粗体，不可编辑） | 显示文本（粗体） |

### formula 行为

- **有 `formula` 字段**：
  - 编辑模式：显示公式提示文本和可点击的「默认」按钮
  - 查看模式：显示公式提示文本（不可交互）
  - 点击「默认」按钮时，自动计算公式并填入 input
- **无 `formula` 字段**：
  - 不显示任何公式提示
  - 适用于固定值或玩家自定义的属性（如 UD 规则的负载上限）

### formula 可用的项

以 `+` 分隔，每一项可以是：

| 项 | 取值 |
|----|------|
| 整数 | 字面值，如 `9` |
| 属性名 | `meta.stats` 里的属性，取该属性调整值 |
| `等级` / `level` | 角色等级 |
| 其他 rightStat 的 `label` | 该数值的当前值 |

最后一条让一个数值可以引用另一个：例如「准备上限」的公式写 `施法等级+1`，即引用同区域名为「施法等级」的 rightStat。若公式里出现无法识别的项，该公式不生效（不显示提示）。

---

## 四、classes[].areas 字段

### 结构

```jsonc
{
  "classes": [
    {
      "id": "barbarian",
      "areas": {
        "gear": {
          "rightStats": [
            {"key": "load", "formula": "8+力量"}
          ]
        },
        "customArea": {
          "title": "怒气资源",
          "rightStats": [
            {"key": "rage", "label": "怒气", "type": "number", "min": 0}
          ]
        }
      }
    }
  ]
}
```

### 用途

职业可以：
1. **覆盖通用区域的部分字段**：如只覆盖 `gear.rightStats[0].formula`
2. **覆盖整个区域**：如覆盖 `title` 和 `note`
3. **添加职业特有区域**：如 `customArea`（未来扩展用）

### 合并示例

**通用配置**（meta.areas）：
```jsonc
"gear": {
  "title": "装备",
  "rightStats": [
    {"key": "load", "label": "负载上限", "type": "number", "formula": "9+力量", "min": 0}
  ]
}
```

**职业覆盖**（classes[].areas）：
```jsonc
"gear": {
  "rightStats": [
    {"key": "load", "formula": "8+力量"}
  ]
}
```

**最终合并结果**：
```jsonc
"gear": {
  "title": "装备",  // 继承通用
  "rightStats": [
    {
      "key": "load",
      "label": "负载上限",  // 继承通用
      "type": "number",     // 继承通用
      "formula": "8+力量",  // 职业覆盖
      "min": 0              // 继承通用
    }
  ]
}
```

---

## 五、完整示例

### 示例 1：基础配置（DW.json）

```jsonc
{
  "meta": {
    "areas": {
      "look": {
        "title": "外观"
      },
      "race": {
        "title": "种族动作",
        "note": "选择一项"
      },
      "alignment": {
        "title": "阵营动作",
        "note": "选择一项"
      },
      "gear": {
        "title": "装备",
        "rightStats": [
          {
            "key": "load",
            "label": "负载上限",
            "type": "number",
            "min": 0
          }
        ]
      },
      "bonds": {
        "title": "羁绊"
      },
      "notes": {
        "title": "笔记"
      },
      "starting": {
        "title": "起始动作"
      },
      "advanced": {
        "title": "进阶动作"
      }
    }
  },
  "classes": [
    {
      "id": "barbarian",
      "name": "野蛮人",
      "areas": {
        "gear": {
          "rightStats": [
            {"key": "load", "formula": "8+力量"}
          ]
        }
      }
    },
    {
      "id": "fighter",
      "name": "战士",
      "areas": {
        "gear": {
          "rightStats": [
            {"key": "load", "formula": "10+力量"}
          ]
        }
      }
    }
  ]
}
```

### 示例 2：无公式配置（UD.json）

```jsonc
{
  "meta": {
    "areas": {
      "gear": {
        "title": "装备",
        "rightStats": [
          {
            "key": "load",
            "label": "负载上限",
            "type": "number",
            "min": 0
            // 注意：无 formula 字段，不显示公式提示
          }
        ]
      }
    }
  },
  "classes": [
    {
      "id": "warrior",
      "areas": {
        "gear": {
          "rightStats": [
            {"key": "load"}
            // 不覆盖 formula（因为本来就没有）
          ]
        }
      }
    }
  ]
}
```

### 示例 3：房规覆盖（DW-HouseRuleTest.json）

```jsonc
{
  "meta": {
    "areas": {
      "race": {
        "title": "种族/背景",
        "note": "选择一项"
      },
      "alignment": {
        "title": "阵营/动机",
        "note": "选择一项"
      }
    }
  }
}
```

---

## 六、渲染效果

### 编辑模式

```
装备 选择你的起始装备                   负载上限 [9] (9+力量) [默认]
└─ title (粗体大写)
   └─ note (灰色小字)
                                      └─ rightStats (右对齐)
```

### 查看模式

```
装备 选择你的起始装备                   负载上限 9 (9+力量)
└─ title (粗体大写)
   └─ note (灰色小字)
                                      └─ rightStats (右对齐，不可编辑)
```

---

## 七、CSS 样式说明

相关 CSS 类（位于 `builder/app_template.html`）：

```css
/* h3 使用 flexbox，space-between 让左右两侧分散对齐 */
.pb-sec h3 {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

/* note 样式：灰色小字 */
.pb-sec h3 small {
  font-weight: 400;
  color: var(--ink-4);
  font-size: 11px;
  text-transform: none;
  margin-left: 4px;
}

/* rightStats 样式：灰色小字，右对齐 */
.pb-sec h3 .h3r {
  font-weight: 400;
  font-size: 11px;
  color: var(--ink-5);
  text-transform: none;
  letter-spacing: 0;
  white-space: nowrap;
}

/* rightStats 中的 input */
.pb-sec h3 .h3r input {
  border: 1px solid var(--line-5);
  border-radius: 3px;
  padding: 1px 3px;
  font-size: 12px;
  background: var(--paper);
  color: var(--ink);
  width: 52px;
  text-align: center;
}

/* rightStats 中的粗体数值 */
.pb-sec h3 .h3r b {
  color: var(--ink);
  font-weight: 700;
}
```

---

## 八、迁移工具

### 从旧格式迁移

运行迁移脚本将旧的 `meta.labels` 格式转换为新的 `meta.areas` 格式：

```powershell
python builder/migrate_area_headers.py
```

**迁移逻辑**：
1. 从 `meta.labels` 提取标题和 note（处理括号语法：`"种族动作（选择一项）"` → `title="种族动作"`, `note="选择一项"`）
2. 为 `gear` 区域生成 `rightStats`
3. 从 `classes[].load` 提取公式并生成 `classes[].areas.gear.rightStats`
4. 备份原文件为 `*.json.backup`
5. 原地替换规则文件

---

## 九、未来扩展方向

当前版本只实现了**区域标题**的模板化。后续可扩展：

1. **区域内容模板**（area body templates）
   - 将区域内容（如外观的多选框、装备的文本框）也模板化
   - 支持 `type: "checkboxGroup"`、`type: "textarea"` 等

2. **条件显示**
   - `rightStats` 支持 `minLevel`、`maxLevel` 字段
   - 只在特定等级范围显示某个属性

3. **多行 rightStats**
   - 支持在标题右侧显示多行属性（当前只支持单行）

4. **职业特有区域**
   - 完整支持职业添加新区域（如法术书、怒气池等）
   - 当前只有标题系统，内容渲染还是硬编码

5. **扩展到法术板块**
   - 法术板块（spellSectionHtml）也有类似的 h3r 结构
   - 可以统一到 areas 系统中

---

## 十、向后兼容性

**不兼容变更**：
- 本格式要求所有规则 JSON 必须使用 `meta.areas` 字段
- 不再支持从 `meta.labels` 自动回退（已移除 fallback 逻辑）
- 旧的 `classes[].load` 字段不再被代码读取（需迁移到 `classes[].areas.gear.rightStats`）

**迁移路径**：
1. 运行 `migrate_area_headers.py` 转换所有规则文件
2. 备份文件保存为 `*.json.backup`，可随时回滚

---

## 十一、API 参考

### 代码函数

**全局变量**：
```javascript
let AREAS = {};  // 从 META.areas 加载
```

**核心函数**：
```javascript
// 获取某个区域的完整配置（通用 + 职业覆盖）
function getAreaHeader(areaKey, cls)
// 返回: {title, note, rightStats}

// 渲染区域标题 HTML
function renderAreaHeader(areaKey, cls)
// 返回: "<h3>...</h3>"

// 渲染单个 rightStat
function renderRightStat(stat, cls)
// 返回: "负载上限 <input...> <span>公式</span>"

// 查找某个 statKey 的定义
function statDefByKey(statKey, cls)
// 返回: {key, label, type, formula, ...} 或 null

// 获取某个 stat 的公式
function statFormula(statKey, cls)
// 返回: "9+力量" 或 undefined

// 计算某个 stat 的默认值
function defaultStatValue(statKey, cls)
// 返回: number
```

---

## 七、Plain 区域模板

### 概述

`body.type = "plain"` 用于基础元素拼装型区域（外观、起源、财富等），通过 `elements` 数组声明式定义内容。

**适用场景**：
- 外观选项 + 自定义输入
- 起源输入框（血缘、社群、背景）
- 财富轨道
- 任何由 text、hint、choices、input、track 组成的区域

### 数据结构

```jsonc
{
  "meta": {
    "areas": {
      "origins": {
        "title": "起源",
        "body": {
          "type": "plain",
          "elements": [
            {"type": "input", "key": "ancestry", "label": "血缘", "prefix": "我是", "hint": "如：矮人、精灵"},
            {"type": "input", "key": "community", "label": "社群", "prefix": "我来自"}
          ]
        }
      },
      "treasure": {
        "title": "财富",
        "body": {
          "type": "plain",
          "elements": [
            {
              "type": "track",
              "key": "treasure",
              "view": "editable",
              "value": [
                {"label": "破产"}, {"slots": 4},
                {"label": "贫困"}, {"slots": 6},
                {"label": "适中"}, {"slots": 8},
                {"label": "富裕"}
              ]
            }
          ]
        }
      }
    }
  },
  "classes": [
    {
      "id": "fighter",
      "areas": {
        "look": {
          "title": "外观",
          "body": {
            "type": "plain",
            "elements": [
              {"type": "choices", "key": "group0", "layout": "break", "value": ["魁梧", "精瘦", "结实"]},
              {"type": "input", "key": "custom0", "tip": "自定义外观"},
              {"type": "choices", "key": "group1", "value": ["锐利的眼神", "冷漠的眼神"]},
              {"type": "input", "key": "notes", "tip": "其他外观描述"}
            ]
          }
        }
      }
    }
  ]
}
```

### 元素类型

#### 1. text - 纯文本/Markdown

```jsonc
{"type": "text", "value": "这是一段说明文字，支持 **加粗** 和 `{标签}` 以及 [ ] 勾选框。"}
```

| 字段 | 必需 | 说明 |
|------|------|------|
| `value` | 是 | Markdown 文本，经 `markdownToHtml` + `applyBoxes` 处理 |
| `key` | 否 | 勾选框状态存储键，缺省时用元素序号 |

**特性**：
- 支持 `{标签}` 渲染为带颜色的标签
- 支持 `[ ]` / `[x]` 渲染为可交互勾选框，状态存入 `char.plainAreas[areaKey][key]`

---

#### 2. hint - 灰色提示文字

```jsonc
{"type": "hint", "value": "这是一条编辑模式下的提示，查看模式隐藏。"}
```

| 字段 | 必需 | 说明 |
|------|------|------|
| `value` | 是 | 提示文本，支持 Markdown |

**行为**：
- 编辑模式：显示为 `.hint`（灰色小字）
- 查看模式：隐藏

---

#### 3. choices - 多选框组

```jsonc
{"type": "choices", "key": "physique", "layout": "break", "value": ["魁梧", "精瘦", "结实", "苗条"]}
```

| 字段 | 必需 | 说明 |
|------|------|------|
| `key` | 是 | 存储键，值为数组 `char.plainAreas[areaKey][key] = ["魁梧", "结实"]` |
| `value` | 是 | 选项列表 `string[]` |
| `layout` | 否 | `"break"`（纵向，默认）或 `"line"`（横向） |
| `view` | 否 | `"editable"` 时查看模式仍可交互（见下文） |

**行为**：
- 编辑模式：所有选项可见，可勾选多个
- 查看模式：只显示已选项，不可勾选（除非 `view: "editable"`）
- 横向布局用 `.addrow` 容器，纵向直接输出 `.opt` 列表

---

#### 4. input - 输入框

```jsonc
{"type": "input", "key": "ancestry", "label": "血缘", "prefix": "我是", "tip": "占位符", "hint": "如：矮人、精灵"}
```

| 字段 | 必需 | 说明 |
|------|------|------|
| `key` | 是 | 存储键，值为字符串 `char.plainAreas[areaKey][key] = "矮人"` |
| `label` | 否 | 行首标签（加粗，带冒号） |
| `prefix` | 否 | 新卡时的预填默认值（与 view 无关） |
| `tip` | 否 | 输入框 placeholder（灰色提示） |
| `hint` | 否 | 输入框下方的小字说明（`.origin-hint`） |
| `view` | 否 | `"editable"` 时查看模式仍可编辑（见下文） |

**行为**：
- 编辑模式：`<div class="origin-line"><div class="origin-row"><b>标签</b>：<input></div><div class="origin-hint">提示</div></div>`
- 查看模式：`<div class="origin-line"><b>标签</b>：值</div>`，值为空则不显示该行（除非 `view: "editable"`）

---

#### 5. track - 轨道

```jsonc
{
  "type": "track",
  "key": "treasure",
  "view": "editable",
  "value": [
    {"label": "破产"},
    {"slots": 4},
    {"label": "贫困"},
    {"slots": 6}
  ]
}
```

| 字段 | 必需 | 说明 |
|------|------|------|
| `key` | 是 | 存储键，值为整数索引 `char.plainAreas[areaKey][key] = 5` |
| `value` | 是 | 交替的 label 和 slots 数组 |
| `view` | 否 | `"editable"` 时查看模式仍可点击 |

**value 结构**：
- `{"label": "标签文本"}` - 渲染为 `<span class="trl">标签</span>`，当前段落的 label 带 `.on`
- `{"slots": 数量}` - 渲染为多个 `<button class="trc">`，小于当前值的格子带 `.on`

**行为**：
- 编辑模式：可点击格子前进/后退
- 查看模式：显示但不可点击（除非 `view: "editable"`）
- 点击格子 N：当前值 < N+1 时前进到 N+1，否则后退到 N

---

### view 字段

`view: "editable"` 用于标记"查看模式下仍可交互"的元素，典型场景是财富轨道。

| 元素类型 | 默认行为（查看模式） | `view: "editable"` |
|---------|---------------------|-------------------|
| `text` | 正常显示 | 同左（无差别） |
| `hint` | 隐藏 | 同左（无差别） |
| `choices` | 只显示已选项，不可勾选 | 全部选项可见且可勾选 |
| `input` | 纯文本行，值为空则不显示 | 保持输入框，可编辑 |
| `track` | 显示但不可点击 | 可点击 |

**示例**：
```jsonc
// 财富轨道在查看模式下仍可点击
{"type": "track", "key": "treasure", "view": "editable", "value": [...]}
```

---

### 数据存储

所有 plain 元素的值统一存储在 `char.plainAreas`：

```javascript
char.plainAreas = {
  "origins": {
    "ancestry": "矮人",
    "community": "铁山氏族"
  },
  "look": {
    "group0": ["魁梧", "结实"],
    "custom0": "左眼有疤",
    "notes": "总是穿着红斗篷"
  },
  "treasure": {
    "treasure": 5  // 轨道索引
  }
}
```

**读写接口**：
```javascript
plainGet(areaKey, key, defaultValue)  // 读取，带惰性初始化
plainSet(areaKey, key, value)         // 写入
```

---

### 职业覆盖

外观选项通常按职业不同，写在 `classes[].areas.look.body`：

```jsonc
{
  "classes": [
    {
      "id": "fighter",
      "areas": {
        "look": {
          "title": "外观",
          "body": {
            "type": "plain",
            "elements": [
              {"type": "choices", "key": "group0", "value": ["魁梧", "精瘦", "结实"]},
              {"type": "input", "key": "custom0", "tip": "自定义"}
            ]
          }
        }
      }
    },
    {
      "id": "wizard",
      "areas": {
        "look": {
          "body": {
            "type": "plain",
            "elements": [
              {"type": "choices", "key": "group0", "value": ["苍老", "年轻", "神秘"]},
              {"type": "input", "key": "custom0", "tip": "自定义"}
            ]
          }
        }
      }
    }
  ]
}
```

---

### 完整示例

```jsonc
{
  "meta": {
    "areaLayout": {
      "left": ["look", "origins", "race", "alignment", "gear", "treasure", "bonds", "notes"],
      "right": ["starting", "advanced"]
    },
    "areas": {
      "origins": {
        "title": "起源",
        "body": {
          "type": "plain",
          "elements": [
            {"type": "hint", "value": "描述你的出身和过去。"},
            {"type": "input", "key": "ancestry", "label": "血缘", "prefix": "我是", "hint": "如：矮人、精灵、人类"},
            {"type": "input", "key": "community", "label": "社群", "prefix": "我来自", "hint": "如：佣兵团、商队、学者团"},
            {"type": "input", "key": "background", "label": "背景", "prefix": "我曾是"}
          ]
        }
      },
      "treasure": {
        "title": "财富",
        "body": {
          "type": "plain",
          "elements": [
            {
              "type": "track",
              "key": "treasure",
              "view": "editable",
              "value": [
                {"label": "破产"}, {"slots": 4},
                {"label": "贫困"}, {"slots": 6},
                {"label": "适中"}, {"slots": 8},
                {"label": "富裕"}
              ]
            }
          ]
        }
      }
    }
  },
  "classes": [
    {
      "id": "fighter",
      "areas": {
        "look": {
          "title": "外观",
          "body": {
            "type": "plain",
            "elements": [
              {"type": "choices", "key": "group0", "layout": "break", "value": ["魁梧的身材", "精瘦的身材", "结实的身材"]},
              {"type": "input", "key": "custom0", "tip": "自定义体型"},
              {"type": "choices", "key": "group1", "value": ["锐利的眼神", "冷漠的眼神", "愤怒的眼神"]},
              {"type": "input", "key": "custom1", "tip": "自定义眼神"},
              {"type": "input", "key": "notes", "tip": "其他外观特征"}
            ]
          }
        }
      }
    }
  ]
}
```

---

## 八、实现细节

### 渲染流程

```javascript
function renderArea(areaKey, cls, m) {
  const body = getAreaHeader(areaKey, cls).body;
  if (body && body.type === "plain") return renderPlainArea(areaKey, cls);
  // 否则走旧渲染函数 switch
}

function renderPlainArea(areaKey, cls) {
  const body = getAreaHeader(areaKey, cls).body;
  const elements = body.elements || [];
  const inner = elements.map((el, i) => {
    el._idx = i;
    const fn = PLAIN_RENDERERS[el.type];
    return fn ? fn(areaKey, el) : "";
  }).join("");
  return `<div class="pb-sec">${renderAreaHeader(areaKey, cls)}${inner}</div>`;
}
```

### 事件处理

**input 事件**：
```javascript
if (d.plain && d.plain.startsWith("input:")) {
  const [, areaKey, key] = d.plain.split(":");
  plainSet(areaKey, key, t.value);
  save();
}
```

**change 事件**：
```javascript
if (d.plain && d.plain.startsWith("choice:")) {
  const [, areaKey, key] = d.plain.split(":");
  let arr = plainGet(areaKey, key, []);
  if (t.checked) { if (!arr.includes(t.value)) arr.push(t.value); }
  else { arr = arr.filter(x => x !== t.value); }
  plainSet(areaKey, key, arr);
  save();
}
```

**click 事件**：
```javascript
if (d.plain && d.plain.startsWith("track:")) {
  const [, areaKey, key, idxStr] = d.plain.split(":");
  const idx = parseInt(idxStr);
  const cur = plainGet(areaKey, key, 0);
  plainSet(areaKey, key, (idx < cur) ? idx : (idx + 1));
  renderPlaybook();
  save();
}
```

---

## 九、moveList 区域模板

### 概述

`body.type = "moveList"` 用于动作列表型区域（种族、阵营、起始动作、进阶动作、心结等）。

**结构**：区域由若干 `groups`（分组）和／或 `moves`（无分组动作）组成，另可配若干 `buttons`。

### 数据结构

```jsonc
{
  "type": "moveList",
  "features": {
    "selectGroups": true,   // 分组带勾选框
    "selectMoves": true     // 动作带勾选框
  },
  "groups": [
    {
      "key": "2-5",
      "label": "进阶 · 2~5 级",
      "note": "可选说明",
      "minLevel": 2,
      "maxLevel": 5,
      "selectable": false,   // 可选：覆盖 features.selectGroups
      "moves": [
        { "name": "动作名", "text": "正文", "requires": "前置动作名", "replaces": "被替代动作名", "selectable": true }
      ]
    }
  ],
  "moves": [ /* 无分组动作，结构同上 */ ],
  "buttons": [
    { "label": "动作", "position": "global", "action": "addMove", "targetGroup": "custom" },
    { "label": "种族", "position": "global", "action": "addGroup" },
    { "label": "动作", "position": "inGroup", "action": "addMove" }
  ]
}
```

### 勾选框归属

勾选框的位置由两个独立开关决定，二者可同时为真：

| 字段 | 位置 | 说明 |
|------|------|------|
| `features.selectGroups` | `body.features` | 分组标题带勾选框，分组名可编辑 |
| `features.selectMoves` | `body.features` | 每个动作带勾选框 |
| `features.viewSelect` | `body.features` | 动作带勾选框，且查看模式下仍可勾选；未勾选的置灰而非隐藏 |
| `selectable` | 单个 group / move | 覆盖所在区域的对应开关 |

**额外规则**：带 `requires` 或 `replaces` 的动作本身即为选择项，无论 `selectMoves` 为何都带勾选框。

### boundMove：绑定动作

`features.boundMove` 填一个动作名。该动作未取得时，整个区域不渲染。

「取得」的判定与勾选框一致：该动作已被勾选，或它本身不带勾选框（属于默认获得）。

```jsonc
"features": { "boundMove": "法术书", "viewSelect": true }
```

法术板块即是此用法：取得「法术书」动作后，法术书区域才出现。

### viewSelect：查看模式可勾选

`features.viewSelect` 为真时，该区域的动作：

- 勾选框在**查看模式下依然可点**
- **未勾选的条目置灰**（而非隐藏），两种模式都如此

适用于需要频繁开关、且开关状态本身是角色卡一部分的条目，例如法术的「已准备 / 未准备」。

**各区域的实际配置**：

| 区域 | selectGroups | selectMoves | 效果 |
|------|-------------|-------------|------|
| `race` | `true` | — | 种族名带勾选框，下辖动作不带 |
| `alignment` | — | `true` | 每个阵营带勾选框 |
| `starting` | — | — | 默认获得；只有互斥／前置动作带勾选框 |
| `advanced` | — | `true` | 每个进阶动作带勾选框 |

### 查看模式可见性

统一规则：**带勾选框的条目须已勾选才显示，不带勾选框的常显**。

- 分组带勾选框且未勾选 → 整个分组隐藏
- 动作带勾选框且未勾选 → 该动作隐藏
- 动作不带勾选框 → 常显（起始动作里的默认动作）
- 分组内无可见动作，且分组自身不带勾选行 → 分组隐藏（空分组不占位）
- `viewSelect` 区域例外：未勾选的动作置灰显示而非隐藏
- `boundMove` 未取得 → 整个区域不渲染

### 字段说明

#### group

| 字段 | 必需 | 说明 |
|------|------|------|
| `key` | 是 | 分组标识，勾选状态与分组名覆盖都以此为键 |
| `label` | 否 | 分组标题（可编辑分组的初始名） |
| `note` | 否 | 分组标题下方的小字 |
| `minLevel` / `maxLevel` | 否 | 等级范围，超出则标题灰显、组内动作禁用 |
| `selectable` | 否 | 覆盖 `features.selectGroups` |
| `moves` | 否 | 该分组下的动作 |

#### move

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 是 | 动作名。规则里的动作以它作为勾选键，`requires` / `replaces` / `boundMove` 也按它引用 |
| `text` | 否 | 正文，支持 Markdown、`{标签}`、`[ ]` 勾选框 |
| `requires` | 否 | 前置动作名（字符串或数组），未满足时禁用 |
| `replaces` | 否 | 被替代动作名（字符串或数组），勾选本动作时自动取消对方 |
| `selectable` | 否 | 覆盖 `features.selectMoves` / `features.viewSelect` |

#### features

| 字段 | 说明 |
|------|------|
| `selectGroups` | 分组带勾选框 |
| `selectMoves` | 动作带勾选框 |
| `viewSelect` | 动作带勾选框，查看模式仍可勾选，未勾选置灰 |
| `boundMove` | 绑定动作名；该动作未取得时整个区域不渲染 |

#### button

| 字段 | 必需 | 说明 |
|------|------|------|
| `label` | 是 | 按钮文字，渲染为 `＋ {label}` |
| `position` | 是 | `global`（区域末尾）或 `inGroup`（分组内） |
| `action` | 是 | `addMove` 或 `addGroup` |
| `targetGroup` | 否 | `addMove` 的落点分组；省略时 `global` 按钮落到无分组列表，`inGroup` 按钮落到所在分组 |

**`targetGroup` 指向的分组不必预先存在**：数据里没有该分组时，点击按钮会自动建一个同 key 的自定义分组。因此 `advanced` 的 `targetGroup: "custom"` 不需要在 JSON 里声明「其他」分组；若已声明则沿用声明的 `label`。

反之，若某个自定义动作所属的分组后来从数据里被删掉，该动作不会消失，而是落到无分组列表里显示。

### 可编辑性

编辑模式下，**内置条目与自定义条目一样可改名、可改正文**；区别只在删除：

- 自定义动作 / 自定义分组：有 `✕` 删除按钮
- 内置动作 / 内置分组：无删除按钮（规则自带的内容不可删）

### 数据存储

```javascript
char.moveListSelections[areaKey]            // 已勾选条目的键：分组用 group.key，
                                            // 规则动作用 name，自定义动作用它自带的 id
char.moveListGroupNames["areaKey::groupKey"] // 分组名覆盖
char.moveListNames["areaKey::名或id"]        // 动作名覆盖
char.moveListTexts["areaKey::名或id"]        // 动作正文覆盖（含 [ ] 勾选状态）

customData.moveListMoves[classId][areaKey]   // 自定义动作 [{id, name, text, group}]
customData.moveListGroups[classId][areaKey]  // 自定义分组 [{key, label, moves}]
```

规则动作用 `name` 作勾选键，是因为 `requires` / `replaces` / `boundMove` 都按名字引用，必须一致；自定义动作用 `id`，所以同名（含两个都还没填名字的空动作）不会连带勾选，改名也不会丢勾选。

### 资料边栏导入

`refSections[].groups[].kind` **直接作为目标区域的 areaKey**，不需要额外的映射字段。

```jsonc
"refSections": [{
  "id": "struggles", "title": "心结", "type": "groups",
  "groups": [{ "key": "struggles", "label": "心结列表", "importable": true, "kind": "struggle" }]
}]
```

导入时：
1. 以 `item.kind` 为 areaKey 取该区域的 body
2. body 为 moveList → 写入该区域的自定义动作；来源带分组且本职业没有该分组时自动新建一个自定义分组
3. 否则回退到该类型的专用处理（法术、心结）

### 迁移

```powershell
python builder/migrate_to_movelist.py
```

脚本可重复执行：既迁移原始字段（`startingMoves` / `alignment` / `advancedMoves` / `racialMoves`），也修复已迁移但字段不对的数据（职业层残留的 `buttons`、旧的 `viewMode` / `editable`、缺失的 `selectGroups` / `selectMoves`）。

---

## 十、版本历史

- **v1.4** (2026-10-26)
  - 心结（struggle）迁入 moveList：标准动作区，动作默认获得、自定义动作可删
  - 升级（advancement）暂以一个不可删除的规则动作承载原整段文本，正文里的 `[ ]` 由 moveList 正文渲染支持（DW2 未定稿，待其形态明确后再决定是否给 plain 增加多勾选框元素）
  - 删除 `struggleHtml` / `advancementHtml`、`meta.advancement`、`char.struggle`、`char.advancementText` 及其事件分支
  - 动作卡色条改由区域的 `color` 字段声明，删除写死的「区域名 → 样式类」映射表 `mvKindClass` 及六个 `--bar-*` 变量
  - 迁移脚本会清理 `areaLayout` 里既无 `meta.areas` 定义、也无遗留渲染函数的悬空键
- **v1.3** (2026-10-26)
  - moveList 新增 `features.boundMove`（绑定动作未取得则整区不渲染）与 `features.viewSelect`（查看模式可勾选、未勾选置灰）
  - 自定义动作的勾选键改用它自带的 `id`，同名动作不再连带勾选；规则动作仍用 `name`（供 `requires` / `replaces` / `boundMove` 引用）
  - 修复 `deepMerge`：`undefined` 现在表示「无改动」而非覆盖为空，此前导致职业未覆盖的区域 body 丢失、整个区域不渲染
  - 法术板块迁入 moveList：每个板块一个区域，区域 key 取原 `spellClass`，施法等级／准备上限改用 `rightStats`
  - 删除 `meta.spellSections`、`meta.prepareCapFormula`、`meta.treasureTiers` 与全部法术专用代码
  - rightStat 的 `formula` 可引用其他 rightStat 的 `label`，取代原先 `施法等级` 的硬编码
  - 资料边栏法术条目的 `kind` 直接为 areaKey；分组名搜索改为遍历所有 moveList 区域
  - 移除角色卡头部的副标题（原先写死读取种族／阵营）
  - 缺省 `areaLayout` 改为按 `areas` 声明顺序，不再写死区域名
- **v1.2** (2026-10-26)
  - 新增 moveList 区域模板（`body.type = "moveList"`）
  - 勾选框归属由 `features.selectGroups` / `features.selectMoves` 两个独立开关决定，可被单个 group / move 的 `selectable` 覆盖
  - `requires` / `replaces` 为动作级字段，带其一者自动成为选择项
  - 统一的 `＋ {label}` 按钮模板，支持 `global` / `inGroup` 两种位置与 `targetGroup` 落点；`targetGroup` 指向的分组不存在时自动创建，分组被删后其动作落到无分组列表
  - 内置条目也可改名改正文；仅自定义条目可删除
  - 空分组不渲染
  - 资料边栏 `kind` 直接作为 areaKey，移除硬编码映射
  - 删除 `raceHtml` / `alignHtml` / `startingHtml` / `advHtml` 及其专用卡片函数与事件分支
- **v1.1** (2026-10-26)
  - 新增 Plain 区域模板（`body.type = "plain"`）
  - 支持 text、hint、choices、input、track 五种元素
  - 支持 `view: "editable"` 查看模式交互
  - 新增 `meta.areaLayout` 控制区域顺序
- **v1.0** (2026-10-26)
  - 初版发布
  - 支持 `meta.areas` 和 `classes[].areas`
  - 支持 title、note、rightStats

---

## 十一、fillbox / bonds / heritage 区域模板

这三类替代了原先 gear / notes / bonds / heritage 四个专用区域。角色数据统一存在 `char.areaData[areaKey]`，所以同一 type 可以有任意多个区域。

### fillbox

一个大文本框，可挂三类附件。替代原先的装备区与笔记区。

```jsonc
{
  "type": "fillbox",
  "resetOnClassChange": true,
  "counters": [{ "key": "coins", "label": "金币" }],
  "addCounter": true,
  "options": [{ "prompt": "选择你的防具：", "options": ["皮甲 (1 护甲)", "链甲 (2 护甲)"] }],
  "hints": ["你为什么离开家乡？"]
}
```

| 字段 | 说明 |
|------|------|
| `counters` | 声明式计数器，名字固定只读。`key` 为存储键，`label` 为显示名，`value` 为初始值 |
| `addCounter` | 为真时给出「＋ 计数器」按钮，玩家可自行添加名字可改、可删的计数器 |

**计数器在查看模式下同样可编辑**：数值、名字、「＋ 计数器」和删除键都保持启用。查看模式才是实际用它计数的场合。声明式计数器的名字宽度由文本决定（名字后留 5px 间隙再接输入框）；玩家添加的计数器因为名字长度未知，名字框会撑满半行。
| `options` | 选项组。每组一个 `prompt` 和若干 `options`，编辑模式下每项前有 ＋ 按钮，点击把该项文本追加进文本框 |
| `hints` | 文本框下方的提示句（灰色小字） |
| `resetOnClassChange` | 为真时换职业清空本区域数据。内容来自职业的区域（装备、羁绊）需要它 |

存储：`{ text, counters: {key: 数值}, extra: [{name, value}] }`

### bonds

若干可增删的文本行，可挂「关系」。

```jsonc
{
  "type": "bonds",
  "resetOnClassChange": true,
  "lines": ["____ 曾与我并肩作战，我信任他。"],
  "relations": true,
  "relationDepth": 3
}
```

| 字段 | 说明 |
|------|------|
| `lines` | 初始文本行（通常写在 `classes[].areas` 里，按职业不同） |
| `relations` | 为真时附加「关系」：每条有目标、描述和一条深度轨道，另给出「＋ 关系」按钮 |
| `relationDepth` | 关系深度轨道的格数，缺省 3 |

存储：`{ lines: [...], relations: [{target, description, depth}] }`

### heritage

一组格子 + 等量的文本行 + 一张说明卡，整区可折叠。

```jsonc
{
  "type": "heritage",
  "boxes": 2,
  "boxesUpgraded": 3,
  "movePlaceholder": "血统动作",
  "note": "每次聚会开始时，标记一个血统格……",
  "upgradePrompt": "当你升级时，若你已达到 6 级或更高，你可以选择：",
  "upgradeEffect": "获得第三个血统格并写下第三个血统动作……"
}
```

| 字段 | 说明 |
|------|------|
| `boxes` | 格子数（同时决定文本行数） |
| `boxesUpgraded` | 勾选 `upgradeEffect` 后的格子数 |
| `movePlaceholder` | 文本行的占位提示 |
| `note` / `upgradePrompt` | 说明卡里的正文段落 |
| `upgradeEffect` | 说明卡末尾带一个勾选框的段落，勾选后格子数变为 `boxesUpgraded` |

存储：`{ boxes: [bool...], moves: [...], upgraded, hidden }`

### 事件编码

这三类共用一个属性 `data-area="<op>:<areaKey>[:<i>[:<j>]]"`，`op` 决定操作。新增 type 时沿用同一套分发。

---

## 十二、版本历史（续）

- **v1.5** (2026-10-26)
  - gear / notes 合并为 `fillbox`，bonds 与 heritage 各成一个 type；四个专用渲染函数全部删除
  - 角色数据统一存 `char.areaData[areaKey]`，移除 `char.gear` / `coins` / `notes` / `counters` / `bonds` / `relationships` / `heritage` 七个顶层字段
  - 金币统一为声明式计数器，`meta.coins` 开关、`COINS_ENABLED` 一并移除；名字宽度由文本决定，不与玩家添加的计数器强行对齐
  - 计数器（含「＋ 计数器」与删除键）在查看模式下保持可编辑
  - 关系成为 bonds 的可选附件，`meta.relationshipDepthMax` 下沉为 `relationDepth`
  - `meta.heritage` 下沉进区域 body，格子数由 `boxes` / `boxesUpgraded` 声明（原先写死 2→3）
  - 职业提问 `classes[].questions` 下沉为 fillbox 的 `hints`，装备选项组下沉为 `options`，羁绊模板下沉为 `lines`
  - 区域渲染改为派发表 `AREA_RENDERERS`，`renderArea` 不再有区域名 switch
  - 新增 `resetOnClassChange`，替代原先写死的「换职业清空装备和羁绊」

---

**相关文档**：
- `RULES_FORMAT.md` - 完整规则 JSON 格式文档（包含其他字段）
- `README.md` - 项目概览
