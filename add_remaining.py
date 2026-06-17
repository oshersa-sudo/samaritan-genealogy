# -*- coding: utf-8 -*-
# Fills the (modest) missing bridge-generation people of the remaining families from
# the transcripts (page_74–98). Each gap-person is added to the same family as their
# census father, with a father_id link. Prefer the transcript over the registry.
import json, io

master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
fam_of = {}
node = {}
for h in master['houses']:
    for f in h['families']:
        for p in f['persons']:
            node[p['id']] = p
            fam_of[p['id']] = f

# idempotent: drop previously added
for h in master['houses']:
    for f in h['families']:
        f['persons'] = [p for p in f['persons'] if not str(p['id']).startswith('ר-')]

def P(pid, name, sex, father, gy, t):
    fam = fam_of.get(father)
    if fam is None:
        print('  ! father missing for', name, father); return
    p = {"id": pid, "name": name, "sex": sex, "father_id": father}
    fam['persons'].append(p)
    fam_of[pid] = fam; node[pid] = p
    par = node[father]; par.setdefault('children_ids', [])
    if pid not in par['children_ids']: par['children_ids'].append(pid)
    if t or gy: stories[pid] = {"t": t, "g": gy}

# ===== אלטיף: ילדי עבד-אלה (#58) כבר במיפקד כ-#59–65 (אין לשכפל). =====
# רק העשרה: #59 ("(שם לאימות)") = מנגיר, הבן הבכור שירש את משרת הטאבו (page_78).
m59 = node.get('59')
if m59 and (m59.get('name') or '').startswith('(שם'):
    m59['name'] = 'מנגיר'
    stories['59'] = {'t': 'בנו הבכור של עבד-אלה; ירש את משרת אביו במשרד הטאבו לאחר שפרש; בעל כתב יפה בערבית; בעל מעמד בעדה.', 'g': '1891–1945'}
# עיפאת כבר במיפקד כ-#65ג (בת שלום #65בּ') — אין לשכפל.
# רבקה (#49) -> סלגֿח (אינה במיפקד)
P('ר-סלגח49', 'סַלֻגִֿח', 'F', '49', '', 'בת רבקה. אשת הכהן הגדול יעקב בן אהרן.')

# ===== שלבי: בת שלבי (#75) =====
P('ר-שלביה', 'שלבְֿיֶה', 'F', '75', '', 'בת שלבי (נולדה אחרי 1909).')

# ===== עבד-אלה/משלמה: בן סעדה (#115) =====
P('ר-אינמר', 'אינמר (פצֿיל)', 'M', '115', '', 'בן סעדה; מת צעיר.')

# ===== צפרים: בת יעקב אלעֻפֿאוי (#211) =====
P('ר-סרוריה', 'סֻרֻריה', 'F', '211', '1897–1976', 'בת יעקב. נישאה לצדקה בן אברהם הצפרי, ואחריו למשלמה בן אבּ-ספֿוה הדנפי.')

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
print('added remaining bridge people:', sum(1 for h in master['houses'] for f in h['families'] for p in f['persons'] if str(p['id']).startswith('ר-')))
