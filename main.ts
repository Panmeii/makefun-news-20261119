// Entry program for the make.fun news-image-20261119 competition
// ("Sum up 19 November's world news in one image").
//
// The picture itself sits next to this file as entry.png — a dense
// front page of forty stories from Thursday 19 November 2026, drawn by
// build_image.py. This program's job is to deliver those exact bytes
// to the grader's output folder and to prove, before it exits, that
// what landed there is a complete, well-formed PNG inside every limit
// the competition sets:
//
//   1. Resolve the output folder: $MAKEFUN_OUTPUT_DIR when the caller
//      sets it, otherwise /output. Create it if it does not exist.
//   2. Copy entry.png into it.
//   3. Walk the copied file chunk by chunk the way the PNG spec lays
//      it out — signature, then a sequence of length/type/data/CRC
//      chunks — and recompute every chunk's CRC-32 to make sure no
//      byte was flipped or lost on the way. The walk must end exactly
//      at the end of the file, on an IEND chunk, having seen an IHDR
//      first and at least one IDAT.
//   4. Check the IHDR dimensions (each at most 1024) and the total
//      byte count (at most 1 MiB).
//
// Any failed check prints the reason to stderr and exits 1, so a
// damaged file fails loudly here rather than scoring zero later.
// Node 22 standard library only; run with `node main.ts`.

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const EDGE_LIMIT = 1024;
const BYTE_LIMIT = 1024 * 1024; // 1 MiB
const SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function abort(reason: string): never {
  console.error(`entry verification failed: ${reason}`);
  process.exit(1);
}

// --- CRC-32 (the PNG chunk checksum, polynomial 0xEDB88320) --------------
const crcTable: number[] = [];
for (let n = 0; n < 256; n += 1) {
  let c = n;
  for (let k = 0; k < 8; k += 1) {
    c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  }
  crcTable[n] = c >>> 0;
}

function crc32(buf: Buffer): number {
  let crc = 0xffffffff;
  for (const byte of buf) {
    crc = crcTable[(crc ^ byte) & 0xff] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

// --- Deliver the image ----------------------------------------------------
const folder = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(join(folder, "entry.png"), target);

// --- Verify what we delivered ---------------------------------------------
const png = readFileSync(target);

if (png.length > BYTE_LIMIT) {
  abort(`file is ${png.length} bytes, over the ${BYTE_LIMIT}-byte cap`);
}
if (png.length < 8 + 25 + 12) {
  abort("file is too short to hold a signature, an IHDR and an IEND");
}
if (!png.subarray(0, 8).equals(SIGNATURE)) {
  abort("first eight bytes are not the PNG signature");
}

let offset = 8;
let width = 0;
let height = 0;
let sawIdat = false;
let sawIend = false;
let chunkIndex = 0;

while (offset < png.length) {
  if (offset + 12 > png.length) {
    abort(`chunk ${chunkIndex} is cut short at byte ${offset}`);
  }
  const length = png.readUInt32BE(offset);
  const type = png.toString("ascii", offset + 4, offset + 8);
  const dataStart = offset + 8;
  const dataEnd = dataStart + length;
  if (dataEnd + 4 > png.length) {
    abort(`chunk ${type} claims ${length} data bytes and overruns the file`);
  }
  const storedCrc = png.readUInt32BE(dataEnd);
  const actualCrc = crc32(png.subarray(offset + 4, dataEnd));
  if (storedCrc !== actualCrc) {
    abort(`chunk ${type} fails its CRC-32 check`);
  }
  if (chunkIndex === 0) {
    if (type !== "IHDR" || length !== 13) {
      abort(`first chunk is ${type} (${length} bytes), not a 13-byte IHDR`);
    }
    width = png.readUInt32BE(dataStart);
    height = png.readUInt32BE(dataStart + 4);
  }
  if (type === "IDAT") sawIdat = true;
  if (type === "IEND") {
    sawIend = true;
    offset = dataEnd + 4;
    break;
  }
  offset = dataEnd + 4;
  chunkIndex += 1;
}

if (!sawIdat) abort("no IDAT chunk found, so the file carries no image data");
if (!sawIend) abort("no IEND chunk found, so the file is truncated");
if (offset !== png.length) {
  abort(`${png.length - offset} stray bytes follow the IEND chunk`);
}
if (width < 1 || height < 1 || width > EDGE_LIMIT || height > EDGE_LIMIT) {
  abort(`dimensions ${width}x${height} fall outside 1..${EDGE_LIMIT} per side`);
}

console.log(
  `entry.png delivered and verified: ${width}x${height} PNG, ` +
    `${png.length} bytes, ${chunkIndex + 1} chunks, all CRC-32 checks passed -> ${target}`,
);
