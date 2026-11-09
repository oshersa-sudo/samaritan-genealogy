# -*- coding: utf-8 -*-
# 2026-11-09 — owner approved the CERTAIN leftovers of the prose sweep (pp.74-90, read from the scan):
#   1. #81 זוהרה's first husband = יעקב השלבי #72 («נישאה קודם ליעקב השלבי, בן דודה, כשהוא ברח ללונדון, השיאוה לחביב בן יעקב צדקה», עמ׳ 81)
#   2. five life stories that were never written: #146, הס-חבובה, דנ-נזמיה58, #161, #162
# Idempotent. Log: danfim_prose2_applied_20261109.json
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
LOG = []


def story(pid, t, g):
    if not (stories.get(pid) or {}).get('t'):
        stories[pid] = {'t': t, 'g': g}; LOG.append({'story': pid})


# 1. the first marriage (hers) — both sides, before her marriage to Habib
if not any('#81' in str(s.get('note') or '') or s.get('ref') == '81' for s in P['72']['spouses']):
    P['72']['spouses'].append({'name': 'זוהרה בת ישראל אלמועלם', 'ref': '81', 'note': '= אדם #81; בת דודתו; נישאה לו לפני נישואיה לחביב בן יעקב צדקה — כשברח ללונדון (עמ׳ 81)'}); LOG.append({'spouse': '72→81'})
if not any('#72' in str(s.get('note') or '') or s.get('ref') == '72' for s in P['81']['spouses']):
    P['81']['spouses'].insert(0, {'name': 'יעקב השלבי', 'ref': '72', 'note': '= אדם #72; בן דודה; נישאה לו קודם, כשברח ללונדון (עמ׳ 81); אחר כך הושאה לחביב בן יעקב צדקה'}); LOG.append({'spouse': '81→72'})

# 2. stories (only facts printed on the page)
story('146', 'בת שמעון וסלוחה. נישאה אחרי 1909 לכהן טביה בן פינחס.', '1902–1979')
story('הס-חבובה', 'בת סעד בן עבד אל-פתאח, שהתאסלם. אשת סלים בן סאלם (#113). נטרפה עליה דעתה ושרפה את עצמה למוות בשנת 1910.', '–1910')
story('דנ-נזמיה58', 'בת הזקונים של עבד-אלה (#58) ומרים בת הכה״ג יעקב בן אהרן; נולדה אחרי 1909. נישאה לעפיף בן זבולן הדנפי (#46). נפטרה ב-1967.', '–1967')
story('161', 'אחותו של סעד בן ישמעאל. נישאה לסעד בן עבד הברא (עבד אלחאלק, נפטר ב-1908) ממשפחת שלבי הדנפי, דודו של אברהם בן מרחיב צדקה הצפרי. ילדה לו בן שמת בקטנותו.', '1834–1889')
story('162', 'בן ישמעאל בן אברהם, מאשתו השנייה שלא נודעה בשמה. נשא את סלוחה בת יצחק לוטפי. נולדו להם ארבעה בנים: שלח (עיארב א-שמהט), יהודה (שוקרי), אברהם וטהור.', '1843–1878')

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('danfim_prose2_applied_20261109.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(len(LOG), 'changes', LOG)
