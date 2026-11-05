# -*- coding: utf-8 -*-
# 2026-11-06 — applies the owner-approved HIGH-confidence corrections to the scan layer
# (master_v2.json + stories.json). Source: genealogy_scan_corrections.xlsx, sheet 'תיקונים מוצעים',
# rows with ודאות='גבוהה' (38). Every correction was verified against the printed page.
# Writes scan_fixes_applied.json (before/after) so each change can be reversed. Idempotent.
import json, io, re, sys
import openpyxl
sys.stdout.reconfigure(encoding='utf-8')

XLSX = r'C:\Users\osher\Documents\torah\genealogy_scan_corrections.xlsx'
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}

ws = openpyxl.load_workbook(XLSX)['תיקונים מוצעים']
rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[8] == 'גבוהה']
print('high rows', len(rows))
log, skipped = [], []


def ref_for(proposed, printed):
    m = re.search(r'\((\d+)\)\s*$', proposed or '')
    n = m.group(1) if m else None
    if n:
        mm = re.search(r'\(' + n + r"[^)]*\)", printed or '')
        return (mm.group(0)[1:-1] if mm else n)
    ms = re.findall(r"\((\d+[^)]*)\)", printed or '')
    return ms[-1] if ms else None


def clean_name(s):
    return re.sub(r'\s*\(\d+\)\s*$', '', s or '').strip()


def nkey(s):
    return re.sub(r"[^\u05d0-\u05ea ]", '', re.sub(r'[\u0591-\u05c7]', '', s or '')).strip()


for r in rows:
    typ, pid, nm, house, field, site, printed, new = r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]
    p = P.get(pid)
    if not p:
        skipped.append((pid, field, 'person not found')); continue
    before = None
    if field == 'שם':
        before = p.get('name'); p['name'] = new
    elif field.startswith('שנת לידה (מפקד)'):
        before = p.get('birth'); p['birth'] = int(new)
    elif field.startswith('שנת פטירה (מפקד)'):
        before = p.get('death'); p['death'] = int(new)
    elif field in ('שנת לידה (לועזי)', 'שנת פטירה (לועזי)'):
        s = stories.setdefault(pid, {'t': '', 'g': ''})
        before = s.get('g', '')
        a, _, b = (before or '').partition('–')
        a, b = a.strip(), b.strip()
        if field == 'שנת לידה (לועזי)': a = str(new)
        else: b = str(new)
        s['g'] = f'{a}–{b}'
    elif field.startswith('בן/בת זוג'):
        sp = p.setdefault('spouses', [])
        nn = clean_name(new); rf = ref_for(new, printed)
        before = json.loads(json.dumps(sp, ensure_ascii=False))
        target = None
        if field == 'בן/בת זוג':                          # replace the wrongly read spouse
            ph = [s for s in sp if (s.get('name') or '').strip().startswith('[')]
            if ph: target = ph[0]
            else:
                import difflib
                target = max(sp, key=lambda s: difflib.SequenceMatcher(None, nkey(s.get('name')), nkey(site if False else nn)).ratio()) if sp else None
                if target and difflib.SequenceMatcher(None, nkey(target.get('name')), nkey(nn)).ratio() < 0.5: target = None
                # for several spouses compare against the 'site' cell too
                if target is None:
                    for s in sp:
                        if nkey(s.get('name')) and nkey(s.get('name')) in nkey(site or ''):
                            target = s
        if target is not None:
            target['name'] = nn
            if rf and not target.get('ref'): target['ref'] = rf
        else:
            if any(nkey(s.get('name')) == nkey(nn) for s in sp):
                skipped.append((pid, field, 'already present')); continue
            e = {'name': nn}
            if rf: e['ref'] = rf
            sp.append(e)
        after_sp = json.loads(json.dumps(sp, ensure_ascii=False))
        log.append({'id': pid, 'field': field, 'before': before, 'after': after_sp, 'printed': printed})
        continue
    else:
        skipped.append((pid, field, 'unknown field')); continue
    log.append({'id': pid, 'field': field, 'before': before, 'after': new, 'printed': printed})

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('scan_fixes_applied.json', 'w', encoding='utf-8').write(json.dumps({'applied': log, 'skipped': skipped}, ensure_ascii=False, indent=1))
print('applied', len(log), 'skipped', skipped)
