# -*- coding: utf-8 -*-
# Gives EVERY person a unique numeric ID ("ת.ז."), field `uid`:
#   * persons whose existing id is a plain number (the printed census list number) keep that number;
#   * everybody else gets the next running number from 1001 (1..999 are kept for the printed census numbers);
#   * the assignment is remembered in uid_registry.json, so a number never changes or gets reused, however often the data is rebuilt;
#   * persons added by the owner on the live site (cloud overrides) are reserved first, so a rebuild can never collide with them.
# The old identifier stays as `id` (links, cloud edits) and is shown at the bottom of the card as «ID קודם». Idempotent.
import json, io, re, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
REG = 'uid_registry.json'
try:
    reg = json.load(io.open(REG, encoding='utf-8'))
except Exception:
    reg = {'next': 1001, 'map': {}}
M = reg['map']
master = json.load(io.open('master_v2.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))

# owner's records on the live site (cloud overrides): reserve their numbers first
live = {}
try:
    live = json.load(urllib.request.urlopen(urllib.request.Request('https://samaritan-genealogy.oshersa.workers.dev/api/data', headers={'User-Agent': 'Mozilla/5.0'}), timeout=15))
except Exception as e:
    print('live overrides not reachable (', e, ') — using what is already registered')
admin_ids = list((live.get('added') or {}).keys())
for i, rec in (live.get('added') or {}).items():
    if rec.get('uid') and i not in M:
        M[i] = int(rec['uid'])


def take(old):
    if old in M:
        return M[old]
    if re.fullmatch(r'\d+', old) and int(old) < 1000 and int(old) not in M.values():
        M[old] = int(old)
    else:
        while reg['next'] in M.values():
            reg['next'] += 1
        M[old] = reg['next']; reg['next'] += 1
    return M[old]


# plain-number ids first (so a printed census number is never taken by a running number)
persons = [p for h in master['houses'] for f in h['families'] for p in f['persons']]
for p in persons:
    if re.fullmatch(r'\d+', p['id']):
        take(p['id'])
for p in persons:
    p['uid'] = take(p['id'])
for m in integ['modern']:
    m['uid'] = take(m['id'])
integ['admin_uids'] = {i: take(i) for i in admin_ids}
# owner's known admin records even when offline
for i in ('e-mw2nfaa4',):
    integ['admin_uids'].setdefault(i, take(i))

uids = [p['uid'] for p in persons] + [m['uid'] for m in integ['modern']] + list(integ['admin_uids'].values())
assert len(uids) == len(set(uids)), 'duplicate uid!'
assert all(isinstance(u, int) for u in uids)
reg['map'] = M
io.open(REG, 'w', encoding='utf-8').write(json.dumps(reg, ensure_ascii=False, indent=1))
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
kept = sum(1 for p in persons if re.fullmatch(r'\d+', p['id']))
print(len(persons), 'scan-layer persons +', len(integ['modern']), 'Excel/events persons +', len(integ['admin_uids']), 'admin → ', len(uids), 'unique uids;',
      kept, 'kept their printed number; next free =', reg['next'])
