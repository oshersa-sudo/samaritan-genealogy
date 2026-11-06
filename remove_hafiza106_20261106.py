# -*- coding: utf-8 -*-
# 2026-11-06 — owner: take חפיזה (#106, a lone root of the Abd-Alla family in the Danfim tree) out for now; archived, uid stays reserved.
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
reg = json.load(io.open('uid_registry.json', encoding='utf-8'))['map']
ARCH = json.load(io.open('removed_persons_20261106.json', encoding='utf-8'))
for h in master['houses']:
    for f in h['families']:
        for p in list(f['persons']):
            if p['id'] == '106':
                assert not p.get('children_ids') and not p.get('father_id')
                f['persons'].remove(p)
                ARCH.append({'person': p, 'story': stories.pop('106', None), 'uid': reg.get('106'), 'reason': 'owner asked to take her out of the tree (2026-11-06)'})
                print('removed', p['id'], p['name'])
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('removed_persons_20261106.json', 'w', encoding='utf-8').write(json.dumps(ARCH, ensure_ascii=False, indent=1))
