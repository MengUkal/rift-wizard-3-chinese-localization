# -*- coding: utf-8 -*-
"""全量审计：找出所有可能未翻译的玩家可见文本。
1) 词典中"保留原文"与"无汉字"的词条 + 出处
2) AST 扫描 .name / .description 赋值字面量中不在词典里的漏网之鱼
输出 → audit_out.txt
"""
import ast, json, os, re, sys

GAME = r"E:\SteamLibrary\steamapps\common\Rift Wizard 3"
HERE = os.path.dirname(os.path.abspath(__file__))

zh = json.load(open(os.path.join(HERE, "text_zh.json"), encoding="utf-8"))
keys_meta = {e["k"]: e for e in json.load(open(os.path.join(HERE, "keys.json"), encoding="utf-8"))}

def has_cjk(s):
    return any("\u4e00" <= c <= "\u9fff" for c in s)

ALLOW = {"SP", "HP", "SH", "LoS", "MUTATED_RUN"}
out = []

# ---- 1) 保留原文 / 无汉字 ----
ident = []
for k in sorted(zh):
    v = zh[k]
    if v == k and k not in ALLOW and not k.startswith("%s"):
        ident.append(k)
out.append("=== A. 保留原文（与英文相同）: %d 条 ===" % len(ident))
for k in ident:
    meta = keys_meta.get(k, {})
    out.append("  %r   <- %s" % (k[:90], meta.get("orig", ["?"])[0]))

nocjk = []
for k in sorted(zh):
    v = zh[k]
    if v == k:
        continue
    core = re.sub(r"\{[^{}]*\}|\[[^\]]*\]|[^\w]", "", k)
    if not has_cjk(v) and len(re.sub(r"[^\w]", "", k)) > 3:
        nocjk.append(k)
out.append("")
out.append("=== B. 译文无汉字: %d 条 ===" % len(nocjk))
for k in nocjk:
    meta = keys_meta.get(k, {})
    out.append("  %r -> %r   <- %s" % (k[:70], zh[k][:40], meta.get("orig", ["?"])[0]))

# ---- 2) .name/.description 赋值字面量中，不在词典里的（被过滤器丢弃的漏网）----
FILES = ["CommonContent.py", "Components.py", "Equipment.py", "FinalBosses.py",
         "Game.py", "Level.py", "LevelGen.py", "LevelGenHelpers.py", "LevelRewards.py",
         "Monsters.py", "Mutators.py", "RareMonsters.py", "RiftWizard3.py",
         "Spells.py", "Vaults.py", "text.py"]
missing = []
for fn in FILES:
    src = open(os.path.join(GAME, fn), encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Attribute) and t.attr in ("name", "description") and \
               isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                s = node.value.value
                if s not in zh:
                    core = re.sub(r"\{[^{}]*\}|\[[^\]]*\]|[^\w]", "", s)
                    if len(core) >= 3:
                        missing.append((fn, node.lineno, t.attr, s))
out.append("")
out.append("=== C. .name/.description 字面量未入典: %d 条 ===" % len(missing))
for fn, ln, attr, s in missing:
    out.append("  %s:%d %s = %r" % (fn, ln, attr, s[:100]))

open(os.path.join(HERE, "audit_out.txt"), "w", encoding="utf-8").write("\n".join(out))
print("audit written: %d lines" % (len(out)))
