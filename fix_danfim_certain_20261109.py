# -*- coding: utf-8 -*-
# 2026-11-09 — applies the MOST CERTAIN of the Danfim completions recommended in danfim_certain_completions_20261109.xlsx
# (owner: "החל רק את הודאיים ביותר").  Certain = stated explicitly in the prose text, the person is identified by census number / parents /
# a year of birth that matches the census list, and no source contradicts it.
# NOT applied (left in the recommendations file): #64's death (the prose says age 3, the census 1½ — conflicting), the deaths of #90 (birth 1863 vs the census 1866),
# #137 (birth 1896 vs 1869) and #149 (two women of the same name on p.88/p.89), all persons born after 1909 except נזמיה (confirmed on two pages),
# and the spouse of #98/#212 beyond what is written.  Idempotent; log in danfim_certain_applied_20261109.json
import json, io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
removed = json.load(io.open('removed_persons_20261106.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
FAMOF = {p['id']: f for h in master['houses'] for f in h['families'] for p in f['persons']}
NIQ = ''.join(chr(c) for c in range(0x0591, 0x05C8))
LOG = []


def nk(x): return ''.join(ch for ch in str(x or '') if ch not in NIQ)


def ah(g): return round((g - 621.57) * 1.030684)


def addnote(pid, t):
    if t not in (P[pid].get('note') or ''):
        P[pid]['note'] = ((P[pid].get('note') or '') + ' ' + t).strip(); LOG.append({'note': pid, 'text': t})


def addsp(pid, new, key):
    L = P[pid].setdefault('spouses', [])
    if any(key == s.get('ref') or key in str(s.get('note') or '') for s in L): return
    L.append(new); LOG.append({'spouse_added': pid, 'name': new['name']})


def setsp(pid, idx, **kw):
    s = P[pid]['spouses'][idx]
    ch = {k: v for k, v in kw.items() if s.get(k) != v}
    if ch: s.update(ch); LOG.append({'spouse': pid, **ch})


def child_id(father, name):
    return next(c for c in P if P[c].get('father_id') == father and nk(P[c]['name']).startswith(name))


GAM = child_id('65', 'גמליאל') if False else None
ids65 = {nk(P[i]['name']): i for i in P if i.startswith('65') and not i == '65'}
GAMLIEL = next(i for i in P if i.startswith('65') and nk(P[i]['name']) == 'גמליאל')
SHALOM = next(i for i in P if i.startswith('65') and nk(P[i]['name']) == 'שלום')
IYFAT = next(i for i in P if i.startswith('65') and nk(P[i]['name']) == 'עיפאת')
AZIZA = next(i for i in P if i.startswith('65') and nk(P[i]['name']) == 'עזיזה')

# ---------------------------------------------------------------- A. death years
D = [('40', 1935), ('42', 1946), ('43', 1917), ('44', 1963), ('46', 1940), ('47', 1975), ('48', 1982), ('53', 1939), ('55', 1918), ('56', 1950),
     ('59', 1945), ('60', 1927), ('61', 1968), ('62', 1979), ('63', 1976), (GAMLIEL, 1932), (SHALOM, 1942), ('67', 1928), ('68', 1971), ('69', 1983),
     ('73', 1908), ('77', 1917), ('78', 1937), ('75א', 1987), ('124', 1908), ('81', 1912), ('82', 1916), ('89', 1917), ('91', 1945), ('92', 1944),
     ('93', 1971), ('98', 1915), ('101', 1917), ('102', 1939), ('111', 1929), ('113', 1939), ('115', 1947), ('116', 1928), ('122', 1882), ('167', 1912),
     ('133', 1949), ('129', 1985), ('131', 1908), ('138', 1920), ('139', 1937), ('140', 1926), (IYFAT, 1982), (AZIZA, 1918)]
for pid, g in D:
    if not P[pid].get('death'):
        P[pid]['death'] = ah(g); LOG.append({'death': pid, 'name': P[pid]['name'], 'year': g, 'hijri': ah(g)})
for pid, g in [('76', 1871), (IYFAT, 1907), (AZIZA, 1880), ('64', 1908)]:
    if not P[pid].get('birth'):
        P[pid]['birth'] = ah(g); LOG.append({'birth': pid, 'name': P[pid]['name'], 'year': g, 'hijri': ah(g)})

# ---------------------------------------------------------------- C. spouse links
addsp('60', {'name': 'לוטפיה בת זבולן', 'ref': '47', 'note': '= אדם #47; לוטפיה נשארה אלמנה אחרי רעידת האדמה של 1927'}, '#47')
addsp('62', {'name': 'תמים בן אפרים הדנפי (כאמל)', 'ref': '69', 'note': '= אדם #69; נישאה לו אחרי 1909'}, '#69')
addsp('69', {'name': 'בדריה בת עבד-אלה', 'ref': '62', 'note': '= אדם #62; נישאה לו אחרי 1909'}, '#62')
addsp(IYFAT, {'name': 'מנגיר בן עבד-אלה הדנפי', 'ref': '59', 'note': '= אדם #59; נישאה לו ב-1922'}, '#59')
addsp('59', {'name': 'עיפאת בת שלום (סלים)', 'ref': IYFAT, 'note': '= אדם #' + IYFAT + '; נישא לה ב-1922'}, '#' + IYFAT)
addsp('92', {'name': 'פתח-אלה בן חביב הצפרי', 'ref': '236', 'note': '= אדם #236; נישאה לו אחרי סעד בן שלמה הצפרי'}, '#236')
addsp('236', {'name': 'זינאב (פגעה) בת אבּ-ספֿוה שהראן', 'ref': '92', 'note': '= אדם #92; נישא לה אחרי 1909'}, '#92')
addsp('93', {'name': 'סוריה בת יעקב הצפרי', 'ref': '212', 'note': '= אדם #212; נישא לה אחרי 1909'}, '#212')
for i, s in enumerate(P['212']['spouses']):
    if 'שלמה בן אב-סכוה' in nk(s['name']):
        setsp('212', i, name='משלמה בן אבּ-ספֿוה הדנפי', ref='93', note='= אדם #93; נישאה לו אחרי 1909 (עמ׳ 82, תרשים עמ׳ 97)')
for i, s in enumerate(P['116']['spouses']):
    if 'שלח בן אברהם' in nk(s['name']):
        setsp('116', i, name='שלח בן אברהם בן שלמה המטרי', ref='253', note='= אדם #253')
for i, s in enumerate(P['253']['spouses']):
    if s.get('ref') == '116': setsp('253', i, name='נסילה (וסילה)', note='= אדם #116')
S117 = P['117']['spouses']
setsp('117', 0, name='אברהם בן סעד המרחיבי', ref='203', note='= אדם #203; מת ב-1902')
setsp('117', 1, name='אברהם בן עבד-חנונה הסתרי', ref='140', note='= אדם #140')
if not any('שלישית' in s['name'] for s in P['85']['spouses']):
    P['85']['spouses'].append({'name': 'אשה שלישית (שמה אינו ידוע)', 'note': 'עמ׳ 82: «נישא לשלוש נשים … שם האשה השלישית אינו ידוע»'}); LOG.append({'spouse_added': '85', 'name': 'אשה שלישית'})

# ---------------------------------------------------------------- D. missing persons (before 1909)
def add(pid, name, sex, father, birth=None, death=None, note='', spouses=None):
    if pid in P: return
    n = {'id': pid, 'name': name, 'sex': sex, 'father_id': father}
    if birth: n['birth'] = birth
    if death: n['death'] = death
    if note: n['note'] = note
    if spouses: n['spouses'] = spouses
    FAMOF[father]['persons'].append(n); P[pid] = n; FAMOF[pid] = FAMOF[father]
    ch = P[father].setdefault('children_ids', [])
    if pid not in ch: ch.append(pid)
    LOG.append({'new': pid, 'name': name, 'father': father})


add('דנ-עארוף110', 'עארוף', 'M', '110', note='בן אברהם (#110) ולפיפה (#114); «מת צעיר» (עמ׳ 84, 85).')
add('דנ-אלקוע101', 'אל-קוע', '', '101', note='ילד של סעד (#101) ופאתבה; כונה «יאל-קוע», שמו המקורי לא זכור; מת בילדותו (עמ׳ 84).')
add('דנ-נזמיה58', 'נזמיה', 'F', '58', death=ah(1967), spouses=[{'name': 'עפיף בן זבולן הדנפי', 'ref': '46', 'note': '= אדם #46; נישאה לו אחרי 1909'}],
    note='בת עבד-אלה (#58) ומרים; נולדה אחרי 1909 (בת הזקונים), נפטרה 1967; אשת עפיף (#46) — עמ׳ 78 ועמ׳ 74.')
addsp('46', {'name': 'נזמיה בת עבד-אלה הדנפי', 'ref': 'דנ-נזמיה58', 'note': '= אדם #דנ-נזמיה58; נישא לה אחרי 1909'}, '#דנ-נזמיה58')

# ---------------------------------------------------------------- F. the three women removed on 6.11.2026 — now placed
arch = {r['person']['id']: r for r in removed}
for pid, father, spouses_new in (
        ('108', '100', None), ('105', '104', None), ('106', '104', None)):
    if pid in P: continue
    r = arch[pid]; p = r['person']
    p['father_id'] = father
    FAMOF[father]['persons'].append(p); P[pid] = p; FAMOF[pid] = FAMOF[father]
    ch = P[father].setdefault('children_ids', []);
    if pid not in ch: ch.append(pid)
    if r.get('story'): stories[pid] = r['story']
    LOG.append({'restored': pid, 'name': p['name'], 'father': father})
# marriages
for pid, name, ref in (('105', 'חילמי בן יעקב השלבי', '78'),):
    P[pid]['spouses'] = [{'name': name, 'ref': ref, 'note': '= אדם #' + ref}]
P['108']['spouses'] = [{'name': 'אבּ-ספֿוה "שהראן" בן אברהם בן שלח', 'ref': '89', 'note': '= אדם #89; אשתו הראשונה, אם אברהם (#90)'}]
P['106']['spouses'] = [{'name': 'ישמעאל (גמעאל) בן שלח', 'ref': '98', 'note': '= אדם #98; ללא ילדים'},
                       {'name': 'פתח-אלה בן חביב הצפרי', 'ref': '236', 'note': '= אדם #236; נישאה לו אחרי מות בעלה הראשון'}]
for i, s in enumerate(P['78']['spouses']):
    if 'עפיפה' in nk(s['name']): setsp('78', i, ref='105', note='= אדם #105')
addsp('236', {'name': 'חפיזה בת שלמה הדנפי', 'ref': '106', 'note': '= אדם #106; נישא לה אחרי מות בעלה'}, '#106')
for i, s in enumerate(P['104']['spouses']):
    if 'סנעאד' in nk(s['name']) or 'סגאר' in nk(s['name']): setsp('104', i, ref='131', note='= אדם #131; נישואין שלישיים (אם עפיפה וחפיזה)')
for i, s in enumerate(P['98']['spouses']):
    if 'חפיזה' in nk(s['name']): setsp('98', i, ref='106', note='= אדם #106; ללא ילדים')
for i, s in enumerate(P['89']['spouses']):
    if 'חפיזה' in nk(s['name']): setsp('89', i, ref='108', note='= אדם #108; אם הבן הראשון')
P['104']['children_ids'] = ['105', '106']
P['100']['children_ids'] = sorted(set(P['100'].get('children_ids') or []) | {'108'}, key=lambda x: (not x.isdigit(), int(re.match(r'\d+', x).group()) if re.match(r'\d+', x) else 0, x))

# ---------------------------------------------------------------- G. aliases / H. stories
for pid, t in (('48', None), ('90', 'כונה «אלערג׳ה הקטן» (חלש ומסכן) — עמ׳ 82.'), ('91', 'כונה «סאלם שהראן» — עמ׳ 82.'),
               ('113', 'כונה «סלים יאגי» — נולד כמאוס בלידה קשה (תאומו מת) — עמ׳ 84, 85.'), ('75א', 'כונתה «אליס = מחאסן» — עמ׳ 80.'), ('107', 'כונתה «יאם אלאמעלי» אחרי נישואיה לישראל הסתרי — עמ׳ 84.')):
    if pid == '48':
        if P['48']['name'] != 'אברהם = חליל': LOG.append({'renamed': '48', 'from': P['48']['name'], 'to': 'אברהם = חליל'}); P['48']['name'] = 'אברהם = חליל'
    else: addnote(pid, t)
SM = [('60', 'בעל חנות לדברי סידקיה ובדים. נהרג ברעידת האדמה הגדולה של 1927. הקים משפחה אחרי 1909.', '1894–1927'),
      ('61', 'חי בעוניו כל ימיו; שליח במשרד הטאבו ב-15 שנות חייו האחרונות; לא כל כך התמצא בשיראן. הקים משפחה אחרי 1909.', '1897–1968'),
      ('62', 'עקרת בית. אחרי 1909 נישאה לתמים בן אפרים הדנפי.', '1900–1979'),
      ('63', 'עבד בטאבו לאחר מות אחיו מנגיר; למד את כל חלקות הטאבו ופרש לגימלאות; לא עסק בנושאים שומרוניים. הקים משפחה אחרי 1909.', '1902–1976'),
      ('65', 'נולדה ב-1906.', '1906–')]
for pid, t, g in SM:
    if pid not in stories: stories[pid] = {'t': t, 'g': g}; LOG.append({'story': pid})

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('danfim_certain_applied_20261109.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(len(LOG), 'changes')
