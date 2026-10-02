#!/usr/bin/env node
/**
 * image-search-mcp: unified image discovery across Pexels, Unsplash and Pixabay.
 *
 * Zero dependencies on purpose. MCP stdio is newline-delimited JSON-RPC 2.0, which is
 * ~60 lines to implement directly. That removes an SDK version to drift against and
 * means `node server.mjs` runs with nothing installed. Node 18+ (global fetch).
 *
 * Design notes that are load-bearing, not preference:
 *  - Pixabay's terms REQUIRE caching responses for 24h and PROHIBIT permanent
 *    hotlinking. So: a 24h disk cache, and download_image exists so assets land on
 *    your own storage rather than being referenced from cdn.pixabay.com.
 *  - Unsplash REQUIRES a GET to links.download_location whenever a download actually
 *    happens. download_image fires it. Skipping it violates the API terms.
 *  - Filters differ per source. Where a source cannot express a requested filter, the
 *    result reports it in unsupported_filters instead of silently returning unfiltered
 *    images that look like they matched.
 */

import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { homedir } from 'node:os';

const PROTOCOL_VERSION = '2025-06-18';
const SERVER = { name: 'image-search-mcp', version: '1.0.0' };

const KEYS = {
  pexels: process.env.PEXELS_API_KEY || '',
  unsplash: process.env.UNSPLASH_ACCESS_KEY || '',
  pixabay: process.env.PIXABAY_API_KEY || '',
};

const CACHE_DIR = process.env.IMAGE_MCP_CACHE_DIR || join(homedir(), '.cache', 'image-search-mcp');
// Pixabay's 24h cache is a terms requirement. The others are courtesy + rate-limit relief.
const CACHE_TTL_MS = { pixabay: 24 * 3600e3, pexels: 15 * 60e3, unsplash: 15 * 60e3 };

/* ------------------------------------------------------------------ vocabulary */

// One color vocabulary for the caller; each source gets its own dialect.
const COLOR_MAP = {
  pexels:   { red:'red', orange:'orange', yellow:'yellow', green:'green', teal:'turquoise',
              blue:'blue', purple:'violet', pink:'pink', brown:'brown', black:'black',
              gray:'gray', white:'white' },
  unsplash: { red:'red', orange:'orange', yellow:'yellow', green:'green', teal:'teal',
              blue:'blue', purple:'purple', pink:'magenta', black:'black', white:'white',
              grayscale:'black_and_white' },
  pixabay:  { red:'red', orange:'orange', yellow:'yellow', green:'green', teal:'turquoise',
              blue:'blue', purple:'lilac', pink:'pink', brown:'brown', black:'black',
              gray:'gray', white:'white', grayscale:'grayscale', transparent:'transparent' },
};
const COLORS = [...new Set(Object.values(COLOR_MAP).flatMap(Object.keys))].sort();

const ORIENTATION_MAP = {
  pexels:   { landscape:'landscape', portrait:'portrait', square:'square' },
  unsplash: { landscape:'landscape', portrait:'portrait', square:'squarish' },
  pixabay:  { landscape:'horizontal', portrait:'vertical' }, // no square concept
};

const PIXABAY_CATEGORIES = ['backgrounds','fashion','nature','science','education','feelings',
  'health','people','religion','places','animals','industry','computer','food','sports',
  'transportation','travel','buildings','business','music'];

const LICENSE = {
  pexels:   { name:'Pexels License', commercial_ok:true, attribution_required:false,
              note:'Free for commercial use. Crediting the photographer is requested, not required.' },
  unsplash: { name:'Unsplash License', commercial_ok:true, attribution_required:false,
              note:'Attribution not legally required but required by API guidelines for API-sourced images. download_location must be triggered on download.' },
  pixabay:  { name:'Pixabay Content License', commercial_ok:true, attribution_required:false,
              note:'No attribution required. Permanent hotlinking prohibited: download to your own storage. Responses must be cached 24h.' },
};

/* ------------------------------------------------------------------ cache */

async function cached(source, url, headers) {
  const key = createHash('sha256').update(url).digest('hex').slice(0, 32);
  const file = join(CACHE_DIR, source, `${key}.json`);
  const ttl = CACHE_TTL_MS[source] ?? 15 * 60e3;

  if (existsSync(file)) {
    try {
      const { at, body } = JSON.parse(await readFile(file, 'utf8'));
      if (Date.now() - at < ttl) return { body, from_cache: true };
    } catch { /* corrupt entry: refetch */ }
  }

  const res = await fetch(url, { headers });
  const text = await res.text();
  if (!res.ok) {
    const hint = res.status === 401 || res.status === 403
      ? `: check the API key for ${source}`
      : res.status === 429 ? `: rate limited by ${source}` : '';
    throw new Error(`${source} HTTP ${res.status}${hint}: ${text.slice(0, 300)}`);
  }
  const body = JSON.parse(text);
  await mkdir(dirname(file), { recursive: true });
  await writeFile(file, JSON.stringify({ at: Date.now(), body }));
  return { body, from_cache: false };
}

/* ------------------------------------------------------------------ normalize */

const ratio = (w, h) => (h ? Number((w / h).toFixed(3)) : null);

function attribution(source, author, authorUrl, pageUrl, title) {
  const utm = '?utm_source=workspace-blueprint&utm_medium=referral';
  if (source === 'unsplash') {
    return {
      text: `Photo by ${author} on Unsplash`,
      html: `Photo by <a href="${authorUrl}${utm}">${author}</a> on <a href="https://unsplash.com/${utm}">Unsplash</a>`,
      required: true,
    };
  }
  if (source === 'pexels') {
    return {
      text: `Photo by ${author} on Pexels`,
      html: `Photo by <a href="${authorUrl}">${author}</a> on <a href="${pageUrl}">Pexels</a>`,
      required: false,
    };
  }
  return {
    text: `Image by ${author} on Pixabay`,
    html: `Image by <a href="${pageUrl}">${author}</a> on <a href="https://pixabay.com/">Pixabay</a>`,
    required: false,
  };
}

function normPexels(p) {
  return {
    id: String(p.id), source: 'pexels',
    description: p.alt || null,
    width: p.width, height: p.height, aspect_ratio: ratio(p.width, p.height),
    avg_color: p.avg_color || null,
    preview_url: p.src?.tiny, display_url: p.src?.large, full_url: p.src?.original,
    download_url: p.src?.original,          // direct, no trigger required
    page_url: p.url,
    author: { name: p.photographer, url: p.photographer_url },
    license: LICENSE.pexels,
    attribution: attribution('pexels', p.photographer, p.photographer_url, p.url),
    tags: [],
  };
}

function normUnsplash(p) {
  return {
    id: p.id, source: 'unsplash',
    description: p.description || p.alt_description || null,
    width: p.width, height: p.height, aspect_ratio: ratio(p.width, p.height),
    avg_color: p.color || null,
    preview_url: p.urls?.thumb, display_url: p.urls?.regular, full_url: p.urls?.full,
    // Not a plain URL on purpose: Unsplash requires triggering download_location.
    download_url: null,
    download_location: p.links?.download_location || null,
    page_url: p.links?.html,
    author: { name: p.user?.name, url: p.user?.links?.html },
    license: LICENSE.unsplash,
    attribution: attribution('unsplash', p.user?.name, p.user?.links?.html, p.links?.html),
    tags: (p.tags || []).map(t => t.title).filter(Boolean),
  };
}

// Pixabay reports imageWidth/imageHeight for the ORIGINAL, but serves originals
// only to full-API accounts. Without that access the largest obtainable file is
// largeImageURL, capped at 1280px on the long edge (fullHDURL is 1920). Reporting
// the original as `width` promises a resolution download_image cannot deliver , 
// so `width`/`height` are the obtainable size and the original is kept alongside.
function normPixabay(h) {
  const cap = h.fullHDURL ? 1920 : 1280;
  const longEdge = Math.max(h.imageWidth, h.imageHeight) || cap;
  const scale = Math.min(1, cap / longEdge);
  const w = Math.round(h.imageWidth * scale);
  const ht = Math.round(h.imageHeight * scale);
  return {
    id: String(h.id), source: 'pixabay',
    description: h.tags || null,
    width: w, height: ht, aspect_ratio: ratio(w, ht),
    original_width: h.imageWidth, original_height: h.imageHeight,
    obtainable_note: scale < 1
      ? `Original is ${h.imageWidth}x${h.imageHeight}; this API key can only download ${w}x${ht} (${cap}px long edge).`
      : null,
    avg_color: null,
    preview_url: h.previewURL, display_url: h.webformatURL,
    // fullHDURL / imageURL are only present for full-API accounts.
    full_url: h.fullHDURL || h.largeImageURL,
    download_url: h.fullHDURL || h.largeImageURL,
    page_url: h.pageURL,
    author: { name: h.user, url: `https://pixabay.com/users/${h.user}-${h.user_id}/` },
    license: LICENSE.pixabay,
    attribution: attribution('pixabay', h.user, null, h.pageURL),
    tags: (h.tags || '').split(',').map(s => s.trim()).filter(Boolean),
    hotlink_prohibited: true,
  };
}

/* ------------------------------------------------------------------ sources */

async function searchPexels(a) {
  const unsupported = [];
  const q = new URLSearchParams({ query: a.query, per_page: String(Math.min(a.per_page, 80)), page: String(a.page) });
  if (a.orientation) q.set('orientation', ORIENTATION_MAP.pexels[a.orientation]);
  if (a.color) {
    const c = COLOR_MAP.pexels[a.color];
    c ? q.set('color', c) : unsupported.push(`color=${a.color}`);
  }
  if (a.size) q.set('size', a.size);
  if (a.category) unsupported.push('category (Pexels has no category filter)');
  if (a.image_type && a.image_type !== 'photo') unsupported.push(`image_type=${a.image_type} (Pexels is photos only)`);

  const { body, from_cache } = await cached('pexels', `https://api.pexels.com/v1/search?${q}`,
    { Authorization: KEYS.pexels });
  return { items: (body.photos || []).map(normPexels), total: body.total_results ?? null, unsupported, from_cache };
}

async function searchUnsplash(a) {
  const unsupported = [];
  const q = new URLSearchParams({ query: a.query, per_page: String(Math.min(a.per_page, 30)), page: String(a.page) });
  if (a.orientation) q.set('orientation', ORIENTATION_MAP.unsplash[a.orientation]);
  if (a.color) {
    const c = COLOR_MAP.unsplash[a.color];
    c ? q.set('color', c) : unsupported.push(`color=${a.color}`);
  }
  if (a.order === 'latest') q.set('order_by', 'latest');
  if (a.size) unsupported.push('size (Unsplash has no size filter: use min_width)');
  if (a.category) unsupported.push('category (Unsplash has no category filter)');
  if (a.image_type && a.image_type !== 'photo') unsupported.push(`image_type=${a.image_type} (Unsplash is photos only)`);

  const { body, from_cache } = await cached('unsplash', `https://api.unsplash.com/search/photos?${q}`,
    { Authorization: `Client-ID ${KEYS.unsplash}`, 'Accept-Version': 'v1' });
  return { items: (body.results || []).map(normUnsplash), total: body.total ?? null, unsupported, from_cache };
}

async function searchPixabay(a) {
  const unsupported = [];
  const q = new URLSearchParams({
    key: KEYS.pixabay, q: a.query,
    per_page: String(Math.max(3, Math.min(a.per_page, 200))),
    page: String(a.page), safesearch: a.safesearch === false ? 'false' : 'true',
    order: a.order === 'latest' ? 'latest' : 'popular',
    image_type: a.image_type || 'photo',
  });
  if (a.orientation) {
    const o = ORIENTATION_MAP.pixabay[a.orientation];
    o ? q.set('orientation', o) : unsupported.push('orientation=square (Pixabay has no square filter)');
  }
  if (a.color) {
    const c = COLOR_MAP.pixabay[a.color];
    c ? q.set('colors', c) : unsupported.push(`color=${a.color}`);
  }
  if (a.category) {
    PIXABAY_CATEGORIES.includes(a.category) ? q.set('category', a.category)
      : unsupported.push(`category=${a.category} (not a Pixabay category)`);
  }
  if (a.min_width) q.set('min_width', String(a.min_width));
  if (a.min_height) q.set('min_height', String(a.min_height));
  if (a.size) unsupported.push('size (Pixabay uses min_width/min_height instead)');

  const { body, from_cache } = await cached('pixabay', `https://pixabay.com/api/?${q}`, {});
  const items = (body.hits || []).map(normPixabay);

  // Pixabay applies min_width/min_height to the ORIGINAL, which this key usually
  // cannot download. Say so rather than returning results that look like matches.
  if (a.min_width || a.min_height) {
    const short = items.filter(i =>
      (a.min_width && i.width < a.min_width) || (a.min_height && i.height < a.min_height));
    if (short.length) {
      unsupported.push(
        `min_width/min_height matched Pixabay's original dimensions, but this key downloads at most ` +
        `${short[0].width >= short[0].height ? short[0].width : short[0].height}px on the long edge: ` +
        `${short.length} of ${items.length} results cannot be obtained at the requested size`);
    }
  }

  return { items, total: body.totalHits ?? null, unsupported, from_cache };
}

const SOURCES = {
  pexels:   { search: searchPexels,   key: 'PEXELS_API_KEY',      limit: '200 req/hour, 20k/month' },
  unsplash: { search: searchUnsplash, key: 'UNSPLASH_ACCESS_KEY', limit: 'Demo 50 req/hour · Production 1000 req/hour' },
  pixabay:  { search: searchPixabay,  key: 'PIXABAY_API_KEY',     limit: '100 req/60s · 24h response cache required' },
};

/* ------------------------------------------------------------------ tools */

function interleave(groups) {
  const out = []; let i = 0;
  for (;;) {
    let added = false;
    for (const g of groups) if (g[i]) { out.push(g[i]); added = true; }
    if (!added) return out;
    i++;
  }
}

async function toolSearchImages(a) {
  const args = {
    query: a.query, per_page: a.per_page ?? 10, page: a.page ?? 1,
    orientation: a.orientation, color: a.color, size: a.size, category: a.category,
    min_width: a.min_width, min_height: a.min_height, image_type: a.image_type,
    order: a.order, safesearch: a.safesearch,
  };
  const requested = a.sources?.length ? a.sources : Object.keys(SOURCES);
  const active = requested.filter(s => SOURCES[s] && KEYS[s]);
  const skipped = requested
    .filter(s => SOURCES[s] && !KEYS[s])
    .map(s => `${s}: ${SOURCES[s].key} not set`);

  if (!active.length) {
    return {
      error: 'No usable source. Every requested source is missing its API key.',
      missing_keys: skipped,
      hint: 'Set the keys in the MCP server env block, then restart the client.',
    };
  }

  const settled = await Promise.allSettled(active.map(s => SOURCES[s].search(args)));
  const per_source = {}, groups = [];
  settled.forEach((r, i) => {
    const s = active[i];
    if (r.status === 'fulfilled') {
      per_source[s] = { returned: r.value.items.length, total_available: r.value.total,
                        unsupported_filters: r.value.unsupported, from_cache: r.value.from_cache };
      groups.push(r.value.items);
    } else {
      per_source[s] = { error: String(r.reason?.message || r.reason) };
    }
  });

  return {
    query: a.query,
    results: interleave(groups),           // round-robin so one source cannot dominate page 1
    per_source,
    skipped_sources: skipped.length ? skipped : undefined,
    reminder: 'Pixabay images must not be permanently hotlinked: use download_image. Unsplash downloads must go through download_image so the required download trigger fires.',
  };
}

async function toolDownloadImage(a) {
  const { source, url, dest } = a;
  if (!SOURCES[source]) throw new Error(`Unknown source: ${source}`);

  let fileUrl = url;

  // Unsplash: the terms require a GET to download_location at actual-download time.
  // It returns the real file URL, so this is both compliance and the way to get the asset.
  let triggered = false;
  if (source === 'unsplash') {
    if (!a.download_location) {
      throw new Error('Unsplash requires download_location (from the search result): pass it so the required download trigger fires.');
    }
    const sep = a.download_location.includes('?') ? '&' : '?';
    const r = await fetch(`${a.download_location}${sep}client_id=${KEYS.unsplash}`);
    if (!r.ok) throw new Error(`Unsplash download trigger failed: HTTP ${r.status}`);
    fileUrl = (await r.json()).url;
    triggered = true;
  }
  if (!fileUrl) throw new Error('No file URL resolved.');

  const res = await fetch(fileUrl);
  if (!res.ok) throw new Error(`Download failed: HTTP ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());

  const out = resolve(dest);
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, buf);

  return {
    saved_to: out, bytes: buf.length, source,
    unsplash_download_triggered: source === 'unsplash' ? triggered : undefined,
    attribution_note: source === 'unsplash'
      ? 'Unsplash API guidelines require visible attribution wherever this image appears.'
      : 'Attribution not required, but credit the author where practical.',
  };
}

function toolListSources() {
  // Reports reachability, not just capability: a configured key is not a working key,
  // and a tool that conflates the two costs a session to debug.
  return {
    sources: Object.entries(SOURCES).map(([name, s]) => ({
      name,
      key_env_var: s.key,
      key_present: Boolean(KEYS[name]),
      status: KEYS[name] ? 'configured' : 'NOT CONFIGURED: searches will skip this source',
      rate_limit: s.limit,
      license: LICENSE[name].name,
      notes: LICENSE[name].note,
    })),
    cache_dir: CACHE_DIR,
    caveat: 'key_present means a value is set, not that it is valid. Run a search to confirm.',
  };
}

const TOOLS = [
  {
    name: 'search_images',
    description: 'Search Pexels, Unsplash and Pixabay at once for any image task: website heroes, landing pages, blog headers, UI backgrounds, social graphics, mockups. Returns a normalized shape per result: direct URLs, dimensions, dominant color, author, license and ready-to-paste attribution. Results are interleaved across sources so one library cannot dominate the first page. Filters a source cannot express are reported in per_source.unsupported_filters rather than silently ignored.',
    inputSchema: {
      type: 'object',
      required: ['query'],
      additionalProperties: false,
      properties: {
        query: { type: 'string', description: 'Concept or subject, e.g. "empty gym interior morning light"' },
        sources: { type: 'array', items: { type: 'string', enum: ['pexels','unsplash','pixabay'] },
                   description: 'Defaults to every source that has a key set.' },
        orientation: { type: 'string', enum: ['landscape','portrait','square'],
                       description: 'Pixabay has no square filter and will report it unsupported.' },
        color: { type: 'string', enum: COLORS, description: 'Normalized across all three color vocabularies.' },
        size: { type: 'string', enum: ['large','medium','small'], description: 'Pexels only (24MP/12MP/4MP).' },
        category: { type: 'string', enum: PIXABAY_CATEGORIES, description: 'Pixabay only.' },
        image_type: { type: 'string', enum: ['photo','illustration','vector','all'],
                      description: 'Pixabay only: Pexels and Unsplash are photos only.' },
        min_width: { type: 'integer', description: 'Pixabay only.' },
        min_height: { type: 'integer', description: 'Pixabay only.' },
        order: { type: 'string', enum: ['popular','latest','relevant'], default: 'relevant' },
        safesearch: { type: 'boolean', default: true, description: 'Pixabay only. Defaults on.' },
        per_page: { type: 'integer', default: 10, description: 'Per source. Caps: Pexels 80, Unsplash 30, Pixabay 200.' },
        page: { type: 'integer', default: 1 },
      },
    },
  },
  {
    name: 'download_image',
    description: 'Download an image to local disk. Use this rather than hotlinking: Pixabay prohibits permanent hotlinking outright, and Unsplash requires a download trigger to fire: this tool fires it and returns the resolved file URL. Pass download_location from the search result for Unsplash items.',
    inputSchema: {
      type: 'object',
      required: ['source','dest'],
      additionalProperties: false,
      properties: {
        source: { type: 'string', enum: ['pexels','unsplash','pixabay'] },
        url: { type: 'string', description: 'download_url from the search result (Pexels / Pixabay).' },
        download_location: { type: 'string', description: 'Required for Unsplash: from the search result.' },
        dest: { type: 'string', description: 'Absolute or relative file path to write, e.g. ./assets/hero.jpg' },
      },
    },
  },
  {
    name: 'list_sources',
    description: 'Report which sources are configured, their rate limits, license terms and the cache directory. Run this first when a search returns fewer sources than expected.',
    inputSchema: { type: 'object', properties: {}, additionalProperties: false },
  },
];

const HANDLERS = { search_images: toolSearchImages, download_image: toolDownloadImage, list_sources: toolListSources };

/* ------------------------------------------------------------------ JSON-RPC over stdio */

const send = msg => process.stdout.write(JSON.stringify(msg) + '\n');
const ok = (id, result) => send({ jsonrpc: '2.0', id, result });
const fail = (id, code, message) => send({ jsonrpc: '2.0', id, error: { code, message } });

async function handle(msg) {
  const { id, method, params } = msg;
  if (id === undefined) return;                   // notification: nothing to answer

  switch (method) {
    case 'initialize':
      return ok(id, { protocolVersion: PROTOCOL_VERSION, capabilities: { tools: { listChanged: false } }, serverInfo: SERVER });
    case 'ping':
      return ok(id, {});
    case 'tools/list':
      return ok(id, { tools: TOOLS });
    case 'tools/call': {
      const fn = HANDLERS[params?.name];
      if (!fn) return fail(id, -32602, `Unknown tool: ${params?.name}`);
      try {
        const out = await fn(params.arguments || {});
        return ok(id, { content: [{ type: 'text', text: JSON.stringify(out, null, 2) }] });
      } catch (e) {
        // isError keeps the model in the loop to correct itself instead of hard-failing the turn.
        return ok(id, { content: [{ type: 'text', text: `Error: ${e.message}` }], isError: true });
      }
    }
    default:
      return fail(id, -32601, `Method not found: ${method}`);
  }
}

let buf = '';

function dispatch(msg) {
  handle(msg).catch(e => { if (msg?.id !== undefined) fail(msg.id, -32603, String(e?.message || e)); });
}

process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => {
  buf += chunk;
  let nl;
  while ((nl = buf.indexOf('\n')) !== -1) {
    const line = buf.slice(0, nl).trim();
    buf = buf.slice(nl + 1);
    if (!line) continue;
    let msg;
    try { msg = JSON.parse(line); } catch { continue; }
    dispatch(msg);
  }
});

// No explicit exit on stdin 'end', deliberately. Two bugs live here:
//  1. process.exit() on 'end' truncates in-flight tool calls: piped input closes stdin
//     immediately, so a search whose HTTP request is still open never answers.
//  2. Calling process.exit() from inside a callback trips a libuv assertion on Windows
//     (UV_HANDLE_CLOSING, src\win\async.c) once handles are already tearing down.
// Node exits on its own when stdin has ended and no work remains, which is both correct
// and what a long-running client wants: stay alive while the pipe is open.
process.stdin.on('error', () => {});
