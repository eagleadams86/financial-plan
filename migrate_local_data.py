#!/usr/bin/env python3
"""One-off edit for a Money Map backup file — stdlib only, no data inside.

Does exactly one thing, because it is the one thing the app will not do on
its own: strip the hand-typed next-year months out of the live grid, so the
app projects them from each row's rule instead of repeating what the
spreadsheet happened to contain. Paycheck counts are KEPT — they're a real
schedule (three-check months and all), not an estimate.

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
    """Delete cells belonging to years after the live year's own.

    The live grid runs long on purpose (Charlie's spans 24 months) so the plan
    can see into next year. Those months were transcribed from the spreadsheet;
    removing them lets the rules do the projecting, which is the whole point of
    the grid. Returns (year key, number of cells removed).
    """
    key = live_year_key(state)
    if not key:
        return None, 0
    yr = state["years"][key]
    doomed = [k for k, cell in yr["cells"].items()
              if k.split("|")[1][:4] > key and cell.get("kind") == "manual"]
    for k in doomed:
        del yr["cells"][k]
    return key, len(doomed)


def main(argv):
    src = Path(argv[1] if len(argv) > 1 else "financial-plan-data.json")
    if not src.exists():
        sys.exit(f"No such file: {src}")
    state = json.loads(src.read_text())
    if not isinstance(state.get("years"), dict):
        sys.exit(f"{src} doesn't look like a Money Map backup (no years object)")

    key, removed = strip_future_months(state)
    if key:
        kept = sum(1 for m in state["years"][key].get("paychecks", {})
                   if m[:4] > key)
        print(f"{key}: removed {removed} hand-typed month(s) beyond {key}; "
              f"kept {kept} paycheck count(s) — the rules project those months now")
        # A row with no rule now has nothing to say about next year. Name those
        # rows rather than leaving them to be noticed as gaps in the grid.
        ruleless = [cat["name"] for cat in state["years"][key]["categories"]
                    if cat.get("rule", "none") == "none" and not cat.get("isBalance")]
        if ruleless:
            print("\n  These rows have no rule, so next year stays blank for them.")
            print("  Give each one a rule in the app (row settings) — "
                  '"average of last year" suits spending that wanders:')
            for name in ruleless:
                print(f"    · {name}")

    dst = src.with_name(src.stem + "-migrated" + src.suffix)
    dst.write_text(json.dumps(state, indent=2))
    print(f"\nWrote {dst}")
    print("Restore it through the app's Back up dialog. Your original is untouched.")


if __name__ == "__main__":
    main(sys.argv)
