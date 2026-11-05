# -*- coding: utf-8 -*-
# Marks modern records whose day/month of birth is AMBIGUOUS in the Excel (both numbers <= 12, e.g. 4.3 could be
# 4 March or 3 April): 'bamb': true. The app then shows neither a zodiac sign nor an exact-date age for them.
# Run after every addition of Excel persons. Idempotent.
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
NIQ = ''.join(chr(c) for c in range(0x0591, 0x05C8))
def norm(s):
    s = ''.join(ch for ch in str(s or '') if ch not in NIQ)
    s = re.sub(r"[׳״\"'`.,/\()\-]", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()
people = json.load(io.open('modern_people.json', encoding='utf-8'))
st = {(norm(p['name']), str(p['byear'] or ''), norm(p['father'])): p.get('bdate_status') for p in people}
integ = json.load(io.open('integrate.json', encoding='utf-8'))
n = 0
for m in integ['modern']:
    if not (m.get('bmonth') and m.get('bday')):
        continue
    s = st.get((norm(m['name']), str(m.get('byear') or ''), norm(m.get('father'))))
    if s == 'ambiguous_md':
        m['bamb'] = True; n += 1
    else:
        m.pop('bamb', None)
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
print('ambiguous dates flagged:', n, 'of', sum(1 for m in integ['modern'] if m.get('bmonth') and m.get('bday')), 'with a day/month')
