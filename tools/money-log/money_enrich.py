"""Categories and recurring charges for money-log.

Category rules live in a small CSV (match, category, subcategory). A rule is a
case-insensitive piece of the description. Rules apply to money out only, so a
rule can never relabel a paycheck or a refund. The first matching rule wins, so
put specific rules above general ones.

Recurring charges are found from the data itself: the same merchant, charged at
least 3 times in at least 3 different months, at a steady amount (most charges
within 15% of the middle amount), at a regular gap of 11 days or more. Everyday
spending (groceries, restaurants, coffee, gas), card payments, transfers and
pay-later installments are left out so the list stays about bills and
subscriptions.

Standard library only.
"""
import csv, datetime, os, re, statistics

EVERYDAY_CATEGORIES = {"groceries", "restaurants", "coffee", "gas", "fast food", "food & dining"}
# Only clear between-account moves and card payments. Bills paid by ACH or online
# ("CITY WATER ACH PMT") and fees ("WIRE TRANSFER FEE") are spending, and a
# matching category rule always beats this guess.
TRANSFER_WORDS = ("payment thank you", "transfer to", "transfer from", "card payment", "credit card pmt")
PAY_LATER_WORDS = ("pay in 4", "pay-in-4", "pay later", "installment")
UNCATEGORIZED = "Uncategorized"


def money(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def norm(s):
    return (s or "").strip().lower()


def load_rules(path):
    rules = []
    if not path or not os.path.exists(path):
        return rules
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            match = norm(row.get("match"))
            if match:
                rules.append({"match": match, "category": (row.get("category") or "").strip(),
                              "subcategory": (row.get("subcategory") or "").strip()})
    return rules


def spend_type(row, rule_matched=False):
    desc, cat = norm(row.get("description")), norm(row.get("category"))
    if cat in {"transfer", "transfers"}:
        return "transfer"
    if not rule_matched and (any(w in desc for w in TRANSFER_WORDS) or cat == "payment"):
        return "transfer"
    if any(w in desc for w in PAY_LATER_WORDS):
        return "pay_later"
    return "spend" if money(row.get("amount")) < 0 else "income"


def categorize(rows, rules):
    """Set category and spend_type on every row. Rules beat the export's own category."""
    out = []
    for raw in rows:
        row = dict(raw)
        row["amount"] = round(money(row.get("amount")), 2)
        matched = False
        if row["amount"] < 0:
            desc = norm(row.get("description"))
            for rule in rules:
                if rule["match"] in desc:
                    row["category"] = rule["category"] or row.get("category", "")
                    if rule["subcategory"]:
                        row["subcategory"] = rule["subcategory"]
                    matched = True
                    break
        row["spend_type"] = spend_type(row, matched)
        if not (row.get("category") or "").strip():
            if row["spend_type"] == "transfer":
                row["category"] = "Transfer"
            else:
                row["category"] = UNCATEGORIZED if row["amount"] < 0 else "Income"
        out.append(row)
    return out


def merchant_key(desc):
    s = re.split(r"des:|conf|indn:|id:", norm(desc))[0]
    s = re.sub(r"[^a-z&' ]", " ", s)  # drop store numbers and dates
    s = re.sub(r"\s+", " ", s).strip()
    return " ".join(s.split()[:3]) or "unknown"


def _date(s):
    return datetime.date.fromisoformat(str(s)[:10])


def _cadence(gap):
    if 24 <= gap <= 38:
        return "monthly"
    if 80 <= gap <= 100:
        return "quarterly"
    if 330 <= gap <= 400:
        return "annual"
    return "irregular"


def _lapse_days(cadence, gap):
    return {"monthly": 60, "quarterly": 150, "annual": 450}.get(cadence, max(60, int(gap * 2)))


def detect_recurring(rows, today=None):
    """Return recurring charges, largest monthly amount first."""
    spends = [r for r in rows if money(r.get("amount")) < 0 and r.get("spend_type") == "spend"
              and norm(r.get("category")) not in EVERYDAY_CATEGORIES]
    if not rows:
        return []
    today = today or max(_date(r["date"]) for r in rows)
    groups = {}
    for r in spends:
        groups.setdefault(merchant_key(r.get("description")), []).append(r)

    found = []
    for key, items in groups.items():
        items.sort(key=lambda r: r["date"])
        if len(items) < 3 or len({r["date"][:7] for r in items}) < 3:
            continue
        amounts = [abs(money(r["amount"])) for r in items]
        mid = statistics.median(amounts)
        if mid <= 0 or len([a for a in amounts if abs(a - mid) / mid <= 0.15]) <= len(amounts) / 2:
            continue
        dates = [_date(r["date"]) for r in items]
        gaps = [(b - a).days for a, b in zip(dates, dates[1:]) if (b - a).days > 0]
        if not gaps:
            continue
        gap = statistics.median(gaps)
        if gap < 11:
            continue
        cadence = _cadence(gap)
        monthly = mid if cadence == "monthly" else mid * 30.44 / gap
        if monthly < 2:
            continue
        lapsed = (today - dates[-1]).days > _lapse_days(cadence, gap)
        found.append({
            "name": items[-1].get("description") or key.title(),
            "category": items[-1].get("category", ""),
            "cadence": cadence,
            "charge": round(mid, 2),
            "monthly": round(monthly, 2),
            "first_seen": dates[0].isoformat(),
            "last_seen": dates[-1].isoformat(),
            "count": len(items),
            "status": "possibly cancelled" if lapsed else "active",
        })
    found.sort(key=lambda r: (-r["monthly"], r["name"].lower()))
    return found
