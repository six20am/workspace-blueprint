#!/usr/bin/env node
/**
 * loc-dl: download digitized items from the Library of Congress.
 *
 * Scope: loc.gov collections and searches. Public JSON API (`?fo=json`), no key,
 * no login. Zero dependencies, Node 18+ (uses global fetch).
 *
 * It downloads bytes AND records rights per item. The rights record is the point:
 * LoC digitizes material it does not own the rights to, so "it came from loc.gov"
 * is not a licence. Every item lands with its rights statement verbatim and
 * `rights_reviewed: false` until a human clears it.
 *
 * Conventions:
 *   - `--out <dir>` is required; the tool never guesses where files belong
 *   - output is `<out>/<YYYY-MM-DD>/` with `manifest.json` + `REVIEW.md`
 *   - `--simulate` previews without downloading
 *
 * See README.md.
 */

import { mkdir, writeFile, readFile, stat } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { resolve, join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const UA = 'workspace-blueprint-loc-dl/1.0 (library-of-congress bulk download tool)';

// LoC asks for considerate crawling and returns 429 when you are not. 1.2s
// between requests is deliberately slower than they require: a bulk pull is
// never the urgent path, and a throttled run that finishes beats a fast one
// that gets your IP blocked.
const DEFAULT_THROTTLE_MS = 1200;
const MAX_RETRIES = 4;

/* ------------------------------------------------------------------ args */

function parseArgs(argv) {
  const a = {
    url: null, out: null, simulate: false,
    max: 25, type: 'any', minWidth: 0, throttle: DEFAULT_THROTTLE_MS,
    query: null, listCollections: false, perPage: 25,
  };
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    const next = () => argv[++i];
    switch (t) {
      case '--out':         a.out = next(); break;
      case '--simulate':    a.simulate = true; break;
      case '--max':         a.max = parseInt(next(), 10); break;
      case '--type':        a.type = next(); break;
      case '--min-width':   a.minWidth = parseInt(next(), 10); break;
      case '--throttle':    a.throttle = parseInt(next(), 10); break;
      case '--query': case '-q': a.query = next(); break;
      case '--collections': a.listCollections = true; break;
      case '-h': case '--help': a.help = true; break;
      default:
        if (t.startsWith('-')) die(`Unknown flag: ${t}`);
        rest.push(t);
    }
  }
  if (rest.length) a.url = rest[0];
  return a;
}

function die(msg) {
  console.error(`\n  ✗ ${msg}\n`);
  process.exit(1);
}

const USAGE = `
loc-dl: download digitized items from the Library of Congress

  node tools/loc-dl/loc-dl.mjs <loc-url> --out <dir> [options]

Options
  --out <dir>        Output folder. A dated subfolder is created inside it. Required.
  --simulate         Fetch metadata, write the manifest, download nothing.
  --max <n>          Stop after n items (default 25). Use with care.
  --type <t>         image | audio | video | any   (default any)
  --min-width <px>   Images only: skip anything narrower.
  --query "<terms>"  Add search terms to the collection or search URL.
  --throttle <ms>    Delay between requests (default ${DEFAULT_THROTTLE_MS}).
  --collections      List LoC collections and exit (no download).

Examples
  # what is in there, downloading nothing
  node tools/loc-dl/loc-dl.mjs "https://www.loc.gov/collections/national-screening-room/" \\
    --out ./assets/loc --simulate

  # 40 large images matching a search inside a collection
  node tools/loc-dl/loc-dl.mjs "https://www.loc.gov/collections/fsa-owi-black-and-white-negatives/" \\
    -q "gymnasium" --type image --min-width 1200 --max 40 --out ./research/loc

Rights: every item is recorded with its LoC rights statement and
rights_reviewed:false. Clear it with a human before anything ships.
`;

/* ------------------------------------------------------------------ http */

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function getJSON(url, throttle) {
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    if (attempt) await sleep(throttle * Math.pow(2, attempt));
    let res;
    try {
      res = await fetch(url, { headers: { 'User-Agent': UA, Accept: 'application/json' } });
    } catch (e) {
      if (attempt === MAX_RETRIES) throw new Error(`network: ${e.message}`);
      continue;
    }
    if (res.status === 429 || res.status >= 500) {
      const ra = parseInt(res.headers.get('retry-after') || '0', 10);
      if (ra) await sleep(ra * 1000);
      if (attempt === MAX_RETRIES) throw new Error(`HTTP ${res.status} after ${MAX_RETRIES} retries`);
      continue;
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const text = await res.text();
    try { return JSON.parse(text); }
    catch { throw new Error(`non-JSON response (${text.slice(0, 80)}…)`); }
  }
}

async function download(url, dest, throttle) {
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    if (attempt) await sleep(throttle * Math.pow(2, attempt));
    let res;
    try {
      res = await fetch(url, { headers: { 'User-Agent': UA } });
    } catch (e) {
      if (attempt === MAX_RETRIES) throw new Error(`network: ${e.message}`);
      continue;
    }
    if (res.status === 429 || res.status >= 500) {
      if (attempt === MAX_RETRIES) throw new Error(`HTTP ${res.status}`);
      continue;
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const buf = Buffer.from(await res.arrayBuffer());
    await writeFile(dest, buf);
    return buf.length;
  }
}

/* ------------------------------------------------------------------ urls */

// Any loc.gov collection or search URL becomes its JSON form. Params we own
// (fo, c, sp, at) are replaced; the caller's own filters are preserved, which is
// what makes "paste the URL from the browser" work.
function apiURL(raw, { page, perPage, query }) {
  let u;
  try { u = new URL(raw); } catch { die(`Not a URL: ${raw}`); }
  if (!/(^|\.)loc\.gov$/.test(u.hostname)) die(`Not a loc.gov URL: ${u.hostname}`);
  u.searchParams.set('fo', 'json');
  u.searchParams.set('c', String(perPage));
  u.searchParams.set('sp', String(page));
  if (query) u.searchParams.set('q', query);
  return u.toString();
}

const stripTags = s => String(s || '').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();

function slug(s, max = 60) {
  return String(s || 'untitled')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, max) || 'untitled';
}

const EXT = {
  'image/jpeg': 'jpg', 'image/jpg': 'jpg', 'image/png': 'png', 'image/tiff': 'tif',
  'image/gif': 'gif', 'video/mp4': 'mp4', 'video/quicktime': 'mov',
  'audio/mpeg': 'mp3', 'audio/mp3': 'mp3', 'audio/wav': 'wav', 'audio/x-wav': 'wav',
  'application/pdf': 'pdf',
};

function extFor(mime, url) {
  if (EXT[mime]) return EXT[mime];
  const m = String(url || '').match(/\.([a-z0-9]{2,4})(?:\?|$)/i);
  return m ? m[1].toLowerCase() : 'bin';
}

const familyOf = mime => {
  const m = String(mime || '');
  if (m.startsWith('image/')) return 'image';
  if (m.startsWith('audio/')) return 'audio';
  if (m.startsWith('video/') || m === 'application/x-video') return 'video';
  return 'other';
};

/* --------------------------------------------------- file candidate picking */

// For time-based media, biggest is the wrong default: LoC serves preservation
// masters (QuickTime, uncompressed WAV) alongside delivery copies, and the master
// is often 5x the size for no usable gain: a 1.6 GB .mov beside a 300 MB .mp4 of
// the same film. Prefer a delivery container, then take the largest within it.
// Images invert this: there is no "delivery vs master" split, so widest wins.
const CONTAINER_RANK = {
  'video/mp4': 0, 'video/m4v': 1, 'video/webm': 2, 'video/mpeg': 3,
  'video/quicktime': 8, 'application/x-video': 9,
  'audio/mpeg': 0, 'audio/mp3': 0, 'audio/mp4': 1, 'audio/x-m4a': 1,
  'audio/flac': 5, 'audio/wav': 8, 'audio/x-wav': 8,
};
const rankOf = mime => (mime in CONTAINER_RANK ? CONTAINER_RANK[mime] : 5);

/**
 * resources[].files is segments × formats. Walk every segment, and within a
 * segment pick the single best format: widest for images, best delivery
 * container then largest for audio/video. One file per segment, so a multi-part
 * item yields multiple files rather than silently collapsing to its first part.
 */
function pickFiles(itemJson, { type, minWidth }) {
  const out = [];
  const resources = Array.isArray(itemJson.resources) ? itemJson.resources : [];

  for (const [ri, resource] of resources.entries()) {
    if (resource.download_restricted) {
      out.push({ skipped: 'download_restricted', resource_index: ri });
      continue;
    }
    const segments = Array.isArray(resource.files) ? resource.files : [];
    for (const [si, segment] of segments.entries()) {
      if (!Array.isArray(segment)) continue;

      const candidates = [];
      for (const f of segment) {
        const url = f.url || f.download;
        if (!url || typeof url !== 'string') continue;
        const mime = f.mimetype || '';
        const fam = familyOf(mime);
        if (fam === 'other') continue;
        if (type !== 'any' && fam !== type) continue;
        const width = Number(f.width) || 0;
        if (fam === 'image' && minWidth && width && width < minWidth) continue;
        candidates.push({
          url: url.startsWith('//') ? `https:${url}` : url,
          mimetype: mime, family: fam,
          width, height: Number(f.height) || 0,
          size: Number(f.size) || 0,
        });
      }
      if (!candidates.length) continue;

      candidates.sort((a, b) =>
        a.family === 'image' && b.family === 'image'
          ? (b.width - a.width) || (b.size - a.size)
          : (rankOf(a.mimetype) - rankOf(b.mimetype)) || (b.size - a.size));

      // LoC does not report width/height on every format: TIFF masters in
      // particular often carry neither, so they sort last on width even when they
      // are the largest file present. Rather than guess which is really biggest,
      // record every alternative alongside the choice so the operator can take a
      // different one without re-crawling. Silent truncation is the failure mode
      // worth avoiding here.
      out.push({
        ...candidates[0],
        resource_index: ri, segment_index: si,
        alternatives: candidates.slice(1).map(c => ({
          mimetype: c.mimetype, width: c.width || null, height: c.height || null,
          size: c.size || null, url: c.url,
        })),
      });
    }
  }
  return out;
}

/* ------------------------------------------------------------------ main */

async function listCollections(throttle) {
  const all = [];
  for (let page = 1; ; page++) {
    const j = await getJSON(`https://www.loc.gov/collections/?fo=json&c=100&sp=${page}`, throttle);
    for (const r of (j.results || [])) all.push({ title: r.title, url: r.id || r.url });
    const p = j.pagination || {};
    if (!p.next || page >= (p.total || 1)) break;
    await sleep(throttle);
  }
  all.sort((a, b) => String(a.title).localeCompare(String(b.title)));
  for (const c of all) console.log(`${c.title}\n  ${c.url}`);
  console.log(`\n${all.length} collections.`);
}

async function main() {
  const a = parseArgs(process.argv.slice(2));
  if (a.help || (!a.url && !a.listCollections)) { console.log(USAGE); process.exit(a.help ? 0 : 1); }

  if (a.listCollections) return listCollections(a.throttle);

  if (!['any', 'image', 'audio', 'video'].includes(a.type)) die(`--type must be image|audio|video|any`);
  if (!Number.isFinite(a.max) || a.max < 1) die('--max must be a positive integer');

  // Validate the URL before anything touches the filesystem. Creating the output
  // directory first and failing after leaves an empty dated folder behind.
  apiURL(a.url, { page: 1, perPage: a.perPage, query: a.query });

  if (!a.out) die('Pass --out <dir>. I will not guess where these belong.');
  const outRoot = resolve(a.out);

  const date = new Date().toISOString().slice(0, 10);
  let dest = join(outRoot, date);
  for (let n = 1; existsSync(dest) && !a.simulate; n++) dest = join(outRoot, `${date}-${n}`);
  await mkdir(dest, { recursive: true });

  console.log(`\n  loc-dl`);
  console.log(`  source   ${a.url}`);
  console.log(`  out      ${dest}${a.simulate ? '  (simulate: nothing will be downloaded)' : ''}`);
  console.log(`  type     ${a.type}   max ${a.max}   throttle ${a.throttle}ms\n`);

  const items = [];
  const problems = [];
  let scanned = 0;

  outer:
  for (let page = 1; ; page++) {
    const url = apiURL(a.url, { page, perPage: a.perPage, query: a.query });
    let listing;
    try { listing = await getJSON(url, a.throttle); }
    catch (e) { die(`Listing failed (page ${page}): ${e.message}`); }

    const results = listing.results || [];
    if (!results.length) break;
    const pag = listing.pagination || {};
    if (page === 1) console.log(`  ${pag.of ?? '?'} items match; taking up to ${a.max}\n`);

    for (const r of results) {
      if (items.length >= a.max) break outer;
      scanned++;

      const itemUrl = r.id && String(r.id).startsWith('http') ? r.id : null;
      if (!itemUrl) { problems.push({ title: r.title, reason: 'no item URL in result' }); continue; }
      if (r.access_restricted) { problems.push({ title: r.title, url: itemUrl, reason: 'access_restricted' }); continue; }

      await sleep(a.throttle);
      let detail;
      try { detail = await getJSON(`${itemUrl.replace(/\/$/, '')}/?fo=json`, a.throttle); }
      catch (e) { problems.push({ title: r.title, url: itemUrl, reason: `item fetch: ${e.message}` }); continue; }

      const it = detail.item || {};
      const rights = []
        .concat(it.rights || [], it.rights_advisory || [])
        .map(stripTags).filter(Boolean);

      const files = pickFiles(detail, { type: a.type, minWidth: a.minWidth });
      const usable = files.filter(f => f.url);
      if (!usable.length) {
        problems.push({
          title: r.title, url: itemUrl,
          reason: files.some(f => f.skipped === 'download_restricted')
            ? 'download_restricted' : `no file matching --type ${a.type}`,
        });
        continue;
      }

      const record = {
        loc_id: it.id || r.id,
        title: it.title || r.title || 'untitled',
        item_url: itemUrl,
        date: it.date || r.date || null,
        contributors: it.contributor_names || null,
        original_format: it.original_format || null,
        access_restricted: !!r.access_restricted,
        rights,
        rights_reviewed: false,
        files: [],
      };

      for (const [i, f] of usable.entries()) {
        const base = `${slug(record.title)}-${slug(String(record.loc_id).split('/').filter(Boolean).pop())}`;
        const suffix = usable.length > 1 ? `-${String(i + 1).padStart(2, '0')}` : '';
        const name = `${base}${suffix}.${extFor(f.mimetype, f.url)}`;
        const entry = {
          file: name, url: f.url, mimetype: f.mimetype, family: f.family,
          width: f.width || null, height: f.height || null,
          expected_bytes: f.size || null, bytes: null, downloaded: false,
          alternatives: f.alternatives || [],
        };

        if (!a.simulate) {
          try {
            await sleep(a.throttle);
            entry.bytes = await download(f.url, join(dest, name), a.throttle);
            entry.downloaded = true;
            console.log(`  ✓ ${name}  (${(entry.bytes / 1048576).toFixed(1)} MB)`);
          } catch (e) {
            entry.error = e.message;
            problems.push({ title: record.title, url: f.url, reason: `download: ${e.message}` });
            console.log(`  ✗ ${name}  ${e.message}`);
          }
        } else {
          console.log(`  · ${name}  ${f.width && f.height ? `${f.width}x${f.height}` : ''} ${f.size ? `${(f.size / 1048576).toFixed(1)} MB` : ''}`);
        }
        record.files.push(entry);
      }
      items.push(record);
    }

    if (!pag.next) break;
    await sleep(a.throttle);
  }

  const manifest = {
    source_url: a.url,
    query: a.query || null,
    run_date: date,
    simulate: a.simulate,
    filters: { type: a.type, min_width: a.minWidth || null, max: a.max },
    scanned,
    items_kept: items.length,
    files_total: items.reduce((n, i) => n + i.files.length, 0),
    bytes_total: items.reduce((n, i) => n + i.files.reduce((m, f) => m + (f.bytes || 0), 0), 0),
    problems,
    rights_note:
      'LoC digitizes material it does not necessarily hold rights to. Each item carries its ' +
      'rights statement verbatim; rights_reviewed is false until a human clears it. Do not ship ' +
      'an item from this manifest without reading its rights field.',
    items,
  };
  await writeFile(join(dest, 'manifest.json'), JSON.stringify(manifest, null, 2));
  await writeFile(join(dest, 'REVIEW.md'), renderReview(manifest, dest));

  console.log(`\n  ${items.length} items, ${manifest.files_total} files` +
    (a.simulate ? ' (simulated)' : `, ${(manifest.bytes_total / 1048576).toFixed(1)} MB`) +
    `${problems.length ? `, ${problems.length} problems` : ''}`);
  console.log(`  manifest.json + REVIEW.md written to ${dest}\n`);
  if (!a.simulate && items.length) console.log(`  Rights are UNREVIEWED. Read REVIEW.md before anything ships.\n`);
}

function renderReview(m, dest) {
  const L = [];
  L.push(`# LoC pull: ${m.run_date}`, '');
  L.push(`**Source:** ${m.source_url}`);
  if (m.query) L.push(`**Query:** \`${m.query}\``);
  L.push(`**Filters:** type=${m.filters.type}${m.filters.min_width ? `, min-width=${m.filters.min_width}` : ''}, max=${m.filters.max}`);
  L.push(`**Scanned:** ${m.scanned} · **Kept:** ${m.items_kept} · **Files:** ${m.files_total}` +
    (m.simulate ? ' *(simulate: nothing downloaded)*' : ` · **${(m.bytes_total / 1048576).toFixed(1)} MB**`));
  L.push('', '---', '');
  L.push(`## Rights: read before using anything here`, '');
  L.push(m.rights_note, '');
  L.push('The Library of Congress digitizes a great deal of material whose rights it does not hold.');
  L.push('A permissive-sounding statement on one item says nothing about the next one. Clear each');
  L.push('item you intend to ship, then set `rights_reviewed: true` in `manifest.json` with a note.');
  L.push('', '---', '');
  L.push('## Items', '');
  for (const it of m.items) {
    L.push(`### ${it.title}`);
    L.push(`- **Item:** ${it.item_url}`);
    if (it.date) L.push(`- **Date:** ${it.date}`);
    if (it.original_format) L.push(`- **Format:** ${[].concat(it.original_format).join(', ')}`);
    L.push(`- **Files:** ${it.files.map(f => `\`${f.file}\``).join(', ') || ', '}`);
    L.push(`- **Rights:** ${it.rights.length ? it.rights.join(' ').slice(0, 400) : '**none stated: treat as unclear**'}`);
    L.push('');
  }
  if (m.problems.length) {
    L.push('---', '', '## Skipped / failed', '');
    L.push('| Item | Why |', '|---|---|');
    for (const p of m.problems) L.push(`| ${String(p.title || p.url || '?').replace(/\|/g, '\\|')} | ${p.reason} |`);
    L.push('');
  }
  L.push('---', '', `Generated by \`tools/loc-dl\`. Output: \`${dest}\``);
  return L.join('\n');
}

main().catch(e => die(e.stack || e.message));
