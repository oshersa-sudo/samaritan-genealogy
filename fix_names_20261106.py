# -*- coding: utf-8 -*-
# 2026-11-06 — owner's corrections of misread names in the scan layer:
#  * #133 תמים: the nickname is «כאמל» (was misread «פֿאמל»)
#  * his wife (#217) is «זינאב (פועה)» — the page prints «זינאב (פועה, 1882–1968) בת אברהם»; the site had «זִינַאבּ (=פגעה)»
#  * the family name «לוטפי» was misread «לֻגֻּפְֿי» / «לנטפי» — fixed everywhere
# Every change is logged in names_fixed_20261106.json (before/after). Idempotent.
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))
LOG = []
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}

# ---- family name Lutfi, everywhere (all string values of the three data files)
LUTFI = {'לֻגֻּפְֿי': 'לוטפי', 'לנטפי': 'לוטפי'}


def walk(o, path):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str):
                nv = v
                for a, b in LUTFI.items():
                    nv = nv.replace(a, b)
                if nv != v:
                    o[k] = nv; LOG.append({'where': path + '/' + str(k), 'from': v, 'to': nv})
            else:
                walk(v, path + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, str):
                nv = v
                for a, b in LUTFI.items():
                    nv = nv.replace(a, b)
                if nv != v:
                    o[i] = nv; LOG.append({'where': path + f'[{i}]', 'from': v, 'to': nv})
            else:
                walk(v, path + f'[{i}]')


walk(master, 'master_v2')
walk(stories, 'stories')
walk(integ, 'integrate')


def setv(d, k, new, where):
    if d.get(k) != new:
        LOG.append({'where': where, 'from': d.get(k), 'to': new}); d[k] = new


# ---- #133 Tamim «כאמל»
s = stories['133']
if 'פֿאמל' in s['t']:
    LOG.append({'where': 'stories/133/t', 'from': s['t'], 'to': s['t'].replace('פֿאמל', 'כאמל')})
    s['t'] = s['t'].replace('פֿאמל', 'כאמל')
# ---- Tamim's wife Zinab (Pu'a) = #217
for sp in P['133'].get('spouses', []):
    if sp.get('name') == 'פגעה=זִינַאבּ בת אברהם':
        setv(sp, 'name', 'זינאב (פועה) בת אברהם', 'master_v2/133/spouses')
if P['217']['name'] == 'זִינַאבּ (=פגעה)':
    setv(P['217'], 'name', 'זינאב (=פועה)', 'master_v2/217/name')
t217 = stories['217']['t']
if "'פגעה'" in t217:
    LOG.append({'where': 'stories/217/t', 'from': t217, 'to': t217.replace("'פגעה'", "'פועה'")})
    stories['217']['t'] = t217.replace("'פגעה'", "'פועה'")

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('names_fixed_20261106.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
for e in LOG:
    print(e['where'], '|', str(e['from'])[:70], '→', str(e['to'])[:70])
print(len(LOG), 'changes')
