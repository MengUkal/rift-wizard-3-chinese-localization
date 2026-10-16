# -*- coding: utf-8 -*-
"""扫描译文中残留的英文单词碎片（显示层），输出报告 → sweep_words.txt"""
import json, os, re, sys

GAME = r"E:\SteamLibrary\steamapps\common\Rift Wizard 3"
HERE = os.path.dirname(os.path.abspath(__file__))
zh = json.load(open(os.path.join(GAME, "mods", "ChineseLocalization", "text_zh.json"), encoding="utf-8"))

ALLOW_WORDS = {
    "HP", "SH", "SP", "LoS", "DISCORD", "PGUP", "PGDN", "NUM", "MOD", "API",
    "PS", "VS", "DLC", "UI", "AOE", "BUFF", "DEBUFF", "DOT",
}
allow_re = re.compile(r"^(?:%s)$" % "|".join(ALLOW_WORDS))

word_re = re.compile(r"[A-Za-z][A-Za-z']{0,20}")
# 切出显示层：去掉 {占位符}；[显示:key] 只保留显示部分
def display_parts(v):
    v = re.sub(r"\{[^{}]*\}", " ", v)
    # [display:key] -> display；[bare] -> bare
    def repl(m):
        inner = m.group(1)
        return inner.split(":", 1)[0]
    return re.sub(r"\[([^\[\]]+)\]", repl, v)

from collections import Counter
words = Counter()
where = {}
for k, v in zh.items():
    disp = display_parts(v)
    for w in word_re.findall(disp):
        wl = w.strip("'")
        if len(wl) < 2:
            continue
        if allow_re.match(wl.upper()) or allow_re.match(wl):
            continue
        words[wl] += 1
        where.setdefault(wl, []).append((k, v))

lines = []
for w, c in words.most_common():
    lines.append("WORD %r x%d" % (w, c))
    for k, v in where[w][:2]:
        lines.append("    KEY: %r" % k[:100])
        lines.append("    VAL: %r" % v[:110])
lines.append("")
lines.append("distinct words: %d" % len(words))
lines.append("values needing repair: %d" % len({k for w in words for k, _ in where[w]}))
# 单独导出需修复的 (key, value) 全列表
badkeys = {}
for w in words:
    for k, v in where[w]:
        badkeys[k] = v
with open(os.path.join(HERE, "repair_keys.json"), "w", encoding="utf-8") as f:
    json.dump(badkeys, f, ensure_ascii=False, indent=1)
lines.append("repair_keys.json written")
open(os.path.join(HERE, "sweep_words.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("done, distinct=%d repair=%d" % (len(words), len(badkeys)))
