# 地城世界 · 车卡工具（Dungeon World Digital Character Sheet CN）

纯前端、可离线使用的 TRPG 角色卡工具（简体中文），通过规则 JSON 支持《地城世界》(Dungeon World) 与《无限地城》(Unlimited Dungeons) 两种规则。单个 HTML 文件，`file://` 双击打开即可。

- 左侧角色卡 + 右侧资料边栏
- 编辑 / 查看双模式，浏览器打印导出 PDF
- 规则分层：底层规则 + 支持房规 JSON 叠加，上层覆盖下层
- 全部板块名、动作分类、属性模型等由规则 JSON 的 `meta` 驱动（去硬编码）

---

## 快速开始

1. 下载 `地城世界车卡工具.html`，以及规则数据（`DW.json` 地城世界 / `UD.json` 无限地城），或在 **Releases** 页面获取
2. 双击打开 HTML，点右上角 **「📥 规则」** 选择对应的规则 JSON（如 `DW.json` 或 `UD.json`）。
3. 开始车卡。规则会自动存进浏览器，刷新后无需重新导入。

> 角色数据存 `localStorage`，换浏览器/清缓存会丢；重要角色请用工具内「导出」备份成 JSON。

---

## 规则 JSON 格式

规则数据是一个 JSON 文件，顶层含 `meta`（配置）、`classes`（职业）、资料内容键（如 `basicMoves`、`spells` 等）。所有板块名、动作分类、属性模型都由 `meta` 驱动。

- 只想**改几个字段**：看 `DW-HouseRuleTest.json` 示例即可。
- 想**导入 / 定制整套规则**：见 [`document/rules-format.md`](document\rules-format.md)（完整字段、类型、标记语法、公式、分层合并）。

---

## 构建流程

环境需 Python 3。

```powershell
# 1) 把模板组装成最终 HTML
python builder\build.py

# 2) 把底层 + 规则包深合并成一份稳定规则
python builder\merge_rules.py DW.json my-classpack.json -o merged.json
```

---

## 目录结构

```
├─ builder\                     ← 源码与脚本
│   ├─ app_template.html        ← UI 与逻辑
│   ├─ build.py                 ← 模板 → 成品 转换脚本
│   └─ merge_rules.py           ← 合并规则包脚本
├─ document\                    ← 文档
│   └─ rules-format.md          ← 规则 JSON 格式完整参考
├─ 地城世界车卡工具.html         ← 成品工具
├─ DW.json                      ← 地城世界 Dungeon World 规则
├─ DW-HouseRuleTest.json        ← 房规示例
├─ UD.json                      ← 无限地城 Unlimited Dungeons 规则
├─ UD-DistantShoresPack.json    ← 远岸风景补充包 Distant Shores Pack 规则
├─ README.md / LICENSE / .gitignore / ...
```

---

## 提交规范（Commit）

| 前缀 | 用途 |
|---|---|
| `feat` | 新功能 |
| `fix` | 修 bug |
| `refactor` | 重构（不改行为） |
| `data` | 数据变更 |
| `docs` | 文档 |
| `build` | 构建脚本 |
| `chore` | 杂项 |

格式：`<前缀>: <中文简短描述>`，如 `fix: 清空规则栈后边栏残留旧数据`。

---

## 参考资料

**《Dungeon World》** 由 Sage LaTorra 与 Adam Koebel 创作（Sage Kobold Productions, 2012）。
官网：https://www.dungeon-world.com/
原始源：https://github.com/Sagelt/Dungeon-World

**《无限地城 Unlimited Dungeons》**——《地城世界》的规则魔改（地城世界粉丝社群的衍生同人作品，无单一作者署名），采用 CC BY-SA 4.0 授权。
原文：https://drive.google.com/file/d/1pv6kVVJhbJi1vr8hVeWh1NqrDQJKgY1B/view?usp=drivesdk

**Dungeon World HTML SRD**（英文）由 flyingturtle（Andrew Codispoti, 2013）制作：
https://github.com/flyingturtle/Dungeon-World-HTML-SRD

**中文繁体汉化** 由 Hazmole 等翻译：
https://hazmole.github.io/Dungeon-World-HTML-SRD-release

**繁转简** 使用 OpenCC。

**第三方 Playbook LaTeX 模板**（制作职业卡排版用）：
https://github.com/rfkeepers/dw-playbooks-tex

---

## TODO

### 0. UD 数据

- 由于 UD 内容尚未校对完，数据 json 格式尚未完全做好，目前只是预览。

### 1. 装备内容

- 已经支持标签术语页，并导入了DW的装备标签内容，但是对应的装备和冒险装备示例还没找到地方存放。此外，UD中引入的追随者机制也可能需要引入更多功能。

### 2. 微调资料边栏样式

- 现状：资料边栏的所有动作、组合全都是同一配色，看起来容易眼花，这一点在“扩展”页面中尤其明显。
- 后续有空时应该修改配色，让各种条目之间有些许差别，降低阅读负担。
- （已分离部分动作样式，不过没有修改配色）

### 3. 装备 / 笔记栏支持 `{标签名}` 标签样式

- 现状：装备（gear）和笔记（notes）栏是 textarea 直出、**不做 markdown 渲染**，因此其中的 `{标签名}` 语法不生效——而在动作、羁绊等做渲染的地方，`{标签名}` 会变成高亮标签（见 `markdownToHtml` 里的 `\{([^{}]+)\}`）。
- 难点：装备/笔记要求**编辑模式下仍可直接编辑文本**，如何在「可编辑 textarea」前提下渲染出标签样式，二者冲突。
- 影响不大，但装备描述里不会渲染标签，因此输入“{1 重量}”也没有任何用。把文本框改成富文本格式有点费时费力，而且对实时修改是否真的友好还有待商榷，可能短期内这个问题解决不了。