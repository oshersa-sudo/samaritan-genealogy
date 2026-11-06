# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
T = io.open('genealogy_template.html', encoding='utf-8').read()
if 'showTreeImage(' in T:
    print('already patched'); sys.exit()


def rep(old, new, count=1):
    global T
    assert T.count(old) == count, (T.count(old), old[:70])
    T = T.replace(old, new)


rep("""function openShare(rootIds, title){
  currentShareText=buildTreeText(rootIds, title);""", """function openShare(rootIds, title){
  currentShareRoots=rootIds.slice(); currentShareTitle=title;
  currentShareText=buildTreeText(rootIds, title);""")
rep("function shareVia(method){\n", "function shareVia(method){\n  if(method==='image'){ showTreeImage(); return; }\n")
rep("let currentShareText='';\n", "let currentShareText='';\n" + io.open('image_share_feature.js', encoding='utf-8').read() + "\n")
rep("""        <button class="sa-copy" data-m="copy">📋 העתק</button>""", """        <button class="sa-img" data-m="image">🖼️ שתף כתמונה</button>
        <button class="sa-copy" data-m="copy">📋 העתק</button>""")
rep("""      <div class="share-hint">השיתוף שולח את העץ כטקסט.""", """      <div class="share-hint">«שתף כתמונה» מצייר את העץ בחלון נפרד, ומשם אפשר לשלוח אותו כתמונה. השיתוף הרגיל שולח את העץ כטקסט.""")
rep('<div id="toast"></div>\n', '''<div id="toast"></div>

<div class="share-modal img-modal" id="imgModal">
  <div class="img-win">
    <div class="share-head">
      <span class="sh-title" id="imgTitle">תמונת העץ</span>
      <button onclick="closeTreeImage()" title="סגור">✕</button>
    </div>
    <div class="img-ctl">
      <label>דורות <select id="imgGen" onchange="renderTreeImage()"></select></label>
      <label><input type="checkbox" id="imgSp" onchange="renderTreeImage()"> הצג בני זוג</label>
      <button id="imgFit" onclick="imgToggleFit()">גודל מלא</button>
      <span class="img-status" id="imgStatus"></span>
    </div>
    <div class="img-body"><img id="imgView" alt="תמונת עץ היוחסין"></div>
    <div class="img-actions">
      <button class="ia-share" onclick="imgShare()">📤 שתף</button>
      <button class="ia-dl" onclick="imgDownload()">⬇️ הורד תמונה</button>
      <button class="ia-copy" onclick="imgCopy()">📋 העתק תמונה</button>
    </div>
  </div>
</div>
''')
rep("</style>", """  .sa-img{background:#8a5a2b} .sa-img:hover{background:#6f4721}
  .img-modal{z-index:95}
  .img-win{background:var(--panel); border-radius:12px; width:min(1100px,100%); max-height:94vh; display:flex; flex-direction:column; box-shadow:0 10px 40px rgba(0,0,0,.35); overflow:hidden}
  .img-ctl{display:flex; gap:14px; align-items:center; flex-wrap:wrap; padding:8px 14px; border-bottom:1px solid var(--line); font-size:13px}
  .img-ctl select,.img-ctl button{font:inherit; font-size:13px; padding:3px 8px; border:1px solid var(--line); border-radius:6px; background:#fff; cursor:pointer}
  .img-status{flex:1; font-size:11.5px; color:var(--muted)}
  .img-body{overflow:auto; padding:8px; background:#ece6d8; text-align:center; min-height:200px}
  .img-body img{max-width:100%; height:auto; box-shadow:0 2px 12px rgba(0,0,0,.25); background:#fff; transition:opacity .2s}
  .img-body img.full{max-width:none}
  .img-actions{display:flex; gap:10px; padding:10px 14px; border-top:1px solid var(--line); flex-wrap:wrap}
  .img-actions button{flex:1; min-width:120px; padding:10px; border:none; border-radius:8px; font:inherit; font-size:14px; font-weight:bold; cursor:pointer; color:#fff}
  .ia-share{background:#25d366} .ia-dl{background:var(--accent)} .ia-copy{background:#5b7fb8}
</style>""")
rep("    const pm=document.getElementById('parModal');",
    "    const im=document.getElementById('imgModal');\n    if(im && im.classList.contains('open')){ closeTreeImage(); return; }\n    const pm=document.getElementById('parModal');")
io.open('genealogy_template.html', 'w', encoding='utf-8').write(T)
print('patched')
