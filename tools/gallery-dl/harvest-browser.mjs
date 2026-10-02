#!/usr/bin/env node
/**
 * harvest-browser: a disposable browser for social harvest auth.
 *
 * Launches an isolated Playwright Chromium with its own profile directory, waits for you to
 * log in by hand, then exports the session as a Netscape cookies.txt for gallery-dl.
 *
 * Why this exists: Chrome 127+ App-Bound Encryption blocks third-party reads of its cookie
 * store, so `gallery-dl --cookies-from-browser chrome` fails with a DPAPI decrypt error on
 * Windows. This sidesteps the problem entirely: cookies come from Playwright's API, not from
 * decrypting a cookie database, so there is nothing to decrypt.
 *
 * The profile directory is disposable and lives outside any client repo. Use a THROWAWAY
 * account: automated pulls carry a real account-flag risk (see README § Authentication).
 *
 *   node harvest-browser.mjs --site instagram --out C:\path\to\cookies.txt
 *   node harvest-browser.mjs --site facebook  --out ...  --profile C:\path\to\profile-dir
 *
 * Flags:
 *   --site <name>     instagram | facebook | <any host>   (default: instagram)
 *   --out <path>      where to write cookies.txt          (required)
 *   --profile <path>  profile dir to reuse                (default: alongside --out)
 *   --timeout <min>   how long to wait for login          (default: 10)
 *   --keep-open       leave the browser open after export
 */

import { chromium } from 'playwright';
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';

const SITES = {
  instagram: { url: 'https://www.instagram.com/accounts/login/', marker: 'sessionid', domain: 'instagram.com' },
  facebook:  { url: 'https://www.facebook.com/login',            marker: 'c_user',    domain: 'facebook.com' },
};

function arg(name, fallback = null) {
  const i = process.argv.indexOf(`--${name}`);
  return i !== -1 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}
const flag = (name) => process.argv.includes(`--${name}`);

const siteName = (arg('site', 'instagram')).toLowerCase();
const out = arg('out');
const timeoutMin = Number(arg('timeout', '10'));

if (!out) {
  console.error('error: --out <path to cookies.txt> is required');
  process.exit(2);
}

const site = SITES[siteName] ?? { url: `https://${siteName}/`, marker: null, domain: siteName };
const profileDir = arg('profile', join(dirname(out), `${siteName}-profile`));

mkdirSync(dirname(out), { recursive: true });
mkdirSync(profileDir, { recursive: true });

console.log(`site     : ${siteName}`);
console.log(`profile  : ${profileDir}   (disposable: delete when done)`);
console.log(`cookies  : ${out}`);
console.log('');

const context = await chromium.launchPersistentContext(profileDir, {
  headless: false,
  viewport: null,
  args: ['--window-size=1280,900'],
});

const page = context.pages()[0] ?? (await context.newPage());
await page.goto(site.url, { waitUntil: 'domcontentloaded' }).catch(() => {});

console.log('>> Log in in the browser window that just opened. Use a THROWAWAY account.');
console.log(`>> Waiting up to ${timeoutMin} min for the session to appear...`);
console.log('');

const deadline = Date.now() + timeoutMin * 60_000;
let cookies = [];
let loggedIn = false;

while (Date.now() < deadline) {
  cookies = await context.cookies();
  if (!site.marker) { loggedIn = cookies.length > 0; }
  else {
    loggedIn = cookies.some(
      (c) => c.name === site.marker && c.value && c.domain.includes(site.domain),
    );
  }
  if (loggedIn) break;
  await new Promise((r) => setTimeout(r, 2000));
}

if (!loggedIn) {
  console.error(`\nerror: no ${site.marker ?? 'session'} cookie after ${timeoutMin} min: not logged in.`);
  await context.close();
  process.exit(1);
}

// Netscape cookie file. Tab-separated; a leading dot on the domain means "include subdomains".
const lines = ['# Netscape HTTP Cookie File', '# Written by harvest-browser.mjs', ''];
for (const c of cookies) {
  const includeSub = c.domain.startsWith('.') ? 'TRUE' : 'FALSE';
  const expires = c.expires && c.expires > 0 ? Math.floor(c.expires) : 0;
  lines.push(
    [c.domain, includeSub, c.path || '/', c.secure ? 'TRUE' : 'FALSE', expires, c.name, c.value].join('\t'),
  );
}
writeFileSync(out, lines.join('\n') + '\n', 'utf8');

// Same session, two more shapes, so one hand login serves every consumer:
//
//   <out>              Netscape cookies.txt  → gallery-dl  (pull.ps1 -CookiesFile)
//   <out>.header.txt   raw Cookie: header    → any tool that takes a raw Cookie header
//   <out>.state.json   Playwright storageState → any Playwright/Stagehand script
//
// The header file is passed straight through as an HTTP Cookie header by tools that accept one.
// (lib/util.mjs fetchUrl), so it wants "name=value; name=value" scoped to the
// target host: not the whole cookie jar.
const scoped = cookies.filter((c) => c.domain.replace(/^\./, '').endsWith(site.domain));
const headerPath = `${out}.header.txt`;
const statePath = `${out}.state.json`;

writeFileSync(headerPath, scoped.map((c) => `${c.name}=${c.value}`).join('; ') + '\n', 'utf8');
await context.storageState({ path: statePath });

console.log(`\nOK: ${cookies.length} cookies total, ${scoped.length} scoped to ${site.domain}.`);
console.log(`  cookies.txt   ${out}`);
console.log(`  Cookie header ${headerPath}`);
console.log(`  storageState  ${statePath}`);
console.log('\nConsumers:');
console.log(`  gallery-dl   tools\\gallery-dl\\pull.ps1 -Out social-harvest -CookiesFile "${out}" -Simulate <url>`);

if (!flag('keep-open')) await context.close();
