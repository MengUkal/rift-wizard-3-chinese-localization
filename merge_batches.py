# -*- coding: utf-8 -*-
"""合并全部批次译文 → text_zh.json，输出覆盖率报告。
用法: python merge_batches.py
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH_DIR = os.path.join(HERE, "batches")

ALLOW_IDENTITY = {"SP", "HP", "SH", "LoS"}
merged = {}
dup = []
batches_present, batches_missing = [], []

names = sorted(f for f in os.listdir(BATCH_DIR) if re.fullmatch(r"src_\d+\.json", f))
for src_name in names:
    n = src_name[4:6]
    zh_path = os.path.join(BATCH_DIR, "zh_%s.json" % n)
    if not os.path.exists(zh_path):
        batches_missing.append(n)
        continue
    with open(zh_path, encoding="utf-8") as f:
        data = json.load(f)
    batches_present.append((n, len(data)))
    for k, v in data.items():
        if k in merged and merged[k] != v:
            dup.append(k)
        merged[k] = v

out = os.path.join(HERE, "text_zh.json")
extras_path = os.path.join(HERE, "extras.json")
if os.path.exists(extras_path):
    with open(extras_path, encoding="utf-8") as f:
        extras = json.load(f)
    for k, v in extras.items():
        merged.setdefault(k, v)

# 后处理：把译文里裸的下划线属性标记 [num_summons] 换成 [召唤物数量:num_summons]，
# 游戏会照常着色（幂等：已带 :key 的标记不会被匹配）
# 强制覆盖：显示用的 ID 与无法中文化的英文语法占位符
FORCE = {
    "MUTATED_RUN": "变异模式",  # 运行模式名，显示在 HUD 与结算
    "Has a {chance}% chance each turn to spawn {num} {spawn}": "每回合有 {chance}% 几率生成 {spawn}",  # {num} 会传 "a"/数字，中文省略
    "Each turn spawns {num} {spawn}": "每回合生成 {spawn}",
    "LANGUAGE": "语言",  # 语言选择菜单标题
    "{num} HP": "{num} 生命",  # 图鉴召唤物预览
    # 英文单复数词作参数的模板（{turns}/{kw}/{s}/{aan}），中文一律省略或改写
    "When an enemy takes {dtype} damage, it has a {chance}% chance to be afflicted with [{duration}:duration] {turns} of [{status}]":
        "敌人受到 {dtype} 伤害时，有 {chance}% 几率被附加 [{duration}:duration] 回合的 [{status}]",
    "At the beginning of each level, enemies are [stunned] for [{duration}:duration] {turns}":
        "每层开始时，敌人陷入 [眩晕:stunned] [{duration}:duration] 回合",
    "Triggers in {turns} {kw}": "{turns} 回合后触发",
    "Pull the target {tiles} tile{s} toward the caster": "将目标向施法者方向拉拽 {tiles} 格",
    "Inflict {buff} for {duration} turn{s}": "施加 {buff}，持续 {duration} 回合",
    "Cast time: {turns} turns": "引导时间：{turns} 回合",
    "Can be channeled for {turns} turns": "可引导 {turns} 回合",
    "Spawn a {monster} every {min_turns} to {max_turns} turns\nNext spawn: {turns} turns":
        "每 {min_turns} 至 {max_turns} 回合生成一只 {monster}\n下次生成：{turns} 回合",
    "Upgrade {s}:": "强化 {s}：",
}
for _k, _v in FORCE.items():
    merged[_k] = _v

# 译名统一（gen_unify.py 生成）：标准名覆盖 + 按英文名词限定范围的句子内替换
UNIFY_PATH = os.path.join(HERE, "term_unify.json")
if os.path.exists(UNIFY_PATH):
    with open(UNIFY_PATH, encoding="utf-8") as _uf:
        _u = json.load(_uf)
    for _k, _v in _u.get("overrides", {}).items():
        merged[_k] = _v
    _hit = 0
    for _rule in _u.get("rules", []):
        _sc = re.compile(_rule["scope"]) if _rule.get("scope") else None
        _ex = re.compile(_rule["exclude"]) if _rule.get("exclude") else None
        for _k in list(merged):
            if _sc is not None and not _sc.search(_k):
                continue
            if _ex is not None and _ex.search(_k):
                continue
            _v = merged[_k]
            for _f, _r in _rule["pairs"]:
                _v = re.sub(_f, _r, _v)
            if _v != merged[_k]:
                merged[_k] = _v
                _hit += 1
    print("译名统一: 标准名覆盖 %d 条，句子规则命中 %d 条" % (len(_u.get("overrides", {})), _hit))
else:
    print("!! 缺少 term_unify.json，跳过译名统一")

bare_tok = re.compile(r"\[([a-z][a-z_]{2,})\]")
LABELS = {
    "minion_damage": "召唤物伤害",
    "minion_health": "召唤物生命",
    "minion_range": "召唤物射程",
    "minion_duration": "召唤物持续",
    "minion_summons": "召唤物数量",
    "num_summons": "召唤物数量",
    "num_targets": "目标数量",
    "max_charges": "最大充能",
    "quick_cast": "快速施法",
}
fixed = 0
for k, v in merged.items():
    if "[" in v:
        nv = bare_tok.sub(lambda m: "[%s:%s]" % (LABELS.get(m.group(1), m.group(1)), m.group(1)), v)
        if nv != v:
            merged[k] = nv
            fixed += 1
            v = nv
    # 英文冠词占位符 {aan} 在中文里无意义，剔除
    if "{aan}" in v:
        nv = v.replace("{aan} ", "").replace("{aan}", "")
        while "  " in nv:
            nv = nv.replace("  ", " ")
        merged[k] = nv
        fixed += 1

with open(out, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1, sort_keys=True)
print("裸属性标记已转彩显: %d 条" % fixed)

identity = [k for k, v in merged.items() if v == k and k not in ALLOW_IDENTITY]
no_cjk = [k for k, v in merged.items()
          if not any("\u4e00" <= c <= "\u9fff" for c in v) and k not in ALLOW_IDENTITY
          and not k.startswith("%s")
          and len(re.sub(r"\{[^{}]*\}|\[[^\]]*\]|[^\w]", "", k)) > 3]

print("批次完成: %s" % ", ".join("%s(%d)" % t for t in batches_present))
if batches_missing:
    print("!! 缺批次: %s" % ", ".join(batches_missing))
print("合并总数: %d → %s" % (len(merged), out))
if dup:
    print("跨批重复且译文不一致: %d 个，如 %r" % (len(dup), dup[:5]))
print("保留原文(与英文相同): %d 个" % len(identity))
for k in identity[:15]:
    print("   =", k[:80])
print("无汉字译文: %d 个" % len(no_cjk))
for k in no_cjk[:15]:
    print("   ~", k[:60], "→", merged[k][:40])
