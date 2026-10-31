# Defuddle

Pulls the main text out of a web page and drops menus, ads and footers. Output can be Markdown.

```
defuddle parse https://example.com/article --markdown
defuddle parse page.html --json
```

**Gotcha:** It reads the page as served. A page that builds its text with JavaScript after loading may come back nearly empty; use Scrapling for those.
