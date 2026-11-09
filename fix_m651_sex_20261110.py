# -*- coding: utf-8 -*-
# 2026-11-10 — owner: M651 «אברהם» (בן גמליאל, נולד 1996) is a son; the registry has him as F (a registry typo).
import json, io
integ = json.load(io.open('integrate.json', encoding='utf-8'))
for m in integ['modern']:
    if m['id'] == 'M651' and m.get('sex') != 'M':
        m['sex'] = 'M'; m['notes'] = ((m.get('notes') or '') + ' המין תוקן לזכר לפי הבעלים (ברשם הקהילה נרשם בטעות כנקבה).').strip()
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
