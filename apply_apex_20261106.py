# -*- coding: utf-8 -*-
# 2026-11-06 — "צמרת" (apex) of the Danfim and Marhibim houses, built from the printed family trees (owner's image of the
# apex diagrams): the missing ancestors above the existing family roots are added and the separate trees are hooked under them.
# New people get ids דנ-… / מר-… and live in a new family «צמרת בית אב …» of their house. Idempotent; log in apex_applied_20261106.json
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
H = {h['house']: h for h in master['houses']}
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
LOG = []

# (id, name, father id, note)   — Danfim
DANFIM = [
    ('דנ-אברהם-דמשק', 'אברהם בן ישמעאל בן אברהם (שבא מדמשק)', None, 'שבא מדמשק במחצית הראשונה של המאה ה-17. אבי כל הדנפים.'),
    ('דנ-אבסכוה-א', 'אב-סכוה', 'דנ-אברהם-דמשק', ''),
    ('דנ-ישמעאל-א', 'ישמעאל', 'דנ-אברהם-דמשק', ''),
    ('דנ-עבדהרחום', 'עבד-הרחום', 'דנ-אברהם-דמשק', ''),
    ('דנ-אברהם-א', 'אברהם', 'דנ-אבסכוה-א', ''),
    ('דנ-משלמה', 'משלמה', 'דנ-אבסכוה-א', 'אבי משפחת משלמה (עץ נפרד).'),
    ('דנ-עבדאל', 'עבדאל', 'דנ-אבסכוה-א', 'אבי משפחת עבד-אלה (עץ נפרד).'),
    ('דנ-יעקב', 'יעקב', 'דנ-אבסכוה-א', ''),
    ('דנ-יצחק-א', 'יצחק', 'דנ-אבסכוה-א', ''),
    ('דנ-שלמה-ב', 'שלמה', 'דנ-יעקב', ''),
    ('דנ-אברהם-ב', 'אברהם', 'דנ-יעקב', ''),
    ('דנ-ישמעאל-ב', 'ישמעאל', 'דנ-יעקב', ''),
    ('דנ-יצחק-ב', 'יצחק', 'דנ-יעקב', ''),
    ('דנ-צדקה', 'צדקה = שלבי', 'דנ-יעקב', 'אבי משפחת שלבי (עץ נפרד).'),
    ('דנ-עבדחנונה', 'עבד-חנונה (אללטיף)', 'דנ-יעקב', 'כונה "אללטיף".'),
    ('דנ-יצחק-ג', 'יצחק', 'דנ-עבדחנונה', ''),
    ('דנ-אבסכוה-ב', 'אב-סכוה', 'דנ-עבדחנונה', ''),
    ('דנ-שמעון', 'שמעון', 'דנ-אבסכוה-ב', ''),
    # separate trees hooked under their apex nodes
    ('דנ-אבסכוה-מ', 'אב-סכוה', 'דנ-משלמה', ''),                 # Mishlama tree: משלמה → אב-סכוה → שלח → {אברהם #84, יצחק #95}
    ('דנ-שלח-מ', 'שלח', 'דנ-אבסכוה-מ', ''),
    ('דנ-עבדחנונה-ש', 'עבד-חנונה', 'דנ-צדקה', ''),               # Shalabi tree: צדקה=שלבי → {עבד-חנונה → ישראל #79, יוסף #71}
    ('דנ-אברהם-ג', 'אברהם', 'דנ-ישמעאל-א', ''),                  # ישמעאל → אברהם → {ישמעאל #121, אב-סכוה}
    ('דנ-אבסכוה-ג', 'אב-סכוה', 'דנ-אברהם-ג', ''),
]
DANFIM_LINKS = {'38': 'דנ-אבסכוה-ב', '50': 'דנ-אבסכוה-ב', '84': 'דנ-שלח-מ', '95': 'דנ-שלח-מ', '100': 'דנ-עבדאל', '112': 'דנ-עבדאל',
                '71': 'דנ-צדקה', '79': 'דנ-עבדחנונה-ש', '121': 'דנ-אברהם-ג'}
# Marhibim
MARHIBIM = [
    ('מר-יעקב-אברהם', 'יעקב בן אברהם', None, ''),
    ('מר-אברהם-מ', 'אברהם', 'מר-אב-מרחיב', ''),
    ('מר-אפרים', 'אפרים', 'מר-אב-מרחיב', ''),
    ('מר-ברוך', 'ברוך (שהתאסלם)', 'מר-אב-יעקב', 'התאסלם. אשתו לאה בת סעד הצפרי לא התאסלמה.'),
    ('מר-מרחיב-י', 'מרחיב', '164', ''),
]
MARHIBIM_LINKS = {'מר-אב-מרחיב': 'מר-יעקב-אברהם'}

# Tzafri (צדקה הצפרי)
TZAFRI = [
    ('צפ-אבזהותה', 'אב-זהותה בן יוסף בן אב-זהותה', None, 'אבי משפחת צדקה הצפרי (נכון עד 1909).'),
    ('צפ-שלח', 'שלח', 'צפ-אבזהותה', ''),
    ('צפ-שלמה-א', 'שלמה', 'צפ-אבזהותה', 'אבי משפחת שלמה הצפרי (עץ נפרד).'),
    ('צפ-יוסף', 'יוסף', 'צפ-אבזהותה', ''),
    ('צפ-פריזה', 'פריזה (בת)', '209', ''),
]
TZAFRI_LINKS = {'צפ-ישמעאל': 'צפ-שלח', '247': 'צפ-שלמה-א'}


def build(house_name, fam_name, nodes, links):
    house = H[house_name]
    if any(f['family'] == fam_name for f in house['families']):
        print('already applied:', fam_name); return
    fam = {'family': fam_name, 'family_no': 0, 'ref_code': '', 'persons': []}
    for pid, name, father, note in nodes:
        p = {'id': pid, 'name': name, 'sex': 'F' if pid in ('צפ-פריזה',) else 'M'}
        if father: p['father_id'] = father
        if note: p['note'] = note
        fam['persons'].append(p); P[pid] = p
        LOG.append({'new': pid, 'name': name, 'father': father})
    for p in fam['persons']:                                   # children_ids of the new parents
        if p.get('father_id') and p['father_id'] in P:
            P[p['father_id']].setdefault('children_ids', []).append(p['id'])
    for child, father in links.items():
        c = P[child]
        LOG.append({'link': child, 'name': c.get('name'), 'old_father': c.get('father_id'), 'new_father': father})
        c['father_id'] = father
        ch = P[father].setdefault('children_ids', [])
        if child not in ch: ch.append(child)
    house['families'].insert(0, fam)


build('ב. בית אב הדנפים', 'צמרת בית אב הדנפים', DANFIM, DANFIM_LINKS)
build('ג. בית אב המרחיבים', 'צמרת בית אב המרחיבים', MARHIBIM, MARHIBIM_LINKS)
build('ד. בית אב הצפרים', 'צמרת בית אב הצפרים', TZAFRI, TZAFRI_LINKS)
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('apex_applied_20261106.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(len([l for l in LOG if 'new' in l]), 'new nodes;', len([l for l in LOG if 'link' in l]), 'links')
