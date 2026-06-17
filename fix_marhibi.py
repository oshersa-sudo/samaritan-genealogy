# -*- coding: utf-8 -*-
# Full rebuild/repair of בית אב המרחיבים from the prose transcripts page_92/94/95.
# Fixes tree POSITIONS (mis-parented + floating nodes), names, and adds the shared
# ancestor that the intro (page_92) documents.
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
house = next(h for h in master['houses'] if 'המרחיבים' in h['house'])
fam_yeh = next(f for f in house['families'] if 'יהושע' in f['family'])
fam_mar = next(f for f in house['families'] if f['family'] == 'משפחת מרחיב המרחיבי')
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

# idempotent: drop previously-added ancestor nodes (NOTE: 'מר-אב-' with trailing hyphen,
# so it does NOT match מר-אברהם202 / מר-אברהם184 added by add_marhibi.py)
for f in house['families']:
    f['persons'] = [p for p in f['persons'] if not str(p['id']).startswith('מר-אב-')]
allp = {p['id']: p for f in house['families'] for p in f['persons']}

# ---- shared ancestors (page_92 intro): מרחיב הקטן → {יעקב, יהושע}; יעקב → {מרחיב#192, סעד#202} ----
fam_yeh['persons'].insert(0, {"id": "מר-אב-מרחיב", "name": "מרחיב הקטן (המאה ה-18)", "sex": "M",
    "children_ids": ["מר-אב-יעקב", "164"], "note": "מרחיב בן יעקב בן אברהם — 'מרחיב הקטן'. הוליד את אברהם, יעקב, יהושע ואפרים."})
fam_yeh['persons'].insert(1, {"id": "מר-אב-יעקב", "name": "יעקב בן מרחיב", "sex": "M",
    "father_id": "מר-אב-מרחיב", "children_ids": ["192", "202"],
    "note": "אבי ענף 'מרחיבי' (בניו מרחיב=פרג' וסעד). בנו ברור התאסלם."})
allp = {p['id']: p for f in house['families'] for p in f['persons']}
setfather("164", "מר-אב-מרחיב")        # יהושע — אבי ענף 'יהושעי'
setfather("192", "מר-אב-יעקב")
setfather("202", "מר-אב-יעקב")

# ================= ענף יהושעי =================
# יוסף(#165) children per page_92: יהושע#166, שת#172, בנימים#175, זבולן#177, ניגֿמה#178.
setfather("175", "165")   # בנימים בן יוסף (היה תחת שת#172) — מאומת ע"י page_95 (אבי בעל עדילה)
setfather("177", "165")   # זבולן בן יוסף (היה תחת שת#172)
setfather("178", "165")   # ניגֿמה (כוכב) בת יוסף, ילדתו האחרונה (הייתה תחת יהושע#166)
setstory("178", "ניגֿמה (כוכב), בת הזקונים של יוסף בן יהושע. נישאה ליעקב בן מרחיב הצפרי; לאחר מותו חיה בבית צדקה בן מרחיב הצפרי.", "1848–1920")
# סעוד(#170) is daughter of יהושע#166, not יוסף#165 (page_92: "סֻאעֻד בת יהושע")
setfather("170", "166")
setstory("170", "סֻאעֻד בת יהושע. נישאה לסעד בן יעקב המרחיבי, ואחריו לבנימים בן שלמה הצפרי.", "1858–1920")

# יצחק(#179) children per page_94: חובב#180, צפר#184, נאסר#190, פאתחה#190א.
setname("180", "חובב")
setfather("190", "179")    # נאצר/באֵר — היה צף (ללא אב)
setfather("190א", "179")   # פאתחה — היה צף
setstory("190", "באֵר/נאצר, בנו השלישי של יצחק. פקיד אצל סוחר בשכם; נשא את זוהרה בת שלח אלפֿלולה; ללא ילדים.", "1854–1908")
setstory("190א", "פאֻתֻפֿה, בתו הבכורה של יצחק. נישאה לשלח בן יצחק הדנפי, ואחריו לסעד בן אבּ-ספֿוה הדנפי.", "1839–1901")
# צפר(#184) children per page_94: זפֿיה#185, מלֻכה#186, פהימה#187, קפה#188, מצליח#189, אברהם.
setname("185", "זפֿיה")
for k in ["186", "187", "188", "189"]:
    setfather(k, "184")    # היו צפים (ללא אב)
setname("188", "קפֿה (כלה)")
# יוסף(#181) daughter קֻאזֻר (מתה בילדותה) — the unnamed #182
setname("182", "קֻאזֻר")
setstory("182", "בת יוסף; מתה בילדותה.", "")

# ================= ענף מרחיבי =================
setname("196", "חובב")     # was mis-read "חפֻוף"; page_95: חובב (חכוב)
setstory("196", "בן אברהם. לא ידע קרוא וכתוב; עבד בסבלות ובשאיבת מים.", "1870–1918")
setstory("194", "בן אברהם. רוכל; מכר גפרורים, חוטים ונרות.", "1875–1941")

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
print("Marhibi fixed: ancestors added; #170/#175/#177/#178 reparented; #186-189/#190/#190א un-floated; names #180/#185/#188/#196/#182/#194")
