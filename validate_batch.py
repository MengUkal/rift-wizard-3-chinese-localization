# -*- coding: utf-8 -*-
"""校验一个翻译批次并落盘 zh_NN.json。
用法: python validate_batch.py NN
要求 batches/build_NN.py 定义 dict T（key=英文原句, value=中文）。
检查通过 → 写 batches/zh_NN.json（按 src 顺序），打印 PASS。
否则打印全部问题（前 20 条），退出码 1。
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
N = sys.argv[1]
src_path = os.path.join(HERE, "batches", "src_%s.json" % N)
build_path = os.path.join(HERE, "batches", "build_%s.py" % N)
out_path = os.path.join(HERE, "batches", "zh_%s.json" % N)

with open(src_path, encoding="utf-8") as f:
    src = json.load(f)

ns = {}
with open(build_path, encoding="utf-8") as f:
    code = f.read()
exec(compile(code, build_path, "exec"), ns)
T = ns.get("T")
if not isinstance(T, dict):
    print("FAIL: build_%s.py 未定义 dict T" % N); sys.exit(1)

ALLOW_IDENTITY = {"SP", "HP", "SH", "LoS"}
ph_re = re.compile(r"\{[^{}]*\}")
tok_re = re.compile(r"\[([^\]:]*)\(?::([^\]]*)?\]?")  # 粗提 [name] / [name:tag]
def tokens(s):
    out = []
    for m in re.finditer(r"\[([^\]:]+)(?::([^\]]+))?\]", s):
        out.append((m.group(1), m.group(2)))
    return out

errors, warns = [], []
missing = [k for k in src if k not in T]
extra = [k for k in T if k not in set(src)]
if missing: errors.append("缺 %d 个 key，如: %r" % (len(missing), missing[:3]))
if extra: errors.append("多 %d 个 key，如: %r" % (len(extra), extra[:3]))

for k in src:
    if k not in T: continue
    v = T[k]
    if not isinstance(v, str) or not v.strip():
        errors.append("空译文: %r" % k[:60]); continue
    # 占位符：value 必须是 key 的子集（{s}/{suffix} 可删）
    kp, vp = ph_re.findall(k), ph_re.findall(v)
    if set(vp) - set(kp):
        errors.append("多余占位符 %s: %r" % (sorted(set(vp)-set(kp)), k[:60]))
    if len(vp) != len(kp) and set(vp) != set(kp):
        miss_ph = [p for p in kp if p not in vp and p not in ("{s}", "{suffix}")]
        if miss_ph:
            errors.append("丢失占位符 %s: %r" % (miss_ph, k[:60]))
    # 标记冒号部分
    kt, vt = tokens(k), tokens(v)
    if len(kt) != len(vt):
        # 允许给裸 token 补 :key
        if not (len(kt) == len(vt)):
            errors.append("[]标记数量不同: %r" % k[:60])
    else:
        for (kn, ktag), (vn, vtag) in zip(kt, vt):
            if kn.strip().lower() == "asseticon":
                if (kn, ktag) != (vn, vtag):
                    errors.append("asseticon 被改动: %r" % k[:60])
                continue
            if ktag != vtag:
                # 允许：原本无 tag，且新 tag == 原显示名小写（纯字母词）
                if ktag is None and vtag is not None and re.fullmatch(r"[A-Za-z][A-Za-z ]*", kn) \
                   and vtag == kn.strip().lower():
                    continue
                errors.append("标记 key 不一致 %r→%r: %r" % (ktag, vtag, k[:60]))
    # 换行数
    if k.count("\n") != v.count("\n"):
        errors.append("换行数不同: %r" % k[:60])
    # 首尾空格
    for label, a, b in (("首", k[:1], v[:1]), ("尾", k[-1:], v[-1:])):
        if a.isspace() and not b.isspace():
            errors.append("%部空格丢失: %r" % (label, k[:60]))
    # 内容检查
    if v == k and k not in ALLOW_IDENTITY and not k.startswith("%s"):
        warns.append("未翻译(与原文相同): %r" % k[:60])
    if not any("\u4e00" <= c <= "\u9fff" for c in v) and k not in ALLOW_IDENTITY and not k.startswith("%s"):
        core = re.sub(r"\{[^{}]*\}|\[[^\]]*\]|[^\w]", "", k)
        if len(core) > 3:
            warns.append("译文无汉字: %r → %r" % (k[:40], v[:40]))

if errors:
    print("FAIL (%d 条):" % len(errors))
    for e in errors[:20]: print("  " + e)
    sys.exit(1)

data = {k: T[k] for k in src}
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print("PASS: %d 条 → zh_%s.json" % (len(data), N))
if warns:
    print("警告 %d 条:" % len(warns))
    for w in warns[:10]: print("  " + w)
