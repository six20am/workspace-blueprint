#!/usr/bin/env node
/**
 * tools/motion/render.mjs: render one template to a video or a still.
 *
 *   node tools/motion/render.mjs --composition <name> --props <file.json> --out <file>
 *        [--aspect 16:9|9:16|1:1] [--scale 0.5] [--frames 0-59]
 *
 * --out ending in .mp4 (or .webm, .mov, .gif) renders a video; ending in .png,
 * .jpg or .webp renders one still (the last frame, where the motion has settled,
 * unless the props set "frame"). --scale shrinks the frame for a quick test.
 * --frames renders only part of the timeline.
 *
 * The props file is JSON. Any string in it that names a file on this computer
 * (relative to the props file, or a full path) is copied into a staging folder
 * so the template can read it; the original is never touched. Everything the
 * script needs is found from its own folder, so it runs from anywhere.
 *
 * Renders on this computer with headless Chrome (downloaded by npm install).
 * No account, no key, nothing uploaded.
 */

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const ENTRY = path.join(ROOT, "src", "index.ts");
const TEMPLATES = [
  "AspectVariant", "BeforeAfter", "BrandedClip", "CaptionBurn", "CoverFrame",
  "DataVideo", "ImagePost", "KenBurns", "Slideshow", "TalkingCards",
];
const ASPECTS = ["16:9", "9:16", "1:1", "4:5", "5:4", "4:3", "3:4"];
const MEDIA = /\.(png|jpe?g|webp|gif|avif|bmp|svg|mp4|mov|webm|m4v|mkv|mp3|wav|m4a|aac|ogg|flac|ttf|otf|woff2?)$/i;
const STILL = /\.(png|jpe?g|webp)$/i;

const die = (msg, code = 1) => {
  console.error(`Error: ${msg}`);
  process.exit(code);
};

const parseArgs = (argv) => {
  const flags = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) die(`unexpected argument: ${a}`);
    const key = a.slice(2);
    const next = argv[i + 1];
    if (next === undefined || next.startsWith("--")) flags[key] = true;
    else {
      flags[key] = next;
      i++;
    }
  }
  return flags;
};

/** Copy every local file the props name into the staging folder; swap in the staged name. */
const stageFiles = (value, propsDir, publicDir, counter) => {
  if (typeof value === "string") {
    if (!MEDIA.test(value) || /^(https?:|data:)/i.test(value)) return value;
    const abs = path.isAbsolute(value) ? value : path.resolve(propsDir, value);
    if (!fs.existsSync(abs)) die(`file named in the props not found: ${value} (looked at ${abs})`);
    const name = `in-${counter.n++}${path.extname(abs).toLowerCase()}`;
    fs.copyFileSync(abs, path.join(publicDir, name));
    return name;
  }
  if (Array.isArray(value)) return value.map((v) => stageFiles(v, propsDir, publicDir, counter));
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, stageFiles(v, propsDir, publicDir, counter)]));
  }
  return value;
};

const main = async () => {
  const flags = parseArgs(process.argv.slice(2));
  if (flags.help || flags.h) {
    console.log(`Usage: node render.mjs --composition <name> --props <file.json> --out <file> [--aspect 16:9|9:16|1:1] [--scale 0.5] [--frames 0-59]\nTemplates: ${TEMPLATES.join(", ")}`);
    return;
  }
  const id = flags.composition;
  if (!id || !TEMPLATES.includes(id)) die(`--composition must be one of: ${TEMPLATES.join(", ")}`);
  if (!flags.props || flags.props === true) die("--props <file.json> is required");
  if (!flags.out || flags.out === true) die("--out <file> is required");
  if (flags.aspect && !ASPECTS.includes(flags.aspect)) die(`--aspect must be one of: ${ASPECTS.join(", ")}`);

  if (!fs.existsSync(path.join(ROOT, "node_modules", "remotion"))) {
    die("Remotion is not installed. Run `npm install` in tools/motion (several hundred MB), or run doctor.", 2);
  }
  const require = createRequire(path.join(ROOT, "package.json"));
  const { bundle } = require("@remotion/bundler");
  const { renderMedia, renderStill, selectComposition, ensureBrowser } = require("@remotion/renderer");

  const propsPath = path.resolve(flags.props);
  if (!fs.existsSync(propsPath)) die(`props file not found: ${propsPath}`);
  let props;
  try {
    props = JSON.parse(fs.readFileSync(propsPath, "utf8"));
  } catch (err) {
    die(`props file is not valid JSON: ${err.message}`);
  }
  const out = path.resolve(flags.out);
  if (fs.existsSync(out)) die(`out file already exists, pick another name: ${out}`);
  fs.mkdirSync(path.dirname(out), { recursive: true });

  const stagingRoot = path.join(ROOT, ".remotion");
  fs.mkdirSync(stagingRoot, { recursive: true });
  const publicDir = fs.mkdtempSync(path.join(stagingRoot, "public-"));
  try {
    const inputProps = stageFiles(props, path.dirname(propsPath), publicDir, { n: 0 });
    if (flags.aspect) inputProps.aspect = flags.aspect;

    await ensureBrowser();
    console.log(`Bundling templates...`);
    const serveUrl = await bundle({ entryPoint: ENTRY, publicDir, rootDir: ROOT });
    const composition = await selectComposition({ serveUrl, id, inputProps });
    const scale = flags.scale ? Number(flags.scale) : 1;
    if (!(scale > 0 && scale <= 4)) die("--scale must be a number above 0 and at most 4");

    if (STILL.test(out)) {
      const frame = Number.isInteger(inputProps.frame) ? inputProps.frame : composition.durationInFrames - 1;
      await renderStill({ composition, serveUrl, inputProps, output: out, frame, scale });
    } else {
      const ext = path.extname(out).toLowerCase();
      const codec = ext === ".webm" ? "vp8" : ext === ".gif" ? "gif" : ext === ".mov" ? "prores" : "h264";
      let frameRange = null;
      if (typeof flags.frames === "string") {
        const m = flags.frames.match(/^(\d+)-(\d+)$/);
        if (!m) die("--frames must look like 0-59");
        frameRange = [Number(m[1]), Math.min(Number(m[2]), composition.durationInFrames - 1)];
      }
      let last = -1;
      await renderMedia({
        composition,
        serveUrl,
        inputProps,
        codec,
        outputLocation: out,
        scale,
        frameRange,
        onProgress: ({ progress }) => {
          const pct = Math.floor(progress * 10) * 10;
          if (pct !== last) {
            last = pct;
            console.log(`Rendering ${pct}%`);
          }
        },
      });
    }
    const { width, height, durationInFrames, fps } = composition;
    const length = STILL.test(out) ? "still" : `${(durationInFrames / fps).toFixed(1)} s`;
    console.log(`Done: ${out} (${Math.round(width * scale)}x${Math.round(height * scale)}, ${length}, ${fs.statSync(out).size} bytes)`);
  } finally {
    fs.rmSync(publicDir, { recursive: true, force: true });
  }
};

main().catch((err) => die(err?.stack || String(err)));
