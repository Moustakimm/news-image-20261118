// news-image-20261118: the entry program (Node 22, standard library only).
// The image is drawn by src/render.py into entry.png; this program copies it
// to /output/entry.png, byte for byte, so both grading runs write the same file.
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const src = new URL('./entry.png', import.meta.url);
// The gate allows at most 1 MiB and 1024x1024 px; fail loudly instead of
// shipping an image the scorer would refuse.
if (statSync(src).size > 1048576) throw new Error('entry.png is over the 1 MiB gate');
copyFileSync(src, join(outDir, 'entry.png'));
