# Financial Plan (financial-plan)

Charlie's personal financial planner, ported from a Numbers spreadsheet kept
2011–2026. Deployed via GitHub Pages: https://eagleadams86.github.io/financial-plan/
On-screen name is **Financial Plan** (tagline: “Charlie’s Epic Money Map”); the repo stays `financial-plan`.

## The one rule that outranks everything

**This repo is PUBLIC. Real financial data must never be committed — not in
code, not in fixtures, not in screenshots pasted into issues.** The app keeps
all data in localStorage. `financial-plan-data.json` and `expected-2026.json`
(the import script's outputs) are gitignored from the first commit; check
`git status` before every push anyway. Test fixtures use invented round
numbers only. If a change needs a realistic payload, invent one.
**Since the household arrived the state also holds people's NAMES and BIRTH
MONTHS, children's among them** — a category this repo never carried before and
more sensitive than a dollar figure. Fixtures use invented names (Sam, Robin,
Ellis); a screenshot pasted into an issue or the README now needs checking for
family names as well as balances.

## Architecture

- **One file — `index.html`** (no build step), plus `theme.css` and a vendored
  `chart.min.js` (third-party, never hand-edit). No npm, no bundler, no CDN.
- `theme.css` is a **byte-identical copy from `~/claude-theme-pack`** (private
  repo, the palette source of truth for ALL apps). Never hand-edit; palette
  changes go through the pack's `tokens.json` + contrast gate, then re-copy.
  Charlie is red-green colourblind: no new colours, ever — reuse tokens, and
  never let hue alone carry a meaning (estimate kind is typography — italics /
  underlines; charts pair colour with dashes, point shapes or stripes).
- The chrome (sticky header, button tabs, four-theme picker with Midnight
  default, anti-flash boot script, Back up dialog, privacy footer, Recent
  changes box) is the family pattern from Sprint Velocity — if a chrome rule
  changes in the family, mirror it here.
- **The tab bar is draggable**, and its order lives in `state.ui.tabOrder` —
  synced and backed up, because a deliberate arrangement should follow you (the
  panel-open set in `fin-open` is device-local; this isn't). Dragging uses
  POINTER events, not HTML5 drag-and-drop, which does nothing on a touchscreen;
  a tab is only picked up after 6px of travel measured with `Math.hypot` (the
  bar WRAPS, so a drag between rows is mostly vertical). `touch-action: pan-y`
  keeps the page scrolling under a finger. Alt+arrow moves the focused tab, so
  reordering isn't pointer-only. Three traps, all of which broke it in Chrome:
  (1) **capture the pointer on the BAR, never on a tab** — reordering means
  `insertBefore`, which detaches and reinserts the dragged tab, and a captured
  element leaving the document loses its capture, so the drag died after one
  hop; (2) **choose the tab on `pointerup`, not on `click`** — while the bar
  holds the capture Chrome retargets the compatibility click to the bar too, so
  a handler on the tab never hears it and tapping does nothing (`click` is kept
  for keyboard activation only, identified by `detail === 0`); (3) **only
  re-append the tabs when the order actually differs** — appending blurs the
  element, and doing it every render threw focus away the moment a tab was
  activated by keyboard, killing arrow navigation.
- **`VIEWS` and `tabOrder()` sit near the top of the file, above `let state =
  load()`** — and `tabOrder` is a function DECLARATION. `coerceShape` calls it,
  `coerceShape` runs inside `load()`, and `load()` catches everything and
  returns a blank state: a const declared further down is in its temporal dead
  zone at that moment, so the ReferenceError is swallowed and THE WHOLE
  WORKBOOK COMES UP EMPTY. Nothing is lost from localStorage, but the screen
  says otherwise. Anything else coerceShape reaches for has to obey the same
  rule. It's a `console.warn`, not an error, so a console check filtered to
  errors will not show it.
- localStorage keys: `fin-state`, `fin-theme`, `fin-updated`, `fin-open`. `save()` is the
  single write chokepoint (and where a future sync layer would hook in, SV
  style). `blankState()`/`coerceShape()`/`migrate()` guard every entry point;
  Restore shape-checks the RAW parse before coercing, so a wrong file is
  refused rather than imported as nothing.

## The engine

- **`computeAll()` is the only place numbers are calculated.** State stores
  inputs (actuals, manual estimates, notes, seeds, overrides); every auto
  estimate, balance, total and goal figure derives at render time. Never
  persist a computed value.
- Cell kinds mirror the spreadsheet's colour Key: `actual` (happened),
  `manual` (Charlie's estimate — beats auto), `auto` (rule-computed),
  `missing` (blank, counts as 0), `pinned` (balance stated outright), `mixed`
  (a split month whose parts disagree, and now also a subtotal spanning both).
  Each kind reads as a different LINE STYLE in the grid, never a colour, and
  every figure in the grid carries one — cells, balances, subtotals, totals.
- Estimate rules are table-driven in `RULES`: `carry` (Internet only — the
  sheet types Phone/Parking/Water into each month they apply, so a carry rule
  there would invent charges), `quarterly` (repeat on a cycle, `cat.every`
  months, default 3), `avg` (Credit Card, Venmo — mean of stored months
  before the estimate), `avglastyear` (mean of the prior calendar year's
  STORED months — never autos, so an estimate can't feed itself),
  `samemonth` (Electric, ROUND, reaches into the prior year's grid),
  `dividends` (per-row `cat.rate`, falling back to
  `settings.midTermRateAnnual` — rate/12 × prior cash+mid), `paycheck`
  (perCheck × count, incl. fractional counts; hidden entirely unless
  `settings.paycheckRule`), `none`.
- **Paycheck counts resolve, they aren't just read.** `resolvePaychecks()` gives
  every month of a year a count — its own if stored, else the SAME MONTH of the
  year before (the prior year's resolved counts, so a second year ahead keeps
  the pattern), else 2 — and `computeYear` returns the map as `paychecks`. A
  year built ahead has none of its own, and assuming two a month is 24 against
  a fortnightly 26, so the old default quietly dropped a fortnight's pay from
  every projected year. Repeating last year's pattern gets the ANNUAL total
  right, which is the point of a projection; a three-check month that has moved
  is typed over. The Paychecks row renders the RESOLVED count (italic `c-auto`
  when inherited, never a colour) — showing `·` beside three checks' worth of
  pay was the real bug — and the cell editor offers it as a placeholder, never
  a value, same rule as the balance branch. Charlie's own import happens to
  carry 2027 counts inside the 2026 grid, which `rolloverYear` copies, so this
  path was invisible in his data and only bit a fresh customer.
- **The backward-looking rules reach over the year boundary**, through the one
  shared helper `priorYearRun()` (the prior year's recorded months for a row,
  oldest first). A year built ahead has no cells of its own, so without it
  `carry`, `quarterly` and `avg` all go blank for twelve months and the
  projection's totals lie. `carry` takes the last month, `quarterly` takes the
  last month AS ITS ANCHOR (a month, not just an amount — an annual bill must
  land in its own month, and the last month with a figure is by definition on
  the beat), `avg` takes the mean, and each defers the moment the new year has
  a real month of its own. It reads RESOLVED cells, autos included — unlike
  `avglastyear`, which must exclude them because it reads the same run it
  writes. Here an auto hands back the figure already on screen, so nothing
  drifts, and a SECOND year built ahead still fills in off the projection
  behind it (the mean of a year of one mean is that mean — there's a test).
  `ruleDesc()` renders a rule with its
  row's own numbers — use it, not RULE_LABEL, wherever a rule is named next
  to a specific row.
- **Accounts are a list, not four fixed ids.** `settings.accounts` is ordered
  `{id, name, rate, creditTo, hub?, since?}`. The ids `cash/mid/long/bank`
  stay reserved (seeds, `overrides`, goal sources and the dividends rule key
  off them). `hub` is the one account ordinary money flows through — do not
  generalize that. An account earns twice over: `rate` compounds into
  `creditTo` (usually itself), and `divRate` is earned the same way but paid
  into `divTo` on a calendar beat (`divEvery`: 1/3/6/12 months, quarterly by
  default) — the brokerage sweep. A payment carries the whole period, so the
  yearly rate means the same whichever frequency it's on. Both are earnings, so both raise Total
  wherever they land; a per-month `balAdjust.interest`/`.dividend` replaces
  either with what really arrived. `since` starts an account partway through, seeded from
  `yr.seeds`, blank and out of Total before it. It is set once — at migration,
  or to the current month when an account is added — and deliberately has NO
  editor field: when tracking began is a fact about the data, and editing it
  would either blank months that hold figures or invent months that never did.
- **The household is a way of READING the plan, never an input to it.**
  `state.people` is a top-level list beside `goals` (not in `settings`, which is
  the app-preferences bag) — `{id, name, role: 'adult'|'child', birth?, retireAge?}`.
  Accounts, retirement accounts, goals (`for`) and budget rows (`person`) point
  INTO it by id. `computeYear` knows nothing about any of it and must stay that
  way: per-owner figures are derived at render time by `ownerSubtotals()`, the
  way `computeGoals` derives over `computed.balances`. That is what keeps the
  real-data cross-check passing untouched — if it ever moves after a household
  change, the change is wrong.
  - `birth` is a **`YYYY-MM` month**, guarded like `since`/`until`. Age, the
    retirement year and the month a child turns 18 are DERIVED (`ageAt`,
    `retirementYearOf`, `majorityMonthOf`) — a stored age is wrong within a year.
  - **`'joint'` is a reserved owner value, not a person.** Shared money has no
    birthday and doesn't retire. It shares the id space, so `person.save` must
    push somebody actually called Joint onto `joint-2`.
  - **Migration invents nothing.** Schema 4 rewrites no data at all: no people
    are guessed and no account is stamped with an owner, because "we don't know"
    and "it's shared" are different claims. An absent owner is the honest state
    and renders as "Unassigned".
  - **Subtotals must add up to Total.** Every account the year computes lands in
    exactly one bucket, unassigned included; they use the grid's existing
    `.subtotal` style and take their kind from `sumKind` like every other
    added-up figure. Rendered only when there is more than one bucket.
  - Renaming a person NEVER changes their id, and deleting one leaves what was
    theirs unassigned (with a toast saying how much) rather than deleting it.
  - Editors only touch `owner`/`for`/`person` **when the field was on the form** —
    a dialog that never asked the question must not answer it.
  - **No account `purpose`/`kind` tag.** It was considered and rejected: nothing
    branches on it, the goal carries "this is for college" better (a 529 and a
    taxable account can both fund one), and the filter axis is the owner. Expect
    it to be re-proposed.
  - Savings bonds and custodial handovers are deliberately NOT modelled. A flat
    `rate` cannot describe an EE bond doubling at 20 years or an I-bond resetting
    against CPI, and `until` must never be reused for majority — it drops the
    account out of Total, and a UTMA reaching 21 is still real money.
- **The Comp tab is ONE person's career** (`settings.compPerson`, defaulting to
  the first adult). Do not reshape `side.comp` into a per-person map:
  `sinceLastYear()` asks whether this salary picked up where last year's ended,
  and a household total has no answer, because one of you can change jobs while
  the other doesn't. A second earner's pay is a budget income row tagged
  `person`, which is what `takeHomePay(st, computed, y, personId)` filters on.
- **`limitsFor(year)` must keep its exact one-argument behaviour** — there is a
  test pinning it. `limitsFor(year, personId)` reads `side.limits[year].by[personId]`;
  the flat fields stay the single-earner case AND belong to the comp person until
  they have their own, so naming a household can't empty a calculator already
  filled in. `by` is the one key in that record that isn't money — coerceShape
  must not let `num()` flatten it to 0. The 401(k) limit is per person; the Roth
  MAGI check is per household. **Filing status decides whose income is counted
  and NOTHING else** — it deliberately sets no threshold, because those move
  every year and a figure shipped here would be quietly wrong within twelve
  months while looking authoritative. The app has no tax model and must not grow
  one.
- A row's `role` is `normal` / `transfer` (+ `transferTo`) / `passthrough`
  (+ `transferTo` + `creditTiming`). The old fixed names (midTransfer, zelle,
  charitable…) still arrive from backups and hand-built fixtures, so every
  read goes through `normRole()`. **The pass-through timing is load-bearing**:
  the old `zelle` landed BEFORE its account's growth, `charitable` AFTER it —
  the real-data cross-check pins that, so never "simplify" it away.
- The month header is pinned by `pinGridHeader()`, not by CSS: `.gridwrap`
  scrolls sideways, which makes it the sticky scroll container, and giving it a
  vertical scroll of its own would put a second scrollbar on screen. The header
  cells (not `<thead>` — a transformed ancestor would break the sticky label
  column inside it) are translated down as the PAGE scrolls, straight off the
  scroll event, because rAF is starved in a background tab.
- Balance chain per month, per account: `base = prior − transfersOut +
  preCredits`; `interest = base × rate/12` (or `yr.balAdjust[bid|m].interest`)
  credited to `creditTo`; then `+ postCredits`, `+ all flows` for the hub, and
  `+ balAdjust.dividend`. At the defaults this reduces exactly to the old
  four formulas — there's a test that pins it. `overrides` pin a month
  outright; later months chain from the pin.
- **The note dot is `hasNote(cell)`** — the cell's own note OR a note on any of
  its split amounts. Asking only about `cell.note` meant a month annotated
  solely on one of its amounts drew no dot and said nothing on hover, leaving
  the note reachable only by opening that cell. The tooltip breaks the amounts
  out whenever there is more than one OR a single one carries a note. A stated
  balance's note earns the dot the same way.
- A cell may carry `parts: [{v, kind, note?}]`. Its `v` stays the sum and its
  `kind` is derived (all-actual, all-manual, or `mixed`), so the engine,
  subtotals, rollover and the charts never have to know about parts.
- **A per-check row's future months OPEN as their checks** — `paycheckParts(cat,
  n, future)` returns one part per payday, prefilled at `perCheck`, with a
  fractional count's remainder as a part of its own so the split always adds up
  to the estimate (there's a test on that invariant). It is a prefill, not
  stored data: nothing is written until Save, same as the single Amount box.
  Returns null — leaving the plain one-amount view — for any other rule, for
  `perCheck: 0` (the existing warning says more than a column of $0 rows would),
  for an entered month, and for a month with no paydays. `cellSplitBtn` restores
  the same breakdown, but only while the total still equals the rule's estimate,
  so re-splitting can't overwrite a figure typed over it. The disabled Amount
  box now tracks the parts (`partsTotal`) instead of sitting on the total the
  split opened with. Note `parseMoney`, NOT `parseFloat`, when reading that box:
  it holds a formatted figure and parseFloat reads "$1,800.00" as nothing.
- "Mark month entered" **materialises** that month's autos into stored
  actuals (the app's overtyping-in-Numbers); re-opening moves the marker back
  and keeps the numbers. Rollover (`rolloverYear`) copies categories+rules,
  keeps overlap manuals, seeds from computed December, and never touches the
  old year.
- **Goals name the accounts they read.** `goal.accounts` is a list of account
  ids and `goal.count` is `capped` / `all` / `overflow` (with `overflowOf`
  naming the goal that claims the money first). The four fixed sources
  (cashBank, midCapped, midOverflow, long) migrate once into that shape. An id
  that no longer exists contributes nothing rather than breaking the goal —
  splitting one account into several is normal, and the goal has to keep
  working while you repoint it.
- **A year can be built before it arrives.** `yearStarted(st, y, today)` is
  derived, never stored: a grid year has begun once today reaches its own
  first month, or once the year before it is entered through December.
  `latestGridYear()` / `startedGridYears()` skip a year that hasn't begun, so
  Goals, History, Retirement and Comp carry on reading the current year while
  the Budget tab can show next year's projections. `newestGridYear()` includes
  it — that's what the year picker and the Build button use.
- **A balance is an `actual` once its month is ENTERED, never because the date
  has passed.** `computeYear` takes no `today` at all now — what a year computes
  depends on what you have filled in, not on what day it is. The current month
  is part-lived and its category cells are still estimates, so a balance chained
  off them is one too; marking the month entered materialises those cells, which
  is precisely when it stops being a guess. The Accounts **Total** row renders
  `c-${kind}` like the rows it adds up — it used to render no kind at all, so
  the headline figure looked like fact while every account above it said
  otherwise.
- **Every added-up figure says what it is made of**, through one pure function,
  `sumKind(kinds)`: the section subtotals across a month, their year totals, and
  the year-total column down each row — the last being the one that really mixes
  (months entered, then months projected), and the one that was silent about it.
  `missing` is IGNORED, never counted: a blank must not drag a column of real
  figures into looking part-estimated, and all-blank has nothing to describe.
  Anything settled beside anything estimated is `mixed` (the dashed mark split
  months already use, and a `mixed` cell carries its own actual up); `manual`
  and `auto` together are just `auto` — they disagree about who guessed, not
  about whether. `partsKind` is the same question one level down and stays
  separate. All four marks are LINE STYLES already in the grid's legend, so
  nothing here adds a colour.
- A month's opening balance comes from last month, else the PRIOR YEAR's same
  month if that year computed one, else the year's own seed. That ordering is
  what keeps a year built early tracking the current year's projection instead
  of freezing at whatever it was seeded with.
- Prior years: `model: 'pinned'` grids and `kind: 'summary'` years. A pinned
  grid has **no balance chain** — it STATES its balances, straight out of
  `yr.overrides`, kind `pinned`, no interest and no carry-forward, and it draws
  only the accounts that actually have a figure in it (the live year's
  `activeBal` rules don't apply to history: the hub wasn't necessarily the hub
  in 2020). Those balances used to be budget ROWS flagged `isBalance`, editable
  as budget lines and invisible to everything that reads accounts; `coerceShape`
  converts them once — one account per distinct row NAME, folding into an
  existing account where the slug already matches, cells moved to `overrides`,
  rows deleted so it can't run twice.
- **A summary year's rows are classified once, by `migrate`, not `coerceShape`.**
  The old bi-weekly sheets imported with almost every row flagged `isBalance`,
  because the importer decides that by "the row's total isn't the sum of its
  months" — impossible on a sheet whose columns were never months. Nine years
  drew NO bars at all on money in vs out, and every row sat under "Balances &
  derived rows". `summaryRowIsFlow(items)` reads the shape those sheets have: a
  closing block of balances and derived totals at the END, with an income line
  allowed to sit inside it without ending it; each balance label may be claimed
  ONCE, so a second "Savings" reading backwards is money moved into savings and
  ends the block; anything called "Total …" is a closing figure (prefix, not an
  exact name — renaming "Monthly" to "Total Cash" otherwise doubled the year);
  a derived total is never a flow wherever it sits. Validated against the
  sheets' own arithmetic: 2011's flows net to its stated end-of-year figure to
  the cent, 2012's to its closing Checking. It lives in **`migrate` under a
  schema gate (schema 3)** — not coerceShape — precisely because it overwrites
  a flag you can set by hand in the row editor, and re-running it every load
  would undo your corrections.
- **Money in vs money out counts what the accounts EARNED**, not just what the
  budget rows moved. `yearFlows(yr, computed, y)` adds `computed.interest` and
  `computed.dividend` to money in (a negative one counts as money out, same as
  a cell) — it used to read category cells only, so the interest that makes
  total liquidity outrun the budget was invisible, thousands a year and growing
  with the balances. A PINNED year adds nothing: its balances are stated, so
  what they earned is already inside them. It takes its year and computed year
  as arguments rather than reaching for globals, so the tests can pin it.
- **`until` closes an account**, the mirror of `since`. Set only on accounts
  built out of history, to the last month ANY year states for that name. Without
  it a bank you left in 2021 keeps its closing balance and rides forward for
  ever, because a live year opens each account on the prior December and history
  is all prior Decembers — it silently inflated Total, which is exactly what the
  real-data cross-check caught. Like `since` it is a fact about the data and has
  no editor field. Closed accounts are also left out of the transfer-target
  dropdown (a row already pointing at one keeps it). The live year is always the newest grid
  that has begun.
  `gridToSummary()` folds a pinned grid into totals — every category is a flow
  now that the old balance rows are accounts, and each account with a stated
  balance keeps its LAST stated month as a balance row (December wherever
  December was recorded), so a converted year shows the same end-of-year
  balances the imported summaries always had. It is permanent,
  and it refuses quietly to be useful: `rulesNeedingYear()` warns when the
  next year has `samemonth`/`avglastyear` rows that read the year being
  converted. `migrate_local_data.py` only ever does the one-off strip of
  hand-typed next-year months from the live grid — converting a year is a
  deliberate, per-year click, never something a script does behind your back.

## Editing

**Every table edits through one dialog** (`#rowDialog`): a section registers
in the `EDITORS` registry with `fields` (spec-driven form), `get`, `save`,
and optionally `del`/`move`. Rows carry `data-edit="<section>"` (+ whatever
keys the section needs — `data-year`, `data-idx`, `data-id`, `data-map`,
`data-list`); add buttons carry `data-add`. ONE delegated listener on
`#views` routes both and passes isNew explicitly — don't add per-row
handlers. New sections: register in EDITORS, stamp the attributes in the
renderer, done. `save`/`del` may RETURN A STRING to be toasted — that is how a
section reports something the reader can't see on the page in front of them;
returning nothing stays silent, and `del` returning `false` still refuses.
**Budget row edits flow forward into the years built ahead** — a projection
year's figures already track every number you type (the engine recomputes
them), but its ROWS were a snapshot taken at rollover, so adding, deleting,
renaming, re-ruling or reordering a row applies there too, and the toast names
the years. `projectionYearsAfter(st, year, today)` decides which years (grid,
later, NOT yet started, and nothing at all if the edited year is behind the
live one — history doesn't rewrite the future); `applyToRow`/`dropRow`/
`swapRows` do the work over a plain list of year objects, so both halves are
pure and pinned by tests. Only the edited row is touched: a row you set up in
next year alone survives, and one you deleted there stays deleted rather than
reappearing. A row present in both does NOT keep a different rule in each.
Budget grid *cells* are the exception — they keep their own
`#cellDialog` (kind/note/revert semantics the generic editor doesn't have).
In its balance branch **every computed figure is a placeholder, never a value**
— the balance as much as the interest and dividend boxes. Filling the balance
box in would make each visit to the dialog pin the month: correcting the
interest would freeze the balance at what it was a moment before, killing the
recalculation the correction was made for, in that account and every later
month chaining off it. A *stated* balance is a real value, because that one is
the stored number.
The grid is keyboard-operable via `wireGridKeys()`: roving tabindex (one tab
stop for the whole grid), arrow keys between cells, Enter/Space to open the cell
editor — the table keeps its own row/column header semantics, so no ARIA grid
roles are layered on.
**A select with NOTHING to offer must not throw.** `buildFields` used to read
`f.options[0][0]` unguarded, so "Claimed first by" — which lists the OTHER goals
— took the whole dialog down for anyone who had none, i.e. everybody adding
their first goal. The throw happens before `showModal()`, so the button simply
did nothing.
`side.retirement`/`side.rothLimit` are GONE — the spreadsheet's free-form
"Imported spreadsheet rows" panel and its loose value arrays, which nothing
computed from. `coerceShape` deletes both keys on load so they stop riding
along in every backup; don't reintroduce them. (`side.retirementAccounts` is
the real retirement list and is unrelated despite the near-identical name.)
A field spec may carry an **`action`** — a small button beside its box for a
move you'd otherwise make by hand across two fields, like the trip line's
"✓ Paid" folding Still due into Paid. It edits the FORM, like `link` does, so
nothing commits until Save; `type="button"` keeps it from submitting. The CSS
puts it UNDER its input, because alongside it shortens that one box and leaves
the row ragged against its neighbours.
Deleting a budget category also deletes its orphaned cells — keep that.

Budget rows carry `section` (income/expense/transfer — display grouping,
inferred once in `coerceShape` for pre-section data, a stored value is never
re-guessed) and `role` (the balance math). Consistency is enforced ONE way:
a transfer role forces the Transfers section, but a Transfers-section row may
keep role `normal` (Roth IRA transfers — the far account isn't tracked, so
its money is ordinary cash-out). Row reorder moves within a section, and is
hidden when `settings.rowSort === 'alpha'` (which sorts at render time and
never touches the stored order). Accounts edit through the `account` section
(click an account row); deleting one is refused while a category still moves
money into it. **Everything user-typed goes through `esc()` on its way into HTML** — the app
builds markup with template literals, so an unescaped interpolation is an XSS
hole. That includes values you might not think of as user input: year keys and
account ids come out of a restored file. JSON that didn't come from this code
(`safeParse`, and the same reviver in the sync module) drops `__proto__`,
because `Object.assign` copies it with [[Set]] and would reassign a prototype.
Numeric fields that reach the page WITHOUT `esc()` (holding shares, trip/PTO
nights, PTO days, allowances) are forced to numbers in `coerceShape` (`num()`) —
several renderers interpolate them raw, so a string of markup in a hand-edited
or corrupted backup would otherwise execute. Coerce the field, don't just esc
the one sink: it closes the whole class. The money maps (comp, bonuses, limits,
donations, retirement amounts/contribs) are num()'d too — a string there is
only ever $NaN on screen, never markup, but NaN poisons every total it reaches.
**Prices come from Twelve Data (`api.twelvedata.com/quote`), not Alpha Vantage.**
The swap happened 2026-08-13 for two reasons that were never going to be fixed
by tuning: AV allowed 25 lookups a day against Twelve Data's 800, and AV's free
tier did not quote MUTUAL FUNDS at all, so a fund could never be priced however
much allowance was left. Twelve Data also answers with an HTTP status and a
`code` (401 wrong key, 404 unknown symbol, 429 out of credits) where AV returned
200 and a paragraph of English that had to be pattern-matched. **Yahoo was
evaluated and rejected on evidence, not taste**: it quotes funds with no key at
all, but sends no `Access-Control-Allow-Origin` header, so no browser page can
read it — reaching it needs a proxy, and a proxy puts the holdings on somebody
else's server. Stooq has no CORS either. Don't re-litigate this without
re-testing CORS first.
- `classifyQuote(status, data)` is the single pure decision — price / noQuote /
  throttled / limited / badKey / failed — and it is table-tested. The response is
  parsed **even when `res.ok` is false**, which is the whole benefit of the new
  supplier: a 401, 404 and 429 each say what happened, and bailing on `res.ok`
  would flatten them back into one shrug.
- **`throttled` and `limited` are both 429 and must never be merged** — the
  per-minute allowance clears while you read the message, the daily one doesn't.
  Twelve Data names which in its message ("the current minute"), so the test is
  a word rather than guesswork. Reporting a transient throttle as the daily cap
  told the reader to come back tomorrow when the fix was to press the button
  again; that bug predates the swap and must not be reintroduced by it.
- **`badKey` is its own outcome**, which AV could never express. Crucially it
  writes NO `noQuote` marker — a mistyped key must not blacklist every ticker.
- The key lives in localStorage **`fin-pricekey`** (named for the job, not the
  supplier). The old `fin-avkey` is deleted on load: nothing can call that host
  any more, and a credential that can't be used is only a liability.
- **`priceProvenance()` puts the fetch time in the holding editor**, as the
  Price field's own `hint`, and the holding editor's `fields` is a FUNCTION
  rather than a list so it can be computed per row. This exists because the bar
  above the tables reports one time for the whole table and deliberately the
  OLDEST of them (`pricesAsOf` is a `Math.min`) — honest as a summary, "nothing
  here is older than this", and useless as provenance. Two holdings fetched
  hours apart both sit under the older heading, which is precisely what made a
  working mutual-fund lookup look like it had never run on 2026-08-13 and cost
  an hour of misdiagnosis. It distinguishes five states, and the one that earns
  its keep is **"you typed this over $X, fetched at…"**: a fetched price is
  copied into the holding but you may type over it, so a hint claiming "fetched"
  above a figure the reader corrected themselves would be the same class of lie
  it was added to stop. Compare, don't assume. Pure over the cache entry with an
  injectable `now`, so the wording is pinned by tests without a clock.

The price lookup records its result per ticker (`fin-quote-run`) and the
Investments tab reports it: a count alone can't say WHICH ticker failed, and
the reasons differ. A holding carries `lookup: false` when it shouldn't be
quoted at all; a row called "Cash" otherwise fetches the real listed company
CASH and overwrites the balance with its share price. The Investments tab tops
up stale prices when it opens, but a ticker that can never be quoted (a wrong
symbol, a wrong key, the daily limit, being offline) stays stale — and
`refreshPrices()` ends in `render()`, which re-opens the tab. Two separate
things keep that from becoming a request loop, and **they are not
interchangeable**:
- **`priceAutoTried`** is per ticker, and a ticker joins it only on a
  DETERMINATE answer — a price, or a genuine "no quote for that". It used to be
  stamped across the whole batch up front, including tickers the loop broke
  before ever reaching, which is why a run cut short after one quote gave up on
  every remaining holding for the rest of the page's life. That was the "it only
  does one at a time" complaint: the quiet pass never went back for them.
- **`priceCoolOffUntil`** is per run, and holds the quiet pass off for a minute
  after a batch ends throttled, capped or failed. That is what actually stops
  the render→refresh loop, which is what frees `priceAutoTried` to be honest
  about what was really asked. The manual Refresh button ignores both.
- **A `noQuote` marker in the quote cache** is the third, and the one that
  actually protects the daily allowance. `priceAutoTried` dies with the page,
  so a holding that can NEVER be quoted — a mistyped symbol, a row that isn't a
  security — was asked about again on every page load, spending a lookup each
  time and never getting anything back. It emptied Alpha Vantage's 25-a-day tier
  in an afternoon; it is kept at 800 for the same reason, since the drain is
  per page load and unbounded. A determinate "no price" writes
  `{ noQuote: true, ts }` into `fin-quotes` beside the real prices, and the quiet
  pass skips it for `NO_QUOTE_TTL_MS` (a day, so a symbol that starts being
  covered is still retried). The manual button ignores it like the others, and
  a `badKey` deliberately writes no marker at all.
  Two consequences to keep: `quoteFresh` must never read a marker as a price
  (it has none), and `pricesAsOf()` counts only entries that hold a price —
  a marker is stamped with the moment we ASKED, so letting it through dates the
  whole "prices as of" line from the last time a lookup failed.

**The refresh latch is a clock, not a flag, and that is not a refinement.**
`refreshingPrices` guards against two runs at once, but it was released only on
the line after the awaited fetch loop — and a `fetch` that never settles never
reaches any release at all: the await simply parks, nothing throws, so the latch
stayed true for the life of the page. From that moment `refreshPrices()` returned
at its own first line and **every press of ↻ Refresh did nothing, silently**,
while the bar went on showing the last completed run — which is how a daily-cap
message from the previous morning came to read as a live refusal. Three things
fix it and all three are needed:
- `AbortSignal.timeout(PRICE_TIMEOUT_MS)` on the request, guarded for browsers
  without it (an outright call would throw into the catch and break lookups
  entirely on the oldest browsers). This handles the ordinary case only.
- **The guard expires on wall-clock time** (`priceRunStartedAt` +
  `PRICE_RUN_STALE_MS`). This is the load-bearing one, because the timer above
  is exactly what cannot be trusted here: `AbortSignal.timeout` is throttled in
  a hidden document and may not fire while the tab is in the background or the
  laptop is asleep — the very situation that strands a request. Nothing has to
  fire for the button to come back.
- **`priceRunToken`**, so a stranded run that finally wakes hours later releases
  nothing it no longer owns and publishes nothing at all — it still holds its own
  `cache` snapshot and tally, and writing either would clobber whatever ran since.
A manual press during a genuine run now toasts instead of returning in silence:
a button that does nothing without saying so is how this hid for a whole day.

**The two failure notes are aged; the third is not.** `runIsToday` gates the
daily-cap note (the allowance resets each day, so yesterday's cap says nothing
about today) and `runIsRecent` gates the throttle note (it clears in about a
minute). The `missing` note has no clock on purpose — that a fund has no quote
is a durable fact about the fund, not news about this minute.

**Mutual funds DO have a free source, and it is the one now in use.** This
paragraph previously concluded the opposite and was wrong — Twelve Data's free
plan quotes FSKAX and VTSAX, proven against a real key before the swap, which is
what made replacing Alpha Vantage worth doing rather than merely tidier. A fund
returns the last NAV struck after the close (identical open/high/low/close,
dated the previous session), so a fund price is never live and never can be;
that is the instrument, not a fault in the lookup. The six-hour cache is
therefore more than fast enough for one.

The throttle/cap distinction now lives in `classifyQuote` (see above) rather
than in pattern-matched prose, but the RULE it protects is unchanged and is the
reason that function is table-tested: a transient throttle reported as the daily
cap tells the reader to come back tomorrow when the fix was to press the button
again. `run.left` is what the batch never
reached, so the tab can say how many are still to come rather than leaving a
bare "5 out of date" reading as a failure.
Both History charts carry a `.chartkey` under them for the dashed projected
outline — the signal was explained only in the prose above the chart, which is
not where you look when wondering why two bars are drawn differently. Its swatch
is neutral, not either series colour: the DASH is the meaning.
Charts get a `summary` argument: a `<canvas>` announces nothing to a screen
reader, and a chart that can't be drawn shouldn't render an empty one. Chart.js
4's BAR element ignores `borderDash` (only lines and arcs honour it), so the
projected-year "dashed edge" on the flow bars is drawn by the `dashedBarEdge`
plugin, and those bars' solid border is turned off (a dash over a same-colour
solid reads as solid). The signal must never be colour alone — Charlie is
red-green colourblind.
- **`afterRaise(c)` is the one place a year's ending salary is worked out** —
  it was written out in seven, and Total comp, the "since last year" join and
  the bonus percentage are all built on it, so a second copy that drifted would
  be its own quiet bug.
- **Bonus % is derived, never stored** — `bonusShare(bonus, bonusBase(c))`,
  measured against the salary the year OPENED on, not what it closed on. A
  bonus arrives with February's merit raise but is earned against the pay you
  were on through the year before it, which is the opening figure — and that
  makes it agree to the basis point with the payroll system, which files the
  same payment under the plan year it was FOR and divides by that year's
  closing salary. Same number: every year opens where the last one closed.
  (Total comp still uses `afterRaise` — that is a total for the year, a
  different question.) It appears as a column in Bonuses by year and as a
  linked box in
  BOTH dialogs (the comp year's `bonus`, a bonus row's `amount`) via the shared
  `linkBonusPct(which, base, moneyKey)`. Ordering rule: type the percentage and
  the dollars follow; type the dollars, or move the SALARY box, and the dollars
  stand while the percentage re-derives — a bonus is what was actually paid.
  Changing the raise leaves it alone: the raise is not part of its base. A year
  with no comp record has no base, so the box disables itself and says why
  rather than showing a stale figure, and the grid shows an em dash.
- **One bonus, one place: `side.bonuses[year]`.** It used to be stored twice —
  there and again as `comp[year].bonus` — and nobody keeps two copies of a
  number in step by hand, so "Where comp stands" reported a $0 bonus and a
  Total comp short by the whole of it for every year the comp dialog had never
  been opened on. `coerceShape` carries a comp year's own figure into the map
  where the map has nothing, the MAP WINS where both exist (it is the one
  described as what actually landed, and it covers years with no comp record),
  and the source field is deleted so a deletion can't resurrect it. The comp
  editor's Bonus box and the Bonuses-by-year row are now two doors onto the
  same figure; renumbering a comp year takes its bonus with it, deleting one
  leaves it (what landed is still true), and an empty box removes the row
  while a typed 0 is kept as a statement. `limitsFor()` reads the map too, so
  the 401(k)/MAGI calculator can borrow a bonus for a year with no comp row.
**"Since last year" on the Comp tab is not a year-on-year comparison** — that
is the raise itself, one row up. `sinceLastYear()` checks the JOIN between two
years: did this salary pick up where the year before ended? The ordinary answer
is yes, so it reads **"as planned"**; a figure appears only when something other
than the annual raise moved the pay. It used to print `+$0.00 (0.00%)` for the
ordinary case, which made a column of perfectly normal years look like failed
sums — that was reported as a bug, and it was a presentation one, not an
arithmetic one. `against` names the year compared whenever a year is missing
from the table (2021 sitting under 2019), because calling that "last year"
without saying so is a lie.
**Figures show cents — `fmtMoney`, everywhere a number is a value.** The
whole-dollar `fmtMoney0` survives for exactly one job: CHART AXIS TICKS, where
`$137,000.00` on every gridline is clutter on a scale rather than precision. If
you add a table, card or chart tooltip, use `fmtMoney`. Rounding a salary to
the dollar was hiding the cents that "salary after the raise" turns on.
Percentages on the Comp tab are `.toFixed(2)`; the progress-bar `width:` styles
keep `.toFixed(1)` because they are layout, not figures.
Money fields are TEXT inputs, not number ones: a number input can render
neither `$` nor a thousands separator. `asMoneyInput()` formats on blur and
`parseMoney()` reads leniently — symbol, commas and spaces all fall away, and
an empty box is null rather than zero. Anything counted rather than paid (the
paycheck count) opts out with `data-money="off"`.
`.grid-fields > div` sets `display: flex`, which outranks the browser's own
`[hidden] { display: none }` — the explicit `div[hidden]` rule is what actually
hides a field, and without it `showIf` looks like it works while changing
nothing on screen. A field spec may carry `showIf(values)` — `buildFields()`
re-evaluates on every select change, which is how each rule shows only its
own setting — and `hint`, a line under the input for a field whose label can't
carry the whole story. Retirement accounts are a generic list
(`side.retirementAccounts`) with a `type` and their own `contribs` by year;
the old fixed `k401` fields and the separate `rothContribs` map migrate once
in `coerceShape` and the sources are emptied so deletions can't resurrect
them. Nothing about Roth IRAs is special-cased in code.
A section may carry **`link(key)`**, called on every keystroke in any input AND
on any select change (picking from a list is as much "one box filling in
another" as typing is — it is what suggests a child's goal target date): one
box filling in another as you type. It reads and writes the FORM, never the
state — nothing is committed until Save, and setting `.value` fires no `input`
event, so there is no loop. The comp editor is the user: **Raise % and Salary
after the raise are one fact written two ways**, so typing either fills the
other, and changing the Salary moves whichever of the two followed from it (the
raise you were given is the fact, so the new salary re-derives — unless there is
no raise yet, in which case salary + the quoted figure are what give it).
`after` is NEVER stored; it is `salary × (1 + raisePct)`, exactly as the Comp
tab has always computed it. Going the other way, `raiseFor(salary, after)`
returns the ROUNDEST percentage that still reproduces `after` to the cent — a
letter says 2.5%, not the 2.500004% the rounded cents imply — falling through to
6dp only for a genuinely flat new salary. That is why `raisePct`'s field spec
sets `dp: 6`: `percent` fields default to 2dp (0.01%), which is plenty for a
rate you type but loses dollars on one derived from a salary.
`EDITORS[x].fields` is called with `(ds, isNew)`, which is how a section can
offer something only while adding — the trip editor's template picker is the
one that uses it. PTO entries carry `from`/`to` ISO days rather than a free-text range; the old
text is read once in `coerceShape` using the year it's filed under, and text
that doesn't parse is kept and still displayed. Dates are formatted by slicing
the ISO string, never by building a Date — a bare ISO day parses as UTC
midnight, which renders as the day before west of Greenwich.
**A year with no donations in it is not drawn** — `renderGiving` filters empty
buckets (needed at render time: deleting the last row of a year empties one
mid-session) and `coerceShape` + `dropDonation()` delete the bucket outright, so
an emptied year can't sit in a backup and come back on restore.
**`settings.givingFund` shows or hides the donor-advised fund section** — not
everyone has one, and the donations themselves have nothing to do with it, which
is why they are always drawn and the paragraph explaining how they file lives
outside that card. Defaulted once from the data like `paycheckRule`: on if there
is a holding in the fund or any donation with a `funding`/`grant`, off for
cash-only giving, and never overruling a choice already made. Turning it off
HIDES, never deletes — the holdings come back intact.
**Donations sort by date, oldest first, undated last** — `data-idx` stays the
position in the STORED list, which is what every edit, delete and move keys off,
so never sort the array itself. A donation carries `pending`: planned, not yet
made. Planned ones are OUT of the year's totals (counting money you haven't
given would overstate the year and the deduction) and called out after them;
the row reads italic plus the word "Planned", the estimate convention, never
colour.
**Giving as a share of income counts what LEFT YOUR OWN ACCOUNTS** —
`givenOutOfPocket()` is fund deposits + cash gifts, magnitudes (a cash gift is
typed +1000 one year and −1000 the next in real data), planned rows excluded. A
**GRANT is deliberately not added**: that dollar was given the day it went into
the fund and is already counted, so folding the grant in would double every
percentage on the tab. The denominators: gross is the Comp tab's total comp
(`afterRaise` + the bonus), take-home is the year's PAY rows only, through
`isPayRow` (the paycheck rule, or a name whose slug is in `PAY_SLUGS` — which is
what makes a history year, whose rows all carry rule `none`, work). A tax
refund, a dividend or a reimbursement is money in but is not pay. `takeHomePay`
reads the COMPUTED cells for the same reason `yearFlows` does — a year still
running must count its projected months, or the share of income reads several
times the truth for eleven months and then snaps back. **A missing denominator
is a dash, never a guess**: no comp record, or nothing in the budget that looks
like pay, and the tile says which. `givingStats` is the ONE pass both the year
cards and the chart read, so the two can't drift; every meter is scaled to
`givingCeiling` — the biggest share any year reaches, rounded up to a whole
percent, floored at 5% — so a year's two bars compare with each other AND with
the years above and below. The over-time chart is drawn only from a second year
(one point is not a trend), mixes bars on a dollar axis with two lines on a
percentage axis, and tells the lines apart by DASH as well as colour; the
diamond points and dashed bar edge mark a year that hasn't finished, keyed off
the calendar year rather than `yearIsProjected` — what matters there is that the
DONATIONS are partial, not that the grid is. `dashedBarEdge` skips non-bar
datasets: a line's points have no `base` or `width`, and `strokeRect` would be
handed NaN on every frame.
**A paragraph explaining a section is a `.note info`, never a `.card`.** A card
promises figures underneath it; one holding nothing but prose leaves the reader
waiting for a table that never comes, which is what the Donations intro was.
The class is **lifted verbatim from Team Dashboard's `.note`** rather than
invented here — the family already had the shape, and a second one would be
exactly the drift the theme rules exist to stop. Only the `info` variant is
carried across; if this app ever needs a status note, copy TD's `ok`/`err`
variants across too rather than re-deriving them. Same reasoning put the giving
tiles' info dot on the LABEL, which is where Sprint Velocity and Team Dashboard
put one on a `.tile`: trailing the foot it landed wherever the sentence happened
to wrap.
**A donation carries an `event`** — the walk, ride or appeal it was given
through — between the foundation and the cause, in the dialog and in the grid.
It is a plain text field, escaped at the sink like `foundation` and `cause`, and
older rows simply have none; nothing tries to split an existing foundation name
into the two, because " - " in a charity's own name is not a separator.
**A field explains itself in its own `hint`, not in the dialog's `sub`.**
Preferences had grown an eight-line paragraph describing five settings at once —
one more sentence each time a setting was added — until the thing you came to
change was unfindable. Its sub is one line now. A `type: 'check'` box is
centred in the 40px an input occupies (`margin-top:10px`), NOT `margin-top:auto`
— that pinned it to the bottom of its cell, so it drifted with however many
lines its hint ran to.
**A donation is filed under the year its DATE falls in**, so editing one whose
date sits outside the table it was in moves it to another table further down
the page — which reads as the row vanishing, especially when you only came to
fix a name. `donation.save` returns a "Moved to 2025 — dated Nov 1 2025" toast
whenever the bucket changes (and "Added to" for a new one). Don't make the move
silent again; a dateless row stays put and says nothing, which is right.
IRA contributions edit through the `contrib` section — one row per (account,
year) so each one is clickable, rather than a field buried in the account
editor. `side.limits[year]` holds the inputs to the two calculators (401(k) limit,
Roth MAGI) and prefills from `side.comp` on first open. App-wide preferences
(currency code — validated against `Intl.supportedValuesOf('currency')`,
since Intl renders unknown codes literally rather than throwing — PTO
default, row sort, the paycheck-rule toggle, the dividend fallback rate, the
assumed retirement return, and the price-lookup key) live behind the header's
⚙ button; `buildMoneyFormats()` rebuilds the formatters on every render.
**Every note a year holds is gathered at its foot** by `notesOfYear(st, y)` —
row notes, cell notes, the per-part notes of a split month, notes on a stated
balance, and the `extraNotes` that arrived with the import (whose `where`
carries a redundant "2015!" sheet prefix, stripped on the way out). A note is
written where it belongs and then impossible to find again: one dot in a
twelve-by-forty grid. The collector is pure over state so it can be tested;
`yearNotes(y)` renders it, and returns '' when there are none so the section
isn't drawn at all rather than sitting empty. Each line carries the cell it
came from and opens it on click — wired in `wireBudget`, because the list sits
outside `.grid` and the grid's own listener can't reach it. The list is GROUPED BY MONTH
(`<h3>` per month, "Not tied to a month" for row and imported notes, and no
headings at all in a summary year, which has none) and the GROUPS flow into
columns so a year of them fills the card. `break-inside: avoid` keeps a month
whole, which is what makes columns safe here — a plain two-column list of notes
read as one line, which is why it isn't that. A summary year is one unheaded
group, so `.notegroups.flat` moves the columns down onto the LIST; leaving them
on the group would park the whole thing in column one. The month lives in the
heading only — `notesOfYear` hands back `where`/`extra`/`m` separately rather
than one pre-joined label, so it isn't repeated on every line. The note text is
`white-space: pre-wrap` — a note
is typed into a textarea over several lines and has to read back the way it was
written, which collapsing it to a paragraph destroyed. A multi-line note puts
its label on a line of its own (`li.multiline`); a one-liner keeps the label
inline after an em dash, because giving every short note two lines doubles the
list for nothing.
**A collapsible panel stays as you left it**: tag it `data-keep="<name>"` and
`restoreOpenSections()` (called from `wireView`, so it re-applies after every
render) does the rest. The set of open names lives in `fin-open`, its own
localStorage key beside `fin-theme` — NOT a field on the state, because opening
a panel is not an edit and must not push a new version of the plan to the cloud
or ride along in every backup. `parseOpen`/`withSection` hold the logic away
from storage so tests can pin them without writing to the real page's own keys;
a corrupt value leaves everything closed rather than throwing mid-render. The
notes panel is one preference across all years rather than one per year —
re-opening it on every year change is the annoyance this removes. The changelog
box is deliberately NOT remembered: it fetches the GitHub API when opened, and
remembering it would fire that request on every page load. The Venmo and large-purchase ledgers are gone entirely, entries
included; `coerceShape` also strips the copies an earlier version folded into
`extraNotes`, matching on `where`, leaving the import's own notes alone.
Investment panes are `side.portfolios` — `{id, name, rows}` each, add/rename/
reorder through the `portfolio` section; the old fixed `taxable`/`hsa` lists
migrate once and are emptied. A holdings table reads through `holdingList()`,
whose key is either `pf:<id>` or a plain side key (`daf`, on the Giving tab).
**Headings are Title Case** — card `<h2>`s, dialog `<h3>`s and help-sheet
titles — with the small words left lowercase ("Bonuses by Year", "Money in vs
Money Out", "Raises over Time", "Average of Last Year") unless they lead. Done
as literals, NOT `text-transform: capitalize`: that would give "DAF Grant" and
"Of", and it would title-case the interpolated names — a portfolio, a trip, a
budget row — which belong to the user and are shown exactly as typed.
Info dots (`helpBtn(key, label)` + the `HELP` table + `#helpDialog`) explain
arithmetic the reader can't see; clicking outside any dialog except the
sync-choice one closes it without saving.

## Read-only share links

Ported from Sprint Velocity, which owns the family pattern — if a share rule
changes there, mirror it here. `#share=<marker>.<base64url>`; marker 1 is
deflate-raw, 0 is plain JSON (older Safari has no `CompressionStream`, and an
uncompressed link can be read by hand when one looks wrong). The payload rides
in the FRAGMENT, which is never sent to a server: no Firestore rules, no
account, no network on either side. `privacy.html` says so and must stay in
step.

- **`viewOnly` does two jobs**: it strips every edit affordance, and — the
  load-bearing one — it makes `save()` a no-op, which is what guarantees a
  borrowed link can never overwrite the plan of whoever opened it. The flag is
  mirrored onto `window.finViewOnly` so the sync module (a separate
  `<script type="module">`) can refuse to initialise: without that,
  `onAuthStateChanged` → `finAdopt()` would replace the visitor's shared payload
  with their own cloud copy under a banner still claiming to be somebody else's
  plan.
- **Read-only is enforced at one chokepoint, not nine renderers.**
  `stripEditAffordances()` runs on the freshly drawn markup inside `render()` and
  takes out `data-add`, `data-edit`, `.addbar`, `.h-edit` and the year buttons;
  `openRowEditor`/`openCellEditor` refuse outright. Adding a renderer needs no
  new gate. The imperative COPY is gated per renderer (`viewOnly ? '' : ' Click
  a row to edit it.'`) — a read-only view that tells you to click things is a
  bug in the writing.
- **`SECTION_NEEDS` is the whole privacy model.** It maps each tab to the state
  branches it actually reads, and nothing else decides what travels. Start
  reading a new branch in a renderer and it must be added there, or the shared
  copy of that tab shows blanks. `BRANCH_OWNERS` says which tab a branch belongs
  to; a branch travelling for a tab that doesn't own it is named out loud in the
  dialog (`shareCarriesNote`) — Giving measures donations against `side.comp`, so
  a Giving link carries the salary history, and the sender is told before they
  send. There is a test that fails the moment a tab is added without an entry.
- **The year window applies to EVERYTHING year-keyed**, not just `state.years`:
  `side.comp`, `bonuses`, `limits`, `donations`, each retirement account's
  `contribs`, `vacations.pto` and dated trips. Trimming only the grid was the
  first version and it was wrong — "the last 3 years" shipped twenty years of
  salary beside it.
- **The window has two ends and they are two different questions.** The CUTOFF
  ("How many years") is how much history goes in. The CEILING (the "years you've
  built ahead" box, unticked by default) is whether the projections ride along at
  all — `shareCeilingYear` is null when they do. `keepShareYear(y, cutoff,
  ceiling)` is the one predicate; either end may be null, which keeps "everything"
  on the same code path as a window rather than a branch around it.
- **The cutoff is ALWAYS measured to `shareStartedYear()`, whichever way the box
  is set** — and getting this wrong made a link worthless rather than merely
  short. A year built ahead has no cells of its own; every month of it is derived
  from the year before through `priorYearRun`. Counting projections as part of
  the window meant "the most recent year" plus projections handed over a 2027
  grid with 2026 cut away, and every carry/quarterly/average rule in it read
  blank. **The window is history; the projections sit on top of it.** There is a
  test pinning that the year a projection is built on always travels with it.
- **"Built ahead" is `yearStarted()`, not the calendar.** A 2027 grid becomes the
  live year the moment December 2026 is marked entered, and from then on it goes
  in either way — the box disables itself when there is nothing left to hold
  back. Deriving it the same way the tabs do is what stops the two disagreeing.
- **Trimming shortens the LINK, never the figures.** Balances chain — a January
  opens on the previous grid year's December, and only the first year falls back
  to `yr.seeds` — so a cut history would silently show the recipient a Cash line
  tens of thousands of dollars off. `reseedShareYears()` rewrites the oldest
  kept year's seeds from `C`'s balances for the December that was cut. There is
  a test that the sender's and the recipient's balances match exactly. The one
  thing a window really does change is the estimate rules that read the prior
  year, and `shareYearNote()` says which rows, reusing `rulesNeedingYear()` —
  the app's own existing answer to that question.
- **Names and notes leave by default** (both boxes start unticked, and every
  choice resets on each open — a link is a decision about THAT link). Names are
  the most sensitive thing the app holds, children's among them: `anonymisePeople`
  rewrites `people[].name` to "Adult 1"/"Child 1" and drops their notes. Ids,
  birth months and every owner reference are untouched, so ages and who-owns-what
  still work. A goal or account the sender NAMED after somebody keeps what they
  typed — the dialog says so rather than guessing which words are a name.
  `stripNotes` WALKS the payload rather than listing the places a note can be:
  the failure mode of a list is that it silently ships one.
- **Nothing the sender typed reaches the recipient's banner.** The label is
  rebuilt from the section list (a fixed vocabulary, filtered against `VIEWS`),
  and the range is two numbers — so a hand-edited link has no text to inject.
  `decodeShare` runs the payload through the same `coerceShape`/`migrate` gate a
  restored backup gets; a link is the least trusted input the app has.
- Tabs not in a link are REMOVED from the bar, not hidden — `render()` reads the
  bar back to decide whether to reorder, and a hidden button would still be in
  that list, so `want` and `have` could never agree and every render would
  re-append (and so blur) the whole bar. `allowedViews()` filters `want` to match.
- **A shared view makes NO network call, and that is a promise in writing.**
  `privacy.html` says creating and opening a link both involve no upload, so
  anything that reaches the wire in `viewOnly` makes the policy false. The one
  that did was the holding price lookup: `allTickers()` reads the SENDER's
  holdings while `priceKey()` and the quote cache are the READER's, so opening a
  shared Investments tab put somebody else's tickers on the wire under the
  reader's own key — spending their own free tier and overwriting the prices
  the sender chose to show. `refreshPrices()` refuses in `viewOnly` (the
  load-bearing guard), `wireInvestments()` returns early, and the whole price bar
  is omitted from the render — every line of it describes the reader's own cache,
  key and last run measured against the sender's tickers, so each would be
  meaningless or a lie. Before adding anything that fetches, ask what it does in
  a shared view. The changelog box is the one deliberate exception: it fetches
  this repo's own public commit list, carries nothing about anybody, and only on
  expand.
- **`squeeze()` catches the WRITER's promises as well as awaiting the reader.** A
  truncated link reaches `DecompressionStream` as invalid deflate and the writable
  side rejects too; only the readable side is awaited, so without those catches
  the same failure also surfaced twice as red "Uncaught (in promise)" on a page
  that had already caught it and drawn the "couldn't be opened" card.
- The price-lookup key is in its own localStorage key, not in state, so it can
  never reach a link. Keep it that way.

## Sync

Optional Google sign-in + Firestore, the family pattern (ported from Sprint
Velocity). Project **financialplan-60c6e**; one doc per user at
`financialplan/{uid}` — the collection name must always match the published
Firestore rules. `firestore.rules` in this repo is the audit-trail copy of
what the console publishes (sibling convention); the console enforces, the
file records — keep them in step. `FIREBASE_CONFIG` (public client config, not a secret) and
`GOOGLE_CLIENT_ID` sit at the top of the sync module; the OAuth client's
Authorized JavaScript origins list `https://eagleadams86.github.io` and
`http://localhost:8016` — a new local port needs registering there or sign-in
fails with origin_mismatch. Sign-in is GIS → `signInWithCredential`
(`initializeAuth`, never `getAuth` — see the comment in the module).
**The cloud doc stores the state as ONE JSON string** (`{ json, updatedAt }`),
never as Firestore fields: Firestore rejects arrays nested inside arrays
(invalid-argument), and the free-form tables are exactly that. Charlie's real
data hit this on the first sign-in — don't "improve" the doc back to
field-per-field. There is a **second, quieter reason that string is
load-bearing**: Firestore also rejects a document holding a single `undefined`
anywhere in it (same `invalid-argument` code), and this app's live state
routinely carries several — 10 of them on 2026-08-12, in `people[].retireAge`,
`side.comp[].raisePct`, `side.donations`, `side.retirementAccounts[].amount`
and `vacations.pto[].allowance`, all perfectly normal half-filled rows.
`JSON.stringify` drops them on the way out, so sync works; hand the object
straight to `setDoc()` and **every push fails from the first one**. Sprint
Velocity lost its sync to exactly that on 2026-08-12, and the local copy looked
perfect throughout because `localStorage` drops the same keys silently. Also:
`invalid-argument` does **not** mean "too big" — Firestore uses that one code
for both, so `describeSyncError()` only says size when Firestore's own message
does, rather than telling the user to delete a year over an app bug.
`remotePayload()` is the single reader (it also accepts the
old `{ data }` shape). Rules the
module keeps: localStorage is the source of truth and the cloud only mirrors
it; the first-sign-in "which copy?" dialog is load-bearing; **an empty copy
never silently beats one with data**; sync failures surface in the button and
privacy note, with no retry button by design; `save()` is the one chokepoint
that calls `cloudPush()`; Delete-all calls `window.cloudWipe` (registered only
while signed in) so a wipe removes the cloud copy too. `privacy.html` must be
updated in the same commit as any change to what sync stores.

## The import script

`import_xlsx.py` — stdlib only (no openpyxl), reads the Numbers-exported
xlsx and emits the two gitignored JSONs. It contains cell addresses and row
labels, never numbers; its stdout reports counts only. The import JSON *is*
the backup JSON — one format, one Restore path. `expected-2026.json` carries
the sheet's cached values + formula text for every live formula cell, which
is what the tests diff the JS engine against.

## Tests

`tests.html` (SV harness: hidden iframe onto the real `index.html`,
`window.__finTestHooks` hands over the consts). Synthetic fixtures only.
**`run()` is async and `await`s each test**, because the share-link encode/decode
goes through `CompressionStream`; `await` on an ordinary return value is a no-op,
so every synchronous test is untouched.
**It only runs on localhost, and enforces that itself** — the family rule from
Team Dashboard: the iframe is created by the gate at the foot of the script
(never in the markup — don't put it back), because on the published site the
invisible frame is a live session and a signed-in browser would start real
sync traffic. The iframe carries `data-fin-tests`, which the sync module in
`index.html` checks so it never initialises inside the harness.
**`file://` is deliberately NOT in `LOCAL_HOSTS`**: it has no hostname, and `''` used to sit
in that list on the reasoning that the suite couldn't run there anyway — but that sent it down
the iframe branch, where the frame silently fails to load and the suite blamed the app.
Opening the file off disk now gets the advice that fixes it, and a frame that never loaded the
app is reported as one setup problem rather than as every test failing at once. CI reaches the
page on `localhost:8016`, so the gate lets it through. The
"Real data (local only)" group fetches the gitignored JSONs and SKIPS on 404
— green in CI and on the public site by design. It compares the LIVE YEAR's
own months only: the grid runs a year past that as a projection now, where the
sheet had those months typed in, so they are not meant to agree. It also skips
`total|` once an account with a `since` has joined, because the sheet's SUM
covers the original four accounts only. When an engine rule changes, change
the matching test in the same commit, re-run the import, and make the local
cross-check pass again. CI: `.github/workflows/tests.yml` (Playwright
Chromium against `python3 -m http.server 8016`).

## Working rules

- Browser-test locally first (`.claude/launch.json` → port 8016, or
  `python3 -m http.server 8016`), then commit, push, verify the Pages deploy.
- Commit subjects are **user-facing** (the Recent changes box lists them
  verbatim) — plain English for a reader, not a diff.
- CSP `connect-src`: `'self'`, the Firebase/Google sign-in hosts, the GitHub
  API (changelog) and `https://api.twelvedata.com` (holding prices — ticker
  only). A new feature that talks to a new endpoint must add it to the CSP in
  the same commit, and update `privacy.html` if it changes what leaves the
  browser. The price-lookup key lives in localStorage `fin-pricekey`, NOT in
  state: state syncs to Firestore and rides along in every backup file, and a
  credential belongs in neither.
- Keep README.md current whenever the app meaningfully changes.
- Help/info icons never sit flush against the word they follow (standing
  preference).
