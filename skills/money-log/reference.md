# money-log reference

## The row every export becomes

| field | meaning |
|---|---|
| `date` | `YYYY-MM-DD` |
| `description` | merchant or memo |
| `amount` | signed: negative is money out, positive is money in |
| `account` | the `--source` name, or the account column when the export has one |
| `category`, `subcategory` | what the export already said (may be blank); a hierarchy like `Food > Restaurants` is split |
| `source` | which export the row came from |

The sign is the contract everything else depends on. After the first run on a new kind of export, open the summary and check that purchases count as spending and paychecks as money in. A flipped sign is the most common import mistake; the fix is `--format` with the right shape.

## Export shapes it reads

Detected from the column headers; the first shape that matches wins.

| shape | columns it looks for | sign |
|---|---|---|
| `card_positive_spend` | Transaction Date, Merchant, Amount (USD) | purchases are positive, so flipped |
| `app_type_column` | Date, Description, Amount, Transaction Type | debit means money out |
| `app_outflow_inflow` | Date, Payee, Outflow, Inflow | outflow is money out |
| `app_merchant_account` | Date, Merchant, Category, Account, Amount | negative is money out |
| `app_name_account` | date, name, amount, category, account | negative is money out |
| `bank_debit_credit` | Date, Debit, Credit | debit is money out |
| `bank_amount` | Date, Description, Amount | negative is money out |

Header variants are accepted ("Posting Date" for Date, "Withdrawal" for Debit, "Deposit" for Credit, and so on). Junk lines above the header row, dollar signs, commas and (123.45) style negatives are handled. Dates are read US style first: 03/04/2026 is March 4.

## Adding a new shape

If an export is not recognized, add one entry to `ADAPTERS` in `tools/money-log/money_adapters.py` and its id to `DETECT_ORDER`, above any shape it could be mistaken for. Example for `Posted Date, Payee, Withdrawal, Deposit, Running Balance`:

```python
"my_bank": {
    "label": "My bank checking export",
    "signature": ["posted date", "withdrawal", "deposit"],
    "date": "Posted Date", "desc": "Payee",
    "debit": "Withdrawal", "credit": "Deposit", "sign": "two_columns",
},
```

## Repeated rows

- **Inside one export:** rows with the same date, amount, description and account are kept once, and each removal is listed in the summary. Banks repeat a row when a pending charge posts. If the person really bought the same thing twice on one day, run again with `--keep-duplicates`.
- **Between exports:** the ledger keeps, for each identical row, the larger of the two counts. Loading September twice adds nothing; a new row is added. Use the same `--source` name for the same account every time, or the same rows count as a second account.

## Recurring charges, exactly

A merchant (its description with store numbers dropped) is recurring when it has at least 3 charges, in at least 3 different months, most of them within 15% of the middle amount, with a middle gap of at least 11 days. The gap sets the cadence: 24 to 38 days monthly, 80 to 100 quarterly, 330 to 400 annual, anything else irregular. The monthly amount is the charge itself for a monthly charge, and spread to a month for the others. Charges under 2 dollars a month are dropped.

Left out on purpose: groceries, restaurants, coffee and gas (a habit, not a bill), transfers and card payments, and pay-later installments. A charge unseen for longer than its cadence allows (60 days for monthly) is marked "possibly cancelled".

## A monthly routine

1. Early each month, the person exports the last month or two from each account.
2. Run the command once per export, each with its own `--source`.
3. Add rules for the biggest lines under "No category yet" and run once more.
4. Read back the summary. Keep the exports: the ledger can always be rebuilt by running them again into an empty money folder.
