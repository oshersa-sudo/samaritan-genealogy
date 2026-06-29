# -*- coding: utf-8 -*-
# READ-ONLY: improved Arabic->Hebrew matching of the event records to the tree, and a
# full review CSV (events_crosscheck.csv). Writes nothing to the tree.
import json, io, re, sys, csv
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
exec(open('match_events.py', encoding='utf-8').read().split('# ---------- match each')[0])  # reuse loaders/helpers
STORIES = json.load(io.open('stories.json', encoding='utf-8'))

HOUSE_OF_TAG = {'דנפים':'דנפים','מרחיבים':'מרחיבים','צפרים':'צפרים','כהונה':'כהונה'}
def tag_in_house(tag, house):
    if not tag: return False
    for t in tag.split('/'):
        if t and t in (house or ''): return True
    return False

# letters that Arabic transliteration confuses -> collapse for matching
def loose2(w):
    # only collapse the genuine Arabic->Hebrew ambiguities, not everything
    w = loose(w)
    w = w.replace('ש','ס')           # Arabic س/ش -> ס or ש (e.g. اسرائيل=ישראל)
    return w
def canon2(w): return loose2(GIVEN.get(w, w))

# rebuild the given-index using loose2 + ALSO index nickname tokens from each person's story
by_given2 = {}
def add_idx(tok, pid):
    if tok and len(tok)>=2: by_given2.setdefault(tok, set()).add(pid)
for pid,p in persons.items():
    for w in words_he(p['name']): add_idx(canon2(w), pid)
    st = (STORIES.get(pid,{}) or {}).get('t','')
    # index single Hebrew words from the story that look like names (length>=3), cheap nickname capture
    for w in re.findall(r'[֐-׿]{3,}', st)[:30]:
        add_idx(loose2(w), pid)

def father_given2(pid):
    p=persons.get(pid)
    if not p: return None
    fid=p.get('father')
    if fid and fid in persons:
        ws=words_he(persons[fid]['name']); return canon2(ws[0]) if ws else None
    fn=p.get('fatherName')
    if fn: ws=words_he(fn); return canon2(ws[0]) if ws else None
    return None

def best_match(rec):
    nb=words(rec.get('name','')); fa=words(rec.get('father',''))
    if not fa: return ('', 'no-father', '')
    fg=canon2(fa[0]); fgf=canon2(fa[1]) if len(fa)>1 else None
    famtag=''
    for w in fa[::-1]:
        if w in FAM: famtag=FAM[w]; break
    cands=list(by_given2.get(fg,[]))
    if not cands: return ('', 'no-match', famtag)
    # rank: grandfather match (+2), house/family match (+1)
    scored=[]
    for pid in cands:
        s=0; fgl=father_given2(pid)
        if fgf and fgl and (fgf==fgl or fgf in fgl or fgl in fgf): s+=2
        if tag_in_house(famtag, persons[pid]['house']): s+=1
        scored.append((s,pid))
    scored.sort(reverse=True)
    top=scored[0]
    conf = 'high' if top[0]>=3 else ('med' if top[0]>=1 else 'low')
    # unique high/med?
    if conf!='low' and sum(1 for s,_ in scored if s==top[0])>1: conf+='?'
    return (top[1], conf, famtag)

rows=[]; stat=Counter()
for rec in events:
    if rec.get('event')!='birth': continue
    pid,conf,famtag=best_match(rec)
    pn=persons[pid]['name'] if pid else ''
    ph=persons[pid]['house'] if pid else ''
    stat[conf.replace('?','')+('?' if conf.endswith('?') else '')]+=1
    stat['_'+ (conf.split('?')[0] if conf in('high','med','low','high?','med?') else conf)]+=1
    rows.append({'מקור':rec['src'],'שנה':rec.get('year',''),'אירוע':rec.get('event'),
                 'שם':rec.get('name',''),'אב':rec.get('father',''),'אם':rec.get('mother',''),
                 'התאמה_בעץ':pn,'מזהה':pid,'בית_אב':ph,'ביטחון':conf})

with io.open('events_crosscheck.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f, fieldnames=['מקור','שנה','אירוע','שם','אב','אם','התאמה_בעץ','מזהה','בית_אב','ביטחון'])
    w.writeheader(); w.writerows(rows)

print('births matched:', len(rows))
c=Counter(r['ביטחון'] for r in rows)
print('confidence:', dict(c))
hi=c.get('high',0)+c.get('med',0); amb=c.get('high?',0)+c.get('med?',0)
print('confident (high+med): %d (%.0f%%) · ambiguous: %d · no/low: %d'%(hi,100*hi/len(rows),amb,c.get('no-match',0)+c.get('low',0)+c.get('no-father',0)))
print('CSV written: events_crosscheck.csv (',len(rows),'rows )')
print()
print('--- sample HIGH-confidence matches ---')
for r in rows:
    if r['ביטחון']=='high':
        print('  %-5s %-12s אב=%-26s → %s [%s]'%(r['שנה'],r['שם'],r['אב'],r['התאמה_בעץ'],r['בית_אב'].replace('בית אב ','')))
        if sum(1 for x in rows if x['ביטחון']=='high')>0 and rows.index(r)>40: break
