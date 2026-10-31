---
name: loc-dl
description: "Downloads images from the Library of Congress with their rights statement attached. Use when real, license-clean historical photos are needed."
---

# loc-dl

Needs Node.js. Run, from the workspace root:

```bash
node tools/loc-dl/loc-dl.mjs "<loc.gov search or collection URL>" --out assets/loc/<topic>/
node tools/loc-dl/loc-dl.mjs --help
```

Every image lands with its rights statement copied word for word and `rights_reviewed: false`. Before any image is used in something published, a person reads the rights line and flips that to `true`. Never skip that.
