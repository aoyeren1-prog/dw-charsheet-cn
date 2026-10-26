# 区域（Areas）格式规范

本文档描述了区域标题的数据格式，用于统一渲染角色卡中的各个区域（外观、种族、阵营、装备、羁绊等）的标题栏。

---

## 一、概述

区域标题系统允许通过 JSON 配置控制每个区域的：
- **标题文本**（title）
- **说明文字**（note）
- **右对齐属性**（rightStats）

### 数据层级

```jsonc
{
  "meta": {
    "areas": {
      // 全局通用区域配置
      "look": { "title": "外观" },
      "gear": { "title": "装备", "rightStats": [...] }
    }
  },
  "classes": [
    {
      "id": "barbarian",
      "areas": {
        // 职业特定覆盖或新增区域
        "gear": { "rightStats": [{"key": "load", "formula": "8+力量"}] }
      }
    }
  ]
}
```

**合并规则**：
- 职业的 `areas[areaKey]` 会与 `meta.areas[areaKey]` 合并
- `title` 和 `note`：职业值优先，不存在时使用通用值
- `rightStats`：按 `key` 字段逐项合并，职业定义覆盖同 key 的通用定义，新 key 追加

---

## 二、meta.areas 字段

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

## 版本历史

- **v1.0** (2026-10-26)
  - 初版发布
  - 支持 `meta.areas` 和 `classes[].areas`
  - 支持 title、note、rightStats
  - 支持 type: number/text/display
  - 支持 formula 和「默认」按钮

---

**相关文档**：
- `RULES_FORMAT.md` - 完整规则 JSON 格式文档（包含其他字段）
- `README.md` - 项目概览
