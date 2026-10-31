"""One offline HTML page for a month: no server, no internet, no scripts, no outside files.

Everything is written into the page as plain HTML and inline CSS, and every value
from the export is escaped. It opens in any browser and works with the network off.
"""
import html

CSS = """
:root{color-scheme:light dark;--bg:#f7f8f5;--panel:#ffffff;--ink:#20231f;--muted:#6f756b;--line:#dfe3d8;--accent:#2f6f73;--warn:#b45f3c}
@media (prefers-color-scheme:dark){:root{--bg:#151714;--panel:#20241f;--ink:#f0f2ec;--muted:#aab0a4;--line:#343a32;--accent:#8ac4bd;--warn:#e0a084}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,"Segoe UI",sans-serif}
header{padding:24px 16px;border-bottom:1px solid var(--line)}h1{margin:0;font-size:24px}h2{font-size:17px;margin:0 0 12px}
main{padding:20px 16px 40px;display:grid;gap:18px;max-width:1000px;margin:0 auto}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px;overflow-x:auto}
.kpi{font-size:26px;font-weight:700}.muted{color:var(--muted)}.warn{color:var(--warn)}
.bar{height:10px;background:var(--line);border-radius:999px;overflow:hidden;margin:4px 0 10px}.fill{height:100%;background:var(--accent)}
.row{display:flex;justify-content:space-between;gap:12px}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:7px 6px;border-bottom:1px solid var(--line)}
th{font-size:12px;color:var(--muted);font-weight:600}.right{text-align:right}
"""


def _m(n):
    return "$" + format(abs(n), ",.2f") if n >= 0 else "-$" + format(abs(n), ",.2f")


def _e(s):
    return html.escape(str(s if s is not None else ""))


def _table(heads, rows, right=()):
    th = "".join('<th class="right">%s</th>' % _e(h) if i in right else "<th>%s</th>" % _e(h)
                 for i, h in enumerate(heads))
    body = "".join("<tr>%s</tr>" % "".join(
        '<td class="right">%s</td>' % c if i in right else "<td>%s</td>" % c for i, c in enumerate(r))
        for r in rows)
    return "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (th, body or "")


def render(month, totals, categories, recurring, month_rows, trend):
    """totals: dict spent/income/net. categories: [(name, total)]. trend: [(month, spent, income)]."""
    top = categories[0][1] if categories else 0
    bars = "".join('<div class="row"><span>%s</span><strong>%s</strong></div>'
                   '<div class="bar"><div class="fill" style="width:%.1f%%"></div></div>'
                   % (_e(name), _m(total), (total / top * 100) if top else 0) for name, total in categories)
    rec_rows = [(_e(r["name"]), _e(r["cadence"]), _m(r["monthly"]), _e(r["last_seen"]),
                 '<span class="warn">possibly cancelled</span>' if r["status"] != "active" else "active")
                for r in recurring]
    trend_rows = [(_e(m), _m(i), _m(s), _m(i - s)) for m, s, i in trend]
    tx_rows = [(_e(r["date"]), _e(r["description"]), _e(r["category"]), _m(r["amount"])) for r in month_rows]
    kpis = "".join('<div class="card"><div class="muted">%s</div><div class="kpi">%s</div></div>' % (k, v) for k, v in (
        ("Spent", _m(totals["spent"])), ("Money in", _m(totals["income"])),
        ("Net", _m(totals["net"])), ("Recurring per month", _m(sum(r["monthly"] for r in recurring if r["status"] == "active")))))
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Money {month}</title>
<style>{css}</style>
</head>
<body>
<header><h1>Money {month}</h1><div class="muted">Built on this computer from a bank export. Nothing here was sent anywhere.</div></header>
<main>
<section class="grid">{kpis}</section>
<section class="card"><h2>Spending by category</h2>{bars}</section>
<section class="card"><h2>Recurring charges</h2>{recurring}</section>
<section class="card"><h2>Month by month</h2>{trend}</section>
<section class="card"><h2>Transactions in {month}</h2>{tx}</section>
</main>
</body>
</html>
""".format(month=_e(month), css=CSS, kpis=kpis, bars=bars or '<p class="muted">No spending this month.</p>',
           recurring=_table(["Charge", "Cadence", "Monthly", "Last seen", "Status"], rec_rows, right=(2,))
           if rec_rows else '<p class="muted">None found yet. It takes three months of charges to spot one.</p>',
           trend=_table(["Month", "Money in", "Spent", "Net"], trend_rows, right=(1, 2, 3)),
           tx=_table(["Date", "Description", "Category", "Amount"], tx_rows, right=(3,)))
