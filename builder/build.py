# -*- coding: utf-8 -*-
"""把 app_template.html 拷贝为最终 HTML（规则通过「导入规则 JSON」加载）。"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(BASE)
TPL = os.path.join(BASE, "app_template.html")
OUT = os.path.join(WORKSPACE, "地城世界车卡工具.html")

with open(TPL, encoding="utf-8") as f:
    tpl = f.read()

assert "__DW_DATA_JSON__" not in tpl, "模板不应再包含 __DW_DATA_JSON__ 占位符"
assert 'src="data.js"' not in tpl, "模板不应再引用 data.js（规则改为导入规则 JSON）"

with open(OUT, "w", encoding="utf-8") as f:
    f.write(tpl)

print("已生成：", OUT, "大小：", os.path.getsize(OUT), "字节")
