# TECH_NOTES · 前置环境部署与工程关键点（v2.0）

> 面向全新设备部署。本机已就绪的环境见文末“第 9 节 本机现状（示例）”。

## 0. 前置软件部署清单（从零开始）

> Windows 10/11。按编号顺序安装，每步都有“验证”命令，全部通过再往下。
标注 [必装] = 生成/转换必需；[按需] = 仅特定功能需要。

### 0.1 Python 3.11-3.13 [必装]
- 下载：https://www.python.org/downloads/ （3.11/3.12/3.13，安装时勾选 “Add python.exe to PATH”）
- 验证：`python --version`
- 说明：YuE2 依赖 torch≥2.x。ComfyUI 便携版自带 python_embeded；本机 Python 用于跑本项目 scripts/ 工具。

### 0.2 Git [按需]
- 下载：https://git-scm.com/download/win （默认选项）
- 验证：`git --version`
- 说明：仅当用 git 安装/更新 ComfyUI 节点时需要。

### 0.3 ffmpeg [必装：转码/格式转换]
- 下载（二选一）：
  - https://www.gyan.dev/ffmpeg/builds/ → release 版 zip
  - https://github.com/BtbN/FFmpeg-Builds/releases （选 win64 gpl latest zip）
- 解压到 `C:\ffmpeg`（内层 `bin` 目录含 ffmpeg.exe / ffprobe.exe）
- **加入环境变量 PATH**：Win+R → `sysdm.cpl` → 高级 → 环境变量 → 系统变量 → Path → 编辑 → 新建 → 粘贴 `C:\ffmpeg\bin` → 确定（新开终端才生效）
- 验证：`ffmpeg -version`、`ffprobe -version`
- 本项目使用：`tools/convert_audio.ps1` 默认调 PATH 中的 ffmpeg，也可 `-Ffmpeg` 指定路径；config.json 可配 `ffmpeg` 项。

### 0.4 Node.js LTS [按需：仅 ComfyUI 桌面版 / 前端开发]
- 下载：https://nodejs.org/ （LTS 版 msi，自动加入 PATH）
- 验证：`node -v`、`npm -v`
- 说明：命令行版 ComfyUI 无需 node。

### 0.5 NVIDIA 驱动（GPU 条件）[必装]
- YuE2-3B 需要 NVIDIA GPU 且显存 ≥ 24GB（BF16 推理；RTX 5090 32GB 实测良好）
- 安装最新 Game Ready / Studio 驱动；PyTorch 自带 CUDA 运行时，驱动较新即可，一般无需单独装 CUDA Toolkit。
- 验证：`nvidia-smi` 能看到 GPU。

### 0.6 ComfyUI [必装：生成主引擎]
- 方式 A（便携版，最省事）：下载 ComfyUI_windows_portable 解压即用（自带 Python/torch）。
- 方式 B（源码）：
  ```
  git clone https://github.com/comfyanonymous/ComfyUI
  cd ComfyUI
  pip install -r requirements.txt
  python main.py            # 默认端口 8188
  ```
- 服务地址：**本项目脚本连的地址写在 `config.json` 的 `comfyui_url`（默认 http://127.0.0.1:8188），用户可改**。
- 验证：浏览器打开 http://127.0.0.1:8188 看到工作台。

### 0.7 ComfyUI-FL-YuE2 节点 [必装]
- 安装：
  ```
  git clone https://github.com/filliptm/ComfyUI-FL-YuE2  ComfyUI\custom_nodes\ComfyUI-FL-YuE2
  pip install -r ComfyUI\custom_nodes\ComfyUI-FL-YuE2\requirements.txt
  ```
- **8 分钟支持（重要）**：编辑 `yue2/nodes.py`，把 `max_duration` 的 `"max": 360` 改为 `720`，重启 ComfyUI（否则 API 会拒绝 >360s 的请求）。config.json 的 `yue2_node_path` 可指向节点目录（供 extend.py 解析谱面）。
- 验证：工作台左侧出现 FL_YuE2_ModelLoader / FL_YuE2_Plan / FL_YuE2_Render。

### 0.8 YuE2 模型权重 [必装]
- 下载（HuggingFace，需登录/同意许可）：
  - **YuE2-3B** → https://huggingface.co/m-a-p/YuE2-3B （model.safetensors 约 6.9GB + qwen.tiktoken 等 9 个文件）
  - **YuE2-Vae** → https://huggingface.co/m-a-p/YuE2-Vae
- 存放（目录名不能错）：
  ```
  ComfyUI\models\yue2\YuE2-3B\
  ComfyUI\models\yue2\YuE2-Vae\
  ```
- 建议 sha256 校验后再用（本机已核验，revision 记录在 SESSION.md）。
- 许可：CC BY-NC 4.0（非商用）。

### 0.9 MiniMax Music 3 [按需：云端 API，非本地安装]
- MiniMax Music 3 是**云端音乐生成服务**（minimax 平台 / Hailuo），不是可下载模型，本地装不了：
  1. 注册账号 → 控制台创建 API Key
  2. 编写结构化 caption（风格/歌词/段落结构建议写全；可用 music-caption-rewriter 技能辅助生成）
  3. 调用 HTTP API 提交任务并轮询结果（见官方文档；注意计费）
- 本地离线替代：Meta MusicGen / Stability Stable Audio Open（HF 权重，本机 torch 推理）。
- 本工程当前生成主路径仍是 YuE2（本地）；MiniMax 作为云端候选记录在案。

### 0.10 后处理（可选，工具链已含）
- **Demucs**（人声分离）：htdemucs 权重约 81MB → 默认存 `demucs_models\htdemucs\`（config.json `demucs_model_dir` 可改）
- **Whisper**（歌词转写）：whisper-small 约 922MB（transformers 格式）→ 默认存 `whisper_models\whisper-small\`（config.json `whisper_model_dir` 可改）

---

## 1. 时长与 token 预算
- 语义 token 数 = 秒数 × 25（render 内部 max_tokens = round(max_seconds × 25)）
- 模型默认编曲 3-7 分钟；**“8 分钟”必须靠谱面长度撑**：约 300 小节（4/4、150BPM 时 1 小节 = 1.6 秒）
- 节点原上限 360s → 需改 nodes.py 为 720s（见 0.7）
- 上下文 24576 token：前缀（style+歌词+谱面）与语义预算之和须小于它；8 分钟（≈12-13.5k 语义 token）可容纳

## 2. 歌词与演唱的对齐（重要）
- **歌词驱动（不锁谱面）**：模型按歌词量作曲，演唱最忠实（实测中文歌词逐句对得上）
- **锁谱面（给 ABC）**：人声旋律固定，歌词被“硬套”；**歌词音节数 ≈ 声乐线音符数**时明显改善
  - 做法：先解析谱面 Vocal 声部音符数（约 1 音节 = 1 音符），再分配歌词行
  - 模型仍会自行重排/改写歌词（如把中文段唱成自己的英文句），可接受度需确认
- 英文演唱比中文更稳；中文可用 Qwen 词典编码，但咬字依赖模型能力

## 3. 纯器乐的“人声残留”问题
- 模型语义阶段会把旋律渲染成类人声音色（即使 Vocal 声部全休止、提示词禁用）
- **可靠方案（双保险）**：
  1. 谱面 Vocal 声部清零（音符→等长休止，保留和弦与结构）
  2. Demucs 人声分离（htdemucs），取 no_vocals 轨
- 实测：清零 + 分离后，伴奏轨已无听感人声（vocals.flac 内容可对照）

## 4. 工程参数速查
| 参数 | 推荐值 | 说明 |
|---|---|---|
| planning | full（谱面+和弦）/ melody / off | 锁谱时必须 full 或 melody |
| guidance | 1.0（full/melody）/ 1.01（off） | ≠1 时跑双分支（更慢） |
| max_duration | 300-520 | 覆盖谱面长度，留余量 |
| acoustic_steps | 32 | 与官方 midpoint 求解器对齐 |
| seed | 任意固定值 | 固定即复现；换词想保旋律可固定 |
| temperature / top_p / top_k | 1.0 / 0.95 / 100 | 默认即可 |

## 5. 谱面（ABC）操作
- 双声部方言：Vocal + Ins 两行交替；和弦符号在引号内（如 "Dm"）
- 段落用 % 段名 注释标记；扩展 = 整段复制（保持声部交替顺序）
- 操作后必须过 yue2/abc_score.parse() 校验（extend.py 已内置）
- 转调/替换和弦：直接改 K: 与和弦符号（尚未封装工具，P1）

## 6. 配置说明（config.json，工程根）
```json
{
  "comfyui_url": "http://127.0.0.1:8188",   // ComfyUI 服务地址，可改
  "ffmpeg": "ffmpeg",                       // ffmpeg 可执行（PATH 或绝对路径）
  "python": "python",                        // python 可执行
  "yue2_node_path": "",                     // ComfyUI-FL-YuE2 节点目录（extend.py 解析谱面用；留空用内置默认）
  "whisper_model_dir": "",                  // whisper 权重目录（留空用内置默认）
  "demucs_model_dir": ""                    // demucs 权重目录（留空用内置默认）
}
```
当某项留空或文件不存在时，脚本回退到内置的默认路径。

## 7. 后处理工具
- **Demucs 4.1.0（htdemucs 单模型）**：手动 wheel 安装路径记录于 .wheelhouse；权重约 81MB（HF 下载）；5090 上约 110 秒音频/秒处理
- **Whisper（transformers 5.x 自带）**：whisper-small 约 922MB；转写提取歌词与时间轴；注意 whisper tokenizer 无 pad_token，pipeline 批处理需设置 `pipe.tokenizer.pad_token_id = eos_token_id`
- 无需 ffmpeg（读写用 soundfile / torchaudio）

## 8. 其他已知坑
- 生成“完整”判据：Render 输出文本 "Song generation complete."（非 "Duration limit reached"）
- 输出时长可能比谱面理论短（模型提前收尾）；要更精确可微调谱面尾部
- 文件重名自动加序号（_00001）；API 提交的请求会排队按序执行
- 一次生成不能中途停续；长曲建议分段规划
- 沙箱/pip 受限环境：依赖用 PyPI wheel 手动下载 + zipfile 解包进 site-packages（已沉淀流程，见 .wheelhouse）
- 生成 Python 源码时注意换行转义（脚本模板里 \n 会变真实换行导致 SyntaxError）

## 9. 本机现状（示例，与 0-8 节对应）
- Python 3.13.11 内嵌（ComfyUI 便携版 python_embeded）；torch 2.13+cu130；RTX 5090 32GB
- ComfyUI 服务：127.0.0.1:8188（config.json comfyui_url）
- YuE2 模型：ComfyUI/models/yue2/（YuE2-3B + YuE2-Vae，sha256 已核验）
- ffmpeg：H:\Program Files\ffmpeg\bin\（已入 PATH）
- Demucs/Whisper 权重已下载（demucs_models\htdemucs、whisper_models\whisper-small）
- 音频输出：ComfyUI/output/audio/YuE2/（48kHz FLAC）
