# -*- coding: utf-8 -*-
"""生成 term_unify.json：译名统一表。
- overrides: 直接覆盖标准名（key -> 新值）
- rules: 按英文名词限定范围的句子内替换 [{scope, exclude?, pairs:[[find,repl],...]}]
merge_batches.py 在 FORCE 之后应用。
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))

overrides = {
    # 标准名本身改成句子/语境里更顺的写法
    "Beam": "光束",
    "Wyrm": "蛟龙",
    "Faeries": "仙灵",
    "Channeling": "引导",
    "Pain": "痛苦魔",
    "Pale Rider": "苍白骑士",
    "Castellan Clogs": "城主木屐",
    "Hag's Eye": "夜巫婆之眼",
    "Seal of Searing": "灼热封印",
    "Bafflement, Demon King": "困惑·魔王",
    "Mordred, Unbound": "莫德雷德·未绑定",
    "%s Frenzy": "%s 狂乱",
    "%s Frenzy Mask": "%s 狂乱面具",
    "%s Curse Doll": "%s 咒术人偶",
}

def R(scope, *pairs, exclude=None):
    d = {"pairs": [list(p) for p in pairs]}
    if scope:
        d["scope"] = scope
    if exclude:
        d["exclude"] = exclude
    return d

rules = [
    # 黏液怪家族
    R(r"\bGreen Slime\b", (r"绿色黏液(?!怪)", "绿色黏液怪"), (r"绿黏液怪", "绿色黏液怪")),
    R(r"\bVoid Slimes?\b", (r"虚空黏液(?!怪)", "虚空黏液怪")),
    R(r"\bBlood Slimes?\b", (r"(?<!鲜)血黏液", "鲜血黏液")),
    R(r"turned into slimes of matching types", (r"电黏液怪", "闪电黏液怪"), (r"冰黏液怪", "冰霜黏液怪")),
    # 法术/怪物显示名
    R(r"\bThunder Strike\b", (r"雷击", "雷霆打击"), (r"雷袭", "雷霆打击")),
    R(r"\bLeghead\b", (r"腿首(?!怪)", "腿首怪"), (r"腿头怪", "腿首怪")),
    R(r"\bGolden Skull\b", (r"黄金骷髅(?!头)", "黄金骷髅头"), (r"黄金头骨", "黄金骷髅头")),
    R(r"\bNight Hag\b", (r"夜婆", "夜巫婆")),
    R(r"\bHag's Eye\b", (r"夜婆之眼", "夜巫婆之眼")),
    R(r"\bAnnihilate\b", (r"湮灭", "歼灭")),
    R(r"\bSeal Fate\b", (r"命运封印", "封印命运")),
    R(r"\bLightning Tether\b", (r"闪电系绳", "闪电锁链")),
    R(r"\bFire Breath\b", (r"火息", "火焰吐息")),
    R(r"\bPyrostatic Pulse\b", (r"焰电脉冲", "静炎脉冲")),
    R(r"\bFiery Tormentor\b", (r"烈焰折磨者", "灼焰折磨者")),
    R(r"\bFiery Tormenting Mass\b", (r"炽焰折磨之团", "灼焰折磨之团")),
    R(r"\bPrismatic Beam\b", (r"棱镜光束", "棱彩光束")),
    R(r"Melt", (r"融化", "熔化"), (r"熔解", "熔化"), (r"熔毁", "熔化")),  # Melt/Melts/Melted 全族统一「熔化」
    R(r"\bSpike Ball\b", (r"(?<!尖)刺球", "尖刺球")),
    R(r"\bSpikeball\b", (r"铜刺球", "铜制尖刺球")),
    R(r"\bCopper Spike Ball\b", (r"铜刺球", "铜制尖刺球"), (r"铜尖刺球", "铜制尖刺球")),
    R(r"\bPrison of Thorns\b", (r"荆棘监狱", "荆棘牢狱"), (r"荆棘囚笼", "荆棘牢狱")),
    R(r"\bEye of Rage\b", (r"怒火之眼", "怒之眼")),
    R(r"\bWorm Shambler\b", (r"蠕虫徘徊者", "蠕虫蹒跚怪"), (r"蠕虫蹒跚者", "蠕虫蹒跚怪")),
    R(r"\bBone Shambler\b", (r"骸骨蹒跚者", "骨蹒跚怪"), (r"白骨蹒跚者", "骨蹒跚怪")),
    R(r"\bLumbriogenesis\b", (r"蚓体生成", "蠕虫生成术")),
    R(r"\bFloating Eye\b", (r"悬浮之眼", "浮空之眼")),
    R(r"\bFireball\b", (r"火球(?!术)", "火球术"), exclude=r"Living Fireball"),
    R(r"\bFlame Rift\b", (r"烈焰裂隙", "火焰裂隙")),
    R(r"\bSummon Blade\b", (r"召唤魔刃", "召唤利刃")),
    R(r"\bFlesh Fiend\b", (r"血肉恶鬼", "血肉魔鬼")),
    R(r"\bWatcher\b", (r"守视者", "看守者")),
    R(r"\bEye Helm\b", (r"眼盔", "眼魔头盔")),
    R(r"\bRaiment of Eyes\b", (r"万目衣", "千眼法衣")),
    R(r"\bEldritch\b", (r"妖异", "邪异")),
    R(r"\bCarnival of Pain\b", (r"苦痛狂欢节", "痛苦狂欢")),
    R(r"\bChaos Fiend\b", (r"混沌恶魔", "混沌魔")),
    R(r"\bFearface\b", (r"惧面兽", "惧面怪")),
    R(r"(?i)drain", (r"汲取", "吸取")),
    R(r"Drains a spell charge", (r"吸取 1 个法术充能", "吸取一个法术充能"), (r"消耗 1 个法术充能", "吸取一个法术充能")),
    R(r"\bSpreads\b", (r"传染", "蔓延")),
    R(r"Summon Blizzards, Storm Clouds", (r"雷云", "风暴云")),
    R(r"\bGhost\b", (r"幽灵", "幽魂")),
    R(r"Summon Death instead of a Ghost", (r"死神", "死亡")),
    R(r"\bShared Pain\b", (r"共痛", "痛苦共享"), (r"共同痛苦", "痛苦共享")),
    R(r"\bBlood Knight\b", (r"(?<!鲜)血骑士", "鲜血骑士")),
    R(r"\bDeath Chill\b", (r"死亡寒息", "死亡冻寒")),
    R(r"\bWinterbringer\b", (r"携冬者", "凛冬使者")),
    R(r"\bOrochi\b", (r"(?<!八岐)大蛇", "八岐大蛇")),
    R(r"\bAnnihilation Goo\b", (r"湮灭软泥", "湮灭黏浆")),
    R(r"\bCombust Poison\b", (r"引爆毒素", "毒素引燃")),
    R(r"\bStonefish\b", (r"石头鱼", "石鱼")),
    R(r"\bIce Faery\b", (r"冰妖精", "冰霜仙灵")),
    R(r"\bAether Spider", (r"以太蛛类", "以太蜘蛛")),
    R(r"\bCorrosion\b", (r"侵蚀", "腐蚀")),
    R(r"\bChain Lightning\b", (r"链式闪电", "连锁闪电")),
    R(r"\bBlood Bullet\b", (r"鲜血子弹", "血弹")),
    R(r"\bRuby Heart\b", (r"红玉之心", "红宝石之心")),
    R(r"\bIce Wyrm\b", (r"冰龙虫", "寒冰蛟龙")),
    R(r"\bIce Drake\b", (r"(?<!寒)冰幼龙", "寒冰幼龙")),
    R(r"\bFire Drake\b", (r"火幼龙", "火焰幼龙")),
    R(r"\bFire Elemental\b", (r"火焰元素", "火元素")),
    R(r"\bEye of Fire\b", (r"火之眼", "火焰之眼")),
    R(r"\bDream the Starwhale\b", (r"梦见星鲸", "梦游星鲸")),
    R(r"\bFreezing Coral\b", (r"冻结珊瑚", "冻凝珊瑚")),
    R(r"\bBishop Boots\b", (r"主教靴", "主教长靴")),
    R(r"\bDream Thief Diadem\b", (r"窃梦冠冕", "窃梦头冠")),
    R(r"\bPsychopomp Staff\b", (r"渡魂法杖", "引魂者法杖")),
    R(r"\bHypno Bauble\b", (r"催眠饰珠", "催眠小饰品")),
    R(r"\bSlimebirth Cantromancy\b", (r"黏液诞生术", "黏液降生坎特罗术")),
    R(r"\bSlimy Voodoo Mantle\b", (r"黏滑巫毒披风", "黏液巫毒披风")),
    R(r"\bPrism of Shattered Sensations\b", (r"破碎感知棱镜", "碎感棱镜")),
    R(r"\bCyst of Eternal Bloom\b", (r"永恒绽放囊肿", "永绽囊肿")),
    R(r"\bOrb of Infinite Slaughter\b", (r"无尽屠戮宝珠", "无尽杀戮宝珠")),
    R(r"\bChaos Scale Crown\b", (r"混沌之鳞王冠", "混沌鳞冠")),
    R(r"\bWyrm Spirit Armor\b", (r"蟠龙之魂护甲", "龙灵护甲")),
    R(r"\bBonus HP\b", (r"额外生命", "加成生命")),
    R(r"\bArcane Warding\b", (r"奥术守卫", "奥术守护")),
    R(r"\bRot\b", (r"腐化", "腐烂")),
    R(r"\bWolves\b", (r"狼获得", "狼群获得")),
    R(r"\bGoatia\b", (r"献祭山羊", "山羊魔")),
    R(r"\bGolden Bull\b", (r"黄金之牛", "黄金公牛")),
    # —— 第二遍：修正 gen_extras 用旧标准名烘焙进组合名的残留（如 幼年射线/临时痛楚）——
    R(r"\bBeam", (r"射线", "光束")),
    R(r"Faeries", (r"仙灵群", "仙灵")),
    R(r"\bPain\b", (r"痛楚", "痛苦魔")),
    R(r"\bPale Rider", (r"灰骑士", "苍白骑士")),
    R(r"\bCastellan Clogs\b", (r"木鞋", "木屐")),
    R(r"\bSeal of Searing", (r"炙烤之印", "灼热封印")),
    R(r"\bChanneling", (r"引导中", "引导")),
    R(r"Each bolt bounces", (r"射线", "弹矢")),
    R(r"\bClogs", (r"木鞋", "木屐")),
    R(r"\bVenom Bear\b", (r"毒液熊", "毒熊")),
    R(r"\bPsychic Seedling\b", (r"种籽", "幼苗")),
    R(r"\bDragon Claw\b", (r"龙爪(?!术)", "龙爪术")),
    R(r"\bRain of Fire\b", (r"火焰之雨", "火雨")),
    R(r"\bScuttler\b", (r"横行蟹", "疾爬者")),
    R(r"\bAllied\b", (r"我方", "友方")),
    R(r"\bRot Sprout", (r"腐朽抽芽", "腐朽苗芽")),
    R(r"\bWyrm", (r"蟠龙", "蛟龙")),
    R(r"\bAura", (r"灵气", "光环")),
    R(r"\bBone Knight", (r"白骨骑士", "骸骨骑士")),
    R(None, (r"痛苦魔魔", "痛苦魔")),
    R(r"Armored", (r"装甲北极熊", "披甲北极熊")),  # 兼容复数与截断别名
    R(r"\bEquipment Chest", (r"装备宝箱", "装备箱")),
    # 毒素伤害标记统一为 中毒（与抗性标签/状态名一致；不影响 以太毒素 等普通词）
    R(None, (r"\[毒素:poison\]", "[中毒:poison]")),
]
rules = [r for r in rules if r]

json.dump({"overrides": overrides, "rules": rules},
          open(os.path.join(HERE, "term_unify.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("overrides: %d, rules: %d" % (len(overrides), len(rules)))
