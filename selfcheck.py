# -*- coding: utf-8 -*-
"""全量自查：格式安全 / 一致性 / 残留 / 未翻译 / 双字 / 3半径"""
import json, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")

GAME = r"E:\SteamLibrary\steamapps\common\Rift Wizard 3"
zh = json.load(open(GAME + r"\mods\ChineseLocalization\text_zh.json", encoding="utf-8"))
old = json.loads(subprocess.run(["git", "show", "a5fcb20:text_zh.json"],
                                capture_output=True, cwd=r"E:\写小说、文字工作\rw3-汉化").stdout.decode("utf-8"))
PH = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")

def phs(s):
    return set(PH.findall(s))

def has_cjk(s):
    return any("\u4e00" <= c <= "\u9fff" for c in s)

# A. 值里出现 key 没有的占位符（显示时 KeyError 崩溃风险）
extra_ph = []
for k, v in zh.items():
    kp, vp = phs(k), phs(v)
    if vp - kp:
        extra_ph.append((k, sorted(vp - kp), v[:100]))
print("A. 值含 key 未定义的占位符（崩溃风险）: %d" % len(extra_ph))
for x in extra_ph[:25]:
    print("   ", repr(x[0][:70]), "extra=", x[1], "V=", repr(x[2][:90]))

# B. key 有占位符，但值里有非法花括号（format 异常）
brace_bad = []
for k, v in zh.items():
    if "{" in v or "}" in v:
        stripped = PH.sub("", v)
        if "{" in stripped or "}" in stripped:
            brace_bad.append((k, v[:100], bool(phs(k))))
print("\nB. 值含非法花括号: %d（其中 key 带占位符=%d）" %
      (len(brace_bad), sum(1 for b in brace_bad if b[2])))
for b in brace_bad[:25]:
    print("   ", repr(b[0][:70]), "V=", repr(b[1][:90]), "key有占位符" if b[2] else "")

# C. 值含 format spec（如 {damage:d}）→ 非数字会崩
spec_bad = [(k, v[:100]) for k, v in zh.items() if re.search(r"\{[A-Za-z_]\w*:[^}]*\}", v)]
print("\nC. 值含 format spec: %d" % len(spec_bad))
for k, v in spec_bad[:20]:
    print("   ", repr(k[:70]), "V=", repr(v[:90]))

# D. 双字事故
pat = re.compile(r"(.)(.)\1\2", re.S)
bad2 = []
for k, nv in zh.items():
    ov = old.get(k) or ""
    if nv == ov:
        continue
    for m in pat.finditer(nv):
        if m.group(0) not in ov:
            bad2.append((k, m.group(0)))
            break
print("\nD. 新增双字事故: %d" % len(bad2), bad2[:10])

# E. 未翻译：无汉字的值（排除纯符号/ID）
no_cjk = [(k, v) for k, v in zh.items() if not has_cjk(v) and v != k]
print("\nE. 无汉字译名: %d" % len(no_cjk))
for k, v in no_cjk[:20]:
    print("   ", repr(k[:60]), "->", repr(v[:50]))

# F. 中英混杂：有汉字且含 3+ 连续字母（排除常见保留词）
KEEP = ("HP", "SP", "SH", "PGUP", "PGDN", "DPS", "LoS", "DMG", "MOD", "URL", "ID", "SL", "AOE", "RNG")
mixed = []
for k, v in zh.items():
    if not has_cjk(v):
        continue
    for m in re.finditer(r"[A-Za-z]{3,}", v):
        w = m.group(0)
        if w.upper() in KEEP:
            continue
        mixed.append((k, w, v[:90]))
        break
print("\nF. 中英混杂(3+字母): %d" % len(mixed))
for x in mixed[:30]:
    print("   ", repr(x[0][:60]), "词=", x[1], "V=", repr(x[2][:80]))

# G. 3 半径 相关
print("\nG. 值含 '半径' 且行首为数字:")
for k, v in zh.items():
    if re.search(r"(^|\n)\s*\d+ ?半径", v):
        print("   ", repr(k[:70]), "V=", repr(v[:100]))
print("   值含 {radius} 且 半径:")
for k, v in zh.items():
    if "半径" in v and "{radius}" in v and "[{radius}:radius]" not in v:
        print("   ", repr(k[:70]), "V=", repr(v[:100]))
