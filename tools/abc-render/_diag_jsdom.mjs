import fs from "node:fs";
import { JSDOM } from "jsdom";
const abcjs = fs.readFileSync("H:/Works/SoundGenPrj/tools/abc-render/node_modules/abcjs/dist/abcjs-basic.js", "utf-8");
const abc = fs.readFileSync("H:/AI/YuE/skills/yue2-music/outputs/iron_v1/score.abc", "utf-8");
const dom = new JSDOM("<!DOCTYPE html><body><div id=\"score\"></div></body>", { pretendToBeVisual: true });
const w = dom.window;
try {
  w.eval(abcjs);
  const ABCJS = w.ABCJS;
  const visual = ABCJS.renderAbc("score", abc, { add_classes: true, print: true, scale: 0.95 });
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
    firstNoteClasses: notes.slice(0, 20).map(e => e.getAttribute("class")),
    lines: t.lines.map(ln => ({
      absElems: ln.absoluteElement ? ln.absoluteElement.elems.length : -1,
      hasStaff: !!ln.staff,
      musicNotes: ln.staff ? ln.staff.musicNotes.length : -1
    }))
  };
  console.log(JSON.stringify(out, null, 1));
} catch (e) {
  console.log("ERR: " + (e && (e.stack || e.message) || e));
}
