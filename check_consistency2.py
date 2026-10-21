# -*- coding: utf-8 -*-
"""译名一致性检测 v2：排除机械组合垃圾 key，只报真实游戏文本里的不一致。
输出 consistency_report2.txt + fix_proposals2.json
"""
import json, os, re, sys
from collections import defaultdict
from difflib import SequenceMatcher

GAME = r"E:\SteamLibrary\steamapps\common\Rift Wizard 3"
HERE = os.path.dirname(os.path.abspath(__file__))
zh = json.load(open(os.path.join(GAME, "mods", "ChineseLocalization", "text_zh.json"), encoding="utf-8"))

def has_cjk(s):
    return any("\u4e00" <= c <= "\u9fff" for c in s)

# ---- 基础 key（批次原始提取，不含生成组合）----
base = set()
for fn in os.listdir(os.path.join(HERE, "batches")):
    if re.fullmatch(r"src_\d+\.json", fn):
        base |= set(json.load(open(os.path.join(HERE, "batches", fn), encoding="utf-8")))

# ---- 机械组合 key 集合（与 gen_extras 同源，用于排除）----
PREFIXES = ["Baby ", "Chalice of ", "Robe of ", "Respawn As ", "Touched by ",
            "Multicast ", "Skeletal ", "Slimy ", "Summon ", "temporary "]
SUFFIXES = [" Egg", " Oculus", " Curse Doll", " Queen", " Swarm Summon", " Spawner",
            " Repeater", " Tome", " Frenzy Mask", " Hunter's Sigil", " Aura", " Burst",
            " Armor", " Weakness", " Frenzy", " Swap", " Retaliation", " Woven",
            " Bolt", " Ball", " Beam", "s Bolt", "s Ball", "s Beam"]
name_re = re.compile(r"^[A-Z][A-Za-z'’\-]*(?: [A-Za-z'’\-]+)*$")
nameish = sorted([k for k in base if name_re.match(k) and 3 <= len(k) <= 40
                  and has_cjk(zh.get(k, ""))], key=lambda x: -len(x))
generated = set()
for p in PREFIXES:
    for n in nameish:
        generated.add(p + n)
for s in SUFFIXES:
    for n in nameish:
        generated.add(n + s)
for n in nameish:
    if len(n) > 20:
        generated.add(n[:18] + "..")
print("nameish: %d  generated: %d" % (len(nameish), len(generated)))

# ---- 标准译名表：只用真实独立名词 key ----
names = {}
for k in base:
    v = zh.get(k)
    if (name_re.match(k) and 1 <= len(k.split()) <= 4 and 2 <= len(k) <= 40
            and has_cjk(v or "") and v != k and len(v) <= 12 and k not in generated):
        names[k] = v
print("canonical: %d" % len(names))

by_first = defaultdict(list)
for k in names:
    by_first[k.split()[0]].append(k)
for lst in by_first.values():
    lst.sort(key=lambda n: -len(n))

def strip_word(w):
    return w.strip('.,:;!?()[]{}"\'`')

def find_names_in(key):
    words = key.split()
    clean = [strip_word(w) for w in words]
    hits = []
    i = 0
    while i < len(words):
        matched = False
        for n in by_first.get(clean[i], ()):
            nw = n.split()
            if i + len(nw) <= len(clean) and clean[i:i+len(nw)] == nw:
                hits.append(n)
                i += len(nw)
                matched = True
                break
        if not matched:
            i += 1
    return hits

def render_check(T, v):
    if T in v:
        return ("ok", None)
    if len(T) >= 3 and T[:-1] in v:
        return ("stem", T[:-1])
    sm = SequenceMatcher(None, T, v, autojunk=False)
    m = sm.find_longest_match(0, len(T), 0, len(v))
    if m.size >= 2:
        return ("lcs", v[m.b:m.b + m.size])
    return ("missing", None)

# ---- 扫描真实 key ----
report = defaultdict(list)
proposals = {}
for k in base:
    if k in generated or k in names:
        continue
    v = zh.get(k)
    if not v or not has_cjk(v):
        continue
    for n in find_names_in(k):
        T = names[n]
        if len(T) == 1:
            continue
        kind, variant = render_check(T, v)
        if kind == "ok":
            continue
        if kind == "stem":
            rest = T[len(variant):]
            new_v = re.sub(re.escape(variant) + "(?!" + re.escape(rest) + ")", T, v) if rest else v.replace(variant, T)
            if new_v != v:
                proposals[k] = new_v
            report[n].append((k, v, kind, variant, new_v))
        else:
            report[n].append((k, v, kind, variant, None))

lines = []
total = sum(len(x) for x in report.values())
lines.append("真实不一致名词: %d  受影响条目: %d  可自动修复: %d" % (len(report), total, len(proposals)))
for n in sorted(report, key=lambda x: -len(report[x])):
    T = names[n]
    lines.append("")
    lines.append("=== %r -> %r （%d 处）===" % (n, T, len(report[n])))
    for k, v, kind, variant, new_v in report[n][:8]:
        lines.append("  [%s] key: %r" % (kind, k[:100]))
        lines.append("        val: %r" % v[:140])
        if new_v:
            lines.append("        建议: %r" % new_v[:140])
    if len(report[n]) > 8:
        lines.append("  ... 还有 %d 处" % (len(report[n]) - 8))

open(os.path.join(HERE, "consistency_report2.txt"), "w", encoding="utf-8").write("\n".join(lines))
json.dump({"names": names, "proposals": proposals},
          open(os.path.join(HERE, "fix_proposals2.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("report2: %d lines, proposals: %d" % (len(lines), len(proposals)))
