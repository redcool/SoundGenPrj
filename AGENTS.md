# AGENTS.md · SoundGenPrj 工程知识文件（供 AI Agent 使用）

> 本文件写给任何进入本工程的 AI agent，先读它再动手。配套文件：`SESSION.md`（会话记忆/状态）。

## 1. 项目是什么

音频生成需求梳理与本地工具链。六大需求方向：
1. 文生曲（text→instrumental）
2. 文生歌（text→lyrics+song）
3. 曲/歌扩展（extend，谱面拉长）
4. 曲/歌 Cover（重作曲/翻唱）
5. 从歌中取出歌词（提取/转写）
6. 音效生成（SFX，不建议走 YuE2）

实现底座：**ComfyUI + FL-YuE2（YuE2-3B，本地 GPU）**。详见 `README.md` 与 `TECH_NOTES.md`。

## 2. 本机关键环境路径

- ComfyUI 便携版根目录：`H:\AI\ComfyUI_windows_portable\`
- Python 解释器：`H:\AI\ComfyUI_windows_portable\python_embeded\python.exe`（3.13.11；内置 torch 2.13+cu130、transformers 5.x、tokenizers、tiktoken、demucs 4.1.0、julius、soundfile、torchaudio）
- ComfyUI 服务：`http://127.0.0.1:8188`（API：`POST /prompt` 提交，`GET /history/{prompt_id}` 轮询结果；单 GPU 顺序排队；地址可在工程根 `config.json` 的 `comfyui_url` 修改）
- YuE2 自定义节点：`ComfyUI\custom_nodes\ComfyUI-FL-YuE2\`（`yue2/nodes.py` 的 max_duration 上限已从 360 改为 720s）
- 模型权重：`ComfyUI\models\yue2\YuE2-3B\` + `YuE2-Vae\`（sha256 已核验）
- 生成音频输出：`ComfyUI\output\audio\YuE2\`（48kHz 立体声 FLAC，重名自动 _00001）
- Demucs 权重：`demucs_models\htdemucs\`；Whisper（transformers 格式）：`whisper_models\whisper-small\`
- ffmpeg/ffprobe：`H:\Program Files\ffmpeg\bin\`
- 本机 GPU：RTX 5090 32GB；渲染约 2 倍实时耗时

## 3. 工程目录

```
SoundGenPrj/
├── README.md          # 需求梳理 + 能力矩阵 + 路线图（P0/P1/P2）
├── TECH_NOTES.md      # 技术要点与已知坑
├── config.json         # 服务地址等配置（comfyui_url 可改）
├── AGENTS.md          # 本文件
├── SESSION.md         # 会话记忆（当前状态/成品索引/偏好）
├── docs/              # 报告与记录（如 歌词核查报告.md）
├── scripts/           # YuE2 生成/后处理工具 CLI
├── tools/             # 通用工具（音频格式转换等）
└── input/ output/ models/ workflows/ logs/   # 建议目录
```

## 4. 工具清单与用法

### scripts/（均在脚本所在目录执行；内部用相对导入 lib_comfy）
```bash
# 文生歌/文生曲
python scripts/generate.py --style "..." --lyrics lyrics.txt --prefix audio/YuE2/demo --duration 480
python scripts/generate.py --style "..." --no-lyrics --prefix audio/YuE2/demo_inst   # 纯器乐
# 谱面扩展（默认 ~300 小节≈8 分钟；--zero-vocals 器乐化）
python scripts/extend.py --abc plan.abc --style "..." --prefix audio/YuE2/demo_ext --duration 520
# Cover（锁谱换词/换风格）
python scripts/cover.py --abc plan.abc --style "..." --lyrics new.txt --prefix audio/YuE2/cover
# Demucs 人声分离（no_vocals.flac + vocals.flac）
python scripts/separate.py --input audio/YuE2/xxx_00001.flac --out stems/xxx
# Whisper 歌词转写（建议喂 vocals.flac；先知会：金属嘶吼会幻觉，见 TECH_NOTES）
python scripts/transcribe.py --audio stems/xxx/vocals.flac --lang en
```

### tools/
```
convert_audio.bat [输入目录] [源格式] [目标格式] [输出目录] [码率]   # 默认 m4a→mp3，原地输出
convert_audio.ps1  # 主逻辑，参数：-InputDir -SourceExt -TargetExt -OutputDir -Bitrate -Force
```

## 5. 生成参数约定（实测推荐）

| 参数 | 推荐 | 说明 |
|---|---|---|
| planning | full / melody / off | 锁谱面必须 full 或 melody |
| guidance | 1.0（full/melody）/ 1.01（off） | ≠1 走双分支更慢 |
| max_duration | 300-520 | 需覆盖谱面理论时长（渲染长度≈小节数×1.6s×0.97） |
| acoustic_steps | 32 | 与官方 midpoint 对齐 |
| seed | 固定整数 | 固定即可复现 |

- 8 分钟 ≈ 300 小节（150BPM 4/4，1 小节=1.6s）；语义 token ≈ 秒×25，上下文 24576
- 锁谱面时歌词音节数应 ≈ 声乐线音符数（模型会自行重排歌词，中文咬字锁谱时打折）
- 纯器乐 = 双重保障：谱面 Vocal 清零 + Demucs no_vocals
- 生成“完整”判据：Render 输出文本为 `Song generation complete.`

## 6. 已知坑（务必先知）

1. **pip 不可用**：装包一律走 PyPI wheel 手动下载 + zipfile 解包进 site-packages（流程见 `.wheelhouse/`）
2. **python -c 引号易碎**：需要执行复杂 Python 时先落 .py 文件再运行
3. **生成 Python 源码时 
 转义坑**：在模板/脚本里写 Python 字符串时注意换行转义打回原形
4. **Whisper 对金属嘶吼会幻觉复读**（“Bye Bye Bye”等）；transformers 5.x pipeline 无 `condition_on_previous_text`；no_repeat_ngram_size 可抑制部分
5. **文件被用户改名**是常态：按当前真实文件名操作（先 Get-ChildItem 确认，别依据旧路径）
6. 输出目录/命名用 ASCII 前缀更稳；中文名文件照常支持
7. 令牌预算：前缀（style+歌词+谱面）+ 语义 token 必须 < 24576

## 7. 工程约定

- 生成参数变更后同步更新 `SESSION.md` 的“当前状态”
- 每次关键产出（新曲、新工具、新结论）在 `SESSION.md` 成品索引登记
- 用户偏好：中文沟通；8 分钟接受 ±30s 近似；完成后必须给出文件路径+时长+试听要点
- 未验证的能力（如 SFX）不要承诺，标注“未验证”即可
