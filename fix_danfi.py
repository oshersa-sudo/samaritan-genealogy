# -*- coding: utf-8 -*-
# Corrections to בית אב הדנפים after a full pass over the prose transcripts
# (page_74…page_85). Census-node fixes only (mis-attributions / typos / unnamed slots).
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
allp = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}

def setname(pid, name):
    if pid in allp: allp[pid]['name'] = name
def setstory(pid, t, g=''):
    stories[pid] = {'t': t, 'g': g}
def setfather(pid, fid):
    if pid in allp:
        old = allp[pid].get('father_id')
        if fid is None:
            allp[pid].pop('father_id', None)
        else:
            allp[pid]['father_id'] = fid
        # clean old parent's children_ids
        if old and old in allp and 'children_ids' in allp[old]:
            allp[old]['children_ids'] = [c for c in allp[old]['children_ids'] if c != pid]
        # add to new parent's children_ids
        if fid and fid in allp:
            allp[fid].setdefault('children_ids', [])
            if pid not in allp[fid]['children_ids']:
                allp[fid]['children_ids'].append(pid)

# --- אלטיף ---
setname('42', 'רבקה')                                   # was typo "ירבקה" (page_74)
setname('64', 'רצון (רדי)')                             # unnamed slot = the son who died at 3
setstory('64', 'בן עבד-אלה; נפטר בגיל שלוש.', '1908–1911')

# --- משלמה ---
setname('98', 'ישמעאל (גֿמעאל)')                        # page_82: בעל חנות בשוק שכם
setstory('98', 'בן שלח. בעל חנות בשוק שכם; איש פשוט שידע ערבית קרוא וכתוב. נשא את חפיזה בת שלמה הדנפי.', '1861–1915')

# --- עבד-אלה ---
# #105 עפיפה + #106 חפיזה: NOT children of #104 שלמה הדנפי (b.1813 — 74y gap). per page_84
# they are daughters of סועאר (הדנפית) and שלמה המרחיבי. Detach the impossible link.
setfather('105', None)
setstory('105', 'בת סועאר (הדנפית) ושלמה המרחיבי. נישאה לחילמי בן יעקב אלשלבי.', '1885–1950')
setfather('106', None)
setstory('106', 'בת סועאר (הדנפית) ושלמה המרחיבי. נישאה לישמעאל בן שלח הדנפי, ואחריו לפתח-אלה בן חביב הצפרי.', '1888–1942')
# #118 זהרה: is זהרה בת סאלם (#112), not בת סעדה (#115) — page_85.
setfather('118', '112')
setname('118', 'זהרה')
setstory('118', 'בת סאלם. נישאה לשת (מרזוק) המרחיבי.', '1863–1900')

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
print('Danfi corrections applied: #42, #64, #98, #105, #106, #118')
