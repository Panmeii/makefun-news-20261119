// Entry point for our make.fun "one image sums up the day's news" entry.
//
// What this program does, in order:
//   1. Copies the bundled entry.png into the output directory the grader
//      points us at (MAKEFUN_OUTPUT_DIR, falling back to /output).
//   2. Re-opens the copied file and proves it really is the image we mean
//      to submit: it checks the PNG magic bytes, reads the width and
//      height out of the IHDR chunk, and confirms the picture stays
//      inside the competition limits (at most 1024x1024 pixels and at
//      most 1 MiB on disk).
//   3. Prints one summary line describing the verified file. Any failed
//      check aborts with a non-zero exit code and a message on stderr,
//      so a broken entry can never slip through quietly.
//
// Only node: builtins are used, so plain `node main.ts` is enough.

import { copyFileSync, readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_WIDTH = 1024;
const MAX_HEIGHT = 1024;
const MAX_BYTES = 1024 * 1024; // 1 MiB, the competition's size cap.

// The eight bytes every PNG file starts with.
const PNG_MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

function fail(reason: string): never {
  console.error(`entry check failed: ${reason}`);
  process.exit(1);
}

const here = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(here, 'entry.png');
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const destPath = join(outDir, 'entry.png');

copyFileSync(sourcePath, destPath);

// --- Verification of the file we just placed -------------------------------

const bytes = readFileSync(destPath);
const sizeOnDisk = statSync(destPath).size;

if (bytes.length < PNG_MAGIC.length || PNG_MAGIC.some((b, i) => bytes[i] !== b)) {
  fail('copied file does not start with the PNG signature bytes');
}

// IHDR is the first chunk after the signature: 4 bytes of length, the four
// letters "IHDR", then width and height as big-endian uint32 values.
if (bytes.toString('ascii', 12, 16) !== 'IHDR') {
  fail('first PNG chunk is not IHDR, so dimensions cannot be trusted');
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);

// A complete PNG ends with the empty IEND chunk, whose name sits in the
// four bytes just before the final CRC. If it is not there, the file was
// truncated or otherwise cut short and must not be submitted.
if (bytes.toString('ascii', bytes.length - 8, bytes.length - 4) !== 'IEND') {
  fail('file does not end with the IEND chunk, so it is truncated or corrupt');
}

if (width > MAX_WIDTH || height > MAX_HEIGHT) {
  fail(`image is ${width}x${height}, over the ${MAX_WIDTH}x${MAX_HEIGHT} limit`);
}
if (sizeOnDisk > MAX_BYTES) {
  fail(`image is ${sizeOnDisk} bytes, over the ${MAX_BYTES}-byte limit`);
}

console.log(
  `entry.png verified: ${width}x${height} PNG, ${sizeOnDisk} bytes, copied to ${destPath}`,
);
