# outbound-check

Scans a file for things that should not leave the workspace, before it is emailed, posted, uploaded or handed to someone.

```
python tools/outbound-check/check.py draft.txt   # scan a file
python tools/outbound-check/check.py -           # scan standard input
```

One line per finding, `line N: <kind>: <masked sample>`. The sample keeps its first two and last two characters, so the report never repeats the secret. Exit 1 when anything was found, 0 when clean.

Kinds: `secret` (keys, tokens, passwords, private keys), `card`, `ssn`, `iban`, `account` (a long number near "account", "acct", "routing" or "aba"), `email`, `phone`, `name`, `address`.

It reads `setup/private-terms.txt` when that file exists. Copy `setup/private-terms.example.txt` to that name and fill it in:

```
name: Jane Example
address: 12 Example Street
term: example.com
```

`name` and `address` lines are matched as whole phrases, ignoring case. A `term:` domain is the owner's own email domain, so addresses at it are not reported. With no terms, every email address is reported; the owner decides which are fine.

The file is the owner's and stays out of git (the workspace `.gitignore` lists it). The tool only reads; it never edits what it scans. Standard library only.
