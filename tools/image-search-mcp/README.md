# image-search-mcp

One MCP server for free stock photo search across Pexels, Unsplash and Pixabay. Normalised results, licence recorded per image, no dependencies (Node 18+).

## Keys

Free API keys, set as environment variables before Claude starts:

| Source | Variable | Where to get it |
|---|---|---|
| Pexels | `PEXELS_API_KEY` | pexels.com/api |
| Pixabay | `PIXABAY_API_KEY` | pixabay.com/api/docs |
| Unsplash | `UNSPLASH_ACCESS_KEY` | unsplash.com/developers (optional; demo tier is 50 requests an hour) |

A source with no key is simply skipped. `list_sources` shows which are live.

## Connect to Claude

Setup does this. By hand:

```
claude mcp add image-search -- node "<workspace>/tools/image-search-mcp/server.mjs"
```

## Tools

- `list_sources`: which sources have keys, their rate limits, the cache folder.
- `search_images`: query, orientation, size, source filter. Returns normalised results with a licence block per image.
- `download_image`: saves the file and writes its licence line beside it.

Always download, never hotlink. Cache lives at `~/.cache/image-search-mcp` (`IMAGE_MCP_CACHE_DIR` to move it).
