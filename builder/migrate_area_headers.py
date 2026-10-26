# -*- coding: utf-8 -*-
"""
数据迁移脚本：将旧的 labels 格式转换为新的 areas 格式
"""
import json
import shutil
import re
import sys
from pathlib import Path

# 需要转换的规则文件
FILES = [
    "DW.json",
    "UD.json",
    "DW-HouseRuleTest.json",
    "UD-DistantShoresPack.json",
    "UD-HeritageHouseRule.json",
    "DW2-demo.json"
]

def extract_title_and_note(text):
    """
    从 '种族动作（选择一项）' 提取标题和 note
    支持中文括号（）和英文括号()
    """
    if not text:
        return text, None
    
    # 匹配中文括号
    match = re.match(r'^([^（]+)(?:（(.+)）)?$', text)
    if match and match.group(2):
        return match.group(1).strip(), match.group(2).strip()
    
    # 匹配英文括号
    match = re.match(r'^([^(]+)(?:\((.+)\))?$', text)
    if match and match.group(2):
        return match.group(1).strip(), match.group(2).strip()
    
    return text, None

def migrate_file(filepath):
    """迁移单个规则文件"""
    filepath = Path(filepath)
    
    if not filepath.exists():
        print(f"⊘ 跳过不存在的文件: {filepath}")
        return False
    
    print(f"处理: {filepath}")
    
    # 备份原文件
    backup_path = Path(str(filepath) + ".backup")
    shutil.copy(filepath, backup_path)
    print(f"  ✓ 已备份至: {backup_path}")
    
    # 读取 JSON
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取 labels
    meta = data.get("meta", {})
    labels = meta.get("labels", {})
    
    if not labels and not data.get("classes"):
        print(f"  ⊘ 跳过空规则文件")
        return True
    
    # 构建 areaHeaders
    area_headers = {}
    
    # look - 直接提取标题
    if "look" in labels:
        area_headers["look"] = {"title": labels["look"]}
    
    # race - 提取标题和 note
    if "race" in labels:
        title, note = extract_title_and_note(labels["race"])
        area_headers["race"] = {"title": title}
        if note:
            area_headers["race"]["note"] = note
    
    # alignment - 提取标题和 note
    if "alignment" in labels:
        title, note = extract_title_and_note(labels["alignment"])
        area_headers["alignment"] = {"title": title}
        if note:
            area_headers["alignment"]["note"] = note
    
    # gear - 含 rightStats
    if "gear" in labels:
        area_headers["gear"] = {
            "title": labels["gear"],
            "rightStats": [
                {
                    "key": "load",
                    "label": labels.get("load", "负载上限"),
                    "type": "number",
                    "min": 0
                }
            ]
        }
    
    # bonds, notes, starting, advanced
    for key in ["bonds", "notes", "starting", "advanced"]:
        if key in labels:
            area_headers[key] = {"title": labels[key]}
    
    # 写入 areas（不再是 areaHeaders）
    if area_headers:
        if "meta" not in data:
            data["meta"] = {}
        data["meta"]["areas"] = area_headers
        print(f"  ✓ 已生成 meta.areas，包含 {len(area_headers)} 个区域")
    
    # 为每个职业生成 areas.gear.rightStats
    classes_migrated = 0
    for cls in data.get("classes", []):
        if "load" in cls:
            if "areas" not in cls:
                cls["areas"] = {}
            cls["areas"]["gear"] = {
                "rightStats": [
                    {"key": "load", "formula": cls["load"]}
                ]
            }
            classes_migrated += 1
    
    if classes_migrated > 0:
        print(f"  ✓ 已为 {classes_migrated} 个职业生成 areas.gear.rightStats")
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ 已写入: {filepath}\n")
    return True

def main():
    """主函数"""
    workspace = Path(__file__).parent.parent
    
    print("=" * 60)
    print("数据迁移：labels → areas")
    print("=" * 60 + "\n")
    
    # 如果命令行指定了文件，只转换指定文件
    if len(sys.argv) > 1:
        files_to_migrate = sys.argv[1:]
    else:
        files_to_migrate = FILES
    
    success_count = 0
    for filename in files_to_migrate:
        filepath = workspace / filename
        if migrate_file(filepath):
            success_count += 1
    
    print("=" * 60)
    print(f"完成！成功迁移 {success_count}/{len(files_to_migrate)} 个文件")
    print("备份文件已保存为 *.json.backup")
    print("=" * 60)

if __name__ == "__main__":
    main()
