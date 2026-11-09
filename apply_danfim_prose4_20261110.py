# -*- coding: utf-8 -*-
# 2026-11-10 — owner's corrections after reading prose_sources_20261109.html:
#   1. «גור» בעלה של אליס = נור בן אברהם בן מרחיב צדקה (#219, בנה של קמרה #160) — מקושר בשני הכיוונים
#   2. אלה (#74): בעלה = יוסף בן חביב צדקה (לפי עמ׳ 80; לא מקושר — ראו דוח); הקישור ל-#52 נותק
#   3. #90: הכינוי «אלעיה הקטן»; #132: מברוכה; #131: סועאד; #92: פועה (זינאב בערבית); «שלפי» → «שלבי»
# Idempotent. Log: danfim_prose4_applied_20261110.json
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
LOG = []


def addnote(pid, t):
    if t not in (P[pid].get('note') or ''):
        P[pid]['note'] = ((P[pid].get('note') or '') + ' ' + t).strip(); LOG.append({'note': pid})


# ---- 1. Alice ↔ Nur
a = P['75א']
a['spouses'] = [{'name': 'נור בן אברהם בן מרחיב צדקה (מנסבחה)', 'ref': '219', 'note': '= אדם #219; נישאה לו אחרי 1909 (עמ׳ 80)'}]
n = P['219']
if not n.get('spouses'):
    n['spouses'] = [{'name': 'אליס (בת שלבי, עליס)', 'ref': '75א', 'note': '= אדם #75א; נישא לה אחרי 1909 (עמ׳ 80)'}]
addnote('75א', 'בעלה נקרא בתמלול ראשון «גור»; תוקן לפי הבעלים: נור בן אברהם בן מרחיב צדקה (בנה של קמרה #160).')
stories['75א'] = {'t': 'בת שלבי. נישאה אחרי 1909 לנור (מנסבחה) בן אברהם בן מרחיב צדקה הצפרי (#219).', 'g': '1902–1987'}
LOG.append('alice-nur')

# ---- 2. Ella: Yosef son of Habib (not linked — #235 «יוסף בן חביב» was born ≈1873, twelve years after her)
P['74']['spouses'] = [{'name': 'יוסף בן חביב צדקה', 'note': 'לפי עמ׳ 80 (הפרוזה) ולפי הבעלים. עמ׳ 76 ורשימת המפקד: יוסף בן יוסף הדנפי (מספר 52 ברשימה).'}]
for s in P['52']['spouses']:
    if s.get('ref', '').startswith('74'):
        s.pop('ref', None); s['name'] = 'אלה בת יעקב השלבי'
        s['note'] = 'לפי עמ׳ 76 ורשימת המפקד; לפי עמ׳ 80 (ולפי הבעלים) נישאה ליוסף בן חביב צדקה — לא הוכרע'
stories['74'] = {'t': 'בת יעקב השלבי. נישאה ליוסף בן חביב צדקה (עמ׳ 80). לפי עמ׳ 76 ורשימת המפקד היא האשה השלישית של יוסף בן יוסף בן שלמה (#52) ואם אברהם — הסתירה לא הוכרעה.', 'g': '1861–1888'}
LOG.append('ella-yosef-habib')

# ---- 3. names
P['90']['name'] = 'אברהם = אלעיה הקטן'
P['90']['note'] = ('רווק; כונה «אלעיה הקטן» (חלש ומסכן) — עמ׳ 82. לפי המלל (עמ׳ 82) נולד 1863; לפי רשימת המפקד 1283 (≈1866) — נשמרה רשימת המפקד: אמו חפיזה נולדה ≈1850 (1266), ו-1863 היה מגיל 13.')
if 'אלערג' in (stories.get('90') or {}).get('t', ''):
    stories['90']['t'] = re.sub(r"'אלערג[^']*'", "'אלעיה הקטן'", stories['90']['t'])
P['131']['name'] = 'סעדה = סועאד'
stories['131']['t'] = stories['131']['t'].replace("'סגֿאר'", "'סועאד'")
P['132']['name'] = 'מפריקה = מברוכה'
stories['132']['t'] = stories['132']['t'].replace("'מהריפה'", "'מברוכה'")
P['92']['name'] = 'פועה = זִינַאבּ'
for p in P.values():
    for s in p.get('spouses') or []:
        if 'פגעה' in (s.get('name') or ''): s['name'] = s['name'].replace('פגעה', 'פועה'); LOG.append({'spouse_text': p['id']})
stories['78']['t'] = re.sub(r'שלפ[ֿ]?י', 'שלבי', stories['78']['t'])
for m in integ['modern']:
    if m.get('notes') and 'שלפי' in m['notes']:
        m['notes'] = m['notes'].replace(' (שלפי = שלבי)', '').replace('שמסה ושלפי', 'שמסה ושלבי'); LOG.append({'registry_note': m['id']})

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('danfim_prose4_applied_20261110.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(LOG)
