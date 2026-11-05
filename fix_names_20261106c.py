# -*- coding: utf-8 -*-
# 2026-11-06 (c) — owner's naming decisions:
#  * #70 «זינאב = פצנה» → «זינאב = הצולעת» (the printed «אלערגיה» = the lame one; #80's story already calls her «הצולעת»)
#  * #133 Tamim: «כאמל» is the Arabic equivalent of «תמים» → shown «תמים = כאמל» (as #69)
#  * «מורג'אן» is the Arabic name of «אב-סכוה» (the apex Abu-Sakua, grandfather of Abraham «אלעיה») → shown on that node and in Abraham's card
#  * «אסעד» = «סעד» in most cases (noted for matching; nothing is merged automatically). Idempotent.
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
LOG = []


def setname(pid, old, new):
    if P[pid]['name'] == old:
        P[pid]['name'] = new; LOG.append((pid, old, new))
    elif P[pid]['name'] != new:
        LOG.append((pid, 'SKIP', P[pid]['name']))


setname('70', 'זַינָאבּ = פִּצֻּנָה', 'זינאב = הצולעת')
setname('133', 'תמים', 'תמים = כאמל')
setname('דנ-אבסכוה-א', 'אב-סכוה', "אב-סכוה = מורג'אן")
t = stories['דנ-אברהם-ב']['t']
old = 'הערה: בערך מופיע גם שם ערבי מלא שלפיו סבו הוא מורג׳אן — לא הוכרע מול «אב-סכוה». '
if old in t:
    stories['דנ-אברהם-ב']['t'] = t.replace(old, "שמו הערבי המלא: אברהים בן יעקוב בן מורג'אן — מורג'אן הוא השם הערבי של סבו אב-סכוה. ")
    LOG.append(('דנ-אברהם-ב', 'story', 'מורג׳אן = אב-סכוה'))
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
io.open('names_fixed_20261106c.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
print(LOG)
