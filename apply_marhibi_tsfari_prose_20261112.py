# -*- coding: utf-8 -*-
# 2026-11-12 — owner: complete the other trees (Marhibim ג., Tsfarim ד.) from the "הרחבות" (the prose of the A.B. newspaper, pp.92-98) — only certain details.
# Method (as for the Danfim prose, apply_danfim_prose_20261109.py): every figure was READ FROM THE SCAN itself (CamScanner 16.06.2026 16.06.pdf, the scanned newspaper),
# not trusted from the text transcriptions (page_9x_*.txt), which had misreadings — e.g. Mitzliach's nickname «תופיק» (not «חופק»), Sa'd b. Shalah's years 1889–1960
# (not 1852–1917), and a made-up life-span for Arieh.
#   A. death / birth years stated in the prose — only where the field is EMPTY       B. printed-vs-census conflicts → a note, never an overwrite
#   C. Arabic nicknames in the name (only when the stored name equals the expected one)    D. marriages named in the prose (unlinked, by name)
#   E. persons named in the prose with explicit parents and missing from the tree (born after 1909)
# Idempotent. Log: marhibi_tsfari_prose_applied_20261112.json
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
FAMOF = {p['id']: f for h in master['houses'] for f in h['families'] for p in f['persons']}
NIQ = ''.join(chr(c) for c in range(0x0591, 0x05C8))
LOG = []
def nk(x): return ''.join(ch for ch in str(x or '') if ch not in NIQ)
def ah(g): return round((g - 621.57) * 1.030684)
def addnote(pid, t):
    if t not in (P[pid].get('note') or ''):
        P[pid]['note'] = ((P[pid].get('note') or '') + ' ' + t).strip(); LOG.append({'note': pid, 'text': t})
def setdeath(pid, g):
    if not P[pid].get('death'): P[pid]['death'] = ah(g); LOG.append({'death': pid, 'year': g})
def setbirth(pid, g):
    if not P[pid].get('birth'): P[pid]['birth'] = ah(g); LOG.append({'birth': pid, 'year': g})
def alias(pid, expect, new):
    cur = nk(P[pid]['name'])
    if cur == expect: P[pid]['name'] = new; LOG.append({'alias': pid, 'from': cur, 'to': new})
    elif nk(new) != cur: LOG.append({'alias_skipped': pid, 'name': cur, 'wanted': new})
def addsp(pid, name, note):
    L = P[pid].setdefault('spouses', [])
    if any(nk(s['name']) == nk(name) for s in L): return
    L.append({'name': name, 'note': note}); LOG.append({'spouse_added': pid, 'name': name})
def add(pid, name, sex, father, note, mother=None, mother_id=None, mother_src=None):
    if pid in P: return
    n = {'id': pid, 'name': name, 'sex': sex, 'father_id': father, 'note': note}
    if mother: n['mother'] = mother
    if mother_id: n['mother_id'] = mother_id
    if mother_src: n['mother_src'] = mother_src
    FAMOF[father]['persons'].append(n); P[pid] = n; FAMOF[pid] = FAMOF[father]
    ch = P[father].setdefault('children_ids', [])
    if pid not in ch: ch.append(pid)
    LOG.append({'new': pid, 'name': name, 'father': father})

# ---- A. years (Gregorian as printed; stored as Hijri like the rest of the tree), only into empty fields
DEATHS = {'168': 1974, '171': 1914, '174': 1933, '176': 1938, '176א': 1929, '184': 1905, '186': 1968, '187': 1970, '188': 1981, '189': 1971,
          'מר-אברהם184': 1967, 'מר-רצון175': 1891, '183': 1950, '185': 1960, '194': 1941, '195': 1959, '196': 1918, '198': 1911, '200': 1914, '201': 1966,
          '204': 1967, '205': 1935, '206': 1917, '208': 1919, '212': 1976, '214': 1928, '215': 1937, '216': 1972, '218': 1917, '219': 1940, '220': 1927,
          '221': 1982, '223': 1978, '224': 1917, '226': 1977, '227': 1986, '229': 1912}
BIRTHS = {'187': 1900, '188': 1901, '189': 1902, 'מר-אברהם184': 1886, '183': 1870, '197': 1863}
for pid, g in BIRTHS.items(): setbirth(pid, g)
for pid, g in DEATHS.items(): setdeath(pid, g)

# ---- B. conflicts between the prose and the census list → note (the census value stays)
PRE = 'לפי הפרוזה של המאמר: '
addnote('178', PRE + 'ניגמה (כוכבה) נולדה ביפו ב-1848 ונפטרה ב-1920 (בעמוד אחד) או ב-1921 (בעמוד אחר) — המאמר עצמו חלוק.')
addnote('190א', PRE + 'נקראת «פאתפה» (1839–1901); בכורת יצחק בן יהושע; נישאה לשלח בן יצחק בן שלח הדנפי ואחריו לסעד בן אבּ-ספֿוה הדנפי.')
addnote('196', PRE + 'חובב (חכוב) 1870–1918; לא ידע קרוא וכתוב, עבד בסבלות ובשאיבת מים. (במפקד נולד 1885.)')
addnote('197', PRE + 'אנוש 1863–1901; העתיק ספרים, עוזרו של הכה״ג יעקב בן אהרן בהוראת הקריאה בתורה לילדים; ידע בראשית ושמות בעל-פה; לא נשא אשה.')
addnote('207', PRE + 'ברוך 1863–1904; היה פקיד; לא נשא אשה ולא כתב ספרים. (במפקד נפטר 1907.)')
addnote('213', PRE + 'אניסה 1843–1889; נישאה ליוסף בן עבד-חנונה הדנפי. (במפקד נולדה 1844, נפטרה 1893.)')
addnote('214', PRE + 'אברהם 1852–1928, נולד ביפו; משירה ומשורר; נשא את קמרה (ירחה) בת סעד הדנפי (1859–1941). (במפקד נולד 1856.)')
addnote('199', PRE + 'בסוף ימיה איבדה את כושר השמיעה ולכן כונתה «אלטרמה» (החרשת); גורשה מאברהם בן סעד ונישאה לסעד בן שלמה הצפרי. שנות חייה — הערכה בלבד: 1850–1930 (בסימן שאלה).')
addnote('170', PRE + 'סעוד 1858–1920 (שנת הפטירה בסימן שאלה); נישאה לסעד בן יעקב המרחיבי (נפטר 1868) ולבנימים בן שלמה הצפרי (1841–1902).')
addnote('169', PRE + 'יהושע (אורש) — נולד 1900; אבד במלחמת העולם הראשונה: הגרמנים לקחוהו עימם ב-1917.')
addnote('171', PRE + 'יצחק 1875–1914, פקיד אצל סוחרי שכם; מת באותו יום עם שלח בן חביב צדקה.')
addnote('208', PRE + 'סעד 1868–1919; נקרא כך משום שנולד לאחר מות אביו; מת בנסיבות מוזרות (מכר ערק בניגוד לחוק, ובבוא השוטרים שפך את החומר). נשא את מלכה בת צפר המרחיבי, שילדה לו אחרי 1909 את אברהם, ברוך וסעדי.')
addnote('206', PRE + 'יעקב 1858–1917, עסק בנגרות, גבה-קומה; נשא את זפיה בת צפר יהושע, שילדה לו אחרי 1909 את רבקה, כאוסר ווג׳יהה.')
addnote('218', PRE + 'צדקה 1883–1917, סוחר בדים; מת ברמלה ממחלת הטיפוס אחרי שניסה להימנע מהגיוס הכפוי לצבא הטורקי ואושפז בבית חולים שבו נדבק.')
addnote('221', PRE + 'השומרוני הראשון שהקים משפחה מעורבת (מ-1923): נישא לבת העדה היהודית מרים חייקין מרוסיה; מ-1928 עד מותו ראש הקהילה השומרונית מחוץ לשכם.')
addnote('222', PRE + 'גואל (בדיע) 1900–1985 — אחרי 1909 נשא שתי נשים יהודיות שנטשו את המסגרת.')
addnote('211', PRE + 'כונה «אל-עפאוי» משום שנולד בשעה שאביו היה בעכו לצורך מסחר; איש דתי מאד, תיקן את ספרי התורה העתיקים בבית הכנסת בשכם, העתיק ספרים, ופעמיים את «ממר מרקה».')

# ---- C. nicknames (the stored name must equal the expected one)
alias('168', 'מרחיב', "מרחיב (בן שת, מפארג')")
alias('189', 'מצליח', "מצליח (בן צפר, תופיק)")
alias('211', 'יעקב', 'יעקב (בן מרחיב, אלעפאוי)')
alias('169', 'יהונשע (בן שת, יהושע)', 'יהונשע (בן שת, יהושע, אורש)')

# ---- D. marriages named in the prose (unlinked)
addsp('221', 'מרים חייקין (יהודיה מרוסיה)', 'נישאה לו מ-1923 — לפי הפרוזה של המאמר')
addsp('223', "אסתר (ג'מילה) (יהודיה)", 'נישא לה ב-1931 — לפי הפרוזה של המאמר')
addsp('226', 'רחל (מן העדה היהודית)', 'נישא לה ב-1937 — לפי הפרוזה של המאמר')
addsp('227', 'אברהם בן פינחס הכהן', 'נישאה לו אחרי 1909 — לפי הפרוזה של המאמר')

# ---- E. children named in the prose (explicit parents), missing from the tree
add('מר-סעדי208', 'סעדי', 'M', '208', PRE + 'נולד אחרי 1909 לסעד ולמלכה בת צפר המרחיבי (אחיו: אברהם וברוך).', mother='מלכה בת צפר', mother_id='186', mother_src='המאמר (הפרוזה), לפי רשומת האב')
add('צפ-נגיה224', "נג'יה", 'F', '224', PRE + 'נולדה אחרי 1909 ליפת (חסן) ולהדיה בת יצחק הכהן.', mother='הדִיֶה בת יצחק', mother_src='המאמר (הפרוזה), לפי רשומת האב')
add('צפ-פתחי224', 'פתחי', 'M', '224', PRE + 'נולד אחרי 1909 ליפת (חסן) ולהדיה בת יצחק הכהן.', mother='הדִיֶה בת יצחק', mother_src='המאמר (הפרוזה), לפי רשומת האב')

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('marhibi_tsfari_prose_applied_20261112.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(sum(1 for x in LOG if 'death' in x), 'deaths;', sum(1 for x in LOG if 'birth' in x), 'births;', sum(1 for x in LOG if 'note' in x), 'notes;',
      sum(1 for x in LOG if 'alias' in x), 'aliases;', sum(1 for x in LOG if 'spouse_added' in x), 'spouses;', sum(1 for x in LOG if 'new' in x), 'new')
print([x for x in LOG if 'alias_skipped' in x])
