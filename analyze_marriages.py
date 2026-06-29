# -*- coding: utf-8 -*-
import json, io, re, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
exec(open('produce_crosscheck.py', encoding='utf-8').read().split('rows=[]')[0])
integ = json.load(io.open('integrate.json', encoding='utf-8')); mods = integ.get('modern', []); mod_by_id = {x['id']: x for x in mods}
NIQ = ''.join(chr(c) for c in range(0x0591, 0x05C8)); FIN = {'ם':'מ','ן':'נ','ץ':'צ','ף':'פ','ך':'כ'}
def norm1(w): w = ''.join(FIN.get(c, c) for c in re.sub('['+NIQ+']', '', w)); return w.replace('ש', 'ס').replace("'", '')
def lev(a, b):
    if a == b: return 0
    if abs(len(a)-len(b)) > 2: return 9
    d = list(range(len(b)+1))
    for i, ca in enumerate(a, 1):
        p = d[0]; d[0] = i
        for j, cb in enumerate(b, 1):
            t = d[j]; d[j] = min(d[j]+1, d[j-1]+1, p+(ca != cb)); p = t
    return d[-1]
GM = {'אסחק':'יצחק','אבראהים':'אברהם','אבראהימ':'אברהם','אסמאעיל':'ישמעאל','יעקוב':'יעקב','יוספ':'יוסף','עמראנ':'עמרם','הארונ':'אהרן','אהרונ':'אהרן','צדקו':'צדקה'}
def keyn(w): return norm1(GM.get(w, w))
def gm(a, b): return keyn(a) == keyn(b) or lev(keyn(a), keyn(b)) <= 1
def fgiven(pid):
    if pid in mod_by_id:
        w = words_he(mod_by_id[pid].get('father', '')); return canon2(w[0]) if w else ''
    p = persons.get(pid); fid = p.get('father') if p else None
    if fid and fid in persons:
        w = words_he(persons[fid]['name']); return canon2(w[0]) if w else ''
    return ''
def sexof(pid):
    if pid in mod_by_id: return (mod_by_id[pid].get('sex', '') or '')[:1]
    return (persons.get(pid) or {}).get('sex', '')
allidx = defaultdict(list)
for pid, p in persons.items():
    w = words_he(p.get('name', ''))
    if w: allidx[keyn(w[0])].append(pid)
def match_person(given, father_given, want_female=False):
    cands = []
    for pid in allidx.get(keyn(given), []):
        if str(pid).startswith(('שכם', 'דמשק', 'קהיר', 'כ-', 'ev-')): continue
        if father_given and not gm(father_given, fgiven(pid)): continue
        if want_female and sexof(pid) not in ('F', 'נ', ''): continue
        cands.append(pid)
    cands = list(dict.fromkeys(cands))
    return cands[0] if len(cands) == 1 else None
def parsemother(s):
    s = re.sub(r'^\s*(ام|أم|أرملة)\s+', '', s)
    w = words(s); return (w[0], w[1] if len(w) > 1 else None) if w else ('', None)
pairs = {}; samp = []
for rec in events:
    if rec.get('event') != 'birth': continue
    mo = rec.get('mother', '') or ''
    if not mo or 'أجنبية' in mo or 'اجنبية' in mo or mo.strip().isdigit(): continue
    fa = words(rec.get('father', ''))
    if len(fa) < 2: continue
    fpid = match_person(fa[0], fa[1])
    mg, mgf = parsemother(mo)
    if not mg: continue
    mpid = match_person(mg, mgf, True)
    if fpid and mpid and fpid != mpid:
        key = tuple(sorted([fpid, mpid]))
        if key in pairs: continue
        pairs[key] = (fpid, mpid)
        if len(samp) < 18: samp.append((persons[fpid]['name'], fpid, persons[mpid]['name'], mpid))
print('זוגות-נישואין ששני בני-הזוג כבר בעץ (משמות אב+אם בלידות):', len(pairs))
for fn, fp, mn, mp in samp:
    print('   %-18s (%s)  ⚭  %-18s (%s)' % (fn, fp, mn, mp))
print()
print('רשומות-נישואין ייעודיות:', len([r for r in events if r.get('event') == 'marriage']))
