# -*- coding: utf-8 -*-
# HIGH-CONFIDENCE enrichment of EXISTING people with DEATH years (and Gregorian birth years
# for census people who lack one) from the event registries. ADDITIVE ONLY — never changes
# a name or a tree position, never overwrites an existing year. DRY unless --apply.
# Starts with the Danfi house. Match must be unique + father-confirmed + era-plausible.
import json, io, re, sys, datetime
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
DRY = '--apply' not in sys.argv
exec(open('produce_crosscheck.py', encoding='utf-8').read().split('rows=[]')[0])   # helpers, persons, by_given2
stories = json.load(io.open('stories.json', encoding='utf-8'))
master = json.load(io.open('master_v2.json', encoding='utf-8'))
node_birth = {p['id']: p.get('birth') for h in master['houses'] for f in h['families'] for p in f['persons']}
DANFI_FAM = {'אלטיפ','אלטיף','אלטיו','סראוי','אלסראוי','דנפי','שלבי','שלפי','משלמה','מסלמה','עבדאללה'}

def father_g(pid):
    p=persons.get(pid); fid=p.get('father') if p else None
    if fid and fid in persons:
        w=words_he(persons[fid]['name']); return canon2(w[0]) if w else ''
    if p and p.get('fatherName'):
        w=words_he(p['fatherName']); return canon2(w[0]) if w else ''
    return ''
def birth_of(pid):
    g=(stories.get(pid,{}) or {}).get('g',''); mm=re.match(r'\s*(\d{3,4})',g or '')
    if mm: return int(mm.group(1))
    b=node_birth.get(pid); return (b+584) if isinstance(b,int) else None
def has_death(pid):
    g=(stories.get(pid,{}) or {}).get('g','') or ''
    return bool(re.search(r'–\s*\d{3,4}', g))
def clean_name(ar):
    ar=re.split(r'\bزوج[ةه]?\b|\bأرملة\b|[(\\/]', ar)[0]
    return re.sub(r'\s+',' ', ar2he(ar)).strip()

def match_unique(gv, fg, ref_year):
    """unique existing person: token-given + father-given confirmed + era-plausible."""
    cands=[]
    for pid in by_given2.get(gv,()):
        if str(pid).startswith(('שכם','דמשק','קהיר','כ-','ev-')): continue   # not real census/modern people
        efg=father_g(pid)
        if not (fg and efg and (fg==efg or fg in efg or efg in fg)): continue
        by=birth_of(pid)
        if by is None: continue
        if ref_year and not (0 <= int(ref_year)-by <= 110): continue        # plausible lifespan
        cands.append(pid)
    cands=list(dict.fromkeys(cands))
    return cands[0] if len(cands)==1 else None

death_enr=[]; birth_enr=[]; seen=set()
for rec in events:
    fa=words(rec.get('father',''))
    # enrichment matches against the WHOLE tree (match_unique is house-agnostic), so process
    # every record — no house filter needed.
    he=clean_name(rec.get('name',''));
    if len(he)<2: continue
    gv=canon2(he.split()[0]); fg=canon2(fa[0]) if fa else ''
    if not fg: continue
    y=(rec.get('year') or '').strip(); ym=re.match(r'(\d{4})$',y); year=ym.group(1) if (ym and 1880<=int(ym.group(1))<=2026) else ''
    if rec.get('event')=='death' and year:
        pid=match_unique(gv,fg,year)
        if pid and not has_death(pid) and ('d',pid) not in seen:
            seen.add(('d',pid)); death_enr.append((pid,persons[pid]['name'],year,(stories.get(pid,{}) or {}).get('g',''),rec.get('name',''),rec.get('father','')))
    elif rec.get('event')=='birth' and year:
        pid=match_unique(gv,fg,year)
        # census person (numeric/alnum id) lacking ANY Gregorian year -> add birth year
        if pid and re.match(r'\d',str(pid)) and not re.match(r'\s*\d{3,4}',(stories.get(pid,{}) or {}).get('g','') or '') and abs(int(year)-(birth_of(pid) or 0))<=8 and ('b',pid) not in seen:
            seen.add(('b',pid)); birth_enr.append((pid,persons[pid]['name'],year,(stories.get(pid,{}) or {}).get('g',''),rec.get('name',''),rec.get('father','')))

print('Danfi HIGH-CONF enrichments — DEATH years:', len(death_enr), '· BIRTH years (census, missing):', len(birth_enr))
print('\n--- DEATH year additions ---')
for pid,nm,y,g,an,af in death_enr:
    print('  #%-6s %-20s  g: %-10s → +פטירה %s   | מקור: %s בن %s'%(pid,nm,g or '(אין)',y,an[:14],af[:24]))
print('\n--- BIRTH year additions (census missing Gregorian) ---')
for pid,nm,y,g,an,af in birth_enr:
    print('  #%-6s %-20s → +לידה %s   | מקור: %s בن %s'%(pid,nm,y,an[:14],af[:24]))

if DRY:
    print('\n(הרצת-יבש — לא נכתב כלום. להחלה: py -3 add_enrichments.py --apply)')
else:
    log=[]
    for pid,nm,y,g,an,af in death_enr:
        cur=(stories.get(pid) or {})
        gg=cur.get('g','') or ''
        mm=re.match(r'\s*(\d{3,4})\s*$', gg) or re.match(r'\s*(\d{3,4})\s*–\s*$', gg)
        newg = (mm.group(1)+'–'+y) if mm else (gg+'' if has_death(pid) else (gg.rstrip('–')+'–'+y if gg else '–'+y))
        stories[pid]=dict(cur); stories[pid]['g']=newg
        log.append(('פטירה',pid,nm,y,gg,newg))
    for pid,nm,y,g,an,af in birth_enr:
        cur=(stories.get(pid) or {}); stories[pid]=dict(cur); stories[pid]['g']=y+(stories[pid].get('g','').replace(y,'') and '' or '')
        log.append(('לידה',pid,nm,y,g,y))
    io.open('stories.json','w',encoding='utf-8').write(json.dumps(stories,ensure_ascii=False,indent=1))
    # append to changelog
    ts=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    L=['','---','# העשרת קיימים — שנות פטירה/לידה (בטוח-גבוה, דנפים) · '+ts,
       'תוספתי בלבד — לא שונה שם/מיקום, לא נדרס ערך קיים.','',
       '| סוג | מזהה | שם | שנה | g לפני | g אחרי |','|---|---|---|---|---|---|']
    for ev,pid,nm,y,b,a in log: L.append('| %s | %s | %s | %s | %s | %s |'%(ev,pid,nm,y,b or '(אין)',a))
    io.open('EVENTS_INTEGRATION_LOG.md','a',encoding='utf-8').write('\n'.join(L))
    print('\nAPPLIED:', len(log), 'enrichments to existing people (additive only).')
