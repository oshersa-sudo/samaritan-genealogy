# -*- coding: utf-8 -*-
# 2026-11-08 — two open points of the page-87 work, fixed by the standing rules (one unambiguous ID per person):
#   A. the eleven persons #150–#160 (children / grandchildren of סעד בן ישמעאל) were entered with working ids «הס-…».  The census gives each of them
#      its printed number (p.86), so the id becomes that number (and, by the standing rule, the numeric ID `uid` equals it).  Every reference
#      (father_id, children_ids, mother_id, spouse links «#id», stories, registry persons' parent) is rewritten; the old ids stay reserved in uid_registry.json.
#      Missing birth years are filled from the census list (p.86).
#   B. «אברהם בן מרחיב הצפרי» — husband of קמרה #160 — was in the data twice: #214 (family list of the Tsfari house of מרחיב, p.96, with his 8 children)
#      and #254 (the appendix «שמות שומרונים שלא נמצאו בגיניאולוגיה», p.101: «אברהם הצפרי ביפו, נולד 1272, נשא את קמרה (160)»).
#      Same birth year, same wife; and the wife's own entry (p.86) cites him as #254.  #254 is merged into #214 (archived in merged_persons_20261108.json,
#      uid 254 stays reserved; `alt_ids:["254"]` on #214 so that a search for 254 finds him).
# Idempotent; log in ids_150_160_fixed_20261108.json
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
RENAME = {'הס-סעד': '150', 'הס-אבספוה': '151', 'הס-סעדיה': '152', 'הס-רסמיה': '153', 'הס-אסעד': '154', 'הס-עבדהרחום': '155',
          'הס-נבון': '156', 'הס-לגזה': '157', 'הס-וגיה': '158', 'הס-צער': '159', 'הס-קמרה': '160'}
BIRTH = {'150': 1240, '156': 1318, '157': 1320, '158': 1323, '159': 1326, '160': 1276}      # census list, p.86
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))
LOG = []
ALT = '|'.join(sorted(map(re.escape, RENAME), key=len, reverse=True))
NOTE_RX = re.compile(r'#\s*(' + ALT + r')(?![א-ת0-9\-])')


def fixstr(s):
    if s in RENAME:
        return RENAME[s]
    return NOTE_RX.sub(lambda m: '#' + RENAME[m.group(1)], s)


def walk(o):
    if isinstance(o, str):
        return fixstr(o)
    if isinstance(o, list):
        return [walk(x) for x in o]
    if isinstance(o, dict):
        return {fixstr(k): walk(v) for k, v in o.items()}
    return o


before = json.dumps(master, ensure_ascii=False)
master = walk(master); stories = walk(stories); integ = walk(integ)
n = sum(1 for k in RENAME if k in before)
if n: LOG.append({'renamed_ids': RENAME})
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
H = {p['id']: (h, f) for h in master['houses'] for f in h['families'] for p in f['persons']}
for k, v in BIRTH.items():
    if not P[k].get('birth'):
        P[k]['birth'] = v; LOG.append({'birth_filled': k, 'birth': v})
for k in RENAME.values():
    t = 'מספר המפקד: #%s (עמ׳ 86).' % k
    if t not in (P[k].get('note') or ''):
        P[k]['note'] = ((P[k].get('note') or '') + ' ' + t).strip()
# the wife's record: the husband is #214 (the census also lists him as #254)
for s in P['160'].get('spouses') or []:
    if s.get('ref') == '214':
        s['name'] = 'אברהם בן מרחיב הצפרי'
        s['note'] = '= אדם #214; בעמ׳ 86 הוא רשום כ-#254 (נספר פעמיים במפקד — אוחד ל-#214)'

# ---------------------------------------------------------------- B. merge #254 into #214
arch_f = 'merged_persons_20261108.json'
try:
    ARCH = json.load(io.open(arch_f, encoding='utf-8'))
except Exception:
    ARCH = []
if '254' in P:
    old = P['254']; keep = P['214']
    h, f = H['254']
    f['persons'].remove(old)
    ARCH.append({'merged_into': '214', 'person': old, 'uid': 254,
                 'why': 'אותו אדם: אברהם בן 1272 הנשוי לקמרה #160 (ברשומת קמרה עמ׳ 86 הוא רשום כ-#254; ברשימת משפחת מרחיב הצפרי, עמ׳ 96, הוא #214 עם 8 ילדיו). #254 הוא הערך ברשימת הבודדים, עמ׳ 101: «אברהם הצפרי ביפו, נולד 1272, נשא את קמרה (160)».'})
    del P['254']
    LOG.append({'merged': '254', 'into': '214'})
keep = P['214']
keep['alt_ids'] = ['254']
t = ('ברשימת הבודדים (עמ׳ 101) הוא נספר שוב כ-#254 («אברהם הצפרי ביפו», נולד 1272, אשתו קמרה #160) — אותו אדם; '
     'ברשומת אשתו (עמ׳ 86) הוא רשום כ-#254. הרשומה #254 אוחדה לכאן.')
if t not in (keep.get('note') or ''):
    keep['note'] = ((keep.get('note') or '') + ' ' + t).strip()
src = keep.get('src') or ''
io.open(arch_f, 'w', encoding='utf-8').write(json.dumps(ARCH, ensure_ascii=False, indent=1))
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('ids_150_160_fixed_20261108.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
for e in LOG: print(e)

# keep the other scripts consistent with the new ids (token-bounded)
for fn in ('fix_hasatri_p87_20261107.py', 'derive_mothers_20261106.py', 'build_sources.py'):
    s = io.open(fn, encoding='utf-8').read()
    s2 = re.sub(r'(' + ALT + r')(?![א-ת0-9\-])', lambda m: RENAME[m.group(1)], s)
    if s2 != s:
        io.open(fn, 'w', encoding='utf-8').write(s2); print('updated', fn)
