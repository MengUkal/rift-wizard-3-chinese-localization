# Rift Wizard 3 简体中文汉化 · 术语表与规则（每个翻译批次必须遵守）

## 铁律
1. 输出 JSON 的 key 必须与输入的英文原句**逐字符一致**（包括大小写、空格、换行 \n、标点）。value 为简体中文。
2. `{xxx}` 占位符：`{damage}` `{val}` `{name}` 等内容占位符必须原样保留，可按中文语序移动位置。`{s}`、`{suffix}` 这类英文复数占位符在中文里直接删掉。
3. 彩色标记 `[显示名:key]`：**只译冒号前的显示名**，冒号后的 key（含占位符形式如 `{attr_key}`）原样保留。
4. `[单词]`（无冒号）：译显示名；若原单词是纯英文单词（如 `[Physical]`、`[Poisoned]`），译文写成 `[中文:原单词小写]`，如 `[物理:physical]`、`[中毒:poisoned]`。
5. `[asseticon:xxx]` 整个标记原样保留，一字不动。
6. 标记里的单字母热键（如 `[H:shields]`、`[C:shields]` 的 H/C/S/E）是按键名，保留字母，只译冒号后的内容之外的部分（其实冒号后也不能动）。即 `[H:shields]` 整体不动，后面的 "Help" 译成「帮助」。
7. 保留原文的换行 `\n` 数量与位置意图；整句首尾若有空格要保留。
8. 标点风格跟原文：原文句尾无句号就不加句号；有逗号句式就保留。
9. 独立出现的缩写 SP、HP、SH 可保留不译（如 key 就是 "SP"）。但 "HP Cost" 这类完整词要译（生命消耗）。
10. 风格：游戏 UI 简洁风，tooltip 空间有限，避免啰嗦；用「你」指代玩家。

## 固定术语（必须一致）
### 专有名词
Wizard 法师｜Dark Wizard 黑暗法师｜Mordred 莫德雷德｜Avalon 阿瓦隆｜Rift 裂隙｜Realm 领域｜Vault 宝库｜Shrine 神龛

### 系统词
Spell 法术｜Upgrade 强化｜Equipment 装备｜Component 组件｜Tag 标签｜Buff 增益｜Minion 召唤物｜
Charges 充能｜Cooldown 冷却｜Range 射程｜Radius 半径｜Duration 持续｜Damage 伤害｜Resist 抗性｜
Turn 回合｜Tile 格｜Level（关卡）层／Level（数值）等级｜Bestiary 魔物图鉴｜Shop 商店｜
Learn Spell 学习法术｜Craft 制作｜Character Sheet 角色面板｜Mutator 变异项｜Mutated Run 变异模式｜
Weekly Run 每周挑战｜Custom Run 自定义模式｜Archmage Trials 大法师试炼｜Autosave 自动存档｜
Victory 胜利｜Defeat 败北｜Portal 传送门｜Loot 战利品｜Spell Power 法术威力（若见 Spell Power/Power 按上下文）

### 元素/伤害
Fire 火｜Ice 冰｜Lightning 闪电｜Physical 物理｜Arcane 奥术｜Dark 黑暗｜Holy 神圣｜Poison 毒素｜
Nature 自然｜Blood 血｜Chaos 混沌｜Heal 治疗｜Metallic 金属｜Slime 黏液｜Glass 玻璃｜Water 水｜
Acid 酸液｜Immolate 焚烧｜Petrification 石化｜Glassification 玻璃化｜Thunderstrike 雷袭

### 学派
Sorcery 巫术｜Conjuration 咒法｜Enchantment 附魔｜Translocation 移转｜Ritual 仪式｜Word 言灵

### 生物类 tag
Dragon 龙｜Demon 恶魔｜Undead 不死｜Elemental 元素｜Construct 构装体｜Spider 蛛类｜Eye 眼魔｜
Fang 利齿｜Orb 宝珠｜Arrow 箭｜Tongue 巨舌｜Living 活物｜Consumable 消耗品｜Leap 跃击｜
Assassin 刺客｜Music 音乐｜Shield 护盾｜Any 任意

### 状态
Stun/Stunned 眩晕｜Poison/Poisoned 中毒｜Bleed/Bleeding 流血｜Freeze/Frozen 冰冻｜
Petrified 石化｜Blind/Blinded 致盲｜Silence/Silenced 沉默｜Fear/Feared 恐惧｜Berserk(ed) 狂暴｜
Necrosis 坏死｜Soaked 潮湿｜Immobilized 定身｜Sleep 睡眠｜Reincarnate 转生｜Channel 引导｜
Quick Cast 快速施法｜Quickstep 疾步｜Clarity 清醒

### 常用动词句式
Deal(s) … damage 造成 … 点伤害｜Gain(s) 获得｜Lose(s) 失去｜Cast 施放｜Kill 击杀｜Summon 召唤｜
Teleport 传送｜"Each turn" 每回合｜"for {n} turns" 持续 {n} 回合｜"up to a max of {n}" 至多 {n}｜
"on cast" 施放时｜"on kill" 击杀时｜"in a [{radius}:radius] tile burst" 在半径 {radius} 格的范围内爆发

### 示例
- `Deal [{damage}:damage] [Fire] damage in a [{radius}:radius] tile burst`
  → `造成 {damage} 点[火:fire]伤害，在半径 {radius} 格的范围内爆发`
- `{unit} takes [{amount} {dtype_label}:{dtype_key}] damage from {source}`
  → `{unit} 受到来自 {source} 的 {amount} 点[{dtype_label}:{dtype_key}]伤害`
- `Inflict {buff} for {duration} turn{s}` → `施加 {buff}，持续 {duration} 回合`

## 补充术语（前几批沉淀，后续批次必须沿用）
Drake 幼龙｜Wyrm 蛟龙｜Imp 小恶魔｜Bomber 投弹手｜Maw 巨口｜spawner 生成器｜chasm 深坑｜
mastery 精通｜allies 友军｜line of sight 视线｜On Pickup: 拾取时：｜Damage Dealt: 已造成伤害：
### 流派法师
Pyromancer 火法师｜Electromancer 雷法师｜Cryomancer 冰法师｜Necromancer 死灵法师｜
Phytomancer 植物法师｜Manamancer 魔力法师｜Sanctumancer 圣所法师｜Ferromancer 铁法师｜
Hemomancer 血法师｜Chronomancer 时空法师｜Chronomancy 时间魔法
### 专名音译（统一用这版）
Lamasu 拉玛苏｜Spriggan 斯普里根｜Boggart 博加特｜Gremlin 格雷布林｜Efreet 伊夫里特｜
Duergar 灰矮人｜Helheim 赫尔海姆｜Yaldabaoth 亚大巴沃｜Jormungandr 耶梦加得｜Ophan 座天使｜
Arachnea 阿拉克涅｜Taurokelevee 陶罗凯利维｜Keraunos 雷霆｜Jaculus 飞蛇｜Grey Goo 灰蛊｜
Vampiricism 吸血术｜Ecophagy 生态吞噬｜Mushboom 爆爆菇｜Displacer Broodmother 移位兽育母
