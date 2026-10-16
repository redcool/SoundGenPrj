# SESSION.md · 会话记忆（由 agent 维护，跨会话接力）

> 本文件记录工程当前状态、成品索引与用户偏好。新 agent 先读 `AGENTS.md` 再读本文件。

## 最近更新

- 2026-10-16（楚辞系列·歌词双版+国殇第2轮）：**用户确立歌词双版交付**（标注版=人看唱：正字+注音+释义；别字版=模型读：同音同调高频字；音频只认别字版；系列总册§10）；**试听定论：主攻别字版逐轮逼近**（易字版降为兜底）；国殇 v2 别字版已换更常见同音字（毂→鼓/殪→意/枹→福/躐→烈/披→批）生成中 seed 834203
- 2026-10-16（楚辞系列·国殇第1轮）：**别字版 vs 易字版对照已生成**——《国殇》v1a别字版 3:13 / v1b易字版 3:28（同风格 seed 834201/834202，四件套 + Demucs 分离 + Whisper 转写）；Whisper-small 对歌声幻觉严重、仅作低配探针；试验记录 docs/楚辞/试验-国殇-别字vs易字-第1轮.md；**待用户人耳试听定版**；产物 output/chuci/ + output/chuci/stems_*
- 2026-10-16（楚辞系列·易字/别字守则）：**用户确立“同音别字法”解决 YuE2 咬字**——生僻字→同音同调常用别字（毂gǔ→古、殪yì→义、枹fú→扶、怼duì→对、躐liè→列…），只动音不动句；**双版本隔离**：别字版只喂模型出音频，歌词卡/字幕/曲谱用原文正字；**逼近闭环**：生成→试听→圈咬错字→换更贴同音字→再生成逐轮收敛。易字版（近义替换）降为兜底。已入 系列总册·创作纪律§9 与 篇目档案·附易字守则；《国殇》原文→别字版→易字版三栏对照+别字完整唱词已落盘，待生成试验
- 2026-10-16（楚辞系列·易字守则）：**用户提议“生僻字换常用字”解决 YuE2 咬字**——确立“字级白话、不动句骨”三档规则（保留/替换/拆解），入 系列总册·创作纪律§9 与 篇目档案·附易字守则；《国殇》原文→易字对照表已落盘，待生成试验（原字版 vs 易字版咬字对比）
- 2026-10-16（楚辞系列开卷）：**为《楚辞》原典谱曲的专辑组启动**——`albums/楚辞之歌/`（8 张专辑目录：01-离骚/02-九歌(11篇)/03-天问/04-九章/05-楚士/06-招魂/07-宋玉-九辩/08-楚声余响，各含 专辑信息.md+歌词/封面/歌曲 子目录）+ 系列总册 README（分卷地图/创作纪律/命名规则）+ `docs/楚辞/楚辞篇目档案.md`（17 卷原文档案+hook 句+谱曲建议）；词稿目录 `input/lyrics/chuci/`，出品目录 `output/chuci/`；风格衔接 风格配器库 §9 楚辞启示录；试水建议：国殇→渔父→山鬼
- 2026-10-16：**历史摇滚专辑封面与 9 张歌曲封面全部改用 ignis gpt-image 重新生成**（专辑封面含中文标题"义名之歌·X"；歌曲封面含歌名+人名，妇好/商汤/伊尹/比干/大禹/文王/武王/周公旦/姜子牙；1024+800，Agnes 旧版全改名 _v1_agnes 留档）；**三张专辑文案完成，主档 = albums/<专辑名>/专辑文案.md**（docs/ 备份已由用户清理）；albums/README + SESSION 索引同步
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

## 楚辞之歌系列（规划中 · 2026-10-16 开卷）

| 内容 | 说明 | 位置 |
|---|---|---|
| 系列总册 | 分卷地图/创作纪律/命名规则/状态总览 | albums/楚辞之歌/README.md |
| 篇目档案 | 17 卷原文档案+hook+谱曲建议 | docs/楚辞/楚辞篇目档案.md |
| 子专辑×8 | 各含 专辑信息.md + 歌词/封面/歌曲 | albums/楚辞之歌/01-离骚 … 08-楚声余响 |

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

| 专辑封面×3（商/夏/西周 卷1） | - | ignis gpt-image 重出（含中文标题 1024+800）：商/西周=v2，夏=v3；Agnes 旧版改 v1_agnes 留档 | albums/{商,夏,西周}-卷1/封面/义名之歌-*-卷1_专辑封面_v2/v3_gptimage(_800).png |
| 专辑文案×3（商/夏/西周 卷1） | - | 名字/意境+标签+卖点+简介+发布清单；主档随专辑 | albums/{商,夏,西周}-卷1/专辑文案.md |
| 歌曲封面×9（gpt-image） | - | 妇好/商汤/伊尹/比干/大禹/文王/武王/周公旦/姜子牙；含歌名+人名 1024+800；Agnes 旧版 _v1_agnes 留档 | albums/{商,夏,西周}-卷1/封面/《歌名》_朝代_年代_人名(_800).png |
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

| 吐哺_短档（周公·4曲制样板） | 3:37/4:11/5:52/5:53 | 短2（殿乐4:11/说书留档）+叙2（史诗5:52/说书5:53）·词631/760/1081/991·四件套+封面 | output/history-rock/ + albums/义名之歌-西周-卷1/ |

| 商卷1短档6人（盘庚/武丁/傅说/微子/祖己/仲虺） | 12版 | 迁殷3:16/4:10 · 复兴4:39/4:11 · 版筑3:40/4:00 · 去国4:25/3:56 · 雊雉4:29/3:15 · 诰3:43/4:19——四件套+封面 | output/history-rock/ + albums/义名之歌-商-卷1/ |

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
- **坑（2026-10-15）**：背景脚本 workdir=scripts 时必须用绝对路径传 --lyrics/--out，相对路径会 FileNotFoundError（《吐哺》叙A2/叙B2 三连败后已修正重发）
- **观察（2026-10-15）**：抓耳短版在颂歌慢板风格下，631→760 字都落在 3:37-3:40（pad 追加在 Final 后=模型不唱）；工具已改为 Final 前插入；史诗颂歌类再快：盘庚 v1a 608字→3:16。短版分布 3:16-4:41（随风格唱速浮动）——抓耳版下限政策待用户试听后定
- **事故（2026-10-15）**：仲虺 v1a 被重复提交两次（重试时参数带错把 v1a 当 v1b 发），v1b 漏生成；已补发真 v1b（seed 833002 techno 卡）。教训：批量补发时必须逐一核对 seed/prefix/out 与目标版本一致
- **ps（2026-10-15）**：style 文本禁用英文撇号（PowerShell 单引号会截断命令——微子 v1a 因此挂过一次）
- **屈原《求索》完成（2026-10-15）**：战国卷首·楚辞风样板（楚辞启示录 §9）——短 v1a 4:28/v1b 4:13、叙 n1a 5:18/n1b 6:32；四件套+封面入 albums/义名之歌-战国-卷1/；下一棒：后羿《射日》（神话层神游体放飞）
- **别字版·检索状态（2026-10-15 复审）**：simple MCP 重启后客户端会话仍报 "Session not found"（需宿主重连/新会话）；web_search 仍缺 DEEPSEEK_API_KEY——网络论证继续待补；已按原理产出《求索》别字版原型（替换表见 _meta/别字版文件）
- **双版词规 v3（2026-10-15 用户定版）**：别字版=标准版全量映射高频同音字，固定喂 YuE2；标准版永不改。用户试听结论：《求索》A/B 均好听，但别字/标准版难辨咬字差 → 统一以高频别字版喂模型。
- **ignis 接入（2026-10-15）**：依 H:\Works\FeiTuPrj_H3\Docs\IMGFLOW_04_Ignis.md —— CLI 在 FeiTuPrj_H3\.tools\ignis\，调用前 `$env:USERPROFILE='H:\Works\FeiTuPrj_H3\.tools\fake-home'`，`ignis imagine --model gpt-image`；本会话可经 pwsh 直调（积分计费，用户已授权封面用途）
- **后羿《射日》完成（2026-10-15）**：夏卷1传说层、楚辞神游体×力量金属、单抽 v1（4:42，别字版仅 脩→修）；四件套+封面入 albums/义名之歌-夏-卷1/
- **字频筛查工具 v1（2026-10-15）**：scripts/lyric_char_report.py——易错/多音筛查+同音建议（谗→缠 等）；全量字频需外部表 input/external/现代汉语字频.txt（待网络恢复接入）；另有 **单抽默认**（新曲先一版，需要再抽）与 **双版词规 v2（标准版永不改，别字版仅逐字同音替换）**
- **专辑制作规范（2026-10-15 确立）**：docs/history-rock/专辑制作规范.md——文案/封面/歌词/歌曲全入 albums/<卷>/；文案体例参考既有喜马拉雅文案；**封面主通道 ignis gpt-image-2（可生成中文，当前会话未注册通道，待接入方式；未接入前 Agnes 兜底）**；商卷1 补 专辑合集封面+专辑文案+每曲文案，战国卷1 文案已回填
- **双版词规（2026-10-15 用户建议）**：标注版（人看/唱）+ 别字版（喂 YuE2：多音字/生僻字→同音同调常用字，提升咬字）；渲染喂别字版、展示用标注版；已写入人物库工作流 step3（注：当日 web 搜索通道不可用——web_search 缺 DEEPSEEK_API_KEY、简单MCP 搜索会话故障——相关论证待补查，先按原理落地）
- **战国卷开卷（2026-10-15）**：屈原《求索》= 卷首+楚辞风样板（楚辞启示录 → 风格配器库 §9：呼唤式 hook/乱曰收尾/意象锤/兮式拖腔/神游语汇）；后羿《射日》= 神话层放飞试验
- **人名规范改名（2026-10-15 用户确立）**：文件名/歌曲名一律用本名——周文王→姬昌、周武王→姬发、周公旦→姬旦、姜子牙→姜尚（已批量改名 173 文件 + meta/人物库/专辑信息同步；故事正文与评价表的叙述性旧称保留，属文学表达）
- **《吐哺》时间线修正（2026-10-15 用户发现）**：原词“成王与仲尼”为跨 500 年并列（仲尼=孔子，周公500年后）→ 改“成王记心间 / 五百年后，仲尼犹慕此贤”；长歌 n1a3/n1b3 已重生成（7:01/5:33/），短歌无此句保留；时间线审查已立为工作流规则（人名并列须同代，后世人物须带时间框架）
- **《吐哺》定稿（2026-10-15 用户确认：短+叙均接受）**：短档主推 v1b 4:11；叙档主推 n1a2 5:52 / n1b2 5:53。→ **抓耳短版时长政策定案：3:30-4:10 可接受，不强求 ≥4:00**（史诗颂歌类唱速快属正常）；长篇叙事 ~6 分钟达标
- **商卷1 整卷完成（2026-10-15）**：10 人名册 40 版全齐（每人 短2 + 叙2）；叙档时长 4:31-7:24；全部四件套+封面入 albums/义名之歌-商-卷1/；9 篇补位/新故事、词稿（短590-632 / 叙865-1030）、评价表 26 人
- **商卷1 短档完成（2026-10-15）**：10 人名册全齐（商汤/伊尹/盘庚/武丁/傅说/妇好/比干/微子/祖己/仲虺），各 2 短版（20 版，含四件套+封面）；补位三人（微子/祖己/仲虺）已入评价表（26 人）；叙事档待批量
- **每角色 4 曲制（2026-10-15 用户新架构）**：每人 = 短抓耳 2 版（当前 v1a/v1b）+ 长篇叙事 2 版（n1a/n1b，另写词稿）；发布定位：抓耳版→汽水/短视频，叙事版→喜马拉雅长音频；叙事版创作原则（≠短版拉长）：独立词稿（6-7min≈850+字）、多主歌按生平章节推进、可加念白/旁白、副歌主题句随段微变、器乐华彩间奏
- **双版本升级（2026-10-15 用户）：一次抽 2 个 = 双风格变体**——v1a/v1b 不再同风格异 seed，而是唱法/曲风/乐器拉开差距（≥2 维不同：主奏乐器、嗓音至少其一不同；混搭层尽量不同）；已写入风格配器库 §0；自下一首（文王/武王）起执行
- **白班新建议（风格多元化）**：摇滚为基座，混搭 techno/world/art/reggae/trance/synthwave/dance/electric 等；中西（→世界）乐器混配，每曲不同的主奏/副奏/节奏配置——待提炼为《风格配器库》（见下一步）
- 妇好线：v1L4/v2b/vB 三版待试听定稿（作品全部保留，不删）
- 下一步：试听妇好/大禹 → 定案 → 第三首（商汤《网开一面》→ 义名之歌-商-卷1）