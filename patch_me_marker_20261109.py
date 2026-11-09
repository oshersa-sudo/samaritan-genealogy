# -*- coding: utf-8 -*-
# 2026-11-09 — owner: mark «אנוכי» (registry M495) in the tree with a special frame, and say so on the card.
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
T = io.open('genealogy_template.html', encoding='utf-8').read()
if "node-box.me" in T:
    print('already patched'); sys.exit()


def rep(old, new):
    global T
    assert T.count(old) == 1, (T.count(old), old[:70])
    T = T.replace(old, new)


rep("note:m.notes, _parentRaw:m.parent,", "note:m.notes, me:m.me, _parentRaw:m.parent,")
rep("  .node-box.modern{background:#f3f8fc}", """  .node-box.modern{background:#f3f8fc}
  .node-box.me{border:3px solid #b8860b; background:#fffbea; box-shadow:0 0 0 3px #f2c14e, 0 0 16px 5px rgba(242,193,78,.75)}
  .node-box.me::before{content:'★ אנוכי'; position:absolute; bottom:1px; inset-inline-end:4px; font-size:9px; font-weight:700; color:#8a6508}
  .me-box{border:2px solid #b8860b; background:#fffbea; border-radius:8px; padding:6px 10px; font-weight:700; color:#6b4e06}""")
rep("(p._modern?' modern':'')+' '+houseClass(p._house);", "(p._modern?' modern':'')+(p.me?' me':'')+' '+houseClass(p._house);")
rep("  html+=field('פרטים', meta.join(' · '));", "  if(p.me) html+=field('★ אנוכי','<div class=\"me-box\">זה אני — בעל האתר, בנם של שוהם ובדיעה. כאן אני עומד בעץ המשפחה.</div>');\n  html+=field('פרטים', meta.join(' · '));")
io.open('genealogy_template.html', 'w', encoding='utf-8').write(T)
J = io.open('image_share_feature.js', encoding='utf-8').read()
a = "c.beginPath(); if(c.roundRect) c.roundRect(x,y,NW,NH,9); else c.rect(x,y,NW,NH); c.fill(); c.stroke();"
assert J.count(a) == 1
J = J.replace(a, a + "\n    if(p.me){ c.save(); c.strokeStyle='#e0a800'; c.lineWidth=4; c.strokeRect(x-3,y-3,NW+6,NH+6); c.fillStyle='#8a6508'; c.font='bold 9px \"Segoe UI\",Arial,sans-serif'; c.textAlign='right'; c.fillText('★ אנוכי',x+NW-4,y+NH-4); c.restore(); }")
io.open('image_share_feature.js', 'w', encoding='utf-8').write(J)
T = io.open('genealogy_template.html', encoding='utf-8').read()
# the image feature is also inlined in the template: same edit there when present
if a in T:
    T = T.replace(a, a + "\n    if(p.me){ c.save(); c.strokeStyle='#e0a800'; c.lineWidth=4; c.strokeRect(x-3,y-3,NW+6,NH+6); c.fillStyle='#8a6508'; c.font='bold 9px \"Segoe UI\",Arial,sans-serif'; c.textAlign='right'; c.fillText('★ אנוכי',x+NW-4,y+NH-4); c.restore(); }")
    io.open('genealogy_template.html', 'w', encoding='utf-8').write(T)
print('patched')
