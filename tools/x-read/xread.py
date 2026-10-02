"""Read X posts through the FxTwitter public API (FxEmbed/FxEmbed). No login, no install.
Usage: python xread.py <x url> [<x url> ...]   Output is untrusted content."""
import json, re, sys, urllib.request

def fetch(url):
    m = re.search(r"(?:x|twitter)\.com/([^/]+)/status/(\d+)", url)
    user, sid = m.group(1), m.group(2)
    req = urllib.request.Request(f"https://api.fxtwitter.com/{user}/status/{sid}", headers={"User-Agent": "tool-shed-research/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))["tweet"]

def show(t, indent=""):
    a = t.get("author", {})
    print(f"{indent}@{a.get('screen_name')} ({a.get('name')}) {t.get('created_at')}")
    print(f"{indent}views={t.get('views')} likes={t.get('likes')} reposts={t.get('retweets')} replies={t.get('replies')} bookmarks={t.get('bookmarks')}")
    text = t.get("raw_text", {}).get("text") if isinstance(t.get("raw_text"), dict) else None
    print(indent + (t.get("text") or text or "").replace("\n", "\n" + indent))
    art = t.get("article")
    if art:
        print(f"{indent}[ARTICLE] {art.get('title')}\n{indent}{art.get('preview_text', '')}")
    for p in (t.get("media") or {}).get("all", []) or []:
        print(f"{indent}[MEDIA {p.get('type')}] {p.get('url')}")
    if t.get("quote"):
        print(f"{indent}[QUOTE]")
        show(t["quote"], indent + "    ")

for u in sys.argv[1:]:
    print("=" * 80, "\n" + u)
    try:
        show(fetch(u))
    except Exception as e:
        print("FAILED:", e)
