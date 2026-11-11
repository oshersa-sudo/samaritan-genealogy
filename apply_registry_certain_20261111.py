# -*- coding: utf-8 -*-
# 2026-11-11 — owner: from the census Excel (מיפקד.xlsx → excel_layer_archive.json), add to the Danfim tree every Danfi / Sarawi person that is CERTAIN; leave the rest.
# Selection: scan3_registry_20261111.py (unique father by name + age; wife on the father's card = the child's mother, OR the father's patronym witnessed
# by the events workbook; closure over generations).  Two registry persons are the SAME people already on the site and are merged (alt_ids), not added.
# Idempotent. Log: registry_certain_applied_20261111.json
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))
arch = {m['id']: m for m in json.load(io.open('excel_layer_archive.json', encoding='utf-8'))['modern']}
scan = json.load(io.open('registry_certain_scan3_20261111.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
M = {m['id']: m for m in integ['modern']}
LOG = []
def ah(g): return round((g - 621.57) * 1.030684)
def norm(s):
    s = re.sub(r'\s+', ' ', s or '').strip()
    s = re.sub(r'\(\s+', '(', s); s = re.sub(r'\s+\)', ')', s); s = re.sub(r'\s*\(', ' (', s)
    return s
rm = json.load(io.open('registry_merged_20261109.json', encoding='utf-8'))
md = json.load(io.open('merge_decisions.json', encoding='utf-8'))
MERGE = {
    'M30': ('65ג', None, 'ברשם הקהילה נרשמה «עיפה בת שלום ורבקה, 1908–1982, נישאה למנגיר בן עבדאלה» — אותה אישה (אב שלום, בעל מנגיר #59, נפטרה 1982).'),
    'M59': ('הס-עבדאלה140', 1921, 'ברשם הקהילה: «נהלה בת אברהם ופיקה, נולדה 1921» — אותה אישה; נישאה לחיכמת בן ישמעאל סראוי.'),
}
for rid, (pid, by, note) in MERGE.items():
    p = P[pid]
    if rid in (p.get('alt_ids') or []): continue
    p['alt_ids'] = sorted(set((p.get('alt_ids') or []) + [rid]))
    if by and not p.get('birth'): p['birth'] = ah(by)
    if note not in (p.get('note') or ''): p['note'] = ((p.get('note') or '') + ' ' + note).strip()
    rm[rid] = pid
    md['merges'].append({'keep': pid, 'away': rid, 'applied': '2026-11-11', 'why': 'אותו אדם: שם, אב ושנת לידה תואמים'})
    LOG.append({'merged': rid, 'into': pid})
n = 0
for rid, v in scan['certain'].items():
    if rid in M or rid in MERGE: continue
    fid = v['father']
    m = json.loads(json.dumps(arch[rid], ensure_ascii=False))
    m['parent'] = fid if fid.startswith('M') else '#' + fid
    m['name'] = norm(m['name']); m.pop('synth', None)
    for fld in ('mother', 'father', 'notes', 'job', 'bplace', 'family'):
        if m.get(fld): m[fld] = norm(m[fld])
    integ['modern'].append(m); M[rid] = m; LOG.append({'added': rid, 'name': m['name'], 'parent': m['parent'], 'why': v['why'][:90]}); n += 1
# every parent must exist
for m in integ['modern']:
    par = (m.get('parent') or '').lstrip('#')
    if par and par not in P and par not in M: print('DANGLING parent', m['id'], par)
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('registry_merged_20261109.json', 'w', encoding='utf-8').write(json.dumps(rm, ensure_ascii=False, indent=1))
io.open('merge_decisions.json', 'w', encoding='utf-8').write(json.dumps(md, ensure_ascii=False, indent=1))
io.open('registry_certain_applied_20261111.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(n, 'added;', sum(1 for x in LOG if 'merged' in x), 'merged')
