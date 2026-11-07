# -*- coding: utf-8 -*-
# 2026-11-09 — owner's request: wherever children of the same father were born to different mothers, show the mother's name in small
# print above each such child's card (tree view and the exported tree image).
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
T = io.open('genealogy_template.html', encoding='utf-8').read()
if 'halfMomInfo' in T:
    print('already patched'); sys.exit()


def rep(old, new):
    global T
    assert T.count(old) == 1, (T.count(old), old[:70])
    T = T.replace(old, new)


rep("function motherShort(p){", """function momKey2(p){                                       // same as motherKey, but two different unnamed wives of one man stay different
  const m=motherPerson(p); if(m) return 'id:'+m.id;
  const t=motherText(p); if(!t) return null;
  return (/^אשה/.test(t) && /נודע/.test(t)) ? 'u:'+t : 't:'+norm(givenOnly(t));
}
function momLabelText(p){
  const m=motherPerson(p); if(m) return 'אם: '+givenOnly(m.name);
  const t=motherText(p); if(!t) return '';
  if(/^אשה/.test(t) && /נודע/.test(t)) return 'אם: '+(/שניי/.test(t)?'אשה שנייה':/ראשונ/.test(t)?'אשה ראשונה':'אשה ללא שם');
  return 'אם: '+givenOnly(t);
}
// half-siblings: the father has children by more than one mother -> the card carries its mother's name
function halfMomInfo(id){
  const f=parentOf[id]; if(!f || !persons[f] || persons[f].sex==='F') return null;      // a woman registered as the parent is the mother herself
  const p=persons[id]; if(!momKey2(p)) return null;
  const sibs=(childMap[f]||[]).filter(c=>persons[c]); if(sibs.length<2) return null;
  const keys=new Set(); sibs.forEach(c=>{ const k=momKey2(persons[c]); if(k) keys.add(k); });
  if(keys.size<2) return null;
  const m=motherPerson(p);
  return {text:momLabelText(p), full:'אמו: '+(m?lineageName(m.id):(motherText(p)||''))};
}
function motherShort(p){""")
rep("""    nodeLayer.appendChild(box); domByPerson.set(id,box);
""", """    nodeLayer.appendChild(box); domByPerson.set(id,box);
    { const hm=halfMomInfo(id);                      // half-siblings: the mother's name, small, above the card
      if(hm){ const lb=document.createElement('div'); lb.className='nb-mom'; lb.textContent=hm.text; lb.title=hm.full;
        lb.style.left=(cx+NODE_W/2-64)+'px'; lb.style.top=(cy-NODE_H/2-13)+'px'; lb.style.width='60px'; nodeLayer.appendChild(lb); } }
""")
rep("  .node-box{touch-action:manipulation;", """  .nb-mom{position:absolute; height:12px; line-height:12px; font-size:9.5px; color:#7b5e2e; text-align:right; direction:rtl; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; cursor:default}
  .node-box{touch-action:manipulation;""")
# exported picture
rep("""    c.beginPath(); if(c.roundRect) c.roundRect(x,y,NW,NH,9); else c.rect(x,y,NW,NH); c.fill(); c.stroke();
""", """    c.beginPath(); if(c.roundRect) c.roundRect(x,y,NW,NH,9); else c.rect(x,y,NW,NH); c.fill(); c.stroke();
    { const hm=halfMomInfo(id); if(hm){ c.save(); c.font='9px "Segoe UI","Arial Hebrew",Arial,sans-serif'; c.fillStyle='#7b5e2e'; c.textAlign='right'; c.fillText(wrapLines(c,hm.text,60,1)[0],x+NW-3,y-4); c.restore(); } }
""")
io.open('genealogy_template.html', 'w', encoding='utf-8').write(T)
print('patched')
