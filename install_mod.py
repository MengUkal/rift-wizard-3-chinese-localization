# -*- coding: utf-8 -*-
"""安装 MOD 到游戏目录：mods/ChineseLocalization/
- 复制入口脚本、描述、text_zh.json、字体
- 校验 options2.dat：lang=zh 且 enabled_mods 含 ChineseLocalization（需要时才改写）
用法: python install_mod.py
"""
import json, os, pickle, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_SRC = os.path.join(HERE, "mod", "ChineseLocalization")
GAME = r"E:\SteamLibrary\steamapps\common\Rift Wizard 3"
MOD_DST = os.path.join(GAME, "mods", "ChineseLocalization")
OPTIONS = os.path.join(GAME, "options2.dat")

text_zh = os.path.join(HERE, "text_zh.json")
if not os.path.exists(text_zh):
    print("缺少 text_zh.json，先跑 merge_batches.py"); sys.exit(1)

os.makedirs(os.path.join(MOD_DST, "fonts"), exist_ok=True)
shutil.copy2(os.path.join(MOD_SRC, "ChineseLocalization.py"), os.path.join(MOD_DST, "ChineseLocalization.py"))
shutil.copy2(os.path.join(MOD_SRC, "description.txt"), os.path.join(MOD_DST, "description.txt"))
shutil.copy2(text_zh, os.path.join(MOD_DST, "text_zh.json"))
try:
    shutil.copy2(os.path.join(MOD_SRC, "fonts", "SourceHanSansCN-Normal.ttf"),
                 os.path.join(MOD_DST, "fonts", "SourceHanSansCN-Normal.ttf"))
except PermissionError:
    print("字体被占用（游戏正在运行），跳过——字体内容未变，不影响")

# ---- options2.dat 检查 ----
changed = False
with open(OPTIONS, "rb") as f:
    options = pickle.load(f)
print("当前 options: lang=%r, enabled_mods=%r" % (options.get("lang"), options.get("enabled_mods")))
if options.get("lang") != "zh":
    options["lang"] = "zh"; changed = True
mods = options.setdefault("enabled_mods", [])
if "ChineseLocalization" not in mods:
    mods.append("ChineseLocalization"); changed = True
if changed:
    tmp = OPTIONS + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(options, f)
    os.replace(tmp, OPTIONS)
    print("options2.dat 已更新: lang=zh, enabled_mods += ChineseLocalization")
else:
    print("options2.dat 无需修改（lang=zh 且 MOD 已启用）")

with open(os.path.join(MOD_DST, "text_zh.json"), encoding="utf-8") as f:
    n = len(json.load(f))
print("安装完成: %s" % MOD_DST)
print("text_zh.json 词条: %d" % n)
