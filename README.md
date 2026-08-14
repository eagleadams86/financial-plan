# Financial Plan

Charlie's personal financial planner — the web-app successor to a Numbers
spreadsheet kept since 2011. Live at
**https://eagleadams86.github.io/financial-plan/**

## Your Numbers Never Leave Your Browser (Unless You Sign In)

**This repo is public and holds code only — never data.** Everything you see
in the app lives in your browser's localStorage. No account is needed; without
signing in, the only network call the page makes is to the GitHub API for the
"Recent changes" box. **Read-only share links** carry their figures inside the
link's own fragment, which is never sent to any server — creating one and
opening one both upload nothing. **Optional sync**: "Sign in to sync" (Google) mirrors
your data to a private Firestore document in the `financialplan-60c6e`
Firebase project — security rules confine every account to its own document,
sign-in uses Google Identity Services (works on corporate networks that block
firebaseapp.com), and "Delete all data" empties the synced copy too. See
[privacy.html](privacy.html). The import files (`financial-plan-data.json`,
`expected-2026.json`) are gitignored from the very first commit; `git status`
must never show them. Since the Household tab arrived, a backup file or a
screenshot can also carry family members' names and birth months, children's
included — treat those the way you treat the figures.

## What It Does

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
  into one of them moves the start back. One account is the **main account** —
  everything ordinary lands there, and transfers and pass-throughs are both
  described against it. Open an account to nominate a different one if your
  banking moves; only one can hold it, so ticking the box moves it. An account
  you stop using can be **closed** from the month it last held anything, so it
  drops out of Total instead of carrying its final balance forward for ever.
  A row that earns interest **names the accounts it earns on**, and any income
  row can be marked as pay so the giving percentages count it. Giving two accounts **exactly the same
  name** says they are the same account under different labels — years of
  history imported under drifting names fold into one row, carrying every
  balance with them. It refuses if both hold a figure in the same month, since
  that would mean losing one. The current year is live: months you've
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
  balance cell reconciles as you type — say what an account really holds and it
  tells you how far that is from what the plan expected, or confirms the two
  agree. It also shows what the account earned that month and lets you override
  the interest or add a dividend — correct either and the balance recomputes
  around it, in whichever account the money is paid into, for that month and
  every month after. **Every note you've written anywhere in a year is gathered
  into a box of its own under the budget** — cells, split parts, balances
  and rows — each one clickable to jump back to what it was about; the box
  isn't there at all in a year you haven't annotated. They're
  grouped by month and laid out across the width of the card, so a year's worth
  reads at a glance instead of running down one long strip. Mark a month "entered" to freeze its
  estimates into numbers, like overtyping formulas in Numbers. A finished year
  can be **converted to a yearly summary** (permanent — the History charts
  carry on unchanged, and each account keeps its end-of-year balance as a
  balance row), or deleted outright. A finished year holds its account
  balances as figures you stated at the time rather than a chain to recompute,
  and an account you've since closed stops at its last month instead of
  following you into later years.
- **The years run across the top** — the way the sheet tabs did in Numbers,
  newest first, with the one you're reading drawn as a filled pill. Drag or
  swipe the strip sideways, or use the ‹ › arrows at its right end, which grey
  out once you reach an end and vanish altogether when every year already fits.
  Click a year to open it; from the keyboard, one Tab lands on the strip and
  the left and right arrow keys walk along it (Home for the newest year, End
  for the oldest). A year kept as a yearly summary is set in italics, one built
  before it has started is underlined with dots, and hovering either says which
  in words.
- **Zoom** — scale the whole app from the header in quarter steps, or type an
  exact percentage in Preferences (50–200%). It belongs to the device you set
  it on: never synced, never in a backup, so a laptop and a desk monitor can
  each have the size that suits them.
- **Budget rows drag into place** — grab a row's name and move it up or down
  within its own section, the same way the tabs rearrange. The order follows
  into the years you've built ahead, so two grids stay readable side by side.
  (Sorting alphabetically turns dragging off, since that order isn't yours to
  arrange; the ↑↓ buttons in a row's editor still work everywhere.) The account
  rows drag too, in their own block — and since accounts are one list rather
  than one per year, that order holds across every year of the plan.
- **The tabs are yours to arrange** — drag one anywhere along the bar (with a
  mouse or a finger), or hold Alt and use the arrow keys. The order is saved and
  follows you to your other devices.
- **Every box folds up** — click any card's heading (the shaded strip across
  the top of it) and the card collapses to that strip, so a tab can be trimmed
  down to the parts you actually read. What you fold is remembered across
  refreshes and, if you're signed in, follows you to your other devices. The
  welcome card is the one exception: hiding the page that explains what the app
  is would be a poor greeting. A box you fold in one year stays folded in the
  next, and anything new is open until you say otherwise.
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
  the soonest deadline you haven't met yet. Its **Where the Total Is Heading**
  line goes **dashed the moment it passes the month you've entered through** —
  so a month the plan has merely worked out never reads as one that happened,
  whether it's next month or a year you've built ahead.
- **Household** — who the plan is for: a partner, your children. Each person
  has a role, an optional birth month and (for an adult) a retirement age, and
  their age, retirement year and the month a child turns 18 are all **worked
  out rather than stored**, so none of it goes stale. Naming people unlocks the
  rest: every account can say whose it is — theirs, yours, **Joint**, or not
  said — and the budget grid grows a subtotal per person just above Total.
  Every account lands in exactly one of those rows (the unassigned gather under
  "Unassigned"), so **the subtotals always add up to Total**. A savings goal can
  say which child it is for, which files it under them here and suggests their
  18th birthday as its target date — a starting point you type straight over.
  Nothing on this tab changes a single figure the budget computes; owner is a
  way of reading the plan, not an input to it. The whole tab stays out of the
  way until you add someone.
- **Retirement** — Traditional vs Roth split, with a per-person breakdown once
  there are two of you; retirement accounts with a type
  (401(k), Roth IRA, HSA…), an owner, and their own contribution history, so nothing
  about Roth IRAs is special-cased; a **401(k) limit calculator per earner**
  (that limit is per person) and a **Roth
  IRA income (MAGI) calculator** that counts both incomes when you file jointly;
  both recompute as you change the figures;
  and a projection of where the balances are heading at an assumed return.
  Contributions are rows you click to edit, one per year and account.
  The thresholds stay figures **you** type: they move every year and differ by
  filing status, and the app deliberately keeps no tax tables.
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
  reorder them), with optional **automatic price lookups** (Twelve Data; free
  key kept on the device, cached six hours, and every price still editable by
  hand). Shares, ETFs and **mutual funds** are all quoted — a fund strikes one
  price a day after the close, so its figure is the last published NAV rather
  than a live one. The free tier allows 800 lookups a day and eight a minute;
  once the supplier says it has no price for a holding, that answer is
  remembered for the day rather than spending the allowance on the same
  question at every visit. Prices top themselves up automatically when they are
  more than six hours old; the **Refresh prices** button ignores that and
  fetches everything on the spot. Open a holding and its Price box says where
  that number came from — plus what the holding is worth and how much of the
  account it is, both keeping up as you type — — fetched and when, typed over a fetched one, or never
  looked up — since the line above the tables can only report the oldest fetch
  across the whole table.
- **Vacations** — per-trip cost tables grouped into one row per year, newest
  first, reorderable within a year. A new trip starts from the lines most trips
  need (airfare, stay, transport, excursions, food, tips, spa) or from nothing,
  your choice. Each line tracks what's paid, what's credited and what's still
  due, with a **✓ Paid** button that settles the rest in one click. Plus the
  holidays & PTO planner, with from/to dates.
- **Giving** — the donations log, each one filed under the year of its date:
  date one in any year, past or future, and that year gets its own table, which
  appears when it has something in it and goes when it doesn't. Plus a
  donor-advised fund's holdings, for those who have one — a Preferences switch,
  since plenty of people don't, and donations are tracked either way. Each
  donation carries the **event** it was given through — a walk, a ride, an
  appeal — beside the foundation receiving it, and is either done or
  **planned**: a planned one reads in italics, stays
  out of the year's totals, and is counted up separately as what's still to go.
  Every year shows what its giving **came to as a share of income** — of gross
  comp, and of take-home pay — on meters drawn against one shared scale, so the
  years compare with each other at a glance. Once a second year has something in
  it, a chart appears above them: dollars given as bars, both percentages as
  lines over the top. Given counts what left your own accounts (fund deposits
  and cash gifts); a grant out of the fund isn't counted twice.
- **History** — total liquidity 2011→now, and money in vs out for every one of
  those years, with the interest your accounts earned counted as money in so the
  two charts tell the same story. Under them, **what you actually spent each
  year**: the expense rows alone, so money swept into savings or moved between
  your own accounts doesn't read as a heavy year — each bar is the year's
  Expenses total from the Budget tab, with a dotted line across the years
  already recorded to say what's usual, and a hover giving the change on the
  year before. The oldest years come from bi-weekly sheets
  whose rows the importer couldn't tell apart; they're sorted out on load, and
  any row it reads wrong is one click to fix. Those years have no Income /
  Expenses / Transfers split to read, so their spending bar counts everything
  the old sheets recorded going out, and the note under the chart says so.
- **Share a read-only link** — show someone part of the plan without giving them
  an account, a file or edit rights. You pick which tabs go in and how many
  years go with them; the whole payload rides in the link's `#fragment`, so
  nothing is uploaded, nothing is stored on the reader's device, and whatever
  they already had saved in their own browser is untouched. People's names are
  replaced with "Adult 1" and "Child 1" unless you tick the box, and your
  written notes stay out unless you ask for them — the two most personal things
  in the plan are the two that leave by default, and so are the years you've
  built ahead — a projection is a guess about money you don't have yet, and
  handing someone one is a different claim from showing them what happened.
  (A year stops counting as a projection the moment it takes over as the real
  one, so that box has nothing to hold back once it has.) The dialog says what a
  link costs in characters, names any tab the year window left empty, and says
  out loud when a tab drags another tab's data along with it (Giving measures
  donations against the salary history, so a Giving link carries it). Trimming
  the years shortens the LINK, never the figures: the oldest year kept is
  re-seeded with the balances it opened on, so the recipient sees the same
  numbers you do. It's a snapshot — later edits don't appear, and a link can't
  be withdrawn once sent, so treat one like emailing a spreadsheet.
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

## Getting Started

**Anyone can just use it** — open the page and press **Start fresh**: it sets
up the current year's budget with a starter set of rows (all renameable,
deletable, reorderable) and every tab's ＋ Add buttons do the rest. No import
needed, no account, and each person's data stays in their own browser — so
sharing the plain URL shares the app, never the numbers. (A **share link** is
the deliberate exception: it carries the figures you picked inside the link
itself.)

Charlie's own one-time migration from the Numbers spreadsheet:

```bash
python3 import_xlsx.py "~/Downloads/Financial Plan.xlsx"
```

Then open the app → **Back up** → **Restore JSON…** → pick
`financial-plan-data.json`. The same Restore path handles ordinary backups —
Export writes `financial-plan-YYYY-MM-DD.json`, Restore reads it back.

Folded away at the foot of that same dialog, under **Start again**, is
**Delete all data**. It's behind a fold on purpose: the one irreversible action
in the app shouldn't sit a mis-click away from Export. Pressing it opens a
confirmation of its own that says exactly how much is going ("This deletes 8
years of budgets, 3 goals…"), says out loud when you're signed in that the
copy in your Google account goes too, and offers the same JSON export as a last
chance to keep any of it.

**You stay signed in, and the deletion reaches your other devices.** The
emptied plan goes out through the normal save path, so the phone sees it land
and asks *"another device has cleared its data — clear this one too?"*;
cancelling keeps the phone's copy and restores it everywhere. Until 2026-08-14
this button deleted the Firestore document and signed you out instead, which
looked tidier and was worse: your other devices were never told, so the next
edit on the phone re-created the document and signing back in poured the whole
plan back. The surviving document holds `{ json: "<blank plan>", updatedAt }` —
no name, no month and no figure in it.

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

### Installing It as an App

The page can live in the Dock or the Applications folder instead of a tab.
Nothing is downloaded and there is no separate version to keep updated — it is
the same page in a window of its own, so it updates when the site does.

- **Chrome** — ⋮ → Cast, Save and Share → **Install page as app…**
- **Safari** (macOS 14+) — **File → Add to Dock**

**The two are not equivalent, and the difference is your data.** Chrome's
installed app shares storage with the browser, so the plan you already have is
simply there. **A Safari web app gets its own storage container**: it shares no
localStorage with Safari, so it opens EMPTY, and the way to fill it is to sign
in and let sync pull the plan down. Treat the Safari one as another device, not
as a shortcut to the tab you already had.

Installing is a window, not a sandbox — an installed app can reach exactly what
any tab on this origin could already reach, no more and no less. The one real
difference is Safari's, and it runs in the safer direction: its separate
container cannot see the sibling apps' data at all.

`manifest.webmanifest` is what makes the install a real app rather than a bare
shortcut, and two things in it are deliberate. **`scope` is `"./"`** — every one
of these apps is served from one origin, and a scope of `/` would swallow the
sibling apps into this app's window; relative keeps it right on the local server
too, where the app sits at the root rather than under `/financial-plan/`. And it
carries **no `file_handlers`, `protocol_handlers` or `share_target`**: those hand
outside data to a page on a shared origin, and nothing here needs them. The CSP
gained exactly one directive for all this, `manifest-src 'self'`.

There is deliberately **no service worker**, so the app does not open offline.
A worker is a resident process on an origin that holds work data, its caches are
origin-wide rather than per app, and a caching bug serves stale code to a
planner whose data schema moves — none of which is worth trading for launching
without wifi.

## Architecture

The icon is drawn by `make_favicon.py` (Pillow): the inline SVG in the page is
what browsers use, `favicon.ico` is the fallback a browser fetches on its own,
and the install icons (`icon-192`, `icon-512`, `icon-512-maskable`,
`apple-touch-icon`) are files because a manifest icon cannot be a data URI. One
script draws all of them from one set of coordinates rather than leaving
binaries nobody can review in a diff. The three shapes differ on purpose:
rounded where nothing will mask them, full-bleed with the mark inset where the
platform crops to a circle, and square for Apple, which applies its own corners.
Re-running it means bumping the `?v=` on every `favicon.ico` reference — two in
`index.html`, one in `privacy.html` — or the old icon stays cached for months.

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

The page only runs on localhost, and enforces that itself: GitHub Pages
publishes `tests.html` next to the app, and on that origin the hidden frame
would be a live session — a signed-in browser would start real cloud sync
inside a frame nobody can see. Anywhere but localhost it refuses, explains
itself, and changes nothing. The frame is also marked `data-fin-tests`, which
the app's sync module checks so it never initialises inside the harness —
the same guard as the sibling apps.
