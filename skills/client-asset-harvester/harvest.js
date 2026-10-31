#!/usr/bin/env node
// asset harvester: crawl a site, download images, classify, write manifest + REVIEW.md.

import { chromium } from "playwright";
import sharp from "sharp";
import phash from "sharp-phash";
import pLimit from "p-limit";
import { Command } from "commander";
import { promises as fs } from "node:fs";
import { existsSync } from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { scoreLogo, founderHint } from "./classify.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const UA = "workspace-blueprint-asset-harvester/1.0";
const SCROLL_CYCLES = 4;
const SCROLL_DELAY_MS = 600;
const DOWNLOAD_CONCURRENCY = 6;

// ---------- CLI ----------
const program = new Command();
program
  .requiredOption("--url <url>", "the website URL to crawl")
  .option("--out <dir>", "folder the dated run folder is created in", "assets/scraped")
  .option("--depth <n>", "link depth from homepage", "2")
  .option("--max-pages <n>", "hard cap on pages crawled", "25")
  .option("--include-pdfs", "download linked PDFs alongside images", false)
  .option("--respect-robots <bool>", "respect robots.txt", "true")
  .option("--workspace <path>", "workspace root (defaults to CWD)", process.cwd());
program.parse(process.argv);
const opts = program.opts();

const respectRobots = String(opts.respectRobots).toLowerCase() !== "false";
const depthMax = parseInt(opts.depth, 10);
const pagesMax = parseInt(opts.maxPages, 10);

// ---------- Helpers ----------
const slug = (s) => s.replace(/^https?:\/\//, "").replace(/[^a-z0-9]+/gi, "-").replace(/(^-|-$)/g, "").toLowerCase().slice(0, 80) || "root";
const sha8 = (buf) => crypto.createHash("sha256").update(buf).digest("hex").slice(0, 8);

async function ensureDir(p) {
  await fs.mkdir(p, { recursive: true });
}

async function resolveOutputDir(workspace, outBase) {
  const today = new Date().toISOString().slice(0, 10);
  const base = path.join(path.resolve(workspace, outBase), today);
  let dir = base;
  let suffix = 0;
  while (existsSync(dir)) {
    suffix += 1;
    dir = `${base}-${suffix}`;
  }
  await ensureDir(path.join(dir, "logo-candidates"));
  await ensureDir(path.join(dir, "unsorted"));
  return dir;
}

async function fetchRobots(originUrl) {
  try {
    const u = new URL("/robots.txt", originUrl).toString();
    const res = await fetch(u, { headers: { "User-Agent": UA } });
    if (!res.ok) return null;
    return await res.text();
  } catch {
    return null;
  }
}

function isAllowedByRobots(robotsTxt, urlPath) {
  if (!robotsTxt) return true;
  const lines = robotsTxt.split("\n").map((l) => l.split("#")[0].trim());
  let applies = false;
  const disallows = [];
  for (const line of lines) {
    const m = line.match(/^User-agent:\s*(.+)$/i);
    if (m) {
      applies = m[1].trim() === "*" || /asset|harvester/i.test(m[1]);
      continue;
    }
    if (!applies) continue;
    const d = line.match(/^Disallow:\s*(.+)$/i);
    if (d) disallows.push(d[1].trim());
  }
  return !disallows.some((d) => d && urlPath.startsWith(d));
}

function pickLargestFromSrcset(srcset) {
  if (!srcset) return null;
  const candidates = srcset.split(",").map((s) => {
    const parts = s.trim().split(/\s+/);
    const url = parts[0];
    const wMatch = parts[1] && parts[1].match(/^(\d+)w$/);
    const w = wMatch ? parseInt(wMatch[1], 10) : 0;
    return { url, w };
  });
  candidates.sort((a, b) => b.w - a.w);
  return candidates[0]?.url || null;
}

// ---------- Page extraction ----------
async function extractFromPage(page) {
  const pageUrl = page.url();
  return await page.evaluate((pageUrl) => {
    const out = [];
    const seen = new Set();
    const add = (rec) => {
      if (!rec.sourceUrl) return;
      try {
        rec.sourceUrl = new URL(rec.sourceUrl, pageUrl).toString();
      } catch {
        return;
      }
      const k = rec.sourceUrl + "|" + (rec.from || "");
      if (seen.has(k)) return;
      seen.add(k);
      out.push(rec);
    };

    // <link rel="icon"> + apple-touch-icon
    document.querySelectorAll("link[rel]").forEach((el) => {
      const rel = (el.getAttribute("rel") || "").toLowerCase();
      const href = el.getAttribute("href");
      if (!href) return;
      if (rel.includes("apple-touch-icon")) add({ sourceUrl: href, from: "apple-touch-icon" });
      else if (rel.includes("icon")) add({ sourceUrl: href, from: "favicon" });
    });

    // og:image, twitter:image
    document.querySelectorAll("meta[property='og:image'], meta[name='og:image']").forEach((el) => {
      const c = el.getAttribute("content");
      if (c) add({ sourceUrl: c, from: "og-image" });
    });
    document.querySelectorAll("meta[name='twitter:image'], meta[property='twitter:image']").forEach((el) => {
      const c = el.getAttribute("content");
      if (c) add({ sourceUrl: c, from: "twitter-image" });
    });

    // schema.org Organization.logo
    document.querySelectorAll("script[type='application/ld+json']").forEach((el) => {
      try {
        const data = JSON.parse(el.textContent || "{}");
        const items = Array.isArray(data) ? data : [data];
        for (const item of items) {
          const arr = Array.isArray(item) ? item : [item];
          for (const node of arr) {
            const logo = node && (node.logo || (node["@graph"] && node["@graph"].find && node["@graph"].find((g) => g.logo)?.logo));
            if (typeof logo === "string") add({ sourceUrl: logo, from: "schema-org-logo" });
            else if (logo && typeof logo === "object" && logo.url) add({ sourceUrl: logo.url, from: "schema-org-logo" });
          }
        }
      } catch {}
    });

    // <img> with src + srcset
    document.querySelectorAll("img").forEach((el) => {
      const inHeader = !!el.closest("header");
      const inFooter = !!el.closest("footer");
      const from = inHeader ? "img-in-header" : inFooter ? "img-in-footer" : "img-body";
      const src = el.currentSrc || el.getAttribute("src");
      const srcset = el.getAttribute("srcset");
      const meta = {
        altText: el.getAttribute("alt") || "",
        className: el.getAttribute("class") || "",
        id: el.getAttribute("id") || "",
      };
      if (src) add({ sourceUrl: src, from, ...meta });
      if (srcset) {
        // Defer largest-pick to JS side
        add({ sourceUrl: srcset, from: from + "-srcset", ...meta, _srcset: true });
      }
    });

    // <picture><source srcset>
    document.querySelectorAll("picture source[srcset]").forEach((el) => {
      const srcset = el.getAttribute("srcset");
      const inHeader = !!el.closest("header");
      const from = inHeader ? "img-in-header-srcset" : "picture-source-srcset";
      if (srcset) add({ sourceUrl: srcset, from, _srcset: true });
    });

    // CSS background-image: scan computed styles of every element
    const all = document.querySelectorAll("*");
    for (const el of all) {
      const bg = window.getComputedStyle(el).backgroundImage;
      if (!bg || bg === "none") continue;
      const matches = bg.match(/url\(["']?([^"')]+)["']?\)/g) || [];
      for (const m of matches) {
        const u = m.match(/url\(["']?([^"')]+)["']?\)/)?.[1];
        if (!u) continue;
        if (u.startsWith("data:")) continue;
        const inHeader = !!el.closest("header");
        add({ sourceUrl: u, from: inHeader ? "css-bg-header" : "css-bg" });
      }
    }

    // Internal links
    const links = [];
    document.querySelectorAll("a[href]").forEach((el) => {
      const href = el.getAttribute("href");
      if (!href) return;
      if (href.startsWith("#") || href.startsWith("mailto:") || href.startsWith("tel:") || href.startsWith("javascript:")) return;
      try {
        const abs = new URL(href, pageUrl).toString().split("#")[0];
        links.push(abs);
      } catch {}
    });

    return { refs: out, links: Array.from(new Set(links)) };
  }, pageUrl);
}

// Resolve _srcset records into the largest URL
function resolveSrcsets(refs) {
  return refs.flatMap((r) => {
    if (r._srcset) {
      const largest = pickLargestFromSrcset(r.sourceUrl);
      if (!largest) return [];
      return [{ ...r, sourceUrl: largest, from: r.from.replace(/-srcset$/, ""), _srcset: undefined }];
    }
    return [r];
  });
}

// ---------- Crawl ----------
async function crawl(startUrl) {
  const origin = new URL(startUrl).origin;
  const robots = respectRobots ? await fetchRobots(startUrl) : null;
  if (respectRobots && robots && !isAllowedByRobots(robots, new URL(startUrl).pathname)) {
    throw new Error("robots.txt disallows the start URL. Re-run with --respect-robots false if you have authorization.");
  }

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ userAgent: UA, viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();

  const queue = [{ url: startUrl, depth: 0 }];
  const visited = new Set();
  const blocked = [];
  const refsAll = []; // {pageUrl, ref}

  while (queue.length && visited.size < pagesMax) {
    const { url, depth } = queue.shift();
    if (visited.has(url)) continue;
    if (new URL(url).origin !== origin) continue;
    if (respectRobots && robots && !isAllowedByRobots(robots, new URL(url).pathname)) continue;

    visited.add(url);
    try {
      // SPA site builders (Wix, Squarespace) never reach "networkidle": they
      // keep long-poll/analytics sockets open: so nav would time out on a fully
      // working page. Wait for DOM, then let client-side render + lazy images settle.
      const resp = await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 }).catch(() => null);
      if (!resp || !resp.ok()) {
        blocked.push({ url, reason: resp ? `HTTP ${resp.status()}` : "navigation failed" });
        continue;
      }
      await page.waitForLoadState("load", { timeout: 15000 }).catch(() => {});
      await page.waitForTimeout(1500);
      const title = await page.title();
      if (/Just a moment|Attention Required|Access denied/i.test(title)) {
        blocked.push({ url, reason: "Cloudflare or bot challenge" });
        continue;
      }

      // Trigger lazy-load
      for (let i = 0; i < SCROLL_CYCLES; i++) {
        await page.evaluate(() => window.scrollBy(0, document.documentElement.scrollHeight / 4));
        await page.waitForTimeout(SCROLL_DELAY_MS);
      }

      const { refs, links } = await extractFromPage(page);
      const resolved = resolveSrcsets(refs);
      for (const r of resolved) refsAll.push({ pageUrl: url, ref: r });

      if (depth < depthMax) {
        for (const link of links) {
          if (!visited.has(link) && new URL(link).origin === origin) {
            queue.push({ url: link, depth: depth + 1 });
          }
        }
      }
    } catch (err) {
      blocked.push({ url, reason: err.message });
    }
  }

  await browser.close();
  return { visited: Array.from(visited), blocked, refsAll };
}

// ---------- Download + analyze ----------
async function downloadAndAnalyze(refsAll, outDir) {
  const limit = pLimit(DOWNLOAD_CONCURRENCY);

  // Group by source URL to count multi-page appearances + collect all "from" signals
  const byUrl = new Map();
  for (const { pageUrl, ref } of refsAll) {
    const key = ref.sourceUrl;
    if (!byUrl.has(key)) byUrl.set(key, { ref: { ...ref }, pages: new Set(), froms: new Set() });
    const rec = byUrl.get(key);
    rec.pages.add(pageUrl);
    rec.froms.add(ref.from);
    // Preserve richest discovery metadata
    rec.ref.altText = rec.ref.altText || ref.altText;
    rec.ref.className = rec.ref.className || ref.className;
    rec.ref.id = rec.ref.id || ref.id;
  }

  const downloaded = [];
  await Promise.all(
    Array.from(byUrl.entries()).map(([url, rec]) =>
      limit(async () => {
        try {
          const referer = Array.from(rec.pages)[0];
          const res = await fetch(url, { headers: { "User-Agent": UA, Referer: referer } });
          if (!res.ok) return;
          const ct = res.headers.get("content-type") || "";
          if (!/^image|svg/i.test(ct) && !/\.(svg|ico|png|jpe?g|webp|gif|avif)(\?|$)/i.test(url)) return;
          const buf = Buffer.from(await res.arrayBuffer());
          if (buf.length < 200) return;

          // sharp analysis (skip favicons / ico: sharp doesn't support them well)
          let width = null, height = null, format = null, hasAlpha = false, dominant = null, ph = null;
          if (/\.svg(\?|$)/i.test(url) || /svg/i.test(ct)) {
            format = "svg";
          } else {
            try {
              const img = sharp(buf);
              const m = await img.metadata();
              width = m.width || null;
              height = m.height || null;
              format = m.format || null;
              hasAlpha = !!m.hasAlpha;
              const stats = await img.stats().catch(() => null);
              if (stats?.dominant) {
                const { r, g, b } = stats.dominant;
                dominant = `#${[r, g, b].map((v) => v.toString(16).padStart(2, "0")).join("")}`;
              }
              ph = await phash(buf).catch(() => null);
            } catch {
              // Format sharp can't read (ico, exotic). Keep the file but skip metadata.
              if (/\.ico(\?|$)/i.test(url)) format = "ico";
            }
          }

          downloaded.push({
            sourceUrl: url,
            buf,
            ref: rec.ref,
            pages: Array.from(rec.pages),
            froms: Array.from(rec.froms),
            meta: { width, height, format, hasAlpha, bytes: buf.length, dominant, phash: ph },
          });
        } catch {}
      })
    )
  );

  // Dedup by phash (fallback: sha8 of buffer)
  const seen = new Map();
  for (const d of downloaded) {
    const key = d.meta.phash || sha8(d.buf);
    if (!seen.has(key)) {
      seen.set(key, d);
    } else {
      // Keep the larger one
      const cur = seen.get(key);
      if (d.buf.length > cur.buf.length) seen.set(key, d);
      // Merge pages/froms
      const merged = seen.get(key);
      const allPages = new Set([...cur.pages, ...d.pages]);
      const allFroms = new Set([...cur.froms, ...d.froms]);
      merged.pages = Array.from(allPages);
      merged.froms = Array.from(allFroms);
    }
  }

  return Array.from(seen.values());
}

// ---------- Write outputs ----------
function extFromUrlOrFormat(url, format) {
  const fromUrl = url.match(/\.([a-z0-9]{2,5})(\?|$)/i)?.[1]?.toLowerCase();
  return fromUrl || format || "bin";
}

async function writeOutputs(assets, outDir, ctx) {
  const manifest = {
    run_date: new Date().toISOString().slice(0, 10),
    source_url: ctx.startUrl,
    out: ctx.out,
    pages_crawled: ctx.visited.length,
    images_unique: assets.length,
    images_total_refs: ctx.totalRefs,
    blocked_pages: ctx.blocked,
    assets: [],
  };

  // Score everything first to rank logo candidates
  const enriched = assets.map((a) => {
    // Pick the strongest "from" for logo scoring
    const fromPriority = ["schema-org-logo", "apple-touch-icon", "favicon", "og-image", "twitter-image", "img-in-header", "css-bg-header", "img-in-footer", "img-body", "css-bg", "picture-source"];
    const bestFrom = fromPriority.find((f) => a.froms.includes(f)) || a.froms[0];
    const discovery = {
      from: bestFrom,
      altText: a.ref.altText || "",
      className: a.ref.className || "",
      id: a.ref.id || "",
      sourceUrl: a.sourceUrl,
    };
    const { score, signals } = scoreLogo({ discovery, meta: a.meta });
    const isFounder = founderHint({
      pagesAppearedOn: a.pages.length,
      meta: a.meta,
      altText: a.ref.altText || "",
    });
    return { ...a, logoScore: score, logoSignals: signals, founderHint: isFounder, bestFrom };
  });

  // Sort by logo score desc to rank logo-candidates
  const logoCandidates = enriched.filter((a) => a.logoScore >= 60).sort((a, b) => b.logoScore - a.logoScore);
  const rest = enriched.filter((a) => a.logoScore < 60);

  // Write files
  let logoIdx = 1;
  for (const a of logoCandidates) {
    const ext = extFromUrlOrFormat(a.sourceUrl, a.meta.format);
    const name = `${String(logoIdx).padStart(2, "0")}-${slug(a.bestFrom)}-${sha8(a.buf)}.${ext}`;
    const rel = path.join("logo-candidates", name);
    await fs.writeFile(path.join(outDir, rel), a.buf);
    manifest.assets.push(buildManifestEntry(a, rel));
    logoIdx += 1;
  }
  for (const a of rest) {
    const ext = extFromUrlOrFormat(a.sourceUrl, a.meta.format);
    const pageSlug = slug(a.pages[0] || "unknown");
    const name = `${pageSlug}-${sha8(a.buf)}.${ext}`;
    const rel = path.join("unsorted", name);
    await fs.writeFile(path.join(outDir, rel), a.buf);
    manifest.assets.push(buildManifestEntry(a, rel));
  }

  await fs.writeFile(path.join(outDir, "manifest.json"), JSON.stringify(manifest, null, 2));
  await fs.writeFile(path.join(outDir, "REVIEW.md"), buildReview(manifest, logoCandidates, enriched));
}

function buildManifestEntry(a, localPath) {
  return {
    id: sha8(a.buf),
    local_path: localPath.replace(/\\/g, "/"),
    source_url: a.sourceUrl,
    first_found_on: a.pages[0],
    all_pages: a.pages,
    alt_text: a.ref.altText || "",
    width: a.meta.width,
    height: a.meta.height,
    format: a.meta.format,
    bytes: a.meta.bytes,
    dominant_color: a.meta.dominant,
    phash: a.meta.phash || null,
    logo_score: a.logoScore,
    logo_signals: a.logoSignals,
    founder_hint: a.founderHint,
    license_caveat: "may be licensed stock from prior build: verify rights before reuse",
  };
}

function buildReview(manifest, logos, enriched) {
  const founderHints = enriched.filter((a) => a.founderHint);
  const lines = [];
  lines.push(`# Asset harvest review: ${manifest.source_url} (${manifest.run_date})\n`);
  lines.push(`Source: ${manifest.source_url}`);
  lines.push(`Pages crawled: ${manifest.pages_crawled}`);
  lines.push(`Unique images: ${manifest.images_unique}`);
  lines.push(`Total image references: ${manifest.images_total_refs}\n`);

  lines.push(`## Logo candidates (ranked)`);
  if (!logos.length) lines.push(`_(none scored ≥60: check unsorted/ manually)_`);
  logos.slice(0, 10).forEach((a, i) => {
    lines.push(`${i + 1}. \`${a._writtenPath || "logo-candidates/" + sha8(a.buf)}\`: score ${a.logoScore}: ${a.logoSignals.join(", ")}`);
  });
  lines.push("");

  lines.push(`## Likely founder / proof photos (appeared on ≥3 pages, portrait aspect)`);
  if (!founderHints.length) lines.push(`_(none detected)_`);
  founderHints.slice(0, 15).forEach((a) => {
    lines.push(`- \`unsorted/${slug(a.pages[0])}-${sha8(a.buf)}\`: found on ${a.pages.length} pages: alt: "${(a.ref.altText || "").slice(0, 60)}"`);
  });
  lines.push("");

  lines.push(`## Pages blocked (Cloudflare / login / 5xx / nav failure)`);
  if (!manifest.blocked_pages.length) lines.push(`_(none)_`);
  manifest.blocked_pages.forEach((p) => lines.push(`- ${p.url}: ${p.reason}`));
  lines.push("");

  lines.push(`## License caveats`);
  lines.push(`Some images may be licensed stock from whoever built this site. That license does not transfer to you. Check the rights before reusing any image that is not clearly the site owner's own photo.`);

  lines.push(`## Next step`);
  lines.push(`When you plan images for a new page, read manifest.json first: reuse real photos of people, places and proof where you have them, and fill only the gaps with stock or generated images.`);
  return lines.join("\n") + "\n";
}

// ---------- Main ----------
async function main() {
  // Pre-flight check on Chromium
  try {
    await chromium.executablePath();
  } catch {
    console.error("Chromium not installed. Run: npx playwright install chromium");
    process.exit(1);
  }

  const outDir = await resolveOutputDir(opts.workspace, opts.out);
  console.log(`[harvest] output dir: ${outDir}`);
  console.log(`[harvest] crawling ${opts.url} (depth=${depthMax}, max-pages=${pagesMax}, respect-robots=${respectRobots})...`);

  const { visited, blocked, refsAll } = await crawl(opts.url);
  console.log(`[harvest] crawled ${visited.length} pages, ${refsAll.length} image refs, ${blocked.length} blocked.`);

  const assets = await downloadAndAnalyze(refsAll, outDir);
  console.log(`[harvest] downloaded ${assets.length} unique images.`);

  await writeOutputs(assets, outDir, {
    startUrl: opts.url,
    out: opts.out,
    visited,
    blocked,
    totalRefs: refsAll.length,
  });

  const reviewPath = path.join(outDir, "REVIEW.md");
  console.log(`[harvest] done. Review: ${reviewPath}`);
}

main().catch((err) => {
  console.error("[harvest] error:", err.message);
  process.exit(1);
});
