"""Export shapes for money-log: turn any bank, card or budgeting-app CSV into one row shape.

Every export uses its own column names, date formats and sign rules. An adapter is a
small dict that says how one export shape maps onto the canonical row below. Add a
new shape by adding one dict to ADAPTERS and its id to DETECT_ORDER.

Canonical row:
    date         YYYY-MM-DD
    description  merchant or memo text
    amount       signed number; NEGATIVE = money out, POSITIVE = money in
    account      account or card name
    category     category the export already had (may be blank)
    subcategory  finer category (may be blank)
    source       which export the row came from

Standard library only. Reads local files; never touches the network.
"""
import csv, datetime, io, re

CANON_FIELDS = ["date", "description", "amount", "account", "category", "subcategory", "source"]

# signature: lowercase header words that must all appear for auto-detection.
# sign: "as_is"       negative already means money out
#       "invert"      the export shows purchases as positive, so flip it
#       "two_columns" separate out/in (or debit/credit) columns, or a type column
ADAPTERS = {
    "card_positive_spend": {
        "label": "Card export where purchases are positive (Transaction Date, Merchant, Amount (USD))",
        "signature": ["transaction date", "merchant", "amount (usd)"],
        "date": "Transaction Date", "desc": "Merchant", "amount": "Amount (USD)",
        "category": "Category", "sign": "invert",
    },
    "app_type_column": {
        "label": "Budgeting app export with a Transaction Type column (debit or credit)",
        "signature": ["date", "description", "amount", "transaction type"],
        "date": "Date", "desc": "Description", "amount": "Amount",
        "category": "Category", "account": "Account Name",
        "type_col": "Transaction Type", "type_debit_values": ["debit"],
        "sign": "two_columns",
    },
    "app_outflow_inflow": {
        "label": "Budgeting app register with Payee, Outflow and Inflow columns",
        "signature": ["date", "payee", "outflow", "inflow"],
        "date": "Date", "desc": "Payee", "category": "Category",
        "account": "Account", "outflow": "Outflow", "inflow": "Inflow",
        "sign": "two_columns",
    },
    "app_merchant_account": {
        "label": "Budgeting app export with Date, Merchant, Category, Account, Amount",
        "signature": ["date", "merchant", "category", "account", "amount"],
        "date": "Date", "desc": "Merchant", "amount": "Amount",
        "category": "Category", "account": "Account", "sign": "as_is",
    },
    "app_name_account": {
        "label": "Budgeting app export with date, name, amount, category, account",
        "signature": ["date", "name", "amount", "category", "account"],
        "date": "date", "desc": "name", "amount": "amount",
        "category": "category", "account": "account", "sign": "as_is",
    },
    "bank_debit_credit": {
        "label": "Bank export with Debit and Credit columns",
        "signature": ["date", "debit", "credit"],
        "date": "Date", "desc": "Description",
        "debit": "Debit", "credit": "Credit", "sign": "two_columns",
    },
    "bank_amount": {
        "label": "Bank export with one signed Amount column (Date, Description, Amount)",
        "signature": ["date", "amount"],
        "date": "Date", "desc": "Description", "amount": "Amount",
        "category": "Category", "sign": "as_is",
    },
}

# Most specific first; the first shape whose signature matches wins.
# (A longest-signature rule misread type-column exports as name/account ones.)
DETECT_ORDER = ["card_positive_spend", "app_type_column", "app_outflow_inflow",
                "app_merchant_account", "app_name_account", "bank_debit_credit", "bank_amount"]

# Header variants, so "Posting Date" still maps to date.
ALIASES = {
    "date": ["date", "transaction date", "posting date", "posted date", "trans date"],
    "desc": ["description", "merchant", "name", "payee", "memo", "details", "transaction"],
    "amount": ["amount", "amount (usd)", "amt"],
    "category": ["category", "categories"],
    "subcategory": ["subcategory", "sub category", "sub-category", "detailed category"],
    "account": ["account", "account name", "card", "account name/number"],
    "debit": ["debit", "withdrawal", "withdrawals", "money out"],
    "credit": ["credit", "deposit", "deposits", "money in"],
    "outflow": ["outflow"],
    "inflow": ["inflow"],
    "type_col": ["transaction type", "type"],
}


def _norm(s):
    return (s or "").strip().lower()


def detect_adapter(headers):
    """Return the best-matching adapter id for a list of CSV headers, or None."""
    hset = {_norm(h) for h in headers}
    for aid in DETECT_ORDER:
        if all(any(s in h for h in hset) for s in ADAPTERS[aid]["signature"]):
            return aid
    return None


def _find_col(headers, wanted, field):
    hmap = {_norm(h): h for h in headers if h}
    if wanted and _norm(wanted) in hmap:
        return hmap[_norm(wanted)]
    for alias in ALIASES.get(field, []):
        if alias in hmap:
            return hmap[alias]
    return None


def parse_amount(raw):
    s = str(raw if raw is not None else "").strip()
    if not s:
        return None
    neg = s.startswith("(") and s.endswith(")")  # (123.45) is an accounting negative
    s = s.replace("(", "").replace(")", "").replace("$", "").replace(",", "").replace("USD", "").strip()
    if s in ("", "-", "--"):
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


_DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%Y/%m/%d",
                 "%b %d, %Y", "%d %b %Y", "%m/%d/%Y %H:%M", "%Y-%m-%dT%H:%M:%S"]


def parse_date(raw):
    """US exports first: 03/04/2026 reads as March 4."""
    s = str(raw or "").strip()
    if not s:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return "%s-%s-%s" % m.groups()
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", s)
    if m:
        mo, da, yr = m.groups()
        yr = ("20" + yr) if len(yr) == 2 else yr
        return "%s-%02d-%02d" % (yr, int(mo), int(da))
    return None


def apply_adapter(headers, rows, adapter_id, source_label="", account_override=None):
    """Convert raw rows (dicts) into canonical rows using one adapter."""
    a = ADAPTERS[adapter_id]
    col = {f: _find_col(headers, a.get(f), f) for f in (
        "date", "desc", "amount", "category", "subcategory", "account",
        "debit", "credit", "outflow", "inflow", "type_col")}
    sign = a.get("sign", "as_is")
    debit_vals = [v.lower() for v in a.get("type_debit_values", [])]

    def get(r, f):
        c = col[f]
        return (r.get(c) or "").strip() if c else ""

    out = []
    for r in rows:
        date = parse_date(get(r, "date"))
        if not date:
            continue
        amount = None
        if sign == "two_columns":
            if col["outflow"] or col["inflow"]:
                amount = (parse_amount(get(r, "inflow")) or 0) - abs(parse_amount(get(r, "outflow")) or 0)
            elif col["debit"] or col["credit"]:
                amount = (parse_amount(get(r, "credit")) or 0) - abs(parse_amount(get(r, "debit")) or 0)
            elif col["type_col"] and col["amount"]:
                v = parse_amount(get(r, "amount"))
                if v is not None:
                    amount = -abs(v) if _norm(get(r, "type_col")) in debit_vals else abs(v)
        else:
            v = parse_amount(get(r, "amount"))
            if v is not None:
                amount = -v if sign == "invert" else v
        if amount is None:
            continue
        cat, sub = get(r, "category"), get(r, "subcategory")
        if not sub and ">" in cat:  # "Food > Restaurants > Fast Food"
            parts = [p.strip() for p in cat.split(">") if p.strip()]
            cat, sub = (parts[0] if parts else cat), " / ".join(parts[1:])
        out.append({
            "date": date,
            "description": get(r, "desc"),
            "amount": round(amount, 2),
            "account": account_override or get(r, "account") or source_label,
            "category": cat,
            "subcategory": sub,
            "source": source_label or adapter_id,
        })
    return out


def read_csv(path):
    """Read a CSV, skipping leading junk lines before the real header."""
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        text = f.read()
    lines = text.splitlines()
    start = 0
    for i, ln in enumerate(lines[:15]):
        low = ln.lower()
        if "date" in low and any(w in low for w in ("amount", "debit", "outflow", "merchant")):
            start = i
            break
    reader = csv.DictReader(io.StringIO("\n".join(lines[start:])))
    rows = list(reader)
    return reader.fieldnames or [], rows
