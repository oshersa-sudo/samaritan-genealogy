# -*- coding: utf-8 -*-
# STANDING RULE (owner, 2026-11-18): every BIRTH date that was taken from the community-registry Excel (מיפקד.xlsx)
# is ONE DAY LATE in the file — the true date is the day before (18.11 → 17.11).  Applies to every Excel-layer person
# (ids M<number>) that has a day + month; year-only dates are untouched.  Death dates are NOT touched (the rule is about births).
#
# Rolls over correctly:  1.3.1990 → 28.2.1990 · 1.1.1942 → 31.12.1941 (byear and g follow).
# The 'bamb' flag (day/month ambiguous in the SOURCE cell) is a property of the Excel cell, not of the date — left as it is.
#
# Idempotent and safe to run on every build (build.ps1 calls it): the ORIGINAL Excel date of each person is kept in
# birthdate_shift_20261118.json, so a second run changes nothing, a person re-added later from the archive (which stays a raw
# mirror of the Excel) is shifted exactly once, and the whole rule can be undone from the log.
import json, io, re, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
LOG = 'birthdate_shift_20261118.json'
integ = json.load(io.open('integrate.json', encoding='utf-8'))
try:
    log = json.load(io.open(LOG, encoding='utf-8'))
except FileNotFoundError:
    log = {'rule': 'תאריך לידה מקובץ המיפקד (אקסל) מוקדם ביום אחד מהכתוב בקובץ — נקבע ע״י הבעלים 18.11.2026. orig = כפי שבאקסל, new = אחרי החסרת יום.', 'persons': {}}
L = log['persons']
n_new = n_same = n_skip = 0
rolled_month, rolled_year, warn = [], [], []
for m in integ['modern']:
    if not re.fullmatch(r'M\d+', str(m.get('id', ''))): continue          # Excel-layer persons only
    if not (m.get('bmonth') and m.get('bday')): continue                 # no day+month → nothing to shift
    if not m.get('byear'): warn.append((m['id'], 'day+month without a year — skipped')); n_skip += 1; continue
    cur = [int(m['byear']), int(m['bmonth']), int(m['bday'])]
    rec = L.get(m['id'])
    if rec and cur == rec['new']: n_same += 1; continue                  # already shifted
    if rec and cur != rec['orig']: warn.append((m['id'], 'date edited since the shift (%s) — left as is' % cur)); n_skip += 1; continue
    orig = rec['orig'] if rec else cur
    try: d = datetime.date(*orig) - datetime.timedelta(days=1)
    except ValueError: warn.append((m['id'], 'invalid date %s — skipped' % orig)); n_skip += 1; continue
    new = [d.year, d.month, d.day]
    if new[0] != orig[0]:
        m['byear'] = new[0]
        if isinstance(m.get('g'), str) and m['g'].startswith(str(orig[0])): m['g'] = str(new[0]) + m['g'][len(str(orig[0])):]
        rolled_year.append((m['id'], m.get('name'), orig, new))
    elif new[1] != orig[1]: rolled_month.append(m['id'])
    m['bmonth'], m['bday'] = new[1], new[2]
    L[m['id']] = {'orig': orig, 'new': new}
    n_new += 1
if n_new:
    io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
    io.open(LOG, 'w', encoding='utf-8').write(json.dumps(log, ensure_ascii=False, indent=1))
print('birth dates (Excel) one day back: %d shifted now, %d already shifted, %d skipped; month rolled back: %d, YEAR rolled back: %s' % (n_new, n_same, n_skip, len(rolled_month), rolled_year))
for w in warn: print('  WARN', *w)
