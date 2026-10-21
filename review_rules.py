# -*- coding: utf-8 -*-
"""针对性复审：打印高风险规则的全部/抽样改动（含完整旧值新值），并扫描用词残留。"""
import json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = r"E:\SteamLibrary\steamapps\common\Rift Wizard 3"
old = json.loads(subprocess.run(["git", "show", "a5fcb20:text_zh.json"], capture_output=True).stdout.decode("utf-8"))
cur = json.load(open(os.path.join(GAME, "mods", "ChineseLocalization", "text_zh.json"), encoding="utf-8"))
u = json.load(open(os.path.join(HERE, "term_unify.json"), encoding="utf-8"))

sim = dict(old)
for k, v in u["overrides"].items():
    sim[k] = v
per_rule = []
for i, rule in enumerate(u["rules"]):
    sc = re.compile(rule["scope"]) if rule.get("scope") else None
    ex = re.compile(rule["exclude"]) if rule.get("exclude") else None
    hits = []
    for k in list(sim):
        if sc and not sc.search(k):
            continue
        if ex and ex.search(k):
            continue
        v = sim[k]
        nv = v
        for f, r in rule["pairs"]:
            nv = re.sub(f, r, nv)
        if nv != v:
            hits.append((k, v, nv))
            sim[k] = nv
    per_rule.append((i, rule.get("scope") or "(全局)", hits))

TARGET = {"\\bDrain\\b", "\\bGhost\\b", "\\bRot\\b", "\\bMelt\\b", "\\bAllied\\b", "\\bAura",
          "\\bThunder Strike\\b", "\\bOrochi\\b", "\\bWyrm", "\\bChanneling", "Faeries",
          "\\bAnnihilate\\b", "\\bMelted Armor\\b", "\\bMelts walls\\b", "\\bLifedrain\\b",
          "\\bBone Knight", "\\bVenom Bear\\b", "\\bPsychic Seedling\\b", "\\bDragon Claw\\b",
          "\\bRain of Fire\\b", "\\bScuttler\\b", "\\bSpike Ball\\b", "\\bClogs", "\\bPain\\b",
          "\\bRegeneration Aura\\b", "(全局)"}
for i, scope, hits in per_rule:
    if scope not in TARGET or not hits:
        continue
    print("### 规则#%d scope=%r 命中 %d" % (i, scope, len(hits)))
    for k, ov, nv in hits[:14]:
        print("  K %r" % (k[:85],))
        print("    OLD %r" % ov[:150])
        print("    NEW %r" % nv[:150])
    if len(hits) > 14:
        print("  ... 还有 %d 条" % (len(hits) - 14))
    print()

print("=== 关键用词残留（当前词典）===")
for p in ["汲取", "吸取", "幽灵", "幽魂", "腐化", "腐烂", "熔化", "熔解", "我方", "友方",
          "痛苦魔", "痛楚", "蟠龙", "蛟龙", "木鞋", "木屐", "雷击", "雷袭", "雷霆打击",
          "大蛇", "八岐大蛇", "仙灵群", "引导中", "痛苦魔魔", "生命汲取", "生命吸取"]:
    print("%-6s %d" % (p, sum(1 for v in cur.values() if p in v)))
