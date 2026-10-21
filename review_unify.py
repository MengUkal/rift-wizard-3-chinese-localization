# -*- coding: utf-8 -*-
"""统一改动复审：
1) 在旧词典(git a5fcb20)上重放 term_unify，与当前安装词典逐 key 对账（应完全一致）
2) 按规则输出所有改动（key、旧值、新值）→ review_report.txt
3) 扫描坏拼接/重复词噪声
"""
import json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = r"E:\SteamLibrary\steamapps\common\Rift Wizard 3"
old = json.loads(subprocess.run(["git", "show", "a5fcb20:text_zh.json"], capture_output=True).stdout.decode("utf-8"))
cur = json.load(open(os.path.join(GAME, "mods", "ChineseLocalization", "text_zh.json"), encoding="utf-8"))
u = json.load(open(os.path.join(HERE, "term_unify.json"), encoding="utf-8"))

# ---- 1) 重放 ----
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
    if hits:
        per_rule.append((i, rule.get("scope") or "(全局)", hits))

print("规则命中总数: %d 条（%d 条规则有命中）" % (sum(len(h) for _, _, h in per_rule), len(per_rule)))
# 对账
diff = [k for k in set(list(sim) + list(cur)) if sim.get(k) != cur.get(k)]
print("重放结果 vs 当前词典 差异: %d 个 key" % len(diff))
for k in diff[:10]:
    print("  DIFF", repr(k[:60]), "sim=", repr(str(sim.get(k))[:50]), "cur=", repr(str(cur.get(k))[:50]))

# ---- 2) 改动明细 ----
out = []
out.append("统一改动明细（%d 条命中 / %d 条规则）" % (sum(len(h) for _, _, h in per_rule), len(per_rule)))
for i, scope, hits in per_rule:
    out.append("")
    out.append("### 规则#%d scope=%r 命中 %d 条" % (i, scope, len(hits)))
    for k, v, nv in hits:
        # 只显示变化片段附近的上下文（前后各 25 字）
        out.append("  KEY  %r" % (k[:80],))
        # 差异窗口
        sm = __import__("difflib").SequenceMatcher(None, v, nv)
        segs = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                segs.append("[%r→%r]" % (v[max(0, i1 - 8):min(len(v), i2 + 8)], nv[max(0, j1 - 8):min(len(nv), j2 + 8)]))
        out.append("       %s" % (" ".join(segs[:4])[:240]))
open(os.path.join(HERE, "review_report.txt"), "w", encoding="utf-8").write("\n".join(out))
print("review_report.txt: %d 行" % len(out))

# ---- 3) 坏拼接扫描（改动值里的异常重复/坏词）----
bad_patterns = ["光束束", "光环环", "蛟龙龙", "木屐屐", "友方方", "腐烂烂", "中毒毒", "霪",
                "的的", "了了", "是是", "有有", "在在", "怪怪", "魔魔", "法法", "术术"]
bad = []
for k, nv in sim.items():
    ov = old.get(k)
    if nv == ov:
        continue
    for p in bad_patterns:
        if p in nv and p not in (ov or ""):
            bad.append((k, p, ov, nv))
            break
print("坏拼接命中: %d 条" % len(bad))
for k, p, ov, nv in bad[:20]:
    print("  BAD", p, repr(k[:50]), repr(nv[:80]))
