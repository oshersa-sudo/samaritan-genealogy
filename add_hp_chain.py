# -*- coding: utf-8 -*-
# Appends the clearly-legible High-Priest lineages from the numbered lists in
# "תולדות בני ישראל השומרונים" to the priestly house (ו) in master_v2.json:
#  (1) late-medieval Shechem High Priests, items 93-112 (1065-1624 CE)
#  (2) the Cairo Levite High Priests (1160-1590 CE)
# Father links are derived from each entry's patronymic ("X בן Y …" -> father = the
# most recent earlier entry named Y). Faint biblical names (items 1-92) are NOT
# included (scan legibility) per the "no uncertain links" rule.
import json, io

master = json.load(io.open('master_v2.json', encoding='utf-8'))
house = next(h for h in master['houses'] if 'הכהונה' in h['house'])
# idempotent: drop previously-added historical chains
house['families'] = [f for f in house['families'] if not f.get('_hp_chain')]

def build_chain(prefix, rows):
    """rows: list of (given, patronymic, label). Returns persons with father links by patronymic."""
    persons = []
    by_given = {}   # given-name -> last pid with that given name
    for i, (given, patro, label) in enumerate(rows):
        pid = '%s%d' % (prefix, i + 1)
        p = {"id": pid, "name": given + (' (בן ' + patro + ')' if patro else ''), "sex": "M"}
        if label: p["note"] = label
        fid = by_given.get(patro) if patro else None
        if fid: p["father_id"] = fid
        persons.append(p)
        by_given[given] = pid
    # children_ids
    cm = {}
    for p in persons:
        if p.get('father_id'): cm.setdefault(p['father_id'], []).append(p['id'])
    for p in persons:
        if p['id'] in cm: p['children_ids'] = cm[p['id']]
    return persons

# (1) Shechem High Priests, items 93-112 (given, father-given, reign-label)
shechem = [
 ("צדקה","אהרן","דור 93 · 1065–1077"),
 ("עמרם","אהרן","דור 94 · עמרם הששי · 1077–1115"),
 ("אהרן","עמרם","דור 95 · אהרן השני · 1115–1136"),
 ("עמרם","אהרן","דור 96 · עמרם השביעי · 1136–1164"),
 ("אהרן","עמרם","דור 97 · אהרן השלישי · 1164–1190"),
 ("נתנאל","אהרן","דור 98 · 1190–1205"),
 ("איתמר","עמרם","דור 99 · מדמשק · כיהן בשכם · 1205–1252"),
 ("עמרם","עמרם","דור 100 · עמרם השמיני · 1252–1269"),
 ("עזי","עמרם","דור 101 · עזי השני · 1269–1291"),
 ("יוסף","עזי","דור 102 · מדמשק · 1291–1308"),
 ("פינחס","יוסף","דור 103 · 1308–1363"),
 ("אלעזר","פינחס","דור 104 · 1363–1387"),
 ("אבישע","פינחס","דור 105 · אבישע השני · ~1387"),
 ("פינחס","אבישע","דור 106 · 1387–1442"),
 ("אבישע","פינחס","דור 107 · אבישע השלישי · 1442–1474"),
 ("אלעזר","אבישע","דור 108 · 1474–1509"),
 ("פינחס","אלעזר","דור 109 · 1509–1549"),
 ("אבישע","פינחס","דור 110 · 1549–1595"),
 ("שלמה","פינחס","דור 111 · 1595–1614"),
 ("שלמה","פינחס","דור 112 · 1614–1624"),
]
# (2) Cairo Levite High Priests
cairo = [
 ("זהרה","חלף","עדות 1160"),
 ("חלף","אברהם","עדות 1277"),
 ("ישע","אברהם","עדות 1332"),
 ("יצחק","אבּ-נפושה","עדות 1332"),
 ("אבי-עזי","","עדות 1336"),
 ("ישראל","אבי-עזי","עדות 1336"),
 ("צדקה","איתמר","עדות 1378"),
 ("צדקה","חלף","עדות 1383"),
 ("שלמה","חלף","עדות 1418"),
 ("פינחס","שלמה","עדות 1418"),
 ("צדקה","ישע","עדויות מ-1431, ~60 שנה"),
 ("אברהם","ישע","עדות 1454"),
 ("אברהם","צדקה","עדויות מ-1534"),
 ("צדקה","בבא","עדות 1590"),
]

house['families'].append({"family_no": 2, "family": "שלשלת הכהנים הגדולים בשכם (דורות 93–112, 1065–1624)",
                          "ref_code": "כהן", "_hp_chain": True,
                          "source_note": "מתוך הרשימה הממוספרת 'הכהנים הגדולים בארץ-ישראל'. דורות 1–92 (מאהרן) לא תומללו — חלקם אינם חדים בסריקה. לאימות.",
                          "persons": build_chain("שכם", shechem)})
house['families'].append({"family_no": 3, "family": "כהני קהיר הלוים (1160–1590)",
                          "ref_code": "לוי", "_hp_chain": True,
                          "source_note": "מתוך 'רשימת הכהנים הגדולים הלוים שכיהנו בקהיר'. לאימות.",
                          "persons": build_chain("קהיר", cairo)})

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
print("priestly house families now:", len(house['families']),
      "| shechem", len(shechem), "| cairo", len(cairo))
