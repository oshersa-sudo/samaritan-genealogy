# -*- coding: utf-8 -*-
# READ-ONLY cross-check: transliterate the Arabic event names to Hebrew and try to
# match each record's FATHER (and newborn) against the existing tree. Reports quality
# only — writes nothing to the tree.
import json, io, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

events = json.load(io.open('events_extracted.json', encoding='utf-8'))
master = json.load(io.open('master_v2.json', encoding='utf-8'))
try: integ = json.load(io.open('integrate.json', encoding='utf-8'))
except Exception: integ = {'modern': []}
mods = integ.get('modern', []) if isinstance(integ, dict) else integ

# ---------- Arabic -> Hebrew ----------
AR2HE = {'ا':'א','أ':'א','إ':'א','آ':'א','ء':'','ب':'ב','ت':'ת','ث':'ת','ج':'ג','ح':'ח','خ':'כ',
 'د':'ד','ذ':'ז','ر':'ר','ز':'ז','س':'ס','ش':'ש','ص':'צ','ض':'צ','ط':'ט','ظ':'ט','ع':'ע','غ':'ע',
 'ف':'פ','ق':'ק','ك':'כ','ل':'ל','م':'מ','ن':'נ','ه':'ה','و':'ו','ي':'י','ى':'י','ة':'ה','ؤ':'ו','ئ':'י','ﻻ':'לא'}
def ar2he(s):
    return ''.join(AR2HE.get(ch, ch if ch.strip() else ' ') for ch in s)

# canonical given-name map (Arabic form / translit -> Hebrew canonical) for common Samaritan names
GIVEN = {
 'עמראנ':'עמרם','אסחק':'יצחק','אבראהימ':'אברהם','אבראהים':'אברהם','אסמאעיל':'ישמעאל','יעקוב':'יעקב',
 'יוספ':'יוסף','יפת':'יפת','צדקה':'צדקה','צדקו':'צדקה','פרג':'מרחיב','לטפי':'לוטפי','חסני':'חסן',
 'ואצפ':'אשר','חביב':'חביב','שלמה':'שלמה','שלח':'שלח','אהרונ':'אהרן','הארונ':'אהרן','פינחאס':'פינחס',
 'מצליח':'מצליח','אבישע':'אבישע','טוביה':'טוביה','עזי':'עזי','נתנאל':'נתנאל','אלעזר':'אלעזר',
 'אבסלאמה':'אבסלאמה','עבדאללה':'עבד-אלה','עבדאללטיפ':'עבד-אלה','חנונה':'עבד-חנונה'}
FAM = {'צדקה':'צפרים/כהונה','אלטיפ':'דנפים','אלטיף':'דנפים','אלטיו':'דנפים','סראוי':'דנפים','אלסראוי':'דנפים',
 'מרגאנ':'מרחיבים','מרחיב':'מרחיבים','דנפי':'דנפים','כהנ':'כהונה'}

def words(s):
    s = ar2he(s)
    s = re.sub(r'[()\[\]/_.,،؛]',' ', s)
    return [w for w in s.split() if w and w not in ('בנ','בן','אבו','אל','אלכאהנ','כאהנ')]
NIQ = ''.join(chr(c) for c in range(0x0591,0x05C8)); FIN={'ם':'מ','ן':'נ','ץ':'צ','ף':'פ','ך':'כ'}
def loose(w):
    w = ''.join(FIN.get(c,c) for c in re.sub('['+NIQ+']','',w))
    return w.replace('ו','').replace('י','').replace('א','').replace('ה','').replace('ע','').replace("'",'')
def canon(w):
    return loose(GIVEN.get(w, w))

def evt_chain(rec):
    """return (newborn_loose, [father-chain loose words], family_tag)"""
    nb = words(rec.get('name',''))
    fa = words(rec.get('father',''))
    famtag = ''
    for w in fa[::-1]:
        if w in FAM: famtag = FAM[w]; break
    nbc = canon(nb[0]) if nb else ''
    fac = [canon(w) for w in fa]
    return nbc, fac, famtag

# ---------- tree lookup ----------
persons = {}
for h in master['houses']:
    for f in h['families']:
        for p in f['persons']:
            persons[p['id']] = {'name':p.get('name',''),'house':h['house'],'father':p.get('father_id')}
for m in mods:
    persons[m['id']] = {'name':m.get('name',''),'house':'(מרשם)','father':m.get('parent'),'fatherName':m.get('father','')}

def name_tokens(nm):
    return set(canon(w) for w in words_he(nm))
def words_he(nm):
    nm = re.sub(r'[()\[\]/_.,=]',' ', nm or '')
    return [w for w in nm.split() if w and w not in ('בן','בת','אבו')]

# index: loose-given -> list of person ids
by_given = {}
for pid,p in persons.items():
    toks = [canon(w) for w in words_he(p['name'])]
    for t in set(toks):
        by_given.setdefault(t, []).append(pid)

def father_given_loose(pid):
    p = persons.get(pid);
    if not p: return None
    fid = p.get('father')
    if fid and fid in persons:
        ws = words_he(persons[fid]['name']); return canon(ws[0]) if ws else None
    fn = p.get('fatherName')
    if fn: ws = words_he(fn); return canon(ws[0]) if ws else None
    return None

# ---------- match each event's FATHER to a tree person ----------
res = Counter(); samples_hit=[]; samples_miss=[]
for rec in events:
    if rec.get('event')!='birth': continue
    nbc, fac, famtag = evt_chain(rec)
    if len(fac)<1: res['no-father']+=1; continue
    fg = fac[0]                     # father's given
    fgf = fac[1] if len(fac)>1 else None   # father's father given
    cands = by_given.get(fg, [])
    # disambiguate by the father's-father name
    good = []
    for pid in cands:
        if fgf:
            fgl = father_given_loose(pid)
            if fgl and (fgl==fgf or fgf in fgl or fgl in fgf): good.append(pid)
        else:
            good.append(pid)
    if good:
        res['father-matched']+=1
        if len(samples_hit)<14:
            samples_hit.append((rec.get('year'),rec.get('name'),rec.get('father'),good[0],persons[good[0]]['name']))
    elif cands:
        res['father-given-only']+=1   # given matches but father-of-father doesn't (ambiguous)
    else:
        res['father-no-match']+=1
        if len(samples_miss)<12:
            samples_miss.append((rec.get('year'),rec.get('name'),rec.get('father')))

print('=== BIRTH records: father cross-match vs tree ===')
print(dict(res))
tot = sum(res.values())
mt = res['father-matched']
print('father uniquely matched: %d / %d  (%.0f%%)'%(mt,tot,100*mt/max(1,tot)))
print('father given-name found (needs disambiguation): %d'%res['father-given-only'])
print()
print('--- sample MATCHED (event father -> tree person) ---')
for y,n,f,pid,pn in samples_hit:
    print('  %-6s %-14s אב=%-30s →  %s (%s)'%(y,n,f,pn,pid))
print('--- sample NOT matched ---')
for y,n,f in samples_miss:
    print('  %-6s %-14s אב=%s'%(y,n,f))
