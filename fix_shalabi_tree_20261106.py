# -*- coding: utf-8 -*-
# 2026-11-06 — «משפחת צדקה=שלבי בן יעקב בן אב-סכוה הדנפי» (printed page 79, upper tree) reconciled with the site (#71 / #79 subtrees,
# hung under the apex «צדקה = שלבי»): the missing generation «צדקה» between #71 and #72, the missing daughter «שלבייה», the missing «מראד»,
# the unnamed grandson of חילמי (#78-son = «יוסף»), spouses named in the tree, and the family name «שלבי» (was misread «שלפֿי»).
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
FAM = next(f for h in master['houses'] for f in h['families'] if f['family'] == 'משפחת שלבי הדנפי')
LOG = []


def add_node(pid, name, sex, father, note=''):
    if pid in P: return
    n = {'id': pid, 'name': name, 'sex': sex, 'father_id': father}
    if note: n['note'] = note
    FAM['persons'].append(n); P[pid] = n
    ch = P[father].setdefault('children_ids', [])
    if pid not in ch: ch.append(pid)
    LOG.append({'new': pid, 'name': name, 'father': father})


def rename(pid, old, new):
    if P[pid].get('name') == old:
        P[pid]['name'] = new; LOG.append({'id': pid, 'name_from': old, 'to': new})


def spouse_rename(pid, idx, old, new):
    sp = P[pid]['spouses'][idx]
    if sp['name'] == old:
        sp['name'] = new; LOG.append({'id': pid, 'spouse_from': old, 'to': new})


# 1. the family name
rename('71', 'יוסף שלפֿי (השלכי)', 'יוסף שלבי (השלבי)')
# 2. missing generation: יוסף (#71) → צדקה → יעקב (#72)
if 'דנ-צדקה-ב' not in P:
    add_node('דנ-צדקה-ב', 'צדקה', 'M', '71', 'אחים ואחיות שלו שמתו קטנים.')
    P['71']['children_ids'] = [c for c in P['71'].get('children_ids', []) if c != '72']
    P['72']['father_id'] = 'דנ-צדקה-ב'
    P['דנ-צדקה-ב'].setdefault('children_ids', []).append('72')
    LOG.append({'moved': '72', 'new_father': 'דנ-צדקה-ב'})
# 3. missing children
add_node('דנ-שלביה72', 'שלבייה', 'F', '72')
add_node('דנ-מראד79', 'מראד', 'M', '79', 'נשא אשה שלא נודעה בשמה.')
# 4. the unnamed grandson of חילמי
if not P['78-son'].get('name'):
    P['78-son']['name'] = 'יוסף'; P['78-son']['sex'] = 'M'; LOG.append({'id': '78-son', 'named': 'יוסף'})
# 5. spouses named in the tree
def add_spouse(pid, sp):
    lst = P[pid].setdefault('spouses', [])
    if not any(s.get('name') == sp['name'] for s in lst):
        lst.append(sp); LOG.append({'id': pid, 'spouse_added': sp['name']})
add_spouse('79', {'name': 'מרים בת הכה״ג שלמה'})
add_spouse('73', {'name': 'סלוח בת שלח הדנפי', 'note': '= אדם #86'})
add_spouse('73', {'name': 'פרוגיה בת ישראל הסתרי'})
spouse_rename('81', 0, 'חביב/חובב הצפרי', 'חביב בן יעקב צדקה')
spouse_rename('80', 0, 'פגעה (זִינַאבּ) בת שלמה הדנפי', 'זינאב (הצולעת) בת שלמה הדנפי')
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('shalabi_tree_fixed_20261106.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
for e in LOG: print(e)
