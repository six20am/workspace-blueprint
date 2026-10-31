---
name: gallery-dl
description: "Downloads original-size images from a social page or web gallery the person owns or has rights to. Use when asked to pull photos from their Instagram, Facebook page or a gallery link."
---

# gallery-dl

Preview first, download second.

Windows:
```powershell
tools\gallery-dl\pull.ps1 -Out social-harvest -Simulate <url>    # lists what it would fetch
tools\gallery-dl\pull.ps1 -Out social-harvest <url>
```

Mac:
```bash
gallery-dl --simulate <url>
gallery-dl -d social-harvest <url>
```

Only from accounts the person owns or has permission for. Login cookies, if needed, are passed at run time (`-CookiesFile` on Windows, `--cookies` on Mac) and never stored.
