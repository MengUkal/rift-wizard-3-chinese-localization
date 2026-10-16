# Rift Wizard 3 简体中文完整汉化 / Chinese Localization

Rift Wizard 3 的全文本简体中文汉化 MOD。

## 特性

- **99000+ 条译文**：UI、法术/强化/装备/组件、怪物图鉴（435 种）、稀有精英、变异项、神龛、剧情文本、战斗日志、结算面板
- 覆盖运行时拼接名（召唤系法术、狂乱面具、法袍、图腾、精通模板、裂隙预览长名截断等）
- 内置 **思源黑体**（Source Han Sans CN，SIL OFL 开源授权），自动应用中文字体
- 游戏内 OPTIONS → LANGUAGE 可随时切回 English

## 安装

把 `mod/ChineseLocalization/` 整个文件夹复制到游戏目录下的 `mods/` 文件夹：

```
Rift Wizard 3/mods/ChineseLocalization/
```

或在本目录直接运行：

```
python install_mod.py
```

首次启用后重启游戏即生效（游戏内 模组 菜单确认已启用）。

## 构建/更新译文

```
python extract_strings.py   # 从游戏源码提取可翻译字符串 → keys.json
python split_batches.py     # 切分翻译批次 → batches/src_NN.json
# ……翻译并校验批次（validate_batch.py NN）……
python gen_extras.py        # 生成运行时拼接名的组合译文
python merge_batches.py     # 合并 → text_zh.json
python install_mod.py       # 安装进游戏
```

游戏更新后：重跑提取 → 审计差异（audit_untranslated.py）→ 补译缺失 key 即可。

## 已知边界

- 标题画面与胜利/败北的美术字为图片资源，不在汉化范围
- 少量纯内部字符串（调试日志、事件 ID）有意保留英文

## 授权

- 译文部分：随意使用，注明来源即可
- 字体：思源黑体，SIL Open Font License
