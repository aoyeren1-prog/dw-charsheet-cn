# 地城世界 · 车卡工具（Dungeon World Digital Character Sheet CN）

纯前端、可离线使用的《地城世界》角色卡工具（简体中文）。单个 HTML 文件，`file://` 双击打开即可，**无需联网、无需服务器、无需构建环境**。规则数据通过 JSON 导入，支持自建房规。

- 左侧角色卡 + 右侧资料边栏
- 编辑 / 查看双模式，浏览器打印导出 PDF
- 规则分层：底层规则 + 支持房规 JSON 叠加，上层覆盖下层
- 全部板块名、动作分类、属性模型等由规则 JSON 的 `meta` 驱动（去硬编码）

---

## 快速开始

1. 去 **Releases** 页面下载最新 `地城世界车卡工具.html`。
2. 在本仓库下载 `data.json`（原版规则数据）。
3. 双击打开 HTML，点右上角 **「📥 规则」** 选择 `data.json`。
4. 开始车卡。规则会自动存进浏览器，刷新后无需重新导入。

> 角色数据存 `localStorage`，换浏览器/清缓存会丢；重要角色请用工具内「导出」备份成 JSON。

---

## 规则 JSON 格式

规则数据是一个 JSON 文件，顶层含 `meta`（配置）、`classes`（职业）、`basicMoves` / `specialMoves`（动作）、`spells`（法术）。所有板块名、动作分类、属性模型都由 `meta` 驱动。

- 只想**改几个字段**：看 `houserule-test.json` 示例即可。
- 想**导入 / 定制整套规则**：见 [`RULES_FORMAT.md`](RULES_FORMAT.md)（完整字段、类型、标记语法、公式、分层合并）。

---

## 构建流程

环境需 Python 3（含 `lxml` 与 `opencc` 依赖，可自行 pip 安装）。

```powershell
# 1) 从 SRD 重新抽取数据（繁体→简体）→ data.json
python builder\extract_data.py

# 2) 把模板组装成最终 HTML
python builder\build.py

# 3) 把底层 + 规则包深合并成一份稳定规则
python builder\merge_rules.py data.json my-classpack.json -o merged.json
```

> `extract_data.py` 读取中文汉化版 SRD（Hazmole 等翻译，繁体）的 `content/classes`。该 SRD 未随仓库分发；如需重新抽取，从 <https://github.com/hazmole/Dungeon-World-HTML-SRD> 下载并解压到本工作区即可——脚本会自动识别 `Dungeon-World-HTML-SRD` / `-master` / `-ZH` 等目录名，**无需手动改名**。

---

## 目录结构

```
├─ builder\                 ← 源码与脚本
│   ├─ app_template.html    ← UI 与逻辑唯一源头
│   ├─ extract_data.py      ← SRD → data.json
│   ├─ build.py             ← 模板 → 最终 HTML
│   └─ merge_rules.py       ← 合并规则包
├─ data.json                ← 规则数据（交付物）
├─ README.md / LICENSE / .gitignore
```

构建产物 `地城世界车卡工具.html` 不入库，走 GitHub Release 分发。

---

## 提交规范（Commit）

约定式提交的简化版，一行一个意思：

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

**Dungeon World HTML SRD**（英文）由 flyingturtle（Andrew Codispoti, 2013）制作：
https://github.com/flyingturtle/Dungeon-World-HTML-SRD

**中文繁体汉化** 由 Hazmole 等翻译：
https://hazmole.github.io/Dungeon-World-HTML-SRD-release

**繁转简** 使用 OpenCC。

**第三方 Playbook LaTeX 模板**（制作职业卡排版用）：
https://github.com/rfkeepers/dw-playbooks-tex

**许可**：
- 规则数据（`data.json`）：CC-BY 3.0 + OGL 1.0a（详见 `LICENSE`）。
- 代码（`builder/`）：MIT（详见 `LICENSE`）。

---

## 待办事项

### 1. 装备 / 笔记栏支持 `{标签名}` 标签样式

- [ ] 现状：装备（gear）和笔记（notes）栏是 textarea 直出、**不做 markdown 渲染**，因此其中的 `{标签名}` 语法不生效——而在动作、羁绊等做渲染的地方，`{标签名}` 会变成高亮标签（见 `markdownToHtml` 里的 `\{([^{}]+)\}`）。
- [ ] 难点：装备/笔记要求**编辑模式下仍可直接编辑文本**，如何在「可编辑 textarea」前提下渲染出标签样式，二者目前冲突。
- 影响不大，但装备描述里的标签会原样显示成 `{重甲}` 这类文本，多少有点难受。有空再研究。

### 2. 支持 Unlimited Dungeons

- [ ] 读完 Unlimited Dungeons 规则后，拓展工具以支持该规则。
- 前期已做部分铺垫：`meta.refSections` 去硬编码（页签/动作分类可配）、`statsMode:"modifiers"`、`statDistribution`、`spellSections`、`prepareCapFormula` 等。
- 待读完后确认 UD 具体规则结构，再补实现。

