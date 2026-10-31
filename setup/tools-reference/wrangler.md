# Wrangler

Cloudflare's command line tool. Runs a site locally and puts it live on Cloudflare Workers. The `site-builder` skill uses it.

```
npx wrangler login --use-keyring --scopes <deploy scopes>
npx astro build && npx wrangler deploy
```

**Gotcha:** `wrangler login` with no `--scopes` asks for every permission the account has, and without `--use-keyring` it keeps the token in a readable file. It also sends usage data to Cloudflare by default; `WRANGLER_SEND_METRICS=false` turns that off. Needs Node 22 or newer and Windows 11 or newer.
