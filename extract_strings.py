# -*- coding: utf-8 -*-
"""Rift Wizard 3 汉化：从游戏源码 AST 提取全部可翻译字符串（loc.T 的 key = 英文原文）。
输出 keys.json（去重、含出处），并打印统计。垃圾 key 无害（查不到就不会用），宁多勿漏。
"""
import ast, json, os, re, sys

GAME = r"E:\SteamLibrary\steamapps\common\Rift Wizard 3"
HERE = os.path.dirname(os.path.abspath(__file__))

FILES = [
    "CommonContent.py", "Components.py", "Equipment.py", "FinalBosses.py",
    "Game.py", "Level.py", "LevelGen.py", "LevelGenHelpers.py", "LevelRewards.py",
    "Monsters.py", "Mutators.py", "RareMonsters.py", "RiftWizard3.py",
    "Spells.py", "SteamAdapter.py", "Vaults.py", "text.py",
]

ident_re = re.compile(r'^[a-z0-9_][a-z0-9_]*$')
path_re = re.compile(r'\.(png|jpg|jpeg|ttf|ttc|otf|json|txt|wav|ogg|dat|csv|py|zip|dll|pyd|gif)$', re.I)

def has_letter(s):
    return any(c.isalpha() and c.isascii() for c in s)

def strip_markup(s):
    t = re.sub(r'\{[^{}]*\}', '', s)     # {placeholders}
    t = re.sub(r'\[[^\[\]]*\]', '', t)   # [text:key] 彩色标记
    t = re.sub(r'[\d\W_]+', '', t)
    return t

strings = {}   # key -> {"orig": [...], "n": int}
idents = set()
fstring_count = 0

def add(s, where, generated=False):
    if s in strings:
        strings[s]["n"] += 1
        if len(strings[s]["orig"]) < 3:
            strings[s]["orig"].append(where)
        return
    strings[s] = {"orig": [where], "n": 1, "gen": generated}

for fn in FILES:
    path = os.path.join(GAME, fn)
    with open(path, encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src)
    doc_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
               and isinstance(body[0].value.value, str):
                for ln in range(body[0].value.lineno, (body[0].value.end_lineno or body[0].value.lineno) + 1):
                    doc_lines.add(ln)
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            fstring_count += 1
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        if node.lineno in doc_lines:
            continue
        s = node.value
        where = "%s:%d" % (fn, node.lineno)
        if ident_re.match(s):
            idents.add(s)
            continue
        if path_re.search(s):
            continue
        if not has_letter(s):
            continue
        if len(strip_markup(s)) < 2:
            # 彩色标记的显示名本身有实质内容（如 [Blood Mastery:blood]）则保留
            disp = "".join(m.group(1) for m in re.finditer(r"\[([^\]:]+):[^\]]*\]", s))
            if len(re.sub(r"[\W_]+", "", disp)) < 4:
                continue
        add(s, where)

# 属性标签：format_attr 把 'minion_damage' 变成 'Minion Damage'，这类 key 运行时生成，需补齐
def title_case(i):
    return " ".join((w[:1].upper() + w[1:]) for w in i.replace("_", " ").split())

gen = 0
for i in sorted(idents):
    if re.match(r'^[a-z_][a-z0-9_]*$', i):
        lb = title_case(i)
        before = len(strings)
        add(lb, "attr_label:%s" % i, generated=True)
        gen += len(strings) - before
add("Requires LoS", "attr_label:requires_los", generated=True)
add("HP Cost", "attr_label:hp_cost", generated=True)

items = [{"k": k, "n": v["n"], "orig": v["orig"], "gen": v.get("gen", False)} for k, v in strings.items()]
items.sort(key=lambda e: (e["orig"][0], e["k"]))

with open(os.path.join(HERE, "keys.json"), "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=1)

total_chars = sum(len(e["k"]) for e in items)
print("unique keys: %d  (generated attr labels: %d)" % (len(items), gen))
print("total chars: %d" % total_chars)
print("f-strings found (skipped, chunks not extracted): %d" % fstring_count)
byfile = {}
for e in items:
    byfile[e["orig"][0].split(":")[0]] = byfile.get(e["orig"][0].split(":")[0], 0) + 1
for fn, cnt in sorted(byfile.items(), key=lambda kv: -kv[1]):
    print("  %-22s %5d" % (fn, cnt))
print("---- sample ----")
for e in items[:30]:
    print(repr(e["k"])[:150])
