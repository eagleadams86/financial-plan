# Money Map

Charlie's personal financial planner — the web-app successor to a Numbers
spreadsheet kept since 2011. Live at
**https://eagleadams86.github.io/financial-plan/**

## Your numbers never leave your browser (unless you sign in)

**This repo is public and holds code only — never data.** Everything you see
in the app lives in your browser's localStorage. No account is needed; without
signing in, the only network call the page makes is to the GitHub API for the
"Recent changes" box. **Optional sync**: "Sign in to sync" (Google) mirrors
your data to a private Firestore document in the `financialplan-60c6e`
Firebase project — security rules confine every account to its own document,
sign-in uses Google Identity Services (works on corporate networks that block
firebaseapp.com), and "Delete all data" removes the synced copy too. See
[privacy.html](privacy.html). The import files (`financial-plan-data.json`,
`expected-2026.json`) are gitignored from the very first commit; `git status`
must never show them.

## What it does

- **Budget** — the monthly grid, 2011–present, grouped into **Income,
  Expenses, Transfers and Accounts** sections with per-month subtotals. Each
  row has a type (which section), a projection rule (repeat last month,
  quarterly, average so far, same month last year, interest, per-check ×
  paychecks), and a behaviour (ordinary cash, or a transfer with the Savings /
  Investments / Other-bank accounts — which are renameable and each carry
  their own configurable interest/growth rate). The current year
  is live:
  past months are actuals, future months are estimates that recompute the way
  the spreadsheet's formulas did (trailing averages, same-month-last-year
  electric, dividends from balances, paycheck × count, 7%/yr long-term
  growth). Click any cell to edit; mark a month "entered" to freeze its
  estimates into numbers, like overtyping formulas in Numbers. The Venmo
  ledger and large-purchase list sit under the grid.
- **Everything is editable, everywhere** — click any row (budget categories,
  goals, holdings, trips and their line items, PTO entries, donations, the
  Venmo ledger, the free-form limits tables, the old yearly summaries) to
  change, annotate, or delete it; every table has a ＋ Add button, budget
  rows and list rows reorder with ↑↓, and the free-form tables take spacer
  lines. Row names, trip names and per-year settings are all just fields in
  the same editor.
- **Goals** — savings goals with progress, target dates, required monthly
  saving, the renovations pace check, and end-of-year liquidity.
- **Retirement** — Traditional vs Roth split, Roth IRA contributions,
  comp & bonuses, contribution limits and the MAGI check, holdings.
- **Vacations** — per-trip cost tables and the holidays & PTO planner.
- **Giving** — the Fidelity Charitable fund and the donations log.
- **History** — total liquidity 2011→now and money in vs out per year.
- **Year rollover** — "Start ⟨next year⟩" duplicates the live grid the way
  Charlie used to duplicate the sheet.

## Getting started

**Anyone can just use it** — open the page and press **Start fresh**: it sets
up the current year's budget with a starter set of rows (all renameable,
deletable, reorderable) and every tab's ＋ Add buttons do the rest. No import
needed, no account, and each person's data stays in their own browser — so
sharing the URL shares the app, never the numbers.

Charlie's own one-time migration from the Numbers spreadsheet:

```bash
python3 import_xlsx.py "~/Downloads/Financial Plan.xlsx"
```

Then open the app → **Back up** → **Restore JSON…** → pick
`financial-plan-data.json`. The same Restore path handles ordinary backups —
Export writes `money-map-YYYY-MM-DD.json`, Restore reads it back.

## Architecture

One file — `index.html` — no build step, alongside `theme.css` (byte-copy
from the private claude-theme-pack, the palette source of truth for all apps)
and a vendored `chart.min.js`. Served by GitHub Pages from `main`. State
schema is versioned (`schema: 1`) with a migration slot.

`computeAll()` in `index.html` is the only place numbers are calculated —
every cell, balance, and goal figure derives from stored inputs at render
time; nothing computed is ever persisted.

## Tests

Open `tests.html` on a local server (`python3 -m http.server 8016`) — it runs
the pure functions in the real `index.html` inside a hidden iframe. All
fixtures are synthetic. On this Mac only, if the import files are present, it
additionally diffs the JS engine against the spreadsheet's own cached values
(94 formula cells + 101 balances, at import time they matched exactly). CI
(`.github/workflows/tests.yml`) runs the same page headless on every push.
