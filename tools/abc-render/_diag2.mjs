import fs from "node:fs";
import { JSDOM } from "jsdom";
const abcjs = fs.readFileSync("H:/Works/SoundGenPrj/tools/abc-render/node_modules/abcjs/dist/abcjs-basic.js", "utf-8");
const abc = fs.readFileSync("H:/AI/YuE/skills/yue2-music/outputs/iron_v1/score.abc", "utf-8");
const dom = new JSDOM("<!DOCTYPE html><body><div id=\"score\"></div></body>", { pretendToBeVisual: true });
const w = dom.window;
const run = new w.Function(abcjs + "\n; return (typeof ABCJS !== \"undefined\") ? {ABCJS, hasRender: typeof ABCJS.renderAbc, keys: Object.keys(ABCJS)} : {no: \"ABCJS undefined\"};");
const res = run.call(w);
console.log("probe:", JSON.stringify(res).slice(0, 700));
if (res.ABCJS && res.hasRender === "function") {
  try {
    const visual = res.ABCJS.renderAbc("score", abc, { add_classes: true });
    const t = visual[0];
    const allSvg = Array.prototype.slice.call(w.document.querySelectorAll("#score svg"));
    const classSet = {};
    allSvg.forEach(s => Array.prototype.forEach.call(s.querySelectorAll("*"), e => (e.getAttribute("class")||"").split(/\s+/).forEach(c => { if (c) classSet[c] = (classSet[c]||0)+1; })));
    const notes = Array.prototype.slice.call(w.document.querySelectorAll("#score .abcjs-note"));
    const out = {
      svgCount: allSvg.length,
      totalNotes: notes.length,
      svgNotesPer: allSvg.map(s => s.querySelectorAll(".abcjs-note").length),
      classCounts: classSet,
      firstNoteClasses: notes.slice(0, 24).map(e => e.getAttribute("class")),
      lines: t.lines.map(ln => ({ absElems: ln.absoluteElement ? ln.absoluteElement.elems.length : -1, hasStaff: !!ln.staff, musicNotes: ln.staff ? ln.staff.musicNotes.length : -1 }))
    };
    console.log("DIAG:" + JSON.stringify(out));
  } catch (e) {
    console.log("RENDER ERR: " + (e && (e.stack || e.message) || e));
  }
} else {
  console.log("ABCJS not usable, trying window eval assignment...");
  w.eval("var __abcjs = (function(){" + abcjs + "\n; return ABCJS; })();");
  console.log("window.__abcjs:", typeof w.__abcjs, w.__abcjs ? Object.keys(w.__abcjs).slice(0, 20).join(",") : "-");
}
