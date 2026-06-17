# -*- coding: utf-8 -*-
# Writes CHANGES.md — a human-readable log of every person ADDED from the scanned
# texts (the priestly house, the High-Priest chains, and the transcript bridge-people),
# grouped by house/family, so the user can review them.
import json, io

master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
allp = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}

PREFIXES = ('הס-', 'מר-', 'ר-', 'כ-', 'שכם', 'קהיר')
def is_added(pid): return any(str(pid).startswith(pfx) for pfx in PREFIXES)

def fname(pid):
    p = allp.get(pid)
    return p['name'] if p else ('#' + str(pid))

out = io.open('CHANGES.md', 'w', encoding='utf-8')
out.write('# שינויים שנוספו מהטקסטים הסרוקים — לעיון ואימות\n\n')
out.write('כל אדם להלן **נוסף** לעץ מתוך הטקסט (התמלולים page_74–98 / הספר "תולדות בני ישראל השומרונים"), '
          'ולא היה במיפקד 1909 המקורי. השנים לועזיות. ההורה מצוין בסוגריים.\n\n')

out.write('## תיקוני-עקביות (סבב ביקורת מול ענפי-המיפקד)\n\n')
out.write('נמצאו כפילויות שבהן אנשים שכבר היו במיפקד נוספו שוב מהתמלול. תוקנו כך — '
          'במקום צומת חדש, **הצומת הקיים במיפקד הועשר** (שם/שנים/סיפור):\n\n')
out.write('- **חיכמת** = #129 (ישמעאל בן ישמעאל, "נולד 4 ימים אחרי מות אביו"). היה משובץ בטעות כבן תמים — הוסר; #129 הועשר ל"ישמעאל (חיכמת)".\n')
out.write('- **תמים (פֿאמל)** = #133 (בן ישראל). היה כפול כ"הס-תמים" — הוסר; #133 הועשר.\n')
out.write('- **פוֹזי** = #134 (אחי תמים, בן ישראל). היה כפול — הוסר; #134 הועשר.\n')
out.write('- **ילדי עבד-אלה האלטיפי (#58)** כבר במיפקד כ-#59–65; 9 הכפילויות הוסרו. רק #59 ("שם לאימות") הועשר ל**מנגיר** (הבן הבכור, יורש משרת הטאבו).\n')
out.write('- **עיפאת** כבר במיפקד כ-#65ג — הכפילות הוסרה.\n')
out.write('- "סברי" (1900) — נמחק; ייחוסו בטקסט אינו חד-משמעי (לא נוחש אב).\n\n')
out.write('---\n\n')

total = 0
for h in master['houses']:
    rows = []
    for f in h['families']:
        for p in f['persons']:
            if is_added(p['id']):
                g = (stories.get(p['id'], {}) or {}).get('g', '')
                fid = p.get('father_id')
                par = fname(fid) if fid else '—'
                t = (stories.get(p['id'], {}) or {}).get('t', '')
                rows.append((f['family'], p['name'], g, par, t))
    if not rows:
        continue
    out.write('## %s\n\n' % h['house'])
    cur_fam = None
    for fam, name, g, par, t in rows:
        if fam != cur_fam:
            out.write('\n### %s\n\n' % fam)
            cur_fam = fam
        total += 1
        line = '- **%s**%s — אב: %s' % (name, (' (' + g + ')') if g else '', par)
        out.write(line + '\n')
        if t:
            out.write('  - %s\n' % t)
    out.write('\n')

out.write('\n---\n**סך הכל נוספו מהטקסט: %d אנשים.** (בנוסף בוצעו תיקוני-מבנה כלליים: תקרת-גיל לאב, '
          'אב-זכר, אסעד=סעד, וצמתי-אב משוחזרים לקבוצות-אחים מהמרשם.)\n' % total)
out.close()
print('CHANGES.md written —', total, 'added persons documented')
