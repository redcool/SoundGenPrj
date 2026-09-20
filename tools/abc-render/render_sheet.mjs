import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const [, , abcPath, outHtml, title = "ABC 曲谱"] = process.argv;
let abc = fs.readFileSync(abcPath, "utf-8");
// 萨克斯音色：第 4 个位置参数为 "sax" 时，为 Ins 声部注入 %%MIDI program 66（次中音萨克斯），
// Vocal 声部保持默认钢琴（program 0）。只注入 K: 行之后的声部段。
const wantSax = process.argv.includes("sax");
if (wantSax) {
  const abcLines = abc.split("\n");
  let kIdx = abcLines.findIndex((l) => l.startsWith("K:"));
  if (kIdx < 0) kIdx = 0;
  const outLines = [];
  let prevProgram = 0;
  for (let i = 0; i < abcLines.length; i++) {
    const l = abcLines[i];
    if (i > kIdx) {
      if (l.trim() === "V: Vocal" && prevProgram !== 0) { outLines.push("%%MIDI program 0"); prevProgram = 0; }
      if (l.trim() === "V: Ins" && prevProgram !== 66) { outLines.push("%%MIDI program 66"); prevProgram = 66; }
    }
    outLines.push(l);
  }
  abc = outLines.join("\n");
}
// 标准谱：自动开启小节编号显示（%%barNumbers 1 = 每小节标号；不改动源谱内容）
if (!abc.includes("%%barNumbers")) {
  const k = abc.indexOf("K:");
  if (k >= 0) {
    const nl = abc.indexOf("\n", k);
    abc = abc.slice(0, nl + 1) + "%%barNumbers 1\n" + abc.slice(nl + 1);
  } else {
    abc = "%%barNumbers 1\n" + abc;
  }
}
const tpl = fs.readFileSync(path.join(here, "template.html"), "utf-8");
const outDir = path.dirname(path.resolve(outHtml));
fs.mkdirSync(outDir, { recursive: true });
fs.copyFileSync(path.join(here, "node_modules", "abcjs", "dist", "abcjs-basic.js"), path.join(outDir, "abcjs-basic.js"));
fs.copyFileSync(path.join(here, "node_modules", "abcjs", "abcjs-audio.css"), path.join(outDir, "abcjs-audio.css"));
const abcJson = JSON.stringify(abc).replace(/</g, "\\u003c");
let html = tpl
  .replace("%%TITLE%%", String(title).replace(/&/g, "&amp;").replace(/</g, "&lt;"))
  .replace("%%ABC%%", abcJson);
fs.writeFileSync(outHtml, html, "utf-8");
console.log("OK:", outHtml);
