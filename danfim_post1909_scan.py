# -*- coding: utf-8 -*-
# analysis only (nothing is changed): registry persons born after 1909 in Danfim families, not yet on the site, whose father (a census person)
# is identified with certainty: exactly ONE census Danfim man of that given name, old enough and alive, has a wife with the registry mother's given name.
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
a = json.load(io.open('excel_layer_archive.json', encoding='utf-8'))['modern']; A = {x['id']: x for x in a}
cur = {m['id'] for m in json.load(io.open('integrate.json', encoding='utf-8'))['modern']}
m = json.load(io.open('master_v2.json', encoding='utf-8'))
P = {}; H = {}
for h in m['houses']:
    for f in h['families']:
        for p in f['persons']: P[p['id']] = p; H[p['id']] = h['house']
NIQ = ''.join(chr(c) for c in range(0x0591, 0x05C8))
PUNCT = re.compile(r"[׳״\"'`.,/\\=()\[\]-]")


def n(s):
    s = ''.join(ch for ch in str(s or '') if ch not in NIQ)
    s = PUNCT.sub(' ', s); s = re.sub(r'\s+', ' ', s).strip()
    return s.translate(str.maketrans('ךםןףץ', 'כמנפצ'))


def given(s):
    s = re.sub(r'\s*[\(（].*$', '', str(s or '')).split(' בת ')[0].split(' בן ')[0]
    s = re.sub(r'\s*=.*$', '', s)
    return n(s)


def names_of(p):
    return {given(t) for t in re.split(r'=', re.sub(r'\(.*?\)', '', p['name']))} | {given(p['name'])}


def greg(h): return round(h / 1.030684 + 621.57) if isinstance(h, int) else None


danf = [i for i in P if H[i].startswith('ב.')]


def candidates(x):
    fn = given(x.get('father')); mn = given(x.get('mother')); by = x['byear']
    out = []
    for i in danf:
        p = P[i]
        if p.get('sex') != 'M' or fn not in names_of(p): continue
        b = greg(p.get('birth')); d = greg(p.get('death'))
        if b and by - b < 16: continue
        if d and by > d + 1: continue
        wives = [given(s['name']) for s in p.get('spouses') or []]
        out.append((i, wives, mn in wives))
    return out


if __name__ == '__main__':
    rows = []
    for x in a:
        if x['id'] in cur or not x['byear'] or x['byear'] < 1909: continue
        if x.get('family') not in ('סראוי', 'דינפי', 'דנפי', 'אלטיף', 'לוטפי', 'משלמה', 'שלבי', 'הסתרי'): continue
        c = candidates(x); ok = [i for i, w, mm in c if mm]
        rows.append((x, c, ok))
    one = [r for r in rows if len(r[2]) == 1]
    print('post-1909 registry persons in Danfim families, not on site:', len(rows), '| exactly one census father with a wife of the mother\'s name:', len(one))
    for x, c, ok in one:
        print(x['id'], x['name'], x['byear'], '|F', x.get('father'), 'M', x.get('mother'), '|plan-parent', x['parent'], '-> census', ok[0], P[ok[0]]['name'][:16], '| other same-name men', len(c) - 1)
