"""Duplicate handling for money-log.

Two cases, kept apart on purpose:

1. Inside one export: rows with the same date, amount, description and account.
   Two real identical purchases on one day are possible, so these are kept by
   default. With --drop-exact-duplicates, remove_exact() keeps one of each and
   returns the rest so the summary can list every removal.

2. Between the saved ledger and a new export that overlaps it: merge_ledger()
   keeps, for each identical row, the larger of the two counts. Re-exporting a
   month you already loaded adds nothing; a genuinely new row is added.

Standard library only.
"""
import re


def row_key(r):
    desc = re.sub(r"\s+", " ", (r.get("description") or "").strip().lower())
    cents = round(float(r["amount"]) * 100)
    return (r["date"], cents, desc, (r.get("account") or "").strip().lower())


def remove_exact(rows):
    """Return (kept, removed). The first of each identical group is kept."""
    seen, kept, removed = set(), [], []
    for r in rows:
        k = row_key(r)
        if k in seen:
            removed.append(r)
        else:
            seen.add(k)
            kept.append(r)
    return kept, removed


def merge_ledger(ledger_rows, new_rows):
    """Union by count: for each key, keep max(count in ledger, count in new)."""
    def bucket(rows):
        b = {}
        for r in rows:
            b.setdefault(row_key(r), []).append(r)
        return b

    old, new = bucket(ledger_rows), bucket(new_rows)
    merged, added = [], 0
    for k in set(old) | set(new):
        a, b = old.get(k, []), new.get(k, [])
        if len(b) > len(a):
            added += len(b) - len(a)
            merged.extend(a + b[len(a):])
        else:
            merged.extend(a)
    merged.sort(key=lambda r: (r["date"], r.get("description", "")))
    return merged, added
