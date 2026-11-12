# -*- coding: utf-8 -*-
# 2026-11-12 — owner: complete the other trees (Marhibim ג., Tsfarim ד., Priests ו.) from the census Excel — only what is CERTAIN.
# Selection: scan4_registry_others_20261112.py → registry_certain_scan4_20261112.json (same gate as the Danfim rounds, plus: strict family→house, dated census fathers only,
# and anyone whose archived Excel-layer parent disagrees with the derived father is held back).  Two registry persons are the SAME people already on the site → merged (alt_ids).
# Idempotent. Log: registry_others_applied_20261112.json
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))
arch = {m['id']: m for m in json.load(io.open('excel_layer_archive.json', encoding='utf-8'))['modern']}
scan = json.load(io.open('registry_certain_scan4_20261112.json', encoding='utf-8'))
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
    'M12': ('222', 1899, 1985, None, 'ברשם הקהילה: «בדיע בן אברהם וקמרה, 1899–1985, סופר ומחבר, נולד בשכם; נישא ליהודיה והתגרש» — אותו אדם (אב אברהם #214, אם קמרה, נולד 1899; פֻדִיע = בדיע).'),
    'M33': ('מר-אברהם208', 1909, 1994, "וג'הה בת יעקב המרחיבי", 'ברשם הקהילה: «אברהם בן סעד ומלכה, 1909–1994, נולד בשכם; נשוי לוג׳הה בת יעקב המרחיבי» — אותו אדם (הנולד 1909 «מלכה הרתה לו בעת המפקד»; אב סעד #208 ואם מלכה).'),
}
for rid, (pid, by, dy, wife, note) in MERGE.items():
    p = P[pid]
    if rid in (p.get('alt_ids') or []): continue
    p['alt_ids'] = sorted(set((p.get('alt_ids') or []) + [rid]))
    if by and not p.get('birth'): p['birth'] = ah(by)
    if dy and not p.get('death'): p['death'] = ah(dy)
    if note not in (p.get('note') or ''): p['note'] = ((p.get('note') or '') + ' ' + note).strip()
    if wife and not p.get('spouses'): p['spouses'] = [{'name': wife, 'note': 'לפי רשם הקהילה'}]
    rm[rid] = pid
    md['merges'].append({'keep': pid, 'away': rid, 'applied': '2026-11-12', 'why': 'אותו אדם: אב, אם ושנת לידה תואמים'})
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
    integ['modern'].append(m); M[rid] = m; LOG.append({'added': rid, 'name': m['name'], 'family': m.get('family'), 'parent': m['parent'], 'why': v['why'][:90]}); n += 1
for m in integ['modern']:
    par = (m.get('parent') or '').lstrip('#')
    if par and par not in P and par not in M and not par.startswith('@'): print('DANGLING parent', m['id'], par)
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('registry_merged_20261109.json', 'w', encoding='utf-8').write(json.dumps(rm, ensure_ascii=False, indent=1))
io.open('merge_decisions.json', 'w', encoding='utf-8').write(json.dumps(md, ensure_ascii=False, indent=1))
io.open('registry_others_applied_20261112.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(n, 'added;', sum(1 for x in LOG if 'merged' in x), 'merged')
