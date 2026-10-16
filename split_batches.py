# -*- coding: utf-8 -*-
"""把 keys.json 整理成翻译批次：
- 丢弃"生成的属性标签"里非真实属性的垃圾 key（真实属性 = get_stat()/filter_attr_/formatted_attrs 里出现过的）
- 补充运行时拼接的组合名（"%s Ball/Beam/Bolt" × 全部 Tag 名）
- 按 ~340 条一批切分，写入 batches/src_NN.json（JSON 数组，元素为英文原句）
用法: python split_batches.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = r"E:\SteamLibrary\steamapps\common\Rift Wizard 3"
BATCH_DIR = os.path.join(HERE, "batches")
os.makedirs(BATCH_DIR, exist_ok=True)

FILES = [
    "CommonContent.py", "Components.py", "Equipment.py", "FinalBosses.py",
    "Game.py", "Level.py", "LevelGen.py", "LevelGenHelpers.py", "LevelRewards.py",
    "Monsters.py", "Mutators.py", "RareMonsters.py", "RiftWizard3.py",
    "Spells.py", "SteamAdapter.py", "Vaults.py", "text.py",
]

with open(os.path.join(HERE, "keys.json"), encoding="utf-8") as f:
    entries = json.load(f)

# ---- 收集真实属性名 ----
attrs = set()
pat_stat = re.compile(r"get_stat\(\s*['\"]([a-z_]+)['\"]")
pat_self = re.compile(r"self\.([a-z_]+)\s*=")
for fn in FILES:
    src = open(os.path.join(GAME, fn), encoding="utf-8").read()
    attrs |= set(pat_stat.findall(src))
attrs |= {"requires_los", "hp_cost", "damage", "duration", "range", "radius",
          "minion_damage", "minion_health", "minion_range", "minion_duration",
          "num_summons", "num_targets", "max_charges", "max_channel", "cooldown",
          "shot_cooldown", "strikechance", "quick_cast", "shields"}

def title_case(i):
    return " ".join((w[:1].upper() + w[1:]) for w in i.replace("_", " ").split())

real_labels = {title_case(a) for a in attrs if re.match(r"^[a-z_][a-z0-9_]*$", a)}
real_labels |= {"Requires LoS", "HP Cost"}

# ---- 收集 Tag 名（用于组合名 & 校验）----
tag_names = set()
pat_tag = re.compile(r'Tag\(\s*["\']([A-Za-z][A-Za-z ]*?)["\']')
for fn in FILES:
    src = open(os.path.join(GAME, fn), encoding="utf-8").read()
    tag_names |= set(pat_tag.findall(src))

# ---- 过滤 + 组合补充 ----
kept, dropped = [], 0
seen = set()
for e in entries:
    k = e["k"]
    if k in seen:
        continue
    seen.add(k)
    if e.get("gen"):
        if k not in real_labels:
            dropped += 1
            continue
    kept.append(k)

composed = []
for t in sorted(tag_names):
    for tmpl in ("%s Ball", "%s Beam", "%s Bolt"):
        s = tmpl % t
        if s not in seen:
            seen.add(s)
            composed.append(s)

allkeys = kept + composed
print("tag names (%d): %s" % (len(tag_names), ", ".join(sorted(tag_names))))
print("keys: %d kept + %d composed = %d (dropped %d junk labels)" % (len(kept), len(composed), len(allkeys), dropped))

# ---- 切批 ----
BATCH = 340
batches = [allkeys[i:i + BATCH] for i in range(0, len(allkeys), BATCH)]
for idx, b in enumerate(batches):
    with open(os.path.join(BATCH_DIR, "src_%02d.json" % idx), "w", encoding="utf-8") as f:
        json.dump(b, f, ensure_ascii=False, indent=1)
    print("src_%02d.json  %4d keys  %6d chars" % (idx, len(b), sum(len(s) for s in b)))
