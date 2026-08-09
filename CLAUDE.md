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
  `missing` (blank, counts as 0), `pinned` (balance stated outright).
- Estimate rules are table-driven in `RULES`: `carry` (Internet only — the
  sheet types Phone/Parking/Water into each month they apply, so a carry rule
  there would invent charges), `avg` (Credit Card, Venmo — mean of stored
  months before the estimate), `samemonth` (Electric, ROUND, reaches into the
  prior year's grid), `dividends` (rate/12 × prior cash+mid), `paycheck`
  (perCheck × count, incl. fractional counts), `none`.
- Balance chain (live year only): cash += all flows except charitable+zelle;
  mid −= mid transfers; long = (long − transfers) × (1 + 7%/12) + charitable;
  bank −= bank transfers − (−zelle). Overrides pin a month; later months
  chain from the pin.
- "Mark month entered" **materialises** that month's autos into stored
  actuals (the app's overtyping-in-Numbers); re-opening moves the marker back
  and keeps the numbers. Rollover (`rolloverYear`) copies categories+rules,
  keeps overlap manuals, seeds from computed December, and never touches the
  old year.
- Prior years: `model: 'pinned'` grids (2020–2025, every cell an actual, no
  balance model) and `kind: 'summary'` years (2011–2019). The live year is
  always the newest grid.

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
Free-form rows (`side.retirement`/`side.rothLimit`) are loose value arrays;
an empty array is a spacer line, and `fmtLoose()` guesses display format.
Deleting a budget category also deletes its orphaned cells — keep that.

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
— green in CI and on the public site by design. When an engine rule changes,
change the matching test in the same commit, re-run the import, and make the
local cross-check pass again. CI: `.github/workflows/tests.yml` (Playwright
Chromium against `python3 -m http.server 8016`).

## Working rules

- Browser-test locally first (`.claude/launch.json` → port 8016, or
  `python3 -m http.server 8016`), then commit, push, verify the Pages deploy.
- Commit subjects are **user-facing** (the Recent changes box lists them
  verbatim) — plain English for a reader, not a diff.
- CSP: `connect-src 'self' https://api.github.com` only. A new feature that
  talks to a new endpoint must add it to the CSP in the same commit.
- Keep README.md current whenever the app meaningfully changes.
- Help/info icons never sit flush against the word they follow (standing
  preference).
