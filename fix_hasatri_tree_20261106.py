# -*- coding: utf-8 -*-
# 2026-11-06 — «צמרת משפחת הסתרי=סראוי (נכון עד 1909)» (printed page 79, lower tree) reconciled with the site:
#   ישמעאל אלסראוי → אברהם → {אב-סכוה, ישמעאל(+מרים בת הכהן יוסף העבתאי)} → אברהם → {ישמעאל=#121, ישראל=#120, עבד הפתח, עבד-אלה}
#   #121 ישמעאל has two unnamed wives: right branch → ישראל(#122), עבד-חנונה(#135), נשווה(#149), סעד(#150) [+ סעדה #161 from the census list];
#   left branch → יעקב (#162, wife #40 סלוח) → {שלח=עיארב א-שמוט, יהודה (שוקרי), אברהם, טהור (#163)}.
#   ישראל (#120) → {סלים, זינאב=פועה (#120א, wife of #135), פרוגיה (#257, wife of #123 / #73 / #177)}.
#   עבד הפתח → סעד (שהתאסלם) → חבובה (wife of #113).
# Also (owner's request, same day): the two persons «חפיזה» (#108) and «עפיפה» (#105) of the Danfim house are taken out of the tree
# (archived in removed_persons_20261106.json, uid numbers stay reserved) — to be added back later when their place is understood.
# Idempotent; log in hasatri_tree_fixed_20261106.json
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
reg = json.load(io.open('uid_registry.json', encoding='utf-8'))['map']
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
FAM = next(f for h in master['houses'] for f in h['families'] if f['family'].startswith('משפחת הסתרי הדנפי'))
LOG = []

# ------------------------------------------------------------ 0. owner's removal request: חפיזה (#108) and עפיפה (#105)
arch_f = 'removed_persons_20261106.json'
try:
    ARCH = json.load(io.open(arch_f, encoding='utf-8'))
except Exception:
    ARCH = []
for pid in ('105', '108'):
    if pid in P:
        p = P[pid]
        for h in master['houses']:
            for f in h['families']:
                if p in f['persons']:
                    f['persons'].remove(p)
        for q in P.values():
            if q.get('children_ids') and pid in q['children_ids']:
                q['children_ids'].remove(pid)
        ARCH.append({'person': p, 'story': stories.pop(pid, None), 'uid': reg.get(pid), 'reason': 'owner asked to take her out of the tree (2026-11-06)'})
        del P[pid]
        LOG.append({'removed': pid, 'name': p['name']})
io.open(arch_f, 'w', encoding='utf-8').write(json.dumps(ARCH, ensure_ascii=False, indent=1))


# ------------------------------------------------------------ helpers
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
    if father:
        ch = P[father].setdefault('children_ids', [])
        if pid not in ch: ch.append(pid)
    if story:
        stories[pid] = {'t': story}
        if greg: stories[pid]['g'] = greg
    LOG.append({'new': pid, 'name': name, 'father': father})


def setfather(pid, new):
    old = P[pid].get('father_id')
    if old == new: return
    if old in P and pid in P[old].get('children_ids', []):
        P[old]['children_ids'].remove(pid)
    P[pid]['father_id'] = new
    ch = P[new].setdefault('children_ids', [])
    if pid not in ch: ch.append(pid)
    LOG.append({'moved': pid, 'from': old, 'to': new})


def find_sp(pid, pred):
    for s in P[pid].get('spouses') or []:
        if pred(s): return s


TREE_P7 = 'לפי תרשים «צמרת משפחת הסתרי=סראוי» (עמ׳ 79).'
# ------------------------------------------------------------ 1. apex of the Hasatri tree
P['דנ-ישמעאל-א']['note'] = 'בתרשים עמ׳ 79: «ישמעאל אלסראוי (הסתרי) בן אברהם שבא מדמשק».'
add('הס-ישמעאל-ב', 'ישמעאל', 'M', 'דנ-אברהם-ג', note=TREE_P7 + ' בן אברהם (אחי אב-סכוה).',
    spouses=[{'name': 'מרים בת הכהן יוסף בן אברהם העבתאי'}])
add('הס-אברהם-ב', 'אברהם', 'M', 'הס-ישמעאל-ב', note=TREE_P7)
if P['121'].get('father_id') != 'הס-אברהם-ב':
    setfather('121', 'הס-אברהם-ב')
P['121']['note'] = ('פרוגניטור (ישמעאל בן ישראל הדנפי). בתרשים עמ׳ 79 הוא מצויר כבן אברהם (השני); '
                    'בכותרת הפרק במאמר נקרא «ישמעאל בן ישראל».')
if not P['121'].get('spouses'):
    P['121']['spouses'] = [
        {'name': 'אשה שלא נודעה בשמה (אם ישראל, עבד-חנונה, נשווה, סעד וסעדה)', 'note': 'ענף ימין בתרשים עמ׳ 79'},
        {'name': 'אשה שנייה שלא נודעה בשמה (אם יעקב)', 'note': 'ענף שמאל בתרשים עמ׳ 79'}]
    LOG.append({'id': '121', 'spouses_added': 2})

# ------------------------------------------------------------ 2. brothers of ישמעאל under אברהם (the second)
add('120', 'ישראל', 'M', 'הס-אברהם-ב', note=TREE_P7 + ' אחי ישמעאל (#121); בתו זינאב (פועה) נישאה לבן דודה עבד-חנונה (#135).',
    story='אחי ישמעאל (#121). בנותיו: זינאב (פועה) ופרוגיה; בנו: סלים.')
add('הס-עבדהפתח', 'עבד הפתח', 'M', 'הס-אברהם-ב', note=TREE_P7)
add('הס-עבדאלה-ב', 'עבד-אלה', 'M', 'הס-אברהם-ב', note=TREE_P7)
add('הס-סלים120', 'סלים', 'M', '120', note=TREE_P7 + ' מופיע בתרשים בלבד.')
add('120א', 'זינאב = פועה', 'F', '120', note=TREE_P7 + ' בתרשים: «פועה (זינאב)».',
    spouses=[{'name': 'עבד-חנונה בן ישמעאל', 'ref': "135 די'ה", 'birth': 1234, 'death': 1301, 'note': '= אדם #135'}])
add('257', 'פרוגיה', 'F', '120',
    note=TREE_P7 + ' נישאה לשלושה: ישמעאל בן ישראל הסתרי (#123), בנימים בן יעקב השלבי (#73), זבולן בן יוסף (#177). לא ילדה.',
    spouses=[{'name': 'ישמעאל בן ישראל הסתרי', 'ref': '123', 'note': '= אדם #123; ללא ילדים'},
             {'name': 'בנימים בן יעקב השלבי', 'ref': '73', 'note': '= אדם #73; ללא ילדים'},
             {'name': 'זבולן בן יוסף', 'ref': '177', 'note': '= אדם #177; ללא ילדים'}])
add('הס-סעד-מתאסלם', 'סעד (שהתאסלם)', 'M', 'הס-עבדהפתח',
    note=TREE_P7 + ' התאסלם וגר בכפר נקורה בנפת שכם (עמ׳ 85 במאמר).')
add('הס-חבובה', 'חבובה', 'F', 'הס-סעד-מתאסלם',
    note=TREE_P7 + ' בטקסט המאמר (עמ׳ 85) נקראת «חפופה»; בסיפור על סלים (#113) באתר — «חביבה». שרפה את עצמה בשנת 1910 (עמ׳ 85).',
    spouses=[{'name': 'סלים בן סאלם הדנפי', 'ref': "113 ד'ד", 'note': '= אדם #113'}])
s113 = P['113'].setdefault('spouses', [])
if not any(s.get('note') == '= אדם #הס-חבובה' or 'חבובה' in s.get('name', '') for s in s113):
    s113.append({'name': 'חבובה בת סעד (שהתאסלם)', 'note': '= אדם #הס-חבובה'})
    LOG.append({'id': '113', 'spouse_added': 'חבובה'})

# ------------------------------------------------------------ 3. children of ישמעאל (#121): right wife branch
add('149', 'נשווה', 'F', '121', birth=1236,
    note='בטקסט המאמר: «בשנוה»; בתרשים עמ׳ 79: «נשווה». ענף ימין (האשה הראשונה).',
    spouses=[{'name': 'אהרן בן שלמה הכהן', 'ref': "17 כי'", 'death': 1258},
             {'name': 'שלמה בן אב-סכוה הדנפי', 'ref': "50 די'א", 'note': '= אדם #50'},
             {'name': 'שלמה בן יעקב הצפרי', 'ref': "239 צי'", 'note': '= אדם #239'}])
add('161', 'סעדה', 'F', '121', birth=1250, death=1307,
    note='ענף ימין (מן הרשימה במאמר; אינה מצוירת בתרשים עמ׳ 79). בנם היחיד מת.',
    spouses=[{'name': 'סעד בן עבד אלחאלק (= עבד-הברא)', 'ref': "255 די'", 'death': 1326, 'note': '= אדם #255'}])
# ------------------------------------------------------------ 4. left wife branch: יעקב (#162) and his sons
add('162', 'יעקב', 'M', '121', birth=1260, death=1295, note='בן האשה השנייה. ענף שמאל בתרשים עמ׳ 79.',
    spouses=[{'name': 'סלוח בת יצחק לוטפי', 'ref': "40 די'א", 'birth': 1268, 'note': '= אדם #40'}])
add('הס-שלח162', 'שלח = עיארב א-שמוט', 'M', '162', note=TREE_P7,
    story='מעתיק ספרים ושוחט מוסמך; למד לכתוב אצל דודו זבולן בן יצחק הדנפי. כתבי היד שלו בספריות הכה״ג אבישע בן פינחס ובני זבולן. לא נשא אשה; מת ערירי.')
add('הס-יהודה162', 'יהודה (שוקרי)', 'M', '162', note=TREE_P7, story='מת ערירי.')
add('הס-אברהם162', 'אברהם', 'M', '162', note=TREE_P7, story='מת ערירי.')
add('163', 'טהור = טאהר', 'M', '162', birth=1297, note='בטקסט המאמר: «טהור החיט».',
    story='חייט מומחה (בעיקר ריקמה); מחבר ומפייט בעברית ובערבית. נאסר זמן ארוך בשכם ובבית הסוהר חיבר את פיוטיו הטובים. במלחמת העולם הראשונה גויס בכפייה בידי התורכים ונעלם; נאמר שמת בירושלים ונקבר בחלקה יהודית. לא נשא אשה.',
    greg='1879–1918')
# order of #121's children as printed: ישראל, עבד-חנונה, נשווה, סעד, סעדה, יעקב
P['121']['children_ids'] = [c for c in ['122', '135', '149', 'הס-סעד', '161', '162']]
for c in P['121']['children_ids']:
    assert P[c].get('father_id') == '121', c

# ------------------------------------------------------------ 5. spouse links / spellings on existing records
s135 = find_sp('135', lambda s: 'בת ישראל' in s.get('name', ''))
if s135 and s135.get('note') != '= אדם #120א':
    s135['name'] = 'זינאב (פועה) בת ישראל'; s135['note'] = '= אדם #120א'
    LOG.append({'id': '135', 'spouse_fixed': 'זינאב (פועה) בת ישראל → #120א'})
if 'זינאב (פגעה)' in stories['135']['t']:
    stories['135']['t'] = stories['135']['t'].replace('זינאב (פגעה)', 'זינאב (פועה)')
s123 = find_sp('123', lambda s: 'בת ישראל' in s.get('name', '') and s.get('ref') in ('25', '257'))
if s123 and s123.get('note') != '= אדם #257; ללא ילדים':
    s123['name'] = 'פרוגיה בת ישראל'; s123['ref'] = '257'; s123['note'] = '= אדם #257; ללא ילדים'
    LOG.append({'id': '123', 'spouse_fixed': 'פרוגיה → #257'})
s177 = find_sp('177', lambda s: s.get('ref') == '257')
if s177 and s177.get('name') != 'פרוגיה בת ישראל הסתרי':
    s177['name'] = 'פרוגיה בת ישראל הסתרי'; LOG.append({'id': '177', 'spouse_name': 'פרוגיה בת ישראל הסתרי'})
s73 = find_sp('73', lambda s: s.get('name', '').startswith('פרוגיה'))
if s73 and 'note' not in s73:
    s73['note'] = '= אדם #257; ללא ילדים'; s73['ref'] = '257'; LOG.append({'id': '73', 'spouse_linked': '#257'})

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('hasatri_tree_fixed_20261106.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
for e in LOG: print(e)
print(len(LOG), 'changes')
