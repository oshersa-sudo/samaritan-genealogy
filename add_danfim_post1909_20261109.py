# -*- coding: utf-8 -*-
# 2026-11-09 — owner: «בתוך ענף הדנפים בלבד, הוסף ילידים אחרי 1909 — רק אם הזיהוי ודאי מול העץ ב-100%».
# A registry (Excel) person born after 1909 is added only when ALL of these hold:
#   1. exactly one Danfim census man carries the father's given name AND has a wife with the mother's given name (the mother's name breaks every tie);
#   2. every other census man of that name is excluded (a known wife with another name, or too young / already dead);
#   3. an independent source confirms the same parents — the Arabic events file gives the full lineage (father + grandfather, mother + her father)
#      that equals the census couple, or the prose (page 78) names the child.
# 17 persons pass; the 18th (M46 שלביה) is the daughter «שלביה» who is already on the site as «ר-שלביה» — it is merged into her, not added.
# Idempotent; log in danfim_post1909_added_20261109.json
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
integ = json.load(io.open('integrate.json', encoding='utf-8'))
arch = {m['id']: m for m in json.load(io.open('excel_layer_archive.json', encoding='utf-8'))['modern']}
master = json.load(io.open('master_v2.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
present = {m['id'] for m in integ['modern']}
LOG = []
SIBL = "65בּ'"
BIRTHPARENT = {  # registry id -> census father
    'M35': '53', 'M41': '53', 'M55': '53', 'M76': '53',                      # אברהם בן יוסף בן יוסף (#53) ותמאם בת הכהן יצחק עמרם
    'M44': next(i for i in P if i.startswith('65') and re.sub('[֑-ׇ]', '', P[i]['name']) == 'שלום'), 'M100': None,   # שלום/סלים (#65בּ') ורפיקה (#68)
    'M56': '60', 'M67': '60', 'M77': '60', 'M91': '60',                      # סלים בן עבד-אלה (#60) ולוטפיה בת זבולן (#47)
    'M69': '69', 'M83': '69', 'M115': '69', 'M121': '69', 'M149': '69', 'M165': '69', 'M188': '69',   # תמים כאמל בן אפרים (#69) ובדריה בת עבד-אלה (#62)
}
BIRTHPARENT['M100'] = BIRTHPARENT['M44']
RENAME = {'M44': 'סמירה (פרידה)'}
SPOUSE = {'M35': {'name': 'עזיזה בת סלים', 'ref': 'M56'}, 'M56': {'name': 'ישמעאל בן אברהם', 'ref': 'M35'}}      # the registry notes + the events file: ישמעאל בן אברהם ↔ עזיזה בת סלים


def norm(s):
    s = re.sub(r'\s+', ' ', s or '').strip()
    s = re.sub(r'\(\s+', '(', s); s = re.sub(r'\s+\)', ')', s); s = re.sub(r'\s*\(', ' (', s)
    return s


for rid, fid in BIRTHPARENT.items():
    if rid in present: continue
    m = json.loads(json.dumps(arch[rid], ensure_ascii=False))
    m['parent'] = '#' + fid
    m['name'] = RENAME.get(rid) or norm(m['name'])
    for fld in ('mother', 'father', 'notes', 'job', 'bplace', 'family'):
        if m.get(fld): m[fld] = norm(m[fld])
    if rid in SPOUSE: m['spouses'] = [SPOUSE[rid]]
    m.pop('synth', None)
    integ['modern'].append(m); LOG.append({'added': rid, 'name': m['name'], 'parent': m['parent'], 'born': m['byear']})

# M46 «שלביה» (b.1917, a lawyer) is the daughter «שלבְֿיֶה» already on the site: merge
p = P['ר-שלביה']
if 'M46' not in (p.get('alt_ids') or []):
    p['alt_ids'] = sorted(set((p.get('alt_ids') or []) + ['M46']))
    p['birth'] = p.get('birth') or round((1917 - 621.57) * 1.030684)
    t = 'ברשם הקהילה (מיפקד.xlsx) נרשמה גם כ-M46 — «שלביה בת שלבי ומלכה, נולדה 1917, עורכת דין, שכם»; אותה בת (נולדה אחרי 1909), אוחדה לכאן. אמה: מלכה (#186), אשת שלבי אחרי 1909.'
    p['note'] = ((p.get('note') or '') + ' ' + t).strip()
    LOG.append({'merged': 'M46', 'into': 'ר-שלביה'})
d = json.load(io.open('merge_decisions.json', encoding='utf-8'))
if not any(x.get('away') == 'M46' for x in d['merges']):
    d['merges'].append({'keep': 'ר-שלביה', 'away': 'M46', 'applied': '2026-11-09', 'why': 'שלביה בת שלבי (#75) ומלכה (#186), נולדה 1917 — כבר באתר כ«ר-שלביה» (בת שלבי שנולדה אחרי 1909, עמ׳ 80)'})
io.open('merge_decisions.json', 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
r = json.load(io.open('registry_merged_20261109.json', encoding='utf-8')); r['M46'] = 'ר-שלביה'
io.open('registry_merged_20261109.json', 'w', encoding='utf-8').write(json.dumps(r, ensure_ascii=False, indent=1))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('danfim_post1909_added_20261109.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(len(LOG), 'changes')
