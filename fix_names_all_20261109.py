# -*- coding: utf-8 -*-
# 2026-11-09 — owner: «כל אישיות בן/בת <אב>, ללא יוצא מן הכלל» — also the older census cards that carry a bracket (nickname / alias / note) but no father.
# The father's given name (first word of the ACTUAL linked father, brackets stripped — same rule as the page's displayName) goes first INSIDE the bracket:
#   «אסעד (סעד)» → «אסעד (בן אבּ-ספֿוה, סעד)»;  an alias mark «(=פרג')» becomes «(בן X, פרג')».
# Names that already say בן/בת (anywhere) are left alone. Idempotent. Log: names_all_20261109.json
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
LOG = []; SKIP = []
# three cards the rule could not reach: a stub name «פריזה (בת)», and two with no recorded sex (the source note says «בת אחת שמתה» / «ילד של סעד»)
if P['צפ-פריזה']['name'] == 'פריזה (בת)': P['צפ-פריזה']['name'] = 'פריזה (בת יעקב)'; LOG.append({'id': 'צפ-פריזה', 'from': 'פריזה (בת)', 'to': 'פריזה (בת יעקב)'})
if not P['182'].get('sex'): P['182']['sex'] = 'F'; LOG.append({'id': '182', 'sex': 'F', 'why': 'הערת המקור: «בת אחת שמתה»'})
if not P['דנ-אלקוע101'].get('sex'): P['דנ-אלקוע101']['sex'] = 'M'; LOG.append({'id': 'דנ-אלקוע101', 'sex': 'M', 'why': 'הערת המקור: «ילד של סעד»'})


def given(name):
    n = re.sub(r'\s*[\(（].*$', '', name or '').strip()
    return n.split()[0] if n.split() else ''


for p in P.values():
    n = p['name']
    if not re.search(r'[\(（]', n) or re.search(r'ב[ןת](\s|\)|,|$)', n): continue
    f = P.get(p.get('father_id'))
    fg = given(f['name']) if f else ''
    if not fg or p.get('sex') not in ('M', 'F'): SKIP.append({'id': p['id'], 'name': n, 'father': p.get('father_id'), 'sex': p.get('sex')}); continue
    rel = 'בת' if p['sex'] == 'F' else 'בן'
    new = re.sub(r'[\(（]\s*=?\s*', '(%s %s, ' % (rel, fg), n, count=1)
    new = re.sub(r', ?\)', ')', new)
    LOG.append({'id': p['id'], 'from': n, 'to': new}); p['name'] = new
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('names_all_20261109.json', 'w', encoding='utf-8').write(json.dumps({'changed': LOG, 'skipped': SKIP}, ensure_ascii=False, indent=1))
print(len(LOG), 'renamed;', len(SKIP), 'skipped')
for x in LOG: print(x)
for x in SKIP: print('SKIP', x)
