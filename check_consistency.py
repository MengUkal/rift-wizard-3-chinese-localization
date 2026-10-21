# -*- coding: utf-8 -*-
"""译名一致性检测：
1) 从独立名词 key（Fireball、Ice Wyrm 这类）建立 标准译名表
2) 扫描所有包含该名词的长句 key，检查其译文里该名词的译法是否与标准一致
3) 输出报告 consistency_report.txt + 可自动修复清单 fix_proposals.json
"""
import json, os, re, sys
from collections import defaultdict
from difflib import SequenceMatcher

GAME = r"E:\SteamLibrary\steamapps\common\Rift Wizard 3"
HERE = os.path.dirname(os.path.abspath(__file__))
zh = json.load(open(os.path.join(GAME, "mods", "ChineseLocalization", "text_zh.json"), encoding="utf-8"))

def has_cjk(s):
    return any("\u4e00" <= c <= "\u9fff" for c in s)

# ---- 1) 标准译名表：独立名词 key ----
name_re = re.compile(r"^[A-Z][A-Za-z'’\-]*(?: [A-Za-z'’\-]+)*$")
names = {}
for k, v in zh.items():
    if (name_re.match(k) and 2 <= len(k.split()) <= 4 and 2 <= len(k) <= 40
            and has_cjk(v) and v != k and len(v) <= 12):
        names[k] = v
print("canonical names: %d" % len(names))

# 按首词索引
by_first = defaultdict(list)
for k in names:
    by_first[k.split()[0]].append(k)
# 长名词优先匹配
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
                hits.append((n, i))
                i += len(nw)
                matched = True
                break
        if not matched:
            i += 1
    return hits

def render_check(T, v):
    if T in v:
        return ("ok", None)
    # 允许掉一个后缀字（如 火球术 -> 火球）
    if len(T) >= 3 and T[:-1] in v:
        return ("stem", T[:-1])
    sm = SequenceMatcher(None, T, v, autojunk=False)
    m = sm.find_longest_match(0, len(T), 0, len(v))
    if m.size >= 2:
        return ("lcs", v[m.b:m.b + m.size])
    return ("missing", None)

# ---- 2) 扫描 ----
report = defaultdict(list)
proposals = {}
scan_keys = [k for k in zh if k not in names]  # 长句/其他 key
for k in scan_keys:
    v = zh[k]
    if not has_cjk(v):
        continue
    for n, _ in find_names_in(k):
        T = names[n]
        if len(T) == 1:
            continue  # 单字标准名噪声太大
        kind, variant = render_check(T, v)
        if kind == "ok":
            continue
        if kind == "stem":
            # 自动修复：variant -> T（避免吃掉 T 的完整形式）
            rest = T[len(variant):]
            if rest:
                new_v = re.sub(re.escape(variant) + "(?!" + re.escape(rest) + ")", T, v)
            else:
                new_v = v.replace(variant, T)
            if new_v != v:
                proposals[k] = new_v
            report[n].append((k, v, kind, variant, new_v if new_v != v else None))
        else:
            report[n].append((k, v, kind, variant, None))

# ---- 3) 输出 ----
lines = []
total_flag = sum(len(x) for x in report.values())
lines.append("不一致名词数: %d  受影响条目: %d  可自动修复: %d" % (len(report), total_flag, len(proposals)))
for n in sorted(report, key=lambda x: -len(report[x])):
    T = names[n]
    lines.append("")
    lines.append("=== %r -> 标准译名 %r （%d 处不一致）===" % (n, T, len(report[n])))
    for k, v, kind, variant, new_v in report[n][:12]:
        lines.append("  [%s] key: %r" % (kind, k[:90]))
        lines.append("        val: %r" % v[:120])
        if variant:
            lines.append("        译法: %r  (标准 %r)" % (variant, T))
        if new_v:
            lines.append("        建议: %r" % new_v[:120])
    if len(report[n]) > 12:
        lines.append("  ... 还有 %d 处" % (len(report[n]) - 12))

open(os.path.join(HERE, "consistency_report.txt"), "w", encoding="utf-8").write("\n".join(lines))
json.dump({"names": names, "proposals": proposals},
          open(os.path.join(HERE, "fix_proposals.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("report: consistency_report.txt  (%d lines)" % len(lines))
print("proposals: fix_proposals.json  (%d)" % len(proposals))
