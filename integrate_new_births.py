# -*- coding: utf-8 -*-
# Single, idempotent events-integration. Adds ONLY genuinely-new people from the event
# registries at HOUSE level (no guessed specific father), never touching existing people:
#   (1) modern births 2003-2026, every house (clear surname).
#   (2) historical births (1888-2002) + deaths, for houses in HIST_HOUSES (start: Danfi),
#       deduped against existing tree people (name+story tokens), labelled "לאימות".
import json, io, re, sys, datetime
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
exec(open('produce_crosscheck.py', encoding='utf-8').read().split('rows=[]')[0])  # helpers, persons, by_given2
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
node_birth = {p['id']: p.get('birth') for h in master['houses'] for f in h['families'] for p in f['persons']}

HOUSE = {'ב. בית אב הדנפים':{'fam':{'אלטיפ','אלטיף','אלטיו','סראוי','אלסראוי','דנפי','שלבי','שלפי','משלמה','מסלמה','עבדאללה'}},
         'ג. בית אב המרחיבים':{'fam':{'מרגאנ','מרחיב'}},
         'ד. בית אב הצפרים':{'fam':{'צדקה','צדקו'}}}
HIST_HOUSES = {'ב. בית אב הדנפים'}                     # houses that also get historical + deaths

def clean_name(ar):
    ar = re.split(r'\bزوج[ةه]?\b|\bأرملة\b|[(\\/]', ar)[0]   # drop "wife/widow of …" + bracketed notes
    return re.sub(r'\s+',' ', ar2he(ar)).strip()
def house_of_rec(fa):
    for hn,info in HOUSE.items():
        for w in fa[::-1]:
            if w in info['fam']: return hn
    return ''
def approxy(pid):
    g=(stories.get(pid,{}) or {}).get('g',''); mm=re.search(r'(\d{3,4})',g or '')
    if mm: return int(mm.group(1))
    b=node_birth.get(pid); return (b+584) if isinstance(b,int) else None
def father_g(pid):
    p=persons.get(pid); fid=p.get('father') if p else None
    if fid and fid in persons:
        w=words_he(persons[fid]['name']); return canon2(w[0]) if w else ''
    if p and p.get('fatherName'):
        w=words_he(p['fatherName']); return canon2(w[0]) if w else ''
    return ''
def exists(gv, fg):
    # dedupe by token-given (by_given2 indexes name AND story tokens, so nickname-variants
    # like חכמת=#129 are caught) + father-given. Checks ALL persons (over-dedup is safe).
    for pid in by_given2.get(gv,()):
        efg=father_g(pid)
        if fg and efg and (fg==efg or fg in efg or efg in fg): return True
        if not fg: return True
    return False

def yr_modern(rec):
    t=(rec.get('sheet') or '').strip(); return t if (rec['src']=='xlsx' and re.fullmatch(r'20[0-2]\d',t) and int(t)>=2003) else ''
def yr_hist(rec):
    if rec['src']=='xls':
        mm=re.match(r'(\d{4})$',(rec.get('year') or '').strip()); return mm.group(1) if (mm and 1880<=int(mm.group(1))<=2002) else ''
    t=(rec.get('sheet') or '').strip(); return t if (re.fullmatch(r'20[0-2]\d',t) and int(t)<2003) else ''

modern={}; hist={}; deaths={}; seen=set()
for rec in events:
    ev=rec.get('event')
    if ev not in ('birth','death'): continue
    fa=words(rec.get('father',''))
    hn=house_of_rec(fa)
    if not hn: continue
    he=clean_name(rec.get('name',''))
    if len(he)<2: continue
    gv=canon2(he.split()[0]); fg=canon2(fa[0]) if fa else ''
    sx='F' if ('أنثى' in (rec.get('sex','') or '') or 'زوج' in (rec.get('name','') or '')) else ('M' if 'ذكر' in (rec.get('sex','') or '') else '')
    item=lambda y:{'year':y,'name':he,'sex':sx,'father':rec.get('father',''),'mother':rec.get('mother','')}
    ym=yr_modern(rec)
    if ev=='birth' and ym:
        if exists(gv,fg): continue
        k=(hn,gv,fg,ym)
        if k in seen: continue
        seen.add(k); modern.setdefault(hn,[]).append(item(ym)); continue
    if hn not in HIST_HOUSES: continue
    yh=yr_hist(rec)
    if not yh: continue
    if ev=='birth':
        if exists(gv,fg): continue
        k=(hn,gv,fg,yh,'b')
        if k in seen: continue
        seen.add(k); hist.setdefault(hn,[]).append(item(yh))
    else:  # death — dedupe by name+father only (death year never equals birth year)
        if exists(gv,fg): continue
        k=(hn,gv,fg,'d')
        if k in seen: continue
        seen.add(k); deaths.setdefault(hn,[]).append(item(yh))

# rebuild events families idempotently
for h in master['houses']:
    h['families']=[f for f in h['families'] if not f.get('_events')]
for kk in [k for k in stories if str(k).startswith('ev-')]: del stories[kk]
seq=0; log=[]
def mk_root(hn, key, label, note, items, is_death):
    global seq
    if not items: return None
    items.sort(key=lambda x:x['year'])
    rid='ev-root-%s-%s'%(key, re.sub(r'\W','',hn)[:4]); kids=[]
    for it in items:
        seq+=1; nid='ev-%d'%seq
        p={'id':nid,'name':it['name'],'father_id':rid}
        if it['sex']: p['sex']=it['sex']
        kids.append(p)
        g = ('–'+it['year']) if is_death else it['year']
        t = ('פטירה '+it['year']+'. ' if is_death else 'לידה '+it['year']+'. ')+'מקור: סגל המאורעות הסامרי. אב: '+it['father']+(' · אם: '+it['mother'] if it['mother'] else '')+('. (ייתכן חופף לאדם קיים — לאימות)' if (is_death or key=='hist') else '')
        stories[nid]={'t':t,'g':g}
        log.append((hn, ('פטירה' if is_death else 'לידה'), it['year'], it['name'], it['father']))
    root={'id':rid,'name':label,'sex':'','note':note,'children_ids':[k['id'] for k in kids]}
    return [root]+kids

for h in master['houses']:
    hn=h['house']; roots=[]
    r=mk_root(hn,'mod','📋 לידות מהמרשם 2003–2026','לידות חדשות מהמרשם, מקובצות ברמת בית-האב.',modern.get(hn,[]),False)
    if r: roots+=r
    r=mk_root(hn,'hist','📋 לידות היסטוריות מהמרשם (לאימות)','לידות 1888–2002 שלא אותרו בעץ — ייתכן חופפות, לאימות.',hist.get(hn,[]),False)
    if r: roots+=r
    r=mk_root(hn,'death','📋 פטירות מהמרשם (לאימות)','פטירות מהמרשם — אנשים שלא אותרו בעץ, לאימות.',deaths.get(hn,[]),True)
    if r: roots+=r
    if roots:
        h['families'].append({'family_no':99,'family':'מרשם המאורעות','ref_code':'אירועים','_events':True,
            'source_note':'מתוך "سجل المناسبات". רק רשומות שלא אותרו בעץ, ברמת בית-האב, ללא ניחוש אב ושינוי קיימים.','persons':roots})

io.open('master_v2.json','w',encoding='utf-8').write(json.dumps(master,ensure_ascii=False,indent=1))
io.open('stories.json','w',encoding='utf-8').write(json.dumps(stories,ensure_ascii=False,indent=1))
ts=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
L=['# לוג שילוב — סגל המאורעות','','**תאריך:** '+ts,'**גיבוי:** `backup_*` + `*.bak`.','',
   '## סיכום: %d אנשים נוספו (ברמת בית-האב, חדשים בלבד)'%len(log),'']
for k,v in Counter((x[0].split('בית אב ')[-1],x[1]) for x in log).items(): L.append('- %s · %s: %d'%(k[0],k[1],v))
L+=['','> לידות 2003-2026: ודאיות (חדשות לגמרי). לידות-היסטוריות+פטירות: סומנו "לאימות" כי ייתכן חופפות לאדם קיים תחת וריאנט-שם.','',
    '## פירוט','','| בית-אב | סוג | שנה | שם | אב (מקור) |','|---|---|---|---|---|']
for hn,ev,y,nm,fa in log: L.append('| %s | %s | %s | %s | %s |'%(hn.split('בית אב ')[-1],ev,y,nm,fa))
io.open('EVENTS_INTEGRATION_LOG.md','w',encoding='utf-8').write('\n'.join(L))
print('ADDED', len(log), '| modern:', sum(len(v) for v in modern.values()), 'hist:', sum(len(v) for v in hist.values()), 'deaths:', sum(len(v) for v in deaths.values()))
print('Danfi hist+death sample:')
for hn,ev,y,nm,fa in [x for x in log if 'דנפים' in x[0] and x[1] in('פטירה',) or ('דנפים' in x[0] and x[2] and int(x[2])<2003 and x[1]=='לידה')][:12]:
    print('  %s %s %s | %s'%(ev,y,nm,fa[:30]))
