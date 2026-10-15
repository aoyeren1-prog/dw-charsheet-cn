# -*- coding: utf-8 -*-
"""
解析《地城世界》汉化项目(Hugo源文件)的职业数据，繁体转简体，输出 data.json（唯一数据源）。
用法: python extract_data.py
"""
import os, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")

from lxml import html as LH

BASE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(BASE)
OPENCC_DIR = os.path.join(WORKSPACE, ".pip-test-opencc")
sys.path.insert(0, OPENCC_DIR)
from opencc import OpenCC
T2S = OpenCC("t2s")

_SRD_CANDIDATES = ["Dungeon-World-HTML-SRD-ZH", "Dungeon-World-HTML-SRD-master", "Dungeon-World-HTML-SRD"]
_SRD_DIR = None
for _c in _SRD_CANDIDATES:
    _p = os.path.join(WORKSPACE, _c)
    if os.path.isdir(_p):
        _SRD_DIR = _p
        break
if _SRD_DIR is None:
    sys.exit("未找到 SRD 目录：请先下载 Hazmole 的中文汉化仓库 https://github.com/hazmole/Dungeon-World-HTML-SRD 并解压到本工作区（目录名可带 -master / -ZH 后缀，脚本会自动识别）。")
SRC_CLASSES = os.path.join(_SRD_DIR, "content", "classes")
CLASS_FILES = [
    "barbarian", "bard", "cleric", "druid", "fighter",
    "immolator", "paladin", "ranger", "thief", "wizard",
]

def fix_zhu(text):
    """opencc t2s 不处理『著→着』；保护『显著』等保留『著』的词后全局替换"""
    protected = {}
    for i, w in enumerate(["显著", "著名", "著作", "编著", "巨著", "论著", "译著", "原著", "著者", "著述", "撰著", "名著", "专著"]):
        key = "\u0001%d\u0001" % i
        if w in text:
            text = text.replace(w, key)
            protected[key] = w
    text = text.replace("著", "着")
    for key, w in protected.items():
        text = text.replace(key, w)
    return text

def clean_name(text):
    """去多余空白 + 剥掉末尾英文括号说明(保留中文括号如 圣疗(魅力))"""
    t = re.sub(r"\s+", " ", text).strip()
    t = re.sub(r"\s*\([^)]*[A-Za-z][^)]*\)\s*$", "", t)
    return re.sub(r"\s+", " ", t).strip()

def normalize_html(frag):
    frag = re.sub(r"<tag\b[^>]*>", '<span class="tag">', frag)
    frag = re.sub(r"</tag>", "</span>", frag)
    frag = re.sub(r'<span class="Tags">', '<span class="tag">', frag)
    frag = re.sub(r'<span class="red">', '<span class="tag">', frag)
    frag = re.sub(r"<b>", "<strong>", frag); frag = re.sub(r"</b>", "</strong>", frag)
    frag = re.sub(r"<div\b[^>]*>", "", frag); frag = re.sub(r"</div>", "", frag)
    def tag_clean(m):
        slash = m.group(1) or ""
        name = m.group(2).lower()
        if name in ("p", "ul", "li", "strong", "em", "br", "span", "h3", "h4"):
            return "<%s%s>" % (slash, name)
        return ""
    frag = re.sub(r"<(/)?([a-zA-Z0-9]+)\b[^>]*>", tag_clean, frag)
    frag = frag.replace("\u3000", " ")
    frag = re.sub(r"[ \t]+\n", "\n", frag)
    frag = re.sub(r"\n{3,}", "\n\n", frag)
    return frag.strip()

def html_to_markdown(frag):
    h = normalize_html(frag)
    h = re.sub(r"<strong[^>]*>", "**", h); h = re.sub(r"</strong>", "**", h)
    h = re.sub(r"<em[^>]*>", "*", h); h = re.sub(r"</em>", "*", h)
    h = re.sub(r'<span[^>]*>', "{", h); h = re.sub(r"</span>", "}", h)
    h = re.sub(r"<li[^>]*>", "- ", h); h = re.sub(r"</li>", "\n", h)
    h = re.sub(r"<ul[^>]*>", "", h); h = re.sub(r"</ul>", "", h)
    h = re.sub(r"<br\s*/?>", "\n", h)
    h = re.sub(r"</p>", "\n\n", h); h = re.sub(r"<p[^>]*>", "", h)
    h = re.sub(r"<h[34][^>]*>", "**", h); h = re.sub(r"</h[34]>", "**", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = re.sub(r"[ \t]+\n", "\n", h)
    h = re.sub(r"\n{3,}", "\n\n", h)
    return h.strip()

def html_to_text(frag):
    h = normalize_html(frag)
    h = re.sub(r"<[^>]+>", "", h)
    return h.strip()

def inner_html(el):
    return "".join(LH.tostring(c, encoding="unicode") for c in el)

def move_name_and_body(move_el):
    h3s = move_el.xpath(".//h3")
    name = clean_name(h3s[0].text_content()) if h3s else ""
    for h3 in h3s:
        h3.getparent().remove(h3)
    body = html_to_markdown(inner_html(move_el))
    return name, body

def split_options(text):
    parts = re.split(r"[，,]\s*(?:或\s*)?", text)
    return [p.strip() for p in parts if p.strip()]

def strip_paren_en(t):
    return re.sub(r"\([^)]*\)", "", t).strip()

def parse_class(cid):
    path = os.path.join(SRC_CLASSES, cid + ".html")
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    raw = fix_zhu(T2S.convert(raw))  # 读取时统一繁体转简体 + 著→着
    root = LH.fromstring(raw)

    h1 = root.xpath("//h1")
    cname = clean_name(h1[0].text_content()) if h1 else cid

    # 简介(风味文字; 可能缺失)
    intro = ""
    intro_div = root.xpath("//div[@id='intro']")
    if intro_div:
        intro = html_to_markdown(inner_html(intro_div[0]))

    # 名字(按种族; 无种族则 race 为空)
    names = []
    names_div = root.xpath("//div[@id='names']")
    if names_div:
        for p in names_div[0].xpath("./p"):
            b = p.xpath("./b|./strong")
            race = clean_name(b[0].text_content()) if b else ""
            tail = p.text_content()
            if ":" in tail:
                tail = tail.split(":", 1)[1]
            elif "：" in tail:
                tail = tail.split("：", 1)[1]
            elif b:
                tail = b[0].tail or ""
            lst = [strip_paren_en(n) for n in split_options(tail)]
            names.append({"race": race, "names": [n for n in lst if n]})

    # 外观
    look = []
    look_div = root.xpath("//div[@id='look']")
    if look_div:
        for li in look_div[0].xpath(".//li"):
            opts = split_options(li.text_content())
            if opts:
                look.append(opts)

    # 属性数值(简体正则)
    body_text = root.text_content()
    hp = damage = load = ""
    m = re.search(r"最大生命值为\s*([^。；;]+)", body_text)
    if m:
        hp = m.group(1).replace("值", "").strip()
    dspan = root.xpath("//span[@id='Damage']")
    if dspan:
        damage = dspan[0].text_content().strip()
    m = re.search(r"负载上限为\s*([^。；;\n]+)", body_text)
    if m:
        load = m.group(1).replace("值", "").strip()
    m = re.search(r"将以下数值分配到你的属性上[：:]\s*([^。\n]+)", body_text)
    stat_note = m.group(1).strip() if m else ""

    # 起始动作（含「选择其中一项」互斥组检测）
    racial_moves, starting_moves = [], []
    sm = root.xpath("//div[@id='startingmoves']")
    if sm:
        choice_groups = []
        current_group = None
        for node in sm[0].xpath(".//p[contains(@class,'Instructions')] | .//div[contains(@class,'Move')]"):
            tag = node.tag.lower()
            if tag == "p":
                txt = node.text_content().strip()
                if ("選擇其中一項" in txt) or ("选择其中一项" in txt):
                    current_group = []
                    choice_groups.append(current_group)
                else:
                    current_group = None
            elif tag == "div":
                h3 = node.xpath("./h3 | .//h3")
                if not h3:
                    continue
                h3class = h3[0].get("class") or ""
                name, body = move_name_and_body(node)
                if not name:
                    continue
                if (h3class == "MoveName") or node.xpath("ancestor::div[@id='racialmoves']"):
                    racial_moves.append({"race": name, "moves": [{"name": name, "text": body}]})
                else:
                    if current_group is not None:
                        current_group.append(name)
                    starting_moves.append({"name": name, "text": body})
        # 互斥组补 replaces（组内互相取代）
        for grp in choice_groups:
            if len(grp) >= 2:
                for name in grp:
                    others = [x for x in grp if x != name]
                    for m in starting_moves:
                        if m["name"] == name:
                            m["replaces"] = others[0] if len(others) == 1 else others

    # 阵营
    alignment = []
    al = root.xpath("//div[@id='alignment']")
    if al:
        for mv in al[0].xpath(".//div[contains(@class,'Move')]"):
            h3 = mv.xpath("./h3 | .//h3")
            if not h3:
                continue
            nm = clean_name(h3[0].text_content())
            for h in h3:
                h.getparent().remove(h)
            alignment.append({"name": nm, "text": html_to_markdown(inner_html(mv))})

    # 装备
    gear = parse_gear(root)

    # 羁绊 (兼容 id='bonds' 与 id='bond')
    bonds = []
    bd = root.xpath("//div[@id='bonds'] | //div[@id='bond']")
    if bd:
        for p in bd[0].xpath("./p"):
            t = p.text_content().strip()
            if t and "至少" not in t and "其中一名" not in t:
                bonds.append(t)

    # 进阶动作(按等级段)
    adv = {"2-5": [], "6-10": []}
    current = "2-5"
    mv_div = root.xpath("//div[@id='moves']")
    if mv_div:
        for child in mv_div[0]:
            if not hasattr(child, "tag"):
                continue
            tag = child.tag.lower()
            cls = child.get("class") or ""
            if tag == "p" and "Instructions" in cls:
                txt = child.text_content()
                if ("6" in txt) or ("六" in txt):
                    current = "6-10"
                continue
            if tag == "div" and "Move" in cls:
                name, _ = move_name_and_body(child)
                requires = replaces = None
                for rp in child.xpath(".//p[contains(@class,'Requirement')]"):
                    rt = rp.text_content().strip()
                    rp.getparent().remove(rp)
                    val = rt.split(":", 1)[-1].split("：", 1)[-1].strip()
                    if rt.startswith("需求") or rt.startswith("需要"):
                        requires = val
                    elif rt.startswith("取代") or rt.startswith("替换"):
                        replaces = val
                body = html_to_markdown(inner_html(child))
                adv[current].append({"name": name, "text": body, "requires": requires, "replaces": replaces})

    return {
        "id": cid, "name": cname, "intro": intro,
        "hp": hp, "damage": damage, "load": load, "statNote": stat_note,
        "names": names, "look": look,
        "racialMoves": racial_moves, "startingMoves": starting_moves,
        "alignment": alignment, "gear": gear, "bonds": bonds,
        "advancedMoves": adv,
    }

def parse_gear(root):
    gr = root.xpath("//div[@id='gear']")
    intro, groups, cur_prompt = [], [], ""
    if gr:
        for child in gr[0]:
            if not hasattr(child, "tag"):
                continue
            tag = child.tag.lower()
            if tag == "p":
                txt = html_to_markdown(LH.tostring(child, encoding="unicode", with_tail=False))
                # 去掉冗余的「负载上限为 X」句（load 已单独解析显示）
                txt = re.sub(r"你的负载上限[^。]*。\s*", "", txt).strip()
                if txt:
                    intro.append(txt)
            elif tag == "ul":
                opts = [html_to_text(LH.tostring(li, encoding="unicode", with_tail=False)) for li in child.xpath("./li")]
                groups.append({"prompt": (cur_prompt or "选择：").strip(), "options": opts})
                cur_prompt = ""
            else:
                # 内联元素（如 <tag>、<span>）也是 prompt 的一部分，转成标签语法并累积
                cur_prompt += html_to_markdown(LH.tostring(child, encoding="unicode", with_tail=False))
            cur_prompt += (child.tail or "")
    # 把起始装备说明（原 intro）拼进第一个分组提示里，避免丢失
    intro_text = "\n".join(intro).strip()
    if intro_text and groups:
        groups[0]["prompt"] = intro_text + "\n\n" + groups[0]["prompt"]
    return {"groups": groups}

def parse_moves():
    path = os.path.join(WORKSPACE, "Dungeon-World-HTML-SRD-ZH", "content", "moves.html")
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    raw = fix_zhu(T2S.convert(raw))
    root = LH.fromstring(raw)
    sections = {"基本动作": "basicMoves", "特殊动作": "specialMoves"}
    result = {"basicMoves": [], "specialMoves": []}
    current = None
    for el in root.xpath("//h1 | //div[contains(@class,'Move')]"):
        if el.tag == "h1":
            current = sections.get(clean_name(el.text_content()))
        elif el.tag == "div" and current:
            h2 = el.xpath("./h2 | .//h2")
            if not h2:
                continue
            name = clean_name(h2[0].text_content())
            for h in h2:
                h.getparent().remove(h)
            body = html_to_markdown(inner_html(el))
            result[current].append({"name": name, "text": body})
    return result

def parse_spells():
    result = {}
    for cid, fname in [("wizard", "wizard/spells.html"), ("cleric", "cleric/spells.html")]:
        path = os.path.join(WORKSPACE, "Dungeon-World-HTML-SRD-ZH", "content", "classes", fname)
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        raw = fix_zhu(T2S.convert(raw))
        root = LH.fromstring(raw)
        spells = []
        current_group = ""
        for el in root.xpath("//h1 | //div[contains(@class,'Spell')]"):
            if el.tag == "h1":
                g = clean_name(el.text_content()).replace(" 法术", "").replace(" 法術", "")
                current_group = g
            elif el.tag == "div":
                h3 = el.xpath("./h3 | .//h3")
                if not h3:
                    continue
                name = clean_name(h3[0].text or h3[0].text_content())
                for h in h3:
                    h.getparent().remove(h)
                body = html_to_markdown(inner_html(el))
                spells.append({"group": current_group, "name": name, "text": body})
        result[cid] = spells
    return result

def main():
    classes = [parse_class(c) for c in CLASS_FILES]
    moves = parse_moves()
    spells = parse_spells()
    data = {
        "meta": {
            "source": "Dungeon-World-HTML-SRD (Hazmole 汉化), 繁体转简体 by OpenCC",
            "license": "CC-BY 3.0 + OGL",
            "stats": ["力量", "敏捷", "体质", "智力", "睿知", "魅力"],
            "statsMode": "scores",
            "modTable": {"1-3": -3, "4-5": -2, "6-8": -1, "9-12": 0, "13-15": 1, "16-17": 2, "18": 3},
            "debilities": {"力量": "虚弱", "敏捷": "颤抖", "体质": "患病", "智力": "晕眩", "睿知": "困惑", "魅力": "疤痕"},
            "labels": {
                "look": "外观", "race": "种族动作", "raceName": "种族",
                "alignment": "阵营动作", "alignmentNote": "动机 / Drive", "alignmentName": "阵营",
                "starting": "起始动作", "advanced": "进阶动作", "customAdvanced": "其他",
                "gear": "装备", "bonds": "羁绊", "notes": "笔记",
                "load": "负载上限", "hpMax": "最大生命", "hpCur": "当前生命",
                "armor": "护甲", "damage": "伤害", "name": "姓名", "level": "等级", "xp": "XP",
                "defaultFormula": "默认", "blank": " ", "casterLevel": "施法等级", "prepareCap": "准备上限", "statDist": "初始分配",
            },
            "advancedTiers": [
                {"key": "2-5", "label": "进阶 · 2~5 级", "minLevel": 1},
                {"key": "6-10", "label": "进阶 · 6~10 级", "minLevel": 6},
            ],
            "spellSections": {
                "spellbook": {"title": "法术书", "source": "法师法术", "trigger": "法术书", "spellClass": "wizard",
                              "groups": ["戏法", "等级1", "等级3", "等级5", "等级7", "等级9"]},
                "cleric": {"title": "牧师法术", "source": "牧师法术", "trigger": "通神", "spellClass": "cleric",
                           "groups": ["祷念", "等级1", "等级3", "等级5", "等级7", "等级9"]},
            },
            "refSections": [
                {"id": "moves", "title": "通用动作", "type": "groups", "groups": [
                    {"key": "basicMoves", "label": "基本动作"},
                    {"key": "specialMoves", "label": "特殊动作"},
                ]},
                {"id": "extension", "title": "扩展", "type": "extension", "groups": [
                    {"key": "customMoves", "label": "自定义动作"},
                ], "articles": "compendium"},
                {"id": "spells", "title": "法术列表", "type": "spells"},
                {"id": "search", "title": "资料速查", "type": "search"},
            ],
            "prepareCapFormula": "施法等级+1",
            "statDistribution": [16, 15, 13, 12, 9, 8],
        },
        "classes": classes,
        "basicMoves": moves["basicMoves"],
        "specialMoves": moves["specialMoves"],
        "spells": spells,
    }
    with open(os.path.join(WORKSPACE, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("职业数:", len(classes))
    print("基本动作:", len(moves["basicMoves"]), "| 特殊动作:", len(moves["specialMoves"]))
    print("法术 法师:", len(spells["wizard"]), "| 牧师:", len(spells["cleric"]))
    for c in classes:
        print(f"\n== {c['name']}({c['id']}) HP={c['hp']!r} 伤害={c['damage']!r} 负载={c['load']!r}")
        print(f"  种族动作 {len(c['racialMoves'])} | 起始动作 {len(c['startingMoves'])} | 阵营 {len(c['alignment'])} | 羁绊 {len(c['bonds'])} | 名字组 {len(c['names'])} | 外观组 {len(c['look'])} | 进阶 2-5:{len(c['advancedMoves']['2-5'])} 6-10:{len(c['advancedMoves']['6-10'])} | 装备组 {len(c['gear']['groups'])}")

if __name__ == "__main__":
    main()
