# Studio（yue2.cpp）渲染流程与规范（2026-10-20 定稿）

> 定位：**主渲染器（2026-10-23 起 = YuE2-Studio 3.7.0 / yue-server，端口 8090）**。ComfyUI-FL-YuE2 降为备用（需谱面定位/精修时用）。实测速度：单版 **56-172 秒**（ComfyUI 同曲 15-25 分钟）。

## 一、引擎与服务

- 引擎路径：`H:\AI\YuE2-Studio-3.6.0-portable-windows-x64\resources\yue2-cpp\yue-server.exe`
- 模型（GGUF）：`data\models\yue2-cpp\YuE2-3B-Q8_0.gguf`（3.5GB）+ `YuE2-Vae-F32.gguf`（0.5GB）；可选 SheetSage2（转谱）/ MERT（音频特征）
- 启动（常驻，端口 8091）：
```
yue-server --model data\models\yue2-cpp\YuE2-3B-Q8_0.gguf --vae data\models\yue2-cpp\YuE2-Vae-F32.gguf --port 8090 --keep-loaded
```
- 工作目录须为 `resources\yue2-cpp`（引擎按相对路径找依赖）。
- ⚠️ **不要用 `| Select-Object -First N` 管道包裹**——管道关闭会杀掉服务进程（曾误杀两次）。用后台任务直跑或重定向到文件。

## 二、API 契约（已验证）

1. `POST http://127.0.0.1:8090/synth`，JSON：`{id, style, lyrics, seed}` → 返回 `{id: <job>}`
2. 轮询 `GET /job?id=<job>&result=1`：
   - **404 = 未就绪**（继续等，间隔 4-5 秒）
   - **200 = 完成**，`Content-Type: multipart/mixed; boundary=yue2-batch-boundary`，含两部分：
     - `application/json`：style / lyrics（回显）/ **abc（ABC 谱面）** / seed / lm_seed / semantic_tokens
     - `audio/mpeg`：歌曲 mp3（服务端默认 **128kbps / 48kHz / 立体声**）
3. 时长由歌词结构决定（**无 340s 上限**，ComfyUI 的截断问题在此不存在）。

## 三、脚本与用法

```bash
# 渲染（自动 192k 标准化）
python scripts/yue_render.py --lyrics <别字版.txt> --style <style> --seed <N> --out-prefix <绝对路径前缀>
# 产出：<前缀>.mp3（192k/48k）+ <前缀>.abc（谱面）+ <前缀>.json（元数据）

# 单独标准化（已有 mp3 / flac）
powershell -File scripts/audio_norm.ps1 -Path <文件>
# mp3 → 192k/48k（原 128k 备份为 *_128k.mp3）；flac → *_master32.wav（48k/32bit float）+ *_192k.mp3
```

## 四、命名规范（铁律）

### 4.0 国别字段（2026-10-23 用户定 · 春秋/战国起强制）

- 格式：`《歌名》_朝代_约前XXX_国_本名[_版本][_引擎].mp3`
- 示例：`《一鸣》_春秋_约前613_楚国_熊侣_v1a_studio.mp3`
- 适用：**春秋、战国**（多国并立时代）；商/西周/夏等单一王朝可省略（或写 商/周）。
- 意义：一个朝代只开一张专辑（义名/恶名各一），国别写进文件名即可筛选，**不再按国分卷**。
- 国名用简称：齐/晋/楚/秦/郑/鲁/宋/卫/吴/越/燕/陈/蔡/曹/滕/莒/邾/周（王畿）。


- 歌曲/词稿：`《歌名》_朝代_年代_本名[_narr][_v版本][_引擎].mp3`
- **人名一律本名，不用称号**：姬诵(成王)/姬钊(康王)/姬满(穆王)/姬虎(召穆公)/姬胡(厉王)/姬宫湦(幽王)/姬静(宣王)/姬燮(夷王)/姬囏(懿王)/姬高(毕公高)/姬封(康叔封)/姬鲜(管叔)/姬度(蔡叔)/姬处(霍叔)；史称无本名者保留（荣夷公/虢石父/申侯/伯夷叔齐/兮甲/虢季子白/芮良夫）。
- 版本后缀：`_v1a/_v1b`（A/B 双抽）；曲风试验 `_v2_techno/_v2_trance/_v2_reggae`；重抽加 2/3。
- 引擎标识：Studio 版 `_studio`；ComfyUI 版 `_yue2`。

## 四点五、人声锁定（2026-10-23 用户反馈「出现 yeah 助气」后新增·强制）

### 现象与原因
- 现象：成品里出现 yeah / oh / uh / hey 等 ad-lib 助气，或和声垫底。
- 原因：style 描述里出现 `chant`、`choir`、`shout`、`groove`、`funk`、`call and response`、`background vocals` 这类词，模型会自动加即兴人声。

### 处理（脚本已自动化）
- `scripts/yue_render.py` 内置 `VOCAL_LOCK` 后缀，**自动追加到每条 style**：
  `solo lead vocal only singing the given lyrics, no ad-libs, no yeah, no oh, no uh, no hey, no improvised vocalizations, no backing vocals, no choir, no shout-along, no call and response, no vocal fills between lines, clean articulation, Mandarin Chinese vocals, no English vocals`
- 因此 style 里**必须避免**这些词：chant / choir / shout / scream-along / groove / funk / hype / crowd。
- 人声描述推荐写法：`controlled low male vocal` / `restrained female vocal` / `clean male baritone`（只写音色与语气，不写「齐吼/合唱」）。

### 结构侧配合
- 歌词里不要写 `(yeah)`、`oh~`、`hey!` 这类衬词；副歌重复靠同一句复沓，不靠拟声。
- bz 版仍需只保留官方段标（`[Verse]/[Chorus]/[Bridge]/[Outro]`），段标内的「齐吼/黑嗓」等提示会被 strip。


- **MP3：192 kbps / 48 kHz / 立体声**（320k 多数设备无优势，不必用）。
- **母带（可选）：48 kHz / 32-bit float WAV**（服务端 FLAC 母带转出；MP3 无位深概念）。
- 保留原 128k 备份 `*_128k.mp3`（不删不破坏）。

## 六、入册流程（每曲）

1. 词稿过 `scripts/audit_lyrics.py`（段标唯一 / 无同文垫段 / 词量 520-700）→ **全绿才准渲染**；
2. `yue_render.py` 渲染 A/B（或试曲风单抽）；
3. 探时长（ffprobe）；
4. 入册：`output/history-rock/` + `albums/<卷>/歌曲/`（mp3 + abc + json）；`歌词/`（_lyric/_style/_meta）；`别字歌词/`（_v*_bz）；
5. 登记：专辑信息曲目表状态、每曲文案、SESSION。

## 七、曲风策略（实测结论）

- **律动系优先**：techno / trance / reggae / edm / metal / industrial——旋律与编曲完成度高，一抽可用（甘棠 v2 三卡均明显优于 v1 民谣/电子；ComfyUI 时代同结论）。
- **民谣/原声类**：需多抽，或用「民谣骨+电子肉」混搭。
- 双抽默认：A=律动系主卡（techno/metal），B=对比卡（编曲层或情绪不同，≥2 维差异）。
- 试曲风单抽：`_v2_<风格>` 命名，保留旧版对比。

## 八、故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 端口连不上 | 服务被管道/任务杀掉 | 重启动（见 §一）；查 Get-CimInstance Win32_Process -Filter Name='yue-server.exe' 杀残留 |
| 启动即退出 exit 1 | 端口被孤儿占用 | 先杀占用进程再启动 |
| job 一直 404 | 渲染未完成（正常，4-5 秒轮询） | 等 60-180 秒 |
| 单版 >5 分钟 | 歌词过长/GPU 忙 | 正常范围；长歌词可拆段 |
| mp3 只有 4MB/4min | 128k 默认 | audio_norm.ps1 转 192k（脚本已自动） |

## 九、验收清单

- [ ] 词稿 audit 全绿（段标唯一/无同文垫段/520-700 字）
- [ ] 命名合规（本名 + 朝代 + 年代 + 版本 + 引擎）
- [ ] mp3 192k/48k（`*_128k.mp3` 备份在）
- [ ] abc 谱面 + json 元数据入册
- [ ] 专辑信息 / 每曲文案 / SESSION 登记
## 十、Style 五段式模板（2026-10-23 用户提供范例后定稿）

### 为什么这样写（YuE2 的特点）

1. **YuE2 的 style 是「整体氛围提示词」，不是编曲指令**：它不理解「第二段加弦乐」这种段落编排，会把描述平均分配到全曲。因此不要写「chorus 时…、bridge 时…」，要写**全曲统一的音色与走向**。
2. **曲风必须前置**：前 3-5 个词决定整体走向（`Chinese wuxia rock` / `power metal` / `dark techno`）。
3. **BPM 要写**：YuE2 会用 BPM 定速度与律动密度（不写则随机漂移）。
4. **人声描述越具体越稳**：性别 + 音域 + 音色 + 距离感（close-mic/distant）+ 克制度。
5. **长 prompt 可以，但要 60-110 词**（≈400-750 字符）；超过 120 词，模型会稀释关键信息。
6. **触发 ad-lib 的词**（chant / choir / shout / gang vocal）——除非你明确要合唱，否则不要写；脚本已自动附加 VOCAL_LOCK。

### 五段结构（按顺序写，用分号连接）

| 段 | 内容 | 示例 |
|---|---|---|
| ① 曲风 + 情绪 | 主 genre + 温度/克制度 | `Chinese wuxia rock, mid-slow and restrained` |
| ② 速度 + 律动 | BPM + 节奏型 | `96 bpm, half-time drums with a slow build` |
| ③ 乐器链 | 3-6 件，中西合并用拼音术语，标注质感 | `solo guqin and xun under distant war drums, crackling electric pipa, tolling bianzhong, low electric bass pulse` |
| ④ 人声 | 性别/音域/音色/距离/克制 | `low male lead, hushed and close-mic, aged and story-worn` |
| ⑤ 制作 + 语言 | 混音质感 + 语言锁定 | `dry, roomy, unprocessed production; Mandarin Chinese vocals` |

### 乐器术语表（拼音，模型识别更好）

`bianzhong`（编钟）· `guqin`（古琴）· `guzheng`（古筝）· `pipa`（琵琶）· `erhu`（二胡）· `dizi`（笛）· `xiao`（箫）· `xun`（埙）· `suona`（唢呐）· `sheng`（笙）· `dagu`（大鼓）· `bianqing`（编磬）

### 生成工具（推荐，保证结构一致）

```bash
python scripts/make_style.py --genre "Chinese wuxia rock" --mood "mid-slow and restrained" \
  --bpm 96 --rhythm "half-time drums with a slow build" \
  --instruments "solo guqin and xun under distant war drums, crackling electric pipa, tolling bianzhong, low electric bass pulse" \
  --vocal "low male lead, hushed and close-mic, aged and story-worn" \
  --production "dry, roomy, unprocessed" --out <曲>_style.txt
```

### 自检

- [ ] 曲风在前 5 词内
- [ ] 有 BPM
- [ ] 乐器 3-6 件、含质感词（crackling/tolling/distant/solo）
- [ ] 人声 4 要素（性别/音域/音色/距离）
- [ ] 无 chant/choir/shout（除非需要合唱）
- [ ] 60-110 词
