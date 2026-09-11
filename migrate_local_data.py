#!/usr/bin/env python3
"""One-off edit for a Financial Plan backup file — stdlib only, no data inside.

Does one thing, because it is the one thing the app will not do on its own:
take the next year back out of the live grid. The spreadsheet ran 24 months so
it could see a year ahead; the app ends the year at December and starts the
next one with "Start <year>" instead. So the hand-typed next-year months go,
and the grid comes back to twelve.

Paycheck counts for that next year go with the rest of it. They were kept
once, on the reasoning that they're a real schedule and the rollover picks
them up — but the rollover reads them out of a grid that, after this script
runs, is twelve months long and renders none of them. That made them a
schedule nobody could see or correct: rebuilding next year copied them back
in every time, so a wrong count survived the year being deleted (financial-
plan, 2026-09-11). The app's boundary now drops counts a year doesn't show,
and a year built ahead repeats last year's pattern on its own.

It does NOT convert any year to a summary. That is a per-year decision, it is
permanent, and the app has a button for it on the year you actually want it.

Reads a backup JSON and writes a new one beside it; the input is never
modified. Restore the output through the app's Back up dialog.

    python3 migrate_local_data.py financial-plan-data.json

Both files are gitignored: real financial data never belongs in this repo.
"""

import json
import sys
from pathlib import Path

def live_year_key(state):
    """The newest grid year still being filled in."""
    keys = sorted(y for y, yr in state["years"].items()
                  if yr.get("kind") == "grid" and yr.get("model") == "live")
    return keys[-1] if keys else None


def strip_future_months(state):
    """Cut the live grid back to its own twelve months.

    Every stored figure belonging to a later year goes — cells, the typed
    balance overrides/adjustments beside them (statedAfter and the same-name
    merge still read those maps, so an orphan past December is not inert) and
    the paycheck counts, which are keyed by month on their own rather than by
    row — and monthCount comes down to 12, so the grid ends at December.
    Returns (year key, entries removed, previous month count).
    """
    key = live_year_key(state)
    if not key:
        return None, 0, 0
    yr = state["years"][key]
    removed = 0
    for field in ("cells", "overrides", "balAdjust"):
        table = yr.get(field)
        if not isinstance(table, dict):
            continue
        doomed = [k for k in table if k.split("|")[1][:4] > key]
        for k in doomed:
            del table[k]
        removed += len(doomed)
    pay = yr.get("paychecks")
    if isinstance(pay, dict):
        doomed = [m for m in pay if m[:4] > key]
        for m in doomed:
            del pay[m]
        removed += len(doomed)
    was = yr.get("monthCount", 12)
    yr["monthCount"] = 12
    return key, removed, was


def main(argv):
    src = Path(argv[1] if len(argv) > 1 else "financial-plan-data.json")
    if not src.exists():
        sys.exit(f"No such file: {src}")
    state = json.loads(src.read_text())
    if not isinstance(state.get("years"), dict):
        sys.exit(f"{src} doesn't look like a Financial Plan backup (no years object)")

    key, removed, was = strip_future_months(state)
    if key:
        print(f"{key}: removed {removed} stored figure(s) beyond {key} and shortened "
              f"the grid from {was} months to 12")
        print(f"  Next year's paycheck counts went with them. Press \u2295 Start "
              f"{int(key) + 1} and each month repeats the same month of {key} — "
              f"three-check months included.")
        # A row with no rule now has nothing to say about next year. Name those
        # rows rather than leaving them to be noticed as gaps in the grid.
        ruleless = [cat["name"] for cat in state["years"][key]["categories"]
                    if cat.get("rule", "none") == "none" and not cat.get("isBalance")]
        if ruleless:
            print("\n  These rows have no projection rule, so any month you haven't "
                  "typed stays\n  blank for them — including every month of next year "
                  "once you start it.")
            print("  Give each one a rule in the app (row settings) — "
                  '"average of last year"\n  suits spending that wanders:')
            for name in ruleless:
                print(f"    · {name}")

    dst = src.with_name(src.stem + "-migrated" + src.suffix)
    dst.write_text(json.dumps(state, indent=2))
    print(f"\nWrote {dst}")
    print("Restore it through the app's Back up dialog. Your original is untouched.")


if __name__ == "__main__":
    main(sys.argv)
