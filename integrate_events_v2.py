# -*- coding: utf-8 -*-
# v2 events integration — adds genuinely-NEW registry people as MODERN entries in
# integrate.json (so they link via the modern-merge), with TWO connection levels:
#   • father-LINKED: the father's name+grandfather strictly match a unique modern person
#     (age-plausible) -> parent = that M-id (a real parent connection).
#   • house-level:    clear surname but no confident father -> parent = '@H:<tag>'.
# Never touches existing people. Cleans prior ev- (master families + integrate modern).
# Run AFTER resolve2.py (which regenerates integrate.json) and before build.
import json, io, re, sys, datetime
from collections import defaultdict, Counter
sys.stdout.reconfigure(encoding='utf-8')
exec(open('produce_crosscheck.py', encoding='utf-8').read().split('rows=[]')[0])   # helpers, persons, by_given2
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))
mods = integ.get('modern', []); mod_by_id = {x['id']: x for x in mods}

# ---- strict transliteration match (keep vowels; only ש/ש→ס) ----
NIQ=''.join(chr(c) for c in range(0x0591,0x05C8)); FIN={'ם':'מ','ן':'נ','ץ':'צ','ף':'פ','ך':'כ'}
def norm1(w): w=''.join(FIN.get(c,c) for c in re.sub('['+NIQ+']','',w)); return w.replace('ש','ס').replace("'",'')
def lev(a,b):
    if a==b: return 0
    if abs(len(a)-len(b))>2: return 9
    d=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        p=d[0]; d[0]=i
        for j,cb in enumerate(b,1):
            t=d[j]; d[j]=min(d[j]+1,d[j-1]+1,p+(ca!=cb)); p=t
    return d[-1]
GIVENMAP={'אסחק':'יצחק','אבראהים':'אברהם','אבראהימ':'אברהם','אסמאעיל':'ישמעאל','יעקוב':'יעקב',
 'יוספ':'יוסף','עמראנ':'עמרם','הארונ':'אהרן','אהרונ':'אהרן','צדקו':'צדקה'}
def keyn(w): return norm1(GIVENMAP.get(w,w))
def gmatch(a,b): return keyn(a)==keyn(b) or lev(keyn(a),keyn(b))<=1

midx=defaultdict(list)
for x in mods:
    w=words_he(x.get('name',''))
    if w: midx[keyn(w[0])].append(x['id'])
def mfg(mid):
    x=mod_by_id.get(mid); w=words_he(x.get('father','')) if x else []; return w[0] if w else ''
def match_father(fc, child_year):
    """unique modern person matching father given+grandfather, age-plausible."""
    if len(fc)<1: return None
    fg=fc[0]; fgf=fc[1] if len(fc)>1 else ''
    cands=[]
    for mid in midx.get(keyn(fg),[]):
        if fgf and not gmatch(fgf, mfg(mid)): continue
        x=mod_by_id[mid]
        if child_year and x.get('byear') and not (15 <= int(child_year)-x['byear'] <= 55): continue
        cands.append(mid)
    cands=list(dict.fromkeys(cands))
    return cands[0] if len(cands)==1 else None

FAM2H={'צדקה':'צפרים','צדקו':'צפרים','אלטיפ':'דנפים','אלטיף':'דנפים','אלטיו':'דנפים','סראוי':'דנפים',
 'אלסראוי':'דנפים','דנפי':'דנפים','שלבי':'דנפים','שלפי':'דנפים','משלמה':'דנפים','מסלמה':'דנפים',
 'עבדאללה':'דנפים','מרגאנ':'מרחיבים','מרחיב':'מרחיבים'}
def house_tag(fa):
    for w in fa[::-1]:
        if w in FAM2H: return FAM2H[w]
    return ''
def clean_name(ar):
    ar=re.split(r'\bزوج[ةه]?\b|\bأرملة\b|[(\\/]', ar)[0]; return re.sub(r'\s+',' ',ar2he(ar)).strip()
def exists(gv, fg):
    for pid in by_given2.get(gv,()):
        efg=''
        p=persons.get(pid); fid=p.get('father') if p else None
        if fid and fid in persons:
            w=words_he(persons[fid]['name']); efg=canon2(w[0]) if w else ''
        elif p and p.get('fatherName'):
            w=words_he(p['fatherName']); efg=canon2(w[0]) if w else ''
        if fg and efg and (fg==efg or fg in efg or efg in fg): return True
        if not fg: return True
    return False

new=[]; seen=set(); stat=Counter()
for rec in events:
    if rec.get('event')!='birth': continue
    fa=words(rec.get('father','')); tag=house_tag(fa)
    if not tag: continue
    he=clean_name(rec.get('name',''))
    if len(he)<2: continue
    t=(rec.get('sheet') or '').strip(); ym = t if (rec['src']=='xlsx' and re.fullmatch(r'20[0-2]\d',t) and int(t)>=2003) else ''
    if not ym: continue                                  # genuinely-new modern births only
    gv=canon2(he.split()[0]); fg=canon2(fa[0]) if fa else ''
    if exists(gv,fg): continue
    k=(gv,fg,ym)
    if k in seen: continue
    seen.add(k)
    mid=match_father(fa, ym)
    sx='F' if 'أنثى' in (rec.get('sex','') or '') else ('M' if 'ذكر' in (rec.get('sex','') or '') else '')
    new.append({'name':he,'sex':sx,'year':ym,'parent_mid':mid,'tag':tag,'father':rec.get('father',''),'mother':rec.get('mother','')})
    stat['linked' if mid else 'house']+=1

# historical births (pre-2003) + deaths — house-level only (no modern father), Danfi/Marhibi/Tsfari
for rec in events:
    ev=rec.get('event')
    if ev not in ('birth','death'): continue
    fa=words(rec.get('father','')); tag=house_tag(fa)
    if not tag: continue
    he=clean_name(rec.get('name',''))
    if len(he)<2: continue
    if rec['src']=='xls':
        mm=re.match(r'(\d{4})$',(rec.get('year') or '').strip()); yh=mm.group(1) if (mm and 1880<=int(mm.group(1))<=2002) else ''
    else:
        t=(rec.get('sheet') or '').strip(); yh=t if (re.fullmatch(r'20[0-2]\d',t) and int(t)<2003) else ''
    if not yh: continue
    gv=canon2(he.split()[0]); fg=canon2(fa[0]) if fa else ''
    if exists(gv,fg): continue
    k=(gv,fg,'h' if ev=='birth' else 'd')
    if k in seen: continue
    seen.add(k)
    sx='F' if 'زوج' in (rec.get('name','') or '') else ''
    new.append({'name':he,'sex':sx,'year':yh,'parent_mid':None,'tag':tag,'is_death':ev=='death',
                'father':rec.get('father',''),'mother':rec.get('mother','')})
    stat['hist' if ev=='birth' else 'death']+=1

# clean prior ev- (master families + integrate modern + stories)
for h in master['houses']: h['families']=[f for f in h['families'] if not f.get('_events')]
for kk in [k for k in stories if str(k).startswith('ev-')]: del stories[kk]
integ['modern']=[x for x in mods if not str(x.get('id','')).startswith('ev-')]

# append as MODERN entries
seq=0; log=[]
for it in sorted(new, key=lambda x:(0 if x['parent_mid'] else 1, x['year'])):
    seq+=1; nid='ev-%d'%seq
    parent = it['parent_mid'] if it['parent_mid'] else ('@H:'+it['tag'])
    integ['modern'].append({'id':nid,'name':it['name'],'sex':('ז' if it['sex']=='M' else 'נ' if it['sex']=='F' else ''),
        'parent':parent,'g':(('–'+it['year']) if it.get('is_death') else it['year']),'byear':(None if it.get('is_death') else int(it['year'])),'dyear':(it['year'] if it.get('is_death') else None),'family':it['tag'],
        'father':it['father'],'mother':it['mother'],'notes':'מתוך סגל המאורעות הסامרי'})
    log.append((it['year'],it['name'],('→ '+mod_by_id[it['parent_mid']]['name']+' ('+it['parent_mid']+')') if it['parent_mid'] else ('בית '+it['tag']),it['father']))

io.open('master_v2.json','w',encoding='utf-8').write(json.dumps(master,ensure_ascii=False,indent=1))
io.open('stories.json','w',encoding='utf-8').write(json.dumps(stories,ensure_ascii=False,indent=1))
io.open('integrate.json','w',encoding='utf-8').write(json.dumps(integ,ensure_ascii=False,indent=1))

ts=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
L=['# לוג שילוב v2 — סגל המאורעות (עם שיוך-אב)','','**תאריך:** '+ts,'**גיבוי:** `backup_*` + `*.bak`.','',
   '## סיכום: %d לידות חדשות'%len(log),'- **משויכות לאב מודרני קיים (חיבור מלא): %d**'%stat['linked'],
   '- ברמת בית-אב (ללא אב ודאי): %d'%stat['house'],'','## פירוט','','| שנה | שם | חיבור | אב (מקור) |','|---|---|---|---|']
for y,nm,conn,fa in log: L.append('| %s | %s | %s | %s |'%(y,nm,conn,fa))
io.open('EVENTS_INTEGRATION_LOG.md','w',encoding='utf-8').write('\n'.join(L))
print('NEW births:',len(log),'| LINKED to a modern father:',stat['linked'],'| house-level:',stat['house'])
print('\nsample LINKED:')
for y,nm,conn,fa in [x for x in log if x[2].startswith('→')][:18]:
    print('  %s %-12s %s'%(y,nm,conn))
