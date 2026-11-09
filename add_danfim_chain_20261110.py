# -*- coding: utf-8 -*-
# 2026-11-10 — owner: why were the post-1909 descendants of Yosef b. Avraham (Parha, #137) never added?
# Cause: the registry (Excel) father «אברהם» + mother «רסמייה» was rated «בינונית» because my matcher compared the mother's name
# letter-for-letter (רסמייה ≠ רסמיה — #153, the wife of #137), so the unique match was missed; everything below Yosef (M40) hung on him.
# The events register also confirms the pair (son Yosef b.1913, «برهوم يوسف عبد اللطيف» + «رسمية مرجان أسعد»).
# Added now: M40 + his children and grandchildren, with the owner's names/nicknames. Also: Shoham (M190) d. 3.3.2022.
# Idempotent. Log: danfim_chain_added_20261110.json
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
integ = json.load(io.open('integrate.json', encoding='utf-8'))
arch = {m['id']: m for m in json.load(io.open('excel_layer_archive.json', encoding='utf-8'))['modern']}
M = {m['id']: m for m in integ['modern']}
LOG = []
# registry id -> (parent, name, extra note)
PLAN = {
 'M40':  ('#137', 'יוסף', None),
 'M222': ('M40', 'אברהם (ברהום)', None),
 'M239': ('M40', 'חבר (סמיר)', None),
 'M281': ('M40', 'נועמן', 'ברשם הקהילה נרשם «נועם»; השם לפי הבעלים — נועמן.'),
 'M327': ('M40', 'נואל', None),
 'M486': ('M222', 'שירין', None),
 'M506': ('M222', 'יוסף (יוסי)', None),
 'M529': ('M222', 'רינת', None),
 'M543': ('M239', 'זהיה (זהו)', None),
 'M561': ('M239', 'דיאנה', None),
 'M579': ('M239', 'הנה', 'נספתה באסון טביעה במי גשמים: מונית ערבית שנפלה אל התהום בחזרתה מלימודיה; נספתה יחד עם חברתה ללימודים, וגופתה נמצאה כעבור כמה ימים. לא נישאה ונפטרה ללא משפחה. ירחמה יהוה. (הזיהוי כבתו הגדולה של חבר/סמיר — בהיעדר שם בדברי הבעלים — לפי רשם הקהילה: ארבע בנות, והיא הגדולה מבין שריהאן.)'),
 'M652': ('M239', 'שריהאן', None),
 'M667': ('M281', 'יזן', None),
 'M691': ('M281', 'יוסף', None),
 'M697': ('M281', 'נאראם', 'ברשם הקהילה נרשמה בטעות בשם «יוסף»; השם לפי הבעלים — נאראם.'),
}
for rid, (par, nm, note) in PLAN.items():
    if rid in M: continue
    m = json.loads(json.dumps(arch[rid], ensure_ascii=False))
    m['parent'] = par; m['name'] = nm; m.pop('synth', None)
    if note: m['notes'] = ((m.get('notes') or '') + ' ' + note).strip()
    integ['modern'].append(m); M[rid] = m; LOG.append({'added': rid, 'name': nm, 'parent': par})
# marriage Avraham (Barhum) ↔ Iris (already on the site as M226)
if 'M226' in M and not any(s.get('ref') == 'M222' for s in M['M226'].get('spouses') or []):
    M['M226'].setdefault('spouses', []).append({'name': 'אברהם (ברהום) בן יוסף', 'ref': 'M222'})
    M['M222']['spouses'] = [{'name': 'איריס (רסמיה) בת אסעד', 'ref': 'M226'}]; LOG.append('spouse M222-M226')
# Shoham's death date
sh = M['M190']
if sh.get('dyear') != 2022:
    sh['dyear'] = 2022; sh['dmonth'] = 3; sh['dday'] = 3
    sh['notes'] = ((sh.get('notes') or '') + ' נפטר ב-3.3.2022.').strip(); LOG.append('M190 died 3.3.2022')
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('danfim_chain_added_20261110.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(len(LOG), LOG)
