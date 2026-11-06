# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
T = io.open('genealogy_template.html', encoding='utf-8').read()
if 'showParents(' in T:
    print('already patched'); sys.exit()


def rep(old, new, count=1):
    global T
    assert T.count(old) == count, (T.count(old), old[:70])
    T = T.replace(old, new)


# 1. a shorter number inside a longer printed reference is not a match
rep("  if(typeof sp.ref==='string'){ const id=resolveId(sp.ref); if(id) return id; }\n  return null;",
    "  if(typeof sp.ref==='string'){\n    const id=resolveId(sp.ref), dr=sp.ref.trim().match(/^\\d+/), di=(id||'').match(/^\\d+/);\n    if(id && (!dr || (di && di[0]===dr[0]))) return id;          // '1260' must not link to #126\n  }\n  return null;")
# 2. modern persons carry the mother link
rep("mother:m.mother, note:m.notes,", "mother:m.mother, mother_id:m.mother_id, mother_house:m.mother_house, mother_src:m.mother_src, note:m.notes,")
# 3. editing
rep("  if('mother' in patch) p.mother = patch.mother;\n",
    "  if('mother' in patch) p.mother = patch.mother;\n  if('mother_id' in patch) p.mother_id = patch.mother_id || undefined;\n  if('mother_house' in patch) p.mother_house = patch.mother_house || undefined;\n")
# 4. card
rep("""  if(p._modern && p.mother){ par+=(par?'<br>':'')+'אם: '+esc(p.mother); }
  else { const moms=motherNamesOf(p);
    if(moms.length) par+=(par?'<br>':'')+'<span class="years">אם (מבין נשות האב): '+moms.map(esc).join(' / ')+'</span>'; }
  if(par) html+=field('הורים', par);""",
"""  par+=(par?'<br>':'')+'שם האם: '+motherHtml(p);
  if(!motherPerson(p) && !motherText(p)){ const moms=motherNamesOf(p); if(moms.length) par+='<br><span class="years">נשות האב: '+moms.map(esc).join(' / ')+'</span>'; }
  par+='<div style="margin-top:8px"><button class="par-btn" data-par="'+escAttr(id)+'">👪 הצג הורים</button></div>';
  html+=field('הורים', par);""")
rep("  pBody.querySelectorAll('[data-go]').forEach(b=> b.onclick=()=>openPerson(b.getAttribute('data-go')) );",
    "  pBody.querySelectorAll('[data-go]').forEach(b=> b.onclick=()=>openPerson(b.getAttribute('data-go')) );\n  pBody.querySelectorAll('[data-par]').forEach(b=> b.onclick=()=>showParents(b.getAttribute('data-par')) );")
# 5. functions
JS = io.open('parents_feature.js', encoding='utf-8').read()
rep("function genOf(id){", JS + "\nfunction genOf(id){")
# 6. HTML
rep('<div id="toast"></div>\n', '''<div id="toast"></div>

<div class="share-modal par-modal" id="parModal">
  <div class="par-win">
    <div class="share-head">
      <span class="sh-title" id="parTitle">ההורים והאחים</span>
      <span class="par-status" id="parStatus"></span>
      <button id="parReplay" title="הפעל שוב">↻ שוב</button>
      <button id="parClose" title="סגור">✕</button>
    </div>
    <div class="par-legend">
      <span><i style="background:#2e7d6b"></i>האב, האם והאחים מאותו אב ואם</span>
      <span><i style="background:#c2722a"></i>אחים מאותו אב ומאם אחרת — מתחת לאב</span>
      <span><i style="background:#7a4f9e"></i>אחים מאותה אם ומאב אחר — מתחת לאם</span>
    </div>
    <div class="par-body" id="parBody"><div class="par-stage" id="parStage"></div></div>
  </div>
</div>
''')
# 7. CSS
rep("</style>", """  .par-btn{padding:6px 14px; font-size:13px; border:1px solid var(--accent2); background:#fff; color:var(--accent); border-radius:18px; cursor:pointer; font-weight:bold}
  .par-btn:hover{background:var(--hl)}
  .par-modal{z-index:90}
  .par-win{background:var(--panel); border-radius:12px; width:min(1100px,100%); max-height:94vh; display:flex; flex-direction:column; box-shadow:0 10px 40px rgba(0,0,0,.35); overflow:hidden}
  .par-win .share-head{gap:10px}
  .par-win .share-head button{font-size:13px}
  .par-status{flex:1; font-size:12px; color:var(--muted); text-align:center}
  .par-legend{display:flex; gap:14px; flex-wrap:wrap; padding:6px 14px; font-size:11px; color:var(--muted); border-bottom:1px solid var(--line)}
  .par-legend i{display:inline-block; width:12px; height:12px; border-radius:3px; margin-inline-end:5px; vertical-align:-2px}
  .par-body{overflow:auto; padding:6px}
  .par-stage{position:relative; margin:0 auto; direction:ltr}
  .par-svg{position:absolute; left:0; top:0; pointer-events:none}
  .pc{position:absolute; width:150px; height:76px; border:2px solid var(--pcc); background:var(--pcb); border-radius:9px; padding:4px 6px; text-align:center; cursor:pointer; overflow:hidden; direction:rtl; box-shadow:0 1px 5px rgba(0,0,0,.15)}
  .pc:hover{filter:brightness(.97); box-shadow:0 2px 9px rgba(0,0,0,.3)}
  .pcA{--pcc:#2e7d6b; --pcb:#e3f2ee} .pcB{--pcc:#c2722a; --pcb:#fbeedd} .pcC{--pcc:#7a4f9e; --pcb:#efe6f6}
  .pc.self{outline:3px solid #222; outline-offset:2px; background:#fff7cf}
  .pc.ghost{border-style:dashed; background:#fafafa; cursor:default; color:#777}
  .pc-role{font-size:10px; font-weight:bold; color:var(--pcc)}
  .pc-n{font-size:13px; font-weight:bold; line-height:1.2; max-height:32px; overflow:hidden}
  .pc-y{font-size:11px; color:#555}
  .pc-h{font-size:10px; color:var(--muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
  .pc-gl{position:absolute; text-align:center; font-size:11px; font-weight:bold; direction:rtl}
</style>""")
# 8. Escape closes the window first
rep("    const sm=document.getElementById('shareModal');\n    if(sm && sm.classList.contains('open')){ sm.classList.remove('open'); return; }",
    "    const pm=document.getElementById('parModal');\n    if(pm && pm.classList.contains('open')){ closeParents(); return; }\n    const sm=document.getElementById('shareModal');\n    if(sm && sm.classList.contains('open')){ sm.classList.remove('open'); return; }")
# 9. admin: mother fields
rep("""    '<label class="ef">סיפור חיים<textarea id="ef-story" rows="4">'+esc(st)+'</textarea></label>'+""",
"""    '<label class="ef">שם האם (טקסט, למשל «זינאב בת אברהם»)<input id="ef-mother" value="'+escAttr(p.mother||'')+'"></label>'+
    '<label class="ef">מזהה האם <span class="ef-cur">כעת: '+(motherPerson(p)?esc(lineageName(p.mother_id)):'—')+'</span>'+
      '<input id="ef-mid" value="'+escAttr(p.mother_id?(persons[p.mother_id]&&persons[p.mother_id].uid||p.mother_id):'')+'" placeholder="ID של האם אם היא קיימת בעץ"></label>'+
    '<label class="ef">בית האב של האם (אם אינה בעץ)<input id="ef-mhouse" value="'+escAttr(p.mother_house||'')+'"></label>'+
    '<label class="ef">סיפור חיים<textarea id="ef-story" rows="4">'+esc(st)+'</textarea></label>'+""")
rep("  const fid=idByAny(val('ef-fid'));\n",
"""  patch.mother=val('ef-mother').trim(); patch.mother_house=val('ef-mhouse').trim();
  { const mid=idByAny(val('ef-mid')); if(mid && !persons[mid]){ toast('מזהה האם אינו קיים'); return; } if(mid===id){ toast('אדם אינו יכול להיות אם של עצמו'); return; } patch.mother_id=mid||null; }
  const fid=idByAny(val('ef-fid'));
""")
rep("    case 'mother': return p.mother||'';", "    case 'mother': return p.mother || (motherPerson(p)?lineageName(p.mother_id):'');")
io.open('genealogy_template.html', 'w', encoding='utf-8').write(T)
print('patched')
