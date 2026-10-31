# jq

Reads, filters and reshapes JSON on the command line.

```
jq '.name' package.json
jq -r '.[] | .id' items.json
```

**Gotcha:** In Windows PowerShell, quote the filter with single quotes and escape inner double quotes, or put the filter in a file and use `jq -f filter.jq`.
