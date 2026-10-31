# qpdf

Splits, joins, rotates, decrypts and repairs PDF files without changing how the pages look.

```
qpdf --empty --pages a.pdf b.pdf -- joined.pdf
qpdf in.pdf --pages . 1-3 -- first-three.pdf
```

**Gotcha:** It cannot remove a password it does not know. For a PDF that opens but will not print or copy, `qpdf --decrypt in.pdf out.pdf` usually works.
