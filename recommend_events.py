# -*- coding: utf-8 -*-
# READ-ONLY: finds the HIGHEST-probability integrations — event records whose PERSON
# (not just the father) confidently matches an existing tree person who is MISSING that
# year. Recommends safe enrichments (add birth/death year). Writes nothing.
import json, io, re, sys, csv
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
exec(open('produce_crosscheck.py', encoding='utf-8').read().split('rows=[]')[0])  # loaders + helpers + best_match
stories = json.load(io.open('stories.json', encoding='utf-8'))

def person_year(pid):
    g = (stories.get(pid,{}) or {}).get('g','')
    return g
def has_birth(pid):
    g = person_year(pid); return bool(re.match(r'\s*\d{3,4}', g or ''))
def has_death(pid):
    g = person_year(pid) or ''
    return '–' in g and bool(re.search(r'–\s*\d', g))

def father_given2(pid):
    p=persons.get(pid)
    if not p: return None
    fid=p.get('father')
    if fid and fid in persons:
        ws=words_he(persons[fid]['name']); return canon2(ws[0]) if ws else None
    fn=p.get('fatherName')
    if fn: ws=words_he(fn); return canon2(ws[0]) if ws else None
    return None

# index persons by (given canon2) -> ids
pidx = {}
for pid,p in persons.items():
    for w in set(canon2(x) for x in words_he(p['name'])):
        pidx.setdefault(w, []).append(pid)

def match_person(rec):
    """match the record's PERSON (name) + its father-chain to a unique tree person."""
    nb = words(rec.get('name','')); fa = words(rec.get('father',''))
    if not nb: return (None,'')
    pg = canon2(nb[0]); fg = canon2(fa[0]) if fa else None
    famtag=''
    for w in fa[::-1]:
        if w in FAM: famtag=FAM[w]; break
    cands = pidx.get(pg, [])
    scored=[]
    for pid in cands:
        s=0; fgl=father_given2(pid)
        if fg and fgl and (fg==fgl or fg in fgl or fgl in fg): s+=2
        if famtag and tag_in_house(famtag, persons[pid]['house']): s+=1
        scored.append((s,pid))
    if not scored: return (None,'')
    scored.sort(reverse=True); top=scored[0]
    if top[0] < 2: return (None,'low')                       # require father-given confirmation
    if sum(1 for s,_ in scored if s==top[0])>1: return (None,'tie')
    return (top[1], 'high' if top[0]>=3 else 'med')

def yr4(rec):
    if rec.get('src')=='xlsx':
        m=re.fullmatch(r'(20[0-2]\d)', (rec.get('sheet') or '').strip()); return m.group(1) if m else ''
    y=(rec.get('year') or '').strip(); m=re.match(r'(\d{4})$',y)
    return m.group(1) if (m and 1880<=int(m.group(1))<=2030) else ''

def approx_birth(pid):
    g=(stories.get(pid,{}) or {}).get('g',''); m=re.match(r'(\d{3,4})',g or '')
    if m: return int(m.group(1))
    b=(node_birth.get(pid));
    if isinstance(b,int): return b+584
    for x in mods:
        if x['id']==pid: return x.get('byear')
    return None
node_birth={}
for h in master['houses']:
    for f in h['families']:
        for p in f['persons']:
            node_birth[p['id']]=p.get('birth')
SPINE=('כ-','שכם','דמשק','קהיר')                 # ancient priestly nodes — never match modern events

rec_births=[]; rec_deaths=[]
for rec in events:
    pid,conf = match_person(rec)
    if not pid or conf not in ('high','med'): continue
    if str(pid).startswith(SPINE): continue          # exclude ancient priestly match-magnets
    y = yr4(rec)
    if not y: continue
    ab = approx_birth(pid)                            # era consistency: the matched person's own era must fit
    if ab is not None and abs(int(y) - ab) > 8: continue
    p = persons[pid]
    if rec.get('event')=='death' and not has_death(pid):
        rec_deaths.append((conf,pid,p['name'],p['house'],y,rec.get('name',''),rec.get('father','')))
    elif rec.get('event')=='birth' and not has_birth(pid):
        rec_births.append((conf,pid,p['name'],p['house'],y,rec.get('name',''),rec.get('father','')))

# dedupe by pid (keep first/high)
def dedupe(lst):
    seen={}; out=[]
    for t in sorted(lst, key=lambda x:0 if x[0]=='high' else 1):
        if t[1] in seen: continue
        seen[t[1]]=1; out.append(t)
    return out
rec_births=dedupe(rec_births); rec_deaths=dedupe(rec_deaths)

print('=== המלצות סבירות-גבוהה (העשרת אנשים קיימים) ===')
print('שנות-פטירה להוספה (אדם קיים, חסרה פטירה):', len(rec_deaths))
print('שנות-לידה להוספה (אדם קיים, חסרה לידה):', len(rec_births))
print('  high:', sum(1 for x in rec_deaths+rec_births if x[0]=='high'), '· med:', sum(1 for x in rec_deaths+rec_births if x[0]=='med'))
print()
print('--- שנות-פטירה (top, high-conf) ---')
for c,pid,nm,hs,y,an,af in [x for x in rec_deaths if x[0]=='high'][:25]:
    print('  פטירה %s → %-22s [%s] | מקור: %s בن %s'%(y,nm,pid,an[:14],af[:22]))
print('--- שנות-לידה (top, high-conf) ---')
for c,pid,nm,hs,y,an,af in [x for x in rec_births if x[0]=='high'][:25]:
    print('  לידה %s → %-22s [%s] | מקור: %s בن %s'%(y,nm,pid,an[:14],af[:22]))

# save full recommendations
with io.open('events_recommend.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f); w.writerow(['סוג','שנה','מזהה','שם_בעץ','בית_אב','ביטחון','שם_במקור','אב_במקור'])
    for c,pid,nm,hs,y,an,af in rec_deaths: w.writerow(['פטירה',y,pid,nm,hs,c,an,af])
    for c,pid,nm,hs,y,an,af in rec_births: w.writerow(['לידה',y,pid,nm,hs,c,an,af])
print('\nכל ההמלצות נשמרו: events_recommend.csv')
