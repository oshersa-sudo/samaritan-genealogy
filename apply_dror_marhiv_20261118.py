# -*- coding: utf-8 -*-
# 2026-11-18 — owner: apply the Dror Marhiv correction (and its details) to the live tree.
#
# THE ERROR: the registry gave both Marhibi "אברהם" groups the same father name, so דרור (b.1964) and מרים (b.1965)
# were hung under אברהם בן סעד (M33, b.1909 — now the live node מר-אברהם208). Their MOTHER column separates them:
#   וג'הה  → M33's five children (מנשה / יצחק / ניסים / ברוך / רצון)         — correct, left untouched
#   דליה   → דרור, מרים (+ יששכר)  — the children of ANOTHER Abraham: אברהם בן יששכר, son of census #195.
# אברהם בן יששכר is not in the registry → added as a son of #195 (as the owner stated); דרור + מרים hang under him.
# Details applied with them: מרים's death year 2024; the brother יששכר; דרור's registry daughter עדן (father דרור + mother נרימן
# — Dror's row says «נישא לנרימן» and Narimaan's row says «נישאה לדרור»: one couple, nothing else it can be).
#
# Idempotent. Additive only — touches no existing person. Log: dror_marhiv_applied_20261118.json
# Order afterwards (STANDING): build_sources.py → annotate_bamb.py → derive_mothers_20261106.py → build.ps1 (assigns uids).
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
integ = json.load(io.open('integrate.json', encoding='utf-8'))
master = json.load(io.open('master_v2.json', encoding='utf-8'))
arch = {m['id']: m for m in json.load(io.open('excel_layer_archive.json', encoding='utf-8'))['modern']}
P = {p['id'] for h in master['houses'] for f in h['families'] for p in f['persons']}
M = {m['id']: m for m in integ['modern']}
LOG = []


def norm(s):
    s = re.sub(r'\s+', ' ', s or '').strip()
    s = re.sub(r'\(\s+', '(', s); s = re.sub(r'\s+\)', ')', s); s = re.sub(r'\s*\(', ' (', s)
    return s


# --- the two persons the registry has no row for (owner-supplied) -------------------------------------------------
OWNER = 'לפי הבעלים — תיקון שיוך דרור ומרים (אושר 18.11.2026)'
NEW = [
    {'id': 'mx-avr-yis', 'name': 'אברהם', 'sex': 'M', 'parent': '#195', 'family': 'מרחיב', 'father': 'יששכר',
     'notes': 'נשוי לדליה. אביהם של דרור, מרים ויששכר. אינו מופיע ברשם הקהילה — הוא אינו אברהם בן סעד (מר-אברהם208, נולד 1909), שילדיו אמם וג׳הה.',
     'src': OWNER + '; שם אשתו דליה — מעמודת האם בשורות דרור (346) ומרים (354), קובץ מיפקד.xlsx, גיליון «תאריך לידה»',
     'mother_src': None},
    {'id': 'mx-yissachar', 'name': 'יששכר', 'sex': 'M', 'parent': 'mx-avr-yis', 'family': 'מרחיב', 'father': 'אברהם',
     'mother': 'דליה', 'notes': 'אחיהם של דרור ומרים. אין עליו פרטים נוספים.',
     'src': OWNER + '; אינו מופיע ברשם הקהילה'},
]
for rec in NEW:
    rec = {k: v for k, v in rec.items() if v is not None}
    if rec['id'] in M: continue
    integ['modern'].append(rec); M[rec['id']] = rec
    LOG.append({'added': rec['id'], 'name': rec['name'], 'parent': rec['parent'], 'source': 'owner'})

# --- the registry persons (from the archived Excel layer: same row, same fields) ------------------------------------
PLACE = {'M342': 'mx-avr-yis', 'M350': 'mx-avr-yis', 'M694': 'M342'}
EXTRA_NOTE = {'M350': ' שנת הפטירה (2024) לפי הבעלים.'}
for rid, parent in PLACE.items():
    if rid in M: continue
    m = json.loads(json.dumps(arch[rid], ensure_ascii=False))
    m['parent'] = parent
    m['name'] = norm(m['name']); m.pop('synth', None)
    for fld in ('mother', 'father', 'notes', 'job', 'bplace', 'family'):
        if m.get(fld): m[fld] = norm(m[fld])
    if rid in EXTRA_NOTE: m['notes'] = (m.get('notes') or '') + EXTRA_NOTE[rid]
    integ['modern'].append(m); M[rid] = m
    LOG.append({'added': rid, 'name': m['name'], 'parent': parent, 'source': 'registry row'})

# --- verify: no dangling parent, and every new chain reaches census #195 ----------------------------------------------
bad = 0
for m in integ['modern']:
    par = (m.get('parent') or '').lstrip('#')
    if par and par not in P and par not in M and not par.startswith('@'): print('DANGLING parent', m['id'], par); bad += 1
def up(i):
    seen = []
    while i in M and i not in seen:
        seen.append(i); i = (M[i].get('parent') or '').lstrip('#')
    return seen + [i]
for rid in ('M342', 'M350', 'M694', 'mx-yissachar'):
    print(rid, '→', ' → '.join(up(rid)))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('dror_marhiv_applied_20261118.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(len(LOG), 'added;', bad, 'dangling')
