# -*- coding: utf-8 -*-
# 2026-11-05 — layer rework. Removes the layer that came from the census Excel (מיפקד.xlsx):
# every 'modern' person (M…, F… placeholder fathers, mx-…) and the 'overlap' year enrichments.
# KEPT: persons that the owner edited/attached directly on the live site (cloud overrides) and
# the chain they hang from:  ev-12 (edited by the owner), M426 (גולן) and M210 (יפת) — the parents of
# the owner's own added record e-mw2nfaa4.
# The complete previous layer is archived in excel_layer_archive.json (restorable). Idempotent.
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
KEEP = {'M210', 'M426'}
integ = json.load(io.open('integrate.json', encoding='utf-8'))
try:
    arch = json.load(io.open('excel_layer_archive.json', encoding='utf-8'))
except Exception:
    arch = None
if arch is None:
    arch = {'modern': integ['modern'], 'overlap': integ.get('overlap', []), 'archived_on': '2026-11-05',
            'note': 'full integrate.json before removal of the Excel layer'}
    io.open('excel_layer_archive.json', 'w', encoding='utf-8').write(json.dumps(arch, ensure_ascii=False, indent=1))
src = {m['id']: m for m in arch['modern']}
ev = {m['id']: m for m in json.load(io.open('events_removed_archive.json', encoding='utf-8'))['modern']}
keep = [src[i] for i in sorted(KEEP)] + [ev['ev-12']]
integ['modern'] = keep
integ['overlap'] = []
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
print('archived', len(arch['modern']), 'persons +', len(arch['overlap']), 'overlap rows; kept', [m['id'] for m in keep])
