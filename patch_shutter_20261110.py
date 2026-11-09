# -*- coding: utf-8 -*-
# 2026-11-10 — owner: everything above the tree folds up after a few seconds into a «shutter» (handle + permanent down-arrow, like the Torah app),
# re-folds a few seconds after being opened; the apex (צמרת) of the tree is centred; the whole app is responsive.
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
T = 'genealogy_template.html'
s = io.open(T, encoding='utf-8').read()
if 'id="shutter"' in s:
    print('already patched'); sys.exit()


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (a[:70], s.count(a))
    s = s.replace(a, b)


# ---------- 1. structure: header + legends + apex go into the shutter body
i0 = s.index('<body>\n<header>')
j0 = s.index('</header>\n\n<main>')
k0 = s.index('  <div class="workspace">')
legends = s[j0 + len('</header>\n\n<main>'):k0]
s = s[:i0] + '<body>\n<div id="shutter" class="open"><div id="shutterBody">\n<header>' + s[i0 + len('<body>\n<header>'):j0] + '</header>\n' \
    '<div class="sh-legends">' + legends + '</div>\n</div>\n' \
    '<button id="shutterHandle" class="sh-handle" type="button" aria-expanded="true" aria-controls="shutterBody" title="פתיחה / קיפול של לוח הכלים" aria-label="פתיחה או קיפול של לוח הכלים: חיפוש, סינון וזום">' \
    '<span class="sh-arrow sh-arrow-l"></span><span class="sh-grip"></span><span class="sh-arrow sh-arrow-r"></span></button>\n</div>\n\n<main>\n' + s[k0:]

# ---------- 2. page layout: the tree fills what the shutter leaves
rep("html,body{margin:0;padding:0}", "html,body{margin:0;padding:0;height:100%}")
rep("    background:var(--bg); color:var(--ink); line-height:1.5;\n  }",
    "    background:var(--bg); color:var(--ink); line-height:1.5;\n    display:flex; flex-direction:column; height:100vh; height:100dvh; overflow:hidden;\n  }")
rep("  main{padding:16px}", "  main{flex:1 1 auto; min-height:0; padding:8px 12px 10px; display:flex; flex-direction:column}")
rep("  .workspace{display:flex; gap:14px; align-items:flex-start}", "  .workspace{display:flex; gap:14px; align-items:stretch; flex:1 1 auto; min-height:0}")
rep("            max-height:calc(100vh - 240px); min-height:440px; position:relative}", "            max-height:none; min-height:200px; position:relative}")
rep("  .tree-canvas{position:relative; transform-origin:100% 0}", "  .tree-canvas{position:relative; transform-origin:100% 0; margin-inline:auto}")
rep("    flex:0 0 360px; align-self:flex-start; position:sticky; top:8px;", "    flex:0 0 clamp(300px,28vw,380px); align-self:flex-start; position:sticky; top:0;")
rep("overflow:auto; max-height:calc(100vh - 120px);\n  }", "overflow:auto; max-height:100%;\n  }")
rep("    #treeHost{max-height:none; height:66vh; min-height:320px}\n", "    #treeHost{max-height:none; min-height:200px}\n")
rep("    .workspace{display:block}\n    #treeHost{max-height:none; height:60vh; min-height:300px}\n", "    #treeHost{max-height:none; min-height:200px}\n")
rep("    header,.legend,.house-legend,#apexHost,#panel,", "    #shutter,header,.legend,.house-legend,#apexHost,#panel,")
rep("    main,.workspace{position:static !important; display:block !important}", "    html,body{height:auto !important; overflow:visible !important; display:block !important}\n    main,.workspace{position:static !important; display:block !important}")

# ---------- 3. CSS: the shutter, tablets, short screens
CSS = r'''
  /* ===== the shutter: header + legends + apex fold up out of the way, like the Torah app's bars ===== */
  #shutter{position:relative; flex:0 0 auto; z-index:30; background:var(--panel)}
  #shutterBody{max-height:none; overflow:visible; transition:max-height .5s ease, opacity .35s ease}
  #shutter.anim #shutterBody,#shutter.folded #shutterBody{overflow:hidden}
  #shutter.folded #shutterBody{max-height:0; opacity:0; pointer-events:none; visibility:hidden; transition:max-height .5s ease, opacity .3s ease, visibility 0s .5s}
  .sh-legends{padding:10px 16px 2px}
  #shutter header{position:static}
  .sh-handle{position:relative; display:flex; align-items:center; justify-content:center; gap:26px; width:100%; height:30px; padding:0; border:0;
    border-bottom:2px solid var(--accent2); background:var(--panel); box-shadow:var(--shadow); cursor:pointer; touch-action:manipulation; -webkit-tap-highlight-color:transparent}
  .sh-handle:focus-visible{outline:3px solid var(--hl-border); outline-offset:-3px}
  /* a chunky handle: a rounded bar with a groove down its middle */
  .sh-grip{position:relative; width:64px; height:12px; border-radius:6px; background:linear-gradient(#d9bd80,#a8823d);
    box-shadow:inset 0 1px 0 rgba(255,255,255,.55), 0 1px 3px rgba(60,45,20,.45); transition:filter .2s}
  .sh-grip::after{content:''; position:absolute; left:10px; right:10px; top:50%; height:2.5px; transform:translateY(-50%); background:rgba(60,45,20,.45); border-radius:2px}
  .sh-handle:hover .sh-grip{filter:brightness(1.1)}
  /* the standing arrow: a double chevron, bobbing downward for as long as the shutter is closed */
  .sh-arrow{position:relative; width:12px; height:12px; flex:0 0 auto; pointer-events:none}
  .sh-arrow::before,.sh-arrow::after{content:''; position:absolute; left:50%; width:10px; height:10px; border-right:3px solid var(--accent); border-bottom:3px solid var(--accent);
    transform:translateX(-50%) rotate(45deg); filter:drop-shadow(0 0 3px rgba(242,193,78,.9))}
  .sh-arrow::before{top:-5px} .sh-arrow::after{top:3px; opacity:.55}
  #shutter.folded .sh-arrow{animation:shBob 1.2s ease-in-out infinite}
  #shutter.folded .sh-arrow::before,#shutter.folded .sh-arrow::after{border-color:#c98a10}
  #shutter.folded .sh-arrow-l{animation-delay:.15s}
  #shutter:not(.folded) .sh-arrow{transform:rotate(180deg); opacity:.55}      /* open: a quiet up-chevron — pull to fold */
  @keyframes shBob{0%,100%{transform:translateY(-3px); opacity:.55} 50%{transform:translateY(5px); opacity:1}}
  @media (prefers-reduced-motion:reduce){ #shutter.folded .sh-arrow{animation:none; opacity:1} #shutterBody{transition:none} }
  /* an open shutter taller than the screen scrolls inside itself (phones with the options panel open) */
  @media (max-width:760px){ #shutter:not(.folded):not(.anim) #shutterBody:has(.controls:not(.collapsed)){overflow:auto; max-height:calc(100dvh - 120px)} }

  /* ===== responsive: tablets / small laptops — the detail panel becomes a bottom sheet instead of squeezing the tree ===== */
  @media (max-width:1000px){
    #panel{position:fixed; left:0; right:0; bottom:0; top:auto; width:auto; align-self:auto; flex:none;
      max-height:85vh; z-index:60; border:none; border-top:3px solid var(--accent2); border-radius:16px 16px 0 0; box-shadow:0 -6px 24px rgba(40,30,15,.4)}
    body.panel-open #panelBackdrop{display:block; position:fixed; inset:0; background:rgba(40,30,15,.45); z-index:59}
    .p-head{border-radius:16px 16px 0 0}
    .search-wrap{min-width:220px}
    .sh-legends{padding:8px 12px 0}
  }
  /* short screens (phones on their side): keep the tree usable */
  @media (max-height:520px){ main{padding:4px 8px 6px} .sh-handle{height:26px} #treeHost{min-height:140px} }
  @media (max-width:430px){ main{padding:6px 6px 8px} .sh-legends{padding:6px 8px 0} }
'''
rep("</style>\n</head>", CSS + "</style>\n</head>")

# ---------- 4. JS: the shutter controller + apex centring
JS = r'''
/* ---------- the shutter: folds itself a few seconds after load and after every opening ---------- */
const shutterEl=document.getElementById('shutter'), shutterBodyEl=document.getElementById('shutterBody'), shutterBtn=document.getElementById('shutterHandle');
let _shT=null; const SH_FIRST=7000, SH_AGAIN=9000;
function shutterBusy(){
  const a=document.activeElement, res=document.getElementById('results');
  return !!((a && shutterEl.contains(a) && /^(INPUT|SELECT|TEXTAREA)$/.test(a.tagName)) || (res && res.classList.contains('open')));
}
function shutterSchedule(ms){ clearTimeout(_shT); _shT=setTimeout(foldShutter, ms); }
function foldShutter(){
  if(shutterEl.classList.contains('folded')) return;
  if(shutterBusy()){ shutterSchedule(3500); return; }          // never fold under the user's hands (typing / picking a result)
  shutterBodyEl.style.maxHeight=shutterBodyEl.scrollHeight+'px'; void shutterBodyEl.offsetHeight;
  shutterEl.classList.add('anim'); shutterEl.classList.remove('open'); shutterEl.classList.add('folded');
  shutterBodyEl.style.maxHeight='0px'; try{ shutterBodyEl.inert=true; }catch(e){}
  shutterBtn.setAttribute('aria-expanded','false'); clearTimeout(_shT);
  setTimeout(()=>{ shutterEl.classList.remove('anim'); afterShutter(); }, 520);
}
function openShutter(){
  shutterEl.classList.remove('folded'); shutterEl.classList.add('open','anim'); try{ shutterBodyEl.inert=false; }catch(e){}
  shutterBodyEl.style.maxHeight=shutterBodyEl.scrollHeight+'px'; shutterBtn.setAttribute('aria-expanded','true');
  setTimeout(()=>{ shutterEl.classList.remove('anim'); shutterBodyEl.style.maxHeight='none'; afterShutter(); }, 520);
  shutterSchedule(SH_AGAIN);
}
function afterShutter(){ /* the tree box just changed height; nothing to re-render, only keep the apex in view */ }
shutterBtn.addEventListener('click',()=>{ shutterEl.classList.contains('folded') ? openShutter() : foldShutter(); });
['pointerdown','keydown','input','wheel','touchstart'].forEach(ev=>shutterBodyEl.addEventListener(ev,()=>{ if(!shutterEl.classList.contains('folded')) shutterSchedule(SH_AGAIN); },{passive:true}));
shutterBodyEl.addEventListener('focusout',()=>{ if(!shutterEl.classList.contains('folded')) shutterSchedule(SH_AGAIN); });
function shutterSoon(){ if(!shutterEl.classList.contains('folded')) shutterSchedule(1400); }   // after a search result was chosen
shutterSchedule(SH_FIRST);

/* ---------- the apex (צמרת) of the shown tree sits in the middle of the screen ---------- */
function centerApex(){
  const host=treeHost; if(!host) return;
  let box=null;
  if(viewMode==='family' && selectedFamilyIdx!=null && familyList[selectedFamilyIdx]){
    const f=familyList[selectedFamilyIdx]; const ids=(f.rootIds&&f.rootIds.length)?f.rootIds:f.allIds.slice(0,1);
    box=domByPerson.get(ids[0]);
  } else box=domByPerson.get(VROOT);
  if(!box) box=host.querySelector('.node-box');
  if(!box) return;
  const hr=host.getBoundingClientRect(), br=box.getBoundingClientRect();
  host.scrollLeft += (br.left+br.width/2)-(hr.left+hr.width/2);
  host.scrollTop=0;
}
let _rzT=null;
window.addEventListener('resize',()=>{ clearTimeout(_rzT); _rzT=setTimeout(()=>{ if(viewMode==='root'&&!focusedBox) fitToWidth(); centerApex(); },220); });
window.addEventListener('orientationchange',()=>setTimeout(()=>{ if(viewMode==='root'&&!focusedBox) fitToWidth(); centerApex(); },350));
'''
rep("/* ---------- init ---------- */", JS + "\n/* ---------- init ---------- */")
rep("fitToWidth();\n// admin editing:", "fitToWidth();\ncenterApex();\n// admin editing:")
# zoom keeps the apex centred
rep("document.getElementById('zoomReset').textContent=Math.round(zoom*100)+'%'; applyZoom(); }", "document.getElementById('zoomReset').textContent=Math.round(zoom*100)+'%'; applyZoom(); if(typeof centerApex==='function'&&!focusedBox) centerApex(); }")
# family / root jump: centre the apex instead of snapping to the edge
rep("renderTree(); treeHost.scrollTop=0; treeHost.scrollLeft=0; return; }", "renderTree(); centerApex(); return; }")
rep("  renderTree(); treeHost.scrollTop=0; treeHost.scrollLeft=0;\n};", "  renderTree(); centerApex();\n};")
# after locating a person from the search: fold the shutter soon
rep("  box.scrollIntoView({behavior:'smooth', block:'center', inline:'center'});\n}", "  box.scrollIntoView({behavior:'smooth', block:'center', inline:'center'});\n  if(typeof shutterSoon==='function') shutterSoon();\n}")
io.open(T, 'w', encoding='utf-8', newline='').write(s)
print('patched')
