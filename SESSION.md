# SESSION.md · 会话记忆（由 agent 维护，跨会话接力）

> 本文件记录工程当前状态、成品索引与用户偏好。新 agent 先读 `AGENTS.md` 再读本文件。

## 最近更新

- 2026-10-16：**历史摇滚三张专辑独立封面完成**（商-卷1 / 夏-卷1 / 西周-卷1；商/西周由 Agnes 生成，夏卷1 初版 Agnes 被用户认为"奇怪"→ 用**公司 ignis + gpt-image 重出 v2**，旧版改名留档）；**三张专辑文案完成并归入专辑目录**（albums/<专辑名>/专辑文案.md：名字/意境+标签+卖点+简介+发布清单；docs/ 同名文件备份不更新）；albums/README 布局规范同步
- 2026-10-14（夜班）：**三首新曲双版本完成**（义名之歌-商-卷1：网开一面 4:22/4:25 · 鼎中乾坤 4:32/4:35 · 七窍心 4:34/4:52，均完整收尾+四件套+封面）；新增《人物评价表》（孙子兵法十维×23人）与 scripts/pad_lyrics.py；夜班日志 docs/夜班-2026-10-14.md
- 2026-10-14：**历史摇滚系列启动（夏商周卷；当日由"武侠摇滚"更名）**。人物库大纲 `docs/history-rock/人物库.md`（11 人 + 传说层，含主要史料列与状态列）；首篇故事《披甲而战》_商_约前1200_妇好.md（约5600字，文内〔注n〕标注史料来源，17 条出处）。故事命名规则：歌名_朝代_年代_人名.md
- 2026-09-21：《一夫当关》延长任务：YuE2 无音频续写能力 → 开发通用工具 scripts/extend_audio.py（分析→同风格续段→拼接→交付）✅ 实测 167s→480s 拼合版 output/yue2/一夫当关_续写版8min.mp3
- 2026-09-21：**《歌曲生成规则》v1 生效**（docs/歌曲生成规则.md）：①默认中文发声 ②四件套交付(音频/歌词/ABC/HTML)。generate.py 已按规则改写(自动追加 Mandarin Chinese vocals + save_song_package)；lib_comfy 新增 extract_score_abc/render_sheet_html/save_song_package（从 ComfyUI history 节点2 text 提取 ABC）
- 2026-09-21：新工具落库 analyze_audio.py / extend_audio.py / transpose_abc.py；lib_comfy 新增 analyze_audio/join_audio/to_delivery/engine_audio_path；config.json 新增 comfyui_output_dir；需求文档 docs/功能需求_音频续写与Cover.md（P0✅ P1 待 SheetSage2）

- 2026-09-16：需求文档 v1.0 完成；convert_audio 工具完成并已实际使用；歌词核查完成（见 docs/歌词核查报告.md）；v11/v13 歌曲文件被用户改名为中文名
- 2026-09-16（续）：TECH_NOTES v2 增补“从零部署”前置清单；新增 config.json（comfyui_url 可改），scripts 全部改为读配置；AGENTS/SESSION 同步更新
- 2026-09-16（终）：Music3 本地节点验证通过（180s 测试版 music3_test_00001.flac）；新增 scripts/music3_generate.py + config music3 节；散落临时文件全部归拢到 tmp/；新增 .gitignore 忽略 tmp/
- 2026-09-16（Music3 用户反馈）：①未唱完 ②旋律不如 YuE2 ③中文发音清晰。采用用户抽卡法：probe=4×60s 多 seed 试旋律记住 seed → final=同 seed 300s 完整版（已固化为 music3_generate.py --mode probe/final；4×60s 抽卡进行中）
- 2026-09-16（Music3 根因实验）：**同 seed 只有同时长才可复现（重渲染 60s 相关 1.000）**；时长改变旋律全变（60s vs 300s 前60s 相关 0.028、60s vs 150s 相关 0.019）。原因疑似 CUDA graph 注册 generator RNG 状态（comfy/model_prefetch.py graph.register_generator_state）→ RNG 消耗节奏与总帧数耦合。**规则：抽卡时长必须=定稿时长**；若重启 ComfyUI 加 --disable-cuda-graphs 后验证 60s→300s 旋律延续是否恢复（待测）

## 当前状态

- ✅ 六类需求文档：`README.md`、`TECH_NOTES.md`（已入 git）
- ✅ 工具链：scripts/{lib_comfy,generate,extend,cover,separate,transcribe}.py、tools/convert_audio.{ps1,bat}
- ✅ YuE2 8 分钟能力验证：v12 纯器乐 8:29（spectral 完整）、v13 歌曲 7:31
- ✅ 歌词核查：v11(4:13) 实际唱的是中文歌词（发音变形）；v13(7:31) 人声为嘶吼/无词，无法还原文字；两首无真实英文歌词（用户已接受）
- ⏳ 待办/可选：
  - **Music3 试听**：scripts/minimax_music3.py + caption/歌词已备好（input/captions/melodeath_pipa_m3_caption.txt、input/lyrics/一百五十年的伤痕.txt），**本地 ComfyUI 节点已跑通（scripts/music3_generate.py probe/final 模式，无需 api_key）**；3×300s 已交付，用户自行手动抽卡中；YuE2 官方工具链 H:\AI\YuE run_yue2 已跑通（flash 补丁待 fork 流程确认 / 或切 eager）
  - 英文歌词版《一百五十年的伤痕》（歌词驱动模式，v8 先例咬字最准）
  - SFX 快速验证（8s 枪声试验；结论大概率：走独立 T2A 或素材库）
  - P1：描述→歌词 LLM 接入；谱面变换工具（转调/重配器）

## 成品索引（可听）

| 文件（basename） | 时长 | 说明 | 位置 |
|---|---|---|---|
| melodeath_pipa_instrumental_8min_v2_00001 | 8:29 | 旋律死金+电琵琶 纯器乐（Vocal 清零+Demucs 双保险） | ComfyUI/output/audio/YuE2/ + YuE2_no_vocals/ |
| 一百五十年的伤痕（=v13 歌曲） | 7:31 | 旋律死金+电琵琶+中文人声 | ComfyUI/output/audio/YuE2/ 与 d:\Users\Admin\Music\260916\一百五十年的伤痕.mp3 |
| 一百五十年的伤痕 1（=v11 歌曲） | 4:13 | 初版歌曲（中文词演唱，发音变形） | 同上 |
| 废墟里的证人 / 证人2 | 7:36 / ~7:40 | 用户自行生成；已 m4a→mp3（320k） | d:\Users\Admin\Music\260916\ |
| 钢铁洪流_v1_工业金属 | 3:22 | 中文工业金属摇滚（YuE2 官方工具链 cot=full） | output\yue2\（音频+score.abc） |
| 钢铁洪流_v2_电琵琶和声 | 3:23 | 同 Vocal 旋律/歌词，sus2/sus4 五声色彩和声+v2.abc | output\yue2\（音频+score.abc） |
| m3_final_0001\/2\/3（Music3） | 5:00 | Music3 本地 300s×3（seed 831105\/831106\/831107） | ComfyUI/output/audio/YuE2/ |
| m3_probe_seed8311xx（Music3） | 1:00×4 | Music3 60s 抽卡版 | ComfyUI/output/audio/YuE2/ |
| 一夫当关_延长版_8min | 4:47 | 同风格重制(首版, YuE2 上限内自然收尾) | output/yue2/ |
| 一夫当关_续写版8min | 8:00 | 续写拼合版: 原曲167s+同风格续段313s (extend_audio.py) | output/yue2/ |
| 三号宿舍_8min_女声 | 7:34 | 女声 8 分钟锁谱版(244小节, seed 831403) | output/yue2/ |
| 沼泽蒲公英 | 6:10 | Heavy/Dark Cyberpunk/80s Game OST 重金属中文叙事(电琵琶主奏) | output/yue2/ |
| 专辑文案《刀锋入梦》 | - | 喜马拉雅武侠摇滚催眠专辑文案 + 封面 | docs/喜马拉雅专辑文案_刀锋入梦.md + output/yue2/刀锋入梦_封面.png |
| 专辑文案《星海漫游指南》 | - | 喜马拉雅神秘/宇宙/时空/生命主题专辑文案 + 封面 | docs/喜马拉雅专辑文案_星海漫游指南.md + output/yue2/星海漫游指南_封面.png |
| 三号宿舍_8min | 5:27 | 男声完整版(自然收尾, seed 831402) | output/yue2/ |
| 三号宿舍_4min | 4:00 | 初版(240s 截断, 已被用户删除) | output/yue2/ |
| 三号宿舍_4min | 4:00 | 初版(240s 截断, Duration limit reached) | output/yue2/ |

| 专辑封面×3（义名之歌 商/夏/西周 卷1） | - | 独立专辑概念封面；商/西周=Agnes 1024+800，夏卷1 v2=gpt-image(ignis 公司平台)，旧 Agnes 版留档 | albums/*/封面/义名之歌-*-卷1_专辑封面(_800).png（夏卷1=_v2_gptimage） |
| 专辑文案×3（商/夏/西周 卷1） | - | 名字/意境+标签+卖点+简介+发布清单；主档随专辑 | albums/{商,夏,西周}-卷1/专辑文案.md（docs/ 同名备份） |
| 披甲而战_v1_yue2（YuE2） | 2:46 | 历史摇滚·战鼓摇滚 中文（妇好），seed 831501，四件套，320k | output/history-rock/ + albums/义名之歌-商-卷1/歌曲/ |

| 披甲而战_v1L4_yue2（YuE2·定稿） | 5:10 | 词v4(574字)·战鼓摇滚·完整收尾·seed 831501·四件套 | output/history-rock/ + albums/义名之歌-商-卷1/歌曲/ |
| 披甲而战_v2b_music3（Music3·定稿） | 4:55 | 词v4·seed 831109·caption+标签词 | output/history-rock/ + albums/义名之歌-商-卷1/歌曲/ |
| 披甲而战_vB_yue2_artrock（YuE2·风格试验） | 4:40 | Art Rock·竹笛/琵琶/男高音吟诵·seed 831601·四件套 | output/history-rock/ + albums/义名之歌-商-卷1/歌曲/ |

| 三过家门_v1b_yue2（YuE2·定稿） | 5:55 | 史诗民谣摇滚·男声苍茫·词583字·seed 831701·四件套+封面 | output/history-rock/ + albums/义名之歌-夏-卷1/ |
| 三过家门_v1a_yue2（340s 截断） | 5:40 | 留档不交付（结尾截断） | output/history-rock/ |

| 网开一面_v1_yue2（YuE2 变体A） | 4:22 | 开国颂歌·词573字·seed 831801·四件套+封面 | output/history-rock/ + albums/义名之歌-商-卷1/ |
| 网开一面_v1b_yue2（YuE2 变体B） | 4:25 | 开国颂歌·seed 831802·四件套 | output/history-rock/ + albums/义名之歌-商-卷1/歌曲/ |

| 七窍心_v1_yue2（YuE2 变体A） | 4:34 | 悲情硬摇滚·词604字·seed 832001·四件套+封面 | output/history-rock/ + albums/义名之歌-商-卷1/ |
| 七窍心_v1b_yue2（YuE2 变体B） | 4:52 | 悲情硬摇滚·seed 832002·四件套 | output/history-rock/ + albums/义名之歌-商-卷1/歌曲/ |

| 鼎中乾坤_v1_yue2（YuE2 变体A） | 4:32 | 智谋techno·词589字·seed 831901·四件套+封面 | output/history-rock/ + albums/义名之歌-商-卷1/ |
| 鼎中乾坤_v1b_yue2（YuE2 变体B） | 4:35 | 智谋techno·seed 831902·四件套 | output/history-rock/ + albums/义名之歌-商-卷1/歌曲/ |

| 愿者上钩_v1a_yue2（YuE2 变体A） | 4:08 | 智谋 techno-art·古筝琶音·词591字·seed 832101·四件套+封面 | output/history-rock/ + albums/义名之歌-西周-卷1/ |
| 愿者上钩_v1b_yue2（YuE2 变体B） | 4:14 | 智谋 techno-art·seed 832102·四件套 | output/history-rock/ + albums/义名之歌-西周-卷1/歌曲/ |

| 羑里_v1a_yue2（YuE2 A卡·古琴慢板） | 4:32 | 哲王·忍·悲凉·词605字·seed 832201·四件套+封面 | output/history-rock/ + albums/义名之歌-西周-卷1/ |
| 羑里_v1b_yue2（YuE2 B卡·ambient管弦） | 4:22 | seed 832202·四件套 | output/history-rock/ + albums/义名之歌-西周-卷1/歌曲/ |

| 牧野_v1a_yue2（YuE2 A卡·史诗金属×唢呐） | 4:41 | 战神·燃·狂·词620字·seed 832301·四件套+封面 | output/history-rock/ + albums/义名之歌-西周-卷1/ |
| 牧野_v1b_yue2（YuE2 B卡·world-rock×电琵琶） | 4:30 | seed 832302·四件套 | output/history-rock/ + albums/义名之歌-西周-卷1/歌曲/ |

更早的作品（melodic_heavy_metal 系列、pure_instrumental_metal 等）曾存在 ComfyUI/output/audio/YuE2/，部分被用户整理/移走，以磁盘现状为准。

## 交付规则（2026-09-17 起）

- **YuE2/Music3 成品交付一律 mp3（320kbps，libmp3lame）**；flac 仅存原生工件于引擎 outputs（H:\AI\YuE\skills\yue2-music\outputs\），交付目录不落 flac
- 转换工具：tools/convert_audio.ps1（-SourceExt flac -TargetExt mp3 -Bitrate 320）

## 用户偏好（重要）

- 中文交流；沟通结果附 文件路径 + 时长 + 试听要点
- “8 分钟”接受 7:50-8:20 近似
- 歌词重排/模型自行改词可接受（“完稿”即收）
- 纯器乐 = 不允许人声；中文歌词要准（歌词驱动模式下咬字最好）
- 音效需求：YuE2 不做，建议其他方案
- 工具化诉求强：新需求尽量沉淀为可复用脚本（ps1/bat/py）
- **Agent 创作纪律（2026-10-14）：不删、不破坏**——作品只增不改，新版本追加命名，废弃版标注保留不删除

## 常用服务状态

- ComfyUI：127.0.0.1:8188（单 GPU，任务排队；托管方式：后台 pwsh 任务）
- 沙箱：当前会话 danger-full-access；pip 不可用（wheel 手动解包）
- Whisper：whisper_models/whisper-small（transformers 格式，需 pipeline 设置 tokenizer.pad_token_id=eos_token_id 才能批处理）

## 会话补充记录（2026-09-18）
- 参考仓库 japanese-composition-skills（Claude Code 风格日式作曲技能库，11 skill：和弦进行/转调/编曲/混音等）已克隆到 H:\AI\ComfyUI_windows_portable\skills\japanese-composition-skills（当前目录非 git 仓库，普通 clone 非 submodule）
- 曲谱渲染：自动注入 %%barNumbers 1 显示小节编号；播放高亮=事件自带 SVG 元素着色（elements 双层嵌套，实测通过）

### 《钢铁洪流》v3（旋律金属 + 萨克斯，2026-09-18）
- 需求：参考 jp skills（japanese-composition-skills）生成旋律金属版并加入萨克斯管
- 做法：iron_v3.abc == v1 派生（Vocal 零改动，33 条 Ins 行改写为次中音萨克斯旋律线：主题-变奏-句尾fill-间奏solo-尾呼）；request industrial_v3.json（style 旋律金属+萨克斯，148 BPM，seed 831203）
- 生成：run_yue2 generate --abc-file + cot full + 本地模型路径（ComfyUI models\yue2\YuE2-3B / YuE2-Vae，offline）→ 229.5s 音频，185.5s 生成
- 校验：compare --voices Vocal 33 行零差异；歌词顺序=request 相同原文
- 交付：output\yue2\ 钢铁洪流_v3_旋律金属萨克斯.mp3(320k) + .score.abc + _曲谱.html（曲谱播放注 %%MIDI program 66 次中音萨克斯 per Ins 段、program 0 per Vocal 段；render_sheet.mjs 新增 sax 参数）
- 注意：--offline 必须显式传本地模型路径；外部 abc 用 generate（all-modes 不收 abc）

### 曲谱鼓/多乐器答疑（2026-09-18）
- 用户问：曲谱似乎只有主乐器，有没有鼓？各乐器如何演奏
- 原理：YuE2 官方 abc_tools 硬校验只接受 V: Vocal / V: Ins 两声部（简谱语义骨架）；鼓/贝斯/节奏吉他/键盘由模型按 style 在音频生成时自动编配，不进谱面
- 曲谱播放（abcjs）只发出谱面声部（Vocal 钢琴 + Ins 萨克斯）→ 与成品音频差异即演示谱 vs 满编音频
- 新增演示能力：渲染端可注入第三声部 V: Drums（clef=bass, %%MIDI program 118 synth drum）；16 分 rock 8-beat pattern（kick=D,(36) snare=a(38) hh=d'(42)），每段与 Vocal/Ins 小节对齐，末小节 fill
- 产物：output\yue2\iron_v3_drum_demo.abc + 钢铁洪流_v3_带鼓演示_曲谱.html（33 处 prog66 萨克斯 + Drums 三声部）
- 演示谱仅供曲谱播放演示；YuE 生成仍用两声部母版（iron_v3.abc）

### 鼓谱改真鼓点（2026-09-18）
- 用户：鼓谱直接用鼓点播放比较好，现在有好几种音色（初版用 program 118 synth drum + 三音高，听感是音调非鼓）
- 正解：abcjs 原生支持 %%MIDI drummap <abc音> <GM鼓键> + V: Drums clef=perc（自动走 GM Channel 10 打击乐，音高映射真实鼓）
- 本曲映射：D,->36 底鼓 / a->38 军鼓 / d'->42 闭镲；render_sheet sax 参数保留（Ins 萨克斯 program 66）
- 已验证：Edge headless 渲染 4.9MB DOM、Drums 声部正常、无 JS 错误；产物 output\yue2\钢铁洪流_v3_带鼓演示_曲谱.html + iron_v3_drum_demo.abc

### 鼓点只响第一段修复（2026-09-18）
- 现象：带鼓演示曲谱只有第一段有鼓点，后续段无
- 排查：谱面数据全曲 66 段鼓行齐全（html 372 处鼓音符）；缺的是播放层通道——abcjs 源码 2612 行：只有 %%MIDI program 128 才切换 MIDI Channel 10 打击乐通道
- 修复：Drums 声部前注入 %%MIDI program 128（+ clef=perc + drummap D,36/a,38/d',42，全全局）→ 重渲染
- 音色：gleitz FluidR3_GM percussion-mp3 每音高一 mp3 文件（curl：C2/D2.mp3 200；F#2(hi-hat) 404 待确认）
- headless 诊断坑：带外部 src 脚本的页面在 --dump-dom 下内嵌脚本不执行（src 请求疑似挂起），纯内嵌 PING 正常；已验证改用 curl/直接验证渲染产物
- 产物：output\yue2\钢铁洪流_v3_带鼓演示_曲谱.html（prog128+drummap+66 萨克斯）

### 演奏不同步修复（2026-09-18）
- 现象：曲谱播放时鼓跨越多个段/很远的段一起亮；用户期望一个段（多小节）内乐器同步进行
- 实证（headless）：事件时序正常（line 单调推进）；事件元素坐标均在同一系统内相邻 staff（176/237/344）——高亮本身不跨系统
- 真因：鼓段插入数为 66（每个 Vocal/Ins 段后都插）= 旋律段(33) 的 2 倍；abcjs 把 V/I/D 按并行声部同时推进 → 前 33 系统后 Vocal/Ins 结束，后 33 系统只剩鼓独奏（lines=66, staffDist 后段=1）
- 修复：make_drum_demo.py 只插 Ins 段后 → 33 鼓段与旋律同长；结构验证 staffDist={3:33} 全三声部同系统，noteTimings 993、时长 205s 与旋律一致
- 高亮升级：template.html CURSOR 小节约束（hlMeasure/hlLine 变化才 clear，同小节三声部整块保持亮、换小节切换）→ 三版重渲染
- abljs 并行语义：多 V: 声部同时开始推进（非顺序）；鼓须与旋律段等长才同步

---

## 历史摇滚系列 · 夏商周卷（2026-10-14 启动；当日更名：武侠摇滚→历史摇滚，目录 wuxia→history-rock）

- 人物库大纲：`docs/history-rock/人物库.md`（专辑地图：义名之歌-夏/商-卷1/西周-卷1、恶名之歌-商-卷2/西周-卷2 + 春秋战国卷预告）
- 故事：#1《披甲而战》_商_约前1200_妇好.md（**第一人称版 v1.1 已出稿**：正文一至六“我”自述、楔子/尾声/身后诸事全知；史料〔注〕17 条原样保留）
- 流程：史料→故事（agent 手写，文内〔注〕标注来源）→审稿→歌词（agent 手写）→配图（Agnes 免费图片模型，包见 H:\AI\AgnesGenWorkFlow）→多引擎生成（YuE2 主 / suno 对比 / Music3·step 备用；四件套交付）→组专辑 albums/→发布（喜马拉雅/汽水）
- 封面命名与故事文件一致（歌名_朝代_年代_人名.png）；写作原则：简单易懂、以史料为基，戏剧色彩自定
- 输出目录：**本课题图片+音频统一 `output/history-rock/`**（与历史 output/yue2 等分离）；agnes-output/ 留生成原图
- 引擎经验（用户实测 2026-10-14）：**YuE2 好听率远高于 Music3、接近 suno6** → 生成优先级 YuE2(主) > suno(外网) > Music3/step(备用)
- **恶名之歌卷**：已立项（反面人物专卷；骂法三铁律：以史料为基 / 史诗控诉·史官审判 / 争议人物另开枭雄卷；"红颜祸水"类并入暴君曲不开骂）
- 专辑：一张专辑 = 朝代 × 义/恶 名，命名 `义名之歌-<朝代>-卷N` / `恶名之歌-<朝代>-卷N`（卷号朝代内起算，一时期可多张，次代重启）；**10 首/张** 标准（EP 3-5 亦可）；专辑地图+人物分卷见 docs/history-rock/人物库.md
- 妇好线：故事 ✅（第一人称 v1.1）；封面 ✅；词 v4（574字；教训：中文唱速实测≈2.2字/秒，≤530字必<4min）；曲风矩阵已入库；**定稿双版：v1L4 YuE2 5:10 + v2b Music3 4:55——待试听定案**
- 大禹线：《三过家门》故事✅ 词✅(583字) 封面✅ 歌✅ v1b（史诗民谣摇滚）——**待用户试听**
- **试听反馈（白班 2026-10-15）**：妇好《披甲而战》=为国而战感 ✅；比干《七窍心》歌词催泪 ✅；伊尹《鼎中乾坤》歌词引发治国之道思考 ✅；**歌词与歌曲已正确匹配**（此前的 2:40 断词问题已解决）；用户自行修复过部分 mp3/歌词文件（尊重用户改动，不覆盖）；YuE2 部分字发音错误=模型层限制，无工具解法（对策：歌词驱动+清嗓+避闭口音堆叠）
- **问题与补救（2026-10-15）**：大禹《三过家门》两版结尾戛然而止（歌唱完但曲子被切断）→ 已产 _outro 版（ffmpeg 残响尾音+8s 三角渐弱：v1b 355.4s / v1a 340.6s，原版保留）；上游防：style 加"resolve & fade"提示 + 词稿留 [Outro]，已写入风格配器库 §8
- **每角色 4 曲制（2026-10-15 用户新架构）**：每人 = 短抓耳 2 版（当前 v1a/v1b）+ 长篇叙事 2 版（n1a/n1b，另写词稿）；发布定位：抓耳版→汽水/短视频，叙事版→喜马拉雅长音频；叙事版创作原则（≠短版拉长）：独立词稿（6-7min≈850+字）、多主歌按生平章节推进、可加念白/旁白、副歌主题句随段微变、器乐华彩间奏
- **双版本升级（2026-10-15 用户）：一次抽 2 个 = 双风格变体**——v1a/v1b 不再同风格异 seed，而是唱法/曲风/乐器拉开差距（≥2 维不同：主奏乐器、嗓音至少其一不同；混搭层尽量不同）；已写入风格配器库 §0；自下一首（文王/武王）起执行
- **白班新建议（风格多元化）**：摇滚为基座，混搭 techno/world/art/reggae/trance/synthwave/dance/electric 等；中西（→世界）乐器混配，每曲不同的主奏/副奏/节奏配置——待提炼为《风格配器库》（见下一步）
- 妇好线：v1L4/v2b/vB 三版待试听定稿（作品全部保留，不删）
- 下一步：试听妇好/大禹 → 定案 → 第三首（商汤《网开一面》→ 义名之歌-商-卷1）