# -*- coding: utf-8 -*-
# 2026-11-09 — owner: the deaf-mute brother is named מראד (printed on p.81); add his story and his deaf wife. He is already on the tree as «דנ-מראד79» (father #79).
# Idempotent. Log: danfim_prose3_applied_20261109.json
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
LOG = []
m = P['דנ-מראד79']
if not m.get('spouses'):
    m['spouses'] = [{'name': 'אשה חרשת (שמה לא נודע)', 'note': 'חרשת; גורשה לפני מותו בגלל מצבו הכלכלי הירוד (עמ׳ 81)'}]; LOG.append('spouse')
t = 'אח אילם של זוהרה ושמסה. נשא אשה חרשת. מת מחנק, כי לא יכול היה לאכול אלא לחם טרי. לפני מותו נאלץ לגרש את אשתו בגלל מצבו הכלכלי הירוד.'
if not (stories.get('דנ-מראד79') or {}).get('t'):
    stories['דנ-מראד79'] = {'t': t, 'g': ''}; LOG.append('story')
note = 'אילם; נשא אשה חרשת (שמה לא נודע); מת מחנק; לפני מותו גירש אותה — עמ׳ 81.'
if m.get('note') != note: m['note'] = note; LOG.append('note')
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('danfim_prose3_applied_20261109.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(LOG)
