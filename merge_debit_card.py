#!/usr/bin/env python3
"""One-off edit for a Financial Plan backup file — stdlib only, no data inside.

Makes the ATM row and the Debit Card row into ONE row, in every year.

The same spending has been recorded under three ids over fourteen years —
`atm` (2013–2019, 2024), `debit-card` (2019, 2021–2023, 2026–2027) and
`atm-debit` (2025) — and the last two were both showing under the name "ATM".
Nothing pairs them: "Where the Money Goes" matches this year's rows against
last year's by CATEGORY ID, so 2026's $9 read "new this year" while 2025's
$1,207.53 read "down 100%", two lines apart in the same table.

So every one of them becomes `debit-card`, named **Debit Card** — the accurate
name, since the row holds both card purchases and cash taken out on the card.

2019 is the year that is really a merge rather than a rename: it kept ATM and
Debit Card as separate rows, and four months (Sep–Dec) have a figure in both.
Those become ONE split cell — the app's own way of saying a month was several
payments — so nothing is added up out of sight and every original amount is
still on the screen, in the cell editor, exactly as it was typed.

What is deliberately NOT touched:

* **Every other year's `cash`.** 2020's "Cash" row is the same habit under a
  fourth name and Charlie said to fold it in, so it moves — but ONLY in 2020.
  `cash` is also the checking account's id, and while the two live in different
  namespaces (only `cells` is rewritten here, the same rule `normalizeIds`
  follows in the app), an id that means two things is not one to rewrite across
  the board on a pattern match.
* **Any figure.** A rename moves keys; the merge adds the four overlapping
  months together and asserts the year totals are unchanged.

Reads a backup JSON and writes a new one beside it; the input is never
modified. Restore the output through the app's Back up dialog.

    python3 merge_debit_card.py financial-plan-data.json

Backups hold real financial data and are gitignored: they never belong in this
repo. This script holds none.
"""

import json
import math
import sys
from pathlib import Path

# The whole decision, in one place: what each old id becomes, and what the
# surviving row is called.
MOVES = {"atm": "debit-card", "atm-debit": "debit-card", "cash": "debit-card"}
NAMES = {"debit-card": "Debit Card"}
# A move that is only true in some years. `cash` names the 2020 spending row
# AND the checking account, so it is named here with the year it may move in
# rather than trusted to a bare id match.
ONLY_IN = {"cash": {"2020"}}


def round2(v):
    """`round2` from index.html — Math.round is half-UP, Python's round is not."""
    return math.floor((v + sys.float_info.epsilon) * 100 + 0.5) / 100


def parts_of(cell):
    """A cell as a list of amounts: its own parts, or itself as a single one."""
    if isinstance(cell.get("parts"), list) and cell["parts"]:
        return [dict(p) for p in cell["parts"]]
    p = {"v": cell.get("v", 0), "kind": cell.get("kind", "actual")}
    return [p]


def parts_kind(parts):
    """`partsKind` from index.html: mixed only if the parts disagree."""
    kinds = {"manual" if p.get("kind") == "manual" else "actual" for p in parts}
    return "mixed" if len(kinds) > 1 else (kinds.pop() if kinds else "actual")


def merge_cells(a, b):
    """Two figures in one month become one split cell.

    A `missing` cell is a NOTE WITH NO FIGURE, so it contributes its words and
    no amount — the same thing it means everywhere else in the app.
    """
    notes = [c.get("note") for c in (a, b) if c.get("note")]
    live = [c for c in (a, b) if c.get("kind") != "missing"]
    if not live:
        cell = {"v": 0, "kind": "missing"}
        if notes:
            cell["note"] = "\n".join(notes)
        return cell
    parts = [p for c in live for p in parts_of(c)]
    cell = {"v": round2(sum(p.get("v", 0) for p in parts)),
            "kind": parts_kind(parts),
            "parts": parts}
    if notes:
        cell["note"] = "\n".join(notes)
    return cell


def moves_for(year):
    """The renames that apply to one year — see ONLY_IN."""
    return {old: new for old, new in MOVES.items()
            if old not in ONLY_IN or year in ONLY_IN[old]}


def rewrite_year(yr, year):
    """Rename the ids in one year's rows, merging any two that collide.

    The cell keys are rewritten from the list of ids that MOVED, matched as a
    literal `id + '|'` prefix (longest first) — never by splitting the key,
    which is what a `|` inside an id breaks. Same rule as `remapPrefixed`.
    """
    cats = yr.get("categories")
    if not isinstance(cats, list):
        return 0, 0
    renames = moves_for(year)
    moved = {}
    kept, dropped = [], set()
    by_id = {}
    for c in cats:
        if not isinstance(c, dict):
            continue
        old = c.get("id")
        new = renames.get(old, old)
        if new != old:
            moved[old] = new
            c["id"] = new
        if new in NAMES:
            c["name"] = NAMES[new]
        if new in by_id:
            # The row already in the list keeps its place in the year's order.
            dropped.add(old)
        else:
            by_id[new] = c
            kept.append(c)
    yr["categories"] = kept

    cells = yr.get("cells")
    if not isinstance(cells, dict):
        return len(moved), 0
    merged = 0
    for old in sorted(moved, key=len, reverse=True):
        new = moved[old]
        for key in [k for k in cells if k.startswith(old + "|")]:
            target = new + key[len(old):]
            cell = cells.pop(key)
            if target in cells:
                cells[target] = merge_cells(cells[target], cell)
                merged += 1
            else:
                cells[target] = cell
    return len(moved), merged


def spend(yr, ids):
    """Everything those rows come to in a year, for the before/after check."""
    cells = yr.get("cells") or {}
    total = 0.0
    for k, v in cells.items():
        if k.split("|")[0] in ids and isinstance(v, dict) and v.get("kind") != "missing":
            total += v.get("v", 0) or 0
    return round2(total)


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    src = Path(argv[1])
    state = json.loads(src.read_text())
    years = state.get("years") or {}
    ids = set(MOVES) | set(MOVES.values())

    before = {y: spend(yr, ids) for y, yr in years.items()}
    touched = []
    for y in sorted(years):
        yr = years[y]
        if not isinstance(yr, dict):
            continue
        renamed, merged = rewrite_year(yr, y)
        after = spend(yr, ids)
        # A rename must not move a dollar, and the merge must only add up.
        if abs(after - before[y]) > 0.005:
            raise SystemExit(f"{y}: total changed, {before[y]} -> {after}")
        seen = [c.get("id") for c in yr.get("categories") or []]
        if len(seen) != len(set(seen)):
            raise SystemExit(f"{y}: duplicate row id after the rewrite")
        if renamed or merged:
            touched.append((y, renamed, merged, after))

    out = src.with_name(src.stem + "-debit-card.json")
    out.write_text(json.dumps(state))
    for y, renamed, merged, after in touched:
        print(f"{y}: {renamed} row(s) renamed"
              + (f", {merged} month(s) merged into split cells" if merged else "")
              + f" — row total unchanged at {after:,.2f}")
    print(f"\nWrote {out}\nRestore it through the app's Back Up & Restore dialog.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
