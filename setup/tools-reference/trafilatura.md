# Trafilatura

Downloads a web page and returns its main text, without the menus and ads. Good for many pages at once.

```
trafilatura -u https://example.com/article
trafilatura -i urls.txt -o out-folder --markdown
```

**Gotcha:** Like Defuddle it does not run JavaScript, so pages that load their text later may come back empty.
