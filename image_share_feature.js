/* ---------- share the branch as a DRAWING (PNG): drawn in its own window, then shared / downloaded / copied ---------- */
let currentShareRoots=[], currentShareTitle='', _imgBlob=null, _imgUrl=null, _imgRun=0;
const HOUSE_COL=[['דנפים','#2e7d6b'],['מרחיבים','#7a4f9e'],['צפרים','#c2722a'],['כהונה','#b0392f']];
function houseColorOf(hn){ const h=HOUSE_COL.find(x=>(hn||'').indexOf(x[0])>=0); return h?h[1]:'#8a8a8a'; }
function treeImgLayout(rootIds, maxGen){
  const pos=new Map(), seen=new Set(); let nx=0, maxD=0, leaves=0;
  function asg(id,d){
    seen.add(id); if(d>maxD) maxD=d;
    const ks=(d+1<maxGen)?(childMap[id]||[]).slice().sort(byBirthIds).filter(c=>!seen.has(c)&&persons[c]):[];
    if(!ks.length){ pos.set(id,{x:nx++,y:d,kids:[]}); leaves++; return; }
    ks.forEach(c=>asg(c,d+1));
    const xs=ks.map(c=>pos.get(c).x); pos.set(id,{x:(Math.min(...xs)+Math.max(...xs))/2,y:d,kids:ks});
  }
  rootIds.forEach(r=>{ if(!seen.has(r) && persons[r]) asg(r,0); });
  return {pos,cols:nx,depth:maxD+1,leaves,count:seen.size};
}
function treeDepthAll(rootIds){ return treeImgLayout(rootIds,999).depth; }
function wrapLines(ctx,text,maxW,maxLines){
  const words=(text||'').split(/\s+/).filter(Boolean), lines=[]; let cur='';
  words.forEach(w=>{ const t=cur?cur+' '+w:w; if(ctx.measureText(t).width<=maxW||!cur) cur=t; else { lines.push(cur); cur=w; } });
  if(cur) lines.push(cur);
  if(lines.length>maxLines){ const keep=lines.slice(0,maxLines); let l=keep[maxLines-1]; while(l.length>1 && ctx.measureText(l+'…').width>maxW) l=l.slice(0,-1); keep[maxLines-1]=l+'…'; return keep; }
  return lines;
}
function spouseLine(p){ const n=(p.spouses||[]).map(s=>givenOnly(s.name)).filter(Boolean).slice(0,2); return n.length?'♥ '+n.join(', '):''; }
function drawTreeImage(rootIds, title, maxGen, withSpouses){
  const L=treeImgLayout(rootIds,maxGen);
  const NW=142, NH=withSpouses?76:58, GX=14, GY=46, PAD=26, HH=96, FH=34;
  const treeW=Math.max(1,L.cols)*(NW+GX)-GX, W=Math.max(560,treeW+2*PAD), H=HH+L.depth*NH+(L.depth-1)*GY+FH+PAD;
  const MAXPX=10000, MAXAREA=64e6;
  let s=2; s=Math.min(s, MAXPX/W, MAXPX/H, Math.sqrt(MAXAREA/(W*H)));
  const cv=document.createElement('canvas'); cv.width=Math.max(1,Math.floor(W*s)); cv.height=Math.max(1,Math.floor(H*s));
  const c=cv.getContext('2d'); c.scale(s,s); c.direction='rtl'; c.textBaseline='alphabetic';
  c.fillStyle='#fffdf8'; c.fillRect(0,0,W,H);
  c.strokeStyle='#b8954a'; c.lineWidth=3; c.strokeRect(6,6,W-12,H-12);
  c.textAlign='center'; c.fillStyle='#7b5e2e'; c.font='bold 24px "Segoe UI","Arial Hebrew",Arial,sans-serif'; c.fillText(title,W/2,44);
  // lineage of the root
  let sub='';
  if(rootIds.length===1){ const p0=persons[rootIds[0]]; const anc=[]; let a=parentOf[rootIds[0]], g=0;
    while(a && persons[a] && g++<100){ anc.unshift(givenOnly(persons[a].name)||a); a=parentOf[a]; }
    sub=(p0?houseShort(p0._house)+(anc.length?' · ':''):'')+(anc.length?'שושלת: '+anc.slice(-6).join(' ‹ ')+(anc.length>6?' (…)':''):''); }
  c.font='14px "Segoe UI","Arial Hebrew",Arial,sans-serif'; c.fillStyle='#7d7468';
  if(sub){ const sl=wrapLines(c,sub,W-2*PAD,1)[0]; c.fillText(sl,W/2,70); }
  const ox=(W-treeW)/2, X=x=>ox+(L.cols-1-x)*(NW+GX)+NW/2, Y=y=>HH+y*(NH+GY);   // mirrored: the first child on the right (Hebrew reading)
  // edges first
  c.strokeStyle='#a89a7c'; c.lineWidth=2; c.lineJoin='round';
  L.pos.forEach((v,id)=>{ if(!v.kids.length) return;
    const px=X(v.x), py=Y(v.y)+NH, my=py+GY/2; c.beginPath(); c.moveTo(px,py); c.lineTo(px,my);
    const xs=v.kids.map(k=>X(L.pos.get(k).x)); c.moveTo(Math.min(...xs,px),my); c.lineTo(Math.max(...xs,px),my);
    v.kids.forEach(k=>{ const kx=X(L.pos.get(k).x); c.moveTo(kx,my); c.lineTo(kx,Y(L.pos.get(k).y)); }); c.stroke(); });
  // nodes
  L.pos.forEach((v,id)=>{
    const p=persons[id], x=X(v.x)-NW/2, y=Y(v.y), col=houseColorOf(p._house), isRoot=rootIds.includes(id);
    c.fillStyle=isRoot?'#fff3c4':(p.sex==='F'?'#f8eaf1':p.sex==='M'?'#e7f0f6':'#f3f0ea'); c.strokeStyle=col; c.lineWidth=isRoot?3.5:2;
    c.beginPath(); if(c.roundRect) c.roundRect(x,y,NW,NH,9); else c.rect(x,y,NW,NH); c.fill(); c.stroke();
    c.fillStyle='#2c2620'; c.font='bold 13px "Segoe UI","Arial Hebrew",Arial,sans-serif';
    const nl=wrapLines(c,displayName(p),NW-12,2); let ty=y+17; nl.forEach(t=>{ c.fillText(t,x+NW/2,ty); ty+=15; });
    const yr=(displayYears(id,p)||'').replace(/^\(|\)$/g,'');
    c.font='11px "Segoe UI","Arial Hebrew",Arial,sans-serif'; c.fillStyle='#6b6255';
    if(yr){ c.fillText(yr,x+NW/2,Math.max(ty,y+NH-(withSpouses?30:9))); }
    if(withSpouses){ const sp=spouseLine(p); if(sp){ c.fillStyle=col; c.fillText(wrapLines(c,sp,NW-12,1)[0],x+NW/2,y+NH-9); } }
  });
  c.textAlign='center'; c.fillStyle='#7d7468'; c.font='12px "Segoe UI","Arial Hebrew",Arial,sans-serif';
  c.fillText('אילן יוחסין שומרוני · מיפקד 1909 · '+L.count+' אנשים · '+location.host,W/2,H-PAD+4);
  return {canvas:cv, layout:L, scale:s};
}
function imgSelValues(){ return {gen:+document.getElementById('imgGen').value||999, sp:document.getElementById('imgSp').checked}; }
function showTreeImage(){
  const roots=currentShareRoots, title=currentShareTitle; if(!roots.length) return;
  const modal=document.getElementById('imgModal'); document.getElementById('imgTitle').textContent='תמונת העץ: '+title;
  const all=treeDepthAll(roots), sel=document.getElementById('imgGen'); sel.innerHTML='';
  // default: as many generations as keep the picture readable (≈ 28 leaves)
  let def=all; for(let g=1; g<=all; g++){ if(treeImgLayout(roots,g).leaves>28){ def=Math.max(1,g-1); break; } }
  for(let g=1; g<=all; g++){ const o=document.createElement('option'); o.value=g; o.textContent=(g===all?'כל '+all+' הדורות':g+' '+(g===1?'דור':'דורות')); sel.appendChild(o); }
  sel.value=def; modal.classList.add('open'); renderTreeImage();
}
function renderTreeImage(){
  const run=++_imgRun, st=document.getElementById('imgStatus'), img=document.getElementById('imgView');
  const v=imgSelValues(); st.textContent='מצייר את העץ…'; img.style.opacity='.35';
  setTimeout(()=>{ if(run!==_imgRun) return;
    let r; try{ r=drawTreeImage(currentShareRoots,currentShareTitle,v.gen,v.sp); }catch(e){ st.textContent='שגיאה בציור: '+e.message; return; }
    r.canvas.toBlob(b=>{ if(run!==_imgRun) return; if(!b){ st.textContent='לא ניתן ליצור תמונה'; return; }
      _imgBlob=b; if(_imgUrl) URL.revokeObjectURL(_imgUrl); _imgUrl=URL.createObjectURL(b);
      img.onload=()=>{ img.style.opacity='1'; }; img.src=_imgUrl;
      const L=r.layout; st.textContent=L.count+' אנשים · '+L.depth+' דורות'+(r.scale<1.99?' · התמונה גדולה מאוד — אפשר להקטין את מספר הדורות לקריאות טובה יותר':'');
    },'image/png');
  },30);
}
function imgFileName(){ return ('אילן-יוחסין-'+currentShareTitle).replace(/[\\\/:*?"<>|\s]+/g,'-').slice(0,60)+'.png'; }
async function imgShare(){
  if(!_imgBlob) return;
  const file=new File([_imgBlob], imgFileName(), {type:'image/png'});
  try{
    if(navigator.canShare && navigator.canShare({files:[file]})){ await navigator.share({files:[file], title:currentShareTitle, text:'אילן יוחסין שומרוני — '+currentShareTitle}); return; }
  }catch(e){ if(e&&e.name==='AbortError') return; }
  imgDownload(); toast('הדפדפן אינו תומך בשיתוף ישיר של תמונה — התמונה ירדה למכשיר, אפשר לשלוח אותה משם');
}
function imgDownload(){
  if(!_imgUrl) return; const a=document.createElement('a'); a.href=_imgUrl; a.download=imgFileName(); document.body.appendChild(a); a.click(); a.remove();
}
async function imgCopy(){
  if(!_imgBlob) return;
  try{ await navigator.clipboard.write([new ClipboardItem({'image/png':_imgBlob})]); toast('התמונה הועתקה ללוח ✓'); }
  catch(e){ toast('העתקת תמונה אינה נתמכת כאן — השתמשו בהורדה'); }
}
function closeTreeImage(){ _imgRun++; document.getElementById('imgModal').classList.remove('open'); }
function imgToggleFit(){ const img=document.getElementById('imgView'); img.classList.toggle('full'); document.getElementById('imgFit').textContent=img.classList.contains('full')?'התאם לחלון':'גודל מלא'; }
