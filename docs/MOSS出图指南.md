# MOSS-Image 出图指南（本机 ComfyUI · 1K 图）

> 2026-10-23 实测：1024×1024，**6-9 秒/张**（20-28 步），成图约 2.1MB。画质与 gpt-image2 接近（用户评价）。

## 一、环境（已就绪）

| 组件 | 路径 |
|---|---|
| ComfyUI | `H:\AI\ComfyUI_windows_portable\`（版本 0.42.0，已**原生支持** MOSS-Image） |
| 服务 | `http://127.0.0.1:8188`（未运行则先启动） |
| 扩散模型 | `ComfyUI\models\diffusion_models\moss_image_sft_int8_convrot.safetensors`（5.04GB，int8） |
| 文本编码器 | `ComfyUI\models\text_encoders\qwen3.5_9b_w4a8_gptq.safetensors`（6.84GB，**必须 9B**） |
| VAE | `ComfyUI\models\vae\flux2-vae.safetensors`（Flux2 latent，**不可换别的 VAE**） |

> MOSS-Image 在 ComfyUI 中的关键约束（源码 `comfy/supported_models.py: MOSSImage`）：
> - `latent_format = Flux2` → 必须用 flux2 系列 VAE
> - 文本编码器只接受 **Qwen3.5-9B**（4B/8B 都不行）
> - 内建 `shift = 5.0`（无需手调 ModelSamplingFlux）

## 二、节点连接（txt2img 最小工作流）

```
UNETLoader(moss_image_sft_int8_convrot)  →  KSampler.model
CLIPLoader(qwen3.5_9b_w4a8_gptq, type=moss_image)  →  CLIPTextEncode(正/负).clip
VAELoader(flux2-vae)  →  VAEDecode.vae
CLIPTextEncode(正)  →  KSampler.positive
CLIPTextEncode(负)  →  KSampler.negative
EmptyFlux2LatentImage(1024×1024)  →  KSampler.latent_image
KSampler  →  VAEDecode  →  SaveImage
```

**关键：CLIPLoader 的 `type` 必须选 `moss_image`**（下拉里有，选错会报编码器不匹配）。

## 三、脚本用法（推荐）

```bash
cd H:\Works\SoundGenPrj\scripts
H:\AI\ComfyUI_windows_portable\python_embeded\python.exe comfy_moss.py ^
  --prompt "Chinese historical rock album cover, bronze altar at dusk, banners, ink-wash texture, bronze gold and ink black, cinematic" ^
  --negative "text, watermark, logo, blurry, low quality" ^
  --steps 28 --cfg 4.5 --seed 7 ^
  --width 1024 --height 1024 ^
  --prefix album_cq --out "H:\Works\SoundGenPrj\tmp\cq_cover.png"
```

参数说明：

| 参数 | 默认 | 说明 |
|---|---|---|
| `--steps` | 28 | 20-30 足够；步数与耗时近似线性（20 步≈6s，28 步≈9s） |
| `--cfg` | 4.5 | 4.0-5.0 之间；越高越贴提示词，过高会偏硬、偏糊 |
| `--sampler` | euler | euler / dpmpp_2m 均可 |
| `--scheduler` | simple | simple / beta / kl_optimal |
| `--width/--height` | 1024 | 竖版 768×1024、横版 1024×768 也可；更大需测试显存 |
| `--out` | — | 指定则拷贝到该路径（并打印原始输出路径） |

## 四、实测数据（RTX 5090）

| 配置 | 耗时 | 产物 |
|---|---|---|
| 1024×1024 · 28 步 · cfg4.5 | **9 秒** | 2161 KB PNG |
| 1024×1024 · 20 步 · cfg4.0 | **6 秒** | 2187 KB PNG |

→ 单张 1K 图 10 秒内，**比 ignis（gpt-image，约 60-120 秒 + 限流）快一个量级**；本地免费、无限抽。

## 五、与现有两条封面通道的分工建议

| 通道 | 速度 | 质量 | 适用 |
|---|---|---|---|
| **MOSS（本机）** | 6-10 秒 | 接近 gpt-image2 | **批量试稿、快速迭代、多版本对比** |
| ignis（gpt-image） | 60-120 秒 + 限流 | 稳定 | 定稿、需要极稳的中文/文字排版时 |
| Agnes（agnes-image-2.5-flash） | 20-40 秒 | 好 | 抽 2 的免费补充 |

建议：**MOSS 做「试稿 3-5 版」→ 选中方向后再用 ignis/Agnes 出定稿**；或直接将 MOSS 纳入「2 抽制」作为第 3 抽（`_v3_moss`）。

## 六、常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| `CLIPLoader` 报编码器不匹配 | type 未选 `moss_image`，或用了 4B/8B | 改 type；换 `qwen3.5_9b_*` |
| VAE 解码出花屏/灰图 | 用了非 flux2 VAE | 换 `flux2-vae.safetensors` |
| 首张很慢（1-2 分钟） | 首次加载 5GB + 7GB 模型 | 属正常，之后 6-10 秒 |
| 显存不足 | 同时跑 YuE2 + MOSS | 先停 8090 的 yue-server 或降低分辨率 |
| 画面偏硬、细节糊 | cfg 过高 | 降到 4.0-4.5 |
| 中文文字乱码 | 模型对汉字支持有限 | 文字后期叠加，prompt 里不要写中文标题 |

## 七、本地二次开发提示

- ComfyUI 已内置 MOSS 专属节点：`MOSSImageLayoutPrompt`（布局/元素框）、`MOSSImageControl`（色彩图/深度图引导）、`TextEncodeMOSSImageEdit`（图生图/编辑）——需要「指定区域放指定元素」或「改图」时用它们；
- 布局节点需要配合 `Create Bounding Boxes` 产生的 element 数组，属进阶用法，普通封面不需要。
