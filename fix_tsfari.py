# -*- coding: utf-8 -*-
# Full repair of בית אב הצפרים (משפחת צדקה) from page_96/97/98.
# The intro (page_96) gives the shared root: ישמעאל בן שלח → {יעקב #209, שלמה #239};
# and יעקב #209 → {מרחיב #210, חובב #228, ענבּרה #237, זוהרה #238}.
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
house = next(h for h in master['houses'] if 'הצפרים' in h['house'])
fam1 = next(f for f in house['families'] if f['family'] == 'משפחת מרחיב הצפרי')
allp = {p['id']: p for f in house['families'] for p in f['persons']}

def setname(pid, name):
    if pid in allp: allp[pid]['name'] = name
def setstory(pid, t, g=''):
    stories[pid] = {'t': t, 'g': g}
def setfather(pid, fid):
    if pid not in allp: return
    old = allp[pid].get('father_id')
    if fid is None: allp[pid].pop('father_id', None)
    else: allp[pid]['father_id'] = fid
    if old and old in allp and 'children_ids' in allp[old]:
        allp[old]['children_ids'] = [c for c in allp[old]['children_ids'] if c != pid]
    if fid and fid in allp:
        allp[fid].setdefault('children_ids', [])
        if pid not in allp[fid]['children_ids']: allp[fid]['children_ids'].append(pid)

# idempotent: drop previously-added ancestor + duplicate
for f in house['families']:
    f['persons'] = [p for p in f['persons'] if p['id'] not in ('צפ-ישמעאל', 'ר-סרוריה')]
stories.pop('ר-סרוריה', None)
allp = {p['id']: p for f in house['families'] for p in f['persons']}

# ---- shared ancestor (page_96): ישמעאל בן שלח בן אבּ-זהותה → יעקב#209, שלמה#239 ----
fam1['persons'].insert(0, {"id": "צפ-ישמעאל", "name": "ישמעאל בן שלח (אבּ-זהותה)", "sex": "M",
    "children_ids": ["209", "239"],
    "note": "ישמעאל בן שלח בן אבּ-זהותה הצפרי. בניו יעקב ושלמה הם ראשי משפחת צדקה של ימינו."})
allp = {p['id']: p for f in house['families'] for p in f['persons']}
setfather("209", "צפ-ישמעאל")     # יעקב צדקה
setfather("239", "צפ-ישמעאל")     # שלמה צדקה

# ---- יעקב #209 children: מרחיב#210 (כבר), חובב#228, ענבּרה#237, זוהרה#238 ----
setfather("228", "209")           # חובב — היה שורש נפרד; הוא בן יעקב, אחי מרחיב (page_98)
setstory("228", "בן יעקב, אחי מרחיב. לא ידע קרוא וכתוב; סוחר שירד מנכסיו. נשא את זהרה בת ישראל אלמנעלם.", "1826–1886")
# ענבּרה + זוהרה are daughters of יעקב #209 (sisters of מרחיב/חובב) — were under חובב #228
setfather("237", "209")
setfather("238", "209")
setstory("237", "בת יעקב צדקה (אחות מרחיב וחובב).", '')
setstory("238", "בת יעקב צדקה (אחות מרחיב וחובב).", '')

# ---- #212 סֻדריה = סֻרֻריה (the daughter of #211 יעקב אלעֻפֿאוי); enrich. ----
setname("212", "סֻדריה (סֻרֻריה)")
setstory("212", "בת יעקב אלעֻפֿאוי (מאשתו בהיה בת עבד-חנונה). נישאה לצדקה בן אברהם הצפרי, ואחרי 1909 למשלמה בן אבּ-ספֿוה הדנפי.", "1897–1976")

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
print("Tsfari fixed: ישמעאל root added; #209/#239 -> ישמעאל; #228 -> #209; #237/#238 -> #209; ר-סרוריה removed (=#212)")
