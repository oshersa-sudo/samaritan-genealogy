# -*- coding: utf-8 -*-
# 2026-11-09 — owner: every person must read «שם (בן/בת <אב>)»; an Arabic nickname may sit inside the same brackets.
#  1. registry persons whose name already carries a bracket (nickname) but no «בן/בת» get the father's given name inside it: «שוהם (בן אסעד, מורגן)»
#     (the father is the ACTUAL linked parent — same rule as the page's displayName)
#  2. Shoham's wife (M274): Hebrew «יפה», Arabic «בדיעה»  → «יפה (בת ישמעאל, בדיעה)»; the children's mother field follows
#  3. Netanel's line: Amit (M659) gets a son Ido, born 2025 (given by the owner)
# Idempotent; log in names_ido_20261109.json
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
integ = json.load(io.open('integrate.json', encoding='utf-8'))
master = json.load(io.open('master_v2.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
M = {m['id']: m for m in integ['modern']}
LOG = []


def given(name):
    n = re.sub(r'\s*[\(（].*$', '', name or '').strip()
    return n.split()[0] if n.split() else ''


def father_of(m):
    par = m.get('parent') or ''
    if par.startswith('#'): par = par[1:]
    q = P.get(par) or M.get(par)
    return given(q['name']) if q else given(m.get('father'))


# 2. Shoham's wife — rename first so step 1 sees the final names
w = M['M274']
w['name'] = 'יפה (בדיעה)'
w['notes'] = 'נישאה לשוהם בן אסעד סראוי'
for s in w.get('spouses') or []:
    if s.get('ref') == 'M190': s['name'] = 'שוהם (מורגן) בן אסעד'
sh = M['M190']
for s in sh.get('spouses') or []:
    if s.get('ref') == 'M274': s['name'] = 'יפה (בדיעה) בת חיכמת'
sh['notes'] = 'נישא ליפה (בדיעה) בת חיכמת סראוי'
for m in integ['modern']:
    if m.get('parent') == 'M190': m['mother'] = 'יפה (בדיעה)'

# 1. father inside the bracket
for m in integ['modern']:
    n = m['name']
    if not re.search(r'[\(（]', n) or re.search(r'ב[ןת]\s', n): continue
    mm = re.match(r'^(.*?)\s*[\(（]([^)）]*)[\)）]\s*$', n)
    if not mm: continue
    rel = 'בת' if m.get('sex') == 'F' else 'בן'
    f = father_of(m)
    if not f: LOG.append({'skipped': m['id'], 'name': n}); continue
    new = '%s (%s %s, %s)' % (mm.group(1), rel, f, mm.group(2))
    LOG.append({'id': m['id'], 'from': n, 'to': new}); m['name'] = new

# 3. Ido
if 'ow-ido' not in M:
    integ['modern'].append({'id': 'ow-ido', 'name': 'עידו', 'sex': 'M', 'parent': 'M659', 'g': '2025', 'byear': 2025,
                            'bmonth': None, 'bday': None, 'dyear': None, 'age': None, 'family': 'סראוי', 'father': 'עמית',
                            'job': None, 'bplace': None, 'mother': None, 'notes': None,
                            'src': 'נוסף לפי הבעלים, 9.11.2026'})
    LOG.append({'added': 'ow-ido', 'parent': 'M659'})
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('names_ido_20261109.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
for x in LOG: print(x)
