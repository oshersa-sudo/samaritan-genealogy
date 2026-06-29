# -*- coding: utf-8 -*-
# Adds MARRIAGE links (spouse cross-connections / dashed lines) between people already in
# the tree, from two sources: (a) birth records' father+mother, (b) the .xlsx groom/bride
# columns. Both spouses must strictly+uniquely match an existing person. Additive only —
# adds a 'spouses' entry; never changes a name/position. DRY unless --apply.
import json, io, re, sys, openpyxl
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
DRY = '--apply' not in sys.argv
exec(open('produce_crosscheck.py', encoding='utf-8').read().split('rows=[]')[0])
master = json.load(io.open('master_v2.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8')); mods = integ.get('modern', []); mod_by_id = {x['id']: x for x in mods}
master_by_id = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
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
GM={'אסחק':'יצחק','אבראהים':'אברהם','אבראהימ':'אברהם','אסמאעיל':'ישמעאל','יעקוב':'יעקב','יוספ':'יוסף','עמראנ':'עמרם','הארונ':'אהרן','אהרונ':'אהרן','צדקו':'צדקה'}
def keyn(w): return norm1(GM.get(w,w))
def gm(a,b): return keyn(a)==keyn(b) or lev(keyn(a),keyn(b))<=1
def fgiven(pid):
    if pid in mod_by_id:
        w=words_he(mod_by_id[pid].get('father','')); return canon2(w[0]) if w else ''
    p=persons.get(pid); fid=p.get('father') if p else None
    if fid and fid in persons:
        w=words_he(persons[fid]['name']); return canon2(w[0]) if w else ''
    return ''
allidx=defaultdict(list)
for pid,p in persons.items():
    w=words_he(p.get('name',''))
    if w: allidx[keyn(w[0])].append(pid)
def match_person(given, fg):
    cands=[pid for pid in allidx.get(keyn(given),[]) if not str(pid).startswith(('שכם','דמשק','קהיר','כ-','ev-')) and (not fg or gm(fg, fgiven(pid)))]
    cands=list(dict.fromkeys(cands))
    return cands[0] if len(cands)==1 else None
def ar(s): return re.sub(r'\s+',' ', ar2he(re.split(r'[(\\/]', s)[0])).strip()
def two(name_he):
    w=[x for x in re.split(r'\s+', name_he) if x]; return (w[0], canon2(w[1]) if len(w)>1 else '') if w else ('','')

pairs={}; src={}
def add_pair(aname, afa, bname, bfa, source):
    ga,_=two(aname); fa_g=canon2(afa.split()[0]) if afa else ''
    gb,_=two(bname); fb_g=canon2(bfa.split()[0]) if bfa else ''
    pa=match_person(ga, fa_g); pb=match_person(gb, fb_g)
    if pa and pb and pa!=pb:
        k=tuple(sorted([pa,pb]))
        if k not in pairs: pairs[k]=(pa,pb); src[k]=source

# (a) birth father+mother
def parsemother(s):
    s=re.sub(r'^\s*(ام|أم|أرملة)\s+','',s); w=words(s); return (' '.join(w[:1]), ' '.join(w[1:2])) if w else ('','')
for rec in events:
    if rec.get('event')!='birth': continue
    mo=rec.get('mother','') or ''
    if not mo or 'أجنبية' in mo or 'اجنبية' in mo or mo.strip().isdigit(): continue
    fa=words(rec.get('father',''));
    if len(fa)<2: continue
    mg=parsemother(mo)
    add_pair(ar(rec.get('father','')), ' '.join(fa[1:2]), ar(mo), mg[1], 'לידה')

# (b) .xlsx groom/bride columns
wx=openpyxl.load_workbook(r'C:\Users\osher\Downloads\سجل المناسبات الجديد.xlsx', read_only=True, data_only=True)
for ws in wx.worksheets:
    rows=list(ws.iter_rows(values_only=True))
    gi=bi=None
    for r in rows[:6]:
        for ci,c in enumerate(r):
            s=str(c or '')
            if 'الزوج' in s and 'ة' not in s: gi=ci
            if 'الزوجة' in s: bi=ci
    if gi is None or bi is None: continue
    for r in rows:
        g=str(r[gi] or '') if gi<len(r) else ''; b=str(r[bi] or '') if bi<len(r) else ''
        if not g or not b or 'أجنبية' in b or 'اسم' in g: continue
        gw=words(g); bw=words(b)
        if len(gw)<2 or len(bw)<2: continue
        add_pair(ar(g), ' '.join(gw[1:2]), ar(b), ' '.join(bw[1:2]), 'נישואין')

print('זוגות-נישואין נקיים (שני בני-הזוג בעץ):', len(pairs))
for k,(a,bp) in list(pairs.items())[:24]:
    print('   %-18s (%s) ⚭ %-18s (%s)  [%s]'%(persons[a]['name'],a,persons[bp]['name'],bp,src[k]))

if not DRY:
    def addspouse(pid, other, oname):
        if pid in mod_by_id:
            x=mod_by_id[pid]; x.setdefault('spouses',[])
            if not any(s.get('ref')==('#'+other if other in master_by_id else other) for s in x['spouses']):
                x['spouses'].append({'name':oname,'ref':(other)})
        elif pid in master_by_id:
            p=master_by_id[pid]; p.setdefault('spouses',[])
            ref = ('#'+other) if other in master_by_id else other
            if not any(s.get('ref')==ref for s in p['spouses']):
                p['spouses'].append({'name':oname,'ref':ref})
    # clear prior auto marriage links (tagged) then add
    for d in (master_by_id, mod_by_id):
        for p in d.values():
            if isinstance(p.get('spouses'),list):
                p['spouses']=[s for s in p['spouses'] if not s.get('_ev')]
    n=0
    for k,(a,bp) in pairs.items():
        addspouse(a, bp, persons[bp]['name']);
        # tag the added ones
        for d,pid,other,oname in [(master_by_id if a in master_by_id else mod_by_id,a,bp,persons[bp]['name'])]:
            sp=(d[pid].get('spouses') or [])
            if sp and sp[-1].get('name')==oname: sp[-1]['_ev']=True
        n+=1
    io.open('master_v2.json','w',encoding='utf-8').write(json.dumps(master,ensure_ascii=False,indent=1))
    io.open('integrate.json','w',encoding='utf-8').write(json.dumps(integ,ensure_ascii=False,indent=1))
    print('APPLIED', n, 'marriage links.')
else:
    print('\n(הרצת-יבש — להחלה: --apply)')
