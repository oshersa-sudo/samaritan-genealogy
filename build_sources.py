# -*- coding: utf-8 -*-
# 2026-11-06 — writes the EXACT source of every person into the data ("src"), shown on the opened card:
#   * Excel persons      → «מיפקד.xlsx, גיליון 'תאריך לידה', שורה N»
#   * census-article persons → «מאמר "מיפקד השומרונים בשנת 1909", עמוד X (עמוד Y בקובץ הסרוק)»  (printed page = PDF page + 72)
#   * priestly houses    → the book «תולדות בני ישראל השומרונים», page of the scanned book file
#   * apex nodes         → the printed family-tree page (עמוד 75)
# Page numbers come from the independent reading of all 29 pages (scan_read) — persons the reading could not place say so.
import json, io, re, sys, glob
import openpyxl
sys.stdout.reconfigure(encoding='utf-8')
XLSX = r'C:\Users\osher\Downloads\מיפקד.xlsx'
FINDINGS = r'C:\Users\osher\Documents\torah\data\genealogy_audit\findings_scan.json'

master = json.load(io.open('master_v2.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))
arch = json.load(io.open('excel_layer_archive.json', encoding='utf-8'))
SF = json.load(io.open(FINDINGS, encoding='utf-8'))['source_fields']
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
NIQ = ''.join(chr(c) for c in range(0x0591, 0x05C8))


def norm(s):
    s = ''.join(ch for ch in str(s or '') if ch not in NIQ)
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r"[׳״\"'`\.,/\\\-]", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


# ------------------------------------------------------------------ Excel rows
wb = openpyxl.load_workbook(XLSX, data_only=True)
rowmap = {}                                    # key -> (sheet, excel row)
for ws in wb.worksheets:
    hdr = None
    for r in range(1, 8):
        vals = [str(c.value).strip() if c.value is not None else '' for c in ws[r]]
        if 'השם' in vals:
            hdr = r; break
    if hdr is None: continue
    vals = [str(c.value).strip() if c.value is not None else '' for c in ws[hdr]]
    ci = {'name': vals.index('השם'), 'bdate': vals.index('תאריך לידה'), 'father': vals.index('שם האב')}
    for row in ws.iter_rows(min_row=hdr + 1):
        name = row[ci['name']].value
        if not name: continue
        by = row[ci['bdate'] + 1].value
        by = '' if by in (None, '') else str(int(by)) if isinstance(by, (int, float)) else str(by).strip()
        key = (norm(name), by, norm(row[ci['father']].value))
        rowmap.setdefault((ws.title, key), row[0].row)
SHEETS = ['תאריך לידה', 'אבא', 'אימה', 'א-ב', 'משפחה', '1955', 'זכות בחירה']


def excel_src(m):
    key = (norm(m['name']), str(m.get('byear') or ''), norm(m.get('father')))
    for sh in SHEETS:
        r = rowmap.get((sh, key))
        if r: return {'sheet': sh, 'row': r}
    return None


excel_rows = {}
for m in arch['modern']:
    if re.fullmatch(r'M\d+', m['id']):
        e = excel_src(m)
        if e: excel_rows[m['id']] = e
io.open('excel_rows.json', 'w', encoding='utf-8').write(json.dumps(excel_rows, ensure_ascii=False, indent=1))
print('excel rows found for', len(excel_rows), 'of', sum(1 for m in arch['modern'] if re.fullmatch(r'M\d+', m['id'])))

# ------------------------------------------------------------------ article pages
ART = 'מאמר «מיפקד השומרונים בשנת 1909»'


def art(pdf_pages):
    pdf_pages = sorted(set(pdf_pages))
    pr = [p + 72 for p in pdf_pages]
    if len(pdf_pages) == 1:
        return f'{ART} — עמוד {pr[0]} (עמוד {pdf_pages[0]} בקובץ הסרוק)'
    return f"{ART} — עמודים {', '.join(map(str, pr))} (עמודים {', '.join(map(str, pdf_pages))} בקובץ הסרוק)"


MANUAL_PAGES = {'182': [18], '242': [28], '251': [29], '252': [29], '253': [29], '254': [29], '255': [29], '256': [29],
                'ר-סלגח49': [2], 'ר-שלביה': [8], 'ר-אינמר': [13], '156': [17], '158': [17], '159': [17], 'דנ-עפיף43': [5], 'דנ-צדקה-ב': [7], '78-son': [7], 'דנ-שלביה72': [7], 'דנ-מראד79': [7],
                'הס-ישמעאל-ב': [7], 'הס-אברהם-ב': [7], '120': [14, 7], '120א': [14, 7], '257': [7, 13, 18], 'הס-עבדהפתח': [7], 'הס-עבדאלה-ב': [7], 'הס-סלים120': [7],
                'הס-סעד-מתאסלם': [7, 13], 'הס-חבובה': [7, 13], '149': [14, 7], '161': [14], '162': [14, 7], 'הס-שלח162': [7, 2, 18], 'הס-יהודה162': [7, 2, 18], 'הס-אברהם162': [7, 2, 18], '163': [14, 7, 2, 18],
                '206': [23], '207': [23], 'מר-אברהם184': [22, 23], 'הס-עבדאלה140': [16], 'הס-סלים140': [16], 'דנ-נדיה-זבולן': [2], 'דנ-ורדה-גמליאל': [6, 2], 'דנ-יוכבד-גמליאל': [6], 'דנ-אבסכוה-גמליאל': [6], 'דנ-אברהם-שלום': [6], 'דנ-שמסה-חילמי': [9], 'דנ-שלפי-חילמי': [9], 'דנ-נדים-משלמה': [10], 'דנ-מדחת-משלמה': [10], 'דנ-מדיחה-משלמה': [10],
                '150': [14, 17, 28], '151': [14, 17], '152': [14, 17, 25], '153': [14, 16, 17],
                '154': [14, 17], '155': [14, 17], '157': [14, 17], '160': [14, 17, 25],
                '203': [22, 23], 'דנ-עארוף110': [12, 13], 'דנ-אלקוע101': [12], 'דנ-נזמיה58': [2, 6], '105': [9, 12, 16], '106': [10, 12, 16], '108': [10, 12],
                 '204': [23], '208': [23], 'צפ-אברהם242': [29], 'צפ-גמליאל242': [29], 'צפ-אלקנה247': [29], '205': [22, 23], 'מר-יוסף175': [21], 'מר-רצון175': [21], 'צפ-אבזהותה211': [25], 'מר-אברהם208': [23],
                'הס-יוסף122': [15], 'הס-ישראל133': [15, 16], 'הס-אברהם133': [15, 16], 'הס-יוסף137': [13, 15], 'הס-יוסף138': [13, 15],
                '141': [14, 15, 16, 17], '142': [14, 15, 16, 17], '143': [14, 15, 17], '144': [14, 15, 17], '145': [14, 15, 17], '146': [14, 15, 17],
                'הס-עזיזה143': [15, 17], '147': [14, 15, 17], '148': [14, 15, 17]}
BOOK = 'ספר «תולדות בני ישראל השומרונים»'


def book_src(pid, name):
    n = None
    m = re.search(r'כה״ג\s+(\d+)', name or '')
    if pid.startswith('שכם') or (pid.startswith('כ-') and False):
        if m: n = int(m.group(1))
        if n:
            pg = 20 if n <= 23 else 21 if n <= 49 else 22 if n <= 82 else 23 if n <= 92 else 24
            return f'{BOOK} — רשימת הכהנים הגדולים (מס׳ {n}), עמוד {pg} בקובץ הסרוק של הספר'
        return f'{BOOK} — רשימת הכהנים הגדולים, עמודים 20–24 בקובץ הסרוק של הספר'
    if pid.startswith('דמשק'):
        return f'{BOOK} — רשימת משני הכה״ג בדמשק, עמוד 25 בקובץ הסרוק של הספר'
    if pid.startswith('קהיר'):
        return f'{BOOK} — רשימת כהני קהיר הלוים, עמוד 26 בקובץ הסרוק של הספר'
    if pid.startswith('כ-'):
        return f'{BOOK} — סעיף צ׳, משפחת הכהנים מבני איתמר, עמוד 18 בקובץ הסרוק של הספר'
    return None


P87_IDS = ('122','123','124','125','126','127','128','129','130','131','132','133','134','135','136','137','138','139','140',
           '150','151','152','153','154','155','156','157','158','159','160')   # also drawn in the printed trees of page 87
EXTRA_PAGES = {i: [7] for i in ('121','122','135','150','71','72','73','74','75','75א','76','77','78','78-son','79','80','81','82','83','ר-שלביה')}   # also drawn in the printed tree of page 79
for _i in P87_IDS: EXTRA_PAGES[_i] = sorted(set(EXTRA_PAGES.get(_i, []) + [15]))
import os as _os
if _os.path.exists('tree_pages.json'):
    for _i, _pg in json.load(io.open('tree_pages.json', encoding='utf-8')).items():
        EXTRA_PAGES[_i] = sorted(set(EXTRA_PAGES.get(_i, []) + _pg))     # pages 91 / 97 (pdf 19 / 25) drawn trees
APEX_NOTE = f'{ART} — עמוד 75 (עמוד 3 בקובץ הסרוק): עצי החיים — צמרות המשפחות'
UNKNOWN = f'{ART} — העמוד המדויק לא אותר'
n_by = {'excel': 0, 'art': 0, 'book': 0, 'apex': 0, 'unknown': 0, 'admin': 0}

APEX_PREFIX = ('דנ-', 'צפ-אבזהותה', 'צפ-שלח', 'צפ-שלמה-א', 'צפ-יוסף', 'צפ-פריזה', 'מר-יעקב-אברהם', 'מר-אברהם-מ', 'מר-אפרים', 'מר-ברוך', 'מר-מרחיב-י')
APEX_ANCHORS = ('מר-אב-מרחיב', 'מר-אב-יעקב', 'צפ-ישמעאל')
for pid, p in P.items():
    src = None
    if pid.startswith(APEX_PREFIX) and pid not in MANUAL_PAGES:
        src = APEX_NOTE; n_by['apex'] += 1
    elif pid.startswith(('שכם', 'דמשק', 'קהיר', 'כ-')):
        src = book_src(pid, p.get('name')); n_by['book'] += 1
    elif pid in APEX_ANCHORS:
        src = APEX_NOTE + '; ופירוט בפרוזה של המאמר'; n_by['apex'] += 1
    elif pid in MANUAL_PAGES:
        src = art(MANUAL_PAGES[pid] + EXTRA_PAGES.get(pid, [])); n_by['art'] += 1
    elif pid in SF and SF[pid]['src']:
        pages = [int(re.sub(r'\D', '', s)) for s in SF[pid]['src']]
        pages = pages + EXTRA_PAGES.get(pid, [])
        src = art(pages); n_by['art'] += 1
    else:
        src = UNKNOWN; n_by['unknown'] += 1
    if pid == 'דנ-אברהם-ב':
        src = src + '; ופרטים נוספים: ויקיפדיה, הערך «אברהם בן יעקב הדנפי»'
    p['src'] = src

# ------------------------------------------------------------------ modern (Excel) + events + admin-restored
for m in integ['modern']:
    if re.fullmatch(r'M\d+', m['id']) and m['id'] in excel_rows:
        e = excel_rows[m['id']]
        m['src'] = f"קובץ מיפקד.xlsx — גיליון «{e['sheet']}», שורה {e['row']}"; n_by['excel'] += 1
    elif m['id'].startswith('ev-'):
        m['src'] = 'נוסף מסגל האירועים ונערך ע״י מנהל באתר'; n_by['admin'] += 1
    else:
        m['src'] = 'מקור לא אותר'; n_by['unknown'] += 1
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
print(n_by)
for pid, p in P.items():
    if p['src'] == UNKNOWN: print('  unplaced:', pid, p.get('name'))
