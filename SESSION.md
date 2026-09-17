# SESSION.md · 会话记忆（由 agent 维护，跨会话接力）

> 本文件记录工程当前状态、成品索引与用户偏好。新 agent 先读 `AGENTS.md` 再读本文件。

## 最近更新

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
  - **Music3 试听**：scripts/minimax_music3.py + caption/歌词已备好（input/captions/melodeath_pipa_m3_caption.txt、input/lyrics/一百五十年的伤痕.txt），**只差 minimax.api_key**（config.json）；主题=《一百五十年的伤痕》旋律死金+电琵琶
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

更早的作品（melodic_heavy_metal 系列、pure_instrumental_metal 等）曾存在 ComfyUI/output/audio/YuE2/，部分被用户整理/移走，以磁盘现状为准。

## 用户偏好（重要）

- 中文交流；沟通结果附 文件路径 + 时长 + 试听要点
- “8 分钟”接受 7:50-8:20 近似
- 歌词重排/模型自行改词可接受（“完稿”即收）
- 纯器乐 = 不允许人声；中文歌词要准（歌词驱动模式下咬字最好）
- 音效需求：YuE2 不做，建议其他方案
- 工具化诉求强：新需求尽量沉淀为可复用脚本（ps1/bat/py）

## 常用服务状态

- ComfyUI：127.0.0.1:8188（单 GPU，任务排队；托管方式：后台 pwsh 任务）
- 沙箱：当前会话 danger-full-access；pip 不可用（wheel 手动解包）
- Whisper：whisper_models/whisper-small（transformers 格式，需 pipeline 设置 tokenizer.pad_token_id=eos_token_id 才能批处理）
