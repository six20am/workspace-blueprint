#!/usr/bin/env python3
"""Scans a file for things that should not leave the workspace.

    python tools/outbound-check/check.py draft.txt     # scan a file
    python tools/outbound-check/check.py -             # scan standard input

Prints one line per finding, "line N: <kind>: <masked sample>", and exits 1 when there is any
finding, 0 when there is none. A binary file (Word, PDF, zip, anything with a NUL byte) is
refused with exit 2: scan the Markdown draft instead. It reads setup/private-terms.txt (the owner's own names, addresses
and email domains) from the workspace root when that file exists. It never edits what it scans.
Standard library only.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TERMS_PATH = os.path.join(ROOT, "setup", "private-terms.txt")

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{22,}"),
    re.compile(r"xox[abpr]-[A-Za-z0-9-]{10,}"),
    re.compile(r"sk_live_[A-Za-z0-9]{10,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]
KEY_VALUE = re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\"']?([A-Za-z0-9_\-]{8,})")
CARD = re.compile(r"(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
IBAN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")
ACCOUNT_WORD = re.compile(r"(?i)\b(?:account|acct|routing|aba)\b")
ACCOUNT_DIGITS = re.compile(r"(?<!\d)\d{8,17}(?!\d)")
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@([A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+)")
PHONE = re.compile(r"(?<!\d)(?:\+1[ \-.]?)?\(?\d{3}\)?[ \-.]?\d{3}[ \-.]?\d{4}(?!\d)")
KINDS = ("name", "address", "term")


def mask(text):
    """Keep the first two and last two characters; the middle becomes '...'."""
    if len(text) <= 4:
        return "..."
    return text[:2] + "..." + text[-2:]


def luhn_ok(digits):
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def is_placeholder(value):
    low = value.lower()
    if low in ("example", "your-key-here") or low.endswith(".example"):
        return True
    return len(set(low)) == 1


def load_terms(path):
    """(kind, value) pairs from lines like 'name: Jane Example'. Blank lines and # comments skipped."""
    terms = []
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return terms
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        kind, _, value = line.partition(":")
        kind, value = kind.strip().lower(), value.strip()
        if kind in KINDS and value:
            terms.append((kind, value))
    return terms


def overlaps(span, spans):
    return any(span[0] < e and s < span[1] for s, e in spans)


def scan_line(line, terms):
    found = []  # (start, kind, matched text)
    owner_domains = {v.lower() for k, v in terms if k == "term"}

    secret_spans = []
    for pat in SECRET_PATTERNS:
        for m in pat.finditer(line):
            secret_spans.append(m.span())
            found.append((m.start(), "secret", m.group(0)))
    for m in KEY_VALUE.finditer(line):
        if is_placeholder(m.group(2)) or overlaps(m.span(), secret_spans):
            continue
        found.append((m.start(), "secret", m.group(0)))

    card_spans = []
    for m in CARD.finditer(line):
        digits = re.sub(r"\D", "", m.group(0))
        if 13 <= len(digits) <= 19 and luhn_ok(digits):
            card_spans.append(m.span())
            found.append((m.start(), "card", m.group(0)))

    for m in SSN.finditer(line):
        found.append((m.start(), "ssn", m.group(0)))
    for m in IBAN.finditer(line):
        found.append((m.start(), "iban", m.group(0)))

    seen_acct = set()
    for w in ACCOUNT_WORD.finditer(line):
        window = line[w.end():w.end() + 40]
        for m in ACCOUNT_DIGITS.finditer(window):
            span = (w.end() + m.start(), w.end() + m.end())
            if span in seen_acct or overlaps(span, card_spans):
                continue
            seen_acct.add(span)
            found.append((span[0], "account", m.group(0)))

    for m in EMAIL.finditer(line):
        if m.group(1).lower() not in owner_domains:
            found.append((m.start(), "email", m.group(0)))

    for m in PHONE.finditer(line):
        if not overlaps(m.span(), card_spans):
            found.append((m.start(), "phone", m.group(0)))

    for kind, value in terms:
        if kind not in ("name", "address"):
            continue
        words = [re.escape(w) for w in value.split()]
        pat = re.compile(r"(?<!\w)" + r"\s+".join(words) + r"(?!\w)", re.IGNORECASE)
        for m in pat.finditer(line):
            found.append((m.start(), kind, m.group(0)))

    found.sort(key=lambda f: f[0])
    return found


def scan(text, terms):
    """[(line number from 1, kind, masked sample)] for everything in text that should not leave."""
    results = []
    for n, line in enumerate(text.splitlines(), 1):
        for _, kind, sample in scan_line(line, terms):
            results.append((n, kind, mask(sample)))
    return results


NOT_TEXT = ('Not a text file. Scan the Markdown draft, or convert it first: '
            'python tools/markitdown/convert.py "<file>"')


def is_binary(path):
    """True for a Word, Excel or zip file (PK), a PDF, or anything with a NUL byte in its first 4 KB."""
    with open(path, "rb") as fh:
        head = fh.read(4096)
    return head[:8].startswith(b"PK") or head[:8].startswith(b"%PDF") or b"\x00" in head


def main(argv):
    if len(argv) != 2:
        print("usage: check.py <file or ->", file=sys.stderr)
        return 2
    try:
        if argv[1] == "-":
            text = sys.stdin.read()
        else:
            if is_binary(argv[1]):
                print(NOT_TEXT)
                return 2
            with open(argv[1], encoding="utf-8", errors="replace") as fh:
                text = fh.read()
    except OSError as err:
        print("cannot read %s: %s" % (argv[1], err), file=sys.stderr)
        return 2
    findings = scan(text, load_terms(TERMS_PATH))
    for n, kind, sample in findings:
        print("line %d: %s: %s" % (n, kind, sample))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
