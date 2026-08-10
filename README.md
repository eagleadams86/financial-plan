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
  Expenses, Transfers and Accounts** sections, with per-month subtotals (a
  section holding a single row skips its subtotal) and a year-total column
  pinned to the right. Each row has a type (which section), a projection rule
  (repeat last month, cycle, average so far, **average of last year**, same
  month last year, interest, per-check × paychecks), and a behaviour: ordinary
  money, a transfer with another account, or a pass-through that never touches
  the main account. **Accounts are a list you own** — add as many as you like,
  each with its own name, growth rate, a choice of which account that interest
  is paid into, and a start that follows your data: an account is tracked from the first month
  you put a figure in, earlier months stay blank rather than zero, and typing
  into one of them moves the start back. The current year is live: months you've
  entered are actuals, everything after them is an estimate that recomputes the
  way the spreadsheet's formulas did — **the account balances included**, so the
  current month reads as the estimate it is until you mark it entered, rather
  than looking like money already counted. Every figure says what it's made of,
  subtotals and year totals too: plain for what happened, italic for a
  projection, dashed for a total spanning both. Click any cell to edit — or **split a month into several
  amounts**, each actual or estimated on its own, totalled on save. A row paid
  per check opens that way already, one line per payday with the amount filled
  in, so correcting a single cheque — a bonus, a missed shift — is one box to
  type in rather than a lump sum to break apart first. A month's
  balance cell shows what the account earned that month and lets you override
  the interest or add a dividend — correct either and the balance recomputes
  around it, in whichever account the money is paid into, for that month and
  every month after. **Every note you've written anywhere in a year is gathered
  into one collapsible list at the foot of it** — cells, split parts, balances
  and rows — each one clickable to jump back to what it was about; the list
  isn't there at all in a year you haven't annotated, and it stays open or shut
  the way you left it, on this device, across years and refreshes. They're
  grouped by month and laid out across the width of the card, so a year's worth
  reads at a glance instead of running down one long strip. Mark a month "entered" to freeze its
  estimates into numbers, like overtyping formulas in Numbers. A finished year
  can be **converted to a yearly summary** (permanent — the History charts
  carry on unchanged), or deleted outright. A finished year holds its account
  balances as figures you stated at the time rather than a chain to recompute,
  and an account you've since closed stops at its last month instead of
  following you into later years.
- **Everything is editable, everywhere** — click any row (budget categories,
  accounts, goals, holdings, retirement accounts, trips and their line items,
  PTO entries, donations, the old yearly summaries) to change, annotate, or
  delete it; every table has a ＋ Add button, rows reorder with ↑↓, and each
  editor shows only the settings the current choice actually uses. Clicking
  outside any dialog closes it without saving, and a small ⓘ beside a figure
  explains the arithmetic behind it. The budget grid is keyboard-operable too:
  Tab into it, move between cells with the arrow keys, and press Enter to edit
  the one you're on.
- **Goals** — savings goals that add up whichever accounts you tick, so
  splitting an account is a matter of ticking the new ones. Each goal counts
  its accounts up to the target, in full, or only what another goal hasn't
  already claimed. Plus progress, target dates, required monthly saving,
  end-of-year liquidity, and a pace check that follows whichever goal is next:
  the soonest deadline you haven't met yet.
- **Retirement** — Traditional vs Roth split; retirement accounts with a type
  (401(k), Roth IRA, HSA…) and their own contribution history, so nothing
  about Roth IRAs is special-cased; a **401(k) limit calculator** and a **Roth
  IRA income (MAGI) calculator** that both recompute as you change the figures;
  and a projection of where the balances are heading at an assumed return.
  Contributions are rows you click to edit, one per year and account.
- **Compensation** — where comp stands, raises over time (the raise in dollars
  and how the salary actually moved since last year, which differ whenever
  something lands mid-year), and bonuses by year — one figure per year, editable
  from the comp year or from the bonus table, whichever you happen to have open,
  and shown both in dollars and as **a percentage of the salary that year opened
  on** — the pay it was earned against, which is the figure a payroll system
  quotes — typed either way round. A year takes the raise either
  way round: **type the percentage and the salary it comes to fills itself in,
  or type the new salary and the percentage does** — whichever your letter
  happened to give you.
- **Investments** — one pane per place you hold investments (add, rename and
  reorder them), with optional **automatic price lookups** (Alpha Vantage; free
  key kept on the device, cached six hours, and every price still editable by
  hand).
- **Vacations** — per-trip cost tables grouped into one row per year, newest
  first, reorderable within a year. A new trip starts from the lines most trips
  need (airfare, stay, transport, excursions, food, tips, spa) or from nothing,
  your choice. Each line tracks what's paid, what's credited and what's still
  due, with a **✓ Paid** button that settles the rest in one click. Plus the
  holidays & PTO planner, with from/to dates.
- **Giving** — the Fidelity Charitable fund and the donations log.
- **History** — total liquidity 2011→now, and money in vs out for every one of
  those years, with the interest your accounts earned counted as money in so the
  two charts tell the same story. The oldest years come from bi-weekly sheets
  whose rows the importer couldn't tell apart; they're sorted out on load, and
  any row it reads wrong is one click to fix.
- **Year rollover** — "Build ⟨next year⟩" duplicates the live grid the way
  Charlie used to duplicate the sheet. Build it as early as you like to see
  where the plan is heading: a year that hasn't arrived shows nothing but
  projections, and they start from the year before rather than a blank page —
  "repeat last month" rows open at December, "average so far" rows at last
  year's average, a cycle bill keeps its beat so an annual renewal still lands
  in its own month, and the paycheck counts repeat last year's pattern — which
  keeps the year's total right if you're paid fortnightly, where assuming two a
  month would lose you a fortnight's pay. Each hands over as soon as you type a
  real month in.
  It keeps tracking the current year as that changes — **rows included**: add a
  row to this year, retire one, rename it, change its rule or move it, and next
  year is changed to match, so a year you built in advance never quietly
  describes a budget you no longer have. Anything you set up in next year alone
  is left alone. And it doesn't become the current year — Goals, History and
  the rest carry on reading this one — until 1 January, or until you mark
  December entered.

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

`migrate_local_data.py` does the one thing the app deliberately won't do to
your data by itself: it takes the next year back out of the live grid. The
spreadsheet ran 24 months so it could see a year ahead; the app ends a year at
December and starts the next with "Start ⟨year⟩". So the hand-typed next-year
months go and the grid comes back to twelve — while next year's paycheck
counts are kept, because the rollover carries them into the new year. It
writes a new file beside the input and never modifies the original. (Folding a
year into a summary is a per-year decision with a button on the year itself —
the script never does it for you.)

```bash
python3 migrate_local_data.py financial-plan-data.json
```

## Architecture

The icon is drawn by `make_favicon.py` (Pillow): the inline SVG in the page is
what browsers use, `favicon.ico` is the fallback a browser fetches on its own,
and the script keeps the two the same picture rather than leaving a binary
nobody can review in a diff.

One file — `index.html` — no build step, alongside `theme.css` (byte-copy
from the private claude-theme-pack, the palette source of truth for all apps)
and a vendored `chart.min.js`. Served by GitHub Pages from `main`. State
schema is versioned (`schema: 2`); every entry point runs the payload through
`coerceShape()`, whose upgrades are presence-based and safe to run twice.

`computeAll()` in `index.html` is the only place numbers are calculated —
every cell, balance, and goal figure derives from stored inputs at render
time; nothing computed is ever persisted.

## Tests

Open `tests.html` on a local server (`python3 -m http.server 8016`) — it runs
the pure functions in the real `index.html` inside a hidden iframe. All
fixtures are synthetic. On this Mac only, if the import files are present, it
additionally diffs the JS engine against the spreadsheet's own cached values
for the live year's own months. (Months beyond that are now a projection the
app works out from the rules, where the spreadsheet had them typed in, so the
two are not meant to agree.) CI
(`.github/workflows/tests.yml`) runs the same page headless on every push.
