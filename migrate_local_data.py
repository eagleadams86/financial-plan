#!/usr/bin/env python3
"""One-off migration for a Money Map backup file — stdlib only, no data inside.

Two things the app deliberately will NOT do to your data on its own, because
both throw information away:

  1. Strip the hand-typed next-year months out of the live grid, so the app
     projects them from each row's rule instead of repeating what the
     spreadsheet happened to contain. Paycheck counts are KEPT: they're a real
     schedule (three-check months and all), not an estimate.

  2. Fold finished years into yearly summaries. A summary keeps one total per
     row — which is all the History charts read — and drops the months.

Reads a backup JSON and writes a new one beside it; the input is never
modified. Restore the output through the app's Back up dialog.

    python3 migrate_local_data.py financial-plan-data.json

Both files are gitignored: real financial data never belongs in this repo.
"""

import json
import sys
from pathlib import Path

# Rules that read a year back. Converting the year they read would blank their
# estimates, so a year with a dependant is left as a grid.
LOOKBACK_RULES = {"samemonth", "avglastyear"}


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


def grid_to_summary(yr, year):
    """Mirror of gridToSummary() in index.html — keep the two in step.

    Flow rows sum across the year. Balance rows keep December's figure: adding
    up twelve monthly balances would be meaningless.
    """
    months = [f"{year}-{m:02d}" for m in range(1, 13)]
    last = months[-1]
    totals = []
    for cat in yr["categories"]:
        row = {"name": cat["name"]}
        if cat.get("isBalance"):
            cell = yr["cells"].get(f"{cat['id']}|{last}")
            row["total"] = round(cell["v"], 2) if cell else 0
            row["isBalance"] = True
        else:
            row["total"] = round(sum(
                yr["cells"].get(f"{cat['id']}|{m}", {}).get("v", 0)
                for m in months), 2)
        if cat.get("note"):
            row["note"] = cat["note"]
        totals.append(row)
    out = {"kind": "summary", "convertedFrom": "grid", "categoryTotals": totals,
           "extraNotes": list(yr.get("extraNotes") or [])}
    if "eoyCash" in yr:
        out["eoyCash"] = yr["eoyCash"]
    return out


def convertible_years(state):
    """Finished grid years that nothing later still reads a year back into."""
    out = []
    for year, yr in sorted(state["years"].items()):
        if yr.get("kind") != "grid" or yr.get("model") != "pinned":
            continue
        nxt = state["years"].get(str(int(year) + 1))
        if nxt and nxt.get("kind") == "grid" and any(
                cat.get("rule") in LOOKBACK_RULES for cat in nxt["categories"]):
            out.append((year, False))   # a later year still needs its months
        else:
            out.append((year, True))
    return out


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

    for year, can in convertible_years(state):
        if can:
            state["years"][year] = grid_to_summary(state["years"][year], year)
            print(f"{year}: converted to a yearly summary")
        else:
            print(f"{year}: left as a grid — the next year has rows that read it")

    dst = src.with_name(src.stem + "-migrated" + src.suffix)
    dst.write_text(json.dumps(state, indent=2))
    print(f"\nWrote {dst}")
    print("Restore it through the app's Back up dialog. Your original is untouched.")


if __name__ == "__main__":
    main(sys.argv)
