# -*- coding: utf-8 -*-
# 2026-11-06 — three printed spouse references were mangled by the OCR (an extra digit glued on) and, because the card resolves a reference
# by its longest valid id prefix, pointed at the WRONG person (#51 יוסף, #71 יוסף שלבי, #126 גֿמילה).  Restored from the page readings:
#   #122 ישראל הסתרי: מסעודה בת שלמה (15כי'), לאה בת אב-סכוה (107דיד);  #210 מרחיב: זינאב (פועה) בת עבד-בורא (260 די'?)
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
FIX = [('122', 0, "515כ'", "15 כי'"), ('122', 1, "710לד'", "107 דיד"), ('210', 1, "1260ד'?", "260 די'?")]
for pid, i, old, new in FIX:
    sp = P[pid]['spouses'][i]
    if sp.get('ref') == old:
        sp['ref'] = new; print(pid, sp['name'], old, '->', new)
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
print('15' in P, '107' in P, '260' in P, '26' in P)
