# -*- coding: utf-8 -*-
# Integrates ONLY the high-confidence, unambiguous, genuinely-NEW births from the event
# registries into the tree, as children of their confidently-matched father.
# Skips anything uncertain: only confidence=='high' (grandfather AND house match, no tie),
# only when the father has no existing child of the same (loose) name (no duplicates),
# only with a clean name + plausible birth year. DRY=1 prints what it WOULD add.
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
DRY = '--apply' not in sys.argv

exec(open('produce_crosscheck.py', encoding='utf-8').read().split('rows=[]')[0])  # loaders, helpers, best_match
# exclude the ANCIENT priestly chains (כ-/שכם/דמשק/קהיר) from the match pool — their many
# common names (יצחק/יוסף/לוי/צדקה...) are false-match magnets for modern Arabic names.
SPINE_EXCL = ('כ-','שכם','דמשק','קהיר')
for _k in list(by_given2.keys()):
    by_given2[_k] = set(p for p in by_given2[_k] if not str(p).startswith(SPINE_EXCL))
    if not by_given2[_k]: del by_given2[_k]
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
fam_of = {}; node = {}
for h in master['houses']:
    for f in h['families']:
        for p in f['persons']:
            node[p['id']] = p; fam_of[p['id']] = f
# existing children names per parent (loose) — from census + modern
kids_loose = {}
def add_kid(par, nm):
    kids_loose.setdefault(par, set()).add(loose2(nm))
for h in master['houses']:
    for f in h['families']:
        for p in f['persons']:
            if p.get('father_id'): add_kid(p['father_id'], (p.get('name') or '').split()[0] if p.get('name') else '')
for x in mods:
    par = x.get('parent','');  par = par[1:] if par.startswith('#') else par
    add_kid(par, (x.get('name') or '').split()[0] if x.get('name') else '')

def clean_name(ar):
    ar = re.split(r'[(\\/]', ar)[0]                 # drop "(زوجة ...)" / "\..." annotations
    he = re.sub(r'\s+',' ', ar2he(ar)).strip()
    return he
def birth_year(rec):
    # ONLY a reliable single-year source: the .xls year column, or an .xlsx sheet whose
    # title is exactly one 4-digit year. Multi-year sheets (e.g. '20111') -> no year.
    if rec.get('src') == 'xlsx':
        t = (rec.get('sheet') or '').strip()
        m = re.fullmatch(r'(20[0-2]\d)', t)
        return m.group(1) if m else ''
    y = (rec.get('year') or '').strip()
    m = re.match(r'(\d{4})$', y)
    return m.group(1) if (m and 1880 <= int(m.group(1)) <= 2030) else ''

def is_male_person(pid):
    p = persons.get(pid) or {}
    nm = p.get('name','')
    sx = (node.get(pid) or {}).get('sex')
    if sx == 'F': return False
    if any(w in nm for w in ('בַּדְרָיָה','שמסה','עיזואת','גֿמילה','ודיעה','זהרה')): return False
    return True
def approx_birth(pid):
    g = (stories.get(pid,{}) or {}).get('g','')
    m = re.match(r'(\d{3,4})', g or '')
    if m: return int(m.group(1))
    b = (node.get(pid) or {}).get('birth')
    if isinstance(b,int): return b + 584             # census Hijri -> Gregorian
    for x in mods:
        if x['id']==pid:
            return x.get('byear')
    return None
def age_ok(pid, child_year):
    fy = approx_birth(pid)
    if fy is None or not child_year: return False    # require a known father age (certainty!)
    return 15 <= (int(child_year) - fy) <= 62

added = []; skip = {'exists':0,'name':0,'year':0,'female_father':0,'dup':0}
seq = 0
seen = set()
for rec in events:
    if rec.get('event') != 'birth': continue
    pid, conf, famtag = best_match(rec)
    if conf != 'high' or not pid: continue           # ONLY rock-solid, unambiguous
    if not is_male_person(pid): skip['female_father']+=1; continue   # no female "fathers"
    nm = clean_name(rec.get('name',''))
    if len(nm) < 2: skip['name']+=1; continue
    key = (loose2(nm.split()[0]), pid)               # dedupe same child across year-sheets
    if key in seen: skip['dup']+=1; continue
    if loose2(nm.split()[0]) in kids_loose.get(pid, set()): skip['exists']+=1; continue  # already a child
    by = birth_year(rec)
    if not by: skip['year']+=1; continue
    if int(by) < 2003: skip.setdefault('historical',0); skip['historical']+=1; continue  # only genuinely-new (beyond my 2002 data)
    if not age_ok(pid, by): skip.setdefault('age',0); skip['age']+=1; continue            # father must be plausibly aged
    seen.add(key)
    sex = 'F' if ('أنثى' in (rec.get('sex','') or '') or 'زوجة' in (rec.get('name','') or '')) else ('M' if 'ذكر' in (rec.get('sex','') or '') else '')
    seq += 1; nid = 'ev-%d' % seq
    note = 'מתוך סגל המאורעות הסامרי (' + rec.get('src','') + '). אב: ' + rec.get('father','') + (' · אם: '+rec.get('mother','') if rec.get('mother') else '')
    added.append({'id':nid,'name':nm,'sex':sex,'father':pid,'g':by,'note':note,
                  'ar':rec.get('name',''),'arfa':rec.get('father',''),'fatherNm':node[pid]['name'] if pid in node else persons[pid]['name']})

print('HIGH-confidence NEW births to add:', len(added))
print('skipped:', skip, '(exists=כבר ילד של האב; name/year=לא תקין)')
from collections import Counter
print('by source:', dict(Counter(rec_src for rec_src in [a['ar'] and ('xlsx' if a['id'] else '') for a in []])))
print()
print('=== preview (all) ===')
for a in added:
    print('  +%-14s (%s,%s) → אב: %s [%s]   | מקור: %s בن %s'%(a['name'],a['g'],a['sex'] or '?',a['fatherNm'],a['father'],a['ar'][:18],a['arfa'][:22]))

if DRY:
    print('\n(הרצת-יבש — לא נכתב כלום. להחלה: py -3 add_events.py --apply)')
else:
    for a in added:
        fid = a['father']; fam = fam_of.get(fid)
        if not fam: continue
        p = {'id':a['id'],'name':a['name'],'father_id':fid}
        if a['sex']: p['sex']=a['sex']
        node[fid].setdefault('children_ids',[]).append(a['id'])
        fam['persons'].append(p); node[a['id']]=p
        stories[a['id']] = {'t':a['note'],'g':a['g']}
    io.open('master_v2.json','w',encoding='utf-8').write(json.dumps(master,ensure_ascii=False,indent=1))
    io.open('stories.json','w',encoding='utf-8').write(json.dumps(stories,ensure_ascii=False,indent=1))
    print('\nAPPLIED:', len(added), 'new people added to master_v2.json + stories.json')
