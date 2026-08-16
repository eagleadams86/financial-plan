#!/usr/bin/env python3
"""One-time converter: Financial Plan.xlsx (Numbers export) -> Financial Plan JSON.

Reads the spreadsheet with the standard library only (zipfile + ElementTree —
openpyxl is deliberately not required) and writes:

  financial-plan-data.json   the app state; Restore it via the Back up dialog
  expected-2026.json         cached spreadsheet values for every formula cell
                             in the live year, used by tests.html's local-only
                             cross-check of the JS formula engine

BOTH OUTPUT FILES HOLD REAL FINANCIAL DATA AND ARE GITIGNORED. This script
itself contains only cell addresses and row labels — never numbers.

Usage:
  python3 import_xlsx.py "~/Downloads/Financial Plan.xlsx" \
      [--out financial-plan-data.json] [--expected expected-2026.json]

What it understands (matches the workbook as of Aug 2026):
  * Year sheets named "YYYY".
      2020-2026: monthly grids (serial-date header row). The latest year whose
      months reach past today imports as the LIVE year: past months become
      actuals, future formula cells become auto-estimates (dropped — the app
      recomputes them), future typed cells become manual estimates. All other
      grid years import read-only ("pinned"): every cell an actual.
      2011-2019: bi-weekly layouts, imported as yearly summaries.
  * The Vacations sheet: per-trip cost tables + the HOL & PTO table.
  * Side tables located by their title cells on any grid sheet (Savings Goals,
    Taxable Investments, Other Money, Roth IRA Contr, Roth / Traditional, HSA,
    "YYYY Comp", "YYYY Retirement Contributions", "YYYY Roth Limit",
    Fidelity Charitable DaF, "YYYY Donations", "YYYY Venmo",
    "YYYY Large CC Purchases", Bonuses).
  * Cell comments -> notes on the matching cell/row; anything unmatched lands
    in that year's extraNotes so nothing is lost.
  * Pay Scales and Mortgage sheets are intentionally skipped (out of scope).
"""

import argparse
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RNS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
PKG_RNS = '{http://schemas.openxmlformats.org/package/2006/relationships}'

EPOCH = date(1899, 12, 30)   # Excel/Numbers serial-date epoch

warnings = []


def warn(msg):
    warnings.append(msg)
    print(f'  ! {msg}', file=sys.stderr)


# ── Workbook loading ─────────────────────────────────────────────────────────

def col_to_num(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def parse_ref(ref):
    m = re.match(r'([A-Z]+)(\d+)$', ref)
    return int(m.group(2)), col_to_num(m.group(1))


class Sheet:
    def __init__(self, name):
        self.name = name
        self.cells = {}      # (row, col) -> {'v': value, 'f': formula or None}
        self.comments = {}   # (row, col) -> text

    def val(self, r, c):
        cell = self.cells.get((r, c))
        return cell['v'] if cell else None

    def num(self, r, c):
        v = self.val(r, c)
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def text(self, r, c):
        v = self.val(r, c)
        return v.strip() if isinstance(v, str) else None

    def formula(self, r, c):
        cell = self.cells.get((r, c))
        return cell['f'] if cell else None

    def find_title(self, pattern):
        """First cell whose string value matches the regex; (row, col, match)."""
        rx = re.compile(pattern)
        for (r, c) in sorted(self.cells):
            v = self.val(r, c)
            if isinstance(v, str):
                m = rx.match(v.strip())
                if m:
                    return r, c, m
        return None


def load_workbook(path):
    z = zipfile.ZipFile(path)
    strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')):
            strings.append(''.join(t.text or '' for t in si.iter(NS + 't')))

    wb = ET.fromstring(z.read('xl/workbook.xml'))
    wb_rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_target = {rel.get('Id'): rel.get('Target') for rel in wb_rels}

    sheets = {}
    for s in wb.find(NS + 'sheets'):
        name = s.get('name')
        rid = s.get(RNS + 'id')
        target = rel_target[rid]
        if not target.startswith('xl/'):
            target = 'xl/' + target
        sheet = Sheet(name)
        root = ET.fromstring(z.read(target))
        for row in root.iter(NS + 'row'):
            for c in row.iter(NS + 'c'):
                ref = c.get('r')
                t = c.get('t')
                v_el = c.find(NS + 'v')
                f_el = c.find(NS + 'f')
                val = None
                if t == 's' and v_el is not None:
                    val = strings[int(v_el.text)]
                elif t == 'inlineStr':
                    is_el = c.find(NS + 'is')
                    val = ''.join(x.text or '' for x in is_el.iter(NS + 't'))
                elif v_el is not None:
                    val = v_el.text
                fml = f_el.text if (f_el is not None and f_el.text) else None
                if val is None and fml is None:
                    continue
                r, cn = parse_ref(ref)
                sheet.cells[(r, cn)] = {'v': val, 'f': fml}

        # comments arrive via the worksheet's own rels
        rels_path = re.sub(r'worksheets/(sheet\d+\.xml)$',
                           r'worksheets/_rels/\1.rels', target)
        if rels_path in z.namelist():
            for rel in ET.fromstring(z.read(rels_path)):
                if rel.get('Type', '').endswith('/comments'):
                    cpath = 'xl/' + rel.get('Target').replace('../', '')
                    for com in ET.fromstring(z.read(cpath)).iter(NS + 'comment'):
                        txt = ''.join(t.text or '' for t in com.iter(NS + 't'))
                        txt = re.sub(r'^Charlie Adams:\s*', '', txt).strip()
                        if txt:
                            sheet.comments[parse_ref(com.get('ref'))] = txt
        sheets[name] = sheet
    return sheets


# ── Small helpers ────────────────────────────────────────────────────────────

def serial_to_date(serial):
    return EPOCH + timedelta(days=int(float(serial)))


def serial_to_month(serial):
    d = serial_to_date(serial)
    return f'{d.year}-{d.month:02d}'


def serial_to_iso(serial):
    return serial_to_date(serial).isoformat()


def is_serial_date(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return False
    return 36000 <= f <= 60000 and f == int(f)


def slug(name):
    s = re.sub(r'\(.*?\)', '', name).strip().lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s or 'row'


def round2(v):
    # Python's round() is banker's rounding; the app's JS round2 rounds half
    # away from zero, so the two can differ at an exact half-cent (2.675 →
    # 2.67 here, 2.68 there). The tests compare with an epsilon, so this only
    # matters if the output is ever diffed exactly.
    return round(v + 0.0, 2)


CONST_FORMULA = re.compile(r'^[\d\s+\-*/().%]+$')   # arithmetic on literals only


def formula_is_constant(f):
    """True for hand-typed sums like =2937.03+2937.04 — no refs, no functions."""
    return bool(f) and bool(CONST_FORMULA.match(f))


# ── Monthly-grid parsing ─────────────────────────────────────────────────────

def find_month_header(sheet):
    """Row containing >=10 ascending serial dates; returns (row, [(col, 'YYYY-MM')])."""
    by_row = {}
    for (r, c), cell in sheet.cells.items():
        if cell['f'] is None and is_serial_date(cell['v']):
            by_row.setdefault(r, []).append((c, cell['v']))
    for r in sorted(by_row):
        cols = sorted(by_row[r])
        if len(cols) < 10:
            continue
        months = [(c, serial_to_month(v)) for c, v in cols]
        # months must be consecutive
        consecutive = all(
            month_diff(months[i][1], months[i + 1][1]) == 1
            for i in range(len(months) - 1))
        if consecutive:
            return r, months
    return None, None


def month_diff(a, b):
    return (int(b[:4]) - int(a[:4])) * 12 + (int(b[5:7]) - int(a[5:7]))


def label_column(sheet, header_row, first_month_col):
    """The column left of the months that holds the row labels."""
    counts = {}
    for (r, c), cell in sheet.cells.items():
        if r > header_row and c < first_month_col and isinstance(cell['v'], str):
            counts[c] = counts.get(c, 0) + 1
    return max(counts, key=counts.get) if counts else 1


def grid_rows(sheet, header_row, months, label_col):
    """Labeled rows below the header with numeric cells in the month columns."""
    month_cols = {c for c, _ in months}
    totals_col = max(month_cols) + 1
    rows = []
    max_row = max(r for r, _ in sheet.cells)
    for r in range(header_row + 1, max_row + 1):
        name = sheet.text(r, label_col)
        if not name:
            continue
        values = {m: sheet.cells.get((r, c)) for c, m in months
                  if (r, c) in sheet.cells}
        total_cell = sheet.cells.get((r, totals_col))
        if not values and total_cell is None:
            continue
        rows.append({'row': r, 'name': name, 'values': values,
                     'total': total_cell})
    return rows, totals_col


def classify_balance(row_info, months):
    """A flow row's Totals cell sums its months; a balance row's equals the
    last month (or is absent). Self-checking — no per-year hardcoding."""
    vals = {}
    for m, cell in row_info['values'].items():
        try:
            vals[m] = float(cell['v'])
        except (TypeError, ValueError):
            pass
    total = row_info['total']
    if total is None:
        return bool(vals)          # no totals cell at all -> looks like a balance
    try:
        t = float(total['v'])
    except (TypeError, ValueError):
        return False
    s = sum(vals.values())
    if abs(t - s) <= 0.02:
        return False               # verified flow
    last = vals[max(vals)] if vals else None
    if last is not None and abs(t - last) <= 0.02:
        return True                # totals repeats the last value -> balance
    return False                   # unverifiable; treat as flow


# ── Live-year import (the one with rules) ────────────────────────────────────

ROLE_BY_NAME = [
    (re.compile(r'mid-?term transfer', re.I), 'midTransfer'),
    (re.compile(r'long-?term transfer', re.I), 'longTransfer'),
    (re.compile(r'^bank transfer', re.I), 'bankTransfer'),
    (re.compile(r'^zelle$', re.I), 'zelle'),
    (re.compile(r'^charitable$', re.I), 'charitable'),
]

RULE_BY_NAME = [
    (re.compile(r'^dividend', re.I), 'dividends'),
    (re.compile(r'^paycheck$', re.I), 'paycheck'),
    (re.compile(r'^credit card$', re.I), 'avg'),
    (re.compile(r'^venmo$', re.I), 'avg'),
    (re.compile(r'^electric$', re.I), 'samemonth'),
    # Internet is the only bill the sheet carries forward by formula chain;
    # Phone, Parking and Water are typed into every month they apply to —
    # a carry rule would invent charges in the months the sheet leaves blank.
    (re.compile(r'^internet$', re.I), 'carry'),
]

BALANCE_ID_BY_NAME = [
    (re.compile(r'^cash', re.I), 'cash'),
    (re.compile(r'^mid', re.I), 'mid'),
    (re.compile(r'^long', re.I), 'long'),
    (re.compile(r'^bank', re.I), 'bank'),
]


def import_live_year(sheet, year, header_row, months, label_col, today, expected):
    """The current planning grid: categories with estimate rules, sparse cells,
    balance seeds + overrides, paychecks row."""
    this_month = f'{today.year}-{today.month:02d}'
    rows, totals_col = grid_rows(sheet, header_row, months, label_col)

    # The live sheet is laid out in blocks separated by blank rows:
    # categories / balances (+ Total) / paychecks. Split on the row gaps —
    # that's what keeps a category called "Bank transfers" from being taken
    # for the "Banks / Venmo" balance row, which merely shares a prefix.
    blocks = []
    for info in rows:
        if blocks and info['row'] == blocks[-1][-1]['row'] + 1:
            blocks[-1].append(info)
        else:
            blocks.append([info])

    categories, cells = [], {}
    balance_rows, paychecks_row, total_row = [], None, None
    for i, block in enumerate(blocks):
        first_name = block[0]['name']
        if i == 0:
            for info in block:
                categories.append({'row': info['row'], 'name': info['name'],
                                   'info': info})
        elif re.match(r'^paychecks$', first_name, re.I):
            paychecks_row = block[0]
        elif next((bid for rx, bid in BALANCE_ID_BY_NAME
                   if rx.match(first_name)), None):
            for info in block:
                if re.match(r'^total$', info['name'], re.I):
                    total_row = info
                    continue
                bal = next((bid for rx, bid in BALANCE_ID_BY_NAME
                            if rx.match(info['name'])), None)
                if bal:
                    balance_rows.append({'id': bal, 'name': info['name'],
                                         'info': info})
                else:
                    warn(f'{year}: unrecognised balance row "{info["name"]}"')
        else:
            warn(f'{year}: unrecognised block starting "{first_name}" — skipped')

    # roles + rules
    out_cats = []
    paycheck_multipliers = []
    for cat in categories:
        name = cat['name']
        cid = slug(name)
        role = next((role for rx, role in ROLE_BY_NAME if rx.search(name)),
                    'normal')
        rule = next((rule for rx, rule in RULE_BY_NAME if rx.match(name)),
                    'none')
        out_cats.append({'id': cid, 'name': name, 'role': role, 'rule': rule})
        cat['id'] = cid
        cat['rule'] = rule

    # "Entered through" = the last month at or before today whose category
    # cells hold no live formulas — i.e. the last month Charlie fully typed
    # over. The current month usually still has projecting formulas in it
    # (it's mid-month), and those must stay estimates, not freeze as actuals.
    # Carry-rule rows (Internet & friends) chain =prior-cell formulas through
    # every month of the sheet, entered or not, so they can't tell us anything
    # — the signal is a live formula in any OTHER row.
    entered_through = None
    for _, m in months:
        if m > this_month:
            break
        has_live_formula = any(
            cat['info']['values'].get(m, {}).get('f')
            and not formula_is_constant(cat['info']['values'][m]['f'])
            for cat in categories
            if cat['rule'] != 'carry' and m in cat['info']['values'])
        if not has_live_formula:
            entered_through = m
    if entered_through is None:
        entered_through = months[0][1]

    # cells: classify actual / manual / auto per month
    for cat in categories:
        for m, cell in cat['info']['values'].items():
            v = None
            try:
                v = float(cell['v'])
            except (TypeError, ValueError):
                continue
            f = cell['f']
            key = f'{cat["id"]}|{m}'
            if m <= entered_through:
                cells[key] = {'v': round2(v), 'kind': 'actual'}
            elif f is None or formula_is_constant(f):
                # typed into a month that's already begun -> it happened
                kind = 'actual' if m <= this_month else 'manual'
                cells[key] = {'v': round2(v), 'kind': kind}
            else:
                # auto-estimate: the app recomputes it. Cached value goes to
                # the expected file so tests can diff the JS engine against it.
                expected['cells'][key] = {'v': v, 'f': f}
                if cat['rule'] == 'paycheck':
                    mm = re.match(r'^([\d.]+)\*[A-Z]+\d+$', f)
                    if mm:
                        paycheck_multipliers.append((m, float(mm.group(1))))
                elif cat['rule'] == 'none':
                    # a one-off hand-authored formula (e.g. =D7, =ROUNDUP(...)):
                    # freeze its value as a manual estimate so nothing is lost
                    cells[key] = {'v': round2(v), 'kind': 'manual',
                                  'note': f'was ={f}'}
                    del expected['cells'][key]

    # paycheck rule: the most common multiplier is the per-check amount;
    # months using a different one freeze as manual estimates.
    per_check = 0
    if paycheck_multipliers:
        by_amount = {}
        for _, amt in paycheck_multipliers:
            by_amount[amt] = by_amount.get(amt, 0) + 1
        per_check = max(by_amount, key=by_amount.get)
        pc_cat = next(c for c in categories if c['rule'] == 'paycheck')
        for m, amt in paycheck_multipliers:
            if amt != per_check:
                key = f'{pc_cat["id"]}|{m}'
                exp = expected['cells'].pop(key, None)
                if exp:
                    cells[key] = {'v': round2(exp['v']), 'kind': 'manual',
                                  'note': f'was ={exp["f"]}'}
    for c in out_cats:
        if c['rule'] == 'paycheck':
            c['perCheck'] = per_check

    # paychecks-per-month row
    paychecks = {}
    if paychecks_row:
        for m, cell in paychecks_row['values'].items():
            try:
                paychecks[m] = float(cell['v'])
            except (TypeError, ValueError):
                pass

    # balances: typed cells pin (override); formula cells past this_month go to
    # the expected file; seeds recovered from the first month's formula value.
    seeds, overrides = {}, {}
    first_month = months[0][1]
    for b in balance_rows:
        bid = b['id']
        for m, cell in b['info']['values'].items():
            try:
                v = float(cell['v'])
            except (TypeError, ValueError):
                continue
            if cell['f'] is None or formula_is_constant(cell['f']):
                if m <= this_month:
                    overrides[f'{bid}|{m}'] = {'v': round2(v)}
                else:
                    overrides[f'{bid}|{m}'] = {'v': round2(v), 'future': True}
            else:
                expected['balances'][f'{bid}|{m}'] = {'v': v, 'f': cell['f']}
        first = b['info']['values'].get(first_month)
        if first is not None and first['f'] and not formula_is_constant(first['f']):
            # e.g. cash Jan = SUM('2025'!M21, flows...) -> seed = cached - flows
            try:
                cached = float(first['v'])
            except (TypeError, ValueError):
                cached = None
            if cached is not None and bid == 'cash':
                flow = 0.0
                for cat in categories:
                    if next((c for c in out_cats if c['id'] == cat['id']))['role'] \
                            in ('charitable', 'zelle'):
                        continue
                    cellv = cells.get(f'{cat["id"]}|{first_month}')
                    if cellv:
                        flow += cellv['v']
                seeds[bid] = round2(cached - flow)
        seeds.setdefault(bid, 0)

    if total_row:
        for m, cell in total_row['values'].items():
            if cell['f'] and not formula_is_constant(cell['f']):
                try:
                    expected['balances'][f'total|{m}'] = {'v': float(cell['v']),
                                                          'f': cell['f']}
                except (TypeError, ValueError):
                    pass

    # comments onto cells (grid area); the rest onto extraNotes
    extra = []
    row_by_num = {c['row']: c for c in categories}
    col_to_month = {c: m for c, m in months}
    for (r, c), txt in sheet.comments.items():
        cat = row_by_num.get(r)
        m = col_to_month.get(c)
        if cat and m:
            key = f'{cat["id"]}|{m}'
            cells.setdefault(key, {'v': 0, 'kind': 'manual'})
            prev = cells[key].get('note')
            cells[key]['note'] = f'{prev} · {txt}' if prev else txt
        else:
            extra.append({'where': f'{sheet.name}!r{r}c{c}', 'note': txt})

    # the sheet's own account labels (e.g. "Cash (SPAXX)") become the app's
    # display names; whitespace runs collapse
    account_names = {b['id']: re.sub(r'\s+', ' ', b['name']).strip()
                     for b in balance_rows}

    return {
        'kind': 'grid', 'model': 'live',
        'startMonth': first_month, 'monthCount': len(months),
        'enteredThrough': entered_through,
        'categories': out_cats, 'cells': cells, 'paychecks': paychecks,
        'seeds': seeds, 'overrides': overrides,
        'extraNotes': extra,
        'accountNames': account_names,
    }


# ── Pinned grid years (history) ──────────────────────────────────────────────

def import_pinned_year(sheet, year, header_row, months, label_col):
    rows, _ = grid_rows(sheet, header_row, months, label_col)
    categories, cells = [], {}
    seen = {}
    for info in rows:
        name = info['name']
        base = slug(name)
        cid = base if base not in seen else f'{base}-{seen[base] + 1}'
        seen[base] = seen.get(base, 0) + 1
        is_bal = classify_balance(info, months)
        categories.append({'id': cid, 'name': name, 'role': 'normal',
                           'rule': 'none',
                           **({'isBalance': True} if is_bal else {})})
        info['id'] = cid
        for m, cell in info['values'].items():
            try:
                v = float(cell['v'])
            except (TypeError, ValueError):
                continue
            cells[f'{cid}|{m}'] = {'v': round2(v), 'kind': 'actual'}

    extra = []
    row_by_num = {info['row']: info for info in rows}
    col_to_month = {c: m for c, m in months}
    for (r, c), txt in sheet.comments.items():
        info = row_by_num.get(r)
        m = col_to_month.get(c)
        if info and m:
            key = f'{info["id"]}|{m}'
            cells.setdefault(key, {'v': 0, 'kind': 'actual'})
            prev = cells[key].get('note')
            cells[key]['note'] = f'{prev} · {txt}' if prev else txt
        else:
            extra.append({'where': f'{sheet.name}!r{r}c{c}', 'note': txt})

    return {
        'kind': 'grid', 'model': 'pinned',
        'startMonth': months[0][1], 'monthCount': len(months),
        'categories': categories, 'cells': cells, 'paychecks': {},
        'seeds': {}, 'overrides': {}, 'extraNotes': extra,
    }, rows


# ── Summary years (2011-2019 bi-weekly layouts) ──────────────────────────────

def import_summary_year(sheet, year):
    """Label col A; the Totals column is either headed 'Totals' or found as the
    rightmost column whose value sums the row (verified per row)."""
    max_row = max(r for r, _ in sheet.cells)
    max_col = max(c for _, c in sheet.cells)
    totals_col = None
    for r in range(1, min(4, max_row) + 1):
        for c in range(2, max_col + 1):
            if (sheet.text(r, c) or '').strip().lower().startswith('total'):
                totals_col = c
                break
        if totals_col:
            break

    items = []
    for r in range(1, max_row + 1):
        name = sheet.text(r, 1)
        if not name or re.match(r'^(date due|jan 1st half)', name, re.I):
            continue
        nums = {}
        for c in range(2, max_col + 1):
            if c == totals_col:
                continue
            n = sheet.num(r, c)
            if n is not None and sheet.text(r, c) is None:
                nums[c] = n
        total = sheet.num(r, totals_col) if totals_col else None
        if total is None and nums:
            # no totals column: rightmost value that sums the rest, else the sum
            cs = sorted(nums)
            last = nums[cs[-1]]
            rest = sum(nums[c] for c in cs[:-1])
            total = last if abs(last - rest) <= 0.02 else sum(nums.values())
        if total is None:
            continue
        s = sum(nums.values())
        is_bal = not (abs((total or 0) - s) <= 0.02)
        note = sheet.comments.get((r, 1)) or ''
        items.append({'name': name, 'total': round2(total),
                      **({'isBalance': True} if is_bal else {}),
                      **({'note': note} if note else {})})

    extra = []
    for (r, c), txt in sheet.comments.items():
        if c == 1:
            continue
        label = sheet.text(r, 1) or f'r{r}c{c}'
        extra.append({'where': f'{sheet.name}!{label}', 'note': txt})

    return {'kind': 'summary', 'categoryTotals': items, 'extraNotes': extra}


# End-of-year liquidity per year: which rows count, and whether to read the
# December column or the Totals column. Labels only — no numbers live here.
EOY_MAP = {
    '2011': (['Total Cash'], 'total'),
    '2012': (['Total'], 'total'),
    '2013': (['Total'], 'total'),
    '2014': (['All Accounts'], 'total'),
    '2015': (['All Accounts'], 'total'),
    '2016': (['All Accounts'], 'total'),
    '2017': (['All Accounts'], 'total'),
    '2018': (['All Accounts'], 'total'),
    '2019': (['Total'], 'total'),
    '2020': (['Total Cash'], 'dec'),
    '2021': (['Checking Account', 'Savings Account'], 'dec'),
    '2022': (['Checking', 'Savings', 'Bridge'], 'dec'),
    '2023': (['Checking', 'Cash Mgmt'], 'dec'),
    '2024': (['Cash', 'Invested'], 'dec'),
    '2025': (['Total'], 'dec'),
}


def extract_eoy(sheet, year, grid_info=None, grid_rows_list=None):
    spec = EOY_MAP.get(year)
    if not spec:
        return None
    labels, mode = spec
    total = 0.0
    found = 0
    if grid_info:   # monthly grid year: read from parsed rows
        dec = f'{year}-12'
        used = set()
        for label in labels:
            # first match by row order — the balance rows sit at the top of
            # the sheets that duplicate a label lower down (2022, 2023)
            for info in sorted(grid_rows_list, key=lambda i: i['row']):
                if info['name'].strip() == label and info['row'] not in used:
                    cell = info['values'].get(dec)
                    if cell is None and info['values']:
                        cell = info['values'][max(info['values'])]
                    if cell is not None:
                        try:
                            total += float(cell['v'])
                            found += 1
                            used.add(info['row'])
                            break
                        except (TypeError, ValueError):
                            pass
    else:           # summary year: read the Totals-column value saved earlier
        pass        # handled by caller from categoryTotals
    if found < len(labels):
        warn(f'{year}: EOY extraction matched {found}/{len(labels)} rows')
    return round2(total) if found else None


def extract_eoy_summary(year_data, year, sheet):
    spec = EOY_MAP.get(year)
    if not spec:
        return None
    labels, _ = spec
    total, found = 0.0, 0
    for label in labels:
        hit = False
        for item in year_data['categoryTotals']:
            if item['name'].strip() == label:
                total += item['total']
                found += 1
                hit = True
                break
        if not hit:
            # 2011 keeps its totals block in a second label column — search the
            # whole sheet for the label and take the nearest number to its right
            for (r, c) in sorted(sheet.cells):
                if (sheet.text(r, c) or '') == label:
                    for dc in range(1, 4):
                        n = sheet.num(r, c + dc)
                        if n is not None:
                            total += n
                            found += 1
                            hit = True
                            break
                if hit:
                    break
    if found < len(labels):
        warn(f'{year}: EOY extraction matched {found}/{len(labels)} rows')
    return round2(total) if found else None


# ── Side tables (titles found on any grid sheet) ─────────────────────────────

def read_table_rows(sheet, r0, c0, ncols, stop_on_blank=2):
    """Rows starting at r0, cols c0..c0+ncols-1, until `stop_on_blank`
    consecutive completely blank rows."""
    out, blanks, r = [], 0, r0
    max_row = max(rr for rr, _ in sheet.cells)
    while r <= max_row and blanks < stop_on_blank:
        vals = [sheet.val(r, c0 + i) for i in range(ncols)]
        if all(v is None for v in vals):
            blanks += 1
        else:
            blanks = 0
            out.append((r, vals))
        r += 1
    return out


GOAL_SOURCE_BY_NAME = {
    'Emergencies': 'cashBank', 'Renovations': 'midCapped',
    'New Car': 'midOverflow', 'Retire Early': 'long',
}


def extract_side_tables(sheets, grid_years, live_year):
    side = {'taxable': [], 'otherMoney': [], 'rothContribs': {}, 'k401': {},
            'hsa': [], 'comp': {}, 'bonuses': {}, 'retirement': {},
            'rothLimit': {}, 'daf': [], 'donations': {}, 'venmo': {},
            'largePurchases': {}}
    goals = []

    def sheet_year_order():
        # newest first so point-in-time tables (taxable, k401…) keep the latest
        return sorted(grid_years, reverse=True)

    for year in sheet_year_order():
        sh = sheets[year]

        # Savings Goals (live year only, by content)
        hit = sh.find_title(r'^Savings Goals$')
        if hit and not goals:
            r0, c0, _ = hit
            for r, vals in read_table_rows(sh, r0 + 2, c0, 6):
                name = vals[0]
                if not isinstance(name, str) or name.startswith('Total'):
                    break
                target = sh.num(r, c0 + 2)
                tdate = sh.val(r, c0 + 4)
                goals.append({
                    'id': slug(name), 'name': name,
                    'source': GOAL_SOURCE_BY_NAME.get(name, 'long'),
                    'target': target or 0,
                    'targetDate': serial_to_iso(tdate) if is_serial_date(tdate) else None,
                })

        hit = sh.find_title(r'^Taxable Investments$')
        if hit and not side['taxable']:
            r0, c0, _ = hit
            for r, vals in read_table_rows(sh, r0 + 2, c0, 3, stop_on_blank=2):
                if isinstance(vals[0], str) and sh.num(r, c0 + 1) is not None:
                    side['taxable'].append({'ticker': vals[0],
                                            'shares': sh.num(r, c0 + 1),
                                            'price': sh.num(r, c0 + 2)})

        hit = sh.find_title(r'^Other Money$')
        if hit and not side['otherMoney']:
            r0, c0, _ = hit
            for r, vals in read_table_rows(sh, r0 + 1, c0, 2, stop_on_blank=1):
                if isinstance(vals[0], str) and sh.num(r, c0 + 1) is not None:
                    side['otherMoney'].append({'name': vals[0],
                                               'balance': sh.num(r, c0 + 1)})

        hit = sh.find_title(r'^Roth IRA Contr')
        if hit and not side['rothContribs']:
            r0, c0, _ = hit
            for r, vals in read_table_rows(sh, r0 + 1, c0, 2, stop_on_blank=1):
                y = sh.num(r, c0)
                amt = sh.num(r, c0 + 1)
                if y and amt is not None:
                    side['rothContribs'][str(int(y))] = amt

        hit = sh.find_title(r'^Roth / Traditional$')
        if hit and not side['k401']:
            r0, c0, _ = hit
            for r, vals in read_table_rows(sh, r0 + 1, c0, 2, stop_on_blank=2):
                label = vals[0]
                amt = sh.num(r, c0 + 1)
                if isinstance(label, str) and amt is not None:
                    key = slug(label)
                    mapping = {'pretax': 'pretax', 'pre': 'pretax',
                               'raa': 'raa', 'rollover': 'rollover',
                               'roth': 'roth', 'match': 'match',
                               'roth-ira': 'rothIra'}
                    if key in mapping:
                        side['k401'][mapping[key]] = amt

        hit = sh.find_title(r'^HSA$')
        if hit and not side['hsa']:
            r0, c0, _ = hit
            for r, vals in read_table_rows(sh, r0 + 2, c0, 3, stop_on_blank=1):
                if isinstance(vals[0], str) and sh.num(r, c0 + 1) is not None:
                    side['hsa'].append({'ticker': vals[0],
                                        'shares': sh.num(r, c0 + 1),
                                        'price': sh.num(r, c0 + 2)})

        m = sh.find_title(r'^(\d{4}) Comp$')
        if m:
            r0, c0, mm = m
            y = mm.group(1)
            comp = {'salary': sh.num(r0 + 2, c0),
                    'raisePct': sh.num(r0 + 3, c0),
                    'bonus': sh.num(r0 + 4, c0 + 1)}
            # older sheets lay this block out differently; only keep a parse
            # that actually looks like (salary, small raise %, bonus)
            if (comp['salary'] or 0) > 20000 and abs(comp['raisePct'] or 0) < 1:
                side['comp'][y] = comp
            else:
                warn(f'{y}: Comp table layout not recognised - skipped')

        m = sh.find_title(r'^(\d{4}) Retirement Contributions$')
        if m:
            r0, c0, mm = m
            y = mm.group(1)
            rows = []
            for r, vals in read_table_rows(sh, r0 + 1, c0, 5, stop_on_blank=2):
                if any(v is not None for v in vals):
                    rows.append([v if not (isinstance(v, str) and v == '') else None
                                 for v in vals])
            side['retirement'][y] = rows

        m = sh.find_title(r'^(\d{4}) Roth Limit$')
        if m:
            r0, c0, mm = m
            y = mm.group(1)
            rows = []
            for r, vals in read_table_rows(sh, r0 + 1, c0, 2, stop_on_blank=2):
                if any(v is not None for v in vals):
                    rows.append(vals)
            side['rothLimit'][y] = rows

        hit = sh.find_title(r'^Fidelity Charitable DaF$')
        if hit and not side['daf']:
            r0, c0, _ = hit
            for r, vals in read_table_rows(sh, r0 + 2, c0, 3, stop_on_blank=1):
                if isinstance(vals[0], str) and sh.num(r, c0 + 1) is not None:
                    side['daf'].append({'ticker': vals[0],
                                        'shares': sh.num(r, c0 + 1),
                                        'price': sh.num(r, c0 + 2)})

        m = sh.find_title(r'^(\d{4}) Donations')
        if m:
            r0, c0, mm = m
            y = mm.group(1)
            items = []
            for r, vals in read_table_rows(sh, r0 + 2, c0, 7, stop_on_blank=1):
                if isinstance(vals[0], str) and vals[0].startswith('Deduct'):
                    break
                foundation = sh.text(r, c0 + 4)
                if not foundation:
                    continue
                dt = sh.val(r, c0)
                items.append({
                    'date': serial_to_iso(dt) if is_serial_date(dt) else str(dt or ''),
                    'funding': sh.num(r, c0 + 1) or 0,
                    'grant': sh.num(r, c0 + 2) or 0,
                    'cash': sh.num(r, c0 + 3) or 0,
                    'foundation': foundation,
                    'cause': sh.text(r, c0 + 5) or '',
                    'deductible': (sh.text(r, c0 + 6) or '').lower() == 'yes',
                })
            side['donations'][y] = items

        m = sh.find_title(r'^(\d{4}) Venmo$')
        if m:
            r0, c0, mm = m
            y = mm.group(1)
            items = []
            for r, vals in read_table_rows(sh, r0 + 1, c0, 4, stop_on_blank=1):
                desc = sh.text(r, c0 + 1)
                amt = sh.num(r, c0 + 2)
                if desc is None or amt is None:
                    continue
                if desc.startswith('Total'):
                    break
                dt = sh.val(r, c0)
                items.append({
                    'date': serial_to_iso(dt) if is_serial_date(dt) else '',
                    'desc': desc, 'amount': amt,
                    'fromBank': (sh.text(r, c0 + 3) or '') == 'Bank',
                })
            side['venmo'][y] = items

        m = sh.find_title(r'^(\d{4}) Large CC Purchases$')
        if m:
            r0, c0, mm = m
            y = mm.group(1)
            items = []
            for r, vals in read_table_rows(sh, r0 + 1, c0, 3, stop_on_blank=1):
                desc = sh.text(r, c0 + 1)
                if desc and desc.startswith('Total'):
                    break
                amt = sh.num(r, c0 + 2)
                dt = sh.val(r, c0)
                if desc is None and amt is None:
                    continue
                items.append({
                    'date': serial_to_iso(dt) if is_serial_date(dt) else '',
                    'desc': desc or '', 'amount': amt if amt is not None else None,
                })
            # drop trailing empty placeholder rows (a date with nothing else)
            while items and not items[-1]['desc'] and items[-1]['amount'] is None:
                items.pop()
            side['largePurchases'][y] = items

        hit = sh.find_title(r'^Bonuses$')
        if hit and not side['bonuses']:
            r0, c0, _ = hit
            for r, vals in read_table_rows(sh, r0 + 2, c0, 2, stop_on_blank=1):
                dt = sh.val(r, c0)
                amt = sh.num(r, c0 + 1)
                if is_serial_date(dt) and amt is not None:
                    side['bonuses'][str(serial_to_date(dt).year)] = amt

    # per-year tables that parsed to nothing are noise, not data
    for key in ('donations', 'venmo', 'largePurchases', 'retirement', 'rothLimit'):
        side[key] = {y: v for y, v in side[key].items() if v}
    return side, goals


# ── Vacations sheet ──────────────────────────────────────────────────────────

def extract_vacations(sheet, pto_allowance):
    trips = []
    pto = {}
    hits = []
    rx = re.compile(r'^(20\d\d) (.+)$')
    for (r, c) in sorted(sheet.cells):
        v = sheet.val(r, c)
        if isinstance(v, str):
            m = rx.match(v.strip())
            if m and sheet.formula(r, c) is None:
                hits.append((r, c, m.group(1), m.group(2)))

    for (r0, c0, year, title) in hits:
        # header row is next: Paid [Credits] Due Total-Cost  (or Dates/Nights/PTO)
        headers = [sheet.text(r0 + 1, c0 + i) for i in range(1, 5)]
        if 'PTO' in [h for h in headers if h]:
            entries = []
            for r, vals in read_table_rows(sheet, r0 + 2, c0, 4, stop_on_blank=1):
                name = vals[0]
                if not isinstance(name, str):
                    if sheet.text(r, c0 + 1) == 'Used':
                        break
                    continue
                dates = sheet.val(r, c0 + 1)
                entries.append({
                    'name': name,
                    'dates': serial_to_iso(dates) if is_serial_date(dates)
                             else str(dates or ''),
                    'nights': sheet.num(r, c0 + 2),
                    'ptoDays': sheet.num(r, c0 + 3) or 0,
                })
            pto[year] = {'allowance': pto_allowance, 'entries': entries}
            continue
        if 'Paid' not in [h for h in headers if h]:
            continue
        has_credits = 'Credits' in [h for h in headers if h]
        ncols = 4 if has_credits else 3
        items = []
        nights = None
        r = r0 + 2
        max_row = max(rr for rr, _ in sheet.cells)
        while r <= max_row:
            label = sheet.text(r, c0)
            if label == 'Total':
                nights = sheet.num(r + 1, c0 + (ncols - 1))
                break
            paid = sheet.num(r, c0 + 1)
            credits = sheet.num(r, c0 + 2) if has_credits else None
            due = sheet.num(r, c0 + (3 if has_credits else 2))
            if label is None and paid is None and due is None:
                break
            note = sheet.comments.get((r, c0)) or sheet.comments.get((r, c0 + 1))
            items.append({'label': label or '', 'paid': paid or 0,
                          **({'credits': credits or 0} if has_credits else {}),
                          'due': due or 0,
                          **({'note': note} if note else {})})
            r += 1
        trips.append({'id': slug(f'{year}-{title}'), 'name': f'{year} {title}',
                      'year': int(year), 'nights': nights, 'items': items})
    return {'trips': trips, 'pto': pto}


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('xlsx')
    ap.add_argument('--out', default='financial-plan-data.json')
    ap.add_argument('--expected', default='expected-2026.json')
    args = ap.parse_args()

    import os
    path = os.path.expanduser(args.xlsx)
    sheets = load_workbook(path)
    today = date.today()

    years = {}
    grid_years = []
    expected = {'cells': {}, 'balances': {}, 'generated': datetime.now().isoformat(),
                'source': os.path.basename(path)}
    live_year = None
    pinned_rows = {}

    for name, sheet in sheets.items():
        if not re.match(r'^\d{4}$', name):
            continue
        header_row, months = find_month_header(sheet)
        if months:
            grid_years.append(name)
            label_col = label_column(sheet, header_row, months[0][0])
            last_month = months[-1][1]
            this_month = f'{today.year}-{today.month:02d}'
            if last_month >= this_month and live_year is None:
                live_candidates = [name]
                # the LIVE year is the latest grid whose months reach past today
            # decide live later; parse pinned for now and re-parse live after
            pinned_rows[name] = (header_row, months, label_col)
        else:
            years[name] = import_summary_year(sheet, name)
            eoy = extract_eoy_summary(years[name], name, sheet)
            if eoy is not None:
                years[name]['eoyCash'] = eoy

    # live year = latest grid whose last month is not in the past
    this_month = f'{today.year}-{today.month:02d}'
    live_candidates = [y for y in grid_years
                       if pinned_rows[y][1][-1][1] >= this_month]
    live_year = max(live_candidates) if live_candidates else None

    for name in sorted(grid_years):
        header_row, months, label_col = pinned_rows[name]
        sheet = sheets[name]
        if name == live_year:
            years[name] = import_live_year(sheet, name, header_row, months,
                                           label_col, today, expected)
        else:
            years[name], rows_list = import_pinned_year(sheet, name, header_row,
                                                        months, label_col)
            eoy = extract_eoy(sheet, name, years[name], rows_list)
            if eoy is not None:
                years[name]['eoyCash'] = eoy

    side, goals = extract_side_tables(sheets, grid_years, live_year)

    vacations = {'trips': [], 'pto': {}}
    if 'Vacations' in sheets:
        vacations = extract_vacations(sheets['Vacations'], 32)

    account_names = {}
    if live_year and years.get(live_year):
        account_names = years[live_year].pop('accountNames', {})

    state = {
        'schema': 1,
        'settings': {'midTermRateAnnual': 0.03, 'longTermRateAnnual': 0.07,
                     'ptoAllowance': 32, 'accountNames': account_names,
                     'accountRates': {'cash': 0, 'mid': 0, 'long': 0.07,
                                      'bank': 0}},
        'years': years,
        'goals': goals,
        'side': side,
        'vacations': vacations,
        'ui': {'activeYear': live_year, 'activeTab': 'budget'},
    }

    with open(args.out, 'w') as f:
        json.dump(state, f, separators=(',', ':'))
    with open(args.expected, 'w') as f:
        json.dump(expected, f, separators=(',', ':'))

    # Report COUNTS only — never values.
    n_cells = sum(len(y.get('cells', {})) for y in years.values())
    n_notes = sum(
        sum(1 for c in y.get('cells', {}).values() if c.get('note'))
        + sum(1 for i in y.get('categoryTotals', []) if i.get('note'))
        + len(y.get('extraNotes', []))
        for y in years.values())
    print(f'Years: {len(years)} ({sum(1 for y in years.values() if y["kind"] == "grid")} grids, '
          f'{sum(1 for y in years.values() if y["kind"] == "summary")} summaries; live = {live_year})')
    print(f'Cells: {n_cells}  Notes: {n_notes}  Goals: {len(goals)}  '
          f'Trips: {len(vacations["trips"])}  '
          f'Expected formula cells: {len(expected["cells"]) + len(expected["balances"])}')
    for y in sorted(years):
        yr = years[y]
        if yr['kind'] == 'grid':
            print(f'  {y}: grid {yr.get("model", "pinned")}, {len(yr["categories"])} rows, '
                  f'{len(yr["cells"])} cells'
                  + (f', eoy ok' if yr.get('eoyCash') is not None else ''))
        else:
            print(f'  {y}: summary, {len(yr["categoryTotals"])} rows'
                  + (f', eoy ok' if yr.get('eoyCash') is not None else ''))
    print(f'Side tables: ' + ', '.join(
        f'{k}={len(v)}' for k, v in side.items() if v))
    if warnings:
        print(f'{len(warnings)} warning(s) above.', file=sys.stderr)
    else:
        print('No warnings.')


if __name__ == '__main__':
    main()
