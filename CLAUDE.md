# Money Map (financial-plan)

Charlie's personal financial planner, ported from a Numbers spreadsheet kept
2011–2026. Deployed via GitHub Pages: https://eagleadams86.github.io/financial-plan/
On-screen name is **Money Map**; the repo stays `financial-plan`.

## The one rule that outranks everything

**This repo is PUBLIC. Real financial data must never be committed — not in
code, not in fixtures, not in screenshots pasted into issues.** The app keeps
all data in localStorage. `financial-plan-data.json` and `expected-2026.json`
(the import script's outputs) are gitignored from the first commit; check
`git status` before every push anyway. Test fixtures use invented round
numbers only. If a change needs a realistic payload, invent one.

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
- localStorage keys: `fin-state`, `fin-theme`, `fin-updated`. `save()` is the
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
  (a split month whose parts disagree). Each kind reads as a different LINE
  STYLE in the grid, never a colour.
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
  `settings.paycheckRule`), `none`. `ruleDesc()` renders a rule with its
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
- A cell may carry `parts: [{v, kind, note?}]`. Its `v` stays the sum and its
  `kind` is derived (all-actual, all-manual, or `mixed`), so the engine,
  subtotals, rollover and the charts never have to know about parts.
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
- A month's opening balance comes from last month, else the PRIOR YEAR's same
  month if that year computed one, else the year's own seed. That ordering is
  what keeps a year built early tracking the current year's projection instead
  of freezing at whatever it was seeded with.
- Prior years: `model: 'pinned'` grids (every cell an actual, no balance
  model) and `kind: 'summary'` years. The live year is always the newest grid
  that has begun.
  `gridToSummary()` folds a pinned grid into totals — flows sum, balance rows
  keep DECEMBER (a sum of monthly balances is meaningless). It is permanent,
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
renderer, done. Budget grid *cells* are the exception — they keep their own
`#cellDialog` (kind/note/revert semantics the generic editor doesn't have).
The grid is keyboard-operable via `wireGridKeys()`: roving tabindex (one tab
stop for the whole grid), arrow keys between cells, Enter/Space to open the cell
editor — the table keeps its own row/column header semantics, so no ARIA grid
roles are layered on.
Free-form rows (`side.retirement`/`side.rothLimit`) are loose value arrays;
an empty array is a spacer line, and `fmtLoose()` guesses display format.
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
The price lookup records its result per ticker (`fin-quote-run`) and the
Investments tab reports it: a count alone can't say WHICH ticker failed, and
the reasons differ — Alpha Vantage's free tier quotes shares and ETFs but not
mutual funds. A holding carries `lookup: false` when it shouldn't be quoted at
all; a row called "Cash" otherwise fetches the real listed company CASH and
overwrites the balance with its share price.
Charts get a `summary` argument: a `<canvas>` announces nothing to a screen
reader, and a chart that can't be drawn shouldn't render an empty one.
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
`EDITORS[x].fields` is called with `(ds, isNew)`, which is how a section can
offer something only while adding — the trip editor's template picker is the
one that uses it. PTO entries carry `from`/`to` ISO days rather than a free-text range; the old
text is read once in `coerceShape` using the year it's filed under, and text
that doesn't parse is kept and still displayed. Dates are formatted by slicing
the ISO string, never by building a Date — a bare ISO day parses as UTC
midnight, which renders as the day before west of Greenwich.
IRA contributions edit through the `contrib` section — one row per (account,
year) so each one is clickable, rather than a field buried in the account
editor. `side.limits[year]` holds the inputs to the two calculators (401(k) limit,
Roth MAGI) and prefills from `side.comp` on first open. App-wide preferences
(currency code — validated against `Intl.supportedValuesOf('currency')`,
since Intl renders unknown codes literally rather than throwing — PTO
default, row sort, the paycheck-rule toggle, the dividend fallback rate, the
assumed retirement return, and the price-lookup key) live behind the header's
⚙ button; `buildMoneyFormats()` rebuilds the formatters on every render.
`extraNotes` renders on summary years only — a live grid says what it means in
its own cells. The Venmo and large-purchase ledgers are gone entirely, entries
included; `coerceShape` also strips the copies an earlier version folded into
`extraNotes`, matching on `where`, leaving the import's own notes alone.
Investment panes are `side.portfolios` — `{id, name, rows}` each, add/rename/
reorder through the `portfolio` section; the old fixed `taxable`/`hsa` lists
migrate once and are emptied. A holdings table reads through `holdingList()`,
whose key is either `pf:<id>` or a plain side key (`daf`, on the Giving tab).
Info dots (`helpBtn(key, label)` + the `HELP` table + `#helpDialog`) explain
arithmetic the reader can't see; clicking outside any dialog except the
sync-choice one closes it without saving.

## Sync

Optional Google sign-in + Firestore, the family pattern (ported from Sprint
Velocity). Project **financialplan-60c6e**; one doc per user at
`financialplan/{uid}` — the collection name must always match the published
Firestore rules. `FIREBASE_CONFIG` (public client config, not a secret) and
`GOOGLE_CLIENT_ID` sit at the top of the sync module; the OAuth client's
Authorized JavaScript origins list `https://eagleadams86.github.io` and
`http://localhost:8016` — a new local port needs registering there or sign-in
fails with origin_mismatch. Sign-in is GIS → `signInWithCredential`
(`initializeAuth`, never `getAuth` — see the comment in the module).
**The cloud doc stores the state as ONE JSON string** (`{ json, updatedAt }`),
never as Firestore fields: Firestore rejects arrays nested inside arrays
(invalid-argument), and the free-form tables are exactly that. Charlie's real
data hit this on the first sign-in — don't "improve" the doc back to
field-per-field. `remotePayload()` is the single reader (it also accepts the
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
`window.__finTestHooks` hands over the consts). Synthetic fixtures only. The
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
  API (changelog) and `https://www.alphavantage.co` (holding prices — ticker
  only). A new feature that talks to a new endpoint must add it to the CSP in
  the same commit, and update `privacy.html` if it changes what leaves the
  browser. The Alpha Vantage key lives in localStorage `fin-avkey`, NOT in
  state: state syncs to Firestore and rides along in every backup file, and a
  credential belongs in neither.
- Keep README.md current whenever the app meaningfully changes.
- Help/info icons never sit flush against the word they follow (standing
  preference).
