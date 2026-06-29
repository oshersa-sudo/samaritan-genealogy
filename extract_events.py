# -*- coding: utf-8 -*-
# READ-ONLY: extracts birth/death/marriage records (Arabic) from the two community
# event registries, normalizes them, and dumps a structured JSON for cross-checking.
# Does NOT touch the tree / master_v2.json.
import xlrd, openpyxl, json, io, re, sys, os
sys.stdout.reconfigure(encoding='utf-8')

XLS = r'C:\Users\osher\Downloads\سجل المناسبات السامرية.xls'      # historical 1888-1979+
XLSX = r'C:\Users\osher\Downloads\سجل المناسبات الجديد.xlsx'      # 2001-2026

def clean(v):
    if v is None: return ''
    s = str(v).strip()
    if re.fullmatch(r'[_ـ\-\s]+', s): return ''          # separator rows (____ / ـــــ)
    if s in ('لا يوجد', 'None'): return ''
    s = re.sub(r'\.0$', '', s)                            # "1909.0" -> "1909"
    return re.sub(r'\s+', ' ', s).strip()

def evtype(s):
    s = s or ''
    if 'ميلاد' in s or s.strip()=='م': return 'birth'
    if 'وفاة' in s or 'وفا' in s or s.strip()=='و': return 'death'
    if 'زواج' in s or 'قران' in s or s.strip()=='ز': return 'marriage'
    if 'حادث' in s or s.strip()=='ح': return 'incident'
    return ''

records = []

# ---------- .xls : 9 cols [#, year, date, hebdate, event, name, father, mother, notes] ----------
wb = xlrd.open_workbook(XLS)
for sh in wb.sheets():
    for r in range(sh.nrows):
        row = [clean(sh.cell_value(r, c)) for c in range(sh.ncols)]
        if len(row) < 9: row += ['']*(9-len(row))
        et = evtype(row[4])
        name, father, mother = row[5], row[6], row[7]
        if not (name or father): continue
        if 'الاسم' in name or 'الرقم' in row[0]: continue   # header rows
        records.append({'src':'xls','sheet':sh.name,'year':row[1] or row[2],'event':et,
                        'name':name,'father':father,'mother':mother,'notes':row[8]})

# ---------- .xlsx : per-year sheets, births section [#, date, name, sex, place, father, *, mother] ----------
wx = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
for ws in wx.worksheets:
    if ws.max_row < 5: continue
    yr = re.sub(r'\D','',ws.title)[:4] or ws.title
    for row in ws.iter_rows(values_only=True):
        cells = [clean(c) for c in row]
        if len(cells) < 8: cells += ['']*(8-len(cells))
        num = cells[0]
        if not re.fullmatch(r'\d+', num or ''): continue    # only numbered data rows
        name, sex, place, father = cells[2], cells[3], cells[4], cells[5]
        mother = cells[7] or cells[6]
        if name or father:
            records.append({'src':'xlsx','sheet':ws.title,'year':yr,'event':'birth',
                            'name':name,'sex':sex,'place':place,'father':father,'mother':mother})
        # marriage columns (husband/wife) appear later in the row, layout varies — capture last two non-empty
        tail = [c for c in cells[8:] if c]
        groom = next((c for c in tail if c not in ('عقد القران','الزواج','زواج','ع','ز/ع','اسم الزوج','اسم الزوجة')), '')
        # (marriages parsed loosely; flagged for manual review)

io.open(r'C:\Users\osher\Documents\sam_Genealogy\files\events_extracted.json','w',encoding='utf-8')\
  .write(json.dumps(records, ensure_ascii=False, indent=1))

from collections import Counter
print('total records:', len(records))
print('by source:', dict(Counter(r['src'] for r in records)))
print('by event:', dict(Counter(r['event'] for r in records)))
# decade spread
def dec(y):
    m=re.match(r'(\d{4})',y or ''); return (m.group(1)[:3]+'0s') if m else '?'
print('by decade:', dict(sorted(Counter(dec(r['year']) for r in records).items())))
print()
print('--- sample births (xls, historical) ---')
for r in [x for x in records if x['src']=='xls' and x['event']=='birth'][:6]:
    print('  %s | %s | אב: %s | אם: %s'%(r['year'],r['name'],r['father'],r['mother']))
print('--- sample births (xlsx, modern) ---')
for r in [x for x in records if x['src']=='xlsx'][:6]:
    print('  %s | %s | אב: %s | אם: %s'%(r['year'],r['name'],r['father'],r['mother']))
