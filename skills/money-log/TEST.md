# Test: money-log

## The ask
"What did I spend last month?"

## The input
A bank CSV export covering three months, with two monthly subscriptions and one repeated row.

## Done looks like
The skill runs `python tools/money-log/money.py` once on the export and reports a monthly summary by category, the recurring charges with their monthly amounts, and an HTML dashboard beside the summary in the `money` folder. Nothing is sent anywhere and no bank login is asked for.
