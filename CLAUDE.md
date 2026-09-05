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
- The chrome (sticky header, button tabs, four-theme picker — plus Auto, which is
  the DEFAULT since 2026-08-22 and follows the reader's system; Midnight is the
  base palette — anti-flash boot script, Back up dialog, privacy footer) is the
  family pattern from Sprint Velocity — if a chrome rule changes in the family,
  mirror it here. (The Recent changes box was part of this list until it was
  removed family-wide on 2026-08-18 — see Working rules.)
- **Page width is the ONE deliberate divergence from the family** (`--page-w`,
  2400px, against SV / Flow Metrics' 1500px) — don't "restore" it. This app's
  main object is a spreadsheet: twelve months, a year total and forty-odd rows,
  and at 1500px December was under the right-hand edge on a screen with room to
  spare. Charts and short tables don't grow with the window, so the family width
  is right for the apps that only have those. The cap is high rather than absent
  so the page still has a shape on an ultrawide. **Prose runs the full width
  too, and that is a decision, not an oversight**: `.sub` and `.note p` were
  briefly held to a 110ch reading measure and it was reverted the same day. A
  card's explanation sits between its heading and its table, so a long line
  costs VERTICAL space — wrapping the paragraph to a comfortable measure pushed
  the grid down the screen, and the grid is the thing you came for. Don't
  re-add a `max-width` there on typographic principle.
  **`.empty` is the deliberate exception** (80ch, centred): an empty state has
  no table under it to push down, so the vertical cost is nil, and its lines are
  CENTRED — both ends move, leaving the eye nothing to return to on the way
  back. The rule is where the line sits, not house style.
- **The tab bar is draggable**, and its order lives in `state.ui.tabOrder` —
  synced and backed up, because a deliberate arrangement should follow you (the
  set of folded boxes in `ui.collapsed` travels for the same reason). Dragging uses
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
- **The History tab is GONE and 'goals' wears the name "Progress"** (2026-08-16).
  The three long-run charts render inside `renderGoals` now, under the goal
  cards; `buildHistoryCharts` still draws them and kept its name. The view ID
  stays `goals` — stored tab orders, folded-box keys and share-link section
  lists all speak it, so renaming the id would orphan all three. `tabOrder()`
  drops `history` from any stored order on its own; no migration. **Savings
  Goals leads the tab since 2026-08-23** — the card you come to this tab to
  read; Net Worth and the pulse are derived summaries and follow it, and the
  charts stay last. The NET WORTH strip sits second:
  `netWorthParts(st)` (pure, tested) sums the investment
  panes, the retirement accounts and the property equity, the renderer adds
  this month's computed liquid total, and the giving fund is measured but NEVER
  added — that money is already given. Each part carries `has*` because absent
  and zero are different answers: a missing branch draws no tile, never $0.00.
  SECTION_NEEDS.goals therefore carries those side branches, and a Progress
  link names them in the share dialog.
  **`pf.accounts` is how a pane says its holdings ARE a budget account's
  money** — the goal-accounts shape (a ticked LIST, since one real brokerage
  account is several budget slices), a statement never a guess, coerced to ids
  that exist and ABSENT when empty. Net worth's tiles still match their tabs;
  only the TOTAL subtracts the linked accounts' computed balances, so the pot
  counts once at the holdings' priced value. `netWorthParts` lists
  `linkedAccounts` from panes WITH rows only — an empty pane claims nothing,
  or its accounts' real money would vanish from the total. The link is said
  out loud in three places: the pane's sub, the Net Worth sub, and the Total
  tile's foot.
- **`side.liabilities`, `side.rates` and `side.snapshots.debts` arrived
  2026-08-22** — see "The Nine Gaps" below for all of it. The one thing worth
  knowing up here: `netWorthParts(st, month)` takes a MONTH now, because what a
  debt is worth depends on when you ask.
- **`side.property` is the household's stuff, not an account** — `{name, kind,
  value, owed?, note?}`, kinds from `PROPERTY_KINDS` (above `load()`, the
  temporal-dead-zone rule). Nothing flows through a house: the engine never
  sees these rows, the Household tab lists them (equity = value − owed) and the
  net worth counts them. Addressed by INDEX like a retirement account — nothing
  points at a property row, so there is nothing an index shift could strand.
  `owed` is deleted when it isn't a number ("paid off" and "never said" render
  the same, and a stored 0 would be a claim the reader didn't make); `value`
  and `owed` go through `num()` — several sinks, one class fix.
- **The Retirement tab draws in two labelled groups** — "Now — Where You Stand"
  (accounts, holdings, contributions, the two eligibility checks) and "Later —
  the Projection" (the at-retirement split, the IRA outlook, the pot chart,
  costs, other income, year by year). `.yearhead` headings inside the
  `.cards2.pairs` grid, `grid-column: 1/-1` so auto-placement can't slot a card
  beside one. Grouping and ORDER only — no card changed its markup, so every
  folded-box key survives.
- **On a phone (≤700px) the chrome shrinks three ways.** The tab bar stops
  wrapping and scrolls sideways (render() nudges the active tab into view by
  RECTANGLE, never offsetLeft, never smoothly — the year strip's rules);
  `pan-x` there means touch DRAG-reordering is desktop-only, which is the
  right trade (Alt+arrow still reorders anywhere). The header zoom picker
  hides (`#zoomSel` — pinch does its job; the exact figure stays in
  Preferences). And the budget grid's admin buttons fold behind one
  "⋯ Actions" toggle (`.gridactions-wrap`, removed WHOLE in
  `stripEditAffordances` — a toggle opening an emptied box is worse than none).
- **`scrollGridToNow()` runs AFTER `wireBoxes`, and that is not a preference**:
  folding machinery reparents a card's contents into `.card-body`, and
  reinserting the gridwrap resets its scroll to 0 — a scroll set in
  `wireBudget` was silently thrown away (found in testing, the pane showed
  January). It opens the grid with the current month in view when it is off
  the visible run — the one cell most phone visits are for — measured with
  getBoundingClientRect against the wrap (offsetLeft is page-relative here),
  instant, never smooth. A history year has no `th.now` and a grid that fits
  whole never scrolls; both fall out of the guards.
- **The year strip is NOT a second tab bar** (`yearPickerHtml` /
  `wireYearStrip`, replacing the old `<select>`). It picks a year INSIDE the
  Budget, so it must not wear the tabs' clothes: pill instead of rectangle,
  `--accent` on `--accent-bg` (the fold-away headings' pairing) instead of
  `--unit-active-bg`, hairlines instead of gaps. Fill AND weight carry the
  choice, and the two unusual years are typography, not hue — italics for a
  summary, a dotted underline for one built before it started, with the words
  in `title` and `aria-label`. Four things it must keep doing:
  (1) a **radiogroup**, not a nested tablist — these buttons redraw the panel
  the view tab already labels rather than revealing one of their own;
  (2) **scroll the chosen year into view only when it's off an end**, measured
  with `getBoundingClientRect` against the rail — `offsetLeft` is relative to
  the PAGE here, so comparing it with `scrollLeft` shuffles the strip on a year
  that was in plain sight;
  (3) **wait for the rail to have a width** before doing either job — the first
  layout after a reload can measure zero, and a zero-wide rail says every year
  is off the end, parking the strip against its right edge;
  (4) **no smooth scrolling** — an animated scroll is a silent no-op in some
  engines (it was in the pane this was built in), and the arrows must land.
  (5) **the CURRENT year wears `chip-now`** — an accent underscore under the
  chip — since 2026-08-24, the mark the month strip already had. It is the
  CALENDAR year (`todayISO().slice(0,4)`), the same kind of fact `thisMonth()`
  is, and deliberately not `latestGridYear()`: that is a claim about the plan
  rather than about today, and it would leave the mark on 2026 halfway through
  2027 because December had not been entered. A plan that is all history marks
  nothing, exactly as a month strip that does not reach this month marks none.
  The mark is a SHAPE and sits on the box's bottom edge, so it never competes
  with the fill that says "this is the one you are reading" — the point is the
  visit where the two differ.
  (6) **"This year" is the month strip's button in the other lens** — since
  2026-08-25 — and it is rendered on the same condition (`showNow`: this year is
  IN the strip and is not the one you're reading) and in the same place, FIRST
  in the nav, so its arrival grows leftwards into the rail instead of shoving
  the arrows out from under the pointer. It clicks through to exactly what the
  chip does, since it is a shortcut to a chip that may be scrolled off the rail
  rather than a second way of choosing a year.
  **The arrows have their own box, `#yearArrows`.** The two halves come and go
  for unrelated reasons — the arrows on whether the rail overflows the WINDOW,
  the button on which year you are READING — and `syncYearNav` hides the arrows
  only, dropping the outer `.yearnav` (which owns the divider rule) just when
  both are gone. One box passes a screenshot and fails the ordinary case: a plan
  of a few years fits without arrows, which is precisely when the button is the
  only thing in there.
  A keyboard move sets `yearKeyMove` so the redraw can hand focus back: picking
  a year rebuilds the view, which blurs the chip, and without it the second
  arrow key goes nowhere — the same trap the tab bar hit.
- **`VIEWS` and `tabOrder()` sit near the top of the file, above `let state =
  load()`** — and `tabOrder` is a function DECLARATION. `coerceShape` calls it,
  `coerceShape` runs inside `load()`, and `load()` catches everything and
  returns a blank state: a const declared further down is in its temporal dead
  zone at that moment, so the ReferenceError is swallowed and THE WHOLE
  WORKBOOK COMES UP EMPTY. Nothing is lost from localStorage, but the screen
  says otherwise. Anything else coerceShape reaches for has to obey the same
  rule. It's a `console.warn`, not an error, so a console check filtered to
  errors will not show it.
- **Form controls are 16px under `(pointer: coarse)` — and that rule now lives in
  the THEME PACK (`theme.css`, pack rule 10), not here.** Don't re-add it locally.
  The one pixel is load-bearing: iOS Safari ZOOMS THE PAGE IN when a focused field is under
  16px, and the body font is 15 — so every tap into a box zoomed the app, which
  then sat wider than the screen: dialogs cut off at the right, the wrap's
  padding gone, and pinching out lasted only until the next field was tapped.
  Reported from the INSTALLED web app on an iPhone, where there is no browser
  chrome to make the zoom legible as zoom. Never "tidy" these back to `inherit`.
  - **The fix has to be the FONT, not the viewport.** `maximum-scale=1` /
    `user-scalable=no` stops it by taking pinch-zoom from everyone — a real
    accessibility loss, and modern iOS ignores it anyway. The viewport meta
    stays `width=device-width, initial-scale=1.0`.
  - **It came here first as a local block, then went to the pack** the same day
    (2026-08-19) once the sweep found all five web apps had the bug. The pack's
    version uses `html` prefixes, which a local block could not: `theme.css` is
    linked BEFORE this `<style>`, so a bare `select`/`textarea` loses the tie to
    `font: inherit` further down. That source-order trap is why the local block
    had to sit last in the sheet, and why it is better off in the pack.
  - **If this app ever overrides a typing control with a class or an id, it owns
    re-asserting 16px on touch** — that is the pack rule's own contract, and
    Sprint Velocity's Jira paste box and PAPTrack's `.field select` are the two
    places in the family that need it. Nothing here does today.
  - **Left alone on purpose: the header theme/zoom/team pickers and the
    read-only share link.** The pickers are `<select>`s pinned to
    `--chrome-h` (30px), so 16px would break the header, and a select opens a
    picker rather than a keyboard; `#shareLink` is `readonly`, which suppresses
    the keyboard on iOS. If a phone ever IS seen zooming on those, the finding
    beats the reasoning — but don't "fix" them speculatively.
  - **Known uncovered edge, deliberately:** the app's own zoom is CSS `zoom` on
    the root, so Preferences below 100% renders these under 16px again and iOS
    may resume. Holding the boxes at a fixed size while everything around them
    shrank would look broken, and the phone hides the header zoom picker anyway.
- **Every modal opens through `openModal(dlg)`, never `showModal()` directly.**
  `showModal()` runs the spec's dialog focusing steps — the `autofocus` element,
  or failing that the FIRST FOCUSABLE one — and there is no `autofocus` anywhere
  in the file, so which dialogs raise a phone's keyboard was decided entirely by
  which happened to open with a text box (cell editor, row/account editor,
  Preferences) rather than a button (Back up, Share, Help). The keyboard then
  covers half the dialog before it has been read. On a COARSE pointer openModal
  moves focus off the field and onto the dialog itself.
  - **Focus still goes INTO the dialog** — that part is not optional, or a
    keyboard/screen-reader user is stranded outside a thing covering the page.
    The CONTAINER is what the ARIA practices offer for this case: every dialog
    here carries `aria-labelledby`, so it announces itself, and Tab reaches the
    first field. `tabIndex` is set at open rather than in the markup — a dialog
    is a focus target only for that moment.
  - **`(pointer: coarse)`, NOT the 700px breakpoint the chrome uses.** The
    keyboard is a fact about touch, not width: a desktop window dragged narrow
    keeps click-a-cell-and-type, a wide tablet is still spared. It is the file's
    only `matchMedia` in JS — everything else branches on width, and this one
    deliberately does not.
  - **`raisesKeyboard(el)` is pure and pinned** over `{tagName, type}`, so the
    type list is a test rather than a rediscovery. The guard is a no-op when the
    browser landed on a button or a checkbox, which is what keeps the
    button-first dialogs untouched and stays right if one later gains a field.
  - **Find is the deliberate exception**, and it needs no special case: it calls
    `openModal` like everything else and then focuses `#searchBox` itself, which
    simply wins. Typing is the entire reason that window opens. Any future
    dialog wanting the keyboard on a phone does the same — focus it afterwards.
  - **Mirrored into Sprint Predictability, Flow Metrics, Golf Handicap and PAPTrack
    on 2026-08-20**, where the same markup accident raised the keyboard on Adjust
    capacity, Teams & boards, four Golf editors and the supply form. A change here
    is a change there.
- **A horizontal scroll box must carry `position: relative`** — `.tablewrap`,
  `.gridwrap`, `.triprow`, `.yearrail` and the narrow-screen `.tabs` all do.
  `overflow-x: auto` is the whole design: a grid too wide for a phone scrolls
  inside its card and the page stays the width of the screen. On iOS that only
  half worked — WebKit clipped it on screen but still counted its full width in
  the DOCUMENT's scrollable area, so the page itself became horizontally
  scrollable into a band of nothing. Found in Sprint Predictability and fixed
  across the family 2026-08-20; measured on iOS 27 at a 402px viewport,
  `documentElement.scrollWidth` 906 against a 402px body. `position: relative` is
  what fixes it and nothing weaker does — a stacking context alone
  (`isolation: isolate`) leaves it at 906, and so does spelling out `overflow-y`;
  `contain: paint` works but takes the containing block for fixed descendants with
  it. The two absolutely positioned things inside these boxes
  (`.grid td.noted::after`, `.yearchip + .yearchip::before`) already hang off a
  `position: relative` of their own, so nothing moved. Chrome and Firefox were
  always right here, so it is only ever visible on a phone.
- **Date and month fields are `appearance: none`, and that lives in `theme.css`.**
  WebKit ignores an author `box-sizing` on a natively drawn control, so
  `width: 100%` on a date input meant the column PLUS its padding and border. See
  rule 11 in the theme pack's CLAUDE.md; don't re-fix it here.
- **Undo is an in-memory ring of saved states** (`undoRing`/`undoSnapshot`,
  cap 20, `pushSnapshot` pure and pinned). save() banks the state it REPLACES
  unless the save is itself an undo (the `undoing` latch — without it repeated
  presses oscillate between the last two states instead of walking back), and
  unless nothing outside `ui` moved (`undoCore`, the state stringified with
  ui nulled) — tab switches and box folds save too, and without that guard
  every ⌘Z walked back through navigation before reaching the edit the
  reader actually regrets. Both halves of that decision are pure and pinned
  now: `coreOf(st)` is the one ui-nulled serialization, `undoBankable(core,
  prev, undoing)` the verdict — save() must keep reading them rather than
  inlining either. The restored snapshot keeps its full `ui`, which
  helpfully lands you on the tab where the reverted change lives.
  No redo, deliberately. finAdopt CLEARS the ring: undoing past another
  device's adopted changes would clobber them under a newer timestamp. The
  ring is NEVER persisted — twenty copies of a plan beside the plan is a
  quota problem and a stale-copy problem. Undone state still passes
  coerceShape/migrate on the way back in. ⌘Z is gated off inputs and open
  dialogs (the browser's own undo owns a text box).
- **The Net Worth card is read AT A MONTH, and the reader picks which**
  (2026-09-01). `worthAsOf(st, liveKey, cur)` is the one answer — pure, pinned —
  and the card, the tiles' estimate mark and the Record button all read it, so a
  snapshot still states EXACTLY the figures that were on screen. Four decisions
  that will look arbitrary later:
  - **The settled month is the year's ENTERED marker, never last calendar
    month.** Marking a month entered is how this app says a month is settled;
    the calendar says nothing about whether the figures in it are facts, and
    offering an unentered August would write the plan's own estimates into
    permanent history — which is the complaint this answers. `monthAhead` is
    asked whether there is a choice at all, rather than `enteredThrough` being
    compared a second time here.
  - **It must be a month the year HOLDS**, and that guard is load-bearing rather
    than defensive: `coerceShape` guarantees a live year an `enteredThrough`,
    backfilling the month BEFORE it starts where nothing has been entered — so
    "nothing is settled" arrives as a real-looking `2025-12` on a 2026 grid, and
    unguarded the switch offered it and the card came back with Liquid $0.00 and
    a total missing every dollar of it. Found on screen against the sample; a
    round-numbered fixture would never have shown it.
  - **`ui.worthAsOf` is a MODE (`'settled'`), never a month.** A stored
    `'2026-08'` is a stale answer by October; "the last month you marked
    entered" stays true for ever. Absent when off, the `flowNoTransfers` rule.
  - **The snapshot's date is the month's last day CAPPED AT TODAY** — one
    expression that reads as today for the month in progress and as the 31st for
    a closed August, which is where a figure stated for August belongs on the
    line. **No seventh snapshot key**: the date already says which month it is.
  Only `liquid` and the debts vary by month at all — holdings, retirement and
  property are stated values with no month to them — so an end-of-month net
  worth is that month's balances beside TODAY's prices. The card says so out
  loud rather than implying a time machine, and that sentence is the reason
  there is no picker over every month in the plan.
  The tiles finally carry the estimate mark the rest of the app has always had
  (`.goal.est`, italic), on Total and Liquid ALONE — no month makes an estimate
  of a figure the reader typed, and marking those would say they had guessed.
  The switch is its own `.asofrow`/`.asofswitch` under the card's opening
  sentence, NOT in the heading band (which already carries the fold chevron, the
  info dot and the ⤢ button) and NOT `.viewswitch` reused — `wireBudgetSwitch`
  querySelectors the first `.viewswitch` on the page.
- **`side.snapshots` is stated net worth history** — {date, total, parts…},
  written ONLY by a deliberate act (the Record button, or a hand-typed row
  from an old statement): the pinned-balance principle, not a breach of
  "never persist a computed value". `netWorthTotals` is the ONE arithmetic
  the card and the button share, so a snapshot states exactly what the screen
  showed. A record needs a DATE and at least one figure or coerceShape drops
  it; a stated `total` wins, absent it the parts sum (`snapshotPoints`, pure).
  **The editor's `save` REBUILDS the row, so it must loop over `SNAPSHOT_PARTS`
  itself** — it carried a retyped list of five keys with `debts` missing, so
  opening a recorded snapshot to fix a typo silently threw away what it said was
  owed. That constant's own comment warns four things have to agree about the
  list; the dialog was the fifth copy, and driving both of its loops off the
  constant is what stops a sixth part being forgotten here (2026-09-01).
  A second Record the same day RESTATES (`upsertSnapshot`, pure and pinned —
  the button writes permanent history through it). The chart line is SOLID —
  recorded facts, and the dash grammar must stay honest. Snapshots are dated,
  so the share window trims them like trips.
- **`tests.html` carries a render SMOKE WALK, and it is not a substitute for the tests
  around it.** Everything else in that file calls a pure function or reads `index.html` as
  text, which left the render layer entirely unexecuted — measured on 2026-08-27, and the
  measurement is the point: `renderMonthView` (35KB), `gridCard` (27KB), `openCellEditor` (16KB) and 208 others sat at
  zero, and none of the nine tabs had ever been drawn. A throw in any of them
  would have shipped green. The walk boots a SECOND, FULL-SIZE frame (the suite's own is
  1x1px, where a render draws into a box with no room and proves nothing), populates it,
  visits every view and opens every window, and fails if the frame throws OR if a panel
  comes back empty — the second half matters, because a render that threw half way leaves an
  element that is present and with nothing in it, which no "did it throw" check would notice.
  **It writes nothing**, and that is enforced rather than intended: `save()` and `confirm()` are top-level declarations in a classic script, so they are
  properties of the frame's window and are replaced before anything is pressed — choosing a
  tab calls save(), and an unstubbed walk would have written an invented household over the
  reader's real plan on the shared origin. `fin-state` is read back at the end and compared.
  The frame carries `data-fin-tests` or index.html busts out of it. The Budget is walked
  through BOTH lenses and a grid cell is clicked, since the month page and the cell editor
  are reachable no other way.
  Verified by breaking a render on purpose and watching the suite go red where nothing else
  did — do that again if you ever doubt it is still connected. The starter carries the same
  walk, so a new app inherits one.
- **CSV export is `csvCell`/`gridToCsv`/`donationsToCsv`** (pure, pinned).
  csvCell defuses the full OWASP formula-trigger set (`= + - @`, tab, CR) on
  TEXT fields only — a negative NUMBER legitimately opens with '-', which is
  why the guard asks isText. Values export RAW; currency dress is the
  spreadsheet's job. downloadCsv prepends a BOM (Excel reads bare UTF-8 as
  Latin-1). The buttons are contextual — the year's grid actions, the Giving
  note — not the Back up dialog.
- **Search is `searchPlan(st, q, allowed)`** (pure, pinned): two characters
  minimum, `SEARCH_CAP` with the overflow COUNTED (`more`), and a budget cell
  hit carries `{type,id,m}` so `goToSearchHit` opens the cell editor after
  navigating; navigation-only in viewOnly. `allowed` is the shared-link
  fence, applied INSIDE searchPlan (absent = unrestricted): a Tax link
  borrows retirement accounts and people via SECTION_NEEDS, and filtering
  only at navigation listed their names as hits whose clicks silently did
  nothing. Filtered hits stay out of `more` too. `goToSearchHit` still checks
  `allowedViews()` — belt and braces. `findBtn` stays visible in shared
  views — searching carried data is reading. ⌘K opens (Ctrl+K off a Mac; the
  title hints say both); a `role="status"` count span announces results to a
  screen reader — the list itself stays out of the live region. The dialog
  renders through esc() everywhere. **Enter in the box opens the first hit**
  (a keydown listener beside the `input` one; nothing when there is no hit),
  and **`goToSearchHit` lands the focus on `#tab-<activeTab>` when it would
  otherwise be on <body> or something with no client rects** — a visible focus
  is left alone, and a cell hit's editor, opened after, keeps its own. Both
  2026-09-04, the family shape from Flow Metrics' 6183b71; see the audit fixes
  at the end, round two.
- **`savingsPulse` / `yearIncome`** are the Progress tab's Savings Rate &
  Runway card — yearIncome mirrors yearSpending exactly (computed cells,
  netted, summary fallback), and a missing denominator is NULL, never 0: no
  income has no rate, and no spending is not "0 months of runway" — nor is a
  missing liquid figure NaN months (both runway inputs are guarded).
  **yearIncome adds what the ACCOUNTS earned** through `accountEarnings` — see
  below. It is the one place the mirror with yearSpending is deliberately not
  exact: an expense is always a row, income is not.
- **`accountEarnings(c, yr, months)` is the ONE answer to "what did the
  accounts themselves earn?"** — every account's interest and dividends over a
  run of months. The Budget grid's Interest & Dividends row, that row's year
  column, the Income total that adds it up, the CSV and the savings rate all
  read it, so none of them can disagree about what a year earned. Pure over the
  computed year, and it reads the interest/dividend MAPS rather than walking
  `accountsOf`, which is what lets `yearIncome` — holding only `(yr, computed)` —
  ask it without a signature change.
  - **`yearFlows` keeps its own loop on purpose.** It asks a different question:
    which DIRECTION each figure moved, so a negative month there counts as money
    out. `accountEarnings` nets across the run the way a category row does.
    Merging them would silently change money in vs money out.
  - **A PINNED year earns exactly what it STATES** (2026-08-19). It computes
    nothing — no chain, no rates — so `computeYear`'s pinned branch fills the
    two maps from `balAdjust` and nothing else, and a past year with no figures
    typed into it earns nothing, exactly as before. The point is that a past
    year could not record its earnings AT ALL: the boxes were hidden, the
    Interest & Dividends row never drew, and money in / the savings rate read a
    history worth thousands a year less than it was. A SUMMARY year has no
    accounts, so it still earns nothing here — its earnings are a
    `categoryTotals` row like any other flow.
    - **A stated earning does NOT move the balance beside it**, and that is the
      whole reason it is safe: a pinned balance was read off a statement and
      already holds what the account made. It is recorded so the money lands
      where the app counts INCOME.
    - **Nothing is routed in a pinned year.** `creditTo`/`divTo` say where the
      money goes TODAY, and reading them over 2021 would announce that year's
      dividends were swept into an account chosen in 2026 — so `receivedInto`
      takes the year and returns `[]` off the live branch, and `balanceTip`
      drops the "into X" suffix by the same test. `earningsOver` takes the year
      only to pass it down.
    - **Freezing a live year stamps its earnings** alongside its balances
      (`gridToPinned`), and `pinnedToLive` takes them off again with the
      `pinnedFrom.balAdjust` it kept. Without the stamp, marking a year as
      history silently cost it every dollar of interest it had made. Only
      non-zero months are stamped, and a figure the reader typed is left alone.
      Converting a pinned year to a summary folds the lot into one
      "Interest & Dividends" flow row (`gridToSummary`).
  - **The kind is the MONTH's, `balanceKinds['total|m']` (i.e. `kindAt`), NOT
    the assorted kinds of the accounts under it.** An account whose balance you
    stated reads `pinned`, so reading the accounts marked an entered January
    "part actual, part estimate" merely because one balance in it had been typed
    in — an estimate mark on a settled month, printed directly above a Total row
    saying `actual`. It only shows in real data; there is a test pinning it. The
    exception is a `balAdjust` figure typed over the computed one, which is a
    statement of fact whatever month it sits in.
  - **The row is drawn only when something earned** (the `activeBal` rule), so a
    plan whose accounts carry no rates is exactly what it was — and the Income
    section draws even with no income ROWS if the accounts earned, since that
    money is income.
  - **The Income subtotal adds it**, which is why `subtotalRow` takes an
    `extra`: a line printed above a total that excludes it is a subtotal you
    cannot add up. That also makes the earnings line count towards the
    "one row is its own subtotal" test.
  - It is NOT part of `takeHomePay`, deliberately: that measures the giving
    percentages against PAY, and interest is not pay.
- localStorage keys: `fin-state`, `fin-theme`, `fin-updated`, `fin-zoom` —
  plus the price machinery's `fin-pricekey` and `fin-quote-run` and sync's
  `fin-sync-uid`, which live OUTSIDE state on purpose (documented in their own
  sections). "Delete everything" clears the price machinery's keys as well as
  state (`fin-pricekey`, `fin-quote-run`, and the legacy `fin-quotes`): the
  ticker list and a working credential must not outlive "every holding in this
  browser is gone" on a shared origin. `fin-theme` and `fin-zoom` are KEPT (the
  dialog says so — they describe a screen, not a plan), and so are the sync
  markers: staying signed in is what lets the emptied plan push to the cloud
  (see the delete-all section under Sync). **`fin-quotes` is GONE — the price cache is
  `state.quotes` now (2026-08-17), and the whole point is that it syncs**; the
  removal of the old key is still attempted on delete-all, for a browser that
  has not been opened since it moved. `save()` is the
  single write chokepoint (and where a future sync layer would hook in, SV
  style). `blankState()`/`coerceShape()`/`migrate()` guard every entry point;
  Restore shape-checks the RAW parse before coercing, so a wrong file is
  refused rather than imported as nothing. coerceShape also forces the GRID's
  own values — cells (v, kind whitelist, parts), seeds, overrides, paychecks
  — since they reach the engine and the page verbatim; overrides are read
  strictly (rateOrNone, not num): an override PINS a balance, and a corrupt
  field must be dropped rather than become a deliberate-looking $0. A live
  year is also guaranteed an `enteredThrough` (the month before startMonth
  when absent) because gridCard calls monthAdd on it unguarded.
- **`settings`' free scalars are held to a type too, and that was the branch
  nothing checked** (fixed 2026-08-21). Everything else in `settings` is a
  whitelisted vocabulary (`rowSort`, `filingStatus`) or a boolean, and those were
  guarded from the start — but `ptoAllowance`, `tagline`, `currency` and the two
  assumed rates went straight through. That is backwards from how it looks: **a
  share link carries all of `settings` by design**, so these are the most
  attacker-controlled fields in the whole state, not the least. Each failed
  differently and all three are pinned in `Untrusted input`:
  - `ptoAllowance` **reaches the page unescaped** — the PTO card interpolates it
    raw whenever the year has no allowance of its own — so a string of markup
    there executed on the origin every app in the family shares. It goes through
    the same `num()` class fix as `shares` and `nights`, not an `esc()` at the
    one sink.
  - `tagline` is read as `(tagline || '').trim()` at the top of `render()`, so a
    NUMBER threw before a single tab was drawn and **the app came up completely
    blank** — no card, no message, nothing the reader could act on.
  - the two rates feed the balance chain, where a non-numeric value is NaN
    through every month after it.
  **They are DELETED when unreadable, never set to `undefined`.** `load()` and
  `finAdopt` merge over `blankState().settings` with `Object.assign`, which
  copies an explicit `undefined` straight over a default — so setting the key is
  not the same as removing it, and only removing it lets the default win. That is
  the same reason `retirementReturnLow`/`High` are deleted rather than blanked;
  there is a test that merges a coerced state over `blankState()` to prove it.
  **Anything added to `settings` from now on needs a line in that block** — it is
  the `SECTION_NEEDS` discipline one level down.
- **`sampleState()` is the DEMO, and every tab must show something from it.** The
  family rule the sibling apps keep, applied to the app that needed it most: a new
  feature is not finished until the sample exercises it, and the roster comment
  above the function says what each part is there to hold up. Load it from the
  welcome card only — a household cannot sensibly be merged into one already
  there, which is why there is no second button in Preferences. Three things that
  will bite a tidy-up. **The sweep row must stay `rule: 'overflow'`** — tidied to
  `carry` it silently stops sweeping and the grid still looks fine. **The tax
  bands must stay round and stay labelled invented** in their own `source` field:
  the app promises it ships no tax figure, and a plausible-looking demo bracket
  is the one way to break that promise while passing every test. **No birth year
  may belong to anyone real** — a fixture is published, and a birth year is a
  fact about a person. `side.otherMoney` is deliberately left empty; a row there
  mints an account of its own, which in a demo reads as a broken empty grid row.
  All of the above is pinned in the `Sample data` test group, which measures
  `sampleState()` itself rather than a copy that could drift.
- **`normalizeIds()` runs first inside `coerceShape`, and every id comes out
  matching `/^[A-Za-z0-9_-]{1,64}$/`** — the family rule Sprint Predictability,
  Flow Metrics, Golf Handicap and PAPTrack all keep, which this app was the last
  to apply (2026-08-21). It covers people, accounts, goals, budget rows,
  portfolios and TRIPS, plus every field that points at one. (Trips were missed
  on the first pass and added the same day — nothing keys a map on a trip id, so
  that was the family rule being kept rather than a hole being closed, but the
  rule is *every* id-bearing list and a sixth one is exactly what a later reader
  would assume was already covered.) **This is not only tidiness:
  an id is a key PREFIX.** Cells, overrides and balance adjustments are stored as
  `<id>|<month>` and read back with `key.split('|')`, so an id carrying a bar
  splits in the wrong place and the month becomes nonsense — a hand-edited backup
  or a crafted share link could corrupt the grid with nothing erroring. Two
  things to know before touching it. The cleaner is **`slugJs`, deterministic**,
  not a fresh random id: a reference re-slugs to the same string its target does,
  so the link survives without a remap table (Sprint Predictability needs one
  because ITS ids are opaque; these are slugs, and slugs can be re-slugged). And
  it **rewrites the keyed maps too** — `cells`, `overrides`, `balAdjust`, `seeds`
  — driven from the list of ids that MOVED rather than by splitting each key,
  because the ids being repaired are exactly the ones a split reads wrongly.
  `slugJs` is idempotent, so a healthy plan is untouched and pays only a regex
  test per id; the test asserting that is the one that matters if this changes.

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
- **Every rule is now gated by the row's own schedule** — `paysIn(cat, m)`
  around the RULES dispatch in `computeYear`, so an estimate lands only where a
  row with a ticked `dueMonths` says its money moves. A row without one is
  ungated and unchanged. See "Due dates" below; it is the only way a due date
  reaches a computed figure.
- Estimate rules are table-driven in `RULES`: `carry` (was Internet only — the
  sheet types Phone/Parking/Water into each month they apply, so a carry rule
  there invented charges; **ticking the months a bill falls in fixes that and
  makes carry safe on a quarterly bill**, 2026-08-25), `quarterly` (repeat on a
  cycle, `cat.every` months, default 3 — **superseded by a ticked `dueMonths`,
  which is stated rather than inferred and cannot be re-phased by one bill paid
  late**), `avg` (Credit Card, Venmo — mean of stored months
  before the estimate), `avglastyear` (mean of the prior calendar year's
  STORED months — never autos, so an estimate can't feed itself),
  `samemonth` (Electric, ROUND, reaches into the prior year's grid — **the
  rounding is per-row since 2026-09-02, see below**),
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
- **A retirement account can list its CONTRIBUTION TYPES** (`a.buckets`, each
`{label, kind, amount}`). One real 401(k) holds a rollover, a Roth deferral, an
employer match and a pre-tax deferral at once, each taxed differently — so **the
account has one contribution limit and several tax treatments**, which is why
`type` stays on the account and `kind` moves to the bucket. Splitting one 401(k)
into five "accounts" to express that was a workaround that made the Roth split
right by accident.
- **No migration and no schema bump** — `buckets` is additive, and folding
  accounts is a user-invoked action (`foldAccounts`), never automatic. Guessing
  that "401k RAA" and "401k rollover" are one real account would be inventing;
  the same-name merge's rule applies — *"a rename does the same job from then
  on, at the point where you actually said they were the same thing."*
- **`retirementPots` emits one pot per BUCKET** when an account has them, one
  per account when it doesn't — which is what keeps a plan that has never used
  them byte-for-byte unchanged, and why the one-pot-per-account test still
  passes. Account-level `contribs` ride on a pot of the ACCOUNT's kind: the
  401(k) card's Roth share already splits the ongoing deferral, and typed
  contribution rows in practice live on IRAs, which have one treatment. **Per-
  bucket contributions are deliberately out of scope** — say so rather than
  half-build it.
- **`401k-mixed` is a real type**, because one 401(k) really does hold a pre-tax
  deferral beside a Roth one. Without it, saying so meant claiming the whole
  account was one or the other — which is what drove faking several accounts in
  the first place, so the restructure was only half a fix until it existed. Its
  third column in `RET_TYPES` is a FALLBACK only, read where no contribution
  types are listed; `traditional` because that is where the bulk of a mixed
  401(k) sits, and the accounts table **prompts** rather than counting quietly
  when an account is marked mixed with nothing under it. `foldAccounts` sets the
  type itself when what it just folded spans both treatments — derived from the
  reader's own accounts, not guessed — and only for the 401(k) family, since a
  Traditional and a Roth IRA are separate accounts in law.
  **The `retAcct` dialog's `sub` is a function** for the same reason: it used to
  say the TYPE decides the split, which stopped being true the moment buckets
  existed, and it was saying it in the one dialog where somebody is choosing one.
- **`kindTotals(accts)` is the one reader** for the Traditional/Roth question on
  screen; the tab asks it twice (the bar and the per-person table) and the two
  drifting apart would show a household whose halves don't add up.
- **The fold refuses whole and changes nothing** — different owners, or a
  `contribs` year claimed by both — the same-name merge's discipline. It also
  **drops the `ra-*` keys from `ui.collapsed`**, because splicing the array
  repoints every index-keyed folded pane; a box springing open is the harmless
  direction. `retAcct.del` drops them for the same reason; `retAcct.move` is
  a two-index swap, so it REMAPS just those two keys and every other fold
  survives the reorder.
**A retirement account can list its HOLDINGS**, the same `{ticker, shares,
price}` rows an investment pane holds, keyed `ra:<index>` through the existing
`holdingList()`. One table, one editor, one price lookup, wherever the rows
live — `priceLists()` includes them, so the refresh, the staleness count and the
six-hour cache cover them for free.
**`retAcctBalance(a)` is the one balance reader**: the holdings if there are
any, otherwise the `amount` typed on it. Derived, never stored — a copy in
`amount` would be the stale figure every total on the tab was quietly adding
up. `amount` is kept untouched underneath as the fallback, so listing holdings
and later clearing them restores the typed figure. The editor's Balance box
becomes a `readout` once holdings exist (a figure you can edit and that is then
ignored is worse than none), and because `readFields` skips a readout, `save`
falls back to the stored `amount` rather than reading `undefined` and zeroing
it. **`retAcct.save` rebuilds the row from scratch, so `rows` is carried across
by hand exactly like `contribs`** — that is the trap every new per-account field
falls into.
**A holding may carry `cost` — the lot's TOTAL basis, optional.** Deleted
rather than zeroed when absent or unreadable-empty ("never said" ≠ a $0 basis
claiming the whole value is gain), num()'d when present. `holding.save`
REBUILDS the row, so the field is carried by hand — the retAcct trap. Gain
formats through `gainText(value, cost)` (pure, null without a real basis);
the Cost/Gain columns appear only when some row in that table has a basis,
and the footer's gain is measured over the costed rows alone, saying how many
were left out. `allHoldings(st)` (pure) is the Everything You Hold rollup —
panes + retirement accounts by upper-cased ticker, DAF excluded by
construction; the card draws only when two pots contribute, and
SECTION_NEEDS.investments carries `side.retirementAccounts` for it.
**`side.targets` is UPPER-CASED ticker → share (0–1)** — the rollup's own
grouping key, so a target typed for "voo" finds the VOO row. Values are read
STRICTLY (rateOrNone) and clamped: num() would turn a corrupt field into a
deliberate-looking 0% target, which is a real statement ("hold none") the
reader never made; an emptied box DELETES for the same reason. Drift renders
in POINTS with the dollar move that would close it, and the Target/Drift
columns appear only once a target exists. A target for a ticker no longer
held stays in the map (you may be about to buy it) with no row to show on.
**`side.classes` is the sibling map** — same key, a SHORT TYPED LABEL (40
chars, escaped at the sink) in the reader's own words, because the app must
not KNOW what a fund is: a shipped taxonomy is the tax-table mistake wearing
an Investments costume. `classRollup(rows, total)` (pure) folds the rollup by
label, case-insensitively, unclassed rows LAST under "Not classed yet" —
"never said", not "miscellaneous". The By Class table draws only once a class
exists, and one dialog (`target`) edits both maps — empty deletes in each.
**`side.classTargets` is the third map** — LOWER-cased class label → share,
the By Class grouping key, edited by clicking a class row (`classTarget`,
data-cls key + data-label for the title). The unclassed bucket can carry no
target — "not classed yet" is not a thing to steer toward — and classRollup
attaches targets only to labelled groups. Ticker targets and class targets
are independent layers on purpose; the class one is where rebalancing rules
usually live, and each dialog's sub says so.
**The tab's TWO CHARTS arrived 2026-09-03** — until then Investments was five
tables and a price bar, the only substantial tab in the app with no chart on it.
Both sit LAST, after the tables they read from, and **each has a card to
itself**, which is not taste: `chartIn(card)` finds a card's chart with
`charts.find`, so a second canvas under one heading would leave the ⤢ resizing
the first and the other stale behind it, and the step arrows would walk the pair
as one stop.
**`allHoldings` rows carry `byPot` for the first of them** — the same money split
by the account it is in, accumulated off the UNROUNDED figure exactly as `value`
is, so a band and the bar it sits in are arrived at the same way. `pots` only
ever named the accounts; the split is the thing the table cannot say, and the
reason the chart is not a picture of a column that already exists.
**`potSeries(roll, cap = 5)` folds the account list to the ramp.** Five is the
pack's wall for `--series-1..5` (gated at ΔE 18 between all ten pairs under both
dichromacies) and its stated answer past five is CHANGE THE CHART, never a sixth
colour — so the tail gathers into one band. A series carries its LABEL and the
accounts it stands for, never a label matched back against an account name: an
account really called "Everything else" would otherwise be handed the folded
band's sum and the figure would look perfectly plausible. Colour is not the only
channel either — the bands run in one fixed order along every bar, the legend
runs in that order, and the tooltip names the account.
**`driftRows(rows, total)` ranks by the TRADE, not the percentage.** One series
and one colour: over and under are told apart by which side of the zero line a
bar is on, which is a position, so this is one of the few charts here where the
red-green rule costs nothing. The zero line alone is drawn at `--border-strong`
against the grid's `--chart-grid`. Rows with no target are not on it at all —
"never said" is not a drift of zero.
**`driftIsByClass(st, roll, clsGroups)` decides the layer in ONE place**, because
the card's opening line names it, its switch shows it and the bars are it. The
switch (`ui.driftByClass`, the `flowNoTransfers` shape — absent when untouched)
only rules when BOTH layers carry a target; with one, that layer is drawn
whatever was stored. It RE-RENDERS rather than redrawing the bars, for the flow
chart's reason: the prose changes with it.
**Both switches sit UNDER their chart** (2026-09-04, this one moved to join the
flow card's): a control between a card's opening sentence and its bars pushes
the bars down the screen, and each of these asks a question you only have after
looking. 16px above, `.sub`'s own bottom margin — the interval the add bars
already use after prose. The gate is the reason this one is easy to forget: a
plan with class targets and no ticker target never draws it at all.
**And the card names the Drift column only when the column is on the page.**
Targets live in `side.targets` whatever shape the plan is, but the rollup card
that carries that column needs two pots — so a reader with one brokerage account
and a target on every fund gets the bars and no column, which is exactly the case
where the bars are the ONLY place the figures appear. Found by walking the gates
after the charts were built, not by reading them.
**THE BAR TINT, 2026-09-03 — and first, the correction.** It was claimed in
conversation that "none of Money Map's fourteen charts" followed theme pack rule
3 (a bar is a tint fill plus a full-strength edge). That was wrong, and wrong in
the direction that would have caused damage if acted on wholesale: EIGHT of the
bar charts had followed it all along — monthNet, flow, Spending, Trip Spending,
Giving and the Roth ladder fill with `--ok-bg` / `--err-bg` / `--accent-bg` and
outline at full strength with `borderWidth: 2, borderSkipped: false`, which is
the rule exactly. The pack ships a ready-made tint token for each of those
colours. Check a claim like that against `newChart` call sites before acting on
it; the survey is four lines of regex.
**The real gap was the CATEGORICAL bars, and only those** — Where the Money Goes
and the two Investments charts. `--series-1..5` exist at full strength and there
is no `--series-N-bg`, so those three had nothing to fill with and stayed flat
and edgeless while every other bar in the app grew an outline. `tintOf(hex,
amount)` + `BAR_TINT` / `BAR_TINT_SOLID` are ported from Sprint Velocity property
by property (the chartTooltipTheme precedent), and `seriesBar(token)` is the one
place a ramp-coloured bar gets its properties, so no chart can take the pale fill
without the outline that carries its contrast. Every bar here is SOLID and
untextured, so every one uses `.45` — the `.68` constant is carried for the rule's
sake and is currently unused.
**On the stacked chart the edge replaced a hairline, and is strictly better.**
Where It's Held used to separate its bands with a 1px line in `--bg-card`; a
full-strength edge in the band's OWN colour separates them and says which account
each one is, and `borderSkipped: false` is what draws it.
**The LEGEND SWATCHES stay at full strength, and that is the pack's own carve-out
rather than a divergence** — rule 3 says not to tint small swatches because those
have to be told apart from EACH OTHER, and rule 4 gates the ramp at full strength
for that reason. Sprint Velocity lets its swatches take the tint because every one
of its series carries a TEXTURE that survives it; Where It's Held's accounts have
none, so at 12px the fill is all a swatch has. `fullStrengthSwatches` does it
through Chart.js's `generateLabels`. **Money Map is the first app in the family to
need that carve-out**, which is why it is written down in the pack too.
A sweep in the suite fails any bar dataset left at `borderWidth: 0` — pinning the
three that were fixed would miss the fourth chart somebody adds next year, and
that is exactly what the mistake looks like.
The linked panes' RECONCILE line compares holdingsValue against the linked
accounts' computed balances this month — agreement is said out loud, the
reconcileNote rule: that is the check passing, not nothing to say.
**A RETIREMENT account has no id — it is addressed by its INDEX**, unlike a
budget account, whose `id` is permanent and load-bearing. `retAcct.save` builds
`{name, type, kind, amount, contribs, owner?}` and nothing anywhere adds an id;
every editor, delete and move keys off `data-idx`. So **never match a retirement
account by `a.id`**: every one of them has `undefined` there, `find` therefore
returns the FIRST account in the list, and the failure is silent and plausible.
It shipped once — the IRA projection printed a Roth IRA's balance under a
401(k)'s name, because a record carried `id: a.id` and the renderer looked it up
by that. `iraOutlook` carries `idx` and the name and owner it needs, so nothing
downstream looks anything up. **Test fixtures must not invent ids for these
accounts either**: the ones for the IRA projection did, which is exactly why the
suite passed while the card was wrong.
**Accounts are a list, not four fixed ids.** `settings.accounts` is ordered
  `{id, name, rate, creditTo, hub?, since?}`. The ids `cash/mid/long/bank`
  stay reserved (seeds, `overrides`, goal sources and the dividends rule key
  off them). `hub` is the one account ordinary money flows through — do not
  generalize that. **It is nominated through `nominateHub(st, id)`**, never by
  setting the flag directly: it CLEARS `hub` from every account before setting
  it, because two hubs would send every ordinary row's money to whichever the
  engine's `find` reached first, and none would send it to whatever happens to
  be first in the list. The account editor offers it as "Main account" on an
  account that already EXISTS — nominating one while creating an account would
  move every budget row's money as a side effect of adding a savings account.
  Unticking is refused rather than obeyed (there is no moment where a plan has
  no hub; you nominate the one you want instead), while the rest of that edit is
  kept — throwing away a rate correction to punish one bad tick is its own
  surprise. Moving it is a big, retroactive change: `normal` rows land on the
  hub and nowhere else, so every live year recomputes. The save reports what
  moved for that reason. `coerceShape` still promotes `accounts[0]` when a
  restored file has none, which is a backstop and not a nomination. An account earns twice over: `rate` compounds into
  `creditTo` (usually itself), and `divRate` is earned the same way but paid
  into `divTo` on a calendar beat (`divEvery`: 1/3/6/12 months, quarterly by
  default) — the brokerage sweep. A payment carries the whole period, so the
  yearly rate means the same whichever frequency it's on. Both are earnings, so both raise Total
  wherever they land; a per-month `balAdjust.interest`/`.dividend` replaces
  either with what really arrived — and in a PINNED year that map is not a
  correction but the whole record, since nothing there is computed. `since` starts an account partway through, seeded from
  `yr.seeds`, blank and out of Total before it. It is set once — at migration,
  or to the current month when an account is added — and deliberately has NO
  editor field: when tracking began is a fact about the data, and editing it
  would either blank months that hold figures or invent months that never did.
- **Typing a balance says how far it is from the computed one**
  (`reconcileNote`, shown live under the Amount box in the balance branch of
  `#cellDialog`). The dialog always displayed the computed figure and then took
  whatever was typed over it in silence, so a correction and a mistyped digit
  looked identical. Agreement is reported too — that is the check passing, and
  the reason to open the dialog at all when the phone says one thing and the
  plan says another. **It states the gap and stops**: it deliberately does not
  offer to invent a correcting row, because the app cannot know what the missing
  money was and a row labelled "adjustment" is a worse record than an honest
  re-anchoring (a pinned balance is already the correction — later months chain
  from it). Only on a LIVE year: a pinned history year computes nothing to
  disagree with, so `editing.computed` is left unset and the note never appears;
  it never appears on a category cell either. **Nor on a month that already
  carries an override**, and that exclusion is the subtle one: a stated month's
  "computed" balance IS the override, so the note compared the figure with
  itself and reported perfect agreement. It shipped saying "Matches the plan
  exactly" over one of Charlie's Venmo months whose stated balance was a few
  dollars adrift from every row feeding it — agreement with yourself is not a check. Colourless by rule — the size of
  the gap is the signal.
- **`passthrough` is how a float is modelled, and the role picker now says so.**
  The generic role already covered it; what was missing was any hint that
  "money that lives in an app on my phone" is what it's for. Charlie's Venmo
  balance and his banks' Zelle rails are the same shape — money that never
  touches the hub account — and the pattern needs NO new code: `passthrough` +
  split amounts with per-part labels + an occasional pinned balance to
  re-anchor. Resist a named "Venmo feature": the moment there is one, PayPal and
  Cash App want theirs, and the generic role already outlives all of them.
- **An account with no balance this month says WHY** (`noBalanceReason`) —
  "closed Dec 2022", "starts Mar 2027", or "not tracked yet". They are three
  different facts and were one sentence: a closed account reading "not tracked
  yet" says the opposite of what happened, since it was tracked for years and
  then stopped. Closed ones then read as history rather than as something you
  forgot to fill in — which matters more now that merging leaves the closed
  accounts standing alone in the list. `until <= month` counts as closed: the
  only way to reach the check in the closing month itself is to have no figure
  in it. Months compare as strings, which `YYYY-MM` is built for.
- **Zoom scales the whole app** — `applyZoom(pct)`, whole percents, CSS `zoom`
  on the root. `zoom` and NOT `transform: scale()` (which scales what is painted
  but not the layout, leaving fixed elements misplaced and a `<dialog>` centred
  on the old box) and not a root font-size (this app is laid out in pixels, so
  scaling type alone stretches text out of its boxes). Stored in its own
  localStorage key `fin-zoom` beside the theme, never in state: it describes a
  screen, not a plan, so it must not sync or ride along in a backup. Applied in
  the head boot script as well, for the same reason the theme is — otherwise the
  page paints at 100% and jumps a frame later. Quarter steps in the header
  picker, an exact percentage in Preferences; a custom figure is injected into
  the picker as its own option so the two can never disagree.
  **FIVE things break under zoom, and all five are the same root cause — CSS
  pixels and screen pixels stop being the same unit:**
  - `getBoundingClientRect()` reports SCREEN pixels (zoom included) while a
    `transform: translateY()` is in the element's own pre-zoom pixels, which the
    zoom then multiplies. `pinGridHeader` measured one and wrote the other, so
    the sticky month header landed short of the app header by exactly the
    difference — 172px out at 150%. It divides by `zoomScale` now. Measured, not
    assumed: at 150%, `translateY(100px)` moves an element 150 screen pixels.
  - **Viewport units ignore zoom entirely.** `100vh` still resolves to the whole
    screen, in pixels the zoom then multiplies, so the dialog's
    `max-height: calc(100vh - 32px)` came out half as tall again as the screen
    and its title scrolled off the top with no way back. `--zoom` is set on the
    root and the calc divides by it. Any new viewport-unit size needs the same.
  - **Chart.js sizes its bitmap from `devicePixelRatio`**, which knows nothing
    about zoom, so a retina chart dropped to one device pixel per CSS pixel at
    200% and went soft while the text around it stayed sharp. `newChart` passes
    `devicePixelRatio × zoomScale`, and `applyZoom` re-renders (guarded by
    `booted`, since it also runs before the first render) so charts rebuild.
  - **Chart.js HIT-TESTING was off by the whole zoom factor** — the worst of the
    four, because it is silent and it lies rather than merely looking wrong.
    `fixChartZoomHitTesting()` is the fix and the long comment above it is the
    explanation. Chrome reports `event.offsetX` WITH the zoom applied and
    `canvas.clientWidth` WITHOUT it (measured at 125%: offsetX 623 against a
    clientWidth of 569 on a canvas whose rect is 711 wide), and Chart.js resolves
    a pointer as one against the other — so the pointer lands `zoom` times too
    far from the left edge and the error GROWS across the chart. Above 100% you
    hover a bar and are told about one to its right, or run off the end and get
    nothing; below 100% you are told about one to its LEFT, which is the case
    that reads as an off-by-one bug in the data rather than as a broken pointer.
    It was reported that way, twice, and the first fix (the solid hover fill)
    addressed a real but SEPARATE legibility problem and left this untouched —
    a good reminder to reproduce a pointer complaint at the reporter's own zoom
    before believing you have understood it. Note the DPR trick above does not
    help here: `canvas.width / currentDevicePixelRatio` cancels back to
    `chart.width` whatever is passed. Measured before and after over every bar of
    both bar charts and every point of the line chart at 75/80/90/100/125/140/150%
    — with the correction disabled, hovering 2024 at 75% reports 2020 and
    hovering 2021 at 125% reports 2024; with it, all correct at every zoom.
    It is patched at the DOM PLATFORM, which normalises each event exactly once
    into `{native, x, y}` that every later step reads, so one correction covers
    tooltips, hover, clicks and all eight charts. Chart.js is vendored and must
    never be hand-edited, which is why the patch lives in `index.html`.
  - **Chart.js LAYS EVERY CHART OUT `zoom` times too wide** — the fifth, found
    2026-08-24 while building the month view and fixed the same day
    (`fixChartZoomSizing`, beside the pointer patch). `getMaximumSize` measures
    the container with `getBoundingClientRect()` — screen pixels — and Chart.js
    writes the answer back as an inline `style.width`, which is read in the
    element's own PRE-zoom pixels. So the canvas came out `zoom` times too wide
    and the page grew a horizontal scrollbar into a band of nothing. Measured on
    the Progress tab at a 1,429px client width and 150%: `getMaximumSize`
    returned 1,324 for a container whose real CSS width was 883, and
    `documentElement.scrollWidth` read 2,038. It does NOT self-heal — Chart.js's
    own ResizeObserver sees a container that has not changed in ITS units — and
    it is invisible at 100%, which is how it survived the four fixes above.
    Patched at the DOM PLATFORM for the same reason the pointer fix is; the
    arithmetic is `zoomedSize(size, scale)`, pure and pinned, and a scale of 1
    hands back the SAME OBJECT because this sits on every chart's resize path.
    **The bitmap was already right** and stays right: `newChart`'s
    `devicePixelRatio × zoomScale` still lands 2.00 device pixels per screen
    pixel at every zoom now that the CSS size is honest. **The pointer fix is
    untouched by it**: it divides by `rect.width / clientWidth`, and that ratio
    is exactly the zoom before and after — measured as 0.0000 away from the zoom
    over all six canvases at 75/100/125/150/175/200%.
    **It is this app's bug alone.** The other three chart apps — Sprint
    Predictability, Flow Metrics and lottery-portfolio — have no app zoom at all
    (checked 2026-08-24: 17 zoom-feature signals here, 0 in each of them), and
    browser zoom does not cause this, since it scales CSS pixels uniformly and
    leaves `getBoundingClientRect` in the same units as `style.width`. Nothing
    to mirror across the family; if an app ever gains the zoom control, it needs
    this patch and the four above with it.
  `zoomScale` is declared beside `pinnedShift`, with the other scroll-handler
  state, rather than beside the zoom controls further down — this file has been
  bitten before by a `let` sitting below its first reader, and it is read on
  every scroll event, which is no place to open localStorage.
- **Nothing in the app is one person's.** It shipped with a name in the markup —
  `<title>` and the `<h1>` both said whose plan it was, so every copy and every
  shared link carried it. `settings.tagline` replaces it: empty by default,
  capped at 60 chars, written by `render()` into both the header and
  `document.title` through textContent. **It travels in a share link, like
  every setting** — see the rule below; the hint on that field used to promise
  the opposite and was simply wrong. When adding anything that names the app,
  ask whose name it is.
- **A dividends row names the accounts it earns on** (`cat.accounts`, read only
  through `dividendAccounts()`). The rule used to read the ids `cash` and `mid`
  literally — invisible to the author, and for anybody else who renamed or
  deleted them the row returned null and went blank with nothing saying why.
  **Absent and empty are different answers**: coerceShape backfills the absent
  case once (from `['cash','mid']`, filtered to accounts that exist) and never
  touches a list the reader has emptied, because an empty list means "earn on
  nothing" and re-filling it would argue with them on every load. Earning on
  nothing is a BLANK month, not a zero — zero claims the balances were nil.
- **`until` is editable** ("Stopped using it"), which it wasn't: it could only
  be written by the spreadsheet importer, so anybody else's closed account
  carried its last balance forward for ever — the exact bug `until` exists to
  fix. Two refusals, both of which say why and neither of which undoes the rest
  of the edit: the **hub can't be closed** (everything ordinary lands there),
  and an account that **still states a balance after that month** can't be,
  because closing takes it out of Total and the figure would vanish from the
  screen while staying in the file. `statedAfter()` is the pure test.
  `since` deliberately stays uneditable — see above.
- **A budget row can declare itself pay** (`cat.isPay`, income rows only).
  `isPayRow(name, rule, isPay)` believes a stored boolean in BOTH directions and
  falls back to the `PAY_SLUGS` guess, which is kept only for plans that predate
  the tick — it is an English word list, so "Income" or "Stipend" got a dash on
  the Giving tab and the only cure was renaming your budget to suit the code.
  The editor opens the box on the EFFECTIVE answer, never the raw stored one:
  opening a row called "Paycheck" to rename it and saving would otherwise store
  `false` and quietly stop it counting.
- **`settings.longTermRateAnnual` is gone.** coerceShape still reads it to seed
  an old plan's Investments rate, then deletes it — nothing else has consulted
  it since accounts became a list. Same treatment `side.retirement` got.
- **Accounts sharing an exact name are ONE account told over the years**
  (`mergeAccountsByName`). The history import made an account per distinct row
  NAME per sheet, so one real brokerage account arrived as four ids — the same
  account under four slightly different wordings — as the spreadsheet's
  wording drifted, and the Who Owns What list read as several identical rows
  each holding a few years. Renaming them to match is how you say they are the
  same thing. Rules that must hold:
  - **It is a SUCCESSION, not a sum.** No month (nor a year's seed) may be
    claimed by two members; where one is, the whole group is left alone and the
    caller is told how many months were in the way. A balance is a fact and
    dropping one to tidy a list is not a trade worth making. This is what makes
    the function safe to run over any state, a restored backup included.
  - **The survivor is the latest incarnation** — still open beats closed, a
    later `until` beats an earlier one. That leaves `until` already correct
    (sorted descending) and means most references need no rewriting, because the
    live account is the one other things point at. `since` widens to the
    earliest, and a member with no `since` outranks any date. `hub` carries
    across: it is a fact about the account, not about the row that won.
  - **Every reference moves**: `creditTo`, `divTo`, a category's `transferTo`,
    `goal.accounts`, a dividends row's `cat.accounts`, and a pane's
    `pf.accounts` (the lists deduplicated — naming both must not list the
    survivor twice). Missing one of the first three leaves a row paying into
    an account that no longer exists, which reads as money vanishing; missing
    one of the two LISTS is worse — coerceShape filters dangling ids from
    them on the next load, so the pane's net-worth link silently vanishes
    (the Total counts the pot twice) or the dividends row quietly stops
    earning on the absorbed account, and nothing ever says so.
  - It runs **once, under the schema 5 gate in `migrate`** — NOT in
    `coerceShape`, for the same reason schema 3's row classification isn't:
    coerceShape runs on every load and this overwrites something you can set by
    hand, so two accounts you deliberately gave one name would be re-merged the
    moment you split them. From then on the **account editor's rename** does the
    job, at the point where you actually said they were the same, and returns a
    toast naming what moved — a merge that silently swallowed four years of
    balances would be indistinguishable from losing them.
  - Verified against Charlie's real data before shipping (2026-08-13): 17
    accounts to 10, all 191 stored figures preserved by name/month, and **all
    402 computed balances across eight years identical** — including 2027's
    closing total. Re-run that comparison if this is ever touched: the reason it
    matters is that a live year opens on the prior December, so moving a
    December balance onto a live account's id could move the year after it.
- **The household is a way of READING the plan, never an input to it.**
  `state.people` is a top-level list beside `goals` (not in `settings`, which is
  the app-preferences bag) — `{id, name, role: 'adult'|'child', birth?, retireAge?}`.
  Accounts, retirement accounts, goals (`for`) and budget rows (`person`) point
  INTO it by id. `computeYear` knows nothing about any of it and must stay that
  way: per-owner figures are derived at render time by `ownerSubtotals()`, the
  way `computeGoals` derives over `computed.balances`. That is what keeps the
  real-data cross-check passing untouched — if it ever moves after a household
  change, the change is wrong.
  - **A brand-new plan starts with one adult called "Me", and that lives in
    `newPlanState()` — NOT in `blankState()`** (2026-08-22). The split is not
    tidiness. `blankState()` is the base of `Object.assign(blankState(), parsed,
    …)` in every load, import, restore and share path, and the baseline
    `buildSharePayload` diffs against; a person put there is handed to any backup
    that predates the household, and an adult appearing in a plan that had none
    re-keys the 401(k) cards from `undefined` to that id (`limitEarners`), so the
    reader watches their contribution limits come back empty from a restore that
    was meant to be lossless. Only the four genuinely-new-plan sites call
    `newPlanState()`: `load()` with nothing saved, `load()`'s unreadable-JSON
    catch, `startFresh()` and Start again. `tests.html` pins both halves,
    including the old-backup merge. The default carries **no birth month** on
    purpose — every age, retirement year and 18th birthday is derived from it, so
    a guessed one prints a wrong date as the app's own answer.
    It also trims the fresh plan's ACCOUNTS to the two the starter budget uses — Cash
    (the hub) and Savings — and puts both in that person's name. `DEFAULT_ACCOUNTS`
    still carries four, because coerceShape rebuilds all four for a backup saved
    before accounts became a list; the other two simply never appeared anywhere on a
    fresh plan, so they read as furniture at $0.00 beside a "+ Add Account" button
    that is the answer for anyone who wants them back.
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
  and NOTHING else here** — it deliberately sets no threshold, because those move
  every year and a figure shipped here would be quietly wrong within twelve
  months while looking authoritative. (Filing status has a second job since the
  Tax tab arrived: it is the innermost key of a bracket table. Same principle —
  it selects between tables the reader typed, and still sets no figure itself.
  That second job is why Preferences ALWAYS asks it, as of 2026-08-19: it was
  hidden until a household existed, back when the Roth check was its only
  reader, which left anyone using the Tax tab without naming a person stuck on
  Single while the bracket editor told them what they were filed under. The
  half that genuinely needs two people — whose income is counted — guards
  itself where it is computed rather than by hiding the question.)
  **Deleting a limits record clears figures, never neighbours**: a second
  earner's delete touches only their `by` entry, and the comp person's delete
  clears the flat record's own fields while `by` still holds somebody — the
  year record itself only goes when nobody else is left in it. It used to
  delete the whole year on the comp person's card, taking the other earner's
  salary and elections with it.
  **The rule this used to state as "the app has no tax model and must not grow
  one" was two rules wearing one coat, and only one of them was ever the
  point** — see "Tax" below. No shipped FIGURE is the real rule and it is
  unchanged. Tax ARITHMETIC was never the point and was never obeyed: `magiCard`
  has always computed a MAGI, measured it against a phase-out band and rendered
  a verdict. What it does not do is *know* the threshold.
- A row's `role` is `normal` / `transfer` (+ `transferTo`) / `passthrough`
  (+ `transferTo` + `creditTiming`). The old fixed names (midTransfer, zelle,
  charitable…) still arrive from backups and hand-built fixtures, so every
  read goes through `normRole()`. **The pass-through timing is load-bearing**:
  the old `zelle` landed BEFORE its account's growth, `charitable` AFTER it —
  the real-data cross-check pins that, so never "simplify" it away.
- **An overflow row keeps `role: 'normal'`** — the engine keys on
  `cat.rule === 'overflow'`, never a new role, so nothing built on roles ever
  moves its money. Its fields, valid only while the rule is `overflow` and
  DELETED otherwise (the Firestore rule — never `undefined`): `overflowFrom`
  (the watched source), `transferTo` (the destination — the transfer field
  reused, so the account-delete guard and the merge already half-knew it; the
  merge's reference-mover must also move `overflowFrom`, and the delete guard
  refuses on BOTH ends), and exactly one of `goalId` (threshold = that goal's
  `target`, read live) or `threshold` (a typed figure, read STRICTLY via
  `rateOrNone` — `num()` would mint junk into a $0 "sweep everything" claim).
  The optional destination cap is the same pair again — `capGoalId` XOR
  `capAmount`, absent meaning uncapped (an absent cap and a $0 cap are
  different claims, which is why junk deletes rather than zeroes).
  `thresholdAccounts`/`capAccounts` exist ONLY as share-freeze artifacts (a
  goal's account set carried as plain ids): coerceShape filters them to real
  accounts and deletes empty lists, the live goal always wins over them, and
  the row editor deletes both on save — what you saved is what the dialog
  showed.
  coerceShape drops dangling ids on both (the goalId pass runs AFTER goal
  coercion, since goals settle after the years loop) and the row degrades to
  blank, never throws; save forces the Transfers section one-way, like a
  transfer role. Deleting a goal still deletes, but toasts which budget rows
  read its target. **Share links**: a budget-only link carries no goals, so
  `freezeOverflowThresholds` (pure, beside `reseedShareYears`) rewrites the
  payload — `goalId` becomes a plain `threshold` at the sender's target — so
  the recipient's figures are IDENTICAL while goal names never leave; a link
  that does carry goals keeps the live tie. privacy.html needed no change: the
  fields ride inside the one `{json}` string sync already stores, no new
  endpoint, nothing new in kind leaves the browser.
- **The grid's hover text is `data-tip` + `wireGridTip()`, never a `title`.**
  A native title bubble needs the POINTER to cross into the cell: scroll the
  grid sideways under a parked cursor, or re-render after a save, and the cell
  under it was never "entered", so no bubble comes — reported as tooltips
  sometimes not showing, unreproducible on a recording because moving the mouse
  to demonstrate heals it. The app's own tip follows pointermove (first pixel of
  movement recovers it), fills through textContent (text however built), hides
  on grid/page scroll and on click (a dialog is about to open over it), and is
  positioned with the zoom rules — event/viewport in screen px, fixed styles in
  pre-zoom px, divide by `zoomScale`; measure at the ORIGIN first, since a tip
  parked against the right edge is squeezed narrow and a width read there
  wraps every later tip into a sliver. **`cellTip(cell)` is pure and tested, and
  reads as THREE BLOCKS separated by a blank line** (settled 2026-08-17), each
  dropped when it has nothing to say: the FIGURE, the amounts it is made of, and
  the NOTE.
  - **A PHONE HAS NO POINTER, and it used to get one anyway** (fixed 2026-08-26).
    A tap on iOS raises a synthetic `mousemove` and THEN a `click`, so the old
    `mousemove` handler put the tip up and the wrap's own click listener took it
    straight back down — reported as the month view's tooltips showing for a
    split second. It was reported THERE rather than on the grid because a grid
    cell answers a tap by opening the cell editor, which hides the flash behind
    a dialog; the month view's derived lines open nothing and leave the flash on
    its own. Touch has its own contract now: the hover path is `pointermove`
    with `pointerType === 'touch'` returned early (a finger dragging is
    scrolling, not hovering), and a TAP on a line that opens nothing pins the
    tip ABOVE that line — `placeGridTipOver`, off the line's rect, because a
    finger is already covering the thing it tapped — until the next tap or
    scroll. `tipOpensEditor` is the rule for which lines those are
    (`td.cell, .mrow[data-cat], .mrow[data-bal]`, and nothing at all in a shared
    view); a line that DOES open one shows no tip, since the dialog says
    everything the tip would have. The click that a tap raised the tip with is
    the one click that does not hide it (`tipHeldByTouch`). `wireGridTip(box)`
    takes an optional box so the suite can wire a probe and replay the whole iOS
    event sequence — nothing shorter tells the fixed behaviour from the broken
    one, since both put the tip up and only one still has it a click later.
  - **A `title` may only ever be the SECOND way to something** (audited across
    every tab, 2026-08-26). It is the quiet half of the same problem: a native
    title does not flash, it simply never appears on a phone at all — so a title
    is fine on a button whose label already says it, or on a row whose editor
    holds the same words, and is a dead end anywhere else. The audit is a DOM
    walk, not a grep, and worth repeating that way: render each tab and collect
    every `[title]` with no `closest('[data-edit],[data-add],[data-note],'
    + '[data-reveal],td.cell,.mrow[data-cat],.mrow[data-bal],button,a,select,'
    + 'input,summary,[role=button]')`. It found six, each fixed by the route it
    needed rather than by one rule:
    - the year grid's derived **Interest & Dividends** row label became
      `data-tip` — it opens no editor, and the month view's own line has
      answered a tap since the fix above, so both lenses now explain the same
      figure the same way. It sits inside `.gridwrap` already, which is why the
      tip did NOT have to be widened past its two boxes to reach it.
    - **Share**, **Interest left** and **% of salary** took the family's help
      dot: each explains a whole COLUMN, which is the job the dot already has.
    - the **year-total** heading had a dot AND a title saying the same thing.
      The title went. Two explanations on one heading is what "one dot, one
      explanation" exists to stop, and the hover copy was the half a phone could
      never read.
    - both "leaves out what has no exchange rate yet" titles were a second copy
      of a sentence the card's own paragraph already prints, and only when it is
      true. They went; the paragraph stands.
    - "percentages of different salaries don't add up" was the only one of the
      six that nothing on screen was carrying. It is now a clause in the Bonuses
      card's paragraph. **A caveat on a total belongs in the open** — a total
      that leaves something out should admit it without being asked.
  - `tipOpensEditor` widened to `[data-edit], [data-add]` at the same time. Now
    that a `data-tip` can sit on a row label, the rule has to cover every way a
    row opens an editor, not just the budget grid's three: a tip pinned under a
    modal is a tip nobody can read.
  - The figure leads. It is what the pointer was aimed at, so it must not be
    hunted for under a list of six. That is why "Total …" sits ABOVE its amounts
    now rather than under them as a sum being built up — they read as the
    working, not the arithmetic.
  - A split month breaks its amounts out one per line; they were once joined
    with " + ", which a three-check month made unreadable.
  - The note is never joined onto the figure with a "·". It is prose the reader
    wrote and is routinely several lines of it — a list of what made the month
    up — so hanging its first line off the end of "-$7,900.00 · your estimate"
    ran the amount, the kind and the first item together as one sentence and
    left the rest dangling under them.
  With no amounts to break out, the note follows the figure directly: one blank
  line, and no gap where a breakdown would have been. Every FIGURE cell carries a data-tip (category, subtotal, owner,
  balance, Total, paycheck, year-total); the row-label `th`s keep native titles
  — theirs is click-affordance prose, not data.
  **An ACCOUNT's cell reads through `balanceTip(st, c, yr, a, m)`** — pure and
  tested like `cellTip`, the balance then what the month EARNED on it. Interest
  and dividends are the two figures that move a balance with no budget row
  saying so, and reading either meant opening the cell editor. Three rules it
  keeps, all of them the house's: **a line only appears when there is something
  to say** (a month that earned nothing is quiet, rather than printing $0.00
  twice on every account with no rate), the **exception being a figure typed
  over the computed one** — a stated $0.00 is a claim somebody made, and it is
  marked the way a stated balance is; and **where the money LANDED is named
  whenever it isn't this account**, since earnings paid elsewhere are the
  likeliest reason a balance didn't move by what it earned.
  **It reads from BOTH ends**, and `receivedInto(st, c, a, m)` is the ONE
  reader for the second — the balance tooltip renders it as "Paid in $102.01
  from Brokerage", one line per account that swept something in, and the cell
  editor says the same thing as a sentence. Two answers to "who paid this in"
  that could disagree is exactly the drift `kindTotals` exists to prevent, so
  neither may re-derive it. It walks the other accounts' `creditTo`/`divTo`
  rather than being handed a map. Without it a hub balance jumps with nothing
  on the tab explaining why, which is the same question the sending lines
  answer from the other side. A source's interest and dividend are ONE figure
  on purpose: the question at this end is where the money came from, and how
  the sender split it is a fact about the sender, said in full on its own cell.
  It mirrors `payInto` rather than assuming — earnings destined for an account
  that isn't running yet stay with the account that earned them, and having a
  balance to hover or edit is the proof the destination is running, since only
  a running account has one.
  **The balance branch carries `⚙ Account settings`**, the mirror of the
  category branch's `⚙ Row settings` — same place in the dialog, same shape of
  edit (the month's figure here, the thing's own rules there). It opens
  `EDITORS.account` through `openRowEditor('account', { bal: id })`, the same
  dataset the account row's LABEL carries, so the two ways in cannot drift. It
  closes the cell dialog first: two open `<dialog>`s stack, and the second's
  Cancel would drop the reader onto a stale copy of the first. Hidden when the
  id names no account — a hand-edited backup can leave a cell behind, and a
  settings button that opens nothing is worse than none.
  **The received figure is deliberately NOT editable in the dialog** — it
  belongs to the account that sent it, and the sentence says so out loud
  ("correct that where it was earned, not here") rather than leaving a reader
  hunting for a box. That is also why the dividend box is labelled **"Dividend
  this month", not "Dividend paid in"**: the two boxes correct what THIS
  account earned while the line above them describes what came IN, and the two
  directions must not share a word.
  **The YEAR-TOTAL column of an account row is its CLOSING balance, never a
  sum** (`closingOf` in gridCard, `balanceYearTip` for the hover, and the same
  rule in `gridToCsv` so the export can't disagree with the screen). Twelve
  monthly balances added together is the same money counted twelve times — a
  meaningless figure in the column a reader trusts most, which is why the
  column sat empty for these rows. It is the last month of THIS calendar year
  that states a balance, so a pinned year recorded through October closes in
  October rather than reading blank. The tooltip says which figure it is and
  at which month — that sentence is what stops the column header ("2026 total")
  reading as a promise it doesn't keep here, and `HELP.rowTotal` carries the
  same exception. Under it ride the YEAR's interest and dividends through
  `earningsOver` (which reads `receivedInto` rather than re-deriving arrivals),
  because "what did this account make me?" is the question the column can
  honestly answer and the monthly tips only answer a twelfth at a time.
  **The Total row drops the arrivals deliberately**: a sweep between two of the
  reader's own accounts is already inside that figure, and naming it there
  would read as money arriving from outside the plan. An owner subtotal shows
  its closing figure alone — what each account earned is on its own row.
  A SUMMARY year has no accounts, so its maps are empty and the extra lines
  fall away with no branch. A PINNED year states its earnings instead of
  computing them, which is why the two earning lines live in
  **`earningLines(st, c, yr, a, m)`** rather than inside `balanceTip`: a past
  year can state what a month EARNED without stating what it HELD, so the blank
  cell's tooltip needs the same two lines. That cell still reads '·' — hovering
  is how every other detail on this grid is found, and a glyph invented for this
  one case is a symbol the reader has to learn.
  Keep it in step with the cell editor's `rateLine`, which answers the same
  question from the account's rates in a live year and, in a past one, says
  instead what the two boxes below it do.
- The month header is pinned by `pinGridHeader()`, not by CSS: `.gridwrap`
  scrolls sideways, which makes it the sticky scroll container, and giving it a
  vertical scroll of its own would put a second scrollbar on screen. The header
  cells (not `<thead>` — a transformed ancestor would break the sticky label
  column inside it) are translated down as the PAGE scrolls, straight off the
  scroll event, because rAF is starved in a background tab.
- Balance chain per month, per account: `base = prior − transfersOut +
  preCredits`; `interest = base × rate/12` (or `yr.balAdjust[bid|m].interest`)
  credited to `creditTo`; then `+ postCredits`, `+ all flows` for the hub,
  `+ balAdjust.dividend`, and **± the overflow sweeps** (below). At the
  defaults this reduces exactly to the old four formulas — there's a test that
  pins it. `overrides` pin a month outright; later months chain from the pin.
- **Overflow sweep rows (`rule: 'overflow'`) resolve INSIDE the balance phase,
  after interest and credit routing — never in `RULES`**, whose entry is a
  stub returning null, because the amount is whatever the SOURCE account would
  end this month holding above a threshold, and that figure doesn't exist
  until phase 2 has run. `overflowOrder(categories)` (pure, tested) walks
  Kahn's algorithm over `overflowFrom → transferTo` edges so a sweep's arrival
  is seen by any row watching the account it lands in — chaining in one month
  — with list order the tie-break for rows sharing a source; a CYCLE is
  refused deterministically (every row in or fed only from it stays blank; the
  cell editor names the fix) rather than iterated. Rules that must hold:
  - **One mechanism, hub included.** Overflow rows are SKIPPED in the phase-2
    partition loop — never `hubFlow`, never `transfersOut`, stored cells
    included — and move money through the month-local `sweepIn`/`sweepOut`
    maps only. The hub's interest base already excludes `hubFlow`, so this is
    arithmetically identical for a hub source, and it means the engine,
    `internalRows`, the tips and the tests reason about one thing.
  - **Post-interest on both ends**: the source keeps its full month of growth
    (the sweep is exactly the excess after it — the account lands ON the
    threshold to the cent), and the money arrives at the destination at month
    end, earning nothing there until the month after.
  - **The optional DESTINATION CAP** (`capGoalId` XOR `capAmount`, the
    threshold pair's twin) clamps the sweep to
    `max(0, cap − endOf(destination))` — Charlie's real shape: two rows both
    drawing from the hub, the first filling Mid-term up to Renovations, the
    row below taking the remainder to Long-term. Rows sharing a source
    resolve in ROW order, each seeing the source already drained. The room is
    measured against the destination's own end-of-month figure, interest
    included, so a full account KEEPS its growth — the cap stops money going
    in, it never sweeps money out — and one that dipped refills before
    anything flows past it. Absent cap = uncapped; a dangling cap goal drops
    to uncapped (coerceShape), and `freezeOverflowThresholds` freezes it like
    the threshold, or an unfrozen cap would sweep past the goal on the
    recipient's copy.
  - **Under threshold → BLANK (`missing`), never $0** — the dividends rule's
    discipline; the resolved cell is written back into `cells` with kind
    `auto` so the grid shows it and "Mark month entered" materialises it, and
    a stored cell beats the rule and moves the stored amount the same way.
  - **Both ends must be `running`** (the `payInto` guard) or the month stays
    blank; the threshold is a goal's target read live (`goalId`) or the row's
    own `threshold`, and a missing/dangling one is blank, never zero.
  - **A goal that names several accounts is measured across the LOT** —
    `overflowMeasure(cat, goals)` (pure, tested) resolves what a row's
    threshold and cap actually watch: the goal's account set when it has one,
    else the row's own end; `thresholdAccounts`/`capAccounts` are the frozen
    lists a share link writes so a recipient measures the same pot. Two
    convergence guards, enforced in the engine and explained in the cell
    editor: the SOURCE must be inside the threshold's measured set and the
    DESTINATION outside it (else the sweep could run for ever and never land
    the pot on its target — blank, deterministically); mirrored for the cap
    (destination in, source out). Ordering edges come from the source and the
    THRESHOLD measure only — **the cap's set is deliberately not an ordering
    input**: a cap is a stopping condition checked in ROW order (the list is
    the reader's transfer priority), and ordering on it would run a catch-all
    before the capped row above it whenever the catch-all's destination sits
    inside the cap's pot. A row below can therefore still pour into a pot a
    row above capped against; the cap bound when its own row ran.
  - **Zero overflow rows must compute bit-identical results to before the
    feature existed** — pinned by 'a sweep that never triggers changes nothing
    at all' plus the untouched engine groups and the real-data cross-check.
  Sign convention: negative = money leaving the source, the transfer-row
  convention; source and destination cancel, so Total never moves. The
  receiving end reads through `sweepArrivals` (pure) — deliberately NOT folded
  into `receivedInto`, which is the one reader for EARNINGS arrivals; a sweep
  has a visible budget row and "Paid in" would be the wrong claim over it.
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
- **`accountShowsInYear(a, yr, c, months, accounts)` decides whether an account
  earns a ROW in a live year** — pure and pinned, and shared with the cell
  editor so the grid and the button that empties a cell cannot disagree about
  whether a row is about to vanish. A Start-fresh budget has no transfers,
  seeds or pins for the accounts beside the hub, and those would sit at $0 for
  ever, so they are hidden until something feeds them.
  **The last test — "it holds money" — was missing until 2026-08-17**, reported
  as "I hit back to estimate and the whole line disappeared". Every other test
  asks whether something POINTS AT the account (a seed, a pin, an adjustment, a
  transfer row, an overflow end, another account's `creditTo`); none noticed a
  balance that had simply carried in, so reverting a stated balance could take
  the row away while the account still had a figure to show.
  **And when the row does legitimately go, the toast says so** (`balRowGoneNote`,
  on both Revert and Clear): emptying the last figure an account had takes its
  row off the grid, and a row vanishing from under the cursor reads as data loss
  — the donation editor's "Moved to 2025" discipline. It is measured AFTER the
  render off the same predicate the grid just used, so the message can never
  claim a disappearance the grid didn't perform.
- **A year can be built before it arrives.** `yearStarted(st, y, today)` is
  derived, never stored: a grid year has begun once today reaches its own
  first month, or once the year before it is entered through December.
  `latestGridYear()` / `startedGridYears()` skip a year that hasn't begun, so
  Progress, Retirement and Comp carry on reading the current year while
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
  **A fourth argument leaves INTERNAL transfers out** — `ui.flowNoTransfers`,
  the card's own checkbox — and the three-argument behaviour is untouched and
  still pinned, the `limitsFor` arrangement. It exists because those bars are
  routinely misread as income and spend: Charlie's 2026 read thousands high
  on both bars until his own sweeps came out — the sweep into savings and the
  part of it that came back were both in there.
  - **`internalRows(yr)` is the ONE test for "is this row internal?"**, read by
    the bars and by the note under them; two answers would put a chart and its
    own caption at odds. It needs **BOTH the Transfers SECTION and an internal
    ROLE** (`transfer`/`passthrough` with a `transferTo`), and each half rules
    out a real row the other gets wrong:
    - **the section**, because that is the reader's own statement of what the
      money IS, and the role under it is only plumbing. Charlie's DAF row is
      filed as an Expense and behaves as a pass-through into Long-term; the
      Zelle and Venmo rows are the same shape. Reading the role alone took a
      real chunk of 2026 spending off his money-out bar — and contradicted a
      call `coerceShape` had already made, since the legacy `charitable` role
      is deliberately NOT among the roles it files under Transfers while
      `zelle` is. He reported it as "I have it set as an expense, why is it a
      transfer?", which is the right question.
    - **the role**, because a Transfers-section row may behave as ordinary Cash
      money when the far side isn't tracked (a Roth IRA contribution). That
      money really left, and dropping it would understate money out by exactly
      what left.
    An absent section falls to `expense`, as renderBudget and yearSpending read
    it, so a pre-sections plan never loses a row silently; coerceShape files
    the legacy transfer roles under Transfers on the way in, which is what
    keeps an imported plan's real sweeps recognised. (`yearSpending` reads
    sections ALONE for its own reason: it must equal the Budget tab's Expenses
    total.)
  - **Interest and dividends are not transfers** and count in both settings.
  - **`flowTransferNote` asks each year whether it has any internal row**, and
    NOT whether it is a summary. That difference was found in the real data:
    the pinned 2020–2025 grids carry forty-odd categories each and not one has
    a transfer role, because the import never recorded which rows were
    transfers. A note naming only the summary years would have left six grid
    years silently unchanged beside a corrected 2026 — and a flat 2024 beside a
    corrected 2026 reads as a fact about 2024.
  - The switch lives in **`ui`**, with the folded boxes and the tab order: it
    describes how you like to READ the plan, so it syncs and follows to the
    phone, and `ui` is the branch a share link trims to three keys. NOT a
    `setting` — those travel in full, and how somebody else likes their chart is
    not something to ship them. Stored ABSENT rather than false when off (both
    in `coerceShape` and at the point of writing), so an untouched plan's `ui`
    is the three keys it has always been. Toggling re-renders the whole view
    rather than rebuilding the one chart — the card's opening sentence and the
    note both change with it — and hands focus back to the fresh checkbox,
    the trap the tab bar and year strip hit before it.
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
- **`gridToPinned()` is the step that was MISSING, and its absence was found by
  auditing Charlie's own backup for state the app couldn't produce** (2026-08-16):
  every pinned grid in it came from the import, because nothing anywhere
  assigned `model` and `startFresh`/`rolloverYear` both hard-code `'live'`. So a
  from-scratch reader could never reach a history year — and, since the Convert
  button is only offered on a non-live one, could never reach a summary year
  either. The same audit found `eoyCash` sitting on those grid years with its
  only editor on the SUMMARY card, so six real figures fed the year-by-year
  chart and the pace check while being invisible and uneditable.
  - **Offered exactly where "Mark … entered" runs out** (`canFreeze` is `live &&
    started && !canClose`), and `freezeYear` re-checks it. That is not
    politeness: an unentered month holds AUTO estimates, a pinned year computes
    none, and freezing one would blank them. Entered months have already
    materialised, so from there the change moves no figure at all — which is
    the promise the tests make (`freezing a year states exactly the balances it
    computed` compares every balance and kind before and after).
  - **A balance stated by hand is never restated** from the computed figure —
    same claim, made by the reader — and `eoyCash` is stamped only when the
    year states none.
  - **`pinnedFrom` is what it was before**, `{enteredThrough, overrides,
    eoyStamped}`, so `pinnedToLive()` puts it back rather than approximately
    back. Only a year the app froze carries one, which is why an IMPORTED
    history year is offered no Re-open button: it states its balances outright
    and has no chain to go back to. coerceShape drops a marker on a live year
    or one that can't say what the year was entered through.
    **Correcting the stamped figure clears `eoyStamped`** (in `sumyear.save`) —
    from then on it is the reader's number and re-opening leaves it alone.
  - **The rollover button is deliberately NOT gated on `live`** any more: a year
    frozen with nothing after it would otherwise have no way to build the year
    that follows, and a pinned December is all `rolloverYear` seeds from.
  - Freezing DOES change one thing and the confirm says so: `yearFlows` counts
    no interest for a pinned year, because stated balances already hold it.

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
**A box you land on has its contents SELECTED**, so typing replaces the figure
rather than running on to the end of it — one delegated `focusin` listener
(`SELECT_ON_FOCUS`), which bubbles where `focus` does not, so it covers every
field `buildFields` creates a moment before showing it with nothing to remember
when adding one. Three things it must keep doing:
- **A TEXTAREA is left alone.** A note is written over several lines and added
  to over time; selecting one on focus puts the whole thing one keystroke from
  gone, and unlike a mistyped amount there is nothing on screen to retype it
  from. The type list is a WHITELIST for the same reason — a type nobody thought
  about is left alone rather than silently swept in.
- **The one-shot `mouseup` guard is load-bearing.** A click focuses on mousedown
  and then places the caret on mouseup, which collapses the selection made a
  moment earlier: without it the feature works from the keyboard and looks
  broken with a mouse, which is how everybody would meet it.
- **That guard is attached only for a POINTER-driven focus** (`focusFromPointer`,
  set on a capturing `pointerdown`). A `{once:true}` listener left hanging after
  a Tab would sit there until the next click on that field and eat the caret
  placement of a later, deliberate one. Clicking a second time places the caret
  normally — the field is focused by then, so no focusin fires — and that is the
  way back in for editing rather than replacing.
**A save hands focus back** (`refocusEditRow` / `refocusGridCell`): the
re-render destroys the element that opened the dialog, the native <dialog>
focus-return lands on the dead node, and a keyboard reader fell to <body> and
tabbed back from the top of the page after every save — the tab bar and year
strip's trap, hit a third time. The fresh element is found by the row's own
data keys (or the cell's type/id/month); a miss (row deleted, year renumbered)
focuses nothing, which is never worse than the old behaviour.
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
**Which left the dialog unable to AGREE with itself**, and `#cellAcceptBtn`
("✓ Accept the Estimates", 2026-08-27) is the answer: agreeing meant reading
three greyed figures and typing them back in, where a slip is indistinguishable
from a real correction. `acceptedFigures(c, type, id, m)` is pure (hook +
tests) and says what the placeholders would say if typed; the handler fills only
the boxes the reader left EMPTY and then calls `cellForm.requestSubmit()`, so
there is still exactly one write path and a correction already in a box is never
overwritten. Two rules it keeps: it is offered on the same condition the
reconciliation note is drawn on (`live && cur !== undefined && !ov` — a pinned
year computes nothing to accept, and a stated month would be agreeing with
itself), and **an earning of zero is left unwritten**, because a stated $0.00 is
a claim ("it paid out, and it was nothing") and silence is not — the same
distinction the amount box makes between a stated zero and nothing recorded. A
computed balance of $0 is not in that argument and is pinned like any other. The
paycheck count gets the same button on the same reasoning; a category cell does
NOT, because its box already opens holding the estimate, so Save is that button.
The grid is keyboard-operable via `wireGridKeys()`: roving tabindex (one tab
stop for the whole grid), arrow keys between cells, Enter/Space to open the cell
editor — the table keeps its own row/column header semantics, so no ARIA grid
roles are layered on.
**Every OTHER clickable editor row is keyboard-operable via `wireEditFocus()`**
(run at the end of `render()`): each `[data-edit]` row/card and `[data-note]`
line outside `.grid` gets `tabindex="0"`, and a delegated keydown on `#views`
turns Enter/Space into the click the delegated click listener already handles.
Two rules it keeps: **no `role="button"` on a `<tr>`** (that strips the row
semantics a screen reader needs to read the table — the `:focus-visible`
outline plus the existing `title` text carry the affordance), and **a
`data-edit` that is itself a `<button>` is skipped** (its native Enter already
clicks, and a second click would call `showModal()` on an open dialog, which
throws). The grid's row labels stay out on purpose: the cell dialog's "⚙ Row
settings" button is the keyboard route to a budget row's editor, and forty more
tab stops in the label column would bury it.
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
**A field left ALONE on a row is stretched to fill it; a short row that still
has two or three fields on it is left alone.** `applyFieldSpans` does this
automatically, not opt-in, and that is the point: the gap was reported twice,
both times from the innocent act of adding a full-width field — which forces a
line break and strands whatever narrow field sat above it. An opt-in flag would
be forgotten by whoever adds the next field. Nothing in it knows which fields
exist.
**The "only when alone" half was learned the hard way (2026-08-17).** It used to
stretch the last field of ANY short row, and once every dialog went to one width
that turned into three complaints in a row — "still due looks longer than the
others", "same on nights", and the amounts in a donation. A box is capped at
320px, so an ordinary quarter-width cell shows 256px and a doubled one shows the
full 320: the stretched field ends up visibly wider than the ones beside it, and
reads as a mistake rather than as a filled row. A LONE field has nothing beside
it to look uneven against, and the stretch buys its HINT the full width instead
of a quarter — that case still earns it. **A row that ought to fill the width
says so with `cols`, which is the honest way to ask.**
It has to be WORKED OUT rather than declared: which row a field lands on depends
on how many optional fields above it are showing *at that moment*, and that
changes under the reader as they pick a different rule. `applyFieldVisibility`
calls it last, because spans are only right once visibility has settled, and it
CLEARS previous spans first — a field stretched while its neighbour was hidden
must not stay stretched when that neighbour comes back. Two traps: a closed
`<dialog>` is `display:none`, and `getComputedStyle` on that returns the
SPECIFIED grid (`repeat(2, minmax(0, 1fr))`) rather than resolved tracks, so it
bails on a zero-width grid and `openRowEditor` runs it again after
`showModal()`; and a `wide` field ends whatever row was in progress, so it
closes the row rather than consuming a column.
The **category dialog is `cols: 2`** for the same reason its role field fills:
every option in it is a whole sentence ("Repeat on a cycle (every N months)")
and a quarter of the dialog cuts them off mid-word. Half fits all but the
dividends rule, whose label interpolates two account names and is long by
nature. (It was measured against a third of the old 640px dialog; the reason
outlived the figure, and the half-column is 523px now rather than 293px.)
**EVERY dialog is one width — `--dialog-w-wide` (1100px)** — and there is no
`dialog.wide` class and no per-section `wide` flag any more (asked for
2026-08-17, after Share, then Account Settings and Donation, had each been
widened one at a time; the token already existed to stop the first two drifting
apart). One width is the rule, so there is nothing to opt into and nothing for
whoever adds the next dialog to forget — the `applyFieldSpans` bargain again.
It began with Preferences, which asks fourteen short questions each with a hint
of its own and at the old 640px stacked them into three narrow columns of
heavily wrapped prose with the thing you came to change two screens down.
Things that go with it and will look arbitrary later:
- **The 230px minimum grid track is the load-bearing half**, and it moved onto
  `.grid-fields` itself rather than a `.wide` variant. Left at the old 150px the
  extra room buys MORE columns rather than wider ones, every hint wraps harder,
  and a dialog comes out barely shorter — its height is set by the hints, not by
  the field count.
- **`cols` is layout INSIDE the fixed width, never the width itself.** `2` for a
  dialog whose fields come in pairs. `3` for a block of exactly three things to
  ask (`yearAmount`, and both windows below): auto-fit gives it four tracks and
  leaves a quarter of the row empty, with `applyFieldSpans` stretching the LAST
  box into the gap so the odd one out ends up wider than the two beside it.
  Three equal columns fill the row evenly. Anything else takes auto-fit.
  **The one thing `cols: 2` also does is NARROW the window** (`dialog.twoup`,
  700px), which is why the two long windows below had to leave it.

## Where a figure came from, said out loud (2026-09-02)

Three findings from an audit for the same fault as the `samemonth` rounding: the
app doing something reasonable and the screen not saying so. All three fixed the
same day; the audit's other three are open and listed at the end.

- **THE PAYCHECK COUNT NAMES ITS OWN SOURCE, and this one was a false sentence
  rather than a silence.** `resolvePaychecks` has three answers — the month's
  own figure, the same month a year ago, else two — and the grid's hover tested
  only the first, so every month without a figure of its own said "Estimated
  from the same month last year", including the ones that fell through to the
  default. In the app's own sample plan that is eleven months of twelve. It is
  the count a `paycheck` row MULTIPLIES BY, so two a month is 24 a year against
  a fortnightly 26.
  - It now returns `{ counts, source }`, and `computeYear` carries
    `paycheckSource` beside `paychecks` the way `balanceKinds` sits beside
    `balances`. **The renderer must READ that map**, never re-derive the branch:
    the same three-way test written twice is one that drifts, and the copy that
    drifts is the one on screen.
  - **The source travels down the year chain.** The prior year's RESOLVED counts
    are what get read, so last year's own default arrives as an ordinary figure;
    without carrying the source with it, a plan where nobody ever typed a count
    said "from the same month last year" in every year after the first, about a
    chain resting on nothing. A count somebody really typed still reads as
    `lastyear` a year later — the middle branch is not flattened into the last.
  - `PAYCHECKS_DEFAULT` — the number was typed out in the engine, the cell
    editor's value and its placeholder. `PAYCHECK_SOURCE_TIP` holds the three
    sentences; the assumed one NAMES the figure (a fortnightly reader can only
    know the claim is wrong if they can see it) and says the cell takes an
    answer.
- **BOTH AVERAGES NOW SAY WHICH MONTHS THEY ARE OVER.** `avg` said "the months
  so far", which in a year built ahead is NO months — it falls back to
  `priorYearRun`, so a fresh 2027 reads last year's average under a label
  describing an empty set. `avglastyear` said "last year" and skips any month of
  it that was itself an estimate, so on a plan entered through August it is an
  average of eight. `ruleDesc` answers for both now, which makes three of
  `RULE_LABEL`'s entries unreachable (these two and `samemonth`) — the table
  keeps them so it still lists every rule, and says so in a comment.
  - **Neither can be phrased conditionally**: `ruleDesc` is pure over the ROW and
    knows nothing about which year is on screen, so each says both halves.
  - **No em-dash inside either sentence** — the row label frames it as
    `Utilities — <desc> — click to edit this row`, and a third dash was
    unreadable.
- **The audit's other three, closed the same day**, all on one principle: the
  figure stays, the screen starts saying where it came from.
  - **A percent box reformats itself on blur** to exactly what `readFields`
    will store (`roundTo(n, f.dp ?? 2)`). Nothing is stored differently — the
    rounding was always there; what changes is that a typed 3.456 reads 3.46
    before you leave the field instead of at the next open. `link` is re-run
    after, because setting `.value` fires no input event and a derived pair (the
    bonus and its share) was worked out from the unrounded text. It is
    `asMoneyInput`'s blur, for the other kind of number.
  - **`parseMoney` reads wrapping parentheses as a minus sign.** Every statement
    and export writes a negative that way and this stripped them with the
    currency symbol, so a pasted `(500)` arrived as `+$500` — not a refusal and
    not a warning, the right number pointing the wrong way, in an app where the
    sign IS what a transfer means. Anchored to the whole string (a stray bracket
    is not the accounting form) and a minus already inside them is not flipped
    back.
  - **AND A MINUS IS NOT ALWAYS U+002D (2026-09-02, the same fault one paste
    further out).** The strip keeps ASCII only, so the MINUS SIGN a statement
    PDF, a Word table or anything set in a real typeface writes was DELETED
    rather than read: `−200` in a transfer row arrived as `+200`, and a CSV
    could carry `(130.00)` and `−120.00` on neighbouring rows and read one as
    negative and the other as positive. `MINUS_FORMS` normalises the six
    characters that ARE hyphens or minus signs by their own Unicode names —
    U+2010 HYPHEN, U+2011 NON-BREAKING HYPHEN, U+2012 FIGURE DASH, U+2212 MINUS
    SIGN, U+FE63 SMALL HYPHEN-MINUS, U+FF0D FULLWIDTH HYPHEN-MINUS — before the
    strip, so both spellings land on one code path. **The EN and EM dash are
    deliberately excluded**: they are sentence punctuation, "Rent — $500" is a
    label with a figure after it, and reading that dash as a sign would be a new
    wrong answer of the kind this exists to stop. The percent branch reads with
    `parseFloat`, which rejects all of them, so money was the outlier rather
    than the rule.
  - **The take-home tile names the rows in its denominator** (`payRowsOf`), and
    adds the sentence about "This is my pay" ONLY where a row got in on its NAME
    alone — with every pay row saying so outright there is no guess to correct,
    and explaining one would answer a question the reader hasn't got. Named on
    the actual tile and never on the projected one below it: they share a
    denominator, and saying it twice reads as two separate claims. `PAY_SLUGS`
    stays — it is the only thing that works for a summary year, whose rows carry
    no rule at all.
- **`roundToDollar` replaced `Math.round` in `samemonth` (2026-09-02), and this
  one MOVES FIGURES.** `Math.round` breaks a tie towards +∞, so an identical
  half-dollar went up as income and down as an expense — and the row that got
  the smaller figure was always the expense. Half away from zero is what a
  person means by "to the nearest dollar". A same-month row sitting on exactly
  −$100.50 read −$100 before and reads −$101 now; nothing else in the app
  rounds to whole dollars, so nothing else moved. It returns +0 for zero on
  purpose: `-0` is a value `fmtMoney` renders as "-$0.00".
- **`avg`'s fallback reads the prior year's COMPUTED cells**, estimates included,
  which is the opposite discipline from `avglastyear` ("so an estimate never
  feeds itself"). Only DESCRIBED, not changed — changing it would move figures
  in every projected year, which is the reader's call, not a fix.

## The as-of pair stacks rather than overflowing (2026-09-03)

Charles: *"fix the overflowing pill on mobile."* The Net Worth card's "as of"
switch ran past the right edge of its card at phone width — 360px of nowrap text
against a 305px card body at 375px.

- **Nothing in it could shrink, and that is by design.** Each label carries a
  month AND what that month is — "Aug 2026 · settled", "Sep 2026 · this month" —
  and `.vswitch` is `white-space: nowrap` because breaking a label at its own "·"
  reads as two separate things rather than one qualified month.
- **`flex-wrap` on the frame plus `flex: 1 1 auto` on the buttons is the whole
  fix, and it is deliberately NOT a width test.** The pair stacks exactly when
  the line will not hold it, so a reader whose browser default is 20px gets the
  stack at a width where a 16px reader does not. `flex: 1 1 auto` fills each line
  it lands on, so stacked the two segments are equal.
- **Two things CSS cannot ask about — whether it actually wrapped — are asked of
  the width instead**, at 520px, comfortably below the ~474px where the line
  stops holding it at a 16px root. Get that wrong at an unusual root size and the
  result is a radius that looks dated, never a control that runs off the card.
  - The frame **stops being a pill**: a `--radius-pill` box two rows tall is a
    lozenge whose ends curve through the buttons inside it. Segments take 2px
    less than the frame, the way the heading band does.
  - `.asofrow` **stops wrapping**, so the ⓘ stays BESIDE the pair instead of
    dropping to a line of its own. A help dot stranded under a control reads as
    explaining whatever comes next. Held to one line, the pair shrinks instead —
    which is what makes it stack.

**The test is a SWEEP, not this one control**: at 375px, nothing in `#views` on
any tab may be wider than the window unless it sits in a box that scrolls
sideways on purpose. A width that overflows is a class of bug — it arrives
whenever a label gains a word — and it is invisible on the desktop where the work
is done. The sweep found exactly one offender, which is what made the fix a
one-line answer instead of a hunt.

## Stepping between charts in full screen (2026-09-03)

**A `‹` and a `›` beside the ⤢ walk the charts on the tab without coming back
down.** Charles asked for it on 2026-09-03; built first in Flow Metrics and
ported here the same day. **This app's copy diverges from the siblings' in one
way, for the reason its ⤢ already does.**

- **The arrows sit IN THE BAND, not in the overlay.** Flow Metrics, Sprint
  Predictability and Lottery Portfolio float their arrows over the card's
  top-right corner, where nothing else lives. Here that corner is the FOLD
  CONTROL, so a cluster over it would sit on a control — the same reason the ⤢
  went into the band on 2026-08-30.
- **One nav, moved from band to band.** `maxiNav` is built once; `attachMaxi()`
  mounts it left of the ⤢ and `detachMaxi()` takes it away, so every door in and
  out — open, close, a step, and the suspend/resume a render does — is covered by
  one pair of call sites.
- **The focus is put back BY HAND after a step**, and that is the price of the
  band. Moving the nav to the next card's band drops the keyboard; the buttons
  are the same two elements wherever the nav is, so the one that was pressed gets
  it back. **And if nothing up there holds it afterwards, the new card's ⤢
  takes it** (2026-09-04): a step lands focus on the arrow that pressed it, or
  on the new card's ⤢, never on the page underneath. See the 2026-09-03 audit
  fixes at the end.
- **The way out after a step lands on the NEW card, on purpose** (2026-09-04).
  `closeMaxi` used to put the scroll back where the reader left and then focus
  the ⤢ without `preventScroll`, so after a step the browser dragged the page to
  wherever that button was — the right chart, by accident, with its top nowhere
  in particular. Charles decided the landing IS wanted, so `maxiStepped` (set by
  `maxiStep`, cleared by `openMaxi`) makes it deliberate: the card's top goes to
  `--pin-clear` (re-measured, × zoomScale), a plain `behavior: 'auto'` jump, and
  the ⤢ is focused with `preventScroll`. No step, the return point is untouched.
  See the 2026-09-03 audit fixes at the end, round two.
- **A step's click stops at the button.** `e.stopPropagation()` plus
  `pointer-events: none` on the icon — without both, the band's fold handler sees
  a click it does not recognise and folds the card, which is exactly what the ⤢
  did on the day it shipped.
- **The walk is `#views`**, which IS the tab the reader is on, because this app
  rewrites it wholesale. A `.boxshut` card is not on it — `maxiReady` already
  says a folded card has nothing to show. Read fresh on every press.
- **`maxiCard()` reads `#chartMaxi > .card`, not `firstElementChild`**: the
  overlay now holds the live region the arrows speak through.
- **`.maxi-nav` takes the `margin-left: auto`, and
  `.maxi-nav:not([hidden]) + .chart-max` gives it up.** Two elements both asking
  for an auto margin SPLIT the free space between them, and the cluster comes
  apart in the middle of the band. **The `:not([hidden])` is not tidiness** —
  without it, reported by Charles within the hour on 2026-09-03, the ⤢ jumped
  from the far end of the band to sit against the heading on every card with one
  chart on its tab. A hidden element is still a SIBLING: `display: none` takes it
  out of the flex layout, not out of the selector, so the button handed its auto
  margin to a nav that was not there to take it. The same family as
  `.chart-max[hidden]` from the other direction — there the attribute did not
  reach the layout, here it did not reach the selector. Pinned by RECTANGLE in
  the suite, because a margin is only visible as geometry.
- **The print rule names `.maxi-nav` explicitly.** The siblings' arrows are
  inside `#chartMaxi`, which print already hides; these are not.
- **The arrow-key handler skips ARIA ROLES, not just form controls.** Found here
  the same day: the Net Worth card carries its "as of" radio pair INSIDE the
  card, so it is still on screen and still reachable while that card fills the
  window — and Right both moved the month and stepped the chart. A
  `<button role="radio">` is not an `<input>`. The guard now names radiogroup,
  tablist, listbox, menu, menubar, slider, spinbutton, grid and tree, and **the
  same list went into all four apps**, because the next such control will be the
  same shape and nobody will remember this.

Its own `t()` with its own 1280x900 frame. **A test that holds a card across a
render is holding a node that no longer exists**, so the assertions after the
re-render compare NAMES.

## The three long windows are laid out in SECTIONS (2026-09-02, Preferences 2026-09-03)

`category` (Budget Row) and `account` (Account Settings) were `cols: 2` and
therefore 700px, and Charles read them as "getting pretty long, depending on the
options selected". They were: a budget row with a sweep rule and a due date on it
ran **1,877px** — nearly three screens — and an account 1,045px, both in a window
half the width of Preferences sitting beside them. Now: the common 1100px, three
columns, and cut into blocks with a rule and a small heading between them.

- **Three columns, not the four auto-fit chooses**, and the old `cols: 2` note's
  reason is why: the options here are whole sentences ("Repeat on a cycle (every
  N months)", "Sweep what an account holds above a goal") and a quarter of 1100px
  cuts them mid-word. A third is 340px, **wider than the 320px cap every box in
  the app is held to** — so no box is a pixel narrower than it was at 700px and
  nothing that read before stops reading. Measured, not guessed: the longest
  option strings are `role` 368px, `goalId`/`capGoalId` 323px, `rule` 312px, and
  a 320px select shows about 282px of text, so `role` was already clipped at the
  old width. **That clipping is untouched and is not what this change was
  about** — fixing it means either a second box cap (a box that doesn't match
  the ones beside it reads as a mistake) or shorter option sentences.
- **`{ sec: 'Heading' }` in a spec is the marker**, and everything after it goes
  in that block until the next. It is OPT-IN and invisible to a spec with none:
  with no marker `#rowFields` IS the grid exactly as it was, which is why the
  other seventeen editors needed no thought. With markers it becomes a plain
  block of `.fieldsec`s, each holding a grid of its own.
- **Each block lays out ON ITS OWN, and that is the mechanical half of the
  point.** A block that ends on a short row ends there, instead of pulling the
  next block's first field up beside it and putting the rule through the middle
  of a row. `applyFieldSpans` iterates the grids; `spansInGrid` does the work.
- **A block whose every field is hidden is GONE, rule and heading with it.** A
  sweep row has no money-moves questions left — the rule dictates both — and a
  heading standing over nothing is worse than the fields being missing.
- **`.fieldsec` is `.manage-sec`'s rule to the token** — `--sp-7` above and
  below, `1px solid var(--border-strong)`, first one takes the spacing and not
  the rule; the heading is `.manage-head`'s three values (`--fs-sm`,
  `--fw-semibold`, `--text-primary`). Sprint Predictability, Golf Handicap and
  the dashboard carry that block, written the same week after Flow Metrics'
  Settings window was read as "big and a bit hard to read". **Keep it in step
  with those three.** The name differs only because these hold a field GRID.
- **A sectioned dialog is never `twoup`**, and `applyFieldSpans` only re-toggles
  that class for a grid that fills the dialog (`ownsDialog`) — with several
  grids, no one of them can be asked what the window should be.
- **A marker is not a field, and `readFields` must step over it BEFORE anything
  asks it for a type.** It has no key, so `rf-undefined` finds nothing and
  reading `.value` off that throws — taking the whole save with it. `openRowEditor`'s
  `inRow` count excludes markers too, or an editor with two fields and a marker
  would seed itself two-up.
- **Four fields MOVED, and each was in a block it had nothing to do with:**
  `isPay` ("this is my pay") sat under the projection rule and moves no figure
  the grid computes — it only tells the Giving tab how to count the row, so it is
  a fact about what the row IS. `until` and the note sat after the due block,
  which put them inside "When It's Due" — the one block `until` has nothing to do
  with, under a heading that would suggest it only applies to a bill with a date.
  In the account window, `seed`/`until`/`hub` sat after both rate blocks, which
  put "is this the main account?" under a heading about dividends.
  **`until` is no longer offered while ADDING a budget row**: last in a flat list
  it was out of the way; third in the first block it was the third thing you read
  while creating a row. The account editor already drew its own only on an
  account that exists — this is that rule applied to the other half of the grid.
- **`name` dropped its `wide` in the account window.** A spanning cell holds its
  BOX to one column (`holdBox`), so the span bought 340px of nothing beside a
  320px box at the old width and would have bought 780 at the new one.
- **The headings are meant to read as a SET**, and the first one deliberately
  does not repeat the window title two lines above it: *What It Is · Future
  Months · How The Money Moves · When It's Due*, and *What It Is · Interest ·
  Dividends*. The account's two rate blocks are three questions each — a rate,
  what that rate is, where it goes; then a rate, where it goes, how often — and
  that pair filling a row exactly is what settled on three columns.
- **PREFERENCES WAS MISSED BY THAT PASS AND TOOK THE SAME TREATMENT A DAY LATER
  (2026-09-03).** Charles asked why the family's preference windows were ruled
  and this one wasn't; it wasn't, and it is the window that needed it most —
  sixteen settings, four to a row, with nothing but a fresh subject in the label
  to say a new group had started. Five blocks: *Your Plan · How Figures Read ·
  What Each Tab Offers · Rates The Plan Assumes · This Device Only*.
- **`This Device Only` is a heading that makes a CLAIM, and that is what its test
  guards.** `pinBars`, `zoom` and `priceApiKey` live in their own localStorage
  keys — never synced, never in a backup, never in a share link — while `Rates
  The Plan Assumes` directly above it holds four figures that travel with the
  plan. Each of those three hints used to have to say "this device only" alone,
  from three different places in one flat grid. A fourth field landing in that
  block, or one of the three leaving it, makes the heading a false statement
  about where the reader's data goes: `tests.html` pins the block's contents by
  name AND pins `get()` reading them from `savedPin()`/`savedZoom()`/`priceKey()`
  rather than from `state.settings`.
- **Sections RETIRED three layout arguments the spec used to make.** The zoom,
  the lead days and the pin were each PLACED — and two of them made `wide` — for
  a reason that had nothing to do with them: an ordinary field added above the
  three retirement rates shifted them by one column and stranded the first at the
  end of the row above, away from the two it is read against. Each block lays out
  its own grid now, so a field can no longer strand a field in another subject,
  and all three sit where their subject puts them. What still holds: **a `wide`
  field ends the row in progress, so one belongs at the top or the bottom of ITS
  OWN block, never in the middle** (`tagline` and `pinBars` open their blocks,
  `dueLeadDays` closes its own).
- **`cols: 4` and `.cols4` (new) — a sectioned window must DECLARE its column
  count.** Auto-fit sizes each block by its own field count, so "How Figures
  Read" (two questions) came out in two half-width columns directly under a block
  drawn in quarters: one window in two layouts, which is exactly what
  `openRowEditor`'s note calls two windows stacked. Four is the first count that
  needs a step on the way down — it is the only one whose columns are narrower
  than a box at the common width — so `.cols4` goes 4 → **2** at 900px → 1 at
  560px. Two, not three: an even split leaves no block ending on a lone field
  beside a gap. `cols2`/`cols3` are untouched.
- **A real frame is what pins it.** `tests.html` opens all three windows in a
  1280x900 iframe and reads the width, the column count of every block, and each
  block's contents by name — a 1x1 frame reads every rectangle as 0 and "it is
  1100px wide" would pass on a window that was never laid out.
- **`#shareDialog` sets no width of its own.** Its two side-by-side panels and a
  link readable in one line are what the common width buys; its own 760px
  two-column breakpoint is untouched, so a phone still stacks as before.
- **`#searchDialog` is 700px on 18px of padding, and every property of it is
  pinned in one block that all six apps carry verbatim (2026-08-23).** It was
  360px sized to a 320px box — the window WAS the box, asked for 2026-08-17 —
  and the box is now the full width of the list under it, which is what a 700px
  window makes right. See the shared note below.
- **THE WINDOW ITSELF IS PINNED, PROPERTY BY PROPERTY, AND THE SAME BLOCK IS IN ALL SIX APPS VERBATIM (2026-08-23).** 700px on 18px of padding — the Back Up & Restore window's size, the family's other fixed-width window — with the heading, the intro line, the box, the hit and its three lines, and the "Nothing matches" line all declared inside the `#searchDialog` block rather than borrowed from whatever quiet-text class the app happens to have. That borrowing is what made one window into six: 360px and 420px wide, a 320px box inside a 360px dialog, a hittab at `--fs-sm` here and `--fs-xs` there, `.04em` typed out beside `--ls-label`, and four different colours on the same sentence. A change to any of it belongs in all six. Two details worth keeping: `#searchDialog > p` is the DIRECT child only (the results list's message is a `<p>` too, and an id in that selector would out-rank `.searchresults .hint` and hand it the intro line's colour), and the block deliberately declares NO dialog chrome — backdrop, shadow, a field's touch-height floor, and the max-height Money Map divides by its own zoom all belong to the app's `dialog` rule and are shared with every other window it opens.
- **A HELP BODY IS AN ARRAY OF PARAGRAPHS, NOT A STRING** (2026-08-23), and a paragraph is
  an array of runs: a plain string, or `b('…')` for bold. `renderHelpBody` walks it with
  `createElement` and `textContent`, so **no part of this is ever parsed as markup** — which
  is the whole reason the shape exists. Five sibling apps write their help as HTML literals
  and are right to; this app holds household names and every figure of a family's finances,
  and the standing rule that help text is copy and not a template was worth keeping. It cost
  one nine-line renderer and bought paragraphs and bold anyway, so there was no trade to
  make. Flow Metrics carries the same pair for the same reason.
  Every entry was ONE paragraph of 200–1,400 characters until this date, which is a wall on
  a phone. Bold carries the thing being defined or the load-bearing claim, **at most one per
  paragraph** — `tests.html` pins that bold stays a minority of the runs, that no paragraph
  is entirely bold, that a body over 450 characters has a break in it, and that every run is
  a string or a `{ b }`. Short entries are deliberately left whole: three sentences split
  into three paragraphs is its own kind of unreadable.
- **EVERY dialog closes on a backdrop click, and `tests.html` enumerates them out of the
  markup rather than from a list** (2026-08-23). `compareDialog` had been missing from the
  registration list — read-only, one Close button, nothing about it that wanted an exception
  — and a hand-written test would have gone on agreeing with the hand-written list. **The
  one documented exception is family-wide and it is `syncChoiceDialog`**: "which copy of
  your data?" has no safe default, so it must be answered rather than dismissed, and the
  test pins that it stays excluded as well as that everything else is included.
  The handler requires **both the press and the release outside**, and tests the pointer
  against the dialog's BOX rather than trusting `e.target`: a click on the backdrop reports
  the dialog as the target, but so does one on the dialog's own 20px of padding. Both
  lottery pages shipped the naive version and had to be fixed the same day.
- **`#helpDialog` is the exception, and the READING MEASURE is what sizes it
  (2026-08-23).** It is the one dialog that is nothing but prose, so `#helpBody`
  (a `<div>` since the bodies became paragraphs — a `<p>` cannot hold them)
  is held to 66ch — at the full 1100px its lines ran to about 150 characters,
  roughly twice a comfortable measure — and the window is `width: fit-content`
  so it takes that measure rather than the common width. The cap came first and
  on its own it only moved the problem: the lines read, but the paragraph hugged
  the left of a 1100px box built for four columns of figures with half the
  window empty beside it, which is the `.twoup` complaint in a dialog with one
  column. Both rules or neither — drop the 66ch and `fit-content` grows the
  window back to 1100px and the 150-character line with it. `max-width` is
  restated as `calc(100% - 32px)` because the base `dialog` rule's `width` is
  the thing being overridden; a phone gets the screen less its margin, as
  before. Left-aligned, unlike `.empty`, because a heading and a button anchor
  the left edge and centring the paragraph would set it adrift of both. All 42
  entries open at the same 666px — the shortest still runs several lines at this
  measure — so the window does not resize as you read your way round the app.
  **WIDTH IS SETTLED; HEIGHT IS THE ONE STILL WORTH WATCHING.** `max-height:
  calc(100vh - 32px)` is the other cap, and an entry long enough to hit it opens
  a window that scrolls — which reads as one whose second half nobody gets to.
  Measured 2026-08-27: the prose runs about 0.35px of height per character at
  this measure, so roughly 2,600 characters is what a 950px-tall window can
  show and about 1,900 is what a 720px laptop can. `monthDue` was 3,539 and
  stood 1,249px tall; it is two entries now (see the due block, below).
  `tests.html` pins a 2,600 ceiling per entry. **The fix when one reaches it is
  a SECOND DOT beside the second heading, never a wider window** — the measure
  would have to go to 106ch to fit an entry that size, which is a 128-character
  line, and the measure is there precisely to stop that. `monthRows` (2,000
  characters) still scrolls on a 720px screen and is the next candidate if it
  grows.
  `tests.html` pins the pair, and pins the HELP table against the dots that open
  it in both directions: a key with no entry opens a sheet with no words in it
  and nothing on screen can say so, and an entry no `helpBtn` points at is a
  second copy waiting to drift. `HELP` is on `__finTestHooks` for that.
  **BOTH RULES ARE FAMILY-WIDE AS OF 2026-08-23, AND SO IS THE `.tile-help` DOT
  BLOCK ABOVE** — the same declarations are in Sprint Predictability, Flow
  Metrics, Golf Handicap and the NY calculator, and a change to any of them
  belongs in all five. Two things moved in this app to get there. The type came
  out of a `style` attribute on the `<p>` and into `#helpBody` in the block, and
  the `.helpbody` class went with it: a shared block cannot key off a class only
  one app has. And **the dot's hover is Flow Metrics' now, not this app's** — it
  fills with `--surface-alt` where this app reached for `--focus-border`, which
  says "focused" to anybody reading the two states side by side. The third rule,
  `#helpBody p, #helpBody li { font-size: inherit }`, does nothing here (the box
  IS the paragraph) and is carried anyway so the block stays whole; Golf Handicap
  and the NY calculator write real `<p>` tags into theirs and need it.
  **THE TYPE, THE COLOUR AND THE PADDING ARE IN THE BLOCK TOO** (2026-08-23, a second pass
  after Charles spotted differences between the windows). Measured across all seven windows,
  four things were drifting on inheritance alone: the heading came out at **700** on the two
  lottery pages, where nothing sets a weight and an `<h2>`/`<h3>` defaults to bold; the prose
  came out at `--text-primary` on the NY calculator, where no `dialog p` rule reaches it, so
  it read brighter than everywhere else AND its `<strong>` had nothing to contrast with;
  Golf Handicap's paragraphs were spaced by the browser's 1em (15px) against 10px elsewhere;
  and the window's own padding was 24px there and 18px in PAPTrack, which is what made three
  different window widths out of one measure. `#helpTitle`, `#helpBody`'s colour, the
  paragraph margins, `#helpBody strong` and `padding: 20px` are all declared now, so none of
  it depends on what the app happens to style a dialog with. All seven windows are 666px.
- **A dialog laid out TWO-UP is narrowed to 700px** (asked for 2026-08-17), and
  only two: three and four columns already fill the common width, and a single
  column never had the problem. At 1100px a two-question dialog put each box at
  the left of a 523px half with 200px of nothing beside it, which read as adrift
  rather than as roomy. 700px is the layout written out — 20px padding, a 320px
  box, 20px, a 320px box, 20px padding — so the space either side of the pair
  and between them is the same; `dialog.twoup` also widens the COLUMN gap to
  that 20px, leaving the row gap alone since that is vertical rhythm.
  The class is set from the RESOLVED grid in `applyFieldSpans`, which is the
  only place that knows how auto-fit landed, and seeded from the spec in
  `openRowEditor` so the dialog opens at its final width instead of snapping a
  frame later. It is only ever on `rowDialog`: Share, Back up, the help sheet
  and the rest keep the common width.
- **Count columns by DROPPING zero-width tracks.** `auto-fit` lays out as many
  tracks as fit and collapses the ones nothing lands in, so a two-field section
  reads back as `"523px 523px 0px 0px"`. Counting the string's words says four,
  which makes every row look short to `applyFieldSpans` and puts its
  one-column measure on a track that isn't there. Only tracks with a width are
  columns — which is also what makes the two-up test above true for a section
  that never asked for `cols: 2`, like the PTO year.
- No media query is needed: `width: calc(100% - 32px)` already wins on a small
  screen and auto-fit falls back to one column at 375px, where `twoup` resolves
  to false on its own.
**A BOX IS SIZED BY ITS INPUT TYPE, never by a per-field setting** — text,
money, number and select all 320px, date/month 180px, all of them a `max-width`
OVER the existing `width: 100%`, so a narrow column still wins and nothing can
push a box past its own cell. It is the `applyFieldSpans` bargain a third time:
an opt-in width is the one whoever adds the next field forgets, and then that
field is the odd one out. 320px is where it is because it takes the longest
thing any text box here really holds — a 32-character API key, whole.
**A NUMBER used to be 130px and no longer is (2026-08-17).** That figure was
right while a dialog was 640px and a column a third of it — a box the length of
a paragraph asking for four characters reads as though the app expects far more
than it does. At the common 1100px a column is ~255px and the reasoning stops
paying: a share count sat as a stub with a gap between it and the price beside
it, and the two percentages in the contribution figures were half the width of
the salary box next to them. Both were reported as boxes that don't line up, and
**consistency across a ROW is what a form is read by**. The cap survives only to
stop a box running the whole width of a two-column dialog.
**A DATE was 180px and no longer is either.** Same reasoning, same outcome: a
date box does have a fixed natural content width with a picker glued to its
right edge, so widening it only opens a gap between the text and the icon — and
it lost anyway, because in a donation the Date box was visibly shorter than
Foundation, Event and Cause on the same line, and one short box in a row of four
is more obviously wrong than a little air inside it.
**A cell that SPANS the row keeps that width for its hint and not for its box.**
`applyFieldSpans` writes an inline `max-width` of one column onto the box in any
spanning cell — a `wide` field, or a lone field it stretched — so a long
explanation still reads across the dialog while the box matches every other box.
It clamps to the SMALLER of the column and the stylesheet's own cap, which is
not fussiness: at two or three columns a column is wider than the cap, and an
inline width set to the column would override that cap upwards and make the box
bigger than its neighbours — the very fault it exists to fix.
**The HINT keeps the full column width** and that is the point of the split: the
long measure is what holds these dialogs to a few rows. A checkbox (sized by the inline style that
centres it) and a textarea (prose) are caught by neither rule. The category
dialog's documented reason for `cols: 2` survives it — 320px is wider than the
293px half-column those sentence-long options were measured against.
**A `wide` field belongs at the TOP or the BOTTOM of a section's list.** It ends
whatever row is in progress, so one in the middle strands its predecessors on a
row of their own — Preferences' subtitle sat second and left the filing-status
select alone, stretched across the whole dialog by `applyFieldSpans` to hide the
gap. Preferences' own order is otherwise by SUBJECT, nearest thing to nearest
thing: the household and tax questions, then how figures and rows read, then the
three switches that turn a tab's machinery on, then the dividend fallback rate,
then the three retirement rates, and last the price key.
**It bit `donation` the moment that dialog went wide, which is the lesson worth
keeping: a mid-list `wide` field is INVISIBLE at 640px and only shows up when
there are enough columns for it to break.** `foundation` sat second and carried
`wide: true`; at four columns it stranded Date alone on a full-width row and split
the three amounts two-and-one, when the dialog's own sub-line tells you to choose
between those three. Dropping the flag cost the field nothing — a text box is
capped at 320px by type either way — and fixed both. Check every `wide` field in a
section before widening its dialog.
**`donation`'s two checkboxes sit together on the closing line, after the
note.** They were briefly split — one riding the end of the amounts row, the
other alone underneath — which made the three amounts read as four things and
gave a lone checkbox a row of its own. The note is `wide`, so it ends its row
and the two ticks start a fresh one: two questions ABOUT the donation, asked
together after everything the donation is.
**The zoom is the exception and is placed by LAYOUT, not by subject** — it
belongs to no group, so it is the one field that can be spent closing a row.
Without it the three retirement rates start one column short of a fresh row and
`retirementReturnAnnual` is stranded at the end of the row above, away from the
two that are read against it: "if it goes worse" and "if it goes better" mean
nothing except beside the figure they are worse and better than. **Anything
added to the group above the zoom must keep that in step.** The alignment is
exact at four columns; a narrower dialog wraps as it always did.
A field spec may be **`type: 'readout'`** — a figure the dialog WORKS OUT and
the reader never types. It renders as a `<p class="field-readout">` rather than
an input, so `readFields` skips it (a `<p>` has no `.value` and asking for one
throws) and nothing about it reaches `save()`; it is filled by `link` like any
other derived box, so it keeps up as you type. Its label uses
`aria-labelledby`, not `for`, because `for` cannot point at a `<p>`. It obeys
the rule that computed values are never persisted — this is the read-only end of
the same principle the balance branch applies with placeholders.
The **holding editor** uses two: Value (shares × price) and Share of account.
The dialog opened by saying "value is shares × price" and then never showed it,
and the second readout is measured against the pane as it WOULD be once saved —
every other row as stored, plus whatever is in the boxes right now — because a
share worked out against the old total disagrees with the table at the exact
moment it is being read. Both show an em dash, never `$0.00`, while a box is
empty: a half-filled row has no value yet, and a confident zero is a different
claim from "you haven't said". Its lookup checkbox is labelled "Look its price
up", NOT "…automatically": the longer label measured 193px into a 191px column,
wrapped, outgrew `label.field`'s `min-height: 2.5em` and pushed its checkbox
below the two figures beside it. The column is over 230px now that every dialog
is the one width, so that particular label fits — but the FAILURE MODE is the
thing to remember, not the figure: a label that wraps outgrows the two-line
allowance and drags its control out of line with its neighbours. Measure before
lengthening one.
A field spec may carry an **`action`** — a small button beside its box for a
move you'd otherwise make by hand across two fields, like the trip line's
"✓ Paid" folding Still due into Paid. It edits the FORM, like `link` does, so
nothing commits until Save; `type="button"` keeps it from submitting. The CSS
puts it UNDER its input, because alongside it shortens that one box and leaves
the row ragged against its neighbours.
**Budget rows drag into place within their section** (`wireRowDrag`), the same
gesture as the tab bar and for the same reason — pointer events, not HTML5
drag-and-drop, which does nothing on a touchscreen. It takes three lessons from
the tabs: the capture goes on a container that never moves (`tbody`), because
`insertBefore` detaches the dragged element and a captured element leaving the
document loses its capture; the row is only picked up after 6px of travel, so an
ordinary click still opens its editor; and only the LABEL cell is a handle,
since every month cell already opens a cell editor of its own.
**One thing it does differently on purpose: the capture is taken when the drag
STARTS, not on pointerdown.** The tab bar owns its own clicks, but a row label
is routed by the delegated `data-edit` listener on `#views`, and a captured
container swallows the click that listener needs — capturing up front meant a
label that no longer opened its editor. For the same reason the trailing click
cannot be swallowed on the tbody: `render()` replaces that element before the
click arrives, so `rowDragEndedAt` tells the delegated listener to skip one.
**Accounts drag the same way**, in their own `data-sec="accounts"` group, and
the two lists cannot be dragged into each other. They are ONE list shared by
every year (`settings.accounts`), so reordering them in 2026 reorders them in
2019 — an account has one place in the plan — whereas budget rows are per year
and carry their new order into the years built ahead. Accounts are NOT gated on
`rowSort`, which sorts budget rows only. Both use `moveInList(arr, id,
beforeId)`; `moveRowBefore` is just that applied across a list of years.
`data-move` names the thing being moved in whichever list it belongs to, and
`data-sec` is the whole permission model: no stamp, no drag. It is absent under `rowSort === 'alpha'` (a display sort over an untouched
stored order — a row dragged there would spring back on the next render) and in
`viewOnly`. `moveRowBefore(yrs, id, beforeId)` is the persistence, and it is NOT
`swapRows`: a drag lands a row anywhere, which two neighbours trading places
cannot express. It matches by ID against each year's own list, never by index —
the years ahead are a rollover snapshot and a row can sit at a different
position in each — and it finds the destination AFTER removing the row, because
taking it out shifts everything below it up by one.
**Touch scrolls rather than drags, deliberately.** No `touch-action` is set on
the label, so a finger still scrolls the grid; the ↑↓ buttons in the row editor
remain the touch and keyboard path. Blocking `touch-action` on the pinned label
column would have cost vertical scrolling to gain a gesture that already has a
working alternative.
Deleting a budget category also deletes its orphaned cells — keep that.
**Every dialog sets `overscroll-behavior: contain`, and it is not cosmetic.** A
scroll container that has run out of scroll hands the rest of the gesture to its
parent, so reaching the foot of a dialog carried straight on into the page behind
it — the plan scrolling away under a dialog still open and still covering it.
Reported on a phone, where a dialog nearly always scrolls and the gesture is a
flick that does not stop at the boundary. `contain`, never `none`: the dialog's
own scrolling is untouched, only the hand-off is. **A new scrollable region that
sits OVER the page needs the same.** The inner `.checklist` deliberately does not
have it — chaining from it to the dialog around it is wanted, and the dialog is
what stops the page. Mirrored into Sprint Velocity, Flow Metrics and Golf
Handicap, which all carried the same default.
**Verifying this needs a real device, and the desktop preview pane will lie to
you.** Its synthetic scroll events are not hit-tested to the element under the
cursor — they go straight to the document, so the page moves and the dialog never
does, which looks exactly like the bug whether or not the bug is there. It was
reproduced, and the fix confirmed, in real iOS Safari on the simulator: same five
swipes, two of them past the dialog's end, then close and see where the page is.
**The toast is a POPOVER (`popover="manual"`), and that is the only way it can
be seen while a dialog is open.** A modal `<dialog>` sits in the browser's TOP
LAYER, which paints above every z-index in the ordinary document, so a toast
fired from an open dialog was drawn under it AND under its 55%-black backdrop —
invisible, indistinguishable from a button that does nothing. It was reported
that way, about the Share dialog's "Copy link", which is the case that has to
work: copying deliberately leaves the dialog open, so the toast is the only
thing that says it happened. **Anything else that has to appear over a dialog
needs the same treatment** — a bigger z-index cannot reach the top layer. Four
things `toast()` keeps doing: it raises the popover BEFORE writing the text (a
popover is `display:none` until shown, and a live region announces a change it
was present for); it reads a layout property in between, or the `display` flip
means the `opacity:0` state is never painted and the fade is skipped; it drops
out of the top layer 250ms after fading, so a spent toast is never parked above
whatever opens next; and it is `manual`, so nothing else can dismiss it and
Escape still belongs to the dialog underneath. The CSS undoes the UA's own
`[popover]` rules (`inset: 0`, `margin: auto`, a border and a background), which
would otherwise park it in a box in the middle of the screen. On a browser with
no popover support the attribute is inert and the toast is exactly the fixed
element it always was. **The same fix belongs in Sprint Velocity, Flow Metrics
and Golf Handicap** — all four share this chrome and all four had the bug.
- **Mirrored into Sprint Predictability, Flow Metrics, Golf Handicap and the two
  lottery calculators on 2026-08-20**, block for block. Two of those needed
  something this file did not: a single-line PROSE field that the TEXTAREA rule
  cannot catch (Golf's round note, PAPTrack's supply note), so the shared block
  now honours a `data-keep-caret` attribute as a by-hand opt-out. Nothing here
  carries it — every prose box in Money Map is a real TEXTAREA — but the
  attribute is wired here too so the block stays identical across the family.

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
- **Syncing the key was weighed and turned down (2026-08-26).** In `state` it
  would leave a plaintext copy in the Firestore doc — and since that doc is one
  opaque JSON string, no rule could ever protect the key on its own — plus a
  copy in every backup file, one careless line from `settings` and therefore
  from every share link. Encrypting it first (a passphrase through PBKDF2 into
  AES-GCM) closes the at-rest hole honestly, but it swaps typing a key per
  device for typing a passphrase per device and buys a forgot-passphrase path,
  a ciphertext version and a rotation story with it. For a free, read-only,
  quota-limited key that is a bad trade.
- **What carries it between devices instead is the BROWSER.** The Preferences
  field is `type: 'password'` — masked, `name`d, `autocomplete="current-password"`
  — so a password manager offers to save it and iCloud Keychain (or its
  equivalent) syncs it end to end encrypted, on a path this app never touches.
  `current-password` and not `new-password`: this is one existing key re-entered
  on a second device, and `new-password` makes Safari offer to invent one.
  `spellcheck=false` + `autocapitalize=off` + `autocorrect=off` are iOS, which
  otherwise capitalises the first letter of a 32-character key and autocorrects
  the rest — and the only report of that arrives a day later as "Twelve Data
  rejected the API key".
- **`password` is a field type in `buildFields`, not a one-off.** It carries a
  Show/Hide button in the same `.field-row` the action fields use (a masked key
  you cannot read back is a typo you cannot find), the button is `type="button"`
  so it never submits the dialog, and its accessible name is `${word} ${f.label}`
  with the visible word FIRST so voice control still matches what it can see.
- **It also carries a clipped ACCOUNT NAME (`autocomplete="username"`), and that
  is a bug report, not a nicety.** Charles's first real Safari save (2026-08-26)
  filed the key under the field NEXT DOOR as its username. Preferences is one
  `<form>`, so every text box in it was a username candidate and the manager took
  the nearest — which would change again the day somebody reorders the dialog. A
  password-only form has to name its own account. The field is `readonly`,
  `tabIndex = -1`, `aria-hidden`, and carries no `name`, so it reaches no
  submission and `readFields` (which looks up by id) never sees it.
- **The `.sr-only` goes on a WRAPPER `<span>`, not on that input** — on the input
  it LOSES: `.grid-fields > div > .field-row > input` is the more specific
  selector, so the "1px" field computed to 20×40. Clipped, so it looked right on
  screen while occupying a real 40px of the flex column. A clipped wrapper is
  absolutely positioned, so the input inside is invisible at any size and out of
  the flow entirely.
- **`input[type="password"]` had to be added to the 320px `max-width` list.** That
  figure was measured on THIS field — a 32-character key held whole — and changing
  its type silently dropped it out of the rule that exists for it. A test pins it.
  The field stays LAST in Preferences partly for this: a password cell is a row
  taller than its neighbours, and the last row is the one place that costs
  nothing. A test pins all of it against the source — the dialog is built from a
  spec at open time, so none of it is reachable through the hooks.
- **The CACHE, unlike the key, is `state.quotes` and therefore SYNCS** (asked for
  2026-08-17). The six-hour clock is a fact about the QUOTE, and the quote is the
  same on every device — left in localStorage it meant the laptop fetched a
  price, the phone received the price (holdings are state) but not its
  timestamp, judged the lot stale and spent the allowance fetching it all again.
  Things that hold it together:
  - **The key stays local and must never follow it.** That is the security rule
    above, not an oversight, and it is why the two live in different places
    despite being one feature. The consequence is worth knowing: a second device
    with no key still shows the synced prices and their "as of" line, and simply
    cannot refresh — which is the right trade.
  - **Top level, not `settings` and not `side`.** `settings` travels in FULL in
    every share link, and the cache is a list of the tickers somebody holds;
    `side` is tab data gated by SECTION_NEEDS. `buildSharePayload` assembles from
    a WHITELIST of top-level keys, so being top-level and unlisted keeps it out
    of a link by construction. There is a test on the placement, because the
    whitelist itself can't be reached from the harness.
  - **`coerceQuotes` is the boundary** — pure and pinned. A price is read
    STRICTLY, never through `num()`: a corrupt field turned into a
    deliberate-looking 0 is copied straight onto a holding by the write-back in
    `refreshPrices`, and a $0 holding is a wrong figure that looks like a real
    one. A `noQuote` marker carries no price. No `ts` means no clock, so the
    entry goes. **A ts more than an hour in the FUTURE is dropped** — this is the
    one field where another device's clock reaches ours, and a badly-set one
    would otherwise pin a price as "fresh" for years, since `freshWithin`
    measures `now - ts`.
  - **`coreOf` nulls `quotes` alongside `ui`**, or a quiet pass that learned
    nothing but a "no quote" marker mints an undo entry and ⌘Z walks back
    through lookups before reaching the edit somebody regrets.
  - **`writeQuoteCache` returns whether anything MOVED, and `refreshPrices`
    saves once** for the cache and the price write-back together. Without that a
    quiet pass pushes a byte-identical document to Firestore on a timer.
  - **The run report `fin-quote-run` deliberately stays local.** It says what
    happened on THIS device a moment ago — throttled, out of credits, offline —
    and `runIsToday`/`runIsRecent` age it; syncing it would have the phone
    announce a throttle it never hit against an allowance it never spent.
  - `adoptLegacyQuoteCache()` folds a browser's old `fin-quotes` in ONCE and
    removes the key. Entries already in state win (they came from a device on
    the newer arrangement), and a second run is a no-op, so a failed removal in
    private mode costs nothing.
  - Adopting a cloud copy written by a build that predates this EMPTIES the
    cache, because `finAdopt` assigns top-level keys wholesale and old builds
    carry no `quotes`. That costs one refresh, never a figure — the prices
    themselves live on the holdings — and it stops once both devices are current.
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
- **A NEWLY TYPED TICKER is looked up on the spot, on its own**
  (`refreshPrices(false, [ticker])` from `holding.save`). The six-hour cache is
  about the QUIET pass — it exists to stop the automatic top-up spending the
  allowance re-asking about prices that cannot have moved — and typing a ticker
  in is not the quiet pass; it is a deliberate request about one holding, as
  much as pressing Refresh is. Without it a new row sat at $0.00 until something
  else happened to trigger a batch, which reads as the lookup being broken.
  Three things keep it honest:
  - **Only when the TICKER is new or changed.** Correcting the share count on a
    row whose price you typed over yourself must not fetch over the top of it —
    that figure is a decision, and this dialog's provenance hint exists to
    record it.
  - **A named run writes back ONLY the tickers it fetched.** A whole-table
    refresh still restates every holding with a fresh quote, which is what
    pressing Refresh asks for; looking up one new ticker must not quietly
    restate a price you typed over elsewhere on the tab.
  - **`pendingLookups` remembers a named ticker asked for while a run is in
    flight**, and the finishing run kicks it off. A quiet background pass
    routinely holds the latch at exactly the moment a ticker is typed, and the
    run in flight was assembled before that ticker existed — dropping it there
    made the feature look intermittent, which is the worst way for it to fail.
- **The manual button also ignores the six-hour cache** (`stalePrices()` takes a
  TTL; a press passes `MANUAL_FRESH_MS`, two minutes, instead of
  `QUOTE_TTL_MS`). The six hours only ever existed to stop the AUTOMATIC pass
  spending the allowance on prices that can't have moved — refusing a deliberate
  press with "everything is less than six hours old" is the app arguing with an
  instruction. **The two minutes are not a token gesture and must not go to
  zero**: when a batch stops at the per-minute limit, the next press is how you
  carry on, and re-asking from the top would spend the whole next minute
  re-fetching what the last press already got and never reach the holdings it
  missed. Long enough for that hand-over, far too short to be a cache.
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
All three long-run charts (on the Progress tab) carry a `.chartkey` under them for the dashed projected
outline — the signal was explained only in the prose above the chart, which is
not where you look when wondering why two bars are drawn differently. Its swatch
is neutral, not either series colour: the DASH is the meaning.
**`yearSpending(yr, computed, y)` is a different question from `yearFlows`, not a
slice of it.** Money out counts every dollar that moved, transfers between the
reader's own accounts included, so a year that swept $40,000 into the brokerage
reads as a $40,000 year — which is why "what did I spend" needed its own figure.
It reads the row SECTIONS (`expense` and nothing else, unsectioned falling to
`expense` exactly as `renderBudget` does) rather than re-deciding what counts,
and that is the load-bearing part: the bar must equal the year's **Expenses total
on the Budget tab**, which the sub-line promises out loud and which was checked
against Charlie's real 2024/2025/2026 to the cent before shipping. Rows are
NETTED across the year, so a refund reduces what the year spent. A summary year
has no sections — the old sheets predate them — so it falls back to everything
that went out, i.e. the same figure as money out; the sub-line names the first
grid year and says so, rather than leaving 2019 and 2020 silently measured by
different rules. The reference line averages the RECORDED years only (a
projection is the plan's own guess, and averaging it in would move the line the
guess is measured against; an empty year is left out too — a zero there says the
sheet is blank, not that nothing was spent) and is **dotted, not dashed**,
because a dash already means "projected" on the bars and in the key beneath
them. Its legend is `reverse: true` for the reason the Giving chart's is:
`order` puts the line in front when it draws, and the legend follows the same
ordering unless told otherwise.
**The hovered bar fills SOLID (`hoverBackgroundColor`), and that is a fix, not a
flourish.** The tooltip is about five bars wide against 41px of bar spacing, and
Chart.js flips it to whichever side of the year it fits on — so from the middle
of the chart onwards it sits to the LEFT of the bar it describes, covers four or
five others and stops just short of its own. It was reported as the chart showing
the previous year's figures; the figures were right every time, hover-tested
across the row (2023 → title "2023", box spanning x 380–577, i.e. over 2018–2022).
The box cannot be narrower than its own sentence, so the BAR carries the
association: nothing else on the chart is solid, and `caretSize: 8` makes the one
part of the box that points at its year hold its own. Watch for this whenever a
tooltip grows a second line — the flip is silent and the chart looks fine in a
screenshot taken at the left-hand end. On a projected bar the fill hides the
dashed edge for as long as the pointer is on it, which is acceptable only because
the tooltip says "(projected)" in words at that moment.
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
  while a typed 0 is kept as a statement — BOTH doors (`comp.save` AND
  `yearAmount.save`) enforce that last rule; the year-row door briefly stored
  0 for an empty box, minting a $0 bonus the reader never claimed. `limitsFor()` reads the map too, so
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
`$100,000.00` on every gridline is clutter on a scale rather than precision. If
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
**A year still running PROJECTS to what it is heading for, because the two
halves of that fraction were being measured over different spans.**
`takeHomePay` reads the COMPUTED cells, so the denominator has always been the
whole year — twelve months of pay, most of them projected. The numerator was
what had actually left by today. Eight months of giving over twelve months of
pay is not a share of anything: it read low all year and jumped in December,
which is the one shape a reader takes as news. `plannedOutOfPocket` is the
mirror of `givenOutOfPocket` — planned fund deposits and cash gifts,
magnitudes, **a planned GRANT deliberately left out for exactly the reason a
made one is**: that dollar left the account the day its deposit did, and
folding it in would count the deposit twice. This is why the projected tile and
the sub's "more is planned" line name different figures without either being
wrong, and both say which they are counting; don't "fix" the discrepancy by
making them agree.
`givingStats` grew `running`, `planned`, `projected`, `projGrossPct` and
`projTakePct`, and took an injectable `today` for the reason `drawdownYears`
has one — whether a year is running decides whether it projects, and a test
that cannot move the date can only pin the answer for the year it runs in.
`buildGivingChart` reads `running` off the stats instead of working it out
again; the tiles and the chart answering that question separately is exactly
how the two would come to disagree. **`projected` is ABSENT, never equal to
`given`, when there is nothing to project** — a finished year, or a running one
with nothing planned — which is what leaves the tab untouched for anyone who
doesn't plan giving ahead, and what stops a fourth tile appearing to repeat the
first. A planned row in a year that is OVER is stale, not forward-looking:
`planned` still counts it so the sub can name it, `projected` stays null.
`givingCeiling` takes the projected shares into its max or the biggest figure
on the tab is the one thing the scale wasn't drawn to hold.
**The projection never displaces a figure of record, and it is read DOWN a
column.** The row of three actuals is exactly what it was; a year with giving
still planned in it grows a SECOND ROW under it saying the same three things
about where the year is heading — dollars over dollars, share over share, so a
projection sits directly beneath the figure it projects. Six tiles or three,
never a mixture, and no second figure hidden inside a tile: the first attempt
folded the projected shares into the actual tiles' feet and it was overlooked
on screen, because a foot is where a tile explains itself, not where it makes a
second claim.
`.goalgrid.pairs` is `repeat(3, minmax(0, 1fr))` — FIXED thirds, never
auto-fit, for the reason `.cards2.pairs` is fixed halves: auto-fit would put
all six on one line on a wide screen and break the pairing at most widths in
between, and the whole point is that the columns line up. One breakpoint at
760px drops it to a single column rather than letting it pass through two,
which would pair each tile with the wrong partner.
A projected tile is the SAME tile with `est` on it — one shape, so the two ends
of a column cannot drift into being different things. `est` carries the
estimate convention: italic figures and a DASHED meter rail (`.goal.est .bar`),
which is the charts' "dashed means not settled yet" said in the vocabulary a
tile has. Never a colour.
**A missing denominator is explained ONCE per column, on the actual tile.**
`givingStats` guarantees a projected share is null wherever its actual one is,
so the tile underneath renders its dash with no `.foot` at all — repeating "No
salary recorded for this year" directly below itself says nothing and reads as
two separate faults rather than one. This is the case a 2027 with planned
giving and no comp record hits, so it is not hypothetical.
**A year of giving CLONES FORWARD, and the copy is a plan.** Each year card's
addbar carries "⧉ Clone to 2027" beside Add donation, and the button names the
year it will write — because that year is `nextUnplannedYear()`, the first one
with NOTHING in it, which is two along once 2027 already holds a plan. That
walk is the safety property, not a nicety: cloning into a year that already had
one would double every figure in it silently, so a clone can only ever CREATE.
It also means the button can be sat next to Add donation without a guard.
`cloneDonationsForward(st, from)` copies EVERY row, the done ones and the ones
already only planned — what is being cloned is the SHAPE of a year's giving,
and last year's intentions are as much a part of that as its receipts. Every
copy lands `pending`, which is the point rather than a detail: it can never
inflate a figure of record, and it feeds the PROJECTION instead, which is the
honest place for giving you have decided on and not yet done. `deductible` and
`note` carry; the source year is not touched.
**`reDate` moves a date by STRING and never builds a Date** — a bare ISO day
parses as UTC midnight and renders as the day before west of Greenwich, the
rule this whole app formats dates by, and `setFullYear` walks straight into it.
**29 February lands on the 28th**, never 1 March: rolling forward would move a
gift into another month to preserve a day-of-year nobody chose. Anything that
isn't a full ISO day stays dateless and keeps sitting in the bucket it is in.
**`dropDonationYear(st, y)` is the counterpart** — "🗑 Delete 2026", the house
shape `deleteYearBtn` already uses. It takes the BUCKET, not just the rows, for
the reason `dropDonation` does: an emptied bucket would ride along in a backup
taken before the next reload and bring the card back on restore. It returns the
count removed and **null, never 0, when there was nothing there**, so the
caller can tell "I deleted none" from "there was nothing to delete" and skip
announcing an edit that never happened.
**Its confirm says undo covers it, and that is TRUE here** — `coreOf` excludes
only `ui` and `quotes`, so a year of giving is in the undo ring like any other
edit (proven on screen: delete, ↩, all seven rows back and still planned).
Don't copy the budget year's "no undo beyond a backup file" wording across;
for this action it would be a lie.
Both buttons live inside `.addbar`, which `stripEditAffordances` removes
wholesale — so a shared read-only link carries neither, with nothing extra to
remember. Both refocus the button that was pressed after the re-render, the
trap every other re-rendering control here already avoids.
**On the chart the projection is DRAWN, not plotted**, so `dashedBarEdge` grew
`opts.to` — per-index values the dashed rectangle reaches instead of the bar's
own top, absent everywhere else so the two Progress charts are bit-for-bit what
they were. Two traps, both found on screen:
- **the bar's own top must be stroked SOLID first** (`if (top !== y)`). A
  running bar carries a transparent border — this plugin is what outlines it —
  so with only the dashed rectangle the end of the real figure was marked by a
  change of fill two shades apart, the gap the caption promises was invisible,
  and the whole bar read as the projected total. Solid box below, dashed box
  carrying on above; they share a base and a width, so the sides say the same
  thing as the tops.
- **the y scale has to be told**, via `suggestedMax`. No dataset holds the
  projected value, so the scale would happily end below the dashed outline and
  clip the one thing it is there to show.
The two percentage LINES stay on the actual figures — a line point cannot be
two values at one x, and a second dashed line on a plot whose lines are already
told apart by dash would be two signals in one costume. The percentages get
their projection in the tiles, the tooltip (in whichever unit the hovered
dataset is in) and the aria summary.
**A projection is marked per MONTH, not per year — `enteredThroughOf(st, y)` is
the one boundary and `yearIsProjected` is now just a question asked of it.**
The Goals tab's "Where the Total Is Heading" line dashed whole years built ahead
and drew the live year solid to December, so next August — a figure chained off
eleven months of estimated category cells — was drawn exactly like last January.
That is the same lie the `kindAt` rule exists to prevent one level down, and the
chart was the last place still telling it. `goalChartPoints()` is pure so the
boundary is pinned by tests, and `renderGoals` reads its caption ("Entered
through Jul 26 — everything after that…") off the SAME points the chart is drawn
from, so the sentence and the curve cannot drift apart. A pinned or summary year
returns `${y}-12`, which is what keeps history solid all the way through. The
tooltip still distinguishes "(estimate)" from "(year built ahead)" — both are
projections, but they are not the same news.
**The retirement projection carries a dotted rule per person, and the horizon
now bends to fit them.** `retirementMarkers(st, labels)` is pure and takes the
CHART'S OWN LABELS, so a rule can never be drawn at a year the chart hasn't got
— a marker clamped to the edge would be a lie told in the one place nobody
would check. Only an adult with both a birth month and a retirement age gets
one (`retirementYearOf` already refuses everyone else, children included);
people retiring in the same year share ONE line, because two rules a pixel
apart is a smudge. The rule is DOTTED and neutral for the reason the spending
chart's average line is: the projection itself is dashed, and a second dashed
thing on the same plot would be two signals in one costume. The name carries
the meaning, never a hue.
`retirementHorizon()` is why the 25 years became a FLOOR: somebody in their
thirties retires past the end of a 25-year chart, which is the reader whose
marker matters most and the only one who would never see it. It stretches to
two years past the last datable retirement — the headroom is not cosmetic, a
rule against the right-hand edge has nowhere to put its name — capped at
`RET_YEARS_MAX`, because a mistyped retirement age must not flatten twenty-five
real years into the left-hand inch. `retMarkerNote()` says out loud who has no
rule and why; a marker that silently isn't drawn reads as the app lacking the
feature rather than as a question nobody has answered.
**The retirement projection SPENDS THE POT DOWN, and the arithmetic is one pure
function.** `drawdownYears(st, thisYear, span)` returns one record a year
(`{y, open, growth, contrib, income, spend, draw, short, close, phase}`), and
the chart, the year-by-year table and the three tiles are three views of
exactly those records — the `givingStats` arrangement, pure over state with an
injectable today. `drawdownOutlook` and `drawdownMarkers` read the same rows.
Things that are load-bearing and will look arbitrary later:
- **Growth on the OPENING balance, then contributions** — bit for bit the old
  `bal * (1 + r) + contribs[y]`. The accumulation half of this chart must not
  move by a cent: a reader who knows their 2045 figure would find it changed by
  a feature about 2060. **`the accumulation half is exactly what it always was`
  recomputes the old formula inside the test and compares** — it is the
  regression guard the whole feature rests on, and it must never be relaxed.
- **`spend` and `safeRate` are ABSENT, never 0, when unset.** Absent is what
  leaves an untouched plan's projection climbing exactly as it always did; a
  stored 0 would be a claim that the household spends nothing. The editor
  DELETES on an empty box for the same reason.
- **"Retires at 55" is four dates, and the reader picks one.** The first version
  silently chose 1 January of the year you turn 55 — the only one of the four
  nobody means — because `retirementYearOf` sliced the year off the birthday
  month and the drawdown started at the top of it. `person.retireWhen` is
  `birthday` (the default, and absent when it is), `jan-that-year` or
  `jan-after`; `retirementMonthOf` is now the primitive and `retirementYearOf`
  is its year, so every existing caller moved with it for free. `retireAge`
  takes halves, because "not a day before 59½" is a real decision made for real
  tax reasons and it only needs month resolution to express.
- **The first year of retirement is usually a PART year, and is pro-rated.**
  `retiredShareOf(y, fromMonth)` is `(13 - month)/12` in the year they go and 1
  after it. Retiring in November is two months of spending; calling it twelve
  overstated that first withdrawal six-fold. Income is deliberately NOT
  pro-rated with it — an income row's start year is the reader's own statement,
  not something to be second-guessed by somebody else's retirement month.
  **The safe-rate check is measured on the first WHOLE year** (`outlook.rateYear`,
  distinct from `firstDrawYear`), or it would call a plan safe on the strength
  of a two-month year; `outlook.partYear` is what makes the card say the two are
  different years instead of quietly showing one under the other's label. The
  year-by-year table's age column reads December, not mid-year, so the row where
  somebody retires at 55 doesn't say 54.
- **The projection can be drawn three ways** — `drawdownScenarios` returns the
  plan at your rate plus the optional `settings.retirementReturnLow`/`High`.
  **Both absent by default**, so the chart is the single line it always was
  until there is something extra to say. `shiftRates(st, delta)` SHIFTS every
  rate by the same points rather than replacing them: an account you said grows
  at 3% while the plan assumes 7% is a statement about how it is invested, and
  a worse market should knock both down rather than flattening them to one
  figure. It returns a copy, and `delta === 0` returns the state untouched.
  **Drawn as a BAND, not three lines**, and that is the design: three curves
  would need three ways of telling them apart, and the only ones left are
  colours (none to spare, and hue may never carry meaning alone here) and more
  dash patterns (loose is saving, tight is drawing — both spoken for). A filled
  range reads by POSITION and leaves the existing line untouched; `--accent-bg`
  inside, `--border-strong` on the edges, no colour invented. The band's two
  datasets must stay adjacent and ahead of the main line, since `fill: '-1'`
  fills to the dataset before it, and the tooltip checks `datasetIndex` so an
  edge never borrows the middle line's story about a withdrawal it never made.
  **THREE ASSUMPTIONS, NOT A PROBABILITY BAND** — said in the chart key, in the
  costs card and in the Preferences hint, because the app has no distribution
  behind these and a band that read as a confidence interval would be the most
  authoritative-looking wrong thing on the tab. Do not add one without a model
  that earns it.
- **The projection grows POTS, not one balance** (`retirementPots`). Each
  retirement account is a pot with its own `rate` (`accountRate` — the account's
  own, else Preferences; **absent means follow Preferences, and a 0 is a real
  statement**, so `coerceShape` reads it strictly rather than through `num()`,
  which would turn a corrupt field into a deliberate-looking 0%). Two extra pots
  carry the 401(k) deferral, which no account owns: the app has never asked
  which of five 401(k)s it lands in, and nominating one would invent an answer.
  **BALANCES follow each account's own type** — the accounts have distinguished
  a pre-tax 401(k) from a Roth one since the day they had types, and saying the
  deferral "counts as Traditional" over the top of that was rightly called
  confusing. The one thing that could not say which was the LIMIT CHECK, which
  holds a single percentage; **`limits[year].rothShare`** (and `.by[personId]`)
  settles it, splitting the deferral into a Roth pot and a pre-tax one.
  **It is 0 unless set — exactly the old behaviour** — and is clamped to 0–1 in
  `limitsForIn`, the single read point, so a hand-edited 500% cannot drive the
  pre-tax side negative. It changes two things and deliberately not the third:
  the Roth part lands on the Roth side of the split, and it does NOT come off
  the MAGI (a Roth contribution is made from income already counted, and
  subtracting it would understate that check in the direction that says "you're
  fine"). The yearly 401(k) limit is untouched — it covers both together, which
  is why "You put in" adds them up. A typed contribution row against a named
  account still wins, at that account's rate.
  **Each pot is rounded to the cent every year** — with one pot that makes the
  loop bit-for-bit the single balance it used to carry, which is what the
  accumulation guard pins.
  **The withdrawal is taken PRO RATA across the pots** and that is deliberate:
  which account you would spend first is a tax decision, this app models no tax,
  and proportional drawing is the only split that expresses no opinion. Do not
  "improve" it into a withdrawal-order strategy.
  `retirementSplit(st, thisYear)` is Traditional against Roth today AND at the
  month the pot starts paying — the mix being what decides how much of a
  retirement is taxable, and the top-of-tab bar only ever showing today. Its
  loop compounds rounded-to-the-cent per pot per year EXACTLY as
  `drawdownYears` does (it briefly compounded unrounded, which agreed on
  round fixtures and drifted by cents on real ones). There is a test that its
  total equals the pot the chart draws that year — cent for cent, odd rates
  on purpose; if those ever disagree, one of them is lying about somebody's
  retirement.
- **`RET_TYPES` lives ABOVE `let state = load()`** because `coerceShape` reads it
  to settle an account that arrived with no `kind`. A const below that line is
  in its temporal dead zone at load time and the ReferenceError is swallowed —
  the whole workbook comes up empty. It was moved for exactly this reason.
- **Contributions come from BOTH places the app records them.**
  `plannedContribs(st, thisYear, span)` is the one source the projection reads:
  the per-year IRA rows (`contribYears`), an IRA's latest figure CARRIED into
  the years it has nothing typed for, PLUS each 401(k) card's RATE, which is how
  most people actually hold the figure.
  **A typed year always wins, in both directions** — that is the escape hatch
  that makes the carry safe, and a typed 0 is a year they really skipped. **A 0
  in the NEWEST year stops the carry entirely**: the last thing you said about
  an account is the current statement of it, and understating what goes in is
  the safe direction for a retirement projection to be wrong in.
  **Only an IRA carries** (`isIra`) — a 401(k)'s pay-in comes from its
  percentage, so carrying its typed rows too would count the same money twice.
  An IRA stops at its OWNER's retirement, or at the household's first for one
  nobody has been assigned; unlike a 401(k) rate, a dollar figure still means
  something on a plan that never named anybody.
  `iraOutlook(st, thisYear)` is the per-account view behind "Where the IRAs
  Land" — balance now, what is still to go in, and what it is worth by the month
  the paying-in stops. **It copies `drawdownYears`' growth convention exactly**
  (year zero untouched, then growth on the opening balance, contribution on
  top): two views of the same money compounding differently is the sort of
  disagreement nobody catches until the figures are years old, and there is a
  test that both count the identical contribution stream. The rate is
  carried forward in today's money until that person's own retirement and
  pro-rated across the year they go — the mirror of `retiredShareOf`, so ten
  months' pay-in and two months' spending add to one year. The projection read
  only the first source at first, and a plan with its percentages filled in
  showed "Paid in —" for forty years while understating itself badly; that is
  how it was found. Two traps worth keeping: **only an earner the plan can DATE
  gets projected contributions** (no retirement month, nothing to stop
  contributing at, and a projection paying in at 95 is worse than one paying in
  never), and **`plannedDeferral` carries the latest year that records a RATE,
  not the latest year of any kind** — a comp year added ahead has a salary and
  no percentages, so reading the last year of any kind would silently carry a
  zero and empty the whole projection.
  `limitsFor(year, personId)` keeps its exact pinned one-argument behaviour; the
  state-taking core is `limitsForIn(st, …)` underneath, the same arrangement
  `contribYears` got.
- **The pot starts paying at the FIRST retirement in the household**, never a
  year in the past. Two people retiring in different years is a DATA question,
  not a branch: the one still working puts their pay in Other Retirement Income
  with an end year. Splitting the spending target by who has retired needs a
  model of who pays for what share of a household, and every household would
  disagree with whatever ratio shipped — don't build it.
- **Income only ever offsets a withdrawal.** Before the drawdown starts `spend`
  is 0, so income does nothing to the pot: money received while working is
  spent, not saved, and the app cannot know otherwise. The record still carries
  it so the table can show it.
- **A year has to be a YEAR.** `num()` turns anything it can't read into 0,
  which is right for an amount and a disaster for `from` — `from: 0` matches
  every year on the chart and would pour a pension into 2026. `coerceShape`
  drops an implausible year instead, and a row with no start year never
  arrives. There is a test.
- **`side.drawdown`, never `side.retirement`** — `coerceShape` does
  `delete s.retirement` on every load (the old imported free-form rows), so a
  branch by that name would vanish on the next refresh.
- **Not in `settings`.** `buildSharePayload` sends `settings: state.settings`
  unconditionally, so anything there rides in EVERY link, including a
  holidays-only one. What a household spends is not that.
- **No RMDs and no Roth-vs-traditional withdrawal order, ever.** Same rule as the
  MAGI threshold and for the same reason: every one of them is a figure with a
  year attached. **Tax itself is no longer on that list** — the drawdown is
  growing a gross-up off the bracket tables the reader types (see "Tax" below).
  Until a table exists the projection is exactly what it always was, and the
  `.note info` above the chart still says the pot is one pot.
- **`SAFE_RATE_DEFAULT` is where the box starts, not advice.** 4% assumes a
  particular mix, a particular length of retirement and one country's history,
  none of which this app checks, and the hint says exactly that.
- **`planToYearOf` shares `retirementYearOf`'s guard** — a plan-to year exists
  exactly where a retirement year does, which is what stops a half-filled
  person stretching the chart forty years for a drawdown they aren't in. The
  default is applied at the point of use and NEVER stored: a stored 95 would be
  a figure the reader never typed sitting in their backup looking like a
  decision. `RET_YEARS_MAX` went 50 → 75 because at 50 a thirty-year-old
  planning to 95 loses fifteen years of their own drawdown.
- **The chart carries three marks and none of them is a colour**: a loose dash
  while saving, a tighter dash while drawing, a dotted rule for a retirement, a
  solid one for the pot running out (`retirementMarkerLines` reads `m.dash`).
  `drawdownMarkers` is concatenated with `retirementMarkers` rather than folded
  into it, so that function keeps its signature and its tests. **Other income
  is deliberately not a second series** — a flow in tens of thousands against a
  balance in millions draws as a flat line on the floor, and there is no colour
  to spare; it lives in the tooltip and its own table.
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
Preferences button; `buildMoneyFormats()` rebuilds the formatters on every
render.
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
**The notes are their own BOX under the budget**, not a panel inside it: they
answer a different question from the grid, and a box nested in a box gives the
reader two headers to fold and no way to guess which one they shut. `renderBudget`
appends `yearNotes(y)` after the grid or summary card; both fold through the one
mechanism below.

## Growth is not income (2026-08-31)

**An account's rate produces one of two things, and the account says which.**
`account.earns` is `'interest'` or `'growth'`, defaulting to interest. Interest
is money the account earned; growth is an investment rising on paper, which
moves the balance and is income nowhere. Asked for from life: an investment
account carried a growth rate, all of it market appreciation, and every figure
that counts income was counting it — Money In overstated by thousands a year,
and a savings rate flattered by a gain nobody can spend.

The app was already half-agreeing: the settings field was labelled "Interest /
growth %/yr" and the cell editor's prose said "Grows X%/yr" while the box beside
it said Interest and the money was counted as pay. The label and the accounting
disagreed; this is which one was wrong.

- **THE SPLIT HAPPENS IN `computeYear`, NOT AT THE READERS, AND THE REASON IS
  WHICH WAY THE MISTAKE FALLS.** There is a third map, `growth`, keyed like the
  other two, and an account's rate feeds `interest` OR `growth` and never both.
  Because they are disjoint, every reader that must EXCLUDE growth needed no
  change at all — `accountEarnings` and `yearFlows` read interest+dividend and
  simply never see it. So a reader nobody taught prints one line too few in a
  tooltip: visible, harmless. The alternative (one map plus a `growthIds` set on
  the computed result) inverts that — a missed reader goes on quietly calling a
  paper gain income, which is the exact bug, invisible, in the savings rate.
  It also preserves `accountEarnings`'s stated contract of reading the maps
  rather than walking `accountsOf`, so its callers still need only
  `(computed, yr)`.
- **`accountGrowth(c, yr, months)` is the one reader for the other question**,
  shaped like `accountEarnings` and sharing `sumEarningMaps` with it — the
  difference between them is which money it is and nothing else, so two loops
  that could drift on how a month is MARKED would be two too many.
- **The override key is still `balAdjust[key].interest`.** One stored field
  meaning "what the rate came to this month", with `earns` saying what to call
  it — the way `rate` has always been dual-purpose. A second `adj.growth` would
  mean a month typed in before an account was marked `growth` quietly stopped
  counting.
- **`coerceShape` forces `creditTo = a.id` on a growth account.** Sweeping an
  unrealized gain into spendable cash would be a SALE, and a percentage does not
  say you sold. That rule is also what lets `receivedInto` stay untouched:
  growth has no receiving end, so no account can report it as money paid in.
  The editor HIDES the destination dropdown rather than disabling it, and that
  is allowed here precisely because the claim is genuinely withdrawn in the data
  — the readout beside it states the rule rather than leaving a gap.
- **A PINNED YEAR CLASSIFIES BY THE ACCOUNT, deliberately unlike
  `creditTo`/`divTo`.** Those are ignored in a past year on the grounds that
  today's routing says nothing about 2021's — and the two are different kinds of
  fact. Where money was SENT is an arrangement; whether an account holds paper
  gains is what the account IS, and an investment that appreciates today
  appreciated then. Reading it forward is also the only option that does not put
  the same money on both sides of the question.
- **`gridToPinned` stamps growth into `adj.interest` too.** Without it, freezing
  a year silently loses the appreciation: the pinned branch computes nothing, so
  the Growth row would empty while the balances it moved stayed put.
- **`gridToSummary` EXCLUDES growth from the Interest & Dividends row**, and
  that exclusion is mandatory rather than tidy — `adj.interest` is the stored
  field for whatever the rate produced, so summing it blind folds a paper gain
  into an income row at the one moment nobody would look again.
  **It is not carried across as a row of its own either**, and that is a real
  loss stated out loud: a summary has two kinds of row, flows and balances, and
  growth is neither. The MONEY is not lost — the balance rows are December's
  closing figures and hold every dollar of it — only the note saying how much of
  the climb was appreciation. `convertYearToSummary`'s confirm says so first.
  Do NOT "fix" this by giving the row `isBalance: true`: that flag's name says
  balance and its job is exclusion, and the row would then be listed among the
  account balances as though growth were one.
- **NEITHER LENS GIVES GROWTH A ROW, and that is the decision.** Both had one
  for a few hours on 2026-08-31 and both came straight back out, on Charles's
  reading, which was right twice:
  - The MONTH page's sat in `.mrows` — *"i don't like growth listed as it's own
    account. plus it's already there on the account row anyway."* `.mrows` IS
    the account list, so a row in it reads as an account called Growth holding
    $88.40; and `earningLines` already said it on the account three lines above.
  - The YEAR grid's sat under Total, and fails the same way one level up: the
    Accounts block is a stack of BALANCES (Total is a balance, Paychecks a
    count), so twelve monthly growth figures in it read as tiny balances under
    a large one.
  **The real shape of the problem: growth is a FLOW that is not income, and the
  grid has no block for one** — Income is the wrong claim outright and Accounts
  is the wrong kind of figure. Rather than invent a third block for one line, it
  is said where it happened: `earningLines` per month under the balance it
  moved, `earningsOver` → `balanceYearTip` for the year on the account's
  year-total cell. One answer, on the account that made it.
  **The Income earnings row is not the precedent it looks like** — that list is
  CATEGORY ROWS, and interest and dividends have no other home on the grid,
  where growth has a perfectly good one.
  **The CSV mirrors the screen and carries no Growth row either**: the rule cuts
  both ways, and a line the file invents that the screen never drew is the same
  disagreement as one it drops.
  **`accountGrowth`, `growthTip` and the `sumEarningMaps` split all went with
  the rows.** They had no reader left, and an unread figure on this file's
  arithmetic is the second copy every other note here warns about;
  `accountEarnings` took its own loop back. The general rule earned twice in one
  day: **before adding a derived row, ask what the list around it is a list OF.**
- **STATING A BALANCE DOES NOT RESTATE THAT MONTH'S GROWTH — BUT THE DIALOG
  OFFERS THE FIGURE** (2026-08-31). Growth is computed off `base` (the opening
  balance after transfers), which an override does not touch, so the pinned
  month keeps the figure the rate implied while every LATER month chains from
  the stated number. Measured: pinning February at 12,000 over an expected
  10,201 leaves February's growth at 101 and moves March's from 102.01 to 120.
  - **`impliedGrowth(typed, computed, growthNow)` = `growthNow + (typed −
    computed)`**, and it is EXACT rather than a guess at the shape of the
    answer: everything else the month did to that balance is already inside
    `computed`, so the residual is precisely what growth would have had to be.
    It is also INVARIANT to whatever is in the Growth box — measured against
    what the plan computed, not against what is typed over it — which is what
    stops the offer chasing its own tail as the reader edits.
  - **THIS IS THE ONE EXCEPTION TO `reconcileNote`'s "state the gap and stop",
    and it does not generalise.** That rule exists because the app cannot know
    what a missing sum was. On a GROWTH account it nearly can: every other
    figure in the month is known, and the one candidate left is the one thing
    nobody can read off a statement line by line. So it is **offered on a growth
    account only** — on a cash account the likelier explanation is an unrecorded
    transaction, and a button there would teach people to bury one in "growth".
  - **It only ever OFFERS.** No auto-fill: `link`-style filling would decide
    that the difference was the market. It is hidden when the month already
    agrees, and hidden when the Growth box already holds a figure — filling a
    box the reader has written in is the one thing an offer must never do.
  - **`updateReconcile` re-reads the note against a typed growth figure**, so
    taking the offer flips the line to "Matches the plan exactly" instead of
    going on quoting a gap just explained. Safe ONLY because a growth account's
    `creditTo` is forced to itself, so its earnings move its own balance one for
    one; do not extend that arithmetic to interest accounts, whose earnings may
    be paid somewhere else entirely.
  - **`growthOfferLabel` puts the DIRECTION in the verb** — "Say This Month Fell
    $6,330.00", never "Grew -$6,330.00", which puts the minus sign where the
    word should be. A fall is half of what the feature is for. Zero reads "Grew
    Nothing", which is a claim rather than a blank.
  - Both are pure and pinned, and the button fills the box and nothing else —
    nothing commits until Save, exactly like `link` and Accept the Estimates.

## Tax

**The principle: the app may COMPUTE tax; it may not KNOW a tax figure.** That
is the rule the old "no tax model" line was reaching for and stating too widely.
Brackets you type are the same shape as `magiLimit`/`k401Limit` — year-keyed and
reader-owned — and the arithmetic over them is the same arithmetic `magiCard`
has always done.

Honoured concretely, and this is the part to hold the line on: **no bracket
amount, rate or deduction is a literal ANYWHERE** — not a default, not a
placeholder, not a realistic-looking fixture. The tests use 10/20/30% on round
thousands, because a realistic figure in a fixture is a shipped figure somebody
copies out one day. `LIMIT_DEFAULTS` is the one pre-existing exception and is
deliberately NOT extended: a wrong limit is one card reading wrong, a wrong
bracket table is forty years quietly reshaped. **A year with no table means no
tax**, which is what makes the no-brackets promise true by construction rather
than by good intentions.

Still forbidden, for the original reason — each is a figure with a year
attached: RMDs, a Roth-vs-traditional withdrawal order, the Social Security
provisional-income formula, SALT/itemising, capital gains, NIIT, IRMAA.

**The whole feature is built.** The regression guard it rests on is that **`the
accumulation half is exactly what it always was` passes UNEDITED** — it does,
and it must keep doing. Its sibling, `with no tables the drawing half is what it
always was, to the cent`, recomputes the old drawing formula inline and compares
every field; between them a plan with no brackets is pinned in both phases.

```js
side.tax = {
  federal: { "2026": { joint: { bands: [{upTo, rate}, … {upTo: null, rate}],
                                deduction?, source? } } },
  state:   { "2026": { … } },
  stateLabel?,          // absent by default — see the looksEmpty trap
  check?: { income }    // the calculator's scratch figure
}
```

- **Jurisdiction outermost** — federal and state move on different clocks, so
  the carry-forward is per jurisdiction. **Year next**, so one trim does each.
  **Filing status innermost**, keyed to `FILING_STATUSES` (written out once, and
  the same list `settings.filingStatus` is validated against — the two drifting
  would file a table under a status the app then refuses to select). **A table
  for a status you have left is KEPT**: filing status changes, and the schedule
  you typed for the year you were single is still the truth about that year.
- **`bands` must be OBJECTS.** `arr()` filters to objects, so a hand-edited
  `bands: [20000, 0.10]` empties SILENTLY — a table that reads "no tax" on
  screen while looking perfectly full in the backup it came from. That is why
  `coerceTaxBands` is its own function with its own tests rather than a line in
  coerceShape's `arr()` loop.
- **`upTo` is read STRICTLY, never through `num()`** — the trap that already bit
  `account.rate` and an income row's `from`. num() turns garbage into a
  deliberate-looking 0, and a 0 top edge is a band that taxes nothing.
  **`upTo: null` is the open band, never `Infinity`** (which round-trips to null
  through JSON anyway); `Infinity` is *accepted* on the way in for that exact
  reason, so a table built in memory doesn't lose its top band.
- **`rate` is CLAMPED to 0–1, and the clamp is the gross-up solver's
  PRECONDITION, not tidiness** — the bisection relies on
  `net'(G) = 1 − m·tradShare ≥ 0`, which holds only while every marginal rate
  does. Pin it with its own test when the solver lands.
- Bands are sorted with the open band last and overlaps dropped. **A record with
  no readable band is deleted**, and so is a year left empty by that — half a
  table standing would tax at rates the reader never managed to enter.
- **`blankState().side.tax` is EXACTLY `{federal:{}, state:{}}` with no string
  fields.** `looksEmpty` returns false for *any* string, so an empty
  `stateLabel` would offer a Tax link to every plan in existence. coerceShape
  deletes an empty one rather than keeping `''`, the branch has a CLOSED key set
  (anything else is deleted), and `BRANCH_HAS_DATA['side.tax']` judges the tab
  on its TABLES as belt to that braces — a number typed into the calculator is
  not a reason to send anybody anything.
- **`SECTION_NEEDS.tax` carries Retirement's whole set beside `side.tax`**,
  because "What the Pot Has to Pay" is read off `drawdownYears` and therefore
  reads everything the drawdown does. They were deliberately absent while the
  tab drew nothing and were added in the same commit as that card — the rule
  either way is that the table describes what the tab ACTUALLY reads: too
  little shows the recipient blanks, too much ships data the tab never displays,
  and only the second is a privacy bug. `shareCarriesNote` names them, since
  Retirement owns them.
- **`trimTaxYearMap`, not `trimShareYearMap`** — and both differences follow
  from a table being an ASSUMPTION about a year rather than a record of one.
  The **CUTOFF applies, the CEILING does not** (a table dated ahead is a
  projection assumption like the assumed return; dropping it would change the
  recipient's figures rather than shorten their link — omitting this is a
  privacy bug in reverse). And **the newest table always travels**, whatever the
  window: every projected year reads the newest table at or before it, so a
  reader whose only table is dated 2020 sending "the last 1 year" would
  otherwise hand over a silently tax-free retirement. `side.tax` is deliberately
  **out of `shareYearUniverse`** for the same reason — a table dated 2028 must
  not stretch what "the last 3 years" means for the budget grid beside it.
- **`VIEWS`, `FILING_STATUSES` and `TAX_JURISDICTIONS` all sit ABOVE `let state
  = load()`** — the temporal-dead-zone rule at the top of this file. coerceShape
  reads all three, `load()` swallows the ReferenceError, and the whole workbook
  comes up blank.

### What the brackets say

- **`taxOn` taxes income above a TRUNCATED table's top band at that band's
  rate, never at 0.** A schedule somebody typed only as far as they read must
  not make the next dollar free; that silent cliff is the one failure this
  could not afford. Unreachable when the table ends in an open band, which is
  the normal case.
- **Two layers, and the split is load-bearing.** `taxRaw`/`taxableAfterRaw`/
  `taxBillRaw` are UNROUNDED and exist for the solver; everything user-facing
  goes through the rounded pair. **`round2` inside the solver turns a strictly
  increasing function into a staircase**, and a bisection chasing a staircase
  lands wherever it happens to stop. The one rounding is `Math.ceil` on the
  final answer.
- **`effectiveRateOn` returns NULL, not 0**, with no income or no table — the
  house rule `impliedRate` already follows. A 0% reads as "you pay no tax"; the
  truth is that the question has not been asked.
- **`taxTableFor` reads the CURRENT filing status only** and never borrows
  another's — taxing a married couple on a single filer's schedule is a wrong
  answer wearing a right one's clothes. `taxStatusGap` is what says so out loud,
  on the tab and in the brackets card.

### The gross-up

- **`grossUpDraw` solves `income + G − tax(taxableOther + G·tradShare) ≥ spend`
  BY BISECTION.** The closed form is exactly solvable and was rejected: it needs
  four special cases nobody gets right twice, and the bisection's test is
  stronger than either — **`net(G) ≥ spend` and `net(G − 0.01) < spend`**, which
  is the definition of the answer rather than a re-derivation of the arithmetic.
  There is a test that checks it as a PROPERTY over a grid.
- **The 0–1 rate clamp in `coerceTaxBands` is this function's PRECONDITION**,
  not tidiness: `net'(G) = 1 − m·tradShare ≥ 0` holds only while every marginal
  rate does. There is a test pinning the two together.
- **Two early returns carry the whole no-tax invariant.** No tables returns
  `Math.max(0, round2(spend − income))` — the literal expression it replaced,
  character for character. `spend === 0` returns 0, without which a TAXABLE
  income row would start draining the pot at 45.
- Brackets by doubling, capped at 60 → `capped: true` rather than hanging, for a
  table that can never reach the target (everything at 100% against a pre-tax
  pot).
- **`taxAtDraw` reports NOTHING TAXABLE when there is no table** — not "nothing
  taxed on an income of X". With no brackets there is no measure, and a record
  carrying a taxable income beside a tax of zero reads as a bug.

### In `drawdownYears`

- **`tradShare` is read off `before`** — after the year's growth and
  contributions, because that is the money being drawn. **Nothing feeds back:**
  drawing pro rata takes the same proportion from every pot, so the draw cannot
  change its own taxable share. That is the strongest argument yet against ever
  making this a withdrawal-order strategy — the moment it became one, this
  figure would depend on the answer it is used to compute.
- **`short` stays GROSS** (what the pot could not produce, which is what
  `runsOutYear` keys off), and `phase` still keys off `spend`, so no existing
  test moved.
- **The bill is measured on the ACTUAL draw, not the wanted one** — a pot that
  ran dry pays tax on the smaller sum it managed.
- New record fields `{tax, taxable, tradShare, want}`; nothing removed.

### The parser

- **Refuses whole, never half** — the JSON-restore discipline. `ok:false`
  carries **no `bands` key at all**, not an empty one, so there is nothing to
  store by accident. Refusals: no percentages, zero bands, not strictly
  increasing (quoting both edges), a rate over 100%, more than 25 bands, two
  rates on a line, an open band that isn't last, and **a last band that isn't
  open-ended** (a pasted schedule that lost its top row is a paste error, where
  a hand-typed truncated table is a deliberate act `taxOn` already handles).
- **Cut each line at "of the amount"/"of the excess"** — what follows is a LOWER
  edge, and reading it as an upper one is an off-by-one-band error that looks
  right in the preview. **NOT cut at "plus"** — that is where the rate lives.
- **Exactly one percentage per line, with the `%` sign.** A bare `0.10` is
  indistinguishable from an amount and guessing is how tables go quietly wrong.
- **An open-ended marker discards its number** (`$80,000+` names the FLOOR).
- **The upper edge comes off an explicit RANGE where there is one, not off the
  largest number.** Taking the largest also works for every well-formed
  schedule, but it silently REPAIRS a reversed range into the figure beside it,
  and a paste that came in backwards has to be refused rather than tidied.
- **`parseBrackets(text, filing)` takes the filing status as an ARGUMENT.** It
  briefly read `state.settings` for one refusal message, which is the
  ambient-state trap in the Tests section above wearing a different hat: the
  same paste would behave differently depending on what the browser held.
- **Three things a real clipboard does, all found by pasting real schedules in
  and all pinned by tests.** Each is a deterministic repair, never a guess —
  which is what makes doing any of them acceptable:
  - **A copy flattens the table onto ONE line** ("…Single Filers10%: Up to
    $12,30012%: $12,301 to…"). Put back by two rules: a digit after a complete
    `,NNN` group starts a new token (a comma-formatted amount's last group is
    exactly three digits, so `$12,30012` can only be `$12,300` then `12`), and a
    digit straight after a LETTER starts one (a heading glued to the first
    band). **Do not "take the last two digits before the %"** — that turns
    `$50,3007%` into `$50,30`, an edge wrong by a factor of ten. Applied only to
    a line carrying more than one percentage, so anything that already parsed is
    untouched.
  - **Markdown bullets and citation footnotes** ride along — `[[1](https://…)]`
    hanging off the last band. **URLs are stripped first and whole**: they are
    full of digits and hyphens (`…/2026-federal-income-tax-brackets…`) and every
    one is something the band reader could take for an edge or a range. Stripped
    rather than ignored as a LINE, because the debris sits on the same line as a
    real band and dropping it would lose the top band.
  - **A wide rate-by-status table** — one row per rate, a column per filing
    status — is narrowed to the reader's own column BEFORE any number is read
    (`pickFilingColumn`). Every other column is somebody else's schedule.
    **Gated on finding a HEADER**, not on the text merely looking wide, or a
    dot-leader schedule or a gutter-separated table would be torn into columns
    that were never there. No column for the current status is a refusal that
    names the ones it did have.
- **An open band with more bands after it means TWO SCHEDULES were pasted**, not
  a band-order mistake — the published pages stack single above married and a
  copy takes both. The message says so and names which one to keep; "put the
  and-above band at the bottom" was advice about a mistake nobody made.
- **Confirm-before-store with NO new dialog**: a `readout` filled by `link()` on
  every keystroke says what will be stored or why nothing will be. That needed
  two small widenings of the dialog machinery, both of which are general fixes
  rather than tax special cases: **`link` now fires on TEXTAREA as well as
  INPUT**, and **a CHECKBOX now re-evaluates `showIf`** like a select always
  has (without it a tick did nothing, which reads as a dead control).

### Other retirement income

- **Store the PERCENTAGES only and derive the tick.** `taxed: true, pct: 0` is a
  pair that cannot mean anything, and one half would eventually contradict the
  other.
- **`stateTaxPct` falls back to the FEDERAL figure, not to zero** — defaulting a
  state share to nothing would quietly halve the bill.
- **Absent is 0% and is SAID OUT LOUD** — an em dash in the Taxable column and a
  line counting the rows nobody has answered for. "Untaxed" and "nobody has
  said" are different claims, and only one of them is the app's to make.
- The fields only appear once a table exists, and `retIncome.save` carries any
  existing shares across untouched when they don't — **a dialog that never asked
  the question must not answer it.**

## One vertical gap: 18px (2026-08-23)

**Every seam between two blocks in this app is 18px** — card to card, card to
a `.cards2` grid, that grid's own `row-gap`, and a toolbar strip to whatever it
sits above. There is no second number to reach for. Measured across all nine
tabs on 2026-08-23 and pinned there.

The one exception is a heading WELDED to the thing it names: `.yearhead` keeps
8px under it, because the label and its trip row are one object and the seam is
the air ABOVE the label. `.cards2 > .yearhead` (Retirement's Now / Later rules)
has its own `8px 0 -8px` and is untouched by the base rule.

Vacations is the tab to watch, because its four seams are each built a
different way and will drift apart again if one is edited alone:

| seam | how the 18px is made |
|---|---|
| add bar → the chart card | the bar's own inline `margin: 0 0 18px` |
| chart card → first year's heading | the card's 18px collapsing into `.yearhead`'s 12px — the same collapse the add bar used to make, so the seam is unchanged |
| trip card → next year's heading | `.triprow`'s 12px collapsing into `.yearhead`'s 12px, **plus the row's 6px `padding-bottom`** |
| trip card → the leave planner | that same 6px, with nothing to collapse into, over `.triprow`'s 12px |
| one tail card → the next | the plain `.card` margin |

**The row's `padding-bottom` is part of every gap you see**, because what a
reader measures is the last trip card's border to the next block's — and the
padding sits between them. Measuring the `.triprow` box instead of the CARDS
inside it is what made three attempts at this land on three different numbers.
Measure card border to card border.

### The add bars are 16px, all of them (2026-08-31)

**`.addbar { margin-top: 16px }` and no overrides.** It was 10px, and the 10px
was only ever true under a TABLE: measured across all 38 bars in the app, 25 sat
at 10px, 7 at 16px, one at 12px and one at 18px. **Two of those four were nobody's
decision** — a bar following a paragraph collapses to `.sub`'s 16px bottom
margin, and one following a card collapses to the card's 18px. The gap was a
property of whatever happened to sit above the button.

- **16 rather than 10** because it is the interval the page already reads by: it
  is `.sub`'s own bottom margin, so a card whose add bar follows a total or a
  paragraph now **opens and closes on the same gap**, and it was already the real
  figure in seven places rather than a new number.
- **Both overrides were deleted**, not kept: `.monthgrid .addbar` (added hours
  earlier for the month cards, and made redundant by the rule) and
  `.note .addbar`'s 12px. One value means one rule.
- **The one surviving 18px is correct and must not be "fixed"** — that bar
  follows a whole `.card`, so it is a seam between two BLOCKS, and 18px is this
  app's block rhythm (see "One vertical gap: 18px" above). It is the collapse
  agreeing with the house rule rather than defying it.
- The measurement is worth repeating rather than trusting the CSS, because
  **margin collapse means the declared value is not the gap**. Walk every tab,
  find each `.addbar`, and measure `bar.top - previousElementSibling.bottom`.

## Card order: the thing you DO leads (2026-08-23)

A tab's first card is the one it is for, not the one that summarises it. Four
tabs were re-ordered on 2026-08-23 because a derived summary or a long-run
chart had drifted to the top and pushed the working card below the fold:

- **Progress** — Savings Goals first, then Net Worth, then Savings Rate &
  Runway, then the four long-run charts, then Where the Money Goes.
- **Vacations** — the add bar, then the trips by year, then the PTO cards,
  then Trip Spending, Year by Year. Leave counting follows the trips it counts.
  **REVERSED on 2026-09-04, for this tab only, and DELIBERATELY** — Charlie
  asked for it, agreed the rule is right elsewhere, and wants this kept as a
  documented exception rather than quietly restored. His reason first, because
  it is the one that decided it: *it looks better than just boxes at the top.*
  The newest year is usually trips that are still only titles — "Not Planned
  Yet" — so the tab opened on a row of collapsed boxes with no figures in them,
  which is a poor first screen however correct the ordering rule is. The rest
  agrees: the trips are a horizontal row per year, newest first, so the working
  card is at the top of the page either way, while at the foot the chart sat
  under every year of trips AND every PTO table, several screens down on a full
  plan — the one card comparing this year with the last few was the one card
  nobody saw. The add bar still leads: it is the tab's toolbar, not a card. The
  other three tabs keep the rule; do not "fix" this one back to match them.
- **Giving** — the filing note (it carries the CSV export and says a year's
  table appears *below*, so it stays welded to them), then the year tables,
  then the Giving Fund, then Giving over Time.
- **Tax** — the disclaimer note, then What ⟨year⟩ Owes / What You'd Pay / What
  the Pot Has to Pay, then the bracket cards and Years You've Stored.
  **With no table stored the order FLIPS** and the tables come first. That is
  not tidiness: `taxNowCard` and `taxCheckCard` both return `''` without a
  table, so answers-first would open the tab on "nothing is being drawn down
  yet" sitting above the very tables that would fill it in.

Two tabs deliberately keep a summary near the top and are not a bug to fix.
**Household** pairs the two SHORT tables in `.cards2 pairs` (pairing the long
account list with the people card stretched it to nine accounts of empty
space), and **Retirement** is explicitly split by two `.yearhead` rules into
"Now — Where You Stand" and "Later — the Projection". **Investments** already
reads the right way round: the panes you edit, then the `Everything You Hold`
roll-up.

The cost to watch when moving a card is empty space, not scroll depth: a card
lifted OUT of a `.cards2` pair leaves its partner half-width with nothing
beside it. All four moves above are between full-width cards, which is why
none of them needed a layout change.

## The tile rows (2026-08-23)

**A `.goalgrid` fills ONE line when the line has room for every tile, and splits
into EQUAL rows when it does not.** Six net-worth tiles in a 1,283px card used
to come out five across with the sixth stranded underneath: plain `auto-fit`
takes as many as fit and drops the remainder wherever it lands. A lone tile
after a full row reads as a mistake — the eye finishes the row, finds a gap, and
goes looking for the thing that should have been there.
- **The count comes from `:has(> :nth-child(N):last-child)`**, which is "exactly
  N children" — the idiom the old four-tile rule already used, so nothing that
  isn't a grid of that size is touched.
- **The width comes from a CONTAINER query, never the viewport.** The same card
  is 1,283px wide on a desktop Progress tab, 710px in a `.cards2` half on
  Retirement, and a phone's width on a phone; a viewport breakpoint would answer
  the wrong question in two of those three. `:has(> .goalgrid)` makes the grid's
  own parent the named container `tiles` — a `.card-body` once `wireBoxes()` has
  run, a `.card` before that — so the width asked about is the width the tiles
  actually get, with no card padding counted in. Where no container is found the
  grid keeps the plain auto-fit line, which is what it always had.
- **The thresholds are the 230px minimum tile and the 12px gap, multiplied
  out**: 2→472, 3→714, 4→956, 5→1198, 6→1440, 7→1682, 8→1924. Narrowest first,
  so the widest rule that matches wins. The tests read those two numbers back
  out of the CSS and check every threshold against them rather than pinning the
  figures a second time, so a change to the tile floor fails the suite instead
  of quietly making a row too tight.
- **Only counts that leave rows differing by at most one tile are offered, and
  never a row holding a single tile.** Five tiles go 5, or 3 + 2, or one per
  line — never 2 + 2 + 1. Seven go 7 or 4 + 3; eight go 8, 4 + 4, 3 + 3 + 2 or
  2 + 2 + 2 + 2. Where the only alternative would strand a single tile the grid
  drops to ONE column and stacks, which is why three tiles between 472px and
  714px are stacked rather than laid out 2 + 1. **It is the same table in every
  app in the family** (2026-08-23), worked out against each one's own minimum
  tile: Sprint Predictability's `.tiles` and the starter's `.stats` at 160px,
  Flow Metrics' `.tiles.group` at 200px. A change to the table belongs in all of
  them.
- **A SHORT LAST ROW IS STRETCHED TO FINISH THE LINE**, never left with a hole
  at the end of it. `lcm(columns, last row)` tracks, the full rows' tiles
  spanning `lcm/columns` and the last row's `lcm/last row`: 3 + 2 is six tracks
  at span 2 and span 3. That is Golf Handicap's hand-counted grid — which its
  own file says has to be redone by hand if a tile is ever added — generalised
  to every count. The stretch is undone at the width where the tiles all fit on
  one line, and **undone on BOTH selectors**: `:nth-child` out-ranks a bare
  `> *` and would otherwise carry its span into the wider layout, which is a
  four-column row with two tiles spanning three tracks apiece. The test walks
  the queries in cascade order keeping each count's state, so that mistake fails
  as "the row is not full" rather than passing unnoticed.
- **Nine or more tiles fall back to auto-fit.** Only the Savings Goals grid can
  get there, and a list that long is a scroll at every width.
- **FOUR tiles are no longer pinned to 2 × 2.** The old rule forced two columns
  at every width to avoid 3 + 1; it also stopped four tiles ever using a wide
  screen, which is what "one line when it fits" asked for on 2026-08-23. They go
  2 × 2 below 956px and four across above it, and the Tax tab's two check-a-
  figure cards are where that shows.
- **`.pairs` is excluded by name from every one of these rules.** Its columns
  pair a projection with the figure it projects (see the Giving section); re-
  flowing them by count would pair each tile with the wrong partner. A test
  walks the rules and fails if any of them forgets the `:not(.pairs)`.

## Keeping the cents on a same-month row (2026-09-02)

`samemonth` is the ONE rule that rounds, and until now nothing on screen said
so. It was found the way an undocumented behaviour always is: a Taxes row that
read −$1,741.72 in 2026 came back as −$1,742.00 in the year built ahead, and the
only way to learn why was to read the source. The rounding itself is right — it
came from the sheet's `ROUND()`, and an electric bill estimated to the dollar
reads as an estimate, which is what it is. It is wrong on a row where the cents
ARE the figure, where the same rounding reads as a number somebody got wrong by
28 cents. So the answer is per-row, not per-app.

- **`cat.keepCents`, a boolean, stored only when TRUE and only while the row is
  a `samemonth` one.** `duePayAhead`'s discipline exactly: `false` and absent
  are one claim, junk deletes, and a row moved off the rule leaves the answer
  behind rather than carrying it into a rule that never asked.
- **No schema bump and no migration** — the `dueMonths` precedent, and here it
  is load-bearing rather than merely convenient. An absent key has to keep
  meaning "round", because that is what every plan written before the tick
  already does; a migration that wrote `keepCents: true` onto existing rows
  would be the same behaviour spelled a second way, and a migration that wrote
  `false` would silently move figures in a plan nobody had touched.
- **The tick is worded for what it DOES, not for the key's sense** — "Keep the
  cents", ticked meaning don't round. A box labelled "Round to whole dollars"
  would have to store the inverse of what it shows, and the inversion is exactly
  the kind of thing that survives one edit and not the next.
- **`ruleDesc` says which way the row rounds on BOTH answers.** A sentence that
  appeared only on the exception would leave the rounding rows — the ones whose
  figures surprise you — as silent as they were. `RULE_LABEL.samemonth` is now
  unreachable and says so in a comment; the table keeps the entry so it still
  lists every rule.
- **Nothing else rounds**, and adding a second rounding rule would make this a
  row-level setting shared by two rules with one name — think about whether
  `keepCents` should widen or whether the new rule should just not round.
- **Known and deliberately left alone: `Math.round` is asymmetric on negatives.**
  An expense of exactly −$100.50 rounds to −$100 while an income of $100.50
  rounds to $101. Half-dollar figures are rare enough that fixing it would move
  more real figures than it would correct, and the tick is now the way out for
  any row where that matters.

## The month view (2026-08-24)

**The Budget has two lenses on one object, and the second one lives INSIDE the
Budget tab rather than as a tenth tab.** `ui.budgetView` picks between them
(`'month'`, or absent for the grid) and `ui.activeMonth` says which month. The
grid is the right shape for planning a year on a wide screen — it is the
Numbers file this app replaces — and the wrong shape for the question a phone
gets asked, which is "what is this month doing, and can I fix that one row
while I'm standing in a shop": on a phone that meant pinching into a
thirteen-column table to reach one cell.

- **Why not a tenth tab.** The two are one object read two ways, the tab bar
  already wraps at nine, and a share link's own tab list, `SECTION_NEEDS`,
  `tabOrder`, `allowedViews` and the search's view filter would all have needed
  a tenth entry to say something the Budget tab already says. The switch sits
  in the year strip's row, where the Budget keeps its chrome, and it is a
  RADIOGROUP for the strip's own reason — it redraws the panel the Budget tab
  already labels rather than revealing one of its own. Neither a `.tab`'s
  rectangle nor a `.yearchip`'s bare pill: a segmented pair inside one hairline
  frame, which is what says the two words are alternatives to each other.
- **Nothing on it computes anything.** Every figure comes out of `C`, the same
  computed year `gridCard` draws from. `monthTotals(c, yr, m, prior)` is the
  ONE place a month is added up and it is pure — it takes no state, because
  everything it needs is the computed year and the year's own rows. The test
  that matters holds it against the grid's own subtotals over every month of
  `sampleState()`: two lenses on one object disagreeing is the only way this
  can be wrong while both pages look right.
- **Income ADDS `accountEarnings`**, exactly as the grid's Income subtotal
  does — that function stays the one reader for "what did the accounts earn?"
  and this must not become a second.
- **NO TRANSFER COUNTS AGAINST `net`** (2026-08-24, a day after it shipped the
  other way), and it is the one piece of arithmetic here worth arguing about.
  **Expenses means gone; Transfers means moved**, and the reader has already
  said which by choosing the section — so whether the far end is an account this
  app tracks decides only whether the other side of the move can be SHOWN, never
  whether the money counts as lost. It shipped adding the EXTERNAL transfers, on
  the reasoning that money leaving the tracked accounts had left; the first real
  month it met held a $7,500 Roth IRA contribution, and Left Over read
  −$7,275.89 IN RED over a month that earned $6,071.90, spent $5,847.79 and
  saved seven and a half thousand — while the same month's $1,000 sweep to
  Mid-term was excluded merely because that account is on this tab. Same act,
  opposite verdict, decided by where the far end is filed. `internal` and
  `external` are still reported (the Moved tile says how much stayed inside);
  `net` reads neither. A transfer that genuinely stops being yours belongs in
  Expenses, and the help says so.
- **The Moved tile shows exactly what the Transfers card totals, sign and all.**
  It used to show the internal part alone, NEGATED — two numbers on one screen
  computed differently and signed differently, which is what got asked about.
  Which rows stayed inside the reader's own accounts is marked on the rows
  themselves. Drawn whenever a transfer row carries a FIGURE rather than when
  the total is non-zero: two moves that cancel still moved money.
- **A row pointing the other way from its section is a REFUND** — cash back, a
  reimbursement, a returned purchase — and its line says it reduced the section
  rather than making it up. "2% of expenses" on a reimbursement said the
  opposite of what happened; `yearSpending` already netted these, only the
  sentence was wrong. For the same reason the Money Out tile's "most of it X"
  considers only rows that actually went OUT — a large refund sorts to the top
  by size and would otherwise be announced as the month's biggest spend.
- **`prior` is the year before's computed object**, for the same reason
  `computeYear` takes one: January's previous month is last December, which
  lives in another year's maps. Absent, the change is simply not reported —
  never zero, which would claim the balance stood still.
- **Editing is the grid's editor.** A row opens `openCellEditor` with the same
  three arguments the grid passes it, which is why notes, split months, the
  revert button and the reconcile note all work with no code of their own. Two
  things had to learn about these rows: `refocusGridCell` (after a save the
  view redraws and the element that opened the dialog is a dead node — the trap
  the tab bar and the year strip both hit) and `stripEditAffordances`, which
  takes `data-cat`/`data-bal` off in a shared view. Removing those attributes
  is what closes the door: the pointer, the hover and the tab stop all key off
  them in CSS, and `wireMonthRows` looks for them too.
- **`yearOfMonth` decides which grid a month is read from** — its own calendar
  year whenever there is a grid HOLDING it, else the year whose projection tail
  reaches it. Membership is checked rather than assumed off the key, because a
  grid year need not start in January. Getting this backwards would draw
  January's cells out of December's projection while the editor wrote them into
  January, and the two would disagree for ever.
- **The two lenses stay on the same place**, and that is a PAIR of moves:
  `pickMonth` sets `ui.activeYear` from the month, and the switch, on the way
  into the month lens, moves `ui.activeMonth` into the active year when it
  isn't already there. Without both, switching lenses teleported the reader to
  whatever the other one was last left on.
- **Rows are sorted BIGGEST FIRST**, and that ordering is the view's whole
  argument — a grid keeps the order you arranged because you read ACROSS it; a
  month is read DOWN. `settings.rowSort` is deliberately not consulted here.
  A row with nothing recorded sinks to the bottom rather than disappearing:
  opening one is how a month gets filled in, and on a phone this list is the
  way in. **THREE EXCEPTIONS now**, and they are written down here because the
  sentence above it is no longer true at all: since 2026-08-26 a row with
  NOTHING RECORDED in the month is hidden, whatever the reason, and the only
  blank row left on the page is one with a bill due in that month. See "An
  empty row drops off the Month page" below — `rowHideable` is the one place
  that decides, `monthUntouched` keeps every row on a month you have not
  started, and the reveal sticks.
- **The estimate kinds are the GRID's**, and the `.c-*` selectors name both
  readers (`.grid td.c-auto, .mamt.c-auto`) rather than being copied — a line
  style that drifted between the lenses would be one month claiming to be
  settled in one and estimated in the other. The tiles italicise, the section
  totals wear the same marks, the chart's projected months are outlined by
  `dashedBarEdge` (Chart.js 4's bar element ignores `borderDash`), and the month
  you are reading is the one bar filled solid.
- **The chart has ONE dataset on purpose.** "Left over" is one figure that can
  go either way, so the two directions are two ends of one series rather than
  two series to tell apart.
- **THE ZERO LINE IS DRAWN HEAVY, and this is the only chart in the app where
  that is right.** Above it a month added to your money, below it the month cost
  you some — every other chart here measures a quantity that cannot go
  backwards, so the emphasis is local to `buildMonthNetChart` rather than in the
  shared `chartAxes()`, where it would put a rule through the middle of charts
  with no crossing to mark. The mark is WEIGHT: `--chart-tick` (the axis label's
  own ink, against `--chart-grid`'s near-background hairline) at 2px, with the
  `$0` label bold to match. Both colours resolve ONCE outside the scriptable
  options — those run per tick per frame, and `getComputedStyle` has no business
  on that path.
- **The bars carry RAG, and it is the one chart entitled to it** (2026-08-24, at
  Charlie's request). The file's standing rule is that hue may never carry a
  meaning ON ITS OWN — he reads none of the four palettes by colour. Here it
  does not have to: the bar's SIDE of the zero line already says which way the
  month went, and the line above is drawn heavy for exactly that reason, so the
  colour is redundancy laid over a signal that is already there. `--ok` (the
  pack's green at hue ~150) and `--err`, full strength for the edge and the
  `-bg` tints for the fill; nothing is invented, and the key under the chart
  says what the two sides mean in words. **Do not copy this to another chart**
  without first asking what non-hue signal is carrying the meaning there.
- **The LEFT OVER tile wears the same pair** (`.goal.up` / `.goal.down`,
  `.goal.done`'s grammar applied to a figure whose SIGN is the question). It is
  the only tile that reports a direction — money in, money out and a closing
  balance have none of their own — and the same condition is met: the figure
  carries its own minus sign, and it is read beside a chart saying the same
  thing by which side of zero a bar sits on. Exactly $0 is neither and stays
  plain. The rules sit AFTER `.goal.est` deliberately: both selectors weigh the
  same, so source order decides, and an estimated month keeps the status ink
  rather than going quiet — which matches the chart, where a projected month is
  just as green or red and says it is projected with a DASH. `.goal.est`'s
  italic still applies and is what carries "not settled yet" on the tile.
  `--text-secondary` on both tints was measured before shipping: the worst pair
  across the four palettes is 4.63:1, so the label and the foot clear AA
  everywhere.
- **The strip's two chip marks are SHARED, and `monthAhead` is why they can be**
  (2026-08-24). `y-future` — the dotted underline — is on a year that has not
  begun AND on a month still to come; `chip-now` is on this year and on this
  month. Three places make the "still to come" claim on one page (the chip, the
  chart's dashed bar, and the estimate kind on every figure), so `monthAhead(yr,
  m)` is the ONE reader: past the entered marker on a live year, never on a
  finished one, which computes nothing. `monthNetPoints` reads it too rather
  than keeping the inline comparison it was born with. `y-summary` stays
  year-only, because a month is never a summary.
- **Clicking a bar SCROLLS THE PAGE TO THE TOP**, and that is not decoration:
  the month changes at the top of the page and the bar is at the bottom of it,
  so the only visible effect was the bar under the pointer going solid — which
  reads as the click doing nothing, and was reported that way. The family's rule
  for an action that moves you somewhere is to put the place you moved to in
  view (`scrollGridToNow`, the year strip's settle, the tab bar's nudge). It is
  INSTANT, never smooth — an animated scroll is a silent no-op in some engines —
  and `pickMonth` returns a boolean so a click on the month you are already
  reading does not throw the page about.
- **ONE INFO DOT PER THING IT EXPLAINS.** The five tiles, the three section
  cards, Accounts and the chart each carry their own, and each opens a sheet
  about that heading alone. It shipped as ONE entry behind ONE dot on the Money
  In tile, which put the explanation of the closing total three paragraphs deep
  in a window opened from a different figure — the dot convention says a dot
  answers for the heading beside it, and a five-part sheet under the first of
  five tiles was not keeping it. The three section cards share `monthRows`,
  which is where the estimate-italic convention is explained now.
- **The due block is TWO dots, and the line between them is WHO IS ASKING**
  (2026-08-27). `monthDue` was one 3,539-character entry answering two questions
  that are never asked together: in the row editor you are SETTING a due date
  (the day, the months, which month the money leaves), and on the Month page it
  is already set and you want to know why a row is on the card and what makes it
  go quiet. Whichever half you came for, the other was in the way — and the
  window scrolled. `rowDue` ("Setting a Due Date") hangs off the due block's own
  opener in the row editor, `monthDue` ("Due and Waiting, Explained") stays on
  the card of that name, and each points at the other in one sentence so the
  half you did not get is still findable. **The window is named for the HEADING
  it sits beside, not for half of it** — it was "How Due Dates Work", which
  named the Due half of a card called Due and Waiting while the entry covered
  the warnings, what the card gathers, and both ways a bill that never arrived
  is handled. Neither restates the other: the projection rule
  is explained only where you tick the months that feed it, the warnings only on
  the card that shows them. Pinned both ways in `tests.html`.
- **A ROW EDITOR FIELD CAN CARRY AN INFO DOT** — `help: 'key'` in its spec
  (plus optional `helpLabel` for the aria-label), rendered by `buildFields` into
  the label with `helpBtn`, for a setting whose explanation has outgrown the
  `hint` under its box. Three things are load-bearing. It goes INSIDE the
  `<label>`, because `.grid-fields > div > label.field` sizes the label as a
  DIRECT child and a wrapper would break that — and a `<button>` is interactive
  content, so the label does not activate its control for a click on one, which
  is what keeps the dot on a CHECKBOX from ticking the box it explains (verified
  in Chrome: the accessible name stays "It has a due date", the dot is a
  separately-named button, and clicking it leaves the box alone). It needs its
  OWN listener on `rowDialog` — the one that routes every other dot is on
  `#views`, and the dialog is not in it. And the help sheet opens ON TOP as a
  second modal in the top layer; Escape closes the upper one first and the
  editor is still there underneath with nothing lost. Golf Handicap has had the
  same shape on its Holes played field since before this.
- **`summaryBalances` was the same fault, found by sweeping the family** (2026-08-27).
  "Balances in a Summary Year" under a heading reading "Balances & Derived Rows" — and
  unlike the due block, the BODY was half an answer too: one paragraph about balance
  rows and not a word about a derived one. It is "Balances & Derived Rows, Explained"
  now, and says what a derived row is (a subtotal the old sheet worked out from rows
  already listed), why both kinds are held out of the year's flows (counting a subtotal
  beside the rows it sums counts that money twice), and which tick moves a row between
  the groups. **A rename over a body that still answers half the heading is the same
  fault in a better hat** — the test checks the words, not just the title.
  **The sweep's verdict on the rest: they are fine.** About a dozen windows describe the
  ANSWER rather than repeating the heading (`safeRate` under What Retirement Costs,
  `taxCheck` under What You'd Pay, `liabilities` under What You Owe). That is not this
  fault and must not be "fixed": the heading asks a question and the title answers it,
  which excludes nobody. The rule is narrow on purpose — it bites when a title names a
  proper SUBSET of a compound heading, because that is what tells half the readers the
  window is not theirs.
  **The dot-coverage test's scan knows both call sites** (`helpBtn('key'` and
  `help: 'key'`); a new way to ask for a dot must be added to it or the entry
  reads as one nothing renders.
- **`dashedBarEdge`'s `_trueBorder` may be a LIST**, one colour per bar, because
  of the above — a scalar is the old behaviour and is what the three earlier
  callers pass. The plugin must never fall through to `ds.borderColor` on a
  per-bar dataset: that is an array there, and it would stroke every projected
  month in whatever colour index 0 happened to be.
- **The tooltip is the grid's.** `wireGridTip` looks for `.gridwrap, .tipzone`
  now — one selector rather than a second copy of a handler that never asked
  what kind of box it was in. The month view wraps itself in `.tipzone`.
- **On a phone the strip stacks** (≤700px): switch and arrows on the line
  above, rail full-width underneath. Three controls in one row is one too many
  at 430px — the switch alone took more than half of it and the rail was left
  showing a month and a half. It reshapes the YEAR strip the same way, which is
  the same improvement for the same reason.
- **A share link sends `ui: {}`**, so a link always opens on the grid, which is
  what somebody sending "the budget" means by it. The switch still draws in a
  shared view — choosing how to read someone's figures is reading.

## Due dates (2026-08-25)

**A budget row can say WHEN its money is owed** — a day of the month, and which
months it falls in. Four flat fields on the category, the overflow row's shape:
`duePay` (`'manual'`/`'auto'`), `dueMonths` (absent = every month), `dueDay`
(absent = no fixed day), `dueHold` (a `YYYY-MM`, reminders paused). All four
DELETED when inapplicable, never `undefined` — the Firestore rule.

- **`duePay` is the MARKER.** A row either names how it is paid or has no
  schedule at all, which makes "is this row scheduled?" one whitelisted-
  vocabulary check (`DUE_PAY`, above `let state = load()` with the other
  vocabularies — the temporal-dead-zone rule). A bad `duePay` deletes the other
  three; a bad `dueMonths` drops on its own and leaves the schedule standing.
  This is deliberately the discipline `cat.rule` still lacks.
- **NOTHING HERE REACHES THE ENGINE.** `computeYear` does not know the fields
  exist, so a corrupt or hostile schedule can make the page quieter or noisier
  and can never move a figure. That is what makes it safe to be display-only,
  to ride in a share link unchanged, and to need **no schema bump and no
  migration** — the `a.buckets` precedent.
- **THE SCHEDULE DRIVES THE ESTIMATE ENGINE (2026-08-25), and this is the one
  place due dates DO reach computed figures.** It shipped orthogonal — the
  `quarterly` rule taking its beat from the last month a figure was TYPED into,
  `dueMonths` describing when the money is owed, and the editor telling the
  reader they were two questions. That was wrong in the way a thing is wrong
  when the reader has already answered it: a bill due Jan/Apr/Jul/Oct but paid
  late in March estimated itself into Mar/Jun/Sep/Dec, and the row's own ticked
  months said one thing while the grid said another.
  - **`paysIn(cat, m)` is the gate**, applied in `computeYear` around the RULES
    dispatch: an estimate is placed only where the row says its money moves. A
    ticked list is a statement that it does NOT move in the other months.
  - **`quarterly` hands back the figure and lets the gate place it** when a list
    is set — `every` steps aside. The two are answers to one question and the
    list is the better one: stated rather than inferred, and it cannot drift.
    The modulo beat is measured from the last month with a figure, so ONE bill
    paid late re-phases the whole row — which is exactly what happens to a bill
    whose biller is behind, the case a cycle rule is most often used for.
  - **It makes `carry` safe on a bill that is not monthly**, which the engine
    section's note said it could never be ("the sheet types Phone/Parking/Water
    into each month they apply, so a carry rule there would invent charges").
    With a ticked list it invents nothing.
  - **A TYPED FIGURE IS NEVER GATED.** It wins above the gate, the way a typed
    figure wins everywhere here — a bill that turned up in a month the schedule
    did not expect is a fact.
  - **A plan with no ticked list computes byte for byte what it always did**,
    because `paysIn` is true for every row without one. That is what keeps the
    real-data cross-check honest, and it has a test of its own shouting about
    it. Verified against the eight imported years before shipping.
- **`dueStatus` is the one verdict** and everything on screen reads it — the
  `accountEarnings` discipline. Check order, and every step is a decision: no
  schedule → not one of its months → **not a live grid year** → an `actual`
  cell → held → autopay → the calendar.
  - **THERE IS NO "the month is entered, so it is paid" SHORT-CUT, and its
    absence is load-bearing.** An entered month with no stored cell resolves
    `missing`, NOT `actual` (`computeYear`'s entered branch) — so that
    short-cut would announce the bill was paid in precisely the case the
    feature exists for: October closed, the water bill never came, the row
    blank. Everything the marker genuinely settles arrives as an `actual`
    anyway, because `markMonthEntered` mints the month's estimates. It was
    written that way first and a test pins the fix.
  - **A non-live year returns `null`, never `'paid'`.** A pinned year states its
    balances and every category cell in it resolves `missing`; measuring one
    against today would put four figures of days-late on every scheduled row of
    2021.
  - `mixed` is **not** paid — a split month with one part still an estimate has
    not finished happening.
  - `paid` beats `held` (a fact beats a request for quiet), and `dueFootWords`
    still says "autopay" on a paid autopay row: the verdict is about the state,
    the sentence is about the arrangement.
- **`duePayAhead` — "the money leaves the month before" (2026-08-25).** A bill
  due on the 3rd is one you settle a week earlier, which is in the PREVIOUS
  month. **Nothing in the figures can tell an early payer from an on-the-day
  one**: a rent cell in August is August's rent to one and September's to the
  other, and both are one payment a month. So the row has to say, and a boolean
  is the honest shape.
  - **Getting it wrong is the worst way a reminder can fail.** Left unshifted, a
    consistent early payer reads LATE every single month for ever, which teaches
    you to ignore the warning.
  - **`dueOn` is the one place the shift lives**, and that is what makes it
    safe. Everything downstream asks that function the same question — "does
    this row's money move in month m, and against what deadline?" — so the hide
    rule, the estimate gate, the outstanding count and the reminder all move
    together rather than three moving and one being forgotten.
  - **The look-ahead SKIPS a shifted row.** It is already reported in the month
    it pays, which is the month you are reading; letting the look-ahead have it
    too would report the month after next.
  - The lead counts to the DUE date, not to the paying month — so "a week before
    the 3rd" starts warning on the 27th of the month before, which is right.
  - Stored only when `true`: `false` and absent are one claim, and an absent key
    leaves a row that was never asked exactly as it was.
- **A row with no fixed day never counts down.** Its deadline is the month's
  last day — a date the app chose, not one the reader gave — so the pill reads
  "Due this month" / "Was due Apr 2026" and prints no day count. `exact: false`
  carries it.
- **`markMonthEntered` skips a HELD row**, and without that the outstanding
  count is dead on arrival. A quarterly bill on a beat month resolves `auto`,
  so entering the month stamps it `actual` — "paid, at the estimate" — for a
  bill that never arrived. Entering a month happens every month, so this is the
  default path, not an edge. The toast says how many rows it left alone.
- **`outstandingDues` is bounded by the plan's own months AND, since
  2026-08-26, by the years that actually carry the schedule** (`scheduledIn` —
  it was only the first of those for a day, and on Charlie's real file that cost
  36 imaginary unpaid quarters back to 2012; the measurement is in "What never
  got paid, on the page you actually open" below). It takes a month
  list and an `at(month) → {cell, has}` lookup rather than reaching for `C`,
  which is both what lets it span a year boundary (January's previous quarter
  is in last year's computed object) and what stops it walking off the front of
  the plan inventing unpaid periods. `has: false` for a month whose grid does
  not carry the row — absent is not unpaid.
  **The AMOUNT is the hard part**: a held row's past months are usually blank
  and summing blanks gives $0.00, which is a figure and is wrong. The row's most
  recent real figure stands in, and `estimated` says so out loud; with no figure
  anywhere, `total` is NULL — the savingsPulse rule.
- **THE CARD LOOKS ONE MONTH AHEAD, and only forward.** A bill due the 1st is
  one you pay in the month BEFORE it, and a lead time exists to tell you while
  there is still time to act — so asking only about the month being read put
  the 1 September rent on the September page, which nobody opens on 25 August,
  while the August page showed August's own rent 24 days late and said nothing
  about the one worth doing something about. `dueStatus` was always right about
  it; it was simply never asked.
  - **Only `soon` and `due` travel back**, and that filter IS the guard — no
    "is this the current month" test exists anywhere. A deadline that has not
    arrived cannot be late, so a past month's page can never drag a later
    bill onto itself; and a late bill belongs on its own month's page, which
    is a click away.
  - **One month deep, by construction.** A sixty-day lead makes more deadlines
    `soon`, but the card still only asks about `m` and `monthAdd(m, 1)` — a
    bill two months out is not one you can pay before this month turns.
  - The line **names its month and points at that month's cell**
    (`data-m`/`data-year`), so opening it records the payment where the money
    will actually go, and the figure beside it is honestly next month's rather
    than a number on an August page that looks like an arithmetic error.
  - `lookIn(month)` is the one lookup the look-ahead and `outstandingDues`
    share — both need a month in whatever year holds it, which is why neither
    reaches for `C` directly.
- **A held row is reported in EVERY month, not only its own.** What is stacking
  up behind it is a fact about the ROW. Reporting a quarterly bill only in
  January, April, July and October hides three unpaid quarters for eight months
  of the year and then announces them in the month you would have noticed
  anyway.
- **The hide rule keys on the KIND, not the value.** `rowHideable` needs all
  three: a schedule, a month it excludes, and `kind === 'missing'` with no note
  and no split parts. `r.v === 0` was the first version and it is wrong three
  ways, ALL of which leave the section total untouched — so a totals test would
  pass while a real record vanished: a split month netting to zero, a STATED
  $0.00 (a claim somebody made), and a note on a zero cell (whose dot goes with
  it).
  - **The rows are RENDERED and merely `hidden`**, never omitted, so search,
    `refocusGridCell` and a screen reader's own find still reach them.
  - **`.mrow[hidden] { display: none }` is required.** `[hidden]` lives in the
    BROWSER's stylesheet, where a class selector out-ranks it, so `.mrow`'s
    `display: grid` wins and the attribute becomes a lie — `el.hidden` reads
    true while the row is on screen. Found exactly that way.
  - The reveal is **`ui.showNotDue`**, beside `ui.collapsed`, absent when
    untouched. A DOM-only toggle was the first idea and it dies on the next
    render — every cell edit ends in `save(); render()` — so catching up three
    quarters of a bill would be reveal, tap, save, reveal, tap, save.
- **IN A SHARED VIEW EVERY COUNTDOWN IS SILENT, and that is the price-bar rule
  rather than a permissions decision.** "Due in 3 days" measures the SENDER's
  frozen deadlines against the READER's clock, so six months after a link is
  made every scheduled row announces that somebody else's bills are half a year
  overdue. No card, no pills. The schedule itself is a fact about the plan and
  stays in the footer. **Rows are not hidden either**: a recipient has no reveal
  button they would think to press.
- **`settings.dueLeadDays` is read STRICTLY through `rateOrNone`, never
  `num()`** — and it is the one free scalar where that distinction bites.
  `num('junk')` is 0, and 0 is INSIDE this field's range ("warn me on the day"),
  so the ordinary clamp would mint a real-looking setting nobody chose. Clamped
  0–60 at three places: the boundary, the Preferences save, and `leadDaysOf` at
  the point of use — the `limitsFor` discipline, because `settings` travels in
  full in every share link and a payload need not have been through the
  boundary this build runs.
- **`dueLeadDays` sits in Preferences by LAYOUT, `wide`, directly above the
  retirement trio.** An ordinary field added to the group above the zoom shifts
  those three by one column and strands the first of them at the end of the row
  above — the alignment the zoom exists to protect. A wide field ends the row
  in progress instead, so the trio still starts one, and `applyFieldSpans`
  holds its BOX to one column while its long hint gets the width.
- **`rolloverYear` copies a row's LIST fields, not just the row.** `{ ...cat }`
  is shallow, so the two years shared one `dueMonths` array and editing this
  year silently rewrote next year's. `cat.accounts`, `thresholdAccounts` and
  `capAccounts` had the same latent bug and are copied now too — the row editor
  was only safe because it assigns a freshly built array rather than pushing
  into the old one, which is a property of one call site rather than of the
  data. A test pins it.
- **The months picker is `wide` and LAST in its block.** A wide field ends the
  row in progress, and every field in the due block shows together — unlike the
  dividends `accounts` picker, whose `showIf` never co-occurs with a neighbour,
  which is why that one gets away with sitting mid-list.
- **Deliberately out of scope**: any notification outside the Month lens (no
  push — a notification that only fires while the page is open is not a
  reminder, and background sync is unsupported where it would matter); a
  separate "mark as paid" tick (paid IS `kind: 'actual'`, and a second door to
  one fact is the drift this file exists to prevent); per-row lead times;
  anything finer than monthly (the plan's unit is `YYYY-MM`); autopay
  VERIFICATION (`duePay: 'auto'` describes an arrangement and claims nothing
  about whether the payment cleared — the help says so); and letting the
  schedule drive the estimate engine, which is a real follow-up (`dueMonths`
  would make `carry` safe on a quarterly bill) but changes computed figures and
  therefore sits behind the real-data cross-check.

## A row that stopped (2026-08-26)

**A budget row can say the last month it had money in it** — `cat.until`, a
`YYYY-MM` string, absent while the row is still in use. Asked for from life:
Charlie changed credit cards and stopped redeeming cash back every month (the
new card collects points, which the budget never sees), so a row that was right
for four months of 2026 is wrong for every month after it — and left alone it
kept estimating itself forward, kept its place on every Month page, and got
copied into next year for him to delete by hand.

- **It is the SAME key, shape and words an account already uses** (`a.until`,
  "Stopped using it"). Two objects answering one question the same way is one
  vocabulary rather than two, and the account field's own hint was the model for
  this one's. Guarded at the boundary exactly like `dueHold`, and deleted when
  inapplicable — never `''`, never `undefined` (the Firestore rule).
- **STATED, never inferred, and that was a real fork.** "The last month with a
  figure" was the other option and it is worse in the way inference usually is:
  the row's whole behaviour would move every time a cell was typed or cleared,
  clearing the last figure would silently un-stop the row, and a bill that
  simply has not been paid yet is indistinguishable from one that never will be.
  Charlie picked the stated month.
- **`rowEnded(cat, m)` is the one reader**, and it lands in exactly three
  places — `rowHideable` deliberately not among them, see below:
  - **`paysIn`, ABOVE the ticked month list.** This is the one thing here that
    reaches `computeYear`, and it has to — a `carry` row that kept repeating
    would never be empty, and a row that is never empty can never drop off the
    Month page, which is the whole point. Above the list because most rows have
    no schedule at all and the row this was built for is one of them.
  - **`dueOn`, gated on `m` (the month the money MOVES, not the deadline).**
    One line, and it silences the reminder, the hide rule, the outstanding count
    and the estimate gate together — the `duePayAhead` discipline. Without it a
    cancelled bill reads late every month for ever, which is the failure that
    teaches you to ignore the warning.
    Between the two of them they are also what makes the row DROP OFF the Month
    page, and they do it at ONE REMOVE rather than by the hide rule naming
    `until`: no estimate and no deadline means an empty cell, and an empty cell
    is what hides. That indirection is deliberate — see "An empty row drops off
    the Month page".
  - **`rolloverYear`**, which filters the categories BEFORE the cells loop reads
    them, so no orphan cell is minted either. Compared against the new year's
    first month rather than assumed: a row stopping inside the new year is still
    that year's row for as long as it lasts.
- **A TYPED FIGURE STILL WINS**, above the gate, the way it wins everywhere in
  this file. A charge that turned up after you stopped is a fact and it keeps
  the row on that month's page.
- **`yearsDroppingRow` is the OTHER half of "it doesn't carry over"** — the
  years already built ahead, which `rolloverYear` can never reach. Pure and
  exported so its two guards can be pinned, and both guards are about not
  deleting something somebody said: a year holding the stop month keeps the row,
  and a year holding any stored cell for it keeps it (dropping a row takes its
  cells with it, and a typed figure is the one thing here that is never ours to
  throw away). Said out loud in the save toast, because losing a row from a year
  you weren't looking at is a bigger surprise than gaining one.
- **No schema bump and no migration** — the `dueMonths` precedent. An absent key
  is what every existing plan already has, and it means exactly what those plans
  currently do; a test pins that a plan with no stopped rows computes byte for
  byte what it always did.
- **It says so in two places on screen, and both are about a row you can see.**
  The grid's row label ("· stopped Apr 2026", beside the schedule) is what stops
  a row whose figures end halfway across from reading as an oversight. The Month
  page's row footer says the same thing — worth the words there precisely
  because the row is hidden by default, so the only reason you are reading it is
  that you pressed Show and want to know what it is doing on the page.
  "Nothing recorded" alone answers the wrong question: every hidden row has
  nothing recorded.
- **The editor field is AFTER the due block and unconditional.** A row that
  stops need never have had a due date. `dueMonths` above it is `wide`, which
  ends the row in progress, and `noteField` below it is wide too — so `until` is
  alone on its row and `applyFieldSpans` stretches the CELL while holding the
  BOX to one column, which is the existing answer to a lone field and needed
  nothing new.
- **The sample carries one** (`cash-back`, an INCOME row on `carry`, stopped in
  April with four months of figures) — a stopped row is not always a bill, and a
  `carry` rule is what makes the demo worth having: without the stop it would
  repeat April into every remaining month, ride into next year and sit on eight
  Month pages saying nothing.

## An empty row drops off the Month page (2026-08-26)

**A row with nothing recorded in the month is hidden, whatever the reason it is
empty.** This shipped twice on the same day and the second version is the one
that matters, so the first is written down here as the mistake it was.

**What shipped first**: the schedule's months, plus a stopped row, plus "the
month is entered or the year is pinned" — three conditions, `rowHideable` with
a `finalized` argument, `monthDues` taking one more parameter. **What killed
it**: a phone screenshot from Charlie. One Expenses list, four rows reading
"nothing recorded" (ATM, Chase Zelle, Checks, M&T Zelle) sitting directly above
a line offering to hide two OTHER blank rows — with nothing on the page to tell
the two groups apart, because the difference was an invisible fact about the
month. His words: "with the new wording it's confusing to see some empty rows
hidden while others aren't." **The lesson worth keeping: a rule the page cannot
explain to the person reading it is not a rule worth having**, and "the month is
entered" is exactly that kind of rule — the reader cannot see it from the rows.

- **`rowHideable(cat, r, m)` is two lines now.** Is the cell empty, and is a
  bill due here. The entered marker and `until` lost their say; they still gate
  the estimate engine, the reminders and the outstanding count, and `until` is
  what EMPTIES the later cells in the first place — two steps, one visible
  result, and no mention of `until` in the hide rule at all.
- **THE ONE EXCEPTION IS A BILL DUE IN THIS MONTH, and it earns it by being
  visible.** Such a row's footer reads "due the 20th" or "autopay, the 1st"
  where a hidden one would read "nothing recorded", and three of its states wear
  a pill besides — so every row left on the page with no figure says why it is
  there, which is the thing the screenshot was missing. Hiding these instead
  would have taken Charlie's water bill off Expenses in the months it is
  actually owed, on the grounds that he had not paid it yet.
- **`dueOn`, not `dueStatus`, is what the exception asks.** That keeps it true
  in a year that is not live (a pinned year has no verdicts, and a bill it says
  fell in March still fell in March), and it is also why a STOPPED row hides
  with no word about `until` here — `dueOn` is null after the stop.
- **WHAT COUNTS AS EMPTY is unchanged and is the part that can lose money**: a
  stated $0.00 (`kind: 'actual'`), a note on a zero cell, and a split month
  netting to zero all keep the row. That is what keeps the visible list adding
  up to the total under it, and it is the only reason a totals test would not
  have caught the first version of this predicate.
- **`monthUntouched` — A MONTH YOU HAVE NOT STARTED KEEPS ALL ITS ROWS.** Found
  by loading a fresh plan: the starter budget arrives with twelve expense rows
  and no figures in any of them, so the Month page a new reader opened was three
  headings, a $0.00 total apiece and a button offering to show them the budget
  they had just made.
  **It shipped PER SECTION and that was wrong for about an hour** — Charlie
  spotted it on his own plan, where Transfers listed three untouched accounts in
  a month whose Income and Expenses had hidden theirs. A per-section guard fires
  on whichever section happens to be entirely empty while the rest of the page
  is full, which is precisely the inconsistency the hide rule exists to remove;
  the guard meant to protect the rewrite was reintroducing it. Asked about the
  MONTH now, once, and handed down to all three sections.
  **A section may therefore collapse to its heading, its total and a reveal
  line, and that is the right answer**: $0.00 moved is a fact worth printing and
  three rows saying "nothing recorded" underneath it are not. Only CATEGORY rows
  are counted — account balances are computed and always there, so they can
  never say whether you have started.
- **`ui.showNotDue` KEEPS ITS NAME** though it now means "show the empty rows".
  Renaming it would orphan the setting in every stored plan and every backup for
  a word nobody sees. The reveal STICKS, and that is what answers the old
  argument for keeping blank rows on the page ("opening one is how a month gets
  filled in"): filling a month in is one tap and then an ordinary list.
- **`monthDues` asks EVERY row now, not only the scheduled ones.** The
  `continue` on a row with no `duePay` used to skip the `quiet` pass with it,
  which is why the hide rule could only ever be about schedules.
- **Still nothing in a shared view.** `viewOnly` forces `quiet: []`, and the
  reason is unchanged: a recipient has no reveal button they would think to
  press, and a section that silently drops rows out of a plan somebody sent them
  is worse than a long list.

## What never got paid, on the page you actually open (2026-08-26)

**On the CURRENT month only, the Due and Waiting card also lists what is still
unpaid from earlier months.** Found by Charlie asking why his missing water bill
wasn't warning him: it was. The July quarter was correctly marked 54 days late —
on the JUNE page, because his row is `duePayAhead` and the money should have
left in June. Two pages back from the one he opens. A warning nobody is shown
is not a warning.

- **The old rule still holds everywhere else.** "A late bill belongs on its own
  month's page" was protecting against reading July next year and being told
  about this April, and `m !== thisMonth()` is the whole guard: no past page and
  no future page gains a thing. THIS month is the page you open, so it is the
  one page where "still unpaid" is a fact about you rather than about somewhere
  you are visiting.
- **`outstandingDues` already worked it out.** Nothing but a held row had ever
  asked it — the function has been right since it was written and was simply
  wired to one caller.
- **A HELD ROW IS SKIPPED.** It is already reported in every month, with a count
  and a figure, by the waiting line. Two accounts of one backlog is how they
  come to disagree.
- **`live: true` is passed to `dueStatus` for these lines** even though the
  month may sit in a year pinned since. That looks like the thing `dueStatus`'s
  third check forbids and it is the opposite: that check stops a pinned year
  measuring EVERY scheduled row against today, and these months have been
  selected one at a time by `outFor` as genuinely outstanding. A quarter that
  went unpaid did not stop being unpaid when the year was frozen.
- **`dueRow` learned a second direction.** `aheadrow` and `backrow` wear the
  SAME mark — a rule down the leading edge — because the mark says "not this
  month" and which way is a question the sentence answers better than a border.
  The back line says "still unpaid, from Jun 2026" and carries `data-m` for that
  month, so opening it records the payment where the money will actually go.

### The bound that made it safe: a schedule is stored PER YEAR

**This is the bug the feature would have shipped on top of, and it was already
live in the held path.** `outstandingDues` walks `planMonths(state)` — every
month the plan holds, 2012 to 2027 on Charlie's file. Its `has` lambda asked
whether the year CARRIES THE ROW, and that is not the same question: a schedule
lives on the row **in each year separately**, so ticking "quarterly, the 3rd" on
Water in 2026 leaves all fourteen earlier copies of that row with no `duePay` at
all. His imported history types the water bill in Jan/Apr/Aug/Nov; his 2026
schedule pays it in Mar/Jun/Sep/Dec. Every one of those older quarters read as
an unpaid period.

**Measured on his real file: 36 outstanding periods, oldest 2012-03. The true
answer is 1.** He never saw it only because he had not set `dueHold` yet —
pausing reminders on that row would have announced fourteen years of imaginary
arrears.

`scheduledIn(yr, id)` is the fix and both readers share it, so the count in the
waiting line and the list of what never got paid can never disagree about which
periods are real. **A year whose plan never said when the money was owed cannot
be behind on it** — the `has: false` rule the function already had, asked about
the right fact. Two tests put the old lookup and the new one side by side over
the same months.

**The general lesson**: a row field added today is stamped on THIS year's copy
of the row (and, through `applyToRow`, on the projection years ahead) — never
backwards. Anything that walks the whole plan's months has to ask each year's
own copy what it says, not assume the row it started from speaks for all of
them.

## A note with no figure (2026-08-26)

**`kind: 'missing'` is a legal STORED cell now — a note on a month where
nothing happened.** Asked for the same afternoon the back-dues shipped: Charlie
wanted to write "the bill never came" on the month his water bill went missing,
and doing so silenced the warning he had just asked for. Three separate things
conspired, and every one of them was ours:

1. **The amount box opened showing `$0.00`.** `missing` is worth 0 because
   nothing was recorded, and the prefill read `resolvedCell.v` without asking
   what kind it was — so a blank month invited you to save a figure it had
   invented. It opens EMPTY now (placeholder "Nothing recorded"), and the
   context line stops appending "· currently $0.00" to the words "nothing
   recorded", which was a contradiction printed on one line.
2. **Clearing the amount deleted the whole cell, note included.** So the only
   way to keep the words was to type a figure, and the only figure that fits is
   0 — a STATED $0.00, which in this file means the bill came and was nothing.
   `dueStatus` reads `kind === 'actual'` as paid, so the warning went out.
3. **The boundary would have undone the fix on the next reload.** `coerceShape`
   coerced any kind outside `['actual','manual','mixed']` to `'actual'`.

- **THE DISTINCTION IS THE POINT.** A stated $0.00 and nothing recorded are two
  different claims, and this file already treats them that way everywhere —
  `rowHideable` refuses to hide a stated zero, `dueStatus` counts one as paid.
  A note-only cell is the third state that was missing: *something written on a
  month that still records nothing*.
- **`computeYear` BRANCHES rather than treating it as a stored cell**, and that
  is the load-bearing part. Falling into the stored branch would SUPPRESS a
  future month's estimate, so annotating next March would silently empty it.
  The note rides along on whatever the month would have resolved to anyway —
  `missing` in an entered month, the rule's `auto` figure in a future one.
- **`markMonthEntered` treats it as no cell too**, and carries the note onto
  the actual it mints. Otherwise writing "check this one" on next month would
  quietly stop that row being entered at all.
- **The boundary deletes a `missing` cell with nothing written on it**, and
  strips any `v` or `parts` off one that has: one spelling of nothing, and a
  kind that claims no figure may not smuggle one.
- **`cellTip` prints no figure for a `missing` cell.** "$0.00 · nothing
  recorded" is the same contradiction as the context line, and it only started
  being seen once a blank month could carry a note worth hovering over.
- **Everything downstream was already right** — EXCEPT the four rules that read
  back along `yr.cells` with `if (cell)`: `carry`, `grow`, `quarterly` and
  `avg` read a note-only month as a stored $0 and carried it forward, and the
  overflow sweep took the stored branch on one (found by the 2026-09-01 audit,
  see Six Fixes From the 2026-09-01 Audit; `isFigure(cell)` is the test now).
  `notesOfYear` reads `yr.cells` for any note whatever the kind, `hasNote`
  earns the grid dot, `rowHideable`'s note guard keeps the row on the Month
  page, and `outstandingDues` still counts the period as owing.
- No schema bump: no existing plan has one, and a build that predates this
  reads a note-only cell as a stated $0.00 — the state it would have been in
  anyway.

## The month view can act, not just read (2026-08-31)

**The month lens is the PHONE lens, and it was the one place you could read the
plan and change nothing about it.** Marking a month entered, or adding a row,
meant switching to a twelve-column spreadsheet to press a button about one of
its columns.

**THE GRID'S BUTTON STRIP WAS DELIBERATELY NOT IMPORTED, and that was the whole
design question.** The first attempt extracted `gridCard`'s bar into a shared
`budgetActionsHtml(y, month)` and drew a trimmed version here. That reasoning
was about not duplicating code and never asked whether a button strip belongs
on this page at all. It does not: the month view is a page of CARDS, the grid's
bar is a spreadsheet's chrome, and eleven of its buttons are about the YEAR —
being offered "Delete 2026" while reading one month is a scope mismatch and a
footgun. **`gridCard` is untouched by this change; nothing is shared.**

Each action sits where the thing it acts on is:

- **`＋ Add an Income Row` / `an Expense Row` / `a Transfer Row`** — an `.addbar`
  at the foot of each section card, carrying `data-sec`. `EDITORS.category.blank`
  was already CALLED as `ed.blank(ds)` and simply never read it; it now opens on
  the section you added from. The section is checked against `SECTION_LABEL`
  rather than trusted — a dataset is markup, and a hand-edited share payload must
  not mint a section that does not exist. The grid's own Add Row passes no
  `data-sec`, which is what keeps its default exactly `expense`.
  **The word is in the LABEL, never a `title`** — this is the phone lens, and a
  title never shows on a phone, so three buttons reading "Add Row" would be
  three identical labels doing three different things. `ADD_ROW_WORD` is written
  out rather than built from `SECTION_LABEL`, whose values are PLURAL and give
  "Add Expenses Row"; a button adds one row.
- **`＋ Add Account`** — the Household tab's own `.addbar` line, verbatim, at the
  foot of the Accounts card.
- **`✓ Mark ⟨month⟩ entered` / `↩ Re-open ⟨month⟩`** — on the month's own STATUS
  LINE, not in a bar. That placement is what makes them unambiguous: the grid
  shows twelve columns, so its button naming one month is fine, but on a page
  about ONE month a button naming another would be the page acting somewhere
  else. Attached to this month's status it can only mean this month, the
  sentence and the button explain each other ("Still to come" → mark it;
  "Entered" → re-open), and there is no rule left to explain.

- **`monthActionsFor(yr, m, started)` is the gating, and it is PURE** because it
  is the one part of this a rendered page cannot easily be asked about. Months
  are entered in ORDER (`markMonthEntered` always takes `enteredThrough + 1`),
  so each action belongs to exactly one month and a month further ahead offers
  neither — not a restriction, the truth. **`reopen` asks
  `enteredThrough === m`, NOT "is this month entered"**, which is true of every
  month at or before the marker; only the last one can go back, which is all
  `reopenMonth` does.
- **NO NEW WIRING, and that is why the ids are the grid's.** `wireBudget`
  already wires `closeMonthBtn`/`reopenMonthBtn` behind `if (btn)` guards and
  already runs for this lens; `data-add` is delegated on `#views`. Both handlers
  key off `activeYearKey()`, which `pickMonth` keeps in step with the month on
  screen.
- **`toEnter`, never `nextM`.** `renderMonthView` already has a `nextM` meaning
  something else — the month AFTER the one on screen, which the due card looks
  ahead into. Two different "next"s in one scope is how they come to be read as
  the same thing; the collision was caught by `node --check`, not by a test.
- **PRINT NEEDED THE TWO IDS NAMED.** On the grid they sit inside
  `.gridactions-wrap`, which the print block already hides; here they are on a
  `<p class="sub">`, so a printed month carried a "Mark Aug 26 entered" button
  until `#closeMonthBtn, #reopenMonthBtn` joined that list.
- **Read-only needed nothing**: `stripEditAffordances` already removes `.addbar`,
  `[data-add]` and both ids. Verified by running it over a clone of the drawn
  page — four affordances before, none after.
- **Accepted limitation:** `sectionCard` returns `''` for a section with no rows
  and no earnings, so a plan with zero transfer rows shows no Transfers card and
  no way to add one *from here*. The grid's general Add Row still covers it, and
  drawing an otherwise-empty card just to hold a button would contradict the
  rule that a section with nothing in it is not drawn.

## Folding a box up

**Every card on every tab collapses to its heading, and the renderers know
nothing about it.** `wireBoxes(view)` walks the freshly drawn markup at the end
of `wireView` and builds the shape: the heading becomes a shaded band carrying a
`.box-toggle` button, everything under it moves into a `.card-body`. That is the
bargain `applyFieldSpans` strikes in the dialogs and for the same reason — an
opt-in flag is the one whoever adds the next card forgets, and "this box doesn't
fold and every other one does" arrives months later.
- **A card with no heading of its own is left alone**, which is what keeps the
  welcome card out of it: its `<h2>` sits inside `.empty`, as every empty
  state's does. Folding "Welcome to Financial Plan" would leave a first-time
  reader looking at a title bar that explains nothing.
- **`.card-body` is listed beside `.card` in every `.card > x` rule.** The wrap
  reparents a card's second `<h2>` and every one of its `.sub` lines, so a rule
  written only against `.card >` silently stops applying to them — which is
  exactly what happened to `.sub` the first time round, on every tab at once. It
  is also the element a tile grid's container query measures, since the wrap
  puts it between the grid and the card — see "The tile rows" above.
- **The set of folded boxes is `state.ui.collapsed`**, beside `ui.tabOrder`, so
  it syncs and follows you to the phone — a deliberate reversal of the old
  `fin-open` localStorage key. The argument for keeping it local was that
  folding a box is not an edit and shouldn't push a new version of your
  finances; that is still true, and it pushes one anyway, because "the boxes I
  never look at stay shut wherever I open this" is worth a debounced write.
  Being in `ui` keeps it out of share links, which send a MINIMAL `ui`
  (`activeYear`, `activeTab`, `tabOrder` — so a shared view opens on the
  sender's first shared tab in the sender's arrangement) with `collapsed`
  deliberately not among them.
- **Stored SHUT, never open.** A card that doesn't exist yet — one added in a
  later version, a year's Notes box appearing the first time a note is written —
  opens by default, and a corrupt list means everything visible rather than
  everything hidden. `cleanBoxKeys`/`isBoxShut`/`withBox` are pure and pinned by
  tests; `coerceShape` runs the list through `cleanBoxKeys`, and they are
  function DECLARATIONS for the temporal-dead-zone reason at the top of this file.
- **`boxKey(view, heading)` strips the DIGITS out of the heading**, so "2026
  Budget" and "2025 Budget" are one box: folding it in one year and finding it
  open in the next is the annoyance that avoids. Same for the count in "Notes
  for 2026 (5)". A renamed heading gets a new key and so re-opens, which is the
  harmless direction to fail.
- **A tab that draws the same heading several times writes `data-box` itself** —
  a donations table per year, a PTO year, a 401(k) check per earner, a portfolio
  pane, a trip. The tie-break for a collision is an ORDINAL, and an ordinal
  moves: fold 2024's donations, add one dated 2026, and a different year is
  folded. It is an OVERRIDE, never an opt-in — a card that says nothing still
  folds, so nothing is forgotten, only occasionally keyed loosely.
- **Two things measure themselves and must be told when a box opens**: a chart
  in a `display:none` card sizes its canvas to nothing, and the grid's pinned
  month header positions off a rectangle that was zero high. `setBoxShut` calls
  `resize()` on the charts inside the card and re-runs `pinGridHeader`, on the
  way open only. For the same reason `wireBoxes` runs LAST in `wireView`, after
  the chart builders — a chart drawn before its box is folded is already the
  right size when the box comes back.
- **The heading's own buttons stay OUTSIDE the toggle** (a trip's ✎ Edit, an
  info dot): a `<button>` inside a `<button>` is invalid and the inner one stops
  being clickable. The toggle does not stretch across the band either, or those
  buttons get shoved out to the far edge of the card instead of sitting beside
  the words where they always have. The whole band is still the hit area — the
  click handler is on the `<h2>` and ignores anything landing on a control.
- **The hover mark is a band shade, a colour and an underline, and the
  underline is not belt-and-braces**: in Dark and Sepia the theme pack's
  `--accent` is essentially `--text-primary`, so the colour change is a no-op
  there. No new colour is invented — `--accent` on `--accent-bg` is the pack's
  own contrast-checked pairing — and open-or-shut is carried by the ANGLE of the
  chevron, never by hue.

The Venmo and large-purchase ledgers are gone entirely, entries
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

## Chart text is on the ramp, and in the app's face (2026-08-30)

**`applyChartTextDefaults()` sets four Chart.js defaults before every
construction: `color`, `borderColor`, `font.family` and `font.size = fsPx('xs')`.**
Sprint Predictability's block, ported the same day the tooltip was themed, so a
chart in one app and a chart in another are the same text beside each other.

Until then every chart here ran at **Chart.js's built-in 12px in Chart.js's
built-in Helvetica** — a size off the pack's ramp entirely, and a typeface the
page is not set in. Chart text is painted onto a canvas, so it inherits nothing:
every size in a Chart.js config is a raw NUMBER OF PIXELS, which is the one thing
the rem ramp exists to stop the page containing. `fsPx(step)` resolves a `--fs-*`
step against the **live** root font size, so a reader who has set their browser's
default to 20px gets 16.25px axis ticks instead of a pinned 12 (measured).

Three things to keep:
- **Set BEFORE the construction.** Chart.js copies the defaults into the chart at
  that moment and never looks at them again, which is why the call sits in
  `newChart` immediately above `new Chart(...)` rather than once at boot.
- **`xs` is the chrome step** — what ticks, legends and tooltips are family-wide.
- **The page zoom is NOT applied here**, and the suite asserts it isn't. `zoom`
  scales the whole document, canvas included, so a 13px label is drawn at 13
  units and comes out at 19.5 on screen at 150% — exactly what happens to the
  body text beside it. Dividing by `zoomScale` would make chart text the one
  thing on the page that refuses to zoom. (Everything else that touches a chart
  in this file DOES need that correction — hit-testing, sizing, the tooltip's
  position — which is what makes this the exception worth writing down.)

## The chart tooltip wears the theme (2026-08-30)

**`chartTooltipTheme()` — six values, and `newChart` merges them into every
chart's `plugins.tooltip`.** Chart.js's own bubble is a hard-coded 80%-black box
with white text: legible on Midnight, and the wrong object on Light and Sepia —
a slab of near-black over a paper-coloured card, the one thing on the page that
did not follow the theme picker. Flow Metrics and Sprint Predictability have
shipped these exact values for a long time; ported here and to the Lottery
Portfolio on 2026-08-30, property by property.

- **`--surface-alt` / `--text-primary` / `--text-secondary` / `--border-strong`,
  `borderWidth: 1`, `padding: 10`.** Sprint Predictability writes
  `--bg-card-alt`, which `theme.css` declares as an alias of `--surface-alt` in
  one place — the same colour under two names, not a divergence. No new colour.
- **MERGED one level deeper than the `Object.assign` above it, and that is the
  whole reason it is not simply another default there.** Nearly every chart in
  this app passes its own `plugins.tooltip` with a `label` callback, and the
  shallow assign would replace the themed object with that one. The order is the
  assertion the suite pins: theme first, the chart's own keys over it, so a
  `caretSize: 8` set beside a wide chart still wins.
- Read at construction like every other `cssVar()` here — a theme change
  re-renders, which rebuilds every chart at the new palette.
- **Colour boxes stay on**, unlike Flow Metrics (whose charts are mostly one
  series): half the tooltips here list several lines at once and the swatch is
  what ties each figure to its line.

The tooltip's REACHABILITY is a separate rule and predates this: a line chart
takes `interaction: { mode: 'index', intersect: false }` so the reader can hover
anywhere in the column, and a bar keeps the default because a bar is its own
target. That rule is this app's, and the family was swept for it the same day.

## One chart, filling the window (2026-08-30)

**Every card that draws a chart carries a ⤢ button that lifts the card into a
fixed overlay filling the window under the header.** Flow Metrics' feature
(2026-08-21), which the starter also carries — if the behaviour changes in one
of the three, mirror it. It is NOT the Fullscreen API and NOT a modal
`<dialog>`: the phrase that shaped it is "with the menu still visible", and both
of those take the header away — `requestFullscreen()` takes the browser's chrome
with it, and a modal dialog is promoted to the top layer, which paints over the
header and makes it inert. `#chartMaxi` is an ordinary fixed div at z-index 15
against the header's 20, starting at `--maxi-top` (the header's MEASURED height)
and outside `.wrap`, which goes `inert` while it is open.

**The card is MOVED, not copied.** Every chart is drawn into a canvas found by
id and a theme or zoom change rebuilds all of them; a second canvas up there
would leave those redraws painting the copy left on the page. A hidden
`.chart-slot` holds the card's seat.

Two things this app has to do that its two siblings do not:
- **`render()` replaces the whole of `#views`,** so the maximised card would be
  orphaned and its placeholder thrown away with the markup round it. `render()`
  calls `maxiSuspend()` as its first line and `maxiResume(id)` at both of its
  exits: the card comes down, the tab is drawn again, and the card carrying the
  same CANVAS ID goes back up. Nothing paints in between, so there is no
  flicker. This is the ordinary path, not an edge case — the ZOOM picker sits in
  the header that deliberately stays live, and changing it re-renders.
- **Cards are rebuilt every render, so their buttons are too.**
  `syncMaxiButtons()` runs at the end of every render and adds what is missing;
  Flow Metrics builds its buttons once at boot because its cards are static
  markup. It also runs from `setBoxShut` — folding is the other thing that
  changes what is drawable, and it does not re-render.

Three more decisions worth keeping:
- **The button lives in the heading BAND**, pushed to the far end with
  `margin-left: auto`, not floating over the card's top-right corner as in the
  siblings: here that corner IS the fold control. The far end is also what keeps
  it clear of the ⓘ, which stays beside the words it explains. A `:has()` rule
  cancels the band's own hover while the button is hovered — the band's hover
  says "this folds the card", which is not what the button does.
- **`.tablewrap` and `.addbar` are hidden in a maximised card.** Four of the
  twelve cards carry a table under their chart; letting forty rows of spending
  push the bars into a strip answers the opposite question to the one asked. The
  `.sub` goes too, but ONLY at ≤640px, where it is a third of the window.
- **`measureMaxiTop()` divides by `zoomScale`.** A rectangle is read in visual
  pixels, which the page zoom has already scaled; `top` is written in layout
  pixels, which it is about to scale again. Same correction as `pinGridHeader`
  and the cell tooltip.

Openable from the console for a test: `maxiCard()`, `openMaxi(card)`,
`closeMaxi()`, `maxiReady(card)`, `chartIn(card)` are all top-level function
declarations, so the suite drives the real thing through the frame's window.

## Read-only share links

Ported from Sprint Velocity, which owns the family pattern — if a share rule
changes there, mirror it here. `#share=<marker>.<base64url>`; marker 1 is
deflate-raw, 0 is plain JSON (older Safari has no `CompressionStream`, and an
uncompressed link can be read by hand when one looks wrong). The payload rides
in the FRAGMENT, which is never sent to a server: no Firestore rules, no
account, no network on either side. `privacy.html` says so and must stay in
step.

**The payload carries its own version, `v: SHARE_PAYLOAD_V`** — a different
thing from `SHARE_FORMAT`, which says how the bytes are packed; this says what
shape is inside them (the SV pattern, mirrored 2026-08-18). `decodeShare`
refuses a HIGHER one, before the shape check (a newer build may well have
changed the shape), with `err.newerVersion` set — and `renderShareError` reads
that mark to say "reload for the current version" instead of telling somebody
their perfectly intact link looks cut in half. Bump the constant whenever the
payload's shape changes in a way an older build would silently misread.

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
- **`settings` travels in FULL, and is the one thing `SECTION_NEEDS` does not
  gate.** Deliberate, decided 2026-08-14, and the opposite of what this file
  used to imply: currency, the rates the projections assume and the subtitle are
  what make the shared figures mean what the sender meant — a recipient reading
  a plan in their own default currency at their own assumed return is reading
  different numbers. **The only credential that must never be shared is the
  Twelve Data price key, and it cannot be**: it lives in localStorage under
  `fin-pricekey` and has never been part of `state`, so it reaches neither a
  link nor a backup nor Firestore. That is the whole reason it is kept there
  rather than in `settings`, and it must stay there — syncing it was weighed
  and turned down on 2026-08-26, and the browser's password manager carries it
  between devices instead (see the price-lookup section). The zoom is out for the
  same reason in a smaller key: it describes a screen, not a plan.
  **`state.quotes` is the case that shows why the whitelist matters**: the price
  cache IS state — it syncs and rides in a backup on purpose — but it is a list
  of the tickers somebody holds, so it must never reach a link. It is kept out
  by being a top-level key `buildSharePayload` does not name, which is why that
  object is assembled from a whitelist rather than by copying `state` and
  deleting from it.
  **So anything added to `settings` is shared by default — if it must not be,
  it does not belong in `settings`.** That is why the drawdown's spending target
  is `side.drawdown` and not a setting: it is data about a household, gated per
  tab like every other branch. The one trim is `settings.accounts`, emptied when
  no grid is going, since a holdings link has no business carrying the names of
  somebody's bank accounts.
- **`SECTION_NEEDS` is the whole privacy model for state BRANCHES.** It maps
  each tab to the branches it actually reads, and nothing else decides what
  travels. Start reading a new branch in a renderer and it must be added there,
  or the shared copy of that tab shows blanks. `BRANCH_OWNERS` says which tab a branch belongs
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
  restored backup gets — and parses with `safeParse`, not bare JSON.parse: a
  link is the least trusted input the app has, coerceShape mutates in place
  without stripping unknown keys, and a crafted `__proto__` would otherwise
  survive into the Object.assign merges downstream.
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
  a shared view.
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
that calls `cloudPush()`. `privacy.html` must be
updated in the same commit as any change to what sync stores.

**Delete-all goes through `save()` + `window.cloudFlush`, NOT a document
deletion — `window.cloudWipe` is gone and must not come back.** It called
`deleteDoc()`, forgot `fin-sync-uid` and signed you out, and the sign-out was
load-bearing: staying signed in would have re-created the document on the next
save a second later. What it never did was tell the OTHER devices. The phone
kept every year, goal and balance, and its next edit re-created the document
from its own copy — so signing back in on the laptop poured the whole plan
back, which is the opposite of what the button says. Pushing an emptied plan
instead lands on the listener's "another device has cleared its data — clear
this one too?" branch, which already existed here and was simply unused by the
wipe path. The surviving document is `{ json: "<blankState>", updatedAt }` —
no name, no month, no figure — so deleting it outright bought appearance rather
than privacy. Same behaviour as Sprint Predictability, Flow Metrics, PAPTrack
and Golf Handicap. (Charlie asked for this on 2026-08-14; the sign-out was the
complaint, the silent phone was the real fault.)

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
**tests.html busts its own cache, on the frame AND on the source fetches
(2026-08-22), and that is not tidiness.** `const BUST = '?t=' + Date.now()` goes
on the hidden `iframe.src` and through `bustFetch()` on every read of a file this
repo serves — `index.html`, `sw.js`, `privacy.html`, `package.json`,
`chart.min.js` and the two gitignored JSONs. The frame cache and the HTTP cache
are different caches and they can disagree: in the lottery repo the same harness
reported **all-green against a page three features out of date**, because the
source-level tests were reading the file off the server while the frame ran a
copy the browser had cached. Nothing errored; the new code was simply never run.
A suite that can pass against a build which exists nowhere is worse than no
suite — it turns "untested" into "verified". **If a test passes when you expected
it to fail, check `document.getElementById('app').contentWindow` has the function
you just wrote before believing anything.** `api.github.com` is deliberately left
un-busted: somebody else's endpoint, not a file we serve.
**A test must never depend on the app's AMBIENT state.** The harness frames the
real `index.html`, so the app inside it loads whatever is in that browser's
`fin-state` — and while testing a feature by hand that is routinely Charlie's
real plan. A test that calls a function reading the global `state` therefore
passes locally and fails in CI on a blank one. It happened with
`shareCarriesNote` (which skips branches with nothing in them): green here, red
in CI, and the local green was the WRONG answer. Build the state a test needs
and pass it in; where a function reads the global, assert over the pure tables
behind it instead. Real data loaded into the harness is not a fixture.
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

## Installing it as an app

`manifest.webmanifest` + the PNG install icons + `manifest-src 'self'` in the
CSP. That is the whole feature; it adds no runtime code beyond one line in
`applyTheme`.

- **`scope` is `"./"`, and it is the security-relevant line.** All the family's
  apps share ONE origin, so a scope of `/` would capture Sprint Velocity and
  Flow Metrics into this app's installed window. Relative also keeps it correct
  on the local server, where the app is at the root rather than under
  `/financial-plan/` — an absolute scope would simply be invalid there and the
  browser would fall back, which is a bug you cannot see locally. `id` is
  absolute (`/financial-plan/`) because an id resolves against the ORIGIN, not
  the manifest's directory: `"./"` there would resolve to `/` and collide with
  every sibling app.
- **No `file_handlers`, `protocol_handlers` or `share_target`.** They deliver
  outside data into a page on an origin holding work figures. Nothing needs them.
- **There IS a service worker now (`sw.js`), and this app is the only one in the
  family with one.** It was refused for a long time, and the three objections on
  record were right to be made — what changed is that two of them turned out to
  be answerable by design rather than by abstention. Recorded in full because
  the next person to touch this needs the reasoning, not just the outcome:
  - *"A resident process on the shared origin."* Bounded, in the end. A worker's
    scope cannot exceed its own directory without the `Service-Worker-Allowed`
    header, and GitHub Pages cannot send headers — so this one structurally
    cannot see Sprint Velocity or Flow Metrics traffic. Locally, where the app
    is served from the root, it does control `tests.html`; the allowlist is what
    makes that harmless, not the scope.
  - *"Caches are ORIGIN-wide, not per app."* True, and it does not go away — any
    page on the origin can read this cache, and a future SV/TD worker could too.
    The answer is the rule in `sw.js`: **only files that are already public in
    this repo are ever cached.** Nothing in there is anything an attacker could
    not read straight off GitHub. The plan stays in localStorage, which every
    page on the origin could already reach, so the threat model does not move.
    It cuts the other way too — `activate` must only ever delete caches with
    this app's `fin-shell-` prefix, or it would wipe a sibling's.
  - *"A caching bug serves stale code to an app whose data schema moves."* Still
    the real risk, and the one the design is built around. **The worker is
    network-first for everything**: the cache is a fallback for a network that
    actually failed, never a first choice. You can only be served cached code
    on a visit where the network did not answer. The braces to that belt is
    `haltForNewerData` in index.html — if a plan turns out to carry a NEWER
    schema than the running build knows, the app refuses to open it rather than
    letting `migrate` (whose gates are all `<`) wave it through to be rendered
    by code that predates its fields.
- **The page's CSP does not apply to the worker.** A worker takes its policy
  from the HTTP response headers of its own script, and Pages cannot set
  headers, so `sw.js` runs with **no CSP at all**, permanently installed. That
  is why it is tiny, has no `eval`/`importScripts`/dynamic import, and never
  touches a cross-origin URL — and why the CSP now spells out `worker-src
  'self'` instead of letting it resolve through the `worker-src → child-src →
  script-src` fallback chain (which reaches `'self'` anyway, but only by
  accident of ordering, and would otherwise inherit script-src's gstatic and
  accounts.google.com hosts).
- **`sw-kill.js` is the escape hatch, and it exists BEFORE it is needed.** A bad
  page is fixed by pushing a new one; a bad worker is resident and can keep
  serving itself. `cp sw-kill.js sw.js`, commit, push — every installed copy
  then clears this app's caches, unregisters itself and reloads its windows, and
  the app is back to being the ordinary online-only page it was before.
- **Two traps found while building it, both of which fail silently:**
  `cache.addAll` is all-or-nothing (one 404 rejects the whole precache, install
  fails, and there is no offline at all while the app looks perfectly healthy
  online); and **`install` fires once per script version**, so if the cache is
  later evicted nothing rebuilds it and offline quietly decays to "whatever the
  last online visit happened to request". Hence `topUp()`, which fetches
  entries individually and is pinged by the page on every load via a
  `shell-check` message — the repair has to be able to run without a new worker
  version to hang it on.
- Registration is guarded three ways, all load-bearing: **not in a frame** (or a
  `tests.html` run would install a worker and then start testing whatever that
  worker had cached), **not in a shared view** (a borrowed read of a plan should
  leave nothing resident in a stranger's browser), and **on `load`**.
- **Testing it locally will mislead you.** The browser holds its own copy of
  `sw.js` and a byte-identical script fires no `install`, so edits appear to do
  nothing and an emptied cache appears not to refill. `await reg.update()`
  before judging any of it — this cost an hour, and the symptom looks exactly
  like a broken worker.
- **Installing is a window, not a sandbox.** Chrome's installed app shares the
  browser's profile storage — it reads `sv-state` and `td-state` exactly like
  any tab on the origin already can. Don't describe it as isolation anywhere.
  **Safari's Add to Dock is the exception and the trap**: a macOS web app gets
  its own storage container, shares no localStorage with Safari, and so opens
  EMPTY — sync is how a plan gets into it. Say so wherever it's documented; it
  reads as data loss otherwise.
- `<meta name="theme-color">` is rewritten by `applyTheme()` from the pack's
  `--bg`, so an installed window's title bar follows the theme instead of
  sitting at midnight above a Light page. Read back from the token, never
  listed here — no new colour, and a pack palette change carries automatically.
- `make_favicon.py` draws every icon from the one set of coordinates, at
  `k=1.0` for the ordinary ones and `MASKABLE_SCALE` for the maskable. The
  maskable is drawn by SCALING THE GEOMETRY, not by pasting the finished tile
  smaller: the first version pasted, and the glow disc — which is drawn to bleed
  off the bottom-left corner — came back with the pasted tile's straight edges
  cut through it. Its `favicon.ico` output is byte-identical to before that
  refactor, which is the check to re-run if the drawing code is ever touched.

## Working rules

- Browser-test locally first (`.claude/launch.json` → port 8016, or
  `python3 -m http.server 8016`), then commit, push, verify the Pages deploy.
- **The boot script carries a frame-buster** (top of `<head>`): GitHub Pages
  cannot send `frame-ancestors` (meta CSP ignores it), so a hostile origin
  could otherwise iframe the app and redress the reader's own figures. The
  ONE legitimate framer is tests.html — same-origin, identified by
  `data-fin-tests` on the frame element; a cross-origin framer reads as
  `frameElement === null` and gets navigated over (or, if sandboxed against
  that, the page hides itself). Don't add frames without teaching this check.
- Commit subjects are plain English for a reader, not a diff. The Recent
  changes box that listed them verbatim was removed 2026-08-18, across the
  whole app family, and the GitHub API went out of the CSP with it.
- CSP `connect-src`: `'self'`, the Firebase/Google sign-in hosts and
  `https://api.twelvedata.com` (holding prices — ticker only). A new feature that talks to a new endpoint must add it to the CSP in
  the same commit, and update `privacy.html` if it changes what leaves the
  browser. **Every page in this repo ships its own CSP meta tag** — index.html,
  privacy.html AND tests.html (which GitHub Pages publishes beside the app, so
  it is as much a page on the shared origin as the app is). A new page starts
  with one; the harness iframe's content is governed by index.html's own CSP,
  not the parent page's. The price-lookup key lives in localStorage `fin-pricekey`, NOT in
  state: state syncs to Firestore and rides along in every backup file, and a
  credential belongs in neither.
- Keep README.md current whenever the app meaningfully changes.
- Help/info icons never sit flush against the word they follow (standing
  preference).
- **`package.json` is a Dependabot manifest, not a build step.** It installs nothing, declares nothing but the vendored `chart.min.js`, is `private: true` with no scripts, and CI passes `--omit=dev` so npm never downloads it. **Dependabot cannot re-vendor a file**, so a version-bump PR would raise the manifest while the app kept serving the old bytes — `tests.html` pins the manifest's pin to the version string inside the bundle, which makes a manifest-only bump fail and turns the PR into the right instruction: update the file too, in all four repos that carry it (lottery, team-dashboard, financial-plan, sprint-velocity). Never add a `scripts` block, and never let the pin become a `^` range — a range cannot be checked against a file.

## The Nine Gaps (2026-08-22)

Nine things the app could not do, built in one pass. Each one is written up
where it lives; what follows is the reasoning a later reader would otherwise
have to re-derive, and the traps that are already paid for.

- **`side.liabilities` is the big one, and schema 7 is its migration.** A debt
  was `property.owed` — one number, retyped by hand or left to rot, while every
  other figure in the file computes itself; and a loan not secured on a house or
  a car had nowhere to live at all. `drawdownYears` even says so in a comment:
  *"a debt the app has no way to model and no business inventing."*
  - **The split is the load-bearing decision.** A debt `securedOn` a property
    comes off that property's EQUITY (which is what `owed` did, so a migrated
    plan's net worth is unchanged to the cent); anything else is its own tile.
    **The total is the same figure either way**, which is what makes a dangling
    `securedOn` safe to degrade to unsecured rather than an error to handle.
    There is a test pinning exactly that.
  - **`netWorthParts` takes a MONTH now.** `liabilityAt(l, month)` walks the
    schedule forward from `asOf`, so what net worth counts is what is owed
    today rather than what was stated in December. `netWorthTotals` already had
    `cur` to hand and passes it down; the parameter is optional so nothing else
    had to change.
  - **`amortize` returns three shapes, not one.** `null` = not enough said
    (no payment); `{never: true}` = the payment does not cover the first
    month's interest, which is REAL and must be said in words rather than drawn
    as a line climbing away; otherwise the schedule. Interest-LEFT re-walks from
    the current balance — reading `a.interest` printed a mortgage's whole
    lifetime cost under a column headed "left", which was the first thing this
    got wrong on screen.
  - **`p.owed` is still coerced and still counted.** A backup from before
    schema 7 is coerced BEFORE it is migrated, and `netWorthParts` runs over
    both states. Don't tidy it away.
  - Property rows have IDS now (`mintIds` in coerceShape — mints only where one
    is absent, never moves a well-formed one, and numbers collisions, because
    two cars called "Car" is exactly the ambiguity `securedOn` cannot survive).
    `uniqueId(list, name, fallback)` beside `slugJs` replaces the five hand-
    written copies of that loop.

- **`grow` is `carry` with a clock.** Steps up once per CALENDAR YEAR, never
  monthly: a 3%/yr rent compounding monthly grows by cents every month, which is
  not a thing a landlord does, and a year built ahead would read twelve figures
  where the reader typed one. Inside a year the exponent is 0 and it IS carry,
  which is what lets a typed month take over mid-year. Its rate is `cat.growth`,
  its OWN key rather than sharing `rate` with the dividends rule — a row moved
  between the two would otherwise carry the other's figure into an answer that
  looked typed.

- **`spendingMix` is the card the data had always been able to feed.** Eleven
  years of per-category monthly figures and one bar a year drawn off them.
  `categorySpend` copies `yearSpending`'s reading rules exactly (computed cells,
  netted, summary years off `categoryTotals`) so the parts always add to the
  total — there is a test asserting that. Matching between years is by row ID
  where both are grids and by NAME where either is a summary; the choice is made
  ONCE for the whole table, because a mixed answer would match half of it.
  `prevDetailed` is the distinction that matters: a summary year with no rows is
  "nothing to compare", not "every row is new", and those are claims about
  different things.
  - **The sample's history years were three dead scalars** (`income`,
    `spending`, `saved`) that nothing in the app has ever read, so every
    long-run chart drew them at $0.00. They are real `categoryTotals` now. That
    was a live defect in the demo, not scope creep for this card.

- **Comp grew `equity` and `match`, and they reach `grossIncome`.** That figure
  is the DENOMINATOR of every giving percentage, which is why both are absent
  rather than 0 and read with `rateOrNone` rather than `num` — `num('junk')` is
  0, and a 0 here is the claim "nothing vested". There is a test that a plan
  without them is unchanged to the cent.

- **`taxNowCard` is the nearest question, finally asked.** The tab had brackets
  and used them only for a withdrawal forty years out. It reads the newest year
  with a comp record rather than the calendar year (a raise letter arrives when
  it arrives) and says in the card what it is NOT — no credits, no itemising, no
  payroll tax, nothing withheld. Say that or a number under a heading with the
  word Tax on it gets read as an answer.

- **The print block declares NO COLOUR, and there is a test that fails if one
  ever appears in it.** The palettes belong to the theme pack; a print palette
  here would be a fifth theme with no contrast gate over it. Printing borrows
  the pack's own `light` theme in JS (`printUsesLightTheme`, on `beforeprint` /
  `afterprint` AND `matchMedia('print')` for Safari) and gives it back. Nothing
  is saved, and the restore reads `themeId()` rather than a remembered value so
  two restores agree. Charts are deliberately NOT rebuilt — a `render()` inside
  a print handler can land after the page is snapshotted, and would leave the
  screen mid-rebuild on a cancelled print.
  - **A `@media print` block probably belongs in the PACK**, so the other four
    apps get one. Flagged rather than done: it is a family-wide change.

- **CSV comes back in.** `csvRows` is a real parser (quotes, doubled quotes,
  CRLF, and it strips the BOM the export itself writes). `readGridCsv` refuses
  WHOLE and names what is wrong — the tax-paste rule.
  - **THE "ROW OF WORDS" GUARD TRACKS TWO FLAGS, and cannot be written as a
    test over `values` (2026-09-02).** It asks whether every month of a row held
    words rather than a figure, and `values` cannot answer: `parseMoney` returns
    a number or NULL, and null is also what an EMPTY column stores — the two
    states the guard exists to separate arrive spelled the same. It shipped as
    `values[m] !== null && Number.isNaN(values[m])`, which parseMoney can never
    satisfy, so the guard **never fired once**: a line of prose (a header
    repeated mid-export, a column the reader added) reached `applyGridCsv`,
    matched no category, and was ADDED to the budget as a row of its own —
    reported in the confirmation as a row gained rather than one skipped.
    `parsedAny`/`wordsOnly` are set as each cell is read. **`wordsOnly` is the
    half that must not be dropped**: a row of empty columns is a round trip
    CLEARING every month it names, and skipping it would silently refuse a
    deletion. Both halves have a test. It skips the Accounts
  block and the Interest & Dividends line because both are computed, and counts
  them as skipped rather than ignoring them silently. `applyGridCsv` decides the
  cell kind exactly as the cell editor does, which is the point: this is typing,
  done faster. The handler rehearses on a deep copy so the confirmation can
  quote real figures before anything moves.

- **`side.rates` makes `settings.currency` mean something.** It was a symbol in
  front of every figure and nothing else. Property, debts and investment PANES
  can carry `cur`; the budget grid deliberately cannot, because its balances
  chain month to month and an edited rate would rewrite years of history.
  - **Each card reads in its OWN money** (`fmtMoneyIn`), and only totals
    convert. Printing £96,000 as "$96,000.00" was the first version of this and
    it is the exact failure the whole table exists to prevent — the wrong figure
    wearing the right symbol.
  - **An unrated currency is EXCLUDED and named** (`nw.unconverted`), never
    converted at 1:1. A foreign flat added in at whatever number happens to be
    typed is the one answer worse than "I can't count this yet".
  - `side.rates` rides in share links with anything that can be held abroad: it
    is the least personal branch in the file, and without it a shared Progress
    tab shows the sender's flat as something it cannot value.

- **A scenario is a FILE, not a second plan in the state.** `comparePlans` reads
  a backup and writes nothing. A plan-inside-a-plan doubles what syncs, doubles
  what a backup carries, and gives the app two answers to "what am I worth" —
  and the whole file is built on there being one. `planHeadlines` reads every
  figure from the function the owning tab draws, so a comparison cannot quote a
  number the app doesn't show; it takes the date DOWN into `startedGridYears`,
  or a fixture year that hasn't happened yet filters itself out and the whole
  plan reports empty. `COMPARE_ROWS.higher` is `false` for spending and owed and
  `null` for a year — a comparison that drew every increase as good would be
  worse than none. A percentage gap is rounded at 6dp and stated in POINTS;
  `round2` on a rate turned a 10.8-point gap into 11.0.

## The Privacy Page Carries the Family Footer (2026-08-21)

Every public page in this account carries the same three things at the foot: the privacy
policy, the repo under the label **How it works**, and the authorship line. The APP's footer
has had all three for a while. `privacy.html` had **none** of them until now — and it is a
public page reached by a link in that very footer, so anybody who followed it landed on a
document with no way back to the thing it documents and no statement of who wrote it. The
lottery site's privacy page had grown the footer first and was the only one; the other four
were brought into line together rather than one at a time, because a convention held by one
page out of five is not a convention.

- **No privacy link in it**, unlike the app's own footer — you are standing on that page. That
  absence is asserted, not just omitted: the test checks there is no `href="privacy.html"`.
- **The authorship line is the app's own, verbatim.** When this was written the repo had no
  NOTICE, so *independent personal project* was plain text; the NOTICE arrived 2026-08-23
  (the app-ownership pattern) and both footers now use the two-link form — *independent
  personal project* links the NOTICE, *MIT licensed* links the LICENSE, still identical to
  the app's own footer.
- `.foot` and `.foot a` are copied from the lottery page's stylesheet unchanged, so all five
  read identically. Muted, inheriting the link colour — provenance at the foot of a document
  rather than something to click on the way in.
- **Pinned in `tests.html`**, so the next page added to this repo cannot quietly ship without
  it.
- **It is a real `<footer>`, and the policy is in a real `<main>`** (2026-08-21, a day after
  the footer itself). A styled `<p>` is not a landmark, and a page whose only landmark is
  contentinfo is worse than one with none — the actual policy would sit in no landmark at all.
  So both went in together.
  - **`</main>` closes BEFORE the `<footer>`, and that ordering is the whole thing.** A
    `<footer>` nested inside `main`, `article` or `section` is **not** contentinfo — it is a
    plain footer for that section. So `.wrap` stays an ordinary `<div>` rather than becoming
    the `<main>`, which would have swallowed the footer and left the page with no contentinfo
    at all while looking correct in the source. A test asserts the ORDER, not just the tags.
  - The back link stays outside `<main>` — it is navigation, not the document.
  - **The tests strip HTML comments and match the footer by its class**, because the notes
    beside both elements name them in prose and one of those notes lives in the `<style>`
    block, which an HTML-comment strip does not reach. Without both, a page that had lost the
    element and kept the comment explaining it would still pass. That is not hypothetical —
    it is how the first version of this test failed.
  - **The strip is a LOOP, not a single `.replace()`** (2026-08-21, `stripHtmlComments`).
    One pass over a multi-character delimiter can leave a NEW opener behind that the pass has
    already gone past, so a single pass is only as good as the input is well-formed — CodeQL's
    `js/incomplete-multi-character-sanitization` flagged exactly this line, and it was open on
    five of the nine public repos at once. Nothing here renders what it strips, so there was
    no vulnerability; the reason to fix it is that a helper that can be fooled about what is
    commented out is one that can miss a live off-origin script, which is what these suites
    exist to catch. Same helper, same wording, in every sibling repo's suite.
  - `.foot` sets `margin`, not `margin-top`, so the rule no longer depends on which element
    carries it: a `<p>` brought a UA bottom margin with it and a `<footer>` does not.

- **`<main>` opens ABOVE the tab strip (2026-08-21), not around the panel alone.** Two things
  were wrong with the old placement: the tabs were in no landmark (axe-core's `region` rule),
  and the skip link jumped straight past them — a keyboard user who took "Skip to content"
  had the whole tab row behind them and could only reach it by shift-tabbing back. The tabs
  and the panel they drive are one widget, so the landmark goes round both, and `#shareBar`
  comes inside with them because it describes what is on screen. `role="tabpanel"` still goes
  on the inner div and NEVER on `<main>`: putting a role on an element is its role, and it
  would silently replace the landmark. Every page here now passes axe-core at WCAG 2.1 A/AA
  plus best-practice, in all four themes, with data loaded, on every tab and with every
  header dialog open.

- **The privacy page's back link lives in a `<nav>` (2026-08-21).** It stays OUTSIDE `<main>`
  — it is navigation, not the document — but "outside main" is not the same as "outside every
  landmark", which is where it sat: axe-core's `region` rule found it on all six privacy pages
  at once. The `<nav>` carries an `aria-label` naming where it goes back to.
- **The base field rule's TYPE LIST is the theme pack's own** (2026-08-22). `select,
  textarea, input[type=text|number|date|month|search|tel|url|email|password]` — the same
  list the pack enumerates in its coarse-pointer rule. It has to stay a whitelist (a
  checkbox handed a surface, a border and padding stops being a checkbox), but a whitelist
  grown by hand is a field that arrives silently UNSTYLED, wearing the browser's own box
  beside fields wearing the theme's. Nothing fails and nothing logs. It has happened twice
  in this family in opposite directions: Flow Metrics was missing `date`, Golf Handicap was
  missing `search`. Borrowing the pack's list is what stops it being a fresh discovery each
  time, since it answers the same question ("is this a thing you type into?") in the one
  place that should. **Adding a type to one means adding it to the other.**
  `input[type=search]` also takes `appearance: none`, like the pack's date fields, because
  the native inset shape ignores the border and radius — that removes Chromium's native ×
  too, so a search box with no other way to clear itself should offer one.
  **Sprint Predictability is the design lead**; Flow Metrics, Money Map and Golf Handicap
  carry the identical list. PAPTrack and the dashboard style fields by CONTAINER
  (`.field input`) and by class (`.ctl`) instead — element selectors, which have no
  equivalent gap — and the lottery pages style their few fields per component. Those three
  are deliberately NOT converted; don't "finish the job" by giving them a type list.
- **Decorative glyphs on buttons are `aria-hidden` everywhere, not just in the header.** The
  header row got the treatment on 2026-08-21 and the rest of the app did not, so a screen
  reader still read "downwards black arrow, Export JSON" in every dialog. Around 50 buttons
  across the family were wrapped in the same pass. The sync button is the exception that
  proves it: its label is rewritten with `textContent` as the state changes, so a span there
  would be blown away — it carries an `aria-label`, re-stated in every branch of `updateUI()`
  so it can never be left describing the previous state.

- **Google's code is fetched when it is asked for, not on every visit (2026-08-22).** `init()`
  used to run unconditionally, so Firebase and the sign-in client were downloaded before
  anyone had touched anything — which is what made the privacy page's wording false. The boot
  branch now asks `shouldBootSync()`, which reads `fin-sync-live`: `'1'` load now, `'0'`
  load nothing, absent → fall back to the legacy `fin-sync-uid` marker (the migration, worth
  at most ONE eager load per browser). `onAuthStateChanged` writes the flag on EVERY report,
  including the null one after signing out — that is what makes signing out stop the requests
  rather than just the syncing.
  - **The warming is load-bearing.** `requestAccessToken()` must be called inside the click
    handler or the popup is blocked, and awaiting a cold import would spend the gesture — so
    the load starts on `pointerenter` / `pointerdown` / `focus`, which all fire before click.
    `onClick` still awaits `ensureInit()` for a keyboard user who never hovers.
  - **The click listener is wired at the boot branch, not at the end of `init()`** — `init()`
    may not have run, and the button has to be pressable in order to be what runs it.
  - `ensureInit()` is idempotent, or a hover and a click start two Firebase apps.
- **Firebase is pinned in `package.json` AND in the `firebasejs/…` URL, and a test holds them
  equal.** Dependabot cannot rewrite a URL, so a manifest-only bump has to fail. All three sync
  apps move to the same version together, like the vendored Chart.js.
- **The header strapline is prefilled with "Charlie's Epic Money Map" (2026-08-22) and is
  still a Preference.** This was the only app in the family without one, because its subtitle
  is reader-settable and the default was empty. `DEFAULT_TAGLINE` beside `SCHEMA` is the one
  source; the markup carries a third copy so the header is at its final width at first paint,
  and it has to be kept in step. **Clearing the field sticks** — `''` is a string and survives
  `coerceShape`, where an absent key falls back to the default. Filling an existing plan is
  **schema 6**, a one-shot in `migrate()` and deliberately NOT a `coerceShape` default: a fill
  that ran on every load could never be cleared. It only ever fills an EMPTY one — a subtitle
  somebody typed is theirs. It travels in a share link like everything else in
  `state.settings`, which is existing deliberate behaviour, not something this changed.

## Six Fixes From the 2026-09-01 Audit

A bug audit of the three work apps on 2026-09-01 (three auditors, each finding
reproduced headless before it was reported) found six here that the suite did not
cover. Each has a test now, proven to fail first by reverting the fix.

- **The four look-back rules ask `isFigure(cell)`, never `if (cell)` (fix 1).** A note-only cell is STORED as `{ v: 0, kind: 'missing', note }` (the 2026-08-26 rule),
  and `carry`, `grow`, `quarterly` and `avg` asked `if (cell)` of `yr.cells` — so a note on a
  blank March was a real $0: April's `carry` went to $0.00 "auto", `grow` rent to $0, the
  `avg` card figure dropped by a third, the `quarterly` bill re-phased onto March and paid
  nothing in June, and December's cash balance moved by thousands, invisibly (kind still said
  auto estimate). `priorYearLast`/`priorYearRun` had it right; `isFigure(cell)` names their
  rule and every rule reading `yr.cells` for a figure goes through it. The question for any
  new rule: does it read `yr.cells`? Then it asks `isFigure`.

- **The overflow sweep asks `isFigure` too (fix 2).** The sweep step's `if (yr.cells[key])` took the stored branch on a note-only cell — moved
  `-resolved.v` = $0 and `continue`d past the estimate — so "remember to do this" written on
  January's sweep cancelled the $4,000 move and every later month inherited the error. Same
  fix as the rules: `isFigure(yr.cells[key])`.

- **The `dividends` rule falls back to `ctx.prior.balances` (fix 3).** `ctx.balances` holds the current year only, so January's `prev` (December) always missed,
  even when `prior.balances` had it — the balance chain itself reads `prior.balances` at the
  same boundary. January was `missing` every year: a year built ahead lost 1/12 of its
  dividend income, and the live year's January stayed blank until typed. The first year of a
  plan, with no prior at all, is still honestly blank.

- **Entering a month settles typed estimates too — `enteredCellFor` (fix 4).** `markMonthEntered` minted only `auto` cells to `actual`; a stored `manual` (the amount
  box's default kind on a future month) kept its kind, and `dueStatus` treats only `actual`
  as paid — so a water bill typed ahead read "late, 35 days" for ever, `outstandingDues`
  counted it, and the month page called the total "your estimate". The marker's own comment
  ("everything the marker settles arrives as actual") was false for typed estimates. The
  per-row decision is now `enteredCellFor(cat, stored, resolved, target)` — PURE, exported in
  the hooks, pinned: actual → leave; held row → waiting (a typed estimate on a held row is
  NOT stamped paid); manual/mixed → actual with every part stamped; note-only → the estimate
  with its note; nothing → nothing.

- **`finAdopt` resets `undoCore` through `coreOf` (fix 5).** It built the baseline by hand as `JSON.stringify({...state, ui: null})`, but `coreOf` also
  nulls `quotes`, so the two strings never matched: the first ui-only `save()` after an adopt
  (a tab click) banked a snapshot and showed Undo over a change that changed nothing, and
  pressing it re-applied the same state with "Put back the way it was". One line: `undoCore =
  coreOf(state)`. Pinned as source, like the halt ordering beside it — the live finAdopt
  writes this browser's fin-state.

- **A dropped Firestore listener is re-opened (fix 6).** On listener error the module set `unsub = null` and nothing re-subscribed until the next
  auth change; the next successful `pushNow` then called `clearSyncError()` → "Syncing again"
  while incoming changes were lost until reload. The listener is `listen()` now: re-opened by
  a successful push (`if (!unsub) listen()` after `clearSyncError()`) and by a `RELISTEN_MS`
  (60 s) timer while it is down; sign-out cancels the timer; `listen()` refuses with nobody
  signed in. Module-scoped, so pinned over the source. The same pattern exists in Golf
  Handicap and PAPTrack and is NOT fixed there — worth a pass if either shows the symptom.

## Fixes From the 2026-09-03 Audit

A bug audit of the three work apps on 2026-09-03 (three auditors, each finding
reproduced headless before it was reported) looked hardest at the code that had
shipped the day before — full-screen stepping, the pinned tab row, the phone tab
row — and found these here. Each has a test now, written first and proven red
against the unfixed page; the commit that fixed it quotes the row.

- **A step by ARROW KEY lands the focus on the new card's ⤢ (fix 1).** `maxiStep` handed the focus back only to a step BUTTON that had held it. Open
  a chart with the ⤢ — which is what holds the focus on opening — and press Right,
  and the element that had it was the old card's ⤢, which the swap had just carried
  back into the inert page: the browser let go, `activeElement` was `<body>`, and the
  next Tab started at the top of a page the reader could not see. After the hand-back
  the function now asks "is the focus a connected element inside `#chartMaxi`?" and if
  not, focuses the new card's `.chart-max` with `{ preventScroll: true }`. The rule in
  one sentence: a step lands focus on the arrow that pressed it, or on the new card's
  ⤢, never on the page underneath. Family-wide; the same shape went into Sprint
  Velocity and Flow Metrics the same day.

- **Printing closes the full-screen window first (fix 2).** `@media print` hides `#chartMaxi`, and the maximised card was INSIDE it — so ⌘P
  over a full-screen chart printed every card but the one the reader was looking at,
  with the page inert behind it. `printForPaper(true)` now calls `closeMaxi()` as its
  first line, ABOVE the Light/Sepia early return (those two skip the theme swap and
  must not skip this) — the line Flow Metrics' `beforePrint()` has always had. The CSS
  comment that said "the card prints where it sits" was wrong and says so now; the
  rule stays as the belt to the closing's braces. Driven through the real
  `beforeprint` event in the suite and read back off the DOM.

- **The phone's tab scroller leaves the focus ring room on every side (fix 3).** At ≤700px `.tabs` is a sideways scroller, and a scroller clips at its padding
  edge: with only `padding-bottom: 4px` the family's 2px ring at 2px offset was sliced
  off along the top, the left of the first tab and the right of the last. Now `padding:
  4px; margin: -4px -4px 0` — the `.yearrail` shape, padding bought back with a negative
  margin so nothing moves. **The bottom margin is 0, not -4px, on purpose**: that 4px was
  already inside the row's height, which `measurePinTops` reads for `--strip-top`, and
  taking it out would have made the pinned band 4px shorter. Measured before and after
  at 375px: row 46px unpinned / 56px pinned, first tab at the row's own top-left, all
  unchanged; only the scroller's own box grew. The test pins the row's height as a RULE
  (tab + 4) rather than as a number, and starts from unpinned and restores the pin it
  found — the pin is a device setting on the harness's origin, and a run that threw
  half-way once left the next run measuring a pinned row.
  **Completed 2026-09-04: the CSS bought the room and `renderTabs`' own nudge spent
  it again.** Picking a tab that sits off an end scrolls the row, and that arithmetic
  measured against the scroller's BORDER edge — so it landed the tab flush and took
  back exactly the 4px the padding had just paid for: tap the last tab and the ring
  was sliced down its right, come back to the first and down its left. The nudge now
  measures against the PADDING edge, reading the figure off `getComputedStyle` so the
  two can never drift. The test passed throughout because it only ever measured the
  row AT REST, which is not the state a reader is in; it now taps the last tab and
  the first and measures after each.
  Two things in that test were also environment-blind, and both read as a false red
  on a Mac while CI stayed green: the 4px checks were exact, where scrolling to an
  end lands a fraction short (3.984375px here — `scrollWidth`/`clientWidth` are
  integers over fractional content), and the row-height rule assumed an overlay
  scrollbar, where `.tabs` asks for `scrollbar-width: thin` on purpose and a machine
  drawing classic scrollbars puts ~11px under the row. The checks now allow the
  sub-pixel and measure the scrollbar rather than assuming it. **A local red that CI
  calls green is worth reading before it is dismissed** — under these two there was a
  real bug.

- **The ⓘ dots answer on a maximised card (fix 4).** Every info dot is answered by one delegated listener on `#views` (the row editor's
  dialog has its own), and `attachMaxi()` MOVES the card into `#chartMaxi`, outside both —
  so on five cards (Net Worth's band dot and its as-of row dot, Where the Money Goes, Where
  the Pot Is Heading, Giving over Time, Raises over Time) the dot did nothing while the
  chart filled the window, though the Escape handler's own comment assumed it did.
  `#chartMaxi` carries the same three-line handler now — read the dot, `stopPropagation`
  (the band's click folds the card), `openHelp` — a third copy on the root of a subtree
  the other two cannot reach. The same dot opens the same window from any of them, so one
  dot still has one explanation. The test presses the dot through `elementFromPoint` and
  shows the Escape handler yielding while the dialog is open; the dialog's own cancel is
  the browser's, exercised by a real key in `mm-verify-f4-helpdot.mjs` rather than by a
  synthetic one that cannot drive it.

- **`$ (1,234.56)` is the accounting form too (fix 5).** `parseMoney`'s bracket test wanted the brackets to wrap the WHOLE string, and Excel's
  Accounting format — and most statement exports — put the currency symbol OUTSIDE them,
  so `$ (1,234.56)` and `$(1,234.56)` arrived POSITIVE, in a typed box and through
  `readGridCsv` alike: the right number pointing the wrong way. `BRACKETED` now admits a
  run of currency symbols (`\p{Sc}`) and whitespace before the opening bracket and nothing
  else — `a(500)b` is still not the form, and the dash boundary above `MINUS_FORMS`
  (en/em dash are punctuation, "Rent — $500" is +500) is untouched. **A trailing minus
  (`500-`) and a `CR` suffix are deliberately NOT read** — they were the audit's
  unconfirmed items, and each is a spelling with its own false positives to think
  about first.

### Round two, 2026-09-04

The audit's leftovers Charles chose to fix the next day — the same routine, a
test first and proven red, the commit quoting the row.

- **A drift with no prices behind it says "no prices", not "on target" (round two, 1).** The Drift column is `value − target × total`, and with no price on any
  holding both are 0 — so the move was 0 and the cell read "on target", a claim with
  nothing behind it (the 2026-09-02 rule: a figure the app cannot know says so where it
  is read). The Furthest From Target chart's tooltip and spoken text are the second
  reader of the same fact and said the same. Now `allHoldings` marks each rollup row
  `priced` (any holding in it with a price above 0), `classRollup` carries the flag up
  to a class when its rows carry it, and one `driftMove(r, total)` answers NULL for a
  total of 0 or an unpriced row — the column and the chart both read it, where before
  each did the subtraction itself. Null rather than 0 on purpose: every reader has to
  say "no prices" instead of rounding it into a number. The cell is muted (an absence,
  not a figure); a null bar draws nothing and sorts last. **An unpriced holding among
  priced ones is covered too** — its move used to be the whole of its target, read as
  "under". Fixture rows that never carried `priced` behave exactly as before, which is
  why the flag is read as `=== false` and not as falsy.

- **A percent is stored as the fraction you typed, not the fraction plus float noise (round two, 2).** `readFields` rounded the PERCENT to `dp` and then divided:
  `roundTo(4.57, 2) / 100`, and 4.57 / 100 is 0.045700000000000005 in floating
  point. Nobody saw it — the display branch rounds the fraction back to 4.57 on the
  way in — but that long form was what the state held, what a backup carried, and
  what every figure computed from the rate started with. Now the FRACTION is rounded
  after the division, to `dp + 2` places (two more than the percent asked for, which
  is exactly what the division took): `roundTo(n / 100, (f.dp ?? 2) + 2)`, so 4.57
  stores as 0.0457 and the raise field's six places store as eight. The same shape
  went into the two other places a fraction made from a percent is STORED — a pasted
  tax schedule's rate (`parseBrackets`, a real 5.85% landed as 0.058499999999999996)
  and the comp editor's raise fallback (`raiseFor(...) / 100`). A `/ 100` that only
  feeds a readout (the drawdown editor's safe-rate line, the salary-after preview)
  is left alone: nothing is stored there. Nothing already in a plan is rewritten —
  every reader has always coped with the long form, and the next save of that row
  writes it clean.

- **Closing after a step lands on the chart you were looking at — deliberately (round two, 3).** `closeMaxi` restored `maxiScrollY` and then called `btn.focus()` with no
  `preventScroll`, so with no step the page went back to its place and after a
  step it went back and was then dragged to wherever the NEW card's ⤢ was — the
  right card by accident, its top at 424px in the test that caught it. Charles
  decided on 2026-09-04 that landing on that chart IS what a reader wants, so it
  is now stated: `maxiStep` sets `maxiStepped`, `openMaxi` clears it, and on the
  way out a stepped close re-measures the pin (`measurePinTops`), reads
  `--pin-clear` — the same clearance a Tab landing uses to stay out from under the
  pinned band, header + whatever is stuck + 8 — and scrolls so the card's top sits
  there (`× zoomScale`, because the property is in layout pixels for the zoomed
  root and the rect is visual; the pinGridHeader lesson the other way round).
  `scrollTo({ behavior: 'auto' })` spells the jump out, and the ⤢ is focused with
  `{ preventScroll: true }` like every other focus() the app makes, so nothing
  moves the page after the landing. With no step the return point is exactly where
  the reader left, as before. **The test sets the pin both ways and restores it**:
  the frame shares the origin's localStorage, and the first draft ran "unpinned"
  with the pin on — the ambient-state trap, again.

- **The Find window: Enter opens the first hit, and the keyboard lands somewhere visible (round two, FF — family-wide).** Two faults. The box had only an `input`
  listener, so Enter did nothing; now a `keydown` listener beside it opens
  `searchHits[0]` the way a click does, `preventDefault`ed, and does nothing at all
  when there is no hit (a plain Enter only — a modified one is left to the box).
  And the dialog closing handed the focus to whatever had it before, which after a
  ⌘K from nowhere in particular was <body>, while the hit had just changed the tab
  underneath — so `goToSearchHit`, after `render()`, asks "is the focus on
  something the reader can see?" and if not (body, or an element with no client
  rects) focuses `#tab-<state.ui.activeTab>` with `preventScroll`. A visible focus —
  the Find button after a click on it — is left alone. The landing happens BEFORE
  a cell hit's editor opens, so the editor takes the focus as it always did and has
  a real place to hand it back to. Flow Metrics' 6183b71 is the model; Sprint
  Velocity got the same shape the same day. The test reads hits through the pure
  `searchPlan` — `searchHits` and `F` are top-level bindings the test frame cannot
  reach, which cost the first two runs of the red-row proof.

## Fixes From the 2026-09-04 Evening Audit

Charles asked for a bug check the evening the Vacations chart moved to the top of its tab and the
two card switches dropped under their charts. One fix per commit, a test proven red against the
pre-fix `index.html` first, README and this file in the same commit.

- **A year with money still due can still grow (fix 1).** The chart's key promised that a
  dashed edge meant "its bar can still grow", and only the calendar year and later were dashed —
  a past year with a trip still owing $740 drew solid, and was averaged as FINISHED, pulling the
  dotted line down by a bill nobody had paid. `vacationYearStats` now carries `due` per year and
  `vacationYearRunning(stats, thisYear)` — pure, in the test hooks — says which bars are still
  forming: the current year and after, and any year with money due. The key says "a trip with
  money still due" instead of "trips still being planned". Three checks in "a year with money
  still due can still grow, whatever the calendar says", including the year that settles once the
  calendar passes it with nothing owed.

- **The sample plan has two years of trips (fix 2).** The chart needs two bars to be a trend, it
  became the tab's first card the same day, and the sample had one trip — so the demo's Vacations
  tab opened with its lead card missing, against the rule that sample data reaches every feature.
  A settled trip the year before (fully paid, so it draws solid and gives the average line a
  finished year to stand on) joins this year's still-forming one, so the key's two states are both
  on show; the Sample data group's collection count moves from one trip to two. Left out on
  purpose: the Spending table's "less back" wording (a row netted negative in both years) still
  has no sample row — the sample's cash back is an INCOME row by its own comment's reasoning, and
  a negative expense row would move every pinned sample total for one line of wording.

