# Repomix

Packs a whole code folder into one text file so it can be handed to an AI assistant in one go.

```
repomix
repomix --include "src/**/*.ts" -o packed.xml
```

**Gotcha:** It skips files listed in `.gitignore`, but a big folder still makes a very big file. Use `--include` to keep it small.
