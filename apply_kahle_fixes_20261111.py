# -*- coding: utf-8 -*-
# 2026-11-11 — owner: «אחד את הדור הכפול» + «תקן רק מה שוודאי לפי המאמר של קאהלה».  Source: P. Kahle, Die Samaritaner im Jahre 1909, PJB 26 (1930), pp.94-103.
#  1. #72 is the DIRECT child of #71 (Kahle p.96) → the extra node «דנ-צדקה-ב» is removed (doubled generation)
#  2. #70: the dates 1252/1301 are her husband's (#80) — removed
#  3. #137: spouse ref 115 → 153 (Kahle p.98: «Rasmije bint Murdschān (153 De)»)
#  4. #96: death 1288 (Kahle p.97)         5. #61: born 1315, name Bedr = Jerah (Kahle p.96 + name table p.93-94)
#  6. #253: born ≈1277 (Kahle p.103)       7. #74 Ella: husband = Yosef b. Yosef #52 (Kahle p.95-96) — link restored
# NOT touched (not certain): the Hasatri apex (De) hypothesis.  Idempotent.  Log: kahle_fixes_applied_20261111.json
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
LOG = []


def addnote(pid, t):
    if t not in (P[pid].get('note') or ''):
        P[pid]['note'] = ((P[pid].get('note') or '') + ' ' + t).strip(); LOG.append({'note': pid})


# 1. the doubled generation
if 'דנ-צדקה-ב' in P:
    for h in master['houses']:
        for f in h['families']:
            f['persons'] = [x for x in f['persons'] if x['id'] != 'דנ-צדקה-ב']
    P['71']['children_ids'] = ['72']; P['72']['father_id'] = '71'
    addnote('71', 'לפי קאהלה (עמ׳ 96): יעקב (#72) הוא בנו הישיר; שאר ילדיו מתו ללא צאצאים.')
    addnote('72', 'לפי קאהלה (עמ׳ 96) בנו הישיר של יוסף שלבי (#71); הצומת «צדקה» שהופיע ביניהם בתרשים ובמלל (עמ׳ 80) היה דור כפול — אוחד ב-11.11.2026.')
    LOG.append('merged doubled generation: דנ-צדקה-ב removed')
# 2. #70
for k in ('birth', 'death'): P['70'].pop(k, None)
addnote('70', 'התאריכים 1252 ו-1301 שהופיעו כאן הם של בעלה (#80) — תוקן לפי קאהלה (עמ׳ 96); אין לה תאריכים משלה.')
# 3. #137
for s in P['137'].get('spouses') or []:
    if s.get('ref', '').startswith('115'): s['ref'] = "153ד'ה"; LOG.append('137 spouse ref -> 153')
# 4. #96
if not P['96'].get('death'): P['96']['death'] = 1288; LOG.append('96 death 1288')
# 5. #61
P['61']['birth'] = 1315
P['61']['name'] = 'בדר = ירח (בן עבדאלה)'
addnote('61', 'בקריאה הקודמת: «פֻּדִיר (זהר)». לפי קאהלה (עמ׳ 96): Bedr, נולד 1315; ובטבלת השמות (עמ׳ 93–94): Bedr = Jerah (ירח).')
# 6. #253
if not P['253'].get('birth'): P['253']['birth'] = 1277; LOG.append('253 birth 1277')
# 7. Ella ↔ Yosef b. Yosef
P['74']['spouses'] = [{'name': 'יוסף בן יוסף הדנפי', 'ref': "52ד'א", 'birth': 1264, 'death': 1327, 'note': '= אדם #52; לפי קאהלה (עמ׳ 96), עמ׳ 76 ורשימת המפקד. בפרוזה בעמ׳ 80 נכתב «יוסף בן חביב צדקה».'}]
for s in P['52']['spouses']:
    if s.get('name', '').startswith('אלה'):
        s['ref'] = "74ד'ב"; s['name'] = 'אלה בת יעקב השלבי'; s['note'] = '= אדם #74; לפי קאהלה (עמ׳ 95–96), עמ׳ 76 ורשימת המפקד'
stories['74'] = {'t': 'בת יעקב השלבי. נישאה ליוסף בן יוסף בן שלמה (#52), בנשותיו השלישית, וילדה לו את אברהם (קאהלה עמ׳ 96; עמ׳ 76). בפרוזה בעמ׳ 80 נכתב שבעלה היה «יוסף בן חביב צדקה» — הסתירה הוכרעה לפי קאהלה.', 'g': '1861–1888'}
LOG.append('Ella relinked to #52')
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('kahle_fixes_applied_20261111.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(LOG)
