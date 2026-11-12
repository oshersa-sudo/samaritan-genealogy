# -*- coding: utf-8 -*-
# 2026-11-12 — owner: complete the OTHER trees (Marhibim, Tsfarim, Priests) from the census Excel (מיפקד.xlsx → excel_layer_archive.json): ONLY what is certain.
# Same gate as the Danfim rounds (scan2 + scan3):
#   unique father by name (every token on the card, spelling-tolerant) + age (16–70, alive at the birth), AND one of
#     (A) the wife on the father's card = the child's mother (pet-form tolerance), or
#     (B) the father's patronym is witnessed by a birth record of the Arabic events workbook (father + grandfather + mother), closure over generations.
#   Extra caution for the non-Danfim trees:
#     * a census father must have a known birth (or a death year inside the plausible window) — historic priests with no dates never qualify;
#     * the candidate father must belong to the matching tree (family→house), and registry fathers to the same family group;
#     * if the archived Excel layer already pointed at a DIFFERENT father (resolvable id), the person is held back as «conflict», not added.
# Output: registry_certain_scan4_20261112.json  {dups, certain, conflicts, rest}
import sys, io, json, re, collections
src = open('scan2_registry_20261111.py', encoding='utf-8').read().split("res = {'dups'")[0]
src = src.replace("DAN_FAM = {'דינפי', 'סראוי'}", "DAN_FAM = {'צדקה', 'מרחיב', 'לוי', 'כהן', 'צפרים'}")
exec(compile(src, 'scan2', 'exec'))
sys.stdout.reconfigure(encoding='utf-8')
GRP = {'דינפי': 'D', 'דנפי': 'D', 'סראוי': 'D', 'צדקה': 'T', 'צפרים': 'T', 'מרחיב': 'M', 'לוי': 'L', 'כהן': 'L'}
HOUSES = {'D': ('ב.',), 'T': ('ד.',), 'M': ('ג.',), 'L': ('ו.',)}   # strict: the 15 Marhibi / 48 Tsfari registry persons already on the site sit only in these houses
SEX = {'ז': 'M', 'נ': 'F', 'm': 'M', 'f': 'F', 'M': 'M', 'F': 'F'}
def sx(v): return SEX.get(v, v)
def grp(x): return GRP.get(x.get('family'))
def census_ok(i, x, by):
    p = P[i]
    if sx(p.get('sex')) != 'M' or H[i][:2] not in HOUSES.get(grp(x), ()): return None
    b, d = greg(p.get('birth')), greg(p.get('death'))
    if b:
        if not (16 <= by - b <= 70): return None
    elif d:
        if not (-1 <= d - by <= 95): return None
    else: return None                       # no dates at all → no age check possible → never certain
    if d and by > d + 1: return None
    return True
def census_cands(x, need_wife=True):
    fn, mn, by = x.get('father'), x.get('mother'), x.get('byear'); out = []
    if not by or not fn: return out
    for i, p in P.items():
        if not census_ok(i, x, by): continue
        if not any(same2(fn, g) for g in names_all(p['name'])): continue
        if (not need_wife) or any(same2(mn, w, True) for w in wives_all(p)): out.append((i, 'census'))
    return out
def modern_cands(x, need_wife=True):
    fn, mn, by = x.get('father'), x.get('mother'), x.get('byear'); out = []
    if not by or not fn: return out
    for i, m in POOL.items():
        if i == x.get('id') or sx(m.get('sex')) != 'M' or not m.get('byear'): continue
        if grp(m) != grp(x): continue
        if not any(same2(fn, g) for g in names_all(m['name'])): continue
        if not (16 <= by - m['byear'] <= 70): continue
        if m.get('dyear') and by > int(m['dyear']) + 1: continue
        if (not need_wife) or any(same2(mn, w, True) for w in wives_all(m)): out.append((i, 'modern'))
    return out
def dup_of(x):
    """registry person == a card already on the site: same given name (lenient), same father name, birth within 3 years."""
    by = x.get('byear'); out = []
    if not by: return out
    for i, p in P.items():
        if sx(p.get('sex')) != sx(x.get('sex')) or H[i][:2] not in HOUSES.get(grp(x), ()): continue
        b = greg(p.get('birth'))
        if not b or abs(b - by) > 3: continue
        if not any(same2(given(x['name']), g, True) for g in names_all(p['name'])): continue
        f = P.get(p.get('father_id'))
        if f and any(same2(x.get('father'), g) for g in names_all(f['name'])): out.append(i)
    for i, m in onsite.items():
        if sx(m.get('sex')) != sx(x.get('sex')) or grp(m) != grp(x) or not m.get('byear') or abs(m['byear'] - by) > 3: continue
        if not any(same2(given(x['name']), g, True) for g in names_all(m['name'])): continue
        if m.get('father') and same2(x.get('father'), m['father'], True) and same2(x.get('mother') or '', m.get('mother') or '', True): out.append(i)
    return out
# ---- events workbook witness (gate B): reuse scan3's definitions
s3 = open('scan3_registry_20261111.py', encoding='utf-8').read()
s3 = s3.split("onsite = {m['id']")[0].split("ev = json.load")[1]
exec(compile("ev = json.load" + s3, 'scan3', 'exec'))
onsite = {m['id']: m for m in integ['modern']}
rm = json.load(io.open('registry_merged_20261109.json', encoding='utf-8'))
ALT = {}
for i, p in P.items():
    for a in p.get('alt_ids') or []: ALT[a] = i
STALE = {'מר-יעקב202': '206', 'מר-זבולן': '204', 'הס-אסעד': '154'}
def canon(i):
    i = STALE.get(i, i); i = rm.get(i, i); i = ALT.get(i, i)
    if i in dups and len(dups[i]) == 1: i = dups[i][0]      # registry person that is the SAME as an on-site card
    return i
absent = {k: x for k, x in absent.items() if x.get('byear') and x.get('father')}
dups = {k: dup_of(x) for k, x in absent.items()}; dups = {k: v for k, v in dups.items() if v}
rest = {k: x for k, x in absent.items() if k not in dups}
certain, why = {}, {}
rounds, changed = 0, True
while changed and rounds < 8:
    changed = False; rounds += 1
    for rid, x in sorted(rest.items(), key=lambda kv: kv[1].get('byear') or 0):
        if rid in certain: continue
        c = census_cands(x) + modern_cands(x)
        c = [y for y in c if y[1] == 'census' or y[0] in onsite or y[0] in certain]
        if len(c) == 1:
            certain[rid] = c[0]; why[rid] = 'wife-match'; POOL[rid] = {**x, 'id': rid}; changed = True; continue
        c2 = census_cands(x, False) + modern_cands(x, False)
        c2 = [y for y in c2 if y[1] == 'census' or y[0] in onsite or y[0] in certain]
        good = [(i, k, evidence(x, i, k)) for i, k in c2]; good = [g for g in good if g[2]]
        if len(good) == 1 and len({g[0] for g in good}) == 1:
            certain[rid] = (good[0][0], good[0][1]); why[rid] = 'events: ' + good[0][2][0]; POOL[rid] = {**x, 'id': rid}; changed = True
# ---- conflict check against the archived layer's own pointer
conflicts = {}
for rid, (fid, kind) in list(certain.items()):
    par = (arch[rid].get('parent') or '')
    if par.startswith('#') or par.startswith('M'):
        pid = canon(par.lstrip('#'))
        if (pid in P or pid in arch) and pid != canon(fid):
            conflicts[rid] = {'derived': fid, 'archive_parent': par}
# a child whose certain father is a conflict is held back too (closure)
changed = True
while changed:
    changed = False
    for rid, (fid, kind) in list(certain.items()):
        if rid in conflicts: continue
        if fid in conflicts: conflicts[rid] = {'derived': fid, 'archive_parent': 'father held back'}; changed = True
final = {k: v for k, v in certain.items() if k not in conflicts}
res = {'dups': dups, 'conflicts': conflicts,
       'certain': {k: {'father': v[0], 'kind': v[1], 'why': why[k]} for k, v in final.items()},
       'rest': [k for k in absent if k not in dups and k not in final]}
io.open('registry_certain_scan4_20261112.json', 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=1))
print('absent', len(absent), '| dups', len(dups), '| certain', len(final), '| conflicts', len(conflicts), '| rounds', rounds)
by_fam = collections.defaultdict(lambda: [0, 0, 0, 0])
for k, x in absent.items():
    f = x['family']; by_fam[f][0] += 1
    if k in dups: by_fam[f][1] += 1
    elif k in final: by_fam[f][2] += 1
    elif k in conflicts: by_fam[f][3] += 1
print('family: absent, dup, certain, conflict'); [print(' ', f, v) for f, v in by_fam.items()]
print('\nDUPS:')
for k, v in dups.items(): print(' ', k, arch[k]['name'], arch[k].get('byear'), 'F', arch[k].get('father'), 'M', arch[k].get('mother'), '==', [(i, (P.get(i) or onsite.get(i))['name'][:24]) for i in v])
print('\nCONFLICTS:')
for k, v in conflicts.items(): print(' ', k, arch[k]['name'], arch[k].get('byear'), v)
print('\nCERTAIN:')
for k, v in final.items():
    x = arch[k]; fa = (P.get(v[0]) or arch.get(v[0]) or {}).get('name')
    print(' ', k, x['family'], x['name'], x.get('byear'), 'F', x.get('father'), 'M', x.get('mother'), '->', v[0], '/', fa, '|', why[k][:60])
