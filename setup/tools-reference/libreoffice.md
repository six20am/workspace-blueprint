# LibreOffice

A free office suite. Here it is mostly used without a window to convert Word, Excel and PowerPoint files to PDF and back.

```
soffice --headless --convert-to pdf report.docx
soffice --headless --convert-to xlsx data.csv
```

**Gotcha:** It is a 300 MB or more download. A conversion fails silently if LibreOffice is already open in a window; close it first.
