# -*- coding: utf-8 -*-
# 2026-11-06 — «שם האם» for every card.  Only what the sources state (nothing guessed):
#   1. the independent reading of the article pages (scan_read: "mother" of a numbered entry, checked against the father's number);
#   2. the father's spouses: explicit notes («אם ילדים א-ג», «אם הבן השני», …), a hand map for the few irregular notes,
#      or the ONLY spouse who is not marked childless;
#   3. the community registry (Excel) layer: its own «mother» column, matched to the father's spouse when possible.
# Output fields on each person: mother_id (a person on the site → linkable), mother (text «שם בת אב»), mother_house (when she is not on the site),
#   mother_src (why).  Idempotent (re-derives everything; never overwrites a value the owner typed in the admin UI — those live in the cloud overrides).
# Log + coverage: mothers_derived_20261106.json
import json, io, re, sys, glob, collections
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
integ = json.load(io.open('integrate.json', encoding='utf-8'))
SCAN = r'C:\Users\osher\Documents\torah\data\genealogy_audit\scan_read'
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
HOUSE_OF = {p['id']: h['house'] for h in master['houses'] for f in h['families'] for p in f['persons']}
NIQ = ''.join(chr(c) for c in range(0x0591, 0x05C8))
FIN = str.maketrans('ךםןףץ', 'כמנפצ')


def n(s):
    s = ''.join(ch for ch in str(s or '') if ch not in NIQ)
    s = re.sub(r"[׳״\"'`\.,/\\\-=()\[\]]", ' ', s)
    return re.sub(r'\s+', ' ', s).strip().translate(FIN)


def given(s):
    s = re.sub(r'\s*[\(（].*$', '', str(s or '')).split(' בת ')[0].split(' בן ')[0]
    s = re.sub(r'\s*=.*$', '', s)
    return s.strip()


ALIAS = {'אסעד': 'סעד'}


def key(s):
    k = n(given(s))
    return ALIAS.get(k, k)


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def same(a, b):
    ka, kb = key(a), key(b)
    if not ka or not kb: return False
    if ka == kb: return True
    return min(len(ka), len(kb)) >= 4 and lev(ka, kb) <= 1


def resolve_id(raw):
    raw = str(raw or '').strip(); best = None
    for i in range(1, len(raw) + 1):
        if raw[:i] in P: best = raw[:i]
    return best


def sp_target(sp):
    for f in (sp.get('note'), sp.get('birth'), sp.get('death')):
        if isinstance(f, str):
            m = re.search(r"#\s*([0-9][0-9א-ת׳']*)", f) or re.search(r'#\s*([א-ת][א-ת0-9\-]*)', f)
            if m:
                t = resolve_id(m.group(1))
                if t: return t
    if isinstance(sp.get('ref'), str):
        t = resolve_id(sp['ref'])
        dr = re.match(r'\d+', sp['ref'].strip())
        di = re.match(r'\d+', t or '')
        if t and (not dr or (di and di.group(0) == dr.group(0))):        # a shorter number inside a longer printed number is NOT a match
            return t
    return None


# house letters of the printed spouse reference (validated below against spouses that resolve to a person)
def house_from_ref(ref):
    r = re.sub(r'^[\d\s]+', '', str(ref or ''))
    if re.match(r"^צ", r): return 'ד. בית אב הצפרים'
    if re.match(r"^מי", r): return 'ג. בית אב המרחיבים'
    if re.match(r"^(ד|אד)", r): return 'ב. בית אב הדנפים'
    if re.match(r"^כ", r): return 'ו. בית אב הכהונה'
    return None


bad = tot = 0
for p in P.values():
    for sp in p.get('spouses') or []:
        t = sp_target(sp); h = house_from_ref(sp.get('ref'))
        if t and h:
            tot += 1
            if HOUSE_OF[t] != h: bad += 1
print('house-from-ref check: %d of %d agree' % (tot - bad, tot))
HOUSE_REF_OK = bad <= max(2, tot // 20)

# ---------------------------------------------------------------- article readings
ART = {}
for fn in sorted(glob.glob(SCAN + r'\p*.json')):
    d = json.load(io.open(fn, encoding='utf-8'))
    for e in d['entries']:
        pid = str(e.get('printed_id') or '')
        if pid and e.get('mother') and pid in P:
            m = re.search(r'\((\d+[א-ת]?)\)', e.get('father') or '')
            if m and P[pid].get('father_id') and m.group(1) != P[pid]['father_id']:
                continue                                         # the reading's father number disagrees with the site → not trusted
            ART.setdefault(pid, (e['mother'], d['page']))

# ---------------------------------------------------------------- hand map for irregular notes: child id -> spouse index
HAND = {'51': 1, '57': 0, '66': 0, '70': 0,                       # #50: «אם יוסף» (first wife), «ילדיו 2-4 ממנה» (נשוה)
        '86': 0, '87': 1,                                         # #85: «ורדה — אם הבן השני»
        '90': 0, '91': 1, '92': 1, '93': 1,                       # #89: «אם הבן הראשון» / «אם שלושת הילדים הבאים»
        '122': 0, '135': 0, '150': 0, '149': 0, '161': 0, '162': 1,   # #121: the two wives of the printed tree
        '203': 0, '205': 0, '206': 0, '207': 1, '208': 1,   # #202: אל פלוה → אברהם, זוהרה, יעקב; סעוד → ברוך, סעד (תרשים עמ׳ 91)
        '240': 0, '242': 1, '247': 1,                                  # #239: אספהאן → בנימים; נשווה → אריה, סעד (תרשים עמ׳ 97)
        'צפ-אלקנה247': 0, '248': 0, '249': 0,                          # #247: מברוכה (#132) → אלקנה, נביהה, חוסון
        '215': 0, '217': 0, '218': 0, '219': 0, '220': 0, '221': 0, '222': 0, '223': 0,   # #214: קמרה (#160); סלוח ללא ילדים
        'צפ-אבזהותה211': 0, '212': 1,                                  # #211: ניגמה → אב-זהותה; בהיה → סוריה
        '166': 0, '172': 0, '175': 0, '177': 0, '178': 1,              # #165: אשה ראשונה → א-ד; לטיפה → ניגמה
        '201': 2,                                                      # #200: עריפה → מרחיב
        '225': 1, '226': 1, '227': 1,                                  # #224: מרים (ללא ילדים) / הדיה בת יצחק → יוסף, עובדיה, יוכבד
        '170': 0, '171': 0,                                            # #166: שמסה (#94) → שת, סעוד, יצחק
        '75א': 0, 'ר-שלביה': 1,                                        # #75: מסעודה (#124); מלכה — נישואים אחרי 1909
        '211': 0, '213': 0, '214': 1, '224': 1,                   # #210: «אם ילדים א-ב / ג-ד»
        '73': 0, '74': 0, '75': 0, '76': 0, '77': 0, '78': 0, 'דנ-שלביה72': 0,   # #72: שמסה (#130) — היא הראשונה; זוהרה (#81) נישאה לו קודם אך אינה אם ילדיו
        'הס-יוסף122': 0, '123': 0, '130': 0, '131': 0, '132': 1, '133': 1, '134': 1}   # #122: «אם ילדים א-ג / ד-ו»
HAND_FATHER = {'50', '85', '89', '121', '122', '202', '210', '239', '247', '214', '211', '165', '200', '224', '166', '75', '72'}
CHILDLESS = re.compile(r'ללא ילדים|לא ילדה')

LOG = []
cov = collections.Counter()


def from_spouse(sp, src):
    t = sp_target(sp)
    if t and P[t].get('sex') != 'M':
        return {'mother_id': t, 'mother_src': src}
    name = sp['name']
    if re.match(r'^אשה( שנייה)? שלא נודעה בשמה', name):
        return {'mother': 'אשה שלא נודעה בשמה (' + ('אשתו הראשונה' if 'שנייה' not in name else 'אשתו השנייה') + ' של ישמעאל)', 'mother_src': src}
    out = {'mother': re.sub(r'\s*\[.*?\]', '', name).strip(), 'mother_src': src}
    h = house_from_ref(sp.get('ref')) if HOUSE_REF_OK else None
    if h: out['mother_house'] = h
    return out


for pid, p in P.items():
    for k in ('mother_id', 'mother', 'mother_house', 'mother_src'): p.pop(k, None)
    fid = p.get('father_id')
    if not fid or fid not in P: cov['no father on site'] += 1; continue
    F = P[fid]; sps = F.get('spouses') or []
    res = None
    if F.get('sex') == 'F':                                  # the registered parent is a woman: she IS the mother (the father is not on the site)
        res = {'mother_id': fid, 'mother_src': 'האם היא ההורה הרשום (האב אינו באתר)'}
        p.update(res); cov['mother set'] += 1; cov['by woman parent'] += 1
        LOG.append({'id': pid, 'name': p['name'], **res}); continue
    # 1. article reading
    if pid in ART:
        mt, page = ART[pid]
        hit = next((s for s in sps if same(mt, s['name'])), None)
        if hit: res = from_spouse(hit, 'המאמר, עמ׳ %d (ופרטי האם מרשומת האב)' % (page + 72))
        else:
            w = [q for q in P.values() if q.get('sex') == 'F' and same(mt, q['name']) and any(sp_target(s) == fid for s in q.get('spouses') or [])]
            if len(w) == 1: res = {'mother_id': w[0]['id'], 'mother_src': 'המאמר, עמ׳ %d' % (page + 72)}
            else: res = {'mother': mt.strip(), 'mother_src': 'המאמר, עמ׳ %d' % (page + 72)}
    # 1b. a hand-mapped child whose article reading is only a name: take the father's spouse record (it carries the link)
    if res is not None and 'mother_id' not in res and pid in HAND and fid in HAND_FATHER and sps and HAND[pid] < len(sps):
        r2 = from_spouse(sps[HAND[pid]], 'הערת האשה אצל האב במפקד')
        if 'mother_id' in r2: res = r2
    # 2. father's spouses
    if res is None and sps:
        if pid in HAND and fid in HAND_FATHER:
            res = from_spouse(sps[HAND[pid]], 'הערת האשה אצל האב במפקד')
        else:
            cand = [s for s in sps if not CHILDLESS.search(s.get('note') or '')]
            if len(cand) == 1: res = from_spouse(cand[0], 'האשה היחידה של האב שלא סומנה כחסרת ילדים')
    if res:
        p.update(res); cov['mother set'] += 1; cov['by ' + res['mother_src'][:20]] += 1
        LOG.append({'id': pid, 'name': p['name'], **res})
    else:
        cov['unknown'] += 1

# ---------------------------------------------------------------- registry (Excel) layer
for m in integ['modern']:
    for k in ('mother_id', 'mother_house', 'mother_src'): m.pop(k, None)
    mt = (m.get('mother') or '').strip()
    par = m.get('parent') or ''
    fid = par[1:] if par.startswith('#') else par
    F = P.get(fid)
    if not mt: cov['modern: no mother'] += 1; continue
    sps = (F.get('spouses') if F else None) or []
    hit = next((s for s in sps if same(mt, s['name'])), None)
    if hit:
        r = from_spouse(hit, 'מרשם הקהילה; פרטי האם מרשומת האב')
        if 'mother_id' in r: m['mother_id'] = r['mother_id']
        elif r.get('mother'): m['mother'] = r['mother']; m['mother_house'] = r.get('mother_house', '')
        if not m.get('mother_house'): m.pop('mother_house', None)
        m['mother_src'] = r['mother_src']; cov['modern: matched father spouse'] += 1
    else:
        m['mother_src'] = 'מרשם הקהילה (עמודת האם)'; cov['modern: text only'] += 1
    LOG.append({'id': m['id'], 'name': m['name'], 'mother': m.get('mother'), 'mother_id': m.get('mother_id'), 'src': m['mother_src']})

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('integrate.json', 'w', encoding='utf-8').write(json.dumps(integ, ensure_ascii=False, indent=1))
io.open('mothers_derived_20261106.json', 'w', encoding='utf-8').write(json.dumps({'coverage': cov, 'rows': LOG}, ensure_ascii=False, indent=1))
print(dict(cov))
