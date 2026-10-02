---
name: image-search
description: "Searches and downloads free stock photos from Pexels, Unsplash and Pixabay with the licence recorded per image. Use when a page or post needs a photo and the person has none."
---

# image-search

This is an MCP server the installer connects to Claude (its tools are `list_sources`, `search_images`, `download_image`). It needs free API keys as environment variables: `PEXELS_API_KEY` and `PIXABAY_API_KEY` (and `UNSPLASH_ACCESS_KEY` if wanted). If a search returns an auth error, tell the person where to get the keys (pexels.com/api, pixabay.com/api) and stop. Run `list_sources` first to see which sources have keys.

Always download, never hotlink. Every download writes the licence line next to the file. Prefer the person's own photos when they have any; stock is the fallback.
