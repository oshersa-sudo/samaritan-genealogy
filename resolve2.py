# -*- coding: utf-8 -*-
import json, io, re
from collections import Counter, defaultdict

NIQQUD = ''.join(chr(c) for c in range(0x0591, 0x05C8))
FINAL = {'ם': 'מ', 'ן': 'נ', 'ץ': 'צ', 'ף': 'פ', 'ך': 'כ'}

def sn(s):
    return ''.join(ch for ch in str(s or '') if ch not in NIQQUD)

def basic(s):
    s = sn(s)
    s = re.sub(r'[׳״"\'`./\\\-]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def loose(s):
    # drop the weak/mater letters א/ו/י so spelling variants collapse
    # (e.g. אסעד == סעד, which the source uses interchangeably)
    s = basic(s)
    s = ''.join(FINAL.get(c, c) for c in s)
    return s.replace('ו', '').replace('י', '').replace('א', '').replace(' ', '')

def variants(s):
    vs = set()
    for part in re.split(r'[=()]', sn(s)):
        b = basic(part)
        if b and len(loose(b)) >= 2:
            vs.add(loose(b))
    return vs

def nmatch(a, b):
    return bool(variants(a) & variants(b))

SKIP = set(['בת', 'בן', 'אל', 'אבו', 'אבּ'])
def given_loose(s):
    b = basic(re.split(r'[=()]', sn(s))[0])
    for t in b.split():
        if t not in SKIP:
            return loose(t)
    return loose(b)

master = json.load(io.open('master_v2.json', encoding='utf-8'))
modern = json.load(io.open('modern_people.json', encoding='utf-8'))

def htag(h):
    for k in ('דנפים', 'מרחיבים', 'צפרים', 'כהונה'):
        if k in h:
            return k
    return 'בודדים'

persons = {}
for h in master['houses']:
    for fam in h['families']:
        for p in fam['persons']:
            p['_house'] = htag(h['house'])
            persons[p['id']] = p

def bgreg(p):
    b = p.get('birth')
    return (b + 584) if isinstance(b, int) else None

def cfather(p):
    fid = p.get('father_id')
    return persons[fid]['name'] if (fid and fid in persons) else p.get('father', '')

def cspouses(p):
    return set(given_loose(s.get('name', '')) for s in (p.get('spouses') or []) if s.get('name'))

# Excel family -> census house
FAM2HOUSE = {'דינפי': 'דנפים', 'סראוי': 'דנפים',
             'צדקה': 'צפרים', 'מרחיב': 'מרחיבים',
             'כהן': 'כהונה', 'לוי': 'כהונה'}

for i, mp in enumerate(modern):
    mp['mid'] = 'M%d' % (i + 1)

def myear(mp):
    y = mp.get('byear', '')
    return int(y) if re.match(r'^\d{4}$', y) else None

MARRY = re.compile(r'(?:נשוי|נישא|נישאה|נשואה|נשא|מאורס)\s+ל([^,]+)')
def mspouse(mp):
    n = sn(mp.get('notes', ''))
    m = MARRY.search(n)
    if not m:
        m = re.search(r'\bל([א-ת]{2,})', n)
    return given_loose(m.group(1)) if m else None

mod_by_fam = defaultdict(list)
for mp in modern:
    mod_by_fam[basic(mp['family'])].append(mp)

# overlap identity: same individual already present in the 1909 census
overlap = {}
for mp in modern:
    my = myear(mp)
    if not my or my > 1912:
        continue
    house = FAM2HOUSE.get(basic(mp['family']))
    if not house:
        continue
    cands = [p for p in persons.values() if p['_house'] == house and nmatch(p['name'], mp['name'])
             and (bgreg(p) is None or abs(bgreg(p) - my) <= 9)]
    fm = [p for p in cands if mp['father'] and nmatch(cfather(p), mp['father'])]
    if len(fm) == 1:
        overlap[mp['mid']] = fm[0]['id']

def mid_or_alias(q):
    return ('#' + overlap[q['mid']]) if q['mid'] in overlap else q['mid']

def resolve_parent(mp):
    fa = mp.get('father', '')
    if not fa:
        return (None, 'no-father-name')
    fam = basic(mp['family'])
    house = FAM2HOUSE.get(fam)
    my = myear(mp)
    moth = given_loose(mp.get('mother', ''))
    # a father candidate must be male AND within one generation (12–70y older) — so a
    # modern person is never grafted onto a same-named ANCIENT ancestor.
    def age_ok(g):
        return (not my) or (g is None) or (my - 70 <= g <= my - 12)
    ccand = [p for p in persons.values() if house and p['_house'] == house and nmatch(p['name'], fa)
             and p.get('sex') != 'F' and age_ok(bgreg(p))]
    mcand = [q for q in mod_by_fam.get(fam, []) if q is not mp and nmatch(q['name'], fa)
             and not basic(q.get('sex', '')).startswith('נ') and age_ok(myear(q))]
    if moth and len(ccand) > 1:
        f = [c for c in ccand if moth in cspouses(c)]
        if f:
            ccand = f
    if moth and len(mcand) > 1:
        f = [c for c in mcand if mspouse(c) == moth]
        if f:
            mcand = f
    if len(mcand) == 1 and len(ccand) == 0:
        return (mid_or_alias(mcand[0]), 'modern')
    if len(ccand) == 1 and len(mcand) == 0:
        return ('#' + ccand[0]['id'], 'census')
    if len(mcand) == 1 and len(ccand) == 1:
        return (mid_or_alias(mcand[0]), 'modern>census')
    if len(mcand) + len(ccand) == 0:
        return (None, 'root-no-candidate')
    return (None, 'ambiguous')

res = Counter()
for mp in modern:
    if mp['mid'] in overlap:
        mp['_parent'] = None
        mp['_why'] = 'overlap'
        res['overlap'] += 1
        continue
    pid, why = resolve_parent(mp)
    mp['_parent'] = pid
    mp['_why'] = why
    res[why] += 1

mid2mp = {mp['mid']: mp for mp in modern}
# Include EVERY person in a mapped family (not priestly, not an overlap duplicate).
# Use the confident parent where we found one; otherwise attach the branch root under
# its house node (@H:<tag>) — a certain family-level link, never a guessed parent.
final = []
for mp in modern:
    if mp['mid'] in overlap:
        continue
    tag = FAM2HOUSE.get(basic(mp['family']))
    if not tag:
        continue
    par = mp.get('_parent')
    mp['_finalparent'] = par if par else ('@H:' + tag)
    final.append(mp)

# Group floating sibling-sets (same father+mother+family, attached at house level)
# under a reconstructed father node, so each branch shows under its named father
# instead of many disconnected leaves. The father node grafts to a census/spine
# person of the same house if his name matches uniquely, else sits under the house.
import collections as _c
def _sibkey(m): return (given_loose(m.get('father', '')), given_loose(m.get('mother', '')), basic(m['family']))
_groups = _c.OrderedDict()
for mp in final:
    if mp['_finalparent'].startswith('@H') and given_loose(mp.get('father', '')):
        _groups.setdefault(_sibkey(mp), []).append(mp)
def _name_tokens(nm):
    return set(loose(t) for t in basic(nm).split() if loose(t))
def _name_has(nm, fa):
    # father-name matches a candidate whose display name CONTAINS it as a token
    # (e.g. children of "שוהם" whose real father is the modern "מורגן שוהם")
    return (loose(fa) in _name_tokens(nm)) or nmatch(nm, fa)

synth_people = []
_si = 0
for key, members in _groups.items():
    fa = members[0]['father']; fam = members[0]['family']; tag = FAM2HOUSE.get(basic(fam))
    if not tag:
        continue
    # estimate the father's birth (~30y before his oldest child) so we never identify
    # him with a same-named ANCIENT census ancestor
    _cy = [myear(m) for m in members if myear(m)]
    _est = (min(_cy) - 30) if _cy else None
    # (a) PREFER an already-resolved MODERN person whose name matches the father —
    # link the children directly to him instead of inventing a synthetic node.
    mf = [q for q in final if q not in members and FAM2HOUSE.get(basic(q['family'])) == tag
          and not basic(q.get('sex', '')).startswith('נ') and _name_has(q['name'], fa)
          and (_est is None or myear(q) is None or abs(myear(q) - _est) <= 35)]
    if len(mf) == 1:
        for mp in members:
            mp['_finalparent'] = mf[0]['mid']
        continue
    # (b) else reconstruct a synthetic father node grouping the siblings
    _si += 1; fid = 'F%d' % _si
    fcand = [p for p in persons.values() if p['_house'] == tag and nmatch(p['name'], fa) and p.get('sex') != 'F'
             and (_est is None or bgreg(p) is None or abs(bgreg(p) - _est) <= 35)]
    fparent = ('#' + fcand[0]['id']) if len(fcand) == 1 else ('@H:' + tag)
    synth_people.append({'id': fid, 'name': fa, 'family': fam, 'parent': fparent, 'sex': 'M',
                         'g': '', 'father': None, 'mother': None,
                         'note': 'אב משוחזר מקבוצת-אחים במרשם (' + str(len(members)) + ' ילדים)'})
    for mp in members:
        mp['_finalparent'] = fid

def sexMF(s):
    s = basic(s)
    return 'M' if s.startswith('ז') else ('F' if s.startswith('נ') else None)

def gstr(mp):
    by = myear(mp)
    dy = mp.get('dyear', '')
    dy = int(dy) if re.match(r'^\d{4}$', dy or '') else None
    if by and dy:
        return '%d–%d' % (by, dy)
    if by:
        return '%d' % by
    return ''

# Manual overrides — user-confirmed corrections that name-matching cannot infer.
# אלעד (M582) is NOT the son of M301 (אברהם בן חיכמת); float him under his house
# (uncertain father) instead of making a wrong link. (user-confirmed, 2026-06)
MANUAL_FLOAT = {'M582'}
for mp in final:
    if mp['mid'] in MANUAL_FLOAT:
        mp['_finalparent'] = '@H:' + (FAM2HOUSE.get(basic(mp['family'])) or 'דנפים')

out_people = []
for mp in final:
    out_people.append(dict(id=mp['mid'], name=mp['name'], sex=sexMF(mp['sex']), parent=mp['_finalparent'],
        g=gstr(mp), byear=myear(mp), bmonth=mp.get('bmonth'), bday=mp.get('bday'),
        dyear=mp.get('dyear') or None, age=mp.get('age') or None, family=mp['family'],
        father=mp.get('father') or None,
        job=mp.get('job') or None, bplace=mp.get('bplace') or None, mother=mp.get('mother') or None,
        notes=mp.get('notes') or None))
# reconstructed father nodes
for s in synth_people:
    out_people.append(dict(id=s['id'], name=s['name'], sex='M', parent=s['parent'],
        g='', byear=None, bmonth=None, bday=None, dyear=None, age=None, family=s['family'],
        father=None, job=None, bplace=None, mother=None, notes=s['note'], synth=True))

ovl_en = []
for mid, cidv in overlap.items():
    mp = mid2mp[mid]
    ovl_en.append(dict(cid=cidv, byear=myear(mp), bmonth=mp.get('bmonth'), bday=mp.get('bday'),
        dyear=mp.get('dyear') or None, age=mp.get('age') or None, g=gstr(mp)))

json.dump(dict(modern=out_people, overlap=ovl_en),
          io.open('integrate.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

out = io.open('resolve2_report.txt', 'w', encoding='utf-8')
out.write('resolution: %s\n' % json.dumps(dict(res), ensure_ascii=False))
out.write('overlap (merge into census): %d\n' % len(overlap))
out.write('final modern nodes added: %d\n' % len(final))
gc = sum(1 for m in final if m['_finalparent'].startswith('#'))
mc = sum(1 for m in final if m['_finalparent'].startswith('M'))
hc = sum(1 for m in final if m['_finalparent'].startswith('@H'))
out.write('  -> onto census: %d ; under modern: %d ; under house (uncertain graft): %d\n' % (gc, mc, hc))
out.write('tree total after merge: %d\n' % (193 + len(final)))
out.close()
print('final', len(final), 'overlap', len(overlap), 'res', dict(res))
