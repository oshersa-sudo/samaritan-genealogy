# -*- coding: utf-8 -*-
# Neutralises everything in integrate.json that was derived from the Arabic community events
# registry (סגל המאורעות / سجل المناسبات): ev- births, evd- daughters (from mother names) and the
# event-derived marriage lines (spouses flagged _ev). Nothing is lost: the removed records are
# written to events_removed_archive.json so they can be restored. Idempotent.
# NOTE: do NOT re-run integrate_events_v2 / integrate_daughters / integrate_marriages afterwards.
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
P = 'integrate.json'
d = json.load(io.open(P, encoding='utf-8'))
mods = d.get('modern', [])
removed, spouse_links = [], []
keep = []
for m in mods:
    if m['id'].startswith('ev-') or m['id'].startswith('evd-'):
        removed.append(m); continue
    sp = m.get('spouses')
    if sp:
        good = [s for s in sp if not s.get('_ev')]
        bad = [s for s in sp if s.get('_ev')]
        for s in bad: spouse_links.append({'person': m['id'], 'spouse': s})
        if good: m['spouses'] = good
        else: m.pop('spouses', None)
    keep.append(m)
ids = {m['id'] for m in keep}
orph = [m['id'] for m in keep if (m.get('parent') or '') and (m['parent'].startswith('ev') )]
assert not orph, orph
d['modern'] = keep
try:
    arch = json.load(io.open('events_removed_archive.json', encoding='utf-8'))
except Exception:
    arch = {'modern': [], 'spouse_links': []}
have = {m['id'] for m in arch['modern']}
arch['modern'] += [m for m in removed if m['id'] not in have]
arch['spouse_links'] += spouse_links
io.open('events_removed_archive.json', 'w', encoding='utf-8').write(json.dumps(arch, ensure_ascii=False, indent=1))
io.open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print('removed persons', len(removed), '| removed spouse links', len(spouse_links), '| modern left', len(keep))
