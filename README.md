# SoundGenPrj · 音频生成需求梳理与实现路线（v1.0）

> 依据本机实际运行验证整理。运行环境：ComfyUI + FL-YuE2（YuE2-3B 音乐模型，约 6.9GB）
> 硬件要求：NVIDIA GPU + BF16，显存 ≥ 24GB（实测 RTX 5090 32GB 运行良好）
> 生成产物：48kHz 立体声 FLAC；渲染约 2 倍实时耗时
> 模型许可：CC BY-NC 4.0（非商用）

---

## 一、需求总览（六类）

### 1. 文生曲（Text → Instrumental Music）
- **定义**：风格/氛围描述 → 纯器乐曲
- **输入**：style 描述（体裁、乐器、速度 BPM、情绪、结构安排）
- **输出**：FLAC 纯音乐
- **实现**：FL_YuE2_Plan(planning=full 或 off, lyrics=空) → FL_YuE2_Render → FL_YuE2_Decode → SaveAudioAdvanced
- **状态**：✅ 已实现（重金属、电琵琶旋律死金等均已实测）
- **要点**：模型即使在无歌词时也会写出 Vocal 声部 → 建议 (a) 谱面清零 Vocal 音符 (b) 渲染后用 Demucs 去人声做双保险

### 2. 文生歌（Text → Song with Lyrics & Vocals）
- **2a 描述 → 歌词**：需文本 LLM 写词（本地未装；可接 Agnes 等 API，或手动给词）
- **2b 歌词 + 风格 → 人声歌曲**：✅ 已验证（中文歌词 + 重金属/旋律死金人声）
- **要点**：歌词“喂多少、唱多长”——歌词驱动（不锁谱面）时模型按歌词量作曲，演唱最准；锁谱面时歌词会被硬套到固定旋律上，中文容易走样

### 3. 曲与歌扩展（Extend）
- **3a 已有歌曲/谱面拉长**：✅ 谱面段落复制（本会话实测 3:43 → 8:29 完整长曲）
- **3b 续写式扩展（提示词引导）**：不可靠；**谱面操作是正路**
- **注意**：8 分钟需 ~300 小节谱面，且 render 上限需放开（本项目已放开到 720s）

### 4. 曲与歌 Cover（重作曲 / 翻唱）
- **4a 旋律保留 + 换歌词/换人声**：✅ 锁原谱 + 新歌词（已验证）
- **4b 换风格演绎**：改 style + 新 seed 重渲染；旋律大概率变化；想控旋律就锁谱
- **4c 完全重作曲**：= 文生曲/文生歌
- **4d 调式/配器变换**：谱面编辑（转调、和弦替换、加花/变奏）——可基于 ABC 做变换工具，编辑器（Piano Roll）已具备

### 5. 从歌中取出歌词（Lyrics Extraction）
- **5a 自产歌曲**：歌词就是输入，直接可得
- **5b 未知来源歌曲**：ASR 语音转文字（Whisper，本地 GPU）。英文较准；金属嘶吼类打折
- **5c 逐句时间轴**：Whisper timestamp 输出（工具链已备，见 scripts/transcribe.py）

### 6. 生成音效（SFX，枪声/剑声等）
- **结论**：YuE2 是“歌曲生成”模型，训练数据以音乐+人声为主，**不建议用于纯音效**（未验证，大概率不可靠）
- **建议路线**：
  1. 独立 T2A（文本→音效）模型：AudioLDM2 / Stable Audio Open（本地可跑，中等开发量）
  2. 免版权音效库（freesound / kenney.nl）——最快
  3. 程序化合成（Bfxr/FMOD）——可控性强
- **可选快速验证**：用极短（约 8s）YuE2 渲染试“gunshot”一次，成本低（随时可执行）

---

## 二、需求-能力矩阵

| # | 需求 | 可行性 | 状态 | 主路径 | 依赖/备注 |
|---|---|---|---|---|---|
| 1 | 文生曲 | 🟢 高 | ✅ 已实现 | Plan(full/off, 空词) → Render | 器乐需 Vocal 清零 + Demucs |
| 2a | 描述→歌词 | 🟢 高 | 🔶 待接 | LLM（Agnes 等） | 需要文本模型授权 |
| 2b | 歌词→歌 | 🟢 高 | ✅ 已实现 | Plan(full, 词) → Render | 歌词驱动演唱最准 |
| 3a | 扩展（拉长） | 🟢 高 | ✅ 已实现 | 谱面段落复制 | 8 分钟需 ~300 小节 |
| 3b | 续写扩展 | 🟡 中 | 🔶 待做 | 谱面生成式续写 | 需开发 |
| 4a | 旋律保留 cover | 🟢 高 | ✅ 已实现 | 锁谱 + 新词/新风格 | seed 固定 |
| 4b | 换风格 | 🟢 高 | ✅ 已实现 | 改 style 重渲染 | 旋律会变 |
| 4d | 配器/调式变换 | 🟡 中 | 🔶 待做 | ABC 变换工具 | 中等开发 |
| 5a | 取自产歌词 | 🟢 高 | ✅ 已知即得 | - | - |
| 5b | 未知来源歌词 | 🟡 中 | 🔶 链路已备 | Whisper 转写 | 嘶吼/中文准确度打折 |
| 6 | 音效 SFX | 🔴 低 | 🔶 未验证 | 独立 T2A / 音效库 | YuE2 不建议 |

---

## 三、推荐工具链（本目录 scripts/）

```
SoundGenPrj/
├── README.md            # 本文档
├── TECH_NOTES.md        # 技术要点与已知坑
├── config.json           # 配置（comfyui_url 等，默认 http://127.0.0.1:8188）
├── scripts/             # 可直接使用的 Python 工具
│   ├── lib_comfy.py     # ComfyUI API 封装（提交/轮询/取结果）
│   ├── generate.py      # 文生曲 / 文生歌
│   ├── extend.py        # 谱面扩展（段落复制拉长）
│   ├── cover.py         # 旋律保留换词/换风格
│   ├── separate.py      # Demucs 人声分离（去人声/取人声轨）
│   └── transcribe.py    # Whisper 从歌声提取歌词（时间轴）
├── tmp/                  # 临时代码与资源（不入 git）
└── input/ output/ models/ logs/   # 建议目录
```

### 快速开始

> 运行前确认工程根 `config.json` 的 `comfyui_url` 指向你的 ComfyUI（默认 http://127.0.0.1:8188，可直接修改）。

```bash
# 文生歌（中文歌词）
python scripts/generate.py --style "melodic death metal, electric pipa, Mandarin vocals" --lyrics lyrics.txt --out audio/YuE2/demo --duration 480
# 文生曲（纯器乐）
python scripts/generate.py --style "instrumental epic metal, electric pipa lead, no vocals" --no-lyrics --out audio/YuE2/demo_inst --duration 480
# 扩展已有谱面到约 8 分钟
python scripts/extend.py --abc plan.abc --out audio/YuE2/demo_ext --duration 480
# 去人声（Demucs）
python scripts/separate.py --input audio/YuE2/demo_00001.flac --out stems/demo
# 提取歌词（Whisper）
python scripts/transcribe.py --audio stems/demo/vocals.flac --lang en
```

---

## 四、工程目录规划建议

```
H:\Works\SoundGenPrj\
├── README.md / TECH_NOTES.md
├── docs/                  # 需求、评审、模板
├── scripts/               # 工具脚本（已提供初版）
├── input/                 # descriptions/ lyrics/ scores/
├── output/                # audio/ stems/ lyrics/
├── models/                # 模型权重引用/下载清单
├── workflows/             # ComfyUI 工作流 json
├── logs/                  # 生成参数记录（可复现）
└── config.yaml            # 通用参数（BaseURL、默认时长等）
```

---

## 五、路线图 / 建议优先级

- **P0（已完成）**：1 文生曲、2b 歌词→歌、3a 谱面扩展、4a/4b cover、5a 歌词已知
- **P1（建议下一步）**：
  - 2a 接 LLM 实现“描述→歌词”（把用户故事/情绪自动转成歌词）
  - 5b 转写链路完善（中文 Whisper 模型、结果清洗、逐句时间轴）
  - 4d 谱面变换工具（转调/重配器），做成 CLI
- **P2（可选）**：6 音效（独立 T2A 或素材库）；批量生成；参数化 Workflow 模板；生成日志/版本管理

---
*本文档会随实践持续更新。技术细节、参数和“已知坑”见 TECH_NOTES.md。*
