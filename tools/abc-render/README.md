# abc-render — ABC 曲谱渲染工具（一页曲谱）

把 YuE2 生成的 `*.abc` 乐谱渲染成浏览器可看/可播/可打印的 HTML 一页曲谱。基于 **abcjs v6**（纯 JS 渲染器）。

## 用法

- **双击 `abc_to_html.bat`**：扫描 bat 所在目录全部 `*.abc`，逐个生成同名 `.html`（不覆盖源文件）
- **拖放**：把文件夹或 abc 文件拖到 bat 上 → 扫描/处理拖入对象
- 依赖同目录 `render_sheet.mjs` + `template.html` + `node_modules/abcjs`（已装，node v18+）
- 输出：`xxx.abc → xxx.html`，abcjs 库自动复制到输出目录；浏览器打开即渲染

## 曲谱生成原理

详见 **`docs/曲谱生成原理.md`**（独立文档：ABC 解析 → 排版 → SVG 渲染 → MIDI/WebAudio 播放与高亮的完整原理）。

## 页面按钮

- ⟳ 重绘 / ▶ 播放曲谱 / ⏹ 停止 / 🖨 打印(存 PDF)；SynthController 自带进度条/播放控制条
- 播放时当前音符橙色高亮（`.abcjs-note.playing`）

## 故障排查

- **页面空白**：Ctrl+F5 强刷；确认 `abcjs-basic.js` 与 html 同目录
- **播放无声/慢**：音色库默认走网络（Web Audio + soundfont CDN），需联网；离线环境可后续内置音色包
- **打印多页**：浏览器打印对话框选 A4、边距窄、开"背景图形"

## 更新日志

- 2026-09-17 v3：播放改 **SynthController**，实现**播放音符高亮**（cursorControl.onEvent + CSS playing 类）
- 2026-09-17 v2：修复标题占位符漏替换；abcjs6 播放 API 迁移（`CreateSynth` 代替已移除的 `setUpAudio`）；修复 `renderAbc` 数组未取 `[0]` 导致的播放报错
- 2026-09-17 v1：初版（bat 批量转换 + HTML 模板）