# -*- coding: utf-8 -*-
# 2026-11-06 — re-adds the Excel (מיפקד.xlsx) persons the owner approved:
#   rule (owner): column L (דרגת ודאות) = 'גבוהה' AND column O (דגלים) does not contain 'חשד'
#   (genealogy_readd_plan.xlsx, sheet 'תוספת מוצעת').
# A person is added only if the father it hangs under is on the site (scan layer, a protected record,
# or another person added in this same run) — otherwise it is listed in excel_readd_pending.json.
# While adding: Hebrew spelling is corrected, and a name that exists both in the Excel and on the site
# with a slightly different (full / defective) spelling takes the SITE spelling.
# Everything added is logged in excel_readd_log.json (id, parent, every spelling change). Idempotent.
import json, io, re, sys
import openpyxl
sys.stdout.reconfigure(encoding='utf-8')

PLAN = r'C:\Users\osher\Documents\torah\genealogy_readd_plan.xlsx'
integ = json.load(io.open('integrate.json', encoding='utf-8'))
arch = json.load(io.open('excel_layer_archive.json', encoding='utf-8'))
M = {m['id']: m for m in arch['modern']}
master = json.load(io.open('master_v2.json', encoding='utf-8'))
census_ids = {p['id'] for h in master['houses'] for f in h['families'] for p in f['persons']}
present = {m['id'] for m in integ['modern']}

# ------------------------------------------------------------------ selection (owner's rule)
ws = openpyxl.load_workbook(PLAN)['תוספת מוצעת']
rows = {r[0]: r for r in ws.iter_rows(min_row=2, values_only=True)}
sel = {i: r for i, r in rows.items() if r[11] == 'גבוהה' and not (r[14] and 'חשד' in r[14])}


def father_of(r):
    m = re.search(r'\(ID ([^)]+)\)\s*$', r[12] or '')
    return m.group(1).strip() if m else None


changed = True
while changed:                                         # a person needs its father on the site
    changed = False
    for i, r in list(sel.items()):
        f = father_of(r)
        ok = f in census_ids or f in present or f in sel
        if not ok:
            del sel[i]; changed = True
pending = [dict(id=i, name=r[1], father_needed=father_of(r), tier=r[11], father_tier=(rows.get(father_of(r)) or [None] * 12)[11])
           for i, r in rows.items() if r[11] == 'גבוהה' and not (r[14] and 'חשד' in r[14]) and i not in sel and i not in present]

# ------------------------------------------------------------------ Hebrew spelling
NIQ = re.compile('[\u0591-\u05c7]')
TOKEN = re.compile(r"[\u0590-\u05ff'\u05f3\"\u05f4\-]+")
# (1) plain typos / non-standard spellings
TYPO = {'צתדקה': 'צדקה', 'נשאה': 'נישאה', 'ניש': 'נישא', 'נישרה': 'נישאה', 'ניכה': 'נכה', 'היתה': 'הייתה', 'חיט': 'חייט',
        'כורח': 'כורך', 'נתנ-אל': 'נתנאל', 'העידה': 'העדה', 'בנימם': 'בנימים', 'יעקוב': 'יעקב'}
# (2) same name, full vs defective spelling -> the SITE's spelling (site: זבולן, הדנפי, אלטיף, אבישע, עיזואת, סראוי…)
SITE = {'זבולון': 'זבולן', 'הדינפי': 'הדנפי', 'דינפי': 'דנפי', 'אילטיף': 'אלטיף', 'אבישוע': 'אבישע', 'עזאת': 'עיזואת', 'עיזאת': 'עיזואת', 'סיראוי': 'סראוי'}
PREF = 'לבהומשכ'
CHANGES = []


def fix_token(t):
    core = NIQ.sub('', t)
    for table in (TYPO, SITE):
        if core in table:
            return table[core]
        if len(core) > 3 and core[0] in PREF and core[1:] in table:
            return core[0] + table[core[1:]]
    return t


def fix_text(s, rec_id, field):
    if not s:
        return s
    orig = s
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\(\s+', '(', s)
    s = re.sub(r'\s+\)', ')', s)
    s = re.sub(r'\s*\(', ' (', s)
    s = TOKEN.sub(lambda m: fix_token(m.group(0)), s)
    # sentence-level fixes found in the Excel notes
    s = re.sub(r'^נישא (?=[\u05d0-\u05ea]+ בת )', 'נישא ל', s) if re.match(r'^נישא נוגה ', s) else s
    s = s.replace('נישא ל ל', 'נישא ל')
    s = s.replace('נישא ניכה', 'נישא נכה')
    s = re.sub(r'^נכה לא נישאה$', 'נכה, לא נישאה', s)
    s = re.sub(r'^לא נישאה הייתה נכה$', 'לא נישאה, הייתה נכה', s)
    s = re.sub(r'^לא נישא (אילם)$', r'לא נישא, \1', s)
    s = re.sub(r'^מת בתאונה בסחנה טבע במים$', 'מת בתאונה בסחנה, טבע במים', s)
    s = s.replace('נישא למרים אישה יהודיה', 'נישא למרים, אישה יהודייה')
    s = s.replace('עורך-דין', 'עורך דין')
    if s != orig.strip():
        CHANGES.append({'id': rec_id, 'field': field, 'from': orig, 'to': s})
    return s


added = []
for i, r in sel.items():
    m = json.loads(json.dumps(M[i], ensure_ascii=False))
    f = father_of(r)
    m['parent'] = ('#' + f) if f in census_ids else f
    for fld in ('name', 'mother', 'father', 'notes', 'job', 'bplace', 'family'):
        if m.get(fld):
            m[fld] = fix_text(m[fld], i, fld)
    m.pop('spouses', None)
    added.append(m)
# parents first so the order in the file is stable
integ['modern'] = integ['modern'] + [m for m in added if m['id'] not in present]
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('excel_readd_log.json', 'w', encoding='utf-8').write(json.dumps(
    {'added': [{'id': m['id'], 'name': m['name'], 'parent': m['parent']} for m in added], 'spelling_changes': CHANGES, 'rule': "L=גבוהה & O ללא 'חשד'; אב חייב להיות באתר"}, ensure_ascii=False, indent=1))
io.open('excel_readd_pending.json', 'w', encoding='utf-8').write(json.dumps(pending, ensure_ascii=False, indent=1))
print('selected by rule:', len([1 for r in rows.values() if r[11] == 'גבוהה' and not (r[14] and 'חשד' in r[14])]), '| added now:', len(added),
      '| waiting for a father node:', len(pending), '| spelling changes:', len(CHANGES))
