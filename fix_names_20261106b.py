# -*- coding: utf-8 -*-
# 2026-11-06 (b) — owner's corrections:
#  * «אלמנעלם» → «אלמועלם» (ישראל אלמועלם = «המורה»), every niqqud variant, in the site data AND in the scripts/transcripts that would
#    otherwise re-introduce it;
#  * #הס-וגיה, son of עבד-הרחום: «וגֿ'יה (ע'גֿ'יה)» → «יפנה = וואג'י».
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
NIQ = '[֑-ׇ]*'
PAT = re.compile('א' + NIQ + 'ל' + NIQ + 'מ' + NIQ + 'נ' + NIQ + 'ע' + NIQ + 'ל' + NIQ + '[םמ]')
LOG = []

def fix_file(path, extra=None):
    t = io.open(path, encoding='utf-8', newline='').read()
    o = t
    t, n = PAT.subn(lambda m: 'אלמועלם' if m.group(0).endswith('ם') else 'אלמועלמ', t)
    if extra:
        for a, b in extra:
            if a in t:
                t = t.replace(a, b); n += 1
    if t != o:
        io.open(path, 'w', encoding='utf-8', newline='').write(t)
        LOG.append({'file': path, 'changes': n})

for f in ['master_v2.json', 'stories.json', 'page_81_mishlama_prose.txt', 'page_88_hasatri_prose.txt', 'page_98_tsfari_prose.txt',
          'diagrams_summary.md', 'events_crosscheck.csv', 'fix_tsfari.py']:
    fix_file(f)
SON = [("וגֿ'יה (ע'גֿ'יה)", "יפנה = וואג'י")]
for f in ['master_v2.json', 'add_hesatri.py']:
    fix_file(f, SON)
print(json.dumps(LOG, ensure_ascii=False))
io.open('names_fixed_20261106b.json', 'w', encoding='utf-8').write(json.dumps(LOG, ensure_ascii=False, indent=1))
