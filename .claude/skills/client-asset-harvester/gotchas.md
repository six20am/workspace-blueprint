# Gotchas: client-asset-harvester

## Cloudflare bot challenge
- Symptom: page title is "Just a moment..." or content is a JavaScript challenge page.
- Behavior: the crawler detects this, logs the URL under `blocked_pages` in manifest, and continues with the next page.
- Workaround: operator can re-run with `--respect-robots false` if appropriate, or manually save the few blocked pages and drop images into `unsorted/` by hand.

## Lazy-loaded images
- The crawler scrolls to the bottom in 4 chunks with 600ms delays between scrolls to trigger most lazy-load libraries (Intersection Observer, scroll listeners).
- Sites with infinite scroll get capped: the crawler does not chase past the 4-cycle limit.
- If a known image is missing from the manifest, increase scroll cycles in `harvest.js` (search for `SCROLL_CYCLES`).

## CSS background-image
- Only images referenced in computed styles at crawl time are captured. Hover states, focus states, and JS-injected styles after interaction are NOT captured.
- Acceptable trade: we want what visitors see on landing, not every state.

## SVG sprites
- A single SVG file containing `<symbol>` definitions used via `<use href="...#id">` is saved once. The manifest records each `#id` it's referenced as.
- Inline SVGs (`<svg>` directly in HTML, no external file) are NOT extracted: there's no source URL to fetch. If the client's logo is an inline SVG, hand-extract it from the page source.

## srcset variants
- Modern responsive images expose multiple URLs via `srcset` (e.g., `image-400.jpg 400w, image-800.jpg 800w`). The crawler downloads the largest variant only: keeps the manifest clean.
- Override: edit `harvest.js`, search for `pickLargestFromSrcset` and change to download all variants.

## Perceptual hash dedup
- Different file formats of the same image (e.g., `hero.jpg` and `hero.webp` served by a CDN) collapse to one entry under the larger / higher-quality file.
- False positives possible for very simple images (a solid-color block, a plain icon). Operator should still skim `unsorted/` if a critical asset seems missing.

## robots.txt
- Default behavior: respect robots.txt. If the root path is disallowed, the crawler halts.
- Operator override: `--respect-robots false`. Only use with the client's written authorization to scrape their site.

## Sites behind login
- The crawler does not authenticate. Login-gated pages return their public placeholder (often the marketing site, sometimes a redirect to a login page).
- For client portals or member areas, operator must export assets manually.

## License caveats
- Scraped images may be licensed stock (Shutterstock, Adobe Stock, iStock) from the previous build. The previous developer's license does NOT transfer to the new build.
- REVIEW.md prints a blanket caveat. Operator must verify rights with the client before reusing any non-founder, non-proof, non-facility image on the new build.

## Founder / proof / facility: never AI per `feedback_two_layer_image_production`
- Real photos of the founder, real customer testimonials, and real facility photos are gold. These are the slots phase 07b cannot AI-generate.
- The `founder_hint` flag in manifest.json is a starting point: operator confirms which is the actual founder.

## File names and paths
- Output filenames in `unsorted/` use a slugified version of the page URL + index (e.g., `about-us-3.jpg`). Multiple images from the same page get sequential indexes.
- `logo-candidates/` filenames lead with a 2-digit rank prefix so the highest-scoring candidate sorts first.

## Multiple runs same day
- Re-running on the same date appends `-1`, `-2`, etc. to the date folder. Older runs are preserved. Manually delete obsolete runs to clean up.

## Memory and disk
- A 25-page crawl with ~50 unique images uses ~300MB Chromium RAM and 5-50MB disk depending on image sizes.
- For larger sites (`--max-pages 100`+), expect proportional growth.

## Playwright Chromium download
- First run after `npm install` requires `npx playwright install chromium` (~150MB one-time).
- The skill prints the install command if Chromium isn't found.

## Idempotency of manifest
- The skill does NOT merge across runs. Each run is self-contained. If you want a historical comparison, diff `manifest.json` between run folders.
