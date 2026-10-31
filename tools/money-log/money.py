"""money-log: a bank or card CSV export in, a monthly summary and recurring charges out.

    python tools/money-log/money.py <export.csv> [--source "<bank or app name>"] [--month YYYY-MM]

It reads one CSV export, works out its shape, removes repeated rows, adds the rows
to the ledger in the money folder, sorts spending into categories by the rule file,
finds recurring charges, and writes two files:

    money/<YYYY>/<YYYY-MM>-summary.md      month, category, total; recurring charges
    money/<YYYY>/<YYYY-MM>-dashboard.html  the same month as one offline page

No bank connection, no network, no upload. It writes only inside the money folder
(plus a .gitignore there so the folder never goes into git). Standard library only.
"""
import argparse, csv, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import money_adapters as AD  # noqa: E402
import money_dedup as DD  # noqa: E402
import money_enrich as EN  # noqa: E402
import money_dashboard as DB  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))  # tools/money-log/ is two levels below the workspace
RULES_EXAMPLE = os.path.join(HERE, "rules.example.csv")


def fmt(n):
    return format(n, ",.2f")


def read_ledger(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["amount"] = float(r["amount"])
    return rows


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def prepare_money_dir(money_dir):
    os.makedirs(money_dir, exist_ok=True)
    gi = os.path.join(money_dir, ".gitignore")
    if not os.path.exists(gi):
        with open(gi, "w", encoding="utf-8") as f:
            f.write("# Private money records: keep this whole folder out of git.\n*\n")


def month_numbers(rows, month):
    mrows = [r for r in rows if r["date"][:7] == month]
    spent = sum(-r["amount"] for r in mrows if r["amount"] < 0 and r["spend_type"] != "transfer")
    income = sum(r["amount"] for r in mrows if r["amount"] > 0 and r["spend_type"] != "transfer")
    transfers = sum(abs(r["amount"]) for r in mrows if r["spend_type"] == "transfer")
    cats = {}
    for r in mrows:
        if r["amount"] < 0 and r["spend_type"] != "transfer":
            cats[r["category"]] = cats.get(r["category"], 0) + -r["amount"]
    categories = sorted(((k, round(v, 2)) for k, v in cats.items()), key=lambda kv: (-kv[1], kv[0]))
    return mrows, categories, {"spent": round(spent, 2), "income": round(income, 2),
                               "net": round(income - spent, 2), "transfers": round(transfers, 2)}


def summary_markdown(month, source, mrows, categories, totals, recurring, removed):
    dates = sorted(r["date"] for r in mrows)
    lines = ["# Money summary: %s" % month, ""]
    lines.append("From %s. Covers %s to %s, %d transactions." % (
        source, dates[0] if dates else month, dates[-1] if dates else month, len(mrows)))
    lines += ["", "## Spending by category", "", "| Month | Category | Total |", "|---|---|---:|"]
    for name, total in categories:
        lines.append("| %s | %s | %s |" % (month, name.replace("|", "/"), fmt(total)))
    lines.append("| %s | **All spending** | **%s** |" % (month, fmt(totals["spent"])))
    lines += ["", "Money in: %s. Spent: %s. Net: %s. Transfers and card payments, not counted: %s." % (
        fmt(totals["income"]), fmt(totals["spent"]), fmt(totals["net"]), fmt(totals["transfers"]))]
    lines += ["", "## Recurring charges", ""]
    if recurring:
        lines += ["| Charge | Cadence | Monthly amount | Last seen | Status |", "|---|---|---:|---|---|"]
        for r in recurring:
            lines.append("| %s | %s | %s | %s | %s |" % (r["name"].replace("|", "/"), r["cadence"],
                                                         fmt(r["monthly"]), r["last_seen"], r["status"]))
    else:
        lines.append("None found yet. It takes charges in three different months to spot one.")
    unc = {}
    for r in mrows:
        if r["category"] == EN.UNCATEGORIZED:
            unc[r["description"]] = unc.get(r["description"], 0) + -r["amount"]
    if unc:
        lines += ["", "## No category yet", "", "Add a line to the rule file for the biggest ones.", ""]
        for desc, total in sorted(unc.items(), key=lambda kv: -kv[1])[:10]:
            lines.append("- %s: %s" % (desc, fmt(total)))
    removed = [r for r in removed if r["date"][:7] == month]
    if removed:
        lines += ["", "## Repeated rows removed", "",
                  "From this export: same date, amount, description and account. Kept one of each.", ""]
        for r in removed:
            lines.append("- %s %s %s" % (r["date"], r["description"], fmt(r["amount"])))
    lines += ["", "Built on this computer. Nothing was sent anywhere. "
              "Run outbound-check on this file before sharing it.", ""]
    return "\n".join(lines)


def run(export, source=None, month=None, fmt_id=None, rules_path=None, money_dir=None, drop_exact_duplicates=False):
    money_dir = money_dir or os.path.join(ROOT, "money")
    if not os.path.isfile(export):
        raise SystemExit("No such file: %s" % export)
    if month and not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        raise SystemExit("--month must look like 2026-09")

    headers, raw = AD.read_csv(export)
    aid = fmt_id or AD.detect_adapter(headers)
    if not aid or aid not in AD.ADAPTERS:
        raise SystemExit("Could not tell what kind of export this is. Columns: %s\n"
                         "Pick one with --format: %s" % (", ".join(headers[:8]), ", ".join(AD.DETECT_ORDER)))
    source = source or os.path.splitext(os.path.basename(export))[0]
    rows = AD.apply_adapter(headers, raw, aid, source_label=source)
    if not rows:
        raise SystemExit("No transactions read from %s (shape: %s)." % (export, aid))
    removed = []
    if drop_exact_duplicates:
        rows, removed = DD.remove_exact(rows)

    prepare_money_dir(money_dir)
    if not rules_path:
        rules_path = os.path.join(money_dir, "rules.csv")
        if not os.path.exists(rules_path):
            shutil.copyfile(RULES_EXAMPLE, rules_path)
    ledger_path = os.path.join(money_dir, "ledger.csv")
    ledger, added = DD.merge_ledger(read_ledger(ledger_path), rows)
    write_csv(ledger_path, ledger, AD.CANON_FIELDS)

    allrows = EN.categorize(ledger, EN.load_rules(rules_path))
    month = month or max(r["date"] for r in rows)[:7]
    recurring = EN.detect_recurring(allrows)
    mrows, categories, totals = month_numbers(allrows, month)
    if not mrows:
        raise SystemExit("No transactions in %s. The ledger covers %s to %s." % (
            month, allrows[0]["date"], allrows[-1]["date"]))

    out_dir = os.path.join(money_dir, month[:4])
    os.makedirs(out_dir, exist_ok=True)
    summary_path = os.path.normpath(os.path.join(out_dir, "%s-summary.md" % month))
    dash_path = os.path.normpath(os.path.join(out_dir, "%s-dashboard.html" % month))
    with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(summary_markdown(month, source, mrows, categories, totals, recurring, removed))
    months = sorted({r["date"][:7] for r in allrows})
    trend = []
    for m in months:
        _, _, t = month_numbers(allrows, m)
        trend.append((m, t["spent"], t["income"]))
    with open(dash_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(DB.render(month, totals, categories, recurring, sorted(mrows, key=lambda r: r["date"]), trend))
    return {"shape": aid, "read": len(rows) + len(removed), "removed": removed, "added": added,
            "month": month, "categories": categories, "totals": totals, "recurring": recurring,
            "summary": summary_path, "dashboard": dash_path, "ledger": ledger_path, "rules": rules_path}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Bank or card CSV export in, monthly summary and recurring charges out.")
    ap.add_argument("export", help="the CSV file the bank, card or app exported")
    ap.add_argument("--source", help="bank or app name, used as the account name")
    ap.add_argument("--month", help="YYYY-MM to summarize (default: the latest month in the export)")
    ap.add_argument("--format", dest="fmt_id", help="export shape when detection fails: " + ", ".join(AD.DETECT_ORDER))
    ap.add_argument("--rules", help="rule file (default: money/rules.csv, made from the example on first run)")
    ap.add_argument("--money-dir", help="where the money folder is (default: money/ in the workspace)")
    ap.add_argument("--drop-exact-duplicates", action="store_true",
                    help="remove identical rows inside this export (same date, amount, description, account)")
    a = ap.parse_args(argv)
    res = run(a.export, a.source, a.month, a.fmt_id, a.rules, a.money_dir, a.drop_exact_duplicates)
    t = res["totals"]
    print("Export shape: %s. Read %d rows, removed %d repeated, added %d new to the ledger." % (
        res["shape"], res["read"], len(res["removed"]), res["added"]))
    print("%s: spent %s, money in %s, net %s, %d categories." % (
        res["month"], fmt(t["spent"]), fmt(t["income"]), fmt(t["net"]), len(res["categories"])))
    print("Recurring: %s" % ("; ".join("%s %s/month" % (r["name"], fmt(r["monthly"])) for r in res["recurring"])
                             or "none found yet"))
    print("Summary:   %s" % res["summary"])
    print("Dashboard: %s" % res["dashboard"])


if __name__ == "__main__":
    main()
