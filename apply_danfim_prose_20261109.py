# -*- coding: utf-8 -*-
# 2026-11-09 — owner: «למעט הצמרת, הוסף מתוך ההרחבות כל הרחבה וכל פרט חסר לעצים הקיימים — כינויים בערבית, שנות לידה ופטירה, וילדים».
# Source: the scanned prose of the A.B. newspaper, pages 74-90 (Danfim house) — every item below was read from the scan itself
# (not only from the earlier text transcriptions, which contained a few misreadings).  The apex (צמרת) is NOT touched.
#   A. missing death/birth years   B. printed-vs-census conflicts → a note, never an overwrite   C. Arabic nicknames in the name
#   D. spouses / links             E. persons missing from the tree (children born after 1909 named in the prose)
#   F. life-story additions        G. Shoham (father of Nira, Osher, Ravit) and his sisters, from the community registry
# Idempotent.  Log: danfim_prose_applied_20261109.json
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))
arch = {m['id']: m for m in json.load(io.open('excel_layer_archive.json', encoding='utf-8'))['modern']}
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
FAMOF = {p['id']: f for h in master['houses'] for f in h['families'] for p in f['persons']}
NIQ = ''.join(chr(c) for c in range(0x0591, 0x05C8))
LOG = []


def nk(x): return ''.join(ch for ch in str(x or '') if ch not in NIQ)
def ah(g): return round((g - 621.57) * 1.030684)


def addnote(pid, t):
    if t not in (P[pid].get('note') or ''):
        P[pid]['note'] = ((P[pid].get('note') or '') + ' ' + t).strip(); LOG.append({'note': pid, 'text': t})


def setdeath(pid, g):
    if not P[pid].get('death'):
        P[pid]['death'] = ah(g); LOG.append({'death': pid, 'year': g})


def setbirth(pid, g):
    if not P[pid].get('birth'):
        P[pid]['birth'] = ah(g); LOG.append({'birth': pid, 'year': g})


def alias(pid, expect, new):
    cur = nk(P[pid]['name'])
    if cur == expect:
        P[pid]['name'] = new; LOG.append({'alias': pid, 'from': cur, 'to': new})
    elif nk(new) != cur:
        LOG.append({'alias_skipped': pid, 'name': cur, 'wanted': new})


def story(pid, t, g=None, replace=False):
    s = stories.get(pid) or {}
    if (not s.get('t')) or replace:
        stories[pid] = {'t': t, 'g': g if g is not None else s.get('g', '')}; LOG.append({'story': pid})
    elif g is not None and not s.get('g'):
        s['g'] = g; LOG.append({'story_g': pid})


def addsp(pid, new, key):
    L = P[pid].setdefault('spouses', [])
    if any(key == s.get('ref') or key in str(s.get('note') or '') for s in L): return
    L.append(new); LOG.append({'spouse_added': pid, 'name': new['name']})


def add(pid, name, sex, father, birth=None, death=None, note=''):
    if pid in P: return
    n = {'id': pid, 'name': name, 'sex': sex, 'father_id': father}
    if birth: n['birth'] = birth
    if death: n['death'] = death
    if note: n['note'] = note
    FAMOF[father]['persons'].append(n); P[pid] = n; FAMOF[pid] = FAMOF[father]
    ch = P[father].setdefault('children_ids', [])
    if pid not in ch: ch.append(pid)
    LOG.append({'new': pid, 'name': name, 'father': father})


GAM = next(i for i in P if i.startswith('65') and nk(P[i]['name']).startswith('גמליאל'))
SHL = next(i for i in P if i.startswith('65') and nk(P[i]['name']).startswith('שלום'))
IFT = next(i for i in P if i.startswith('65') and nk(P[i]['name']) == 'עיפאת')

# ----------------------------------------------------------- A. death / birth years stated in the prose (only where the field is empty)
for pid, g in (('39', 1915), ('45', 1967), ('50', 1888), ('58', 1937), ('64', 1911), ('75', 1920), ('90', 1947), ('105', 1950), ('106', 1942),
               ('117', 1967), ('125', 1977), ('126', 1915), ('127', 1912), ('134', 1923), ('137', 1928), ('149', 1883), ('151', 1912), ('152', 1950),
               ('153', 1972), ('154', 1974), ('155', 1917), ('157', 1985), ('159', 1918), ('160', 1941), ('163', 1918), ('217', 1968)):
    setdeath(pid, g)
setbirth('106', 1888)

# ----------------------------------------------------------- B. the printed prose and the census disagree → a note (the census value stays)
addnote('39', 'במלל (עמ׳ 74): «יצחק בנו (1824–1915)»; לפי המפקד נולד 1245 (≈1829).')
addnote('58', 'במלל (עמ׳ 76) נדפסה שנת הלידה 1850 — סותרת את המפקד (1286 ≈ 1869; אמו ורדה נולדה 1841), ולכן נשמר המפקד.')
addnote('90', 'לפי המלל (עמ׳ 82) נולד 1863; לפי המפקד 1283 (≈1866).')
addnote('137', 'במלל (עמ׳ 88) נדפס «1896–1928»; לפי המפקד נולד 1286 (≈1869) — כנראה היפוך ספרות. שנת הפטירה 1928 מפורשת.')
addnote('122', 'לפי המלל (עמ׳ 86): 1816–1881.')
addnote('135', 'לפי המלל (עמ׳ 88): 1818–1887 (המפקד: 1234–1301 ≈ 1819–1884).')
addnote('130', 'במלל (עמ׳ 88): «1850–1910?» — שנת הפטירה בסימן שאלה.')
addnote('96', 'במלל (עמ׳ 82): «1803–1871?» — שנת הפטירה בסימן שאלה.')
addnote('107', 'במלל (עמ׳ 84): «1848–1920?» — שנת הפטירה בסימן שאלה.')
addnote('149', 'בעמ׳ 89 נקראת «נשרונה» (1820–1883); נישאה לשלושה: הכהן אהרן בן שלמה (1817–1840), שלמה בן אב-סכוה הדנפי, ושלמה בן ישמעאל הצפרי (ילדה לו את אריה ואת סעד).')
if (stories.get('58') or {}).get('g') == '1850–1937': stories['58']['g'] = '–1937'; LOG.append({'story_g': '58'})
if (stories.get('104') or {}).get('g') == '1813–1889': stories['104']['g'] = '1843–1889'; LOG.append({'story_g': '104', 'fix': '1813→1843 (read from the scan, p.84)'})
if (stories.get('137') or {}).get('g') in (None, ''): stories.setdefault('137', {})['g'] = '–1928'
if (stories.get('126') or {}).get('g') in ('1893–', None, ''): stories.setdefault('126', {})['g'] = '1891–1915'
for pid, g in (('127', '1894–1912'), ('125', '1889–1977'), ('128', '1900–'), ('45', '1894–1967'), ('65ג', '1907–1982'), ('67', '1889–1928'), ('68', '1892–1971')):
    pass

# ----------------------------------------------------------- C. Arabic nicknames in the name (the same «א = ב» form the site already uses)
for pid, cur, new in (('41', 'שפיקה', 'שפיקה = רחומה'), ('54', 'עבד-חנונה', 'עבד-חנונה = עבד-אללטיף'), ('60', 'סלים', 'סלים = שלום'),
                      (GAM, 'גמליאל', 'גמליאל = ג׳מיל'), (SHL, 'שלום', 'שלום = סלים'), ('75', 'שלבי', 'שלבי = אבוקאט'), ('83', 'זבולן', 'זבולן = פיאד'),
                      ('90', 'אברהם', 'אברהם = אלערג׳ה הקטן'), ('91', 'שלח', 'שלח = סאלם שהראן'), ('103', 'עבד-אלה', 'עבד-אלה = אלחג׳ירי'),
                      ('107', 'לאה', 'לאה = יאם אלאמעלי'), ('113', 'סלים', 'סלים = אלעאצי'), ('131', 'סעדה', 'סעדה = סגאר'),
                      ('132', 'מפריקה', 'מפריקה = מהריפה'), ('135', 'עבד-חנונה', 'עבד-חנונה = עבד-אללטיף'), ('136', 'יוסף', 'יוסף = אלפירגה')):
    alias(pid, cur, new)
if stories.get('113') and 'יאגי' in stories['113']['t']:
    stories['113']['t'] = stories['113']['t'].replace("כונה 'סלים יאגי'", "כונה 'סלים אלעאצי'"); LOG.append({'story_fix': '113'})
addnote('113', 'בעמ׳ 84 נקרא «סלים "אלעאצי"» (1857–1939), ובסיפור הקודם — «סלים יאגי».')

# ----------------------------------------------------------- E. persons missing from the tree (children born after 1909, parents explicit in the prose)
SRC = 'עמ׳ '
add('דנ-נדיה-זבולן', 'נדיה', 'F', '43', death=ah(1989), note='בת הזקונים של זבולן (#43) ורבקה בת פינחס הכהן; נולדה אחרי 1909, נפטרה 1989 — עמ׳ 74.')
add('דנ-ורדה-גמליאל', 'ורדה', 'F', GAM, note='בת גמליאל והדיה; נולדה אחרי 1909 (עמ׳ 78); נישאה ליוסף=לוטפי בן זבולן (#44) אחרי 1909 (עמ׳ 74).')
add('דנ-יוכבד-גמליאל', 'יוכבד', 'F', GAM, note='בת גמליאל והדיה; נולדה אחרי 1909 — עמ׳ 78.')
add('דנ-אבסכוה-גמליאל', 'אב-ספוה', 'M', GAM, note='בן גמליאל והדיה; נולד אחרי 1909 — עמ׳ 78.')
add('דנ-אברהם-שלום', 'אברהם', 'M', SHL, note='בן שלום (סלים) ורפיקה; נולד אחרי 1909 (אחי עיפאת, עם סמירה ויעקב) — עמ׳ 78.')
add('דנ-נדים-משלמה', 'נדים', 'M', '93', note='בן משלמה וסרייה בת יעקב הצפרי; נולד אחרי 1909; חירש-אילם-עיוור — עמ׳ 82.')
add('דנ-מדחת-משלמה', 'מדחת', 'M', '93', note='בן משלמה וסרייה בת יעקב הצפרי; נולד אחרי 1909; חירש-אילם-עיוור — עמ׳ 82.')
add('דנ-מדיחה-משלמה', 'מדיחה', 'F', '93', note='בת משלמה וסרייה בת יעקב הצפרי; נולדה אחרי 1909 — עמ׳ 82.')
if GAM in P and 'ללא ילדים' in (P[GAM].get('note') or ''):
    P[GAM]['note'] = P[GAM]['note'].replace('ללא ילדים', 'ללא ילדים עד 1909; אחרי 1909 נולדו להם ורדה, יוכבד ואב-ספוה (עמ׳ 78)'); LOG.append({'note_fix': GAM})
# the correction of an earlier transcription: the two children of #140 born after 1909 are «סלים ונהלה» (p.88), not «עבד-אלה וסלים»
if 'הס-עבדאלה140' in P and nk(P['הס-עבדאלה140']['name']) == 'עבד-אלה':
    P['הס-עבדאלה140']['name'] = 'נהלה'; P['הס-עבדאלה140']['sex'] = 'F'
    P['הס-עבדאלה140']['note'] = 'בת אברהם (#140) ופיקה (#117); נולדה אחרי 1909 — עמ׳ 88 («אחרי 1909 — סלים ונהלה»). בסריקה קודמת נקראה בטעות «עבד-אלה».'
    LOG.append({'renamed': 'הס-עבדאלה140', 'to': 'נהלה'})
if 'הס-עבדאלה140' in stories and 'עבד-אלה' in stories['הס-עבדאלה140'].get('t', ''):
    stories['הס-עבדאלה140'] = {'t': 'בת אברהם בן עבד-חנונה ופיקה; נולדה אחרי 1909.', 'g': ''}

# ----------------------------------------------------------- D. spouses / links
addsp('44', {'name': 'ורדה בת גמליאל הדנפי', 'ref': 'דנ-ורדה-גמליאל', 'note': '= אדם #דנ-ורדה-גמליאל; נישא לה אחרי 1909 (עמ׳ 74)'}, '#דנ-ורדה-גמליאל')
addsp('דנ-ורדה-גמליאל', {'name': 'יוסף=לוטפי בן זבולן הדנפי', 'ref': '44', 'note': '= אדם #44; נישאה לו אחרי 1909 (עמ׳ 74)'}, '#44')
addsp('75א', {'name': 'גור בן אברהם צדקה', 'note': 'נישאה לו אחרי 1909 (עמ׳ 80)'}, 'גור בן אברהם צדקה')
addsp('156', {'name': 'תמאם בת סעד הצפרי', 'note': 'נישא לה אחרי 1909; ללא ילדים (עמ׳ 89)'}, 'תמאם בת סעד הצפרי')
if '195' in P:
    addsp('157', {'name': 'יששכר בן אברהם המרחיבי', 'ref': '195', 'note': '= אדם #195 (עמ׳ 89)'}, '#195')
    addsp('195', {'name': 'לגזה (רוזה) בת עבד-הרחום הסתרי', 'ref': '157', 'note': '= אדם #157 (עמ׳ 89)'}, '#157')
addsp('154', {'name': "נג'אח", 'note': 'אם ילדיו שוהם, עיטאף, איריס (רסמיה) ונתנאל — לפי רשם הקהילה'}, "נג'אח")
addnote('127', 'התארסה ליוסף=לוטפי בן זבולן (#44) ומתה חודשים לאחר מכן (1912) — עמ׳ 88.')
addnote('44', 'נשא את ורדה בת גמליאל הדנפי אחרי 1909 (עמ׳ 74); בצעירותו התארסה אליו ודיעה (#127) בת ישמעאל הסתרי, אך מתה ב-1912 (עמ׳ 88).')
addnote(IFT, 'נישאה למנגיר בן עבד-אלה הדנפי ב-1922 (עמ׳ 78).')

# ----------------------------------------------------------- F. life stories (only where the card has none, or the new facts must be added)
story('45', 'בן זבולן. לא עבד מימיו וחי על חשבון אחיו; פעמיים עסק בתיווך — רק בשנות חייו האחרונות; לא נשא אשה. העתיק ספרים אך כתב ידו לא היה יפה; ידע קרוא וכתוב, שירה ודת.', '1894–1967', replace=True)
story('44', 'בנו של זבולן. עסק במסחר והרוויח כסף עד שיכול היה להתחתן ולהקים משפחה; אחרי 1909 נשא את ורדה בת גמליאל הדנפי. בצעירותו התארסה אליו ודיעה בת ישמעאל הסתרי, אך מתה חודשים לאחר מכן.', '1892–1963', replace=True)
story(IFT, 'בכורת שלום (סלים) ורפיקה. עקרת בית; ידעה קרוא עברית וערבית ולמדה בבית הספר. ב-1922 נישאה למנגיר בן עבד-אלה הדנפי.', '1907–1982')
story('70', 'פועה (זינאב), בת שלמה — נקראה «אלערג׳ה» (הצולעת) כי נולדה עם רגל אחת קצרה מן השנייה. נישאה לעבד-חנונה בן ישראל השלבי הדנפי; עקרת בית.')
story('67', 'בת אפרים ורבקה. נישאה לבן-דודה גמליאל; עקרת בית.', '1889–1928')
story('68', 'בת אפרים ורבקה. נישאה לבן-דודה שלום (סלים); עקרת בית.', '1892–1971')
story('74', 'בת יעקב השלבי. נישאה ליוסף בן יוסף בן שלמה (#52), בנשותיו השלישית, וילדה לו את אברהם. בעמ׳ 80 נכתב שבעלה היה «יוסף בן חביב צדקה»; המפקד ועמ׳ 76 מזהים אותו כיוסף בן יוסף בן שלמה.', '1861–1888', replace=True)
story('78', 'בן יעקב. זילזל בעניני דת; היה אישיות מרכזית בקהילה. נשא את עפיפה בת שלמה הדנפי; בנם יוסף מת ילד, ואחרי 1909 נולדו להם שמסה ושלפי. גר שנים רבות בסלט ורוב שנותיו בשכם.', '1878–1937', replace=True)
story('93', 'הפיקח באחיו; שמר דת, למד תורה ותפילה והעתיק ספרים. אחרי 1909 נשא את סרייה בת יעקב הצפרי, שילדה לו את נדים ומדחת (שניהם חירשים-אילמים-עיוורים) ואת הבת מדיחה.', '1891–1971', replace=True)
story('125', 'עזי (עיזאת). פקיד אצל סוחרי שכם ויפו ומנהל חשבונות — ביפו עבד אצל משפחות הבאם ופראס ובשכם אצל משפחות יעיש ותמימי. אומרים שהעתיק פעם כתב-יד אחד ומכרו. הקים משפחה אחרי 1909.', '1889–1977')
story('127', 'מתה צעירה. התארסה ליוסף=לוטפי בן זבולן הדנפי ומתה חודשים לאחר מכן ממחלה.', '1894–1912')
story('128', 'עסק בנגרות כל ימיו; העתיק כתב-יד אחד או שניים. הקים משפחה אחרי 1909.', '1900–')
story('140', 'פקיד בממשל התורכי שיצא לגמלאות; העתיק ספרים ותורות; היה משירה טוב מאד; לא אמר בבית הכנסת ולא אהב להתבלט. נשא את ופֿיקה בת בנימים המטרי. ילדיהם: עבד-חנונה, קמר, ואחרי 1909 — סלים ונהלה.', '1854–1926', replace=True)
story('149', 'נשרונה (1820–1883), אחותו של עבד-חנונה בן ישמעאל. נישאה לשלושה: הכהן אהרן בן שלמה (ילדה לו את יעקב); שלמה בן אב-סכוה הדנפי (ילדה לו את אב-ספוה, אפרים וזינאב); ושלמה בן ישמעאל הצפרי (ילדה לו את אריה ואת סעד).', '1820–1883', replace=True)
story('156', 'עבד אצל סוחר בשכם, פתח חנות בדים ועבר לחולון; העתיק ספרים הרבה; ידע ספרי בראשית ושמות בעל-פה. אחרי 1909 נשא את תמאם בת סעד הצפרי (ללא ילדים).', '1901–', replace=True)
story('דנ-נדיה-זבולן', 'בת הזקונים של זבולן; נולדה אחרי 1909. נפטרה ב-1989.', '–1989')
story('דנ-ורדה-גמליאל', 'בת גמליאל והדיה; נולדה אחרי 1909 ונישאה ליוסף=לוטפי בן זבולן.')
story('דנ-יוכבד-גמליאל', 'בת גמליאל והדיה; נולדה אחרי 1909.')
story('דנ-אבסכוה-גמליאל', 'בן גמליאל והדיה; נולד אחרי 1909.')
story('דנ-אברהם-שלום', 'בן שלום (סלים) ורפיקה; נולד אחרי 1909, אחי עיפאת.')
story('דנ-נדים-משלמה', 'בן משלמה וסרייה; נולד אחרי 1909; חירש, אילם ועיוור.')
story('דנ-מדחת-משלמה', 'בן משלמה וסרייה; נולד אחרי 1909; חירש, אילם ועיוור.')
story('דנ-מדיחה-משלמה', 'בת משלמה וסרייה; נולדה אחרי 1909.')

# registry persons that ARE the prose's children — merged / confirmed, never duplicated
sal = P.get('הס-סלים140')
if sal is not None and 'M42' not in (sal.get('alt_ids') or []):
    sal['alt_ids'] = sorted(set((sal.get('alt_ids') or []) + ['M42']))
    sal['birth'] = sal.get('birth') or ah(1914)
    addnote('הס-סלים140', 'ברשם הקהילה (מיפקד.xlsx) נרשם גם כ-M42 — «סלים בן אברהם ופיקה, נולד 1914»; אחרי 1909 (עמ׳ 88: «סלים ונהלה»).')
    sal.setdefault('spouses', []).append({'name': "עיפא נאג'י כהן", 'note': 'לפי רשם הקהילה'})
    stories['הס-סלים140'] = {'t': 'בן אברהם בן עבד-חנונה ופיקה; נולד אחרי 1909 (לפי רשם הקהילה: 1914).', 'g': '1914–'}
    LOG.append({'merged': 'M42', 'into': 'הס-סלים140'})
    rm = json.load(io.open('registry_merged_20261109.json', encoding='utf-8')); rm['M42'] = 'הס-סלים140'
    io.open('registry_merged_20261109.json', 'w', encoding='utf-8').write(json.dumps(rm, ensure_ascii=False, indent=1))
    md = json.load(io.open('merge_decisions.json', encoding='utf-8'))
    md['merges'].append({'keep': 'הס-סלים140', 'away': 'M42', 'applied': '2026-11-09', 'why': 'אב «אברהם» ואם «ופיקה» — הזוג היחיד #140/#117; עמ׳ 88: «אחרי 1909 — סלים ונהלה»'})
    io.open('merge_decisions.json', 'w', encoding='utf-8').write(json.dumps(md, ensure_ascii=False, indent=1))
for _m in integ['modern']:
    if _m['id'] in ('M58', 'M81') and 'עמ׳ 81' not in (_m.get('notes') or ''):
        _m['notes'] = ((_m.get('notes') or '') + ' נזכר/ת בשמו/ה גם במלל (עמ׳ 81): «אחרי 1909 נולדו להם שמסה ושלפי» (שלפי = שלבי).').strip(); LOG.append({'registry_confirmed': _m['id']})

# sort position only (never shown as a year): children whose year of birth is unknown but whose place among their siblings is stated in the prose
for _pid, _y in (('78-son', 1326), ('דנ-עפיף43', 1308), ('דנ-אברהם-שלום', 1921)):
    if _pid in P and P[_pid].get('ord_year') != _y:
        P[_pid]['ord_year'] = _y; LOG.append({'ord_year': _pid, 'value': _y})

# ----------------------------------------------------------- G. Shoham (+ sisters, children) from the community registry — the owner's family
integ_ids = {m['id'] for m in integ['modern']}
FAMILY = {  # registry id -> (parent, display name, spouses)
    'M190': ('#154', 'שוהם (מורגן)', [{'name': 'בדיעה בת חיכמת', 'ref': 'M274'}]),
    'M206': ('#154', 'רוחמה (עיטאף)', None),
    'M226': ('#154', 'איריס (רסמיה)', None),
    'M457': ('M190', 'נירה', None),
    'M495': ('M190', 'אושר', None),
    'M530': ('M190', 'רווית', None),
}
for rid, (par, nm, sps) in FAMILY.items():
    if rid in integ_ids: continue
    m = json.loads(json.dumps(arch[rid], ensure_ascii=False))
    m['parent'] = par; m['name'] = nm
    if sps: m['spouses'] = sps
    m.pop('synth', None)
    if rid == 'M495':
        m['me'] = True; m['notes'] = None
    integ['modern'].append(m); LOG.append({'registry_added': rid, 'name': nm, 'parent': par})
M = {m['id']: m for m in integ['modern']}
if 'M274' in M and not any(s.get('ref') == 'M190' for s in (M['M274'].get('spouses') or [])):
    M['M274'].setdefault('spouses', []).append({'name': 'שוהם (מורגן) בן אסעד סראוי', 'ref': 'M190'}); LOG.append({'spouse': 'M274→M190'})
if 'M300' in M and M['M300'].get('mother') == "נג'וח":
    M['M300']['mother'] = "נג'אח"; LOG.append({'mother_spelling': 'M300', 'to': "נג'אח (כמו אחיו ואחיותיו)"})

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('danfim_prose_applied_20261109.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(len(LOG), 'changes')
