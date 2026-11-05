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
                'ר-סלגח49': [2], 'ר-שלביה': [8], 'ר-אינמר': [13], 'הס-נבון': [17], 'הס-וגיה': [17], 'הס-צער': [17], 'דנ-עפיף43': [5],
                'מר-יעקב202': [23], 'מר-ברור202': [23], 'מר-אברהם184': [22, 23], 'הס-עבדאלה140': [16], 'הס-סלים140': [16]}
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
        src = art(MANUAL_PAGES[pid]); n_by['art'] += 1
    elif pid in SF and SF[pid]['src']:
        pages = [int(re.sub(r'\D', '', s)) for s in SF[pid]['src']]
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
