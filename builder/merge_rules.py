# -*- coding: utf-8 -*-
"""
合并规则 JSON：底层 + 若干规则包 → 深合并（含 $delete 语义）→ 输出一份完整规则。

用法:
  python merge_rules.py base.json pack1.json pack2.json -o merged.json

语义与工具内一致：
  - 对象字段上层覆盖下层
  - 数组按 id/name 匹配合并（同键覆盖、新键追加）
  - 对象字段值为 null → 删除该字段
  - 数组条目 {"id"/"name": "...", "$delete": true} → 删除匹配条目
"""
import os, json, argparse


def is_obj(v):
    return isinstance(v, dict)


def entry_field(e):
    if isinstance(e, dict):
        if "id" in e:
            return "id"
        if "name" in e:
            return "name"
    return None


def merge_array(base, patch):
    out = [dict(x) if isinstance(x, dict) else x for x in base]
    for pe in patch:
        if isinstance(pe, dict) and pe.get("$delete") is True:
            field = entry_field(pe)
            if field:
                val = pe.get(field)
                out = [x for x in out if not (isinstance(x, dict) and x.get(field) == val)]
            continue
        field = entry_field(pe)
        if field:
            val = pe.get(field)
            idx = next((i for i, x in enumerate(out) if isinstance(x, dict) and x.get(field) == val), -1)
            if idx != -1:
                out[idx] = deep_merge(out[idx], pe)
            else:
                out.append(dict(pe))
        else:
            out.append(pe)
    return out


def deep_merge(base, patch):
    if not is_obj(patch):
        return patch
    out = dict(base) if is_obj(base) else {}
    for k, pv in patch.items():
        if pv is None:
            out.pop(k, None)
            continue
        bv = out.get(k)
        if isinstance(pv, list):
            out[k] = merge_array(bv if isinstance(bv, list) else [], pv)
        elif is_obj(pv) and is_obj(bv):
            out[k] = deep_merge(bv, pv)
        else:
            out[k] = pv
    return out


def main():
    ap = argparse.ArgumentParser(description="合并规则 JSON（底层 + 规则包 → 深合并）")
    ap.add_argument("files", nargs="+", help="JSON 文件，第一个是底层，后续按顺序叠加")
    ap.add_argument("-o", "--output", default="merged.json", help="输出文件（默认 merged.json）")
    args = ap.parse_args()

    merged = {}
    for path in args.files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        merged = deep_merge(merged, data)
        print("已合并:", path)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print("输出:", args.output, "大小:", os.path.getsize(args.output), "字节")


if __name__ == "__main__":
    main()
