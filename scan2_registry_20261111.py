# -*- coding: utf-8 -*-
# 2026-11-11 — round 2: absent registry persons of the Danfi / Sarawi families (the only families the Excel holds for the Danfim tree).
# Same certainty gate as round 1 (unique father by name + age + father's wife = child's mother, closure over generations), with
#   (a) father names matched on EVERY name token on the card (nicknames after «=» and in brackets), not just the first word;
#   (b) mother names matched with pet-form tolerance (עיפה~עיפאת ...);
#   (c) a separate duplicate test: a registry person that is the SAME person as a card already on the site (given name + father + birth year) is merged, not added.
import json, io, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
exec(open('scan_registry_certain_20261111.py', encoding='utf-8').read().split('DAN_FAM =')[0])   # reuse nrm / lev / greg / loaders
def toks(seg):
    seg = NIQ.sub('', seg)
    t = seg.split()
    if t and t[0] in ('בן', 'בת'): t = t[2:]
    out = []
    for w in t:
        for u in re.split(r'[,،]', w):
            u = u.strip("׳״\"'`.()[] ")
            if u and u not in ('בן', 'בת'): out.append(u)
    return out
def names_all(name):
    out = set()
    for seg in re.split(r'=|\(|\)', str(name or '')):
        seg = re.split(r' ב[ןת] ', ' ' + seg + ' ')[0].strip()
        for w in toks(seg) if not seg.startswith(('בן ', 'בת ')) else toks(seg):
            out.add(w)
    for seg in re.split(r'=|\(|\)', str(name or '')):                # parenthetical «בן X, כינוי»
        seg = seg.strip()
        if seg.startswith(('בן ', 'בת ')):
            for w in toks(seg): out.add(w)
    return {w for w in out if len(nrm(w)) >= 2}
def same2(a, b, lenient=False):
    a, b = nrm(a), nrm(b)
    if not a or not b: return False
    if a == b: return True
    if same(a, b): return True
    sk0 = lambda t: re.sub('[ויאה]', '', t)
    if len(sk0(a)) >= 3 and sk0(a) == sk0(b): return True
    if lenient:
        sk = lambda t: re.sub('[ויאה]', '', t)
        if len(sk(a)) >= 3 and sk(a) == sk(b): return True
        if min(len(a), len(b)) >= 3 and lev(a, b) <= 1: return True
    if lenient and len(a.rstrip('האת')) >= 3 and a.rstrip('האת') == b.rstrip('האת'): return True
    if lenient and min(len(a), len(b)) >= 3 and (a.startswith(b) or b.startswith(a)) and abs(len(a) - len(b)) <= 2: return True   # עיפה ~ עיפאת
    return False
def wives_all(p):
    out = set()
    for s in p.get('spouses') or []:
        out |= names_all(s['name'])
    n = p.get('notes') or ''
    for mm in re.finditer(r'נישא(?:ה)?(?: פעמיים)? ל(?:ה)?([^,;]+?)(?: בן | בת |$)', n):
        out |= names_all(mm.group(1))
    return out

DAN_FAM = {'דינפי', 'סראוי'}
onsite = {m['id']: m for m in integ['modern']}
MERGED = set(json.load(io.open('registry_merged_20261109.json', encoding='utf-8')).keys())
for d in json.load(io.open('merge_decisions.json', encoding='utf-8')).get('merges', []): MERGED.add(d.get('away'))
for p in P.values():
    for a in p.get('alt_ids') or []: MERGED.add(a)
absent = {i: m for i, m in arch.items() if i not in onsite and m.get('family') in DAN_FAM and not str(i).startswith('F') and i not in MERGED}
POOL = {i: m for i, m in arch.items() if m.get('family') in DAN_FAM or i in onsite}; POOL.update(onsite)

def father_of(x):
    return x.get('father')
def census_cands(x, need_wife=True):
    fn, mn, by = x.get('father'), x.get('mother'), x.get('byear'); out = []
    if not by or not fn: return out
    for i, p in P.items():
        if not H[i].startswith('ב.') or p.get('sex') != 'M': continue
        if not any(same2(fn, g) for g in names_all(p['name'])): continue
        b, d = greg(p.get('birth')), greg(p.get('death'))
        if b and not (16 <= by - b <= 70): continue
        if d and by > d + 1: continue
        if (not need_wife) or any(same2(mn, w, True) for w in wives_all(p)): out.append((i, 'census'))
    return out
def modern_cands(x, need_wife=True):
    fn, mn, by = x.get('father'), x.get('mother'), x.get('byear'); out = []
    if not by or not fn: return out
    for i, m in POOL.items():
        if i == x.get('id') or m.get('sex') != 'M' or not m.get('byear'): continue
        if not any(same2(fn, g) for g in names_all(m['name'])): continue
        if not (16 <= by - m['byear'] <= 70): continue
        if m.get('dyear') and by > int(m['dyear']) + 1: continue
        if (not need_wife) or any(same2(mn, w, True) for w in wives_all(m)): out.append((i, 'modern'))
    return out

# ---- duplicates of cards already on the site (census persons): same given name, same father name, birth within 3 years
def dup_of(x):
    by = x.get('byear'); out = []
    if not by: return out
    for i, p in P.items():
        if {'ז': 'M', 'נ': 'F'}.get(p.get('sex'), p.get('sex')) != x.get('sex') or not H[i].startswith('ב.'): continue
        b = greg(p.get('birth'))
        if not b or abs(b - by) > 3: continue
        if not any(same2(given(x['name']), g, True) for g in names_all(p['name'])): continue
        # father's name on the card
        f = P.get(p.get('father_id'))
        if f and any(same2(x.get('father'), g) for g in names_all(f['name'])): out.append(i)
    return out
dups = {k: dup_of(x) for k, x in absent.items()}
dups = {k: v for k, v in dups.items() if v}

certain = {}
changed = True; rounds = 0
rest = {k: x for k, x in absent.items() if k not in dups}
while changed and rounds < 8:
    changed = False; rounds += 1
    for rid, x in sorted(rest.items(), key=lambda kv: kv[1].get('byear') or 0):
        if rid in certain: continue
        c = census_cands(x) + modern_cands(x)
        c = [y for y in c if y[1] == 'census' or y[0] in onsite or y[0] in certain]
        # a candidate that is itself an on-site duplicate/other absent person unresolved is excluded (not yet certain)
        if len(c) == 1:
            certain[rid] = c[0]; POOL[rid] = {**x, 'id': rid}; changed = True
res = {'dups': dups, 'certain': {k: {'father': v[0], 'kind': v[1]} for k, v in certain.items()}}
io.open('registry_certain_scan2_20261111.json', 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=1))
print('absent', len(absent), '| duplicates', len(dups), '| certain', len(certain), '| rounds', rounds)
print('\nDUPLICATES (registry person == card on the site):')
for k, v in dups.items(): print(' ', k, arch[k]['name'], arch[k].get('byear'), 'F', arch[k].get('father'), 'M', arch[k].get('mother'), '==', [(i, P[i]['name'], greg(P[i].get('birth'))) for i in v])
print('\nCERTAIN (new):')
for k, v in certain.items():
    x = arch[k]; fa = (P.get(v[0]) or arch.get(v[0]) or {}).get('name')
    print(' ', k, x['name'], x.get('byear'), 'F', x.get('father'), 'M', x.get('mother'), '->', v[0], fa, '|', (x.get('notes') or '')[:40])
