// Copies the pre-rendered news page (entry.png, drawn by render.py) to the output
// directory after checking the contest limits. Node 22, standard library only.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const png = readFileSync(join(here, "entry.png"));

const SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!png.subarray(0, 8).equals(SIG)) throw new Error("entry.png is not a PNG");
if (png.length > 1048576) throw new Error(`entry.png is ${png.length} bytes, over 1 MiB`);
const width = png.readUInt32BE(16);
const height = png.readUInt32BE(20);
if (width > 1024 || height > 1024) throw new Error(`entry.png is ${width}x${height}, over 1024`);
if (png.subarray(png.length - 8, png.length - 4).toString("latin1") !== "IEND") {
  throw new Error("entry.png does not end with an IEND chunk");
}

mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, "entry.png"), png);
console.log(`wrote ${join(outDir, "entry.png")} (${width}x${height}, ${png.length} bytes)`);
