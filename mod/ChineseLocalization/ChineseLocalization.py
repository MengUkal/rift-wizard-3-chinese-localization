# -*- coding: utf-8 -*-
"""Rift Wizard 3 简体中文完整汉化 MOD
- 注册 zh 语言（游戏内 语言 菜单可选 简体中文）
- 译文由本 MOD 自带 text_zh.json 提供，不改动游戏本体文件
- 随 MOD 附带思源黑体（Source Han Sans CN, SIL OFL 授权），自动切换中文字体
- 若用户未手动选择过其他语言，则默认以简体中文启动
"""

import os
import sys
import json
import re

LANG = 'zh'

try:
	MOD_ROOT = os.path.dirname(os.path.abspath(__file__))
except NameError:
	MOD_ROOT = os.path.abspath(os.path.join('mods', 'ChineseLocalization'))

# 黑匣子：任何加载问题都写进 load_debug.log，便于诊断
def _dbg(msg):
	try:
		with open(os.path.join(MOD_ROOT, 'load_debug.log'), 'a', encoding='utf-8') as f:
			f.write(msg + '\n')
	except Exception:
		pass

_dbg('=== entry start, python %s ===' % sys.version.split()[0])

import Localisation as loc

# ---- 1) 把 zh 注册进语言列表（语言菜单用 available_locales() ∩ LANG_DISPLAY_NAME）----
_orig_available_locales = loc.available_locales

def _available_locales_with_zh():
	try:
		codes = set(_orig_available_locales())
	except Exception:
		codes = set()
	codes.add(LANG)
	return sorted(codes)

loc.available_locales = _available_locales_with_zh
# 显示名用 "Chinese"：切到英文后菜单字体（SpecialElite）没有中文字形，
# 「简体中文」会整行隐形；拉丁名两种字体都能正常显示
loc.LANG_DISPLAY_NAME[LANG] = 'Chinese'

# ---- 2) 译文加载：优先读 MOD 自带的 text_zh.json ----
_data_cache = None

def _load_mod_data():
	global _data_cache
	if _data_cache is None:
		path = os.path.join(MOD_ROOT, 'text_zh.json')
		with open(path, 'r', encoding='utf-8') as f:
			_data_cache = json.load(f)
	return _data_cache

_orig_load = loc.load

def _load_translations(lang):
	if lang == LANG:
		return _load_mod_data()
	return _orig_load(lang)

_load_translations.cache_clear = getattr(_orig_load, 'cache_clear', lambda: None)
loc.load = _load_translations
_dbg('sections 1-2 ok (locale registered, loader patched)')

# ---- 3) 默认语言：MOD 加载时先切到 zh。
# 游戏主界面初始化时会用 options 里的 lang 覆盖这里（玩家在菜单里选过别的语言就听玩家的）。----
loc.set_locale(LANG)

# ---- 4) 中文字体：游戏主模块在 MOD 加载时已初始化 FONT_MAP，可直接登记。----
def _register_font():
	main = sys.modules.get('__main__')
	if main is None:
		return
	font_path = os.path.join(MOD_ROOT, 'fonts', 'SourceHanSansCN-Normal.ttf')
	if not os.path.exists(font_path):
		return
	font_map = getattr(main, 'FONT_MAP', None)
	if isinstance(font_map, dict):
		# 绝对路径经 os.path.join(FONT_DIR, path) 会原样返回，正好绕开字体目录限制
		font_map[LANG] = font_path
	size_map = getattr(main, 'FONT_SIZE_MAP', None)
	if isinstance(size_map, dict):
		size_map[LANG] = 22

_register_font()

# ---- 5) 直接替换 text.py 模块的字符串常量（教程页等界面不走 T() 直绘原文）。
# 中文串即使再经过 T() 查不到 key 也会原样返回，占位符与译文一致，两条路径都安全。----
def _patch_text_module():
	try:
		import text as _text
	except Exception:
		return
	data = _load_mod_data()
	replaced = 0
	for name, val in list(vars(_text).items()):
		if name.startswith('_') or not isinstance(val, str):
			continue
		zh = data.get(val)
		if zh:
			setattr(_text, name, zh)
			replaced += 1

_patch_text_module()

# ---- 6) 商店筛选器悬浮说明：这些字符串是裸 .format() 拼接、不走 T()，
# 直接包住 PyGameView 的四个方法输出中文。----
def _patch_shop_filter_tooltips():
	main = sys.modules.get('__main__')
	cls = getattr(main, 'PyGameView', None)
	if cls is None or main is None:
		return
	data = _load_mod_data()

	def z(s):
		t = data.get(s)
		return t if (t and any('\u4e00' <= c <= '\u9fff' for c in t)) else s

	# 热键行
	def add_hotkey(self, desc, hotkey):
		if not hotkey:
			return desc
		return "{desc}\n热键：  {hotkey}".format(desc=desc, hotkey=hotkey)
	cls.add_shop_filter_hotkey_description = add_hotkey

	# 值描述行（Results with ... tag 等）
	orig_base = cls.get_shop_filter_value_base_description
	ST = getattr(main, 'SHOP_FILTER_TAGS', None)
	SA = getattr(main, 'SHOP_FILTER_ATTR', None)
	SB = getattr(main, 'SHOP_FILTER_BONUS', None)
	SGT = getattr(main, 'SHOP_FILTER_GAIN_TAGS', None)
	SGA = getattr(main, 'SHOP_FILTER_GAIN_ATTR', None)
	SRT = getattr(main, 'SHOP_FILTER_RECIPE_TAGS', None)

	def base_desc(self, category, value):
		label = z(self.get_shop_filter_value_label(category, value))
		if category == ST: return "带有「%s」标签的结果" % label
		if category == SA: return "带有「%s」属性的结果" % label
		if category == SB: return "强化「%s」属性的结果" % label
		if category == SGT: return "可通过强化附加「%s」标签的结果" % label
		if category == SGA: return "可通过强化附加「%s」属性的结果" % label
		if category == SRT: return "需要「%s」标签的结果" % label
		return orig_base(self, category, value)
	cls.get_shop_filter_value_base_description = base_desc

	# 类别描述里的"下一类"行
	orig_catdesc = cls.get_shop_filter_category_description
	def catdesc(self, category):
		s = orig_catdesc(self, category)
		if isinstance(s, str):
			s = s.replace("\nNext category:  ", "\n下一类：")
		return s
	cls.get_shop_filter_category_description = catdesc

	# 悬浮标题行 "Tags: Blood" → "标签：血"
	orig_target = cls.get_shop_filter_value_target
	def target(self, category, value):
		t = orig_target(self, category, value)
		try:
			name = getattr(t, 'name', None)
			if isinstance(name, str) and ': ' in name:
				cat, _, label = name.partition(': ')
				t.name = "%s：%s" % (z(cat), z(label))
		except Exception:
			pass
		return t
	cls.get_shop_filter_value_target = target

	# 开场消息兜底：不管 text 模块补丁是否生效，进入 new_game 后直接查词典强翻
	orig_new_game = cls.new_game
	def new_game(self, *args, **kwargs):
		orig_new_game(self, *args, **kwargs)
		try:
			# 伪试炼名映射：左栏/检视面板以 pre_resolved 直绘 trial_name，
			# 无法走查表，故直接把存储值换成中文（二者非真实试炼，不影响 Steam 统计）
			trial_map = {"MUTATED_RUN": "变异模式", "Custom": "自定义模式"}
			g = getattr(self, 'game', None)
			if g is not None:
				tn = getattr(g, 'trial_name', None)
				if tn in trial_map:
					g.trial_name = trial_map[tn]
				else:
					m = re.match(r'^weekly_(\d+)$', tn or '')
					if m:
						g.trial_name = '每周挑战 #%s' % m.group(1)
			msg = getattr(self, 'message', None)
			if not isinstance(msg, str):
				return
			TAIL = "\n\n\n\nChallenge Modifiers:"
			if TAIL in msg:
				# 尾巴后面可能还跟着变异项描述，用 partition 而不是 endswith
				head, _, rest = msg.partition(TAIL)
				t = data.get(head)
				if t:
					self.message = t + "\n\n\n\n挑战修正项：" + rest
				else:
					self.message = head + "\n\n\n\n挑战修正项：" + rest
				return
			t = data.get(msg)
			if t:
				self.message = t
		except Exception:
			pass
	cls.new_game = new_game

	# ---- 7) 大法师试炼列表：原版把描述固定画在列表下方，列表一长描述就被顶出屏幕。
	# 替换整个方法：描述改为锚定屏幕底部向上排，保证完整显示。----
	def _patch_pick_trial():
		main_local = sys.modules.get('__main__')
		all_trials = getattr(main_local, 'all_trials', None)
		trial_cls = getattr(main_local, 'Trial', None)
		color_victory = getattr(main_local, 'COLOR_VICTORY', (255, 255, 255))
		if not all_trials or trial_cls is None:
			return
		import SteamAdapter

		def draw_pick_trial(self):
			rect_w = max(self.font.size(t.name)[0] for t in all_trials)
			cur_x = self.screen.get_width() // 2 - rect_w // 2
			cur_y = self.screen.get_height() // 2 - self.linesize * (len(all_trials) // 2)

			for trial in all_trials:
				line_w = self.font.size(trial.name)[0]
				self.draw_string(trial.name, self.screen, cur_x, cur_y, (255, 255, 255), mouse_content=trial, content_width=line_w)
				if SteamAdapter.get_trial_status(trial.name):
					self.draw_string("*", self.screen, cur_x - 16, cur_y, color_victory)
				cur_y += self.linesize

			if isinstance(self.examine_target, trial_cls):
				desc = self.examine_target.get_description()
				lines = desc.split('\n')
				# 描述锚定屏幕底部向上排；若与列表重叠则下移到列表之下（宁可轻微出界也不遮挡）
				start_y = self.screen.get_height() - (len(lines) + 1) * self.linesize
				cur_y = max(cur_y + self.linesize, start_y)
				for line in lines:
					cur_x_desc = (self.screen.get_width() // 2) - (self.font.size(line)[0] // 2)
					self.draw_string(line, self.screen, cur_x_desc, cur_y)
					cur_y += self.linesize

		cls.draw_pick_trial = draw_pick_trial

	_patch_pick_trial()

	# ---- 8) 消息界面（开场诗等）自动缩字号：行数超出屏幕时逐级减小字体直到放得下 ----
	def _patch_draw_message():
		cls_dm = getattr(sys.modules.get('__main__'), 'PyGameView', None)
		if cls_dm is None:
			return

		def draw_message(self):
			lines = self.message.split('\n')
			margin = self.border_margin
			avail_h = self.screen.get_height() - margin * 2
			px = getattr(self, 'font_px', 22)
			font = self.font
			linesize = self.linesize
			while len(lines) * linesize > avail_h and px > 12:
				px = max(12, int(px * 0.88))
				font, linesize = self.get_how_to_play_font(px)
			cur_y = margin
			if self.center_message:
				cur_y = max(margin, self.screen.get_height() // 2 - linesize * len(lines) // 2)
			for line in lines:
				if line:
					self.draw_string(line, self.screen, 0, cur_y, center=self.center_message,
					                 content_width=self.screen.get_width(), font=font, linesize_override=linesize)
				cur_y += linesize

		cls_dm.draw_message = draw_message

	_patch_draw_message()

# ---- 9) 中文换行：游戏 TOKEN_RE 把连续 \w（含中文）当成一个“单词”，
# 无空格的中文整句进 draw_wrapped_string 无法断行，长句被面板右缘裁掉。
# 包装 tokenize：含中文且长度 > 2 的词按单字拆开，让换行可落在任意字边界。----
def _patch_tokenize_cjk():
	main = sys.modules.get('__main__')
	cls = getattr(main, 'PyGameView', None)
	if cls is None or not hasattr(cls, 'tokenize'):
		return
	_orig_tokenize = cls.tokenize
	_cjk_re = re.compile(r'[\u3400-\u9fff\uf900-\ufaff]')

	def tokenize(self, txt):
		for tok in _orig_tokenize(self, txt):
			try:
				if tok[0] == 'word' and len(tok[1]) > 2 and _cjk_re.search(tok[1]):
					for ch in tok[1]:
						yield ('word', ch)
				else:
					yield tok
			except Exception:
				yield tok
	cls.tokenize = tokenize

_patch_tokenize_cjk()
_dbg('section9 ok (cjk wrap patch)')

try:
	_patch_text_module()
	_dbg('section5 ok (text module patched)')
	_patch_shop_filter_tooltips()
	_dbg('entry complete OK')
except Exception:
	import traceback
	_dbg('ENTRY CRASH:\n' + traceback.format_exc())
