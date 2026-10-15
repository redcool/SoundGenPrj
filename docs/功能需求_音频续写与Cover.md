# 功能需求：音频续写（extend_audio）与音频 Cover（cover_audio）通用工具

> 状态：DRAFT（2026-09-21）
> 目标读者：本项目 AI agent 与用户；实现前先确认本文档，实现过程按 P0/P1/P2 拆分逐个落地。
> 关联：AGENTS.md（工程约定）、TECH_NOTES.md（能力边界与坑）、scripts/{generate,extend,cover,separate,transcribe}.py

---

## 0. 背景与动机

工程现有工具全部要求**输入是文本/谱面**（style+lyrics+ABC），生成的也是全新音频。
用户手上常见素材却是"一段已有音频"（如《一夫当关.mp3》，AI 平台生成的 2:47 纯器乐），期望：

1. **延长它**：同样的风格与调子，生成新的段落，与原有音频拼合成更长的完整曲目（如 8 分钟）。
2. **Cover 它**：依据原音频的风格与调子，用新的乐器组合 / 新的调性（带一定随机性）演绎成一个新版本。

这两件事目前只能靠手工组合工具凑（先分析→再 generate→再 ffmpeg 拼接），且 pygame/ffmpeg 等零散步骤没有沉淀。
本需求把它们固化为**两个通用 CLI 工具**：`scripts/extend_audio.py` 与 `scripts/cover_audio.py`。

---

## 1. 需求一：音频续写 extend_audio

### 1.1 目标
输入一段音频（mp3/flac/wav），输出 `原音频 + 同风格续写段落` 拼合后的更长音频。
语义："延续这首曲子，不是重做"。

### 1.2 输入 / 输出契约
```
python scripts/extend_audio.py \
  --input inputSound/一夫当关.mp3 \
  --target-duration 480          # 目标总长(秒)；默认 480(≈8:00) \
  --style "..."                  # 可选：风格描述；缺省时从原曲自动分析 + 默认风格 \
  --out output/yue2/一夫当关_续写版 \
  --format mp3 --bitrate 320     # 交付格式；复用 tools/convert_audio.ps1 逻辑
```
输出：拼合后的完整音频（默认 mp3 320k），外加：
- 续写段原始 flac（引擎输出）
- `plan.json` 或记参数日志（可复现）
- `analysis.json`：原曲分析结果（BPM/调性/风格标签/人声占比）

### 1.3 处理链路（六步）
1. **原曲分析**（新增 `lib_comfy.analyze` 或独立 `scripts/analyze_audio.py`）
   - ffprobe：时长 / 采样率 / 声道 / 码率
   - BPM 检测：自相关峰（工程已沉淀，tmp 中的 FFT 自相关脚本升级进正式模块）
   - 调性（key）检测：chroma 直方图 + Krumhansl-Schmuckler 模板打分（numpy/scipy 即可，无需 librosa）
   - 人声占比：Demucs 分离后按 RMS 能量比（已有 separate.py 逻辑）
   - 输出 `analysis.json`
2. **风格构建**：用户 `--style` 优先；缺省时 = 分析特征（BPM/调性/人声）+ 明确"续写风格一致"措辞
3. **续段生成**：`generate.py` 逻辑（planning=full，seed 可传），duration = 目标总长 − 原曲时长
   - 为保证调性一致：style 中显式写明 `in [key]`（如 "in A minor"），并固定 seed
4. **对齐**：检查两段采样率/声道，必要时 resample（ffmpeg）
5. **无缝拼接**：ffmpeg concat（两段同参数直拼）；可选 `--crossfade` 秒数做交叉淡化（默认 0.5s，需保证 BPM 对齐，否则宁可不淡）
6. **格式交付**：复用 `tools/convert_audio.ps1`（mp3 320k），工程约定见 SESSION.md

### 1.4 验收标准
- 输出总长 ≈ 目标长（±5s，模型提前收尾属已知特性，续段以实际生成为准）
- 听感：拼接点无明显断崖/速度突变（BPM 一致）
- 调性：续段主音/调性与原曲一致（客观可测：两段 chroma 主峰一致）

### 1.5 已知风险与对策
| 风险 | 对策 |
|---|---|
| 续段调性跑偏 | style 显式 key + 生成后 chroma 校验；不合格丢弃重 roll |
| 续段提前收尾（模型特性） | duration 留 10~15s 余量；收尾完不完整可补一段 outro 重拼 |
| 拼接点不齐 | 按 BPM 计算拼接拍点，对齐到整拍后再 concat |
| 原曲非 44.1k | 统一 resample 到 44.1k 或 48k（与续段一致） |

---

## 2. 需求二：音频 Cover cover_audio

### 2.1 目标
输入一段音频，输出"基于其风格与调子、但用新乐器和（可能新的）调性"演绎的新版本，
随机性体现在乐器选择 / 配器 / seed 上（同一输入每次可出不同版本）。

### 2.2 输入 / 输出契约
```
python scripts/cover_audio.py \
  --input inputSound/一夫当关.mp3 \
  --style "epic orchestral metal, brass and strings, new arrangement"  # 新乐器/新演绎表述 \
  --transpose +2                  # 可选：转调（半音）；默认同调 \
  --seeds 3                       # 出 3 个不同随机版本 \
  --out output/yue2/一夫当关_cover \
  --format mp3 --bitrate 320
```
输出：每个 seed 一个完整音频 + 若转谱成功则附 score.abc。

### 2.3 两条实现路线（依赖成本不同）

**路线 A：音频→谱面→锁谱 cover（推荐，最忠于原旋律）** —— P1
1. 原曲分析（同 1.3.1）
2. **SheetSage2 转写**：H:\AI\YuE 官方 covers.md 流程（Python 3.11 独立 venv + FFmpeg 6.1 + MERT 编码器，需下载 ~2-3GB）→ 得到 `score.abc`（含旋律，可选和弦）
3. 谱面变换：`--transpose` 直接改 `K:` 与音符（开发 `scripts/transpose_abc.py`，P1）
4. `cover.py` 现有链路：锁谱（planning=full）+ 新 style + 多个 seed → 多版本
5. 交付/格式转换同上

**路线 B：不转谱的"风格化演绎"（轻量，旋律不严格保留）** —— P0 可先行
1. 原曲分析（同上）
2. Whisper 歌词转写（有此曲则带词，纯器乐则跳过）
3. 新 style（用户描述或分析派生的"换乐器"描述）+ 固定原调性 + 多 seed 重生成
4. 交付

> 决策点：路线 A 需要安装 SheetSage2（约 2-3GB + 独立 Python 环境，一次性成本 ~15-30 分钟）。
> 如果用户要"旋律基本保留"的 cover，必须走 A；接受"风格化演绎"则 B 足够。

### 2.4 验收标准
- 输出可听，且明显是"新乐器/新配器"版本（与原文在原调上可对比）
- 多 seed 之间互不相同（旋律/配器有差异）
- （路线 A）谱面转写 error 为 None，且音频与 score 对应

---

## 3. 通用设计

### 3.1 共用模块
- `scripts/lib_comfy.py` 扩展：
  - `analyze_audio(path) -> analysis dict`（BPM/key/chroma/人声占比/时长）
  - `join_audio(seg1, seg2, out, crossfade=0, resample=44100)`（ffmpeg concat/crossfade）
  - `to_delivery(src, out, fmt="mp3", bitrate=320)`（调 convert_audio.ps1）
- 新文件：
  - `scripts/analyze_audio.py`（CLI 包装，也可单独用）
  - `scripts/extend_audio.py`
  - `scripts/cover_audio.py`
  - `scripts/transpose_abc.py`（P1，谱面转调）

### 3.2 配置（config.json）
增加：
```json
"extend": { "crossfade": 0.5, "default_format": "mp3", "default_bitrate": 320 },
"sheetsage2": { "venv": "", "model": "m-a-p/SheetSage2", "ffmpeg61": "" }
```

### 3.3 交付与日志
- 一律 mp3 320k（除非 --format 指定）；flac 仅存引擎原生输出
- 每次运行写 `logs/` 记录：输入 sha256、style、seed、duration、分析结果、渲染状态（complete/truncated）
- SESSION.md 成品索引登记

---

## 4. 实现计划（逐个落地）

### P0（无新依赖，立即可做）
- [ ] `lib_comfy.analyze_audio`：BPM（自相关）+ 调性（chroma+KS）+ 人声占比（demucs）+ 时长
- [ ] `scripts/extend_audio.py`：分析→同风格续段→对齐→concat→交付（路线=同风格重制拼合）
- [ ] 用《一夫当关》实测：2:47 → ~8:00 拼合版

### P1（需装 SheetSage2）
- [ ] SheetSage2 转写环境搭建（按 YuE covers.md）
- [ ] `scripts/transpose_abc.py`：谱面转调
- [ ] `scripts/cover_audio.py` 路线 A（转谱→锁谱→多 seed）

### P2（增强/按需）
- [ ] cover_audio 路线 B（风格化演绎，用 Whisper 歌词）
- [ ] 续写拼接的"整拍对齐"增强（BPM 网格吸附）
- [ ] 多段续写（分段生成再拼，支持 >10 分钟）
- [ ] 随机乐器库：预置几套"换乐器"style 模板，--flavor 选择

---

## 5. 待确认问题（实现前）
1. extend 的"同调性"是否严格要求？（A：严格，key 检测+校验 / B：宽松，只 style 里写 key）
2. cover 是否要装 SheetSage2？还是一开始就走"风格化演绎"（不锁谱）？
3. 默认交付格式维持 mp3 320k 即可？（确认）
