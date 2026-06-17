# -*- coding: utf-8 -*-
# Fills the missing bridge-generation people of the Marhibi house from the
# transcripts page_94 / page_95 (prefer the transcript over the registry).
import json, io

master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
allp = {p['id']: (p, f) for h in master['houses'] for f in h['families'] for p in f['persons']}

def fam_of(pid): return allp[pid][1] if pid in allp else None
def P(pid, name, sex, father, gy, t, fam, children=None):
    p = {"id": pid, "name": name, "sex": sex}
    if father: p["father_id"] = father
    if children: p["children_ids"] = children
    fam['persons'].append(p)
    if t or gy: stories[pid] = {"t": t, "g": gy}
def addchild(pid, cid):
    if pid in allp:
        par = allp[pid][0]; par.setdefault('children_ids', [])
        if cid not in par['children_ids']: par['children_ids'].append(cid)

# remove previously-added
for h in master['houses']:
    for f in h['families']:
        f['persons'] = [p for p in f['persons'] if not str(p['id']).startswith('מר-')]

fam2 = next(f for h in master['houses'] for f in h['families'] if f['family'] == 'משפחת מרחיב המרחיבי')   # #192-202
fam1 = next(f for h in master['houses'] for f in h['families'] if f['family'] == 'משפחת יהושע המרחיבי')    # #164-190א

# --- family 2: #202 סעד (סֻעֻאד, מת 1868) — בניו (page_95) ---
addchild('202', 'מר-אברהם202')
P('מר-אברהם202', 'אברהם (בן סעד)', 'M', '202', '1846–1902',
  'בנו בכורו של סעד. סופר ומעתיק בכתב יפה; פקיד אצל סוחרי שכם. נשא את סעדה ("אלטרמה") בת מרחיב, ואחריה את זפֿיקה בת בנימים המטרי.', fam2,
  children=['מר-זבולן'])
P('מר-זבולן', 'זבולן (פיאד)', 'M', 'מר-אברהם202', '1886–1967',
  'בן אברהם. נגר; חי בשכם ועבר לחולון; מעריץ הכה"ג מצליח בן פינחס. נשא ב-1919 את פהֶימה בת צפר המרחיבי.', fam2)
addchild('202', 'מר-יעקב202'); addchild('202', 'מר-ברור202'); addchild('202', 'מר-סעוד202')
P('מר-יעקב202', 'יעקב (בן סעד)', 'M', '202', '', 'בן סעד (מאשתו אלפֻלֻה).', fam2)
P('מר-ברור202', 'ברור (בן סעד)', 'M', '202', '', 'בן סעד (מאשתו סעֻדֶה בת יהושע).', fam2)
P('מר-סעוד202', 'סֻעֻד (בן סעד)', 'M', '202', '1868–1919',
  'בן סעד; נקרא כך כי נולד אחרי מות אביו.', fam2)

# --- family 1 (יהושעי): #184 צפר -> אברהם 1886 ---
# NOTE: קמרה (1870–1950) is ALREADY census #183 (its father was the uncertain "179?").
# The transcript (page_94) makes her the daughter of חובב #180, so we fix #183's broken
# father link to #180 and enrich it — instead of adding a duplicate (was מר-קמרה180).
if '183' in allp:
    k183 = allp['183'][0]
    k183['father_id'] = '180'
    addchild('180', '183')
    stories['183'] = {'t': 'בת חובב. נישאה לאפרים בן שת המרחיבי.', 'g': '1870–1950'}
addchild('184', 'מר-אברהם184')
P('מר-אברהם184', 'אברהם המרחיבי', 'M', '184', '1886–1967', 'בן צפר.', fam1)

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
print('added Marhibi bridge people:', sum(1 for h in master['houses'] for f in h['families'] for p in f['persons'] if str(p['id']).startswith('מר-')))
