# -*- coding: utf-8 -*-
# 2026-11-11 round 3: father identification with the Arabic events workbook (סגל המאורעות) as the independent witness for the father's patronym.
# A registry person x is certain when: exactly ONE candidate father c (name tokens + age) whose patronym is confirmed by an events BIRTH record
# whose father's given name = x's father, whose mother's given name = x's mother, and whose father's patronym = c's father's name.
import sys, io, json, re, collections
src = open('scan2_registry_20261111.py', encoding='utf-8').read().split("res = {'dups'")[0]
exec(compile(src, 'scan2', 'exec'))
ev = json.load(io.open('events_extracted.json', encoding='utf-8'))
AR2HE = {'ا':'א','أ':'א','إ':'א','آ':'א','ء':'','ب':'ב','ت':'ת','ث':'ת','ج':'ג','ح':'ח','خ':'כ','د':'ד','ذ':'ז','ر':'ר','ز':'ז','س':'ס','ش':'ש','ص':'צ','ض':'צ','ط':'ט','ظ':'ט','ع':'ע','غ':'ע','ف':'פ','ق':'ק','ك':'כ','ل':'ל','م':'מ','ن':'נ','ه':'ה','و':'ו','ي':'י','ى':'י','ة':'ה','ؤ':'ו','ئ':'י'}
def ar2he(s): return ''.join(AR2HE.get(c, c if c.strip() else ' ') for c in re.sub('[ً-ٟ]', '', s or ''))
def loose(w):
    w = nrm(w).replace("'", '').replace('׳', ''); w = re.sub('[ויאהע]', '', w); return re.sub(r'(.)\1+', r'\1', w)
def aw(s):
    t = [w for w in ar2he(re.sub(r'[()\[\]/\_.,،؛]', ' ', s or '')).split() if w not in ('אל', 'הכאהנ', 'כאהנ', 'אלכאהנ')]
    out = []; i = 0
    while i < len(t):
        if t[i] in ('עבד', 'אבו') and i + 1 < len(t): out.append(t[i] + t[i + 1]); i += 2
        else: out.append(t[i]); i += 1
    return out
EVB = []
for e in ev:
    if e.get('event') != 'birth': continue
    f, m = aw(e.get('father')), aw(e.get('mother'))
    if len(f) >= 2 and m: EVB.append((f, m, e))
def father_names(c, kind):
    if kind == 'census': return names_all(P[P[c]['father_id']]['name']) if P[c].get('father_id') in P else set()
    return names_all(POOL[c].get('father') or '') if c in POOL else set()
def evidence(x, c, kind):
    fx, mx = loose(x['father'] or ''), loose(x['mother'] or '')
    pats = {loose(w) for w in father_names(c, kind)}
    hit = []
    for f, m, e in EVB:
        if loose(f[0]) != fx or loose(m[0]) != mx: continue
        if loose(f[1]) in pats and loose(f[1]): hit.append(' '.join(f[:3]) + ' | ' + ' '.join(m[:3]))
    return hit
onsite = {m['id']: m for m in integ['modern']}
exec(src.split('dups = {k: dup_of')[1].split('certain = {}')[0].join(['dups = {k: dup_of', '']) if False else '')
dups2 = {k: dup_of(x) for k, x in absent.items()}; dups2 = {k: v for k, v in dups2.items() if v}
rest = {k: x for k, x in absent.items() if k not in dups2 and k != 'M38'}
certain = {}; why = {}
rounds = 0; changed = True
while changed and rounds < 8:
    changed = False; rounds += 1
    for rid, x in sorted(rest.items(), key=lambda kv: kv[1].get('byear') or 0):
        if rid in certain: continue
        # gate A (round-2 gate): wife on the father's card
        c = [(i, 'census') for i, k in census_cands(x) ] + modern_cands(x)
        c = [y for y in c if y[1] == 'census' or y[0] in onsite or y[0] in certain]
        if len(c) == 1: certain[rid] = c[0]; why[rid] = 'wife-match'; POOL[rid] = {**x, 'id': rid}; changed = True; continue
        # gate B: patronym witnessed in the events workbook
        c2 = census_cands(x, False) + modern_cands(x, False)
        c2 = [y for y in c2 if y[1] == 'census' or y[0] in onsite or y[0] in certain]
        good = [(i, k, evidence(x, i, k)) for i, k in c2]
        good = [g for g in good if g[2]]
        if len(good) == 1 and len({g[0] for g in good}) == 1:
            certain[rid] = (good[0][0], good[0][1]); why[rid] = 'events: ' + good[0][2][0]; POOL[rid] = {**x, 'id': rid}; changed = True
res = {'dups': dups2, 'certain': {k: {'father': v[0], 'kind': v[1], 'why': why[k]} for k, v in certain.items()}}
io.open('registry_certain_scan3_20261111.json', 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=1))
print('absent', len(absent), '| dups', len(dups2), '| certain', len(certain), '| rounds', rounds)
for k, v in certain.items():
    x = arch[k]; fa = (P.get(v[0]) or arch.get(v[0]) or {}).get('name')
    print(k, x['name'], x.get('byear'), 'F', x.get('father'), 'M', x.get('mother'), '->', v[0], '/', fa, '|', why[k][:70])
