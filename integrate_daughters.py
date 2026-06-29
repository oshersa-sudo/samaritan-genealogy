# -*- coding: utf-8 -*-
# Adds NEW daughters discovered via mother-names: a birth record's mother "X بنت Y Z"
# means X is a daughter of Y. Where Y(+grandfather) strictly+uniquely matches a tree
# person and X is not already their child (robust dedupe incl. nickname variants), add
# X as that person's daughter (modern entry, parent = the father). Additive; never
# changes existing people. id prefix 'evd-'. Run AFTER integrate_events_v2, before
# integrate_marriages. DRY unless --apply.
import json, io, re, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
DRY = '--apply' not in sys.argv
# reuse the strict matcher + helpers from integrate_marriages (everything before 'pairs={')
exec(open('integrate_marriages.py', encoding='utf-8').read().split('pairs={}')[0])

# child-given-keys already under each tree person (via father_id OR modern parent)
kids = defaultdict(set)
for cid, c in persons.items():
    w = words_he(c.get('name', '')); g = keyn(w[0]) if w else None
    if not g: continue
    fid = c.get('father')
    if fid and fid in persons: kids[fid].add(g)
    if cid in mod_by_id:
        par = mod_by_id[cid].get('parent', ''); par = par[1:] if par.startswith('#') else par
        if par in persons: kids[par].add(g)

# robust existence: does any person with given≈X already have father≈fname?
def already(xgiven, father_pid):
    fw = words_he(persons[father_pid].get('name', '')); fname_g = keyn(fw[0]) if fw else ''
    for pid in allidx.get(keyn(xgiven), []):
        fg = fgiven(pid)
        if fg and (keyn(fg) == fname_g or gm(fg, fname_g)): return True
    return False

def parsemother(s):
    s = re.sub(r'^\s*(ام|أم|أرملة)\s+', '', s); return words(s)
def htag(pid):
    h = (persons.get(pid) or {}).get('house', '')
    for t in ('דנפים','מרחיבים','צפרים','כהונה'):
        if t in (h or ''): return t
    if pid in mod_by_id: return mod_by_id[pid].get('family','')
    return ''

found = {}; samp = []
for rec in events:
    if rec.get('event') != 'birth': continue
    mo = rec.get('mother', '') or ''
    if not mo or 'أجنبية' in mo or 'اجنبية' in mo or mo.strip().isdigit(): continue
    mw = parsemother(mo)
    if len(mw) < 2: continue
    xg = mw[0]; mfa = mw[1]; mgf = mw[2] if len(mw) > 2 else ''
    fpid = match_person(mfa, canon2(mgf) if mgf else '')      # mother's FATHER in the tree
    if not fpid: continue
    if keyn(xg) in kids.get(fpid, set()): continue            # already a known child
    if already(xg, fpid): continue                            # nickname-variant safety
    key = (keyn(xg), fpid)
    if key in found: continue
    xhe = re.sub(r'\s+', ' ', ar2he(xg)).strip()       # xg = the mother's given name (already parsed)
    if len(xhe) < 2: continue
    found[key] = {'name': xhe, 'father': fpid, 'husband': rec.get('father', ''), 'src_mother': mo}
    if len(samp) < 14: samp.append((xhe, persons[fpid]['name'], fpid))

print('בנות חדשות להוספה (אם בת אב-שבעץ, שאינה כבר ילדה):', len(found))
for nm, fn, fp in samp: print('   %-14s בת %s (%s)' % (nm, fn, fp))

if DRY:
    print('\n(הרצת-יבש — להחלה: --apply)')
else:
    integ['modern'] = [x for x in integ['modern'] if not str(x.get('id','')).startswith('evd-')]
    seq = 0
    for key, d in found.items():
        seq += 1; nid = 'evd-%d' % seq
        parent = ('#'+d['father']) if d['father'] in {p['id'] for h in master['houses'] for f in h['families'] for p in f['persons']} else d['father']
        integ['modern'].append({'id': nid, 'name': d['name'], 'sex': 'נ', 'parent': parent,
            'g': '', 'byear': None, 'family': htag(d['father']),
            'father': persons[d['father']]['name'], 'mother': '',
            'notes': 'בת ' + persons[d['father']]['name'] + ' (מהמרשם). נישאה ל' + re.sub(r'\s+',' ',ar2he(d['husband'])).strip()})
    io.open('integrate.json','w',encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
    print('APPLIED', seq, 'new daughters (modern entries, parent = their father).')
