# -*- coding: utf-8 -*-
# Rebuilds the missing Hesatri (Sarawi) "סעד בן ישמעאל" branch from the original
# transcript page_89_hasatri_prose.txt, and grafts it under census #121 (ישמעאל,
# the Hesatri progenitor).  Chain: סעד → אבּ-ספֿוה(=אב-סכוה) → אסעד → modern.
import json, io

master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))

# locate the Hesatri family + its progenitor #121
hes_fam = None
for h in master['houses']:
    for f in h.get('families', []):
        if 'הסתרי' in f.get('family', ''):
            hes_fam = f
ids = {p['id'] for f in (fam for h in master['houses'] for fam in h['families']) for p in f['persons']}

def P(pid, name, sex, father, gyears, t, children=None):
    p = {"id": pid, "name": name, "sex": sex}
    if father: p["father_id"] = father
    if children: p["children_ids"] = children
    hes_fam['persons'].append(p)
    stories[pid] = {"t": t, "g": gyears}

# remove if previously added (idempotent)
hes_fam['persons'] = [p for p in hes_fam['persons'] if not str(p['id']).startswith('הס-')]

# attach סעד as a son of #121 (its children list gets him too)
prog = next(p for f in (fam for h in master['houses'] for fam in h['families']) for p in f['persons'] if p['id'] == '121')
prog.setdefault('children_ids', [])
if 'הס-סעד' not in prog['children_ids']:
    prog['children_ids'].append('הס-סעד')

P('הס-סעד', 'סעד בן ישמעאל', 'M', '121', '1824–1882',
  'בן ישמעאל הסתרי, אחי ישראל ועבד-חנונה. משירה. נשא את זמהרה בת יעקב הצפרי. ילדיו: אבּ-ספֿוה, עבד-הרחום וקמרה.',
  children=['הס-אבספוה', 'הס-עבדהרחום', 'הס-קמרה'])
P('הס-אבספוה', 'אבּ-ספֿוה (אב-סכוה)', 'M', 'הס-סעד', '1854–1912',
  'בן סעד. היסטוריון ופקיד אצל סוחרי שכם; חיבר מילונים ערבית-עברית. נשא את אמינה בת אבּ-ספֿוה הדנפי. ילדיו: סעדיה, רסמיה ואסעד.',
  children=['הס-סעדיה', 'הס-רסמיה', 'הס-אסעד'])
P('הס-סעדיה', 'סעדיה', 'F', 'הס-אבספוה', '1887–1950',
  'בת אבּ-ספֿוה. הראשונה שלמדה לקרוא ערבית מאביה. נישאה לפרץ בן אברהם הצפרי.')
P('הס-רסמיה', 'רסמיה', 'F', 'הס-אבספוה', '1891–1972',
  'בת אבּ-ספֿוה. נישאה לאברהם בן יוסף בן עבד-חנונה הסתרי.')
P('הס-אסעד', 'אסעד (סעד)', 'M', 'הס-אבספוה', '1896–1974',
  'בן אבּ-ספֿוה. חנווני; חנות מכולת; עבד ביפו; בקיא בתרגום מילים מערבית לעברית מן המילונים שחיבר אביו. (אבי הענף הסראוי המודרני; השם נכתב גם "סעד".)')
P('הס-עבדהרחום', 'עבד-הרחום', 'M', 'הס-סעד', '1856–1917',
  'בן סעד. רוכל; מכר דברי סדקית בכפרים. נשא את מרים בת חביב הצפרי. ילדיו: נבון, לגזה, וגֿיה וצער.',
  children=['הס-נבון', 'הס-לגזה', 'הס-וגיה', 'הס-צער'])
P('הס-נבון', 'נבון (פֿתֻמַי)', 'M', 'הס-עבדהרחום', '1901–',
  'בן עבד-הרחום. עבד אצל סוחר בשכם, פתח חנות בדים, עבר לחולון; העתיק ספרים; ידע בראשית ושמות בעל-פה.')
P('הס-לגזה', 'לֻגֿזה (רוזה)', 'F', 'הס-עבדהרחום', '1902–1985',
  'בת עבד-הרחום. נישאה ליששכר בן אברהם המרחיבי; בעלת תפישה מהירה; בקיאה במסורות ובחשבון הימים.')
P('הס-וגיה', "וגֿ'יה (ע'גֿ'יה)", 'M', 'הס-עבדהרחום', '1905–',
  'בן עבד-הרחום. רוכל בדים, פתח חנות בדים; בקיא בתפילה ובספרי בראשית ושמות; זקן צלותה.')
P('הס-צער', 'צער (סֻפֿחִי)', 'M', 'הס-עבדהרחום', '1908–1918',
  'בן עבד-הרחום. ילד פיקח; מת ממחלה בילדותו.')
P('הס-קמרה', 'קמרה (ירחה)', 'F', 'הס-סעד', '1859–1941',
  'בת סעד. נישאה לאברהם מרחיב הצפרי; חיה עמו ביפו.')

# --- page_88: ENRICH existing census people (do NOT duplicate). ---
# Earlier these were wrongly added as new הס- nodes; the census already has them:
#   תמים = #133 (בן ישראל #122) · פוזי = #134 (אחי תמים, בן ישראל) ·
#   ישמעאל(חיכמת) = #129 (בן ישמעאל #123, נולד 4 ימים אחרי מות אביו).
def has(pid): return any(p['id'] == pid for f in (fam for h in master['houses'] for fam in h['families']) for p in f['persons'])
def getp(pid):
    for f in (fam for h in master['houses'] for fam in h['families']):
        for p in f['persons']:
            if p['id'] == pid: return p
    return None
if getp('133'):
    stories['133'] = {'t': 'תמים (פֿאמל) בן ישראל. אדם חכם; עסק בכתיבת עצומות ובקשות לבתי משפט; מנהל חשבונות אצל סוחרים; העתיק כתבי-יד רבים בעברית ובערבית ומכר לחו"ל. חי ביפו עם בנו 1940–1947, שב לשכם. נשא את זינאב (פועה) בת אברהם.', 'g': '1870–1949'}
if getp('134'):
    stories['134'] = {'t': 'פוֹזי בן ישראל, אחי תמים. לא למד מקצוע; למד לכתוב מאחיו ועזר לו בכתיבת בקשות; חלה בנמק ברגלו ומת במהלך ניתוח קטיעה.', 'g': '1872–1923'}
if getp('129'):
    getp('129')['name'] = 'ישמעאל (חיכמת)'
    stories['129'] = {'t': 'נקרא על שם אביו ישמעאל, שמת ארבעה ימים לפני לידתו. חייט; למד תורה; ידע על-פה ספרי בראשית ושמות; משירה; העתיק כתבי-יד רבים.', 'g': '1904–1985'}
# NOTE: the tailor "עבד-חנונה (עבד אללטיף, 1903)" of page_88 line 32 is NOT a direct
# son of #135 (born 1818 — an 85y gap is impossible). He is a later descendant named
# after his ancestor #135; the prose doesn't give his father, so per "no uncertain
# links" he is NOT added. (Was wrongly added as הס-עבדחנונה135; removed.)
if has('135'):
    g135 = getp('135'); g135.setdefault('children_ids', [])
    g135['children_ids'] = [c for c in g135['children_ids'] if c not in ('הס-תמים', 'הס-עבדחנונה135')]
# אברהם #140 -> עבד-אלה, סלים (נולדו אחרי 1909)
if has('140'):
    getp('140')['children_ids'] = ['הס-עבדאלה140', 'הס-סלים140']
P('הס-עבדאלה140', 'עבד-אלה', 'M', '140', '',
  'בן אברהם בן עבד-חנונה (נולד אחרי 1909).')
P('הס-סלים140', 'סלים', 'M', '140', '',
  'בן אברהם בן עבד-חנונה (נולד אחרי 1909).')

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
print('added Hesatri סעד branch:', sum(1 for p in hes_fam['persons'] if str(p['id']).startswith('הס-')), 'persons')
