# -*- coding: utf-8 -*-
# Integrates ONLY genuinely-NEW modern births (2003-2026) from the events registry, as a
# clearly-labelled "events registry" family under each house — at HOUSE level, with NO
# guessed specific father (honest). Does NOT touch any existing person/name/position.
# Writes a changelog (EVENTS_INTEGRATION_LOG.md). Idempotent (removes prior ev- additions).
import json, io, re, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
exec(open('produce_crosscheck.py', encoding='utf-8').read().split('rows=[]')[0])  # helpers + persons
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))

FAM2H = {'צדקה':'ד. בית אב הצפרים','צדקו':'ד. בית אב הצפרים','אלטיפ':'ב. בית אב הדנפים','אלטיף':'ב. בית אב הדנפים',
 'סראוי':'ב. בית אב הדנפים','אלסראוי':'ב. בית אב הדנפים','מרגאנ':'ג. בית אב המרחיבים','מרחיב':'ג. בית אב המרחיבים','דנפי':'ב. בית אב הדנפים'}

# existing (newborn-given, father-given) pairs across the whole tree — to skip anyone already present
exist = set()
def fgiven(p):
    fid=p.get('father')
    if fid and fid in persons:
        w=words_he(persons[fid]['name']); return canon2(w[0]) if w else ''
    if p.get('fatherName'):
        w=words_he(p['fatherName']); return canon2(w[0]) if w else ''
    return ''
for pid,p in persons.items():
    g=[canon2(w) for w in words_he(p['name'])]
    if g: exist.add((g[0], fgiven(p)))

# collect the new births
new = {}
seen = set()
for rec in events:
    if rec.get('src')!='xlsx' or rec.get('event')!='birth': continue
    t=(rec.get('sheet') or '').strip()
    if not re.fullmatch(r'20[0-2]\d', t) or int(t)<2003: continue
    nm=re.split(r'[(\\/]', rec.get('name',''))[0]
    he=re.sub(r'\s+',' ', ar2he(nm)).strip()
    if len(he)<2: continue
    fa=words(rec.get('father',''))
    house=''
    for w in fa[::-1]:
        if w in FAM2H: house=FAM2H[w]; break
    if not house: continue
    key=(canon2(he.split()[0]), canon2(fa[0]) if fa else '')
    if key in exist or key in seen: continue
    seen.add(key)
    sx = 'F' if 'أنثى' in (rec.get('sex','') or '') else ('M' if 'ذكر' in (rec.get('sex','') or '') else '')
    new.setdefault(house, []).append({'year':t,'name':he,'sex':sx,'father':rec.get('father',''),'mother':rec.get('mother','')})

# remove any previous ev- integration (idempotent)
for h in master['houses']:
    h['families'] = [f for f in h['families'] if not f.get('_events')]
for k in [k for k in stories if str(k).startswith('ev-')]: del stories[k]

seq=0; log=[]
for h in master['houses']:
    items = new.get(h['house'])
    if not items: continue
    items.sort(key=lambda x:x['year'])
    rootid='ev-root-'+re.sub(r'\W','',h['house'])[:4]
    kids=[]
    for it in items:
        seq+=1; nid='ev-%d'%seq
        p={'id':nid,'name':it['name']}
        if it['sex']: p['sex']=it['sex']
        p['father_id']=rootid
        kids.append(p)
        note='מתוך סגל המאורעות הסامרי (מרשם הקהילה). אב: '+it['father']+(' · אם: '+it['mother'] if it['mother'] else '')
        stories[nid]={'t':note,'g':it['year']}
        log.append((h['house'], it['year'], it['name'], it['sex'] or '?', it['father'], it['mother']))
    root={'id':rootid,'name':'📋 לידות מהמרשם 2003–2026 (סגל המאורעות)','sex':'',
          'note':'אנשים חדשים מהמרשם הרשמי שטרם שולבו לפי אב ספציפי — מקובצים ברמת בית-האב.','children_ids':[k['id'] for k in kids]}
    fam={'family_no':99,'family':'מרשם המאורעות — לידות 2003–2026','ref_code':'אירועים','_events':True,
         'source_note':'חולץ משני קבצי "سجل المناسبات" (סגל המאורעות הסامרי). שולבו רק לידות חדשות (אחרי 2002) עם בית-אב ברור, ללא ניחוש אב ספציפי וללא שינוי אנשים קיימים.',
         'persons':[root]+kids}
    h['families'].append(fam)

io.open('master_v2.json','w',encoding='utf-8').write(json.dumps(master,ensure_ascii=False,indent=1))
io.open('stories.json','w',encoding='utf-8').write(json.dumps(stories,ensure_ascii=False,indent=1))

# changelog
ts=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
L=['# לוג שילוב — לידות מהמרשם (סגל המאורעות)','',
   '**תאריך:** '+ts,'**גיבוי לשחזור:** תיקיית `backup_*` + הקבצים `master_v2.json.bak`, `stories.json.bak`.','',
   '## מה שולב','- **רק לידות חדשות (2003–2026)** מתוך שני קבצי האקסל, שאינן קיימות בעץ.',
   '- שולבו **ברמת בית-האב** תחת משפחה חדשה "מרשם המאורעות", מקובצות תחת צומת-תווית — **בלי לנחש אב ספציפי**.',
   '- **לא שונו** שמות, מיקומים או פרטים של אף אדם קיים.','',
   '## מה לא שולב (במכוון)','- לידות היסטוריות, פטירות, נישואין — דורשים שיוך-אדם שאינו ודאי דיו.',
   '- כל שיוך-אב ספציפי — התעתיק ערבית→עברית + שמות נפוצים אינם מאפשרים ודאות.','',
   '## סיכום: %d אנשים נוספו'%len(log),'']
from collections import Counter
for hs,c in Counter(x[0] for x in log).items(): L.append('- %s: %d'%(hs,c))
L+=['','## פירוט מלא','','| בית-אב | שנה | שם (עברית) | מין | אב (מקור) | אם (מקור) |','|---|---|---|---|---|---|']
for hs,y,nm,sx,fa,mo in log:
    L.append('| %s | %s | %s | %s | %s | %s |'%(hs.split('בית אב ')[-1],y,nm,sx,fa,mo))
io.open('EVENTS_INTEGRATION_LOG.md','w',encoding='utf-8').write('\n'.join(L))
print('ADDED', len(log), 'new people across', len(set(x[0] for x in log)), 'houses')
print('changelog: EVENTS_INTEGRATION_LOG.md')
