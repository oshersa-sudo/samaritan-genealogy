# -*- coding: utf-8 -*-
# Final cleanup after the add_*.py scripts: drop any children_ids / orphan stories
# that point to persons which no longer exist (e.g. removed duplicate nodes).
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))

ids = set()
for h in master['houses']:
    for f in h['families']:
        for p in f['persons']:
            ids.add(str(p['id']))

removed = 0
for h in master['houses']:
    for f in h['families']:
        for p in f['persons']:
            ch = p.get('children_ids')
            if ch:
                kept = [c for c in ch if str(c) in ids]
                removed += len(ch) - len(kept)
                p['children_ids'] = kept

orphan = [k for k in stories if k not in ids and not k.startswith(('כ-', 'שכם', 'קהיר'))]
for k in orphan:
    del stories[k]

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
print('pruned %d dangling children refs, %d orphan stories' % (removed, len(orphan)))
