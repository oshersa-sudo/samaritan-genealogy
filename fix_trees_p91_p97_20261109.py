# -*- coding: utf-8 -*-
# 2026-11-09 — the six printed trees of pages 91 and 97 («נכון ל-1909») reconciled with the site:
#   page 97 (Tsfari house):  שלמה בן ישמעאל בן שלח · חביב בן יעקב בן ישמעאל · מרחיב בן יעקב בן ישמעאל
#   page 91 (Marhibi house): יוסף בן יהושע · יצחק בן יהושע · יעקב בן מרחיב
# Sources: the owner's photos of both pages, the independent reading of the census pages (scan_read) and the census prose of pp.93-101.
# Main corrections:
#   * אריה (#242) is the father of זכאי/מוטיע/ישראל/יצחק (+ אברהם and גמליאל who died young) — they hung directly under שלמה;
#   * סעד (#247) is a son of שלמה (#239) — the separate apex «שלמה» (צפ-שלמה-א) is the same man and is archived;
#   * the census numbers 203–208 (children of סעד #202) replace the working ids «מר-…», and the missing #205 זוהרה is added;
#   * missing people: אלקנה, אב-זהותה, יוסף and רצון (sons of בנימים #175), אברהם (b.1909, son of #208), the unnamed first wife of יוסף #165 and of #192;
#   * wrong spouse links: #180's wife (#97), #167's wife's father (סאלם, not אב-סכוה), #165's note, #240's wife (#170);
#   * second/third marriages written in the prints: #214+סלוח(#233), #233+אברהם(#214), #235+מלכה(#186), #186+שלבי(#75)+יוסף(#235), #185+סעד בן שלח(#231),
#     #188↔ישמעאל(#176א), #247+סעדה(#199)↔#199, #212's 2nd husband; names as printed (נביהה, זכיה, נאסר, כאתבה, מוטיע …).
# Idempotent; log in trees_p91_p97_fixed_20261109.json
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
RENAME = {'מר-אברהם202': '203', 'מר-זבולן': '204', 'מר-יעקב202': '206', 'מר-ברור202': '207', 'מר-סעוד202': '208'}
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))
LOG = []
ALT = '|'.join(sorted(map(re.escape, RENAME), key=len, reverse=True))
NOTE_RX = re.compile(r'#\s*(' + ALT + r')(?![א-ת0-9\-])')


def fixstr(s):
    return RENAME[s] if s in RENAME else NOTE_RX.sub(lambda m: '#' + RENAME[m.group(1)], s)


def walk(o):
    if isinstance(o, str): return fixstr(o)
    if isinstance(o, list): return [walk(x) for x in o]
    if isinstance(o, dict): return {fixstr(k): walk(v) for k, v in o.items()}
    return o


if any(k in json.dumps(master, ensure_ascii=False) for k in RENAME):
    master = walk(master); stories = walk(stories); integ = walk(integ); LOG.append({'renamed_ids': RENAME})
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
FAMOF = {p['id']: f for h in master['houses'] for f in h['families'] for p in f['persons']}
NIQ = ''.join(chr(c) for c in range(0x0591, 0x05C8))


def nk(x): return ''.join(ch for ch in str(x or '') if ch not in NIQ)


def ah(g): return round((g - 621.57) * 1.030684)


def add(pid, name, sex, father, birth=None, death=None, note='', spouses=None, story=None, greg=None):
    if pid in P: return
    n = {'id': pid, 'name': name, 'sex': sex, 'father_id': father}
    if birth: n['birth'] = birth
    if death: n['death'] = death
    if note: n['note'] = note
    if spouses: n['spouses'] = spouses
    FAMOF[father]['persons'].append(n); P[pid] = n; FAMOF[pid] = FAMOF[father]
    if story:
        stories[pid] = {'t': story}
        if greg: stories[pid]['g'] = greg
    LOG.append({'new': pid, 'name': name, 'father': father})


def kids(pid, order):
    for c in order:
        assert c in P and P[c].get('father_id') == pid, (c, P.get(c, {}).get('father_id'), pid)
    if P[pid].get('children_ids') != order:
        P[pid]['children_ids'] = order; LOG.append({'children_order': pid, 'ids': order})


def setfather(pid, new):
    old = P[pid].get('father_id')
    if old == new: return
    if old in P and pid in (P[old].get('children_ids') or []): P[old]['children_ids'].remove(pid)
    P[pid]['father_id'] = new
    LOG.append({'moved': pid, 'from': old, 'to': new})


def sp(pid, frag):
    for s in P[pid].get('spouses') or []:
        if frag in nk(s.get('name')) or frag == s.get('ref'): return s
    return None            # already applied on an earlier run (the fragment was renamed)


def upd(pid, frag, **kw):
    s = sp(pid, frag)
    if s is None: return
    ch = {k: v for k, v in kw.items() if s.get(k) != v}
    if ch: s.update(ch); LOG.append({'spouse': pid, **ch})


def addsp(pid, new, key):
    L = P[pid].setdefault('spouses', [])
    if any(key in nk(s.get('name')) or key == s.get('ref') or key in str(s.get('note') or '') for s in L): return
    L.append(new); LOG.append({'spouse_added': pid, 'name': new['name']})


def ren(pid, name, note=None):
    if P[pid]['name'] != name:
        LOG.append({'renamed': pid, 'from': P[pid]['name'], 'to': name}); P[pid]['name'] = name
    if note and note not in (P[pid].get('note') or ''):
        P[pid]['note'] = ((P[pid].get('note') or '') + ' ' + note).strip()


def addnote(pid, t):
    if t not in (P[pid].get('note') or ''):
        P[pid]['note'] = ((P[pid].get('note') or '') + ' ' + t).strip(); LOG.append({'note': pid})


T97 = 'לפי תרשים עמ׳ 97 («נכון ל-1909»).'
T91 = 'לפי תרשים עמ׳ 91 («נכון ל-1909»).'

# =============================================================== A. שלמה בן ישמעאל בן שלח הצפרי (p.97)
ren('242', 'אריה = נימר', 'בתרשים עמ׳ 97: «אריה»; בכתב היד של המפקד: «נימר». ' + T97)
P['242']['birth'] = P['242'].get('birth') or 1270
upd('242', 'שפיקה', name='שפיקה בת בנימים יהושע המרחיבי', note='= אדם #176')
upd('176', 'אריה', name='אריה בן שלמה הצפרי', note='= אדם #242')
for c in ('243', '244', '245', '246'): setfather(c, '242')
ren('244', 'מוטיע')
add('צפ-אברהם242', 'אברהם', 'M', '242', note=T97 + ' «אחד משני הבנים האחרונים של אריה; מת בקטנותו» (עמ׳ 101).')
add('צפ-גמליאל242', 'גמליאל', 'M', '242', note=T97 + ' «מת בן 12 חודשים» (עמ׳ 101).')
kids('242', ['243', '244', '245', '246', 'צפ-אברהם242', 'צפ-גמליאל242'])
upd('243', 'חוסון', name='חוסון בת סעד צדקה', note='= אדם #249')
upd('239', 'אספהאן', name='אספהאן ממשפחת מרחיב')
upd('239', 'נשו', name='נשווה בת ישמעאל הדנפי')
upd('240', 'סעוד', ref="170מ'", note='= אדם #170')
# סעד (#247) is a son of שלמה (#239) — the separate apex «שלמה» (צפ-שלמה-א) is the same man
setfather('247', '239')
kids('239', ['240', '242', '247'])
if 'צפ-שלמה-א' in P:
    arch_f = 'merged_persons_20261108.json'
    ARCH = json.load(io.open(arch_f, encoding='utf-8'))
    old = P['צפ-שלמה-א']
    FAMOF['צפ-שלמה-א']['persons'].remove(old)
    if 'צפ-שלמה-א' in (P[old['father_id']].get('children_ids') or []): P[old['father_id']]['children_ids'].remove('צפ-שלמה-א')
    ARCH.append({'merged_into': '239', 'person': old, 'uid': None,
                 'why': 'בעמ׳ 97 (שלמה בן ישמעאל בן שלח) סעד #247 הוא בן שלמה, ובעמ׳ 101 נאמר «שלמה בן ישמעאל בן שלח … אחיו של יעקב»; במפקד #247 הוא «בן שלמה צדקה» (#239). הצומת «שלמה» שנבנה מתרשים הצמרות (עמ׳ 75) הוא אותו שלמה.'})
    io.open(arch_f, 'w', encoding='utf-8').write(json.dumps(ARCH, ensure_ascii=False, indent=1))
    del P['צפ-שלמה-א']; LOG.append({'archived': 'צפ-שלמה-א', 'into': '239'})
addsp('247', {'name': 'סעדה בת מרחיב המרחיבי', 'ref': '199', 'note': '= אדם #199 (עמ׳ 101: «נשא שלוש נשים»)'}, '#199')
# keep the printed order of the wives: מברוכה, סעדה, פועה
L = P['247']['spouses']; L.sort(key=lambda s: 0 if 'מפרוקה' in nk(s['name']) or 'מברוכה' in nk(s['name']) else 1 if '#199' in str(s.get('note')) else 2)
kids('247', ['צפ-אלקנה247', '248', '249']) if 'צפ-אלקנה247' in P else None
add('צפ-אלקנה247', 'אלקנה = פאיז', 'M', '247', death=ah(1886), note=T97 + ' «שמת בן שנה ב-1886 מפצעים בראשו» (עמ׳ 101).')
kids('247', ['צפ-אלקנה247', '248', '249'])
ren('248', 'נביהה', 'בתרשים עמ׳ 97 ובעמ׳ 101: «נביהה».')
upd('235', 'ביהה' if any('ביהה' in nk(x.get('name')) for x in P['235']['spouses']) else 'בדיעה', name='נביהה בת סעד הצפרי')
addsp('199', {'name': 'סעד בן שלמה הצפרי', 'ref': '247', 'note': '= אדם #247'}, '#247')
ren('199', 'סעדה = אלטרמה', 'ברשימת המפקד (עמ׳ 95) נישאה גם לסעד בן שלמה הצפרי (#247); בתרשים עמ׳ 97 מופיע בעלה זה ליד עדילה (#198).')
upd('199', 'אברהם', note='= אדם #203')
addnote('198', 'בתרשים עמ׳ 97 מופיע ליד שמה גם «סעד בן שלמה הצפרי»; ברשימת המפקד (עמ׳ 95) הוא בעלה של סעדה אחותה (#199).')

# =============================================================== B. חביב בן יעקב בן ישמעאל הצפרי (p.97)
upd('228', 'זוהרה', name='זוהרה בת ישראל הדנפי (אלמועלם)', note='= אדם #81')
upd('229', 'מרים', name='מרים בת שלח הדנפי', note='= אדם #87')
L = P['233']['spouses']
if not any(s.get('ref') == '214' for s in L):
    L.insert(0, {'name': 'אברהם בן מרחיב צדקה הצפרי', 'ref': '214', 'note': '= אדם #214; נישואיה הראשונים'}); LOG.append({'spouse_added': '233', 'name': 'אברהם #214'})
addsp('214', {'name': 'סלוח בת חביב הצפרי', 'ref': '233', 'note': '= אדם #233; ללא ילדים'}, '#233')
addsp('235', {'name': 'מלכה בת צפר המרחיבי', 'ref': '186', 'note': '= אדם #186; נישאה לו אחרי 1909'}, '#186')
addnote('181', 'בתרשים עמ׳ 91: «שתי בנות שנפטרו».')

# =============================================================== C. מרחיב בן יעקב בן ישמעאל הצפרי (p.97)
S = P['210']['spouses']
S[0]['name'] = 'טורפה (=פדיעה) בת עבד-אלה השלבי'; S[1]['name'] = 'זינאב (פועה) בת עבד-הברא (עבד אלחאלק) השלבי'
S = P['211']['spouses']
S[0]['name'] = 'ניגמה בת יוסף המרחיבי'; S[1]['name'] = 'בהיה בת עבד-חנונה הדנפי'
add('צפ-אבזהותה211', 'אב-זהותה', 'M', '211', note=T97 + ' בן ניגמה; «מת בקטנותו» (עמ׳ 97 בטקסט).')
kids('211', ['צפ-אבזהותה211', '212'])
addsp('212', {'name': 'שלמה בן אב-סכוה הדנפי', 'note': 'נישאה לו אחרי 1909 (לפי תרשים עמ׳ 97)'}, 'שלמה בן אב-סכוה')

# =============================================================== D. יוסף בן יהושע המרחיבי (p.91)
L = P['165']['spouses']
if not any('ראשונה' in s['name'] for s in L):
    L.insert(0, {'name': 'אשה ראשונה ששמה לא נודע (אם ילדיו א-ד)', 'note': 'לפי תרשים עמ׳ 91'}); LOG.append({'spouse_added': '165', 'name': 'אשה ראשונה'})
upd('165', 'לטיפה', note='אשתו השנייה (אם ניגמה); = אדם #256')
kids('165', ['166', '172', '175', '177', '178'])
upd('167', 'זהרה', name='זוהרה בת סאלם (שלום) הדנפי')
add('מר-יוסף175', 'יוסף', 'M', '175', note=T91 + ' «מת במאה ה-19, צעיר; אין פרטים» (עמ׳ 93).')
add('מר-רצון175', 'רצון', 'M', '175', note=T91 + ' «מת קטן ב-1891; אין פרטים» (עמ׳ 93).')
kids('175', ['מר-יוסף175', '176', 'מר-רצון175', '176א'])
ren('178', 'ניגמה = כוכב', 'בכתב היד של המפקד: «ניג׳מה (כוכבה)». ' + T91)

# =============================================================== E. יצחק בן יהושע המרחיבי (p.91)
upd('180', 'זהרה', name='זוהרה בת שלח הדנפי', ref="97ד'ג", note='= אדם #97')
ren('185', 'זכיה', 'בתרשים עמ׳ 91: «זכיה»; בעמ׳ 94: «זפיה».')
upd('185', 'יעקב', note='= אדם #206')
addsp('185', {'name': 'סעד בן שלח הצפרי', 'ref': '231', 'note': '= אדם #231; לפי תרשים עמ׳ 91'}, '#231')
addsp('231', {'name': 'זכיה בת צפר המרחיבי', 'ref': '185', 'note': '= אדם #185'}, '#185')
upd('186', 'סעד', note='= אדם #208')
addsp('186', {'name': 'שלבי בן יעקב השלבי', 'ref': '75', 'note': '= אדם #75; נישואיה אחרי 1909'}, '#75')
addsp('186', {'name': 'יוסף בן חביב הצפרי', 'ref': '235', 'note': '= אדם #235; נישואיה אחרי 1909'}, '#235')
addsp('75', {'name': 'מלכה בת צפר המרחיבי', 'ref': '186', 'note': '= אדם #186; נישאה לו אחרי 1909'}, '#186')
upd('187', 'זבולן', note='= אדם #204')
addsp('188', {'name': 'ישמעאל בן בנימים המרחיבי', 'ref': '176א', 'note': '= אדם #176א'}, '#176א')
addsp('176א', {'name': 'קפה (כלה) בת צפר המרחיבי', 'ref': '188', 'note': '= אדם #188'}, '#188')
ren('190', 'נאסר', 'בכתב היד של המפקד: «נאצר»; בתרשים עמ׳ 91 ובעמ׳ 94: «נאסר».')
upd('190', 'זוהרה', note='= אדם #205; ללא ילדים')
ren('190א', 'כאתבה', 'בכתב היד של המפקד: «פאתחה» / «פאחבה»; בתרשים עמ׳ 91: «כאתבה».')

# =============================================================== F. יעקב בן מרחיב המרחיבי (p.91)
if not P['192'].get('spouses'):
    P['192']['spouses'] = [{'name': 'אם-חליל (אשה שלא נודעה בשמה)', 'note': 'חיה כמאה שנה; לפי תרשים עמ׳ 91'}]; LOG.append({'spouse_added': '192', 'name': 'אם-חליל'})
upd('200', 'זהרה', note='= אדם #205; גורשה')
upd('200', 'עריפה', name='עריפה בת בנימים הצפרי', note='= אדם #241 (הדדי)')
add('205', 'זוהרה = אלפלוזה', 'F', '202', birth=1271,
    spouses=[{'name': 'שלח אלעיארב', 'ref': '200', 'note': '= אדם #200; גורשה'}, {'name': 'נאסר בן יצחק המרחיבי', 'ref': '190', 'note': '= אדם #190; ללא ילדים'}],
    note=T91 + ' «אלפלוזה היה שם אמה» (עמ׳ 94); בתרשים עמ׳ 91 האם: «אל פלוה».')
ren('207', 'ברוך (בן סעד)', 'מת רווק (עמ׳ 95).')
P['207']['birth'] = P['207'].get('birth') or 1280; P['207']['death'] = P['207'].get('death') or 1325
P['206']['birth'] = P['206'].get('birth') or 1275
upd('203', 'סעדה', note='= אדם #199')
upd('203', 'ופליקה', note='= אדם #117')
kids('203', ['204'])
upd('204', 'פהימה', note='= אדם #187')
P['204']['birth'] = P['204'].get('birth') or 1304
P['206']['spouses'] = P['206'].get('spouses') or [{'name': 'זכיה בת צפר המרחיבי', 'ref': '185', 'note': '= אדם #185'}]
upd('208', 'מלכה', note='= אדם #186')
add('מר-אברהם208', 'אברהם', 'M', '208', birth=1327, note=T91 + ' נולד 1909 — מלכה הרתה לו בעת המפקד (הערת א.ב.).')
kids('208', ['מר-אברהם208'])
kids('202', ['203', '205', '206', '207', '208'])


# a link note that repeats the «= אדם #N» already stored in the birth/death field of the same spouse is redundant — shown twice on the card
for _p in P.values():
    for _s in _p.get('spouses') or []:
        _n = _s.get('note')
        if isinstance(_n, str):
            _m = re.match(r'^= אדם #(\S+?)(?:;\s*(.*))?$', _n)
            if _m and any(('= אדם #' + _m.group(1)) in str(_s.get(k) or '') for k in ('birth', 'death')):
                if _m.group(2): _s['note'] = _m.group(2)
                else: del _s['note']

# =============================================================== pages for the sources (pdf page = printed − 72)
def subtree(r, acc):
    acc.add(r)
    for c in (P[r].get('children_ids') or []):
        if c in P: subtree(c, acc)
    return acc
tp = {}
for roots, page in ((['239', '228', '210'], 25), (['165', '179', '192', '202'], 19)):
    ids = set()
    for r in roots: subtree(r, ids)
    ids |= {'מר-אב-יעקב', 'צפ-ישמעאל'} if page == 25 else {'מר-אב-יעקב'}
    for i in ids:
        if i in P: tp.setdefault(i, []).append(page)
io.open('tree_pages.json', 'w', encoding='utf-8').write(json.dumps(tp, ensure_ascii=False, indent=1))

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('trees_p91_p97_fixed_20261109.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
for e in LOG: print(e)
print(len(LOG), 'changes')
