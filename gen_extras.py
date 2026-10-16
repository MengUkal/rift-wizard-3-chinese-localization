# -*- coding: utf-8 -*-
"""生成运行时拼接名的组合译名 → extras.json（merge_batches.py 会并入 text_zh.json）。
拼接点：
- CommonContent.py:1804  f"Skeletal {unit.name}"          （任意怪物名）
- CommonContent.py:1078  f"{tag.name} {attr_label} Bonus" （增益名）
- Equipment.py:6485      f"{tag.name} Tome"               （装备名）
- Equipment.py:6981      f"{name} Hunter's Sigil"         （装备名）
- Equipment.py:7150      f"Crown of {Sin|Virtue}"         （增益名）
- Spells.py:278          f"{spell.name} Repeater"         （增益名）
- Spells.py:6272         f"Multicast {spell.name}"        （增益名）
- RiftWizard3.py:1341    f"NUM {keyname}"                 （键帽名，0-9）
- Spells.py:8112         f"a {knight}"                    （描述格式值）
规则：绝不覆盖已有条目。
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = r"E:\SteamLibrary\steamapps\common\Rift Wizard 3"

zh = json.load(open(os.path.join(HERE, "text_zh.json"), encoding="utf-8"))

# 基础 key 只取原始提取集（batches），避免把上一轮生成的组合名再当基础名滚雪球
base = set()
for fn in os.listdir(os.path.join(HERE, "batches")):
    if re.fullmatch(r"src_\d+\.json", fn):
        with open(os.path.join(HERE, "batches", fn), encoding="utf-8") as f:
            base |= set(json.load(f))

def has_cjk(s):
    return any("\u4e00" <= c <= "\u9fff" for c in s)

# 名称样 key：首字母大写、仅字母/空格/撇号/连字符，已有中文翻译
name_re = re.compile(r"^[A-Z][A-Za-z'’\-]*(?: [A-Za-z'’\-]+)*$")
nameish = [k for k in base if name_re.match(k) and 3 <= len(k) <= 40
           and has_cjk(zh.get(k, "")) and zh[k] != k]

# tag 名与属性标签（与 split_batches.py 同源逻辑）
FILES = ["CommonContent.py","Components.py","Equipment.py","FinalBosses.py","Game.py",
         "Level.py","LevelGen.py","LevelGenHelpers.py","LevelRewards.py","Monsters.py",
         "Mutators.py","RareMonsters.py","RiftWizard3.py","Spells.py","Vaults.py"]
tag_names = set()
pat_tag = re.compile(r'Tag\(\s*["\']([A-Za-z][A-Za-z ]*?)["\']')
attrs = set()
pat_stat = re.compile(r"get_stat\(\s*['\"]([a-z_]+)['\"]")
for fn in FILES:
    src = open(os.path.join(GAME, fn), encoding="utf-8").read()
    tag_names |= set(pat_tag.findall(src))
    attrs |= set(pat_stat.findall(src))
attrs |= {"requires_los","hp_cost","damage","duration","range","radius","minion_damage",
          "minion_health","minion_range","minion_duration","num_summons","num_targets",
          "max_charges","max_channel","cooldown","shot_cooldown","strikechance","quick_cast"}

def title_case(i):
    return " ".join((w[:1].upper() + w[1:]) for w in i.replace("_", " ").split())

attr_labels = [title_case(a) for a in attrs if re.match(r"^[a-z_][a-z0-9_]*$", a)]
attr_labels += ["Requires LoS", "HP Cost"]

added, skipped = 0, 0
def put(k, v):
    global added, skipped
    if k in zh:
        skipped += 1
        return
    zh[k] = v
    added += 1

def Z(key):
    t = zh.get(key)
    return t if t and has_cjk(t) else None

# (a) Skeletal X
for n in nameish:
    put("Skeletal " + n, "骸骨" + zh[n])
# (b) {tag} {attr} Bonus
for t in sorted(tag_names):
    zt = Z(t)
    if not zt: continue
    for a in attr_labels:
        za = Z(a)
        if not za: continue
        put("%s %s Bonus" % (t, a), zt + za + "加成")
# (c) {tag} Tome
for t in sorted(tag_names):
    zt = Z(t)
    if zt: put(t + " Tome", zt + "法典")
# (d) {X} Hunter's Sigil
for n in nameish:
    put(n + " Hunter's Sigil", zh[n] + "猎手印记")
# (e) Crown of Sin / Virtue
put("Crown of Sin", "罪之王冠")
put("Crown of Virtue", "德之王冠")
# (f) {X} Repeater
for n in nameish:
    put(n + " Repeater", zh[n] + "连发")
# (g) Multicast {X}
for n in nameish:
    put("Multicast " + n, "多重施法：" + zh[n])
# (h) NUM 0-9 键帽
for d in "0123456789":
    put("NUM " + d, "小键盘" + d)
# (i) a {knight}
for en, cn in [("a Void Knight", "一名虚空骑士"), ("a Storm Knight", "一名风暴骑士"),
               ("a Chaos Knight", "一名混沌骑士"), ("a Blood Knight", "一名鲜血骑士")]:
    put(en, cn)

# (j) 精通模板（法术描述里的 [X Mastery:x]: [{mastery}:x] 行）
# 这些字面量去掉彩色标记后只剩冒号，会被提取器过滤，所以直接扫源码生成
word_zh = {"Blood": "血", "Ice": "冰", "Lightning": "闪电", "Nature": "自然", "Fire": "火",
           "Dark": "黑暗", "Eye": "眼魔", "Metallic": "金属", "Chaos": "混沌", "Sorcery": "巫术"}
mast_src_re = re.compile(r'\\n\[(\w+) Mastery:(\w+)\]: \[([^\]:]+):(\w+)\]')
for fn in FILES:
    src = open(os.path.join(GAME, fn), encoding="utf-8").read()
    for m in mast_src_re.finditer(src):
        word, k1, val, k2 = m.groups()
        wz = word_zh.get(word)
        if not wz:
            continue
        key = "\n[%s Mastery:%s]: [%s:%s]" % (word, k1, val, k2)
        put(key, "\n[%s精通:%s]：[%s:%s]" % (wz, k1, val, k2))
put("[{tag_label} Mastery:{tag_key}]: [{mastery}:{tag_key}]",
    "[{tag_label}精通:{tag_key}]：[{mastery}:{tag_key}]")

# (j2) 变异模式开场：message = intro_text + "\n\n\n\nChallenge Modifiers:"（拼接后整体查表）
intro_key = "\n\nAwaken, Wizard\n\nLong have you wandered amongst the stars\n\nWhile you rested, your deeds have become myth, and your powers faded to nought\nAges have come and gone, and Avalon has fallen into ruin\nYour ancient foe has risen once more\n\nMordred's hand reaches ever forth, his hunger endless, his malice without measure \nWhere his shadow falls, the world withers and cries out in torment\nIn the darkest night, your light sparks to life\n\nThe rift stands open\nAvalon calls her champion\n\nTake up your staff and your cloak\nGo forth, and slay Mordred\n\n"
intro_zh = zh.get(intro_key)
if intro_zh:
    put(intro_zh + "\n\n\n\nChallenge Modifiers:", intro_zh + "\n\n\n\n挑战修正：")

# (l) printf 拼接名家族（源码 .name = "..." % x 扫描结果）
tag_zh = {t: Z(t) for t in sorted(tag_names) if Z(t)}
# × 标签名
for t, zt in tag_zh.items():
    put(t + " Aura", zt + "光环")
    put(t + " Retaliation", zt + "反击")
    put(t + " Burst", zt + "爆发")
    put(t + " Armor", zt + "护甲")
    put(t + " Frenzy", zt + "狂乱")
    put(t + " Frenzy Mask", zt + "狂乱面具")
    put(t + " Swap", zt + "互换")
    put(t + " Weakness", zt + "弱点")
# × 怪物/装备名（nameish）
for n in nameish:
    zn = zh[n]
    put("Summon " + n, "召唤" + zn)
    put("Respawn As " + n, "重生为" + zn)
    put(n + " Spawner", zn + "生成器")
    put("Touched by " + n, zn + "之触")
    put(n + " Egg", zn + "蛋")
    put(n + " Oculus", zn + "魔眼")
    put("Robe of " + n, zn + "法袍")
    put("Chalice of " + n, zn + "圣杯")
    put(n + " Curse Doll", zn + "咒术人偶")
    put(n + " Queen", zn + "女王")
    put("Baby " + n, "幼年" + zn)
    put(n + " Swarm Summon", zn + "虫群召唤")
    put("Slimy " + n, "黏滑" + zn)
# 杂项
put("Robe of Void", "虚空法袍")
put("Chalice of Void", "虚空圣杯")
put("Robe of Fire", "火焰法袍")
put("Chalice of Fire", "火焰圣杯")

# (m) 长名截断别名：裂隙预览面板在翻译前把 >20 字符的名字截成前 18 字符+".."再查表
#     （RiftWizard3.py:7770），所以为所有长名字补截断形式的 key
for n in nameish:
    if len(n) > 20:
        put(n[:18] + "..", zh[n])

# (n) 源码里拼好的纯标记 fmt 串（resolve_fmt 会拿它查 T，查不到原样显示英文）
#     Spells.py:1301-1302 的 buff_kw 等；防御性地把常见状态词都补上
fmt_status_zh = {
    "bleed": "流血", "bleeding": "流血", "poison": "毒素", "poisoned": "中毒",
    "stun": "眩晕", "stunned": "眩晕", "frozen": "冰冻", "freeze": "冰冻",
    "glassed": "玻璃化", "glassified": "玻璃化", "petrified": "石化", "petrification": "石化",
    "burn": "灼烧", "burning": "灼烧", "soaked": "潮湿", "silenced": "沉默",
    "blinded": "致盲", "blind": "致盲", "feared": "恐惧", "berserk": "狂暴", "berserked": "狂暴",
    "necrosis": "坏死", "immobilized": "定身", "stasis": "停滞",
}
for w, c in fmt_status_zh.items():
    put("[%s]" % w, "[%s:%s]" % (c, w))
put("[glassed] or [petrified]", "[玻璃化:glassed]或[石化:petrified]")

# (q) 裸状态词：fmt 直接传单词（无括号、无标记），如 "施加 poison，持续 3 回合"
for w, c in fmt_status_zh.items():
    put(w, c)
put("slimes", "黏液怪")

# (r) 召唤系法术名："Summon X" 与运行时加复数的 "Summon Xs"
for n in nameish:
    zn = zh[n]
    put("Summon " + n, "召唤" + zn)
    put("Summon " + n + "s", "召唤" + zn)

# (p) 追加修复：漏网拼接名 + 运行时 fmt 词
put("MUTATED_RUN", "变异模式")
put("blink", "闪现")
put("hop", "跳跃")
# 召唤系临时单位名：CommonContent.py:389 spawn_name = "temporary " + spawn_name
for n in nameish:
    put("temporary " + n, "临时" + zh[n])
# 拼接漏网的 5 个弹系名
for t in ("Arcane", "Ice", "Physical"):
    zt = Z(t)
    if zt:
        put(t + " Bolt", zt + "弹")
for t, extra in (("Holy", "神圣"), ("Slime", "黏液")):
    zt = Z(t)
    if zt:
        put(t + " Ball", extra + "球")

# (k) 筛选器相关固定串（兜底，缺才补）
put("Toggle this filter", "切换此筛选器")
put("Filter tags", "筛选标签")
put("Filter attributes", "筛选属性")
put("Filter attribute bonuses", "筛选属性加成")
put("Show filters", "显示筛选器")

# (o) 变异项类名（自定义模式列表走 cls.__name__ 反射，源码无字面量）
CLASS_ZH = {
    "SpellStatMultiplier": "法术属性倍率",
    "SpellTagRestriction": "法术标签限制",
    "EquipmentTagRestriction": "装备标签限制",
    "SpellTagElimination": "法术标签移除",
    "EnemyBuff": "敌方强化",
    "ExtraSpawns": "额外生成",
    "FixedRewards": "固定奖励",
    "RemoveRewards": "移除奖励",
    "RespawnAsMutator": "重生变异",
    "LevelOneRewards": "首层奖励",
    "EnemyResistance": "敌方抗性",
    "PlayerVulnerability": "玩家易伤",
    "Weather": "天气",
    "DamageDebuff": "伤害削弱",
    "RandomSpellRestriction": "随机法术限制",
    "RandomEquipmentRestriction": "随机装备限制",
    "SpellLevelElimination": "法术等级移除",
    "SpellLevelRestriction": "法术等级限制",
    "SpBonus": "SP加成",
    "SpPenalty": "SP惩罚",
    "SpPerLevel": "每层SP",
    "ExtraElites": "额外精英",
    "NumPortals": "传送门数量",
    "MonsterHPMult": "怪物生命倍率",
    "EnemyShields": "敌方护盾",
    "SpellHPCostAdd": "法术生命消耗增加",
    "Attrition": "消耗战",
    "SuperSpawners": "超级生成器",
    "SpellCooldowns": "法术冷却",
    "Forgetful": "健忘",
    "Awestruck": "敬畏",
    "Treachery": "背叛",
    "Thieving": "盗窃",
    "Crumbling": "崩塌",
    "LevelOneMegaChests": "首层巨型宝箱",
    "BonusRerolls": "额外重掷",
    "MoreSpawners": "更多生成器",
    "FewerSpawners": "更少生成器",
    "HarderMonsters": "更强敌人",
    "ExtraComponents": "额外组件",
    "Confinement": "禁锢",
    "OneSpell": "单法术",
    "GiantSlayer": "屠巨者",
    "MemoryLeak": "记忆泄漏",
    "Amnesiac": "失忆者",
    "WildMagic": "狂野魔法",
    "BloodRites": "血礼",
    "Flawless": "无瑕",
    "Chronomancer": "时空法师",
    "SpawnWizards": "生成法师",
    "MordredsVengeance": "莫德雷德的复仇",
    "Scavenger": "拾荒者",
}
for cn, cz in CLASS_ZH.items():
    put(cn, cz)

with open(os.path.join(HERE, "extras.json"), "w", encoding="utf-8") as f:
    json.dump(zh, f, ensure_ascii=False, indent=1, sort_keys=True)
print("nameish keys: %d" % len(nameish))
print("added: %d, skipped(existing): %d, total now: %d" % (added, skipped, len(zh)))
for probe in ["Skeletal Goblin", "Fire Tome", "Sorcery Max Charges Bonus", "Crown of Sin",
              "Multicast Death Bolt", "Death Bolt Repeater", "NUM 1"]:
    print("  %r -> %r" % (probe, zh.get(probe)))
