# -*- coding: utf-8 -*-
# Cross-checks every TEXT-ADDED person (prefixes הס-/מר-/ר-) against the original
# census persons, to find likely DUPLICATES / mis-placements (same name + overlapping
# birth year), so they can be reconciled.
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))

NIQQUD = ''.join(chr(c) for c in range(0x0591, 0x05C8)); FINAL = {'ם':'מ','ן':'נ','ץ':'צ','ף':'פ','ך':'כ'}
def sn(s): return ''.join(ch for ch in str(s or '') if ch not in NIQQUD)
def basic(s):
    s = sn(s); s = re.sub(r'[׳״"\'`./\\\-]', ' ', s); return re.sub(r'\s+', ' ', s).strip()
def loose(s):
    s = basic(s); s = ''.join(FINAL.get(c, c) for c in s)
    return s.replace('ו','').replace('י','').replace('א','').replace(' ','')
def variants(s):
    return set(loose(b) for b in (basic(p) for p in re.split(r'[=()]', sn(s))) if b and len(loose(b)) >= 2)
def nmatch(a, b): return bool(variants(a) & variants(b))

ADDED = ('הס-', 'מר-', 'ר-')
def is_added(pid): return any(str(pid).startswith(x) for x in ADDED)

def gyear(pid, p):
    g = (stories.get(pid, {}) or {}).get('g', '')
    m = re.match(r'(\d{3,4})', g or '')
    if m: return int(m.group(1))
    b = p.get('birth')
    return (b + 584) if isinstance(b, int) else None

persons = []
for h in master['houses']:
    for f in h['families']:
        for p in f['persons']:
            persons.append((p, f['family']))

added = [(p, fam) for p, fam in persons if is_added(p['id'])]
orig  = [(p, fam) for p, fam in persons if not is_added(p['id'])]

print('Checking %d added vs %d original census persons...\n' % (len(added), len(orig)))
hits = 0
for ap, afam in added:
    ay = gyear(ap['id'], ap)
    for op, ofam in orig:
        if not nmatch(ap['name'], op['name']):
            continue
        oy = gyear(op['id'], op)
        if ay and oy and abs(ay - oy) <= 6:
            hits += 1
            print('DUP?  added %-18s %s (%s) [%s]' % (ap['id'], ap['name'], ay, afam))
            print('      census #%-6s %s (%s) [%s]' % (op['id'], op['name'], oy, ofam))
print('\npotential duplicates:', hits)
