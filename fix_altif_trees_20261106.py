# -*- coding: utf-8 -*-
# 2026-11-06 — the two printed trees «משפחת יוסף בן אב-סכוה בן עבד-חנונה הדנפי» and «משפחת שלמה בן אב-סכוה בן עבד-חנונה הדנפי»
# (the printed page 77) compared with the site (#38 and #50 subtrees) and corrected: spouse names/epithets, a missing first wife, a missing child,
# links to the spouses who are people on the site, and sex where the tree states it. Every change is checked against the current value first.
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
FAM = next(f for h in master['houses'] for f in h['families'] if f['family'] == 'משפחת אלטיף הדנפי')
LOG = []


def spouse(pid, idx, old, new, note=None):
    sp = P[pid]['spouses'][idx]
    if sp['name'] != old:
        LOG.append({'skip': pid, 'idx': idx, 'expected': old, 'found': sp['name']}); return
    sp['name'] = new
    if note: sp['note'] = note
    LOG.append({'id': pid, 'spouse': idx, 'from': old, 'to': new, 'note': note})


# ---- tree 1 (Yosef #38)
spouse('39', 0, 'זֻהְרָה בת אסעד', 'זהרה בת סעד הצפרי')
spouse('40', 0, 'יעקב בן ישמעאל', 'יעקב בן ישמעאל הסתרי')
spouse('41', 0, 'יצחק', 'יצחק בן עמרם הכהן')
spouse('43', 0, 'רבקה בת פינחס', 'רבקה בת פינחס הכהן')
spouse('49', 0, 'שלמה', 'שלח בן אברהם הדנפי', '= אדם #85')
if not P['47'].get('spouses'):
    P['47']['spouses'] = [{'name': 'סלים בן עבדאלה הדנפי', 'note': '= אדם #60'}]
    LOG.append({'id': '47', 'added_spouse': 'סלים בן עבדאלה הדנפי'})
# second «עפיף» among the children of זבולן (#43) — printed twice in the tree
if 'דנ-עפיף43' not in P:
    n = {'id': 'דנ-עפיף43', 'name': 'עפיף', 'sex': 'M', 'father_id': '43', 'note': 'מופיע פעמיים בין ילדי זבולן בעץ המודפס.'}
    FAM['persons'].append(n); P['דנ-עפיף43'] = n
    P['43'].setdefault('children_ids', []).append('דנ-עפיף43')
    LOG.append({'new': 'דנ-עפיף43', 'father': '43'})

# ---- tree 2 (Shlomo #50)
spouse('50', 0, 'נשונה בת ישמעאל', 'נשוה בת ישמעאל הדנפי')
if len(P['50']['spouses']) == 1:
    P['50']['spouses'].append({'name': 'אשתו הראשונה (שמה לא נודע)', 'note': 'אם יוסף'})
    LOG.append({'id': '50', 'added_spouse': 'אשתו הראשונה (שמה לא נודע)'})
spouse('51', 0, 'זהרה בת אסעד', 'זהרה בת סעד הצפרי')
spouse('52', 0, 'עזייה בת מרחיב', 'עזייה בת מרחיב צדקה', 'מתה ללא ילדים')
spouse('52', 1, 'מרים בת חביב', 'מרים בת חביב צדקה', 'גורשה')
spouse('52', 2, 'אלה בת יעקב אלשלבי', 'אלה בת יעקב השלבי')
spouse('53', 0, 'תמאם בת יצחק', 'תמאם בת יצחק הכהן')
spouse('56', 0, 'שלמה', 'שלמה בן עמרם הכהן')
spouse('57', 0, 'ורדה בת עמרם', 'ורדה בת עמרם הכהן')
spouse('58', 0, 'מרים בת יעקב', 'מרים בת יעקב הכהן')
spouse('65בּ\'', 0, 'רבקה בת אפריס', 'רפיקה בת אפרים הדנפי')
spouse("65אא'", 0, 'הדִיֶה בת אפרים', 'הדִיֶה בת אפרים הדנפי')
spouse('67', 0, 'גמליאל בן אבּ-סכנה', 'גמליאל בן אבּ-סכוה הדנפי')
spouse('68', 0, 'שלום בן אבּ-סכוה', 'שלום בן אבּ-סכוה הדנפי')
# sex stated / implied by the tree: מניר, רצון unmarked (male names); «עיפאת (בת)»
for pid, sx in (('59', 'M'), ('64', 'M'), ('65ג', 'F')):
    if not P[pid].get('sex'):
        P[pid]['sex'] = sx; LOG.append({'id': pid, 'sex': sx})
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('altif_trees_fixed_20261106.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
for e in LOG: print(e)

# the printed reference «209 ב'-צ'» of Zohara bat Sa'd points to #209 (Yaakov Tzedaka, a man) — not her; keep the printed text, drop the wrong link
master = json.load(io.open('master_v2.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
for pid in ('39', '51'):
    sp = P[pid]['spouses'][0]
    if sp.get('ref'):
        sp['note'] = f"הפניה מודפסת: {sp.pop('ref')} (לא אומתה — אינה מתאימה לאדם #209 שבעץ)"
        print('ref moved to note for', pid)
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
