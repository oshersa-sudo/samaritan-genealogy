# -*- coding: utf-8 -*-
# 2026-11-10 — owner: add the post-1909 descendants of the Danfim that are CERTAIN, leave the rest.
# Selection: scan_post1909_certain_20261110.py (unique father by name + age + the father's wife = the child's mother; closure over generations).
#  * 38 new persons attached;  * 6 registry persons that are the SAME people already on the site are merged (alt_ids) instead of added;
#  * left out as uncertain: M38 «נג'לא» (probably the prose's «יוכבד» — different name), and everything the scan could not settle.
#  * Hana (M579): the drowning (2012) added as a story and as her year of death.
# Idempotent. Log: post1909_certain_added_20261110.json
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))
arch = {m['id']: m for m in json.load(io.open('excel_layer_archive.json', encoding='utf-8'))['modern']}
scan = json.load(io.open('post1909_certain_scan_20261110.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
M = {m['id']: m for m in integ['modern']}
LOG = []


def ah(g): return round((g - 621.57) * 1.030684)


def norm(s):
    s = re.sub(r'\s+', ' ', s or '').strip()
    s = re.sub(r'\(\s+', '(', s); s = re.sub(r'\s+\)', ')', s); s = re.sub(r'\s*\(', ' (', s)
    return s


# ---- merges: registry person == person already on the site
MERGE = {  # registry id -> (on-site master id, birth year to set if the card has none, note)
    'M36': ('דנ-ורדה-גמליאל', 1912, 'ברשם הקהילה: «ורדה בת ג׳מיל והדיה, נולדה 1912»; סגל המאורעות: נולדה בין 1909 ל-1913.'),
    'M37': ('דנ-נדיה-זבולן', 1912, 'ברשם הקהילה וסגל המאורעות: נולדה 1912.'),
    'M63': ('דנ-אבסכוה-גמליאל', 1922, 'ברשם הקהילה: «מורגן (אב סיכוה) בן ג׳מיל והדיה, נולד 1922»; סגל המאורעות: נולד 1921–1922. מרג׳אן = אב-סכוה.'),
    'M28': ('54', None, 'ברשם הקהילה נרשם «עבד אללטיפ בן אברהם ותמאם, נולד 1906» — אותו אדם.'),
    'M9': ('128', None, 'ברשם הקהילה נרשם «סברי בן ישמעאל ובדיעה, נולד 1899» — אותו אדם.'),
    'M26': ('62', None, 'ברשם הקהילה נרשמה «בדריה בת עבדאלה ומרים, נולדה 1905»; לפי המלל והמפקד נולדה ≈1900.'),
}
rm = json.load(io.open('registry_merged_20261109.json', encoding='utf-8'))
md = json.load(io.open('merge_decisions.json', encoding='utf-8'))
for rid, (pid, by, note) in MERGE.items():
    p = P[pid]
    if rid in (p.get('alt_ids') or []): continue
    p['alt_ids'] = sorted(set((p.get('alt_ids') or []) + [rid]))
    if by and not p.get('birth'): p['birth'] = ah(by)
    if note not in (p.get('note') or ''): p['note'] = ((p.get('note') or '') + ' ' + note).strip()
    x = arch.get(rid) or {}
    if x.get('notes') and not p.get('spouses') and re.search('נישא', x['notes']):
        p['spouses'] = [{'name': re.sub(r'^נישא(?:ה)? ל', '', x['notes']).strip(), 'note': 'לפי רשם הקהילה'}]
    rm[rid] = pid
    md['merges'].append({'keep': pid, 'away': rid, 'applied': '2026-11-10', 'why': 'אותו אדם: אב ואם זהים, שם ושנת לידה תואמים (בדיקה מול המלל/סגל המאורעות)'})
    LOG.append({'merged': rid, 'into': pid})
io.open('registry_merged_20261109.json', 'w', encoding='utf-8').write(json.dumps(rm, ensure_ascii=False, indent=1))
io.open('merge_decisions.json', 'w', encoding='utf-8').write(json.dumps(md, ensure_ascii=False, indent=1))

# ---- additions
SKIP = set(MERGE) | {'M38'}
REPARENT = {'M302': 'דנ-אבסכוה-גמליאל'}        # his father M63 is the on-site אב-ספוה
for rid, fid in scan['fresh'].items():
    if rid in SKIP or rid in M: continue
    fid = REPARENT.get(rid, fid)
    m = json.loads(json.dumps(arch[rid], ensure_ascii=False))
    m['parent'] = fid if (fid.startswith('M')) else '#' + fid
    m['name'] = norm(m['name']); m.pop('synth', None)
    for fld in ('mother', 'father', 'notes', 'job', 'bplace', 'family'):
        if m.get(fld): m[fld] = norm(m[fld])
    integ['modern'].append(m); M[rid] = m; LOG.append({'added': rid, 'name': m['name'], 'parent': m['parent']})

# ---- Hana (M579): the drowning, 2012
h = M['M579']; h['dyear'] = 2012
h['notes'] = 'נספתה ב-2012 באסון טביעה במי גשמים: מונית ערבית שנפלה אל התהום בחזרתה מלימודיה; נספתה יחד עם חברתה ללימודים, וגופתה נמצאה כעבור כמה ימים. לא נישאה ונפטרה ללא משפחה. ירחמה יהוה.'
stories['M579'] = {'t': 'בת חבר (סמיר) ווידאד, הגדולה מבין שריהאן. ב-2012 נספתה באסון טביעה במי גשמים: מונית ערבית שנפלה אל התהום בחזרתה מלימודיה. היא נספתה יחד עם חברתה ללימודים, וגופתה נמצאה כעבור כמה ימים. לא נישאה ונפטרה ללא משפחה. ירחמה יהוה.', 'g': '1989–2012'}
LOG.append('M579 died 2012')

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('post1909_certain_added_20261110.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(sum(1 for x in LOG if isinstance(x, dict) and 'added' in x), 'added;', sum(1 for x in LOG if isinstance(x, dict) and 'merged' in x), 'merged')
