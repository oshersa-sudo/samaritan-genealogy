# -*- coding: utf-8 -*-
# 2026-11-07 — the three printed trees of page 87 («משפחת ישראל / עבד-חנונה / סעד בן ישמעאל בן אברהם הסתרי הדנפי (נכון ל-1909)»)
# reconciled with the site.  Reading of the print (owner's photo) + the independent reading of the census pages (scan_read, p.86) + the prose of pp.88-89.
#   1. ישראל (#122): + יוסף (named only in parentheses in the print); תמים (#133) gets his two named children ישראל and אברהם (the census calls the
#      second «נאברב»), the others «עוד ילדים שמתו».
#   2. עבד-חנונה (#135): the eight census persons 141–148 that were never on the site —
#      141 עבד-חנונה, 142 קמר (children of אברהם #140), 143 שמעון (+סלוח #233) with 144 יעקב, 145 זינאב=פועה (+#230), 146 כוכב and (not numbered,
#      died 1897) עזיזה, and the sisters 147 נעימה (+#89) and 148 בהייה (+#211); the two infants «יוסף ?» under #137 and #138.
#   3. סעד (#150 «150»): already complete — only the wife/husband links are made (the wives' records point at the census numbers 150-160).
# Idempotent; log in hasatri_p87_fixed_20261107.json
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
FAM = next(f for h in master['houses'] for f in h['families'] if f['family'].startswith('משפחת הסתרי הדנפי'))
LOG = []
T87 = 'לפי תרשים עמ׳ 87 («נכון ל-1909»).'


def ah(g):
    return round((g - 621.57) * 1.030684)


def add(pid, name, sex, father, birth=None, death=None, note='', spouses=None, story=None, greg=None):
    if pid in P:
        return
    n = {'id': pid, 'name': name, 'sex': sex}
    if father: n['father_id'] = father
    if birth: n['birth'] = birth
    if death: n['death'] = death
    if note: n['note'] = note
    if spouses: n['spouses'] = spouses
    FAM['persons'].append(n); P[pid] = n
    if story:
        stories[pid] = {'t': story}
        if greg: stories[pid]['g'] = greg
    LOG.append({'new': pid, 'name': name, 'father': father})


def kids(pid, order):
    for c in order:
        assert c in P, c
        assert P[c].get('father_id') == pid, (c, P[c].get('father_id'), pid)
    if P[pid].get('children_ids') != order:
        P[pid]['children_ids'] = order; LOG.append({'children_order': pid, 'ids': order})


NIQ = ''.join(chr(c) for c in range(0x0591, 0x05C8))


def nk(x):
    return ''.join(ch for ch in str(x or '') if ch not in NIQ)


def spnote(pid, frag, note):
    for s in P[pid].get('spouses') or []:
        if frag in nk(s.get('name')) or frag == s.get('ref'):
            if s.get('note') != note:
                s['note'] = note; LOG.append({'spouse_link': pid, 'note': note})
            return
    raise SystemExit('spouse not found on %s: %s' % (pid, frag))


# =============================================================== 1. ישראל בן ישמעאל (#122)
add('הס-יוסף122', 'יוסף', 'M', '122', note=T87 + ' שמו בסוגריים בתרשים; אינו ברשימת המפקד.')
kids('122', ['123', 'הס-יוסף122', '130', '131', '132', '133', '134'])
P['133']['note'] = ('בתרשים עמ׳ 87 מצוירים שני ילדיו הנזכרים בשמם (ישראל ואברהם) ואחריהם «עוד ילדים שמתו»; '
                    'ברשומת המפקד: «שלושת ילדיהם מתו בעודם קטנים», ובפרוזה: נולדו ילדים רבים (יש האומרים 9).')
add('הס-ישראל133', 'ישראל', 'M', '133', birth=ah(1903), note=T87 + ' מת בילדותו.',
    story='נולד לפני 1909 ומת בילדותו.', greg='1903–')
add('הס-אברהם133', 'אברהם', 'M', '133', birth=ah(1908),
    note=T87 + ' בטקסט המאמר (עמ׳ 88) נקרא «נאברב». מת בילדותו.',
    story='נולד לפני 1909 ומת בילדותו.', greg='1908–')
kids('133', ['הס-ישראל133', 'הס-אברהם133'])

# =============================================================== 2. עבד-חנונה (#135)
add('141', 'עבד-חנונה = אללטיף', 'M', '140', birth=1321,
    note=T87 + ' בתרשים: «עבד-חנונה».',
    story='חייט כל חייו; יצא לגימלאות והחל להעתיק ספרים. עד 1933 חי בשכם, אחר כך עבר ליפו, שב לשכם ב-1947 וב-1951 עבר לחולון.', greg='1903–')
add('142', 'קמר', 'F', '140', birth=1326, note=T87 + ' מתה בילדותה.',
    story='נולדה ב-1908 ומתה בילדותה.', greg='1908–')
kids('140', ['141', '142', 'הס-עבדאלה140', 'הס-סלים140'])

add('143', 'שמעון', 'M', '135', birth=1274, death=ah(1925), note=T87 + ' מספר המפקד: #143.',
    spouses=[{'name': 'סלוח בת חביב צדקה', 'ref': "233 צי'", 'birth': 1276, 'note': '= אדם #233; אלה נישואיה השניים (בטקסט עמ׳ 89: «עלֻתֶה»)'}],
    story='חי דתי; לא ידע קרוא וכתוב. נשא את סלוח (עלֻתֶה, 1859–1935) בת חביב צדקה. בשתי שנות חייו האחרונות אבדה לו ההכרה.', greg='1857–1925')
add('הס-עזיזה143', 'עזיזה', 'F', '143', birth=ah(1883), death=ah(1897),
    note=T87 + ' מתה צעירה, לפני המפקד — ללא מספר מפקד (בטקסט עמ׳ 89: «אין פרטים»).', greg='1883–1897')
add('144', 'יעקב', 'M', '143', birth=1310, death=ah(1977), note=T87,
    story='עבד כחייט וכבעל מלון; שכר מלונות בקבלנות (לפעמים הפסיד, לפעמים הרוויח); רוב שנותיו חי ביפו; לא נשא אשה.', greg='1892–1977')
add('145', 'זינאב = פועה', 'F', '143', birth=1315, death=ah(1977), note=T87,
    spouses=[{'name': 'בנימים (אלאמין) בן שלמה צדקה הצפרי', 'ref': "230 צי'", 'birth': 1295, 'note': '= אדם #230'}],
    story='נישאה לבנימים בן שלמה צדקה הצפרי (1878–1943).', greg='1897–1977')
add('146', 'כוכב = עדלה', 'F', '143', birth=1319, death=ah(1979),
    note=T87 + ' בכתב היד של המפקד: «פואב» (קריאה לא ודאית); בתרשים ובפרוזה (עמ׳ 89): «כוכב (עדלה)».',
    spouses=[{'name': 'טביה בן פינחס הכהן', 'note': 'נישאה אחרי 1909'}], greg='1902–1979')
kids('143', ['הס-עזיזה143', '144', '145', '146'])

add('147', 'נעימה', 'F', '135', birth=1278, death=ah(1915),
    note=T87 + ' בטקסט המאמר: «ניעמה» / «ביעמה».',
    spouses=[{'name': 'אבּ-ספֿוה "שהראן" בן שלמה הדנפי', 'ref': "89 ד'ג", 'birth': 1256, 'note': '= אדם #89; אשתו השנייה'}],
    story='עקרת בית. נישאה לאבּ-סְפֿוָה "שהראן" בן שלמה הדנפי (1839–1917).', greg='1861–1915')
add('148', 'בהייה', 'F', '135', birth=1279, death=ah(1941),
    note=T87 + ' בטקסט המאמר: «בהיה» / «בַּהִיֶה».',
    spouses=[{'name': 'יעקב בן מרחיב הצפרי', 'ref': "211 צי'", 'birth': 1258, 'death': 1316, 'note': '= אדם #211'}],
    story='עקרת בית. נישאה ליעקב בן מרחיב הצפרי וילדה לו את סֻגֿריֶה.', greg='1862–1941')
kids('135', ['136', '140', '143', '147', '148'])

add('הס-יוסף137', 'יוסף ?', 'M', '137', note=T87 + ' השם בתרשים עם סימן שאלה. מת בן 7 ימים ונקבר בחצר הבית (עמ׳ 88).')
add('הס-יוסף138', 'יוסף ?', 'M', '138', note=T87 + ' השם בתרשים עם סימן שאלה. מת בן 10 ימים (עמ׳ 88).')
kids('137', ['הס-יוסף137']); kids('138', ['הס-יוסף138'])
# 137's wife pointed at #115 by the number inside «115ד'» — she is רסמיה #153 (= «153»)
spnote('137', 'רסמיה', '= אדם #153; בן אחד מת בגיל 7 ימים')

# =============================================================== 3. סעד בן ישמעאל (#150 = «150»): links only
spnote('150', "238 צי'", '= אדם #238; בתרשים עמ׳ 87 מודפס «זוהרה בן יעקב הצפרי» (בן/בת — טעות דפוס); ברשומת המפקד: בת יעקב בן ישמעאל הצפרי')
spnote('238', 'סעד', '= אדם #150')
spnote('111', 'אב-ספוה', '= אדם #151')
spnote('234', 'עבד-הרחום', '= אדם #155')
spnote('215', 'סעדיה', '= אדם #152')
# קמרה (#160) — married אברהם בן מרחיב הצפרי (#214; the census prints him a second time as #254 «ככל הנראה זהה»)
if not P['160'].get('spouses'):
    P['160']['spouses'] = [{'name': 'אברהם בן מרחיב הצפרי', 'ref': '214', 'note': '= אדם #214; ברשומת המפקד הוא מופיע גם כ-#254'}]
    LOG.append({'id': '160', 'spouse_added': 'אברהם בן מרחיב הצפרי #214'})
spnote('214', 'קמרה', '= אדם #160')
P['160']['note'] = (P['160'].get('note', '') + ' ' + T87).strip() if T87 not in P['160'].get('note', '') else P['160']['note']
print('150 children:', P['150'].get('children_ids'))


# =============================================================== 4. names as printed on page 87 (cosmetic, same persons)
def rename_sp(pid, frag, new):
    for sp in P[pid].get('spouses') or []:
        if frag in nk(sp.get('name')):
            if sp['name'] != new:
                LOG.append({'spouse_renamed': pid, 'from': sp['name'], 'to': new}); sp['name'] = new
            return
    raise SystemExit('spouse not found %s %s' % (pid, frag))


if P['150']['name'] != 'סעד':          # «סעד בן ישמעאל» printed in full → the card adds «(בן ישמעאל)» itself
    LOG.append({'renamed': '150', 'from': P['150']['name'], 'to': 'סעד'}); P['150']['name'] = 'סעד'
rename_sp('122', 'מסעודה', 'מסעודה בת שלמה הכה״ג')
rename_sp('123', 'בדיעה', 'בדיעה בת יעקב הכה״ג')
rename_sp('124', 'שלבי', 'שלבי בן יעקב השלבי')
rename_sp('139', 'יצחק', 'יצחק בן עמרם הכהן')

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('hasatri_p87_fixed_20261107.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
for e in LOG: print(e)
print(len(LOG), 'changes')
