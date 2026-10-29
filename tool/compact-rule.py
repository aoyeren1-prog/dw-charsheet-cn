'''用 compact_json 库压缩规则 json 的行数（就地压缩，自动备份 .bak）

用法：python tool\\compact-rule.py <规则.json> [更多.json ...]
'''
import json
import sys
import shutil
from compact_json import Formatter


def compact(path):
    # 1. 读取原文件
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. 备份原文件为 <path>.bak
    bak = path + ".bak"
    shutil.copyfile(path, bak)

    # 3. 压缩参数（根据需要修改）
    formatter = Formatter()
    formatter.max_inline_length = 100
    formatter.ensure_ascii = False  # 关闭 ASCII 强制转义，保留原生中文

    # 4. 就地写回（覆盖原文件）
    with open(path, "w", encoding="utf-8") as f:
        f.write(formatter.serialize(data) + "\n")

    print("已压缩：%s（原文件备份到 %s）" % (path, bak))


def main():
    if len(sys.argv) < 2:
        print("用法：python tool\\compact-rule.py <规则.json> [更多.json ...]")
        sys.exit(1)
    for path in sys.argv[1:]:
        compact(path)


if __name__ == "__main__":
    main()
