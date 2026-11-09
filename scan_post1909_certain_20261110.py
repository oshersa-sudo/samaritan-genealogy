# -*- coding: utf-8 -*-
# 2026-11-10 — which absent registry persons of the Danfim families can be attached with certainty?
# certain = exactly ONE candidate father (census person on the site, or a registry person already on the site / certain in an earlier round)
#   whose given name matches (spelling-tolerant: final letters, double yod, ±1 letter), who is old enough (16–70) and alive, and whose WIFE's given
#   name matches the child's mother (census: spouses; registry: spouses / the note «נישא ל…»).  Closure: children of a newly certain father are tried next.
import json, io, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))
arch = {m['id']: m for m in json.load(io.open('excel_layer_archive.json', encoding='utf-8'))['modern']}
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
H = {p['id']: h['house'] for h in master['houses'] for f in h['families'] for p in f['persons']}
NIQ = re.compile('[֑-ׇ]')
FIN = str.maketrans('ךםןףץ', 'כמנפצ')
ALIAS = {'אסעד': 'סעד', 'זבולון': 'זבולן', 'ג׳מיל': 'גמיל', "ג'מיל": 'גמיל', 'גמיל': 'גמיל', 'רג׳א': 'רגא', "רג'א": 'רגא', "רג'ה": 'רגא', 'רגה': 'רגא', 'מוניר': 'מנגיר', 'מונגיר': 'מנגיר'}


def nrm(s):
    s = NIQ.sub('', str(s or '')); s = re.sub(r"[׳״\"'`.,/\()\[\]\-]", '', s).strip().translate(FIN)
    s = s.replace('יי', 'י').replace('וו', 'ו')
    return ALIAS.get(s, s)


def lev(a, b):
    if a == b: return 0
    if abs(len(a) - len(b)) > 1: return 2
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1): cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def same(a, b):
    a, b = nrm(a), nrm(b)
    if not a or not b: return False
    if a == b: return True
    a2, b2 = a.rstrip('הא'), b.rstrip('הא')
    if a2 and a2 == b2: return True
    return min(len(a), len(b)) >= 4 and lev(a, b) <= 1


def given(s):
    s = re.sub(r'\s*[\(（].*$', '', str(s or '')); s = re.sub(r'\s*=.*$', '', s)
    s = s.split(' בת ')[0].split(' בן ')[0]
    return s.split()[0] if s.split() else ''


def names_of(name):
    out = set()
    for t in re.split(r'=|\(|\)', str(name or '')):
        g = given(t)
        if g: out.add(g)
    return out


def greg(h): return round(h / 1.030684 + 621.57) if isinstance(h, int) else None


def wives_of_census(p):
    return [given(s['name']) for s in p.get('spouses') or []]


def wives_of_modern(m):
    w = [given(s['name']) for s in m.get('spouses') or []]
    n = m.get('notes') or ''
    mm = re.search(r'נישא(?:ה)? ל(?:ה)?(.+?)(?: בן | בת |$)', n)
    if mm: w.append(given(mm.group(1).strip()))
    return w


DAN_FAM = {'דינפי', 'דנפי', 'סראוי', 'אלטיף', 'לוטפי', 'משלמה', 'שלבי', 'הסתרי', 'שלבי'}
onsite = {m['id']: m for m in integ['modern']}
cand_modern = dict(onsite)           # grows by closure
certain = {}                         # rid -> (father id, evidence)
absent = {i: m for i, m in arch.items() if i not in onsite and (m.get('family') in DAN_FAM) and m.get('father') and not str(i).startswith('F')}


def candidates(x):
    fn, mn, by = x.get('father'), x.get('mother'), x.get('byear')
    if not by: return []
    out = []
    for i, p in P.items():
        if not H[i].startswith('ב.') or p.get('sex') != 'M': continue
        if not any(same(fn, g) for g in names_of(p['name'])): continue
        b, d = greg(p.get('birth')), greg(p.get('death'))
        if b and not (16 <= by - b <= 70): continue
        if d and by > d + 1: continue
        if any(same(mn, w) for w in wives_of_census(p)): out.append((i, 'census'))
    for i, m in POOL.items():
        if i == x.get('id'): continue
        if m.get('sex') != 'M' or not m.get('byear'): continue
        if not any(same(fn, g) for g in names_of(m['name'])): continue
        if not (16 <= by - m['byear'] <= 70): continue
        if m.get('dyear') and by > int(m['dyear']) + 1: continue
        if any(same(mn, w) for w in wives_of_modern(m)): out.append((i, 'modern'))
    return out


POOL = {i: m for i, m in arch.items() if m.get('family') in DAN_FAM or i in onsite}
POOL.update(onsite)
MERGED = set(json.load(io.open('registry_merged_20261109.json', encoding='utf-8')).keys())
for d in json.load(io.open('merge_decisions.json', encoding='utf-8')).get('merges', []): MERGED.add(d.get('away'))
for p in P.values():
    for a in p.get('alt_ids') or []: MERGED.add(a)
absent = {k: v for k, v in absent.items() if k not in MERGED}
changed = True
rounds = 0
while changed and rounds < 6:
    changed = False; rounds += 1
    for rid, x in sorted(absent.items(), key=lambda kv: kv[1].get('byear') or 0):
        if rid in certain: continue
        c = candidates(x)
        if len(c) == 1 and (c[0][1] == 'census' or c[0][0] in onsite or c[0][0] in certain):
            certain[rid] = c[0]; cand_modern[rid] = {**x, 'id': rid}; changed = True
res = {'certain': {k: {'father': v[0], 'kind': v[1], 'name': arch[k]['name'], 'by': arch[k].get('byear'), 'F': arch[k].get('father'), 'M': arch[k].get('mother')} for k, v in certain.items()},
       'uncertain': [k for k in absent if k not in certain]}
io.open('post1909_certain_scan_20261110.json', 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=1))
print('absent Danfim-family registry persons:', len(absent), '| certain:', len(certain), '| remaining:', len(absent) - len(certain), '| rounds', rounds)
byfather = collections.defaultdict(list)
for k, v in certain.items(): byfather[v[0]].append(arch[k]['name'] + ' (' + str(arch[k].get('byear')) + ')')
for f, ks in byfather.items(): print(f, (P.get(f) or {}).get('name') or (cand_modern.get(f) or {}).get('name'), '->', ', '.join(ks))

# ---- duplicates: a certain person whose father already has an on-site child of the same name and a close birth year
def onsite_children(fid):
    out = []
    if fid in P:
        for c in P[fid].get('children_ids') or []:
            q = P.get(c)
            if q: out.append((c, q['name'], greg(q.get('birth'))))
    for i, m in integ['modern']:
        pass
    return out
kids = collections.defaultdict(list)
for m in integ['modern']:
    par = (m.get('parent') or '').lstrip('#')
    kids[par].append((m['id'], m['name'], m.get('byear')))
for fid, p in P.items():
    for c in p.get('children_ids') or []:
        q = P.get(c)
        if q: kids[fid].append((c, q['name'], greg(q.get('birth'))))
dups, fresh = {}, {}
for rid, (fid, kind) in certain.items():
    x = arch[rid]; hit = None
    for cid, cn, cb in kids.get(fid, []):
        if any(same(given(x['name']), g) for g in names_of(cn)) and (cb is None or abs((cb or 0) - x['byear']) <= 9): hit = cid; break
    (dups if hit else fresh)[rid] = hit or fid
print('\nduplicates of persons already on the site:', len(dups))
for rid, cid in dups.items(): print('  ', rid, arch[rid]['name'], arch[rid].get('byear'), '== on-site', cid)
print('\nfresh certain:', len(fresh))
for rid, fid in fresh.items(): print('  ', rid, arch[rid]['name'], arch[rid].get('byear'), '| F', arch[rid].get('father'), '| M', arch[rid].get('mother'), '| parent', fid, '|', (arch[rid].get('notes') or '')[:40])
io.open('post1909_certain_scan_20261110.json', 'w', encoding='utf-8').write(json.dumps({'dups': dups, 'fresh': fresh}, ensure_ascii=False, indent=1))
