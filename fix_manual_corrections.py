# -*- coding: utf-8 -*-
# User-confirmed manual corrections that name-matching can't infer. Runs AFTER resolve2
# (edits integrate.json). Idempotent (ids prefixed 'mx-'). Additive/re-parent only.
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
integ = json.load(io.open('integrate.json', encoding='utf-8'))
mods = integ['modern']; mid = {x['id']: x for x in mods}

# drop prior manual nodes (idempotent)
integ['modern'] = [x for x in mods if not str(x.get('id','')).startswith('mx-')]
mods = integ['modern']; mid = {x['id']: x for x in mods}

def setp(pid, **kw):
    if pid in mid: mid[pid].update(kw)

# --- דרור מרחיב is son of אברהם בן יששכר (bn #195), NOT M33 (אברהם בן סעד). ---
# The registry gave both groups father="אברהם"; the mother field separates them:
#   וג'הה  -> M33's children (mnsh/ytzhq/nisim/brwkh/rtzwn)  [correct, left as-is]
#   דליה   -> אברהם בן יששכר's children (דרור, מרים)          [fixed here]
# אברהם בן יששכר himself is missing from the registry — add him as a son of census #195.
integ['modern'].append({'id':'mx-avr-yis','name':'אברהם (בן יששכר)','sex':'ז','parent':'#195',
    'g':'1932–','byear':1932,'dyear':None,'family':'מרחיב','father':'יששכר','mother':None,
    'notes':'בן יששכר (#195). נשוי לדליה. (תיקון מבוסס-מקור: אביהם של דרור, מרים ויששכר)'})
# his son יששכר (דרור\'s brother, named after grandfather #195)
integ['modern'].append({'id':'mx-yissachar','name':'יששכר','sex':'ז','parent':'mx-avr-yis',
    'g':'','byear':None,'dyear':None,'family':'מרחיב','father':'אברהם','mother':'דליה',
    'notes':'בן אברהם בן יששכר; אחיהם של דרור ומרים.'})
# re-parent דרור + מרים to their real father; add מרים's death year 2024
setp('M342', parent='mx-avr-yis')
setp('M350', parent='mx-avr-yis', dyear='2024', g='1965–2024', age='59')

io.open('integrate.json','w',encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
print('manual corrections applied:')
for i in ['mx-avr-yis','mx-yissachar','M342','M350']:
    x={y['id']:y for y in integ['modern']}.get(i,{})
    print('  %-13s %-16s parent=%s dyear=%s'%(i, x.get('name'), x.get('parent'), x.get('dyear')))
