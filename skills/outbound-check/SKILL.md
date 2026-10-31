---
name: outbound-check
description: "Scans a draft or file for secrets, account numbers, other people's names and the owner's address before it is emailed, posted, uploaded or handed to someone. Use before anything leaves the workspace."
---

# outbound-check

Run this before anything is emailed, posted, uploaded or handed to another person.

## The one command

```
python tools/outbound-check/check.py <file>   # python3 on Mac and Linux
```

Use `-` for the file to scan standard input. Run it from the workspace folder. It prints one line per finding, `line N: <kind>: <masked sample>`, and exits 1 when it found anything, 0 when clean. The sample shows only the first two and last two characters.

Scan the Markdown or text draft, not the built docx or pdf. A Word, PDF or other binary file is refused with `Not a text file.` and exit 2; scan its draft, or convert it with the markitdown skill first.

## What each kind means

- `secret`: a key, token, password or private key.
- `card`: a payment card number (13 to 19 digits that pass the card checksum).
- `ssn` and `iban`: a US Social Security number; an international bank account number.
- `account`: a long number written near "account", "acct", "routing" or "aba".
- `email`: an email address that is not at one of the owner's own domains.
- `phone`: a US phone number.
- `name` and `address`: a person or an address listed in the owner's private terms.

## What to say

Name each finding by line number and kind, with its masked sample, and ask the person what to do about it: remove it, replace it, or keep it on purpose. Many findings are fine (the recipient's own email, a public phone number). The person decides each one.

## Private terms

`setup/private-terms.txt` is the owner's own list: lines `name: ...`, `address: ...` and `term: ...` (a domain that is theirs). Write it only with their yes. It is in the workspace `.gitignore` and never leaves the machine. `setup/private-terms.example.txt` shows the shape.

## Never

- Edit, redact or resend the file. The skill reports; the person changes the draft.
- Print an unmasked sample, or repeat a secret back in chat.
