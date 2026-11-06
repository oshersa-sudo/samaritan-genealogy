/* ---------- «שם האם» on the card + «הצג הורים» (animated parents / siblings window) ---------- */
function houseShort(h){ return (h||'').replace(/^[א-ת]\.\s*/,''); }
function lineageName(id){                                   // «זינאב בת אברהם בן יוסף»
  const q=persons[id]; if(!q) return '';
  const fid=parentOf[id]; let father='', gf='';
  if(fid && persons[fid]){ father=givenOnly(persons[fid].name); const gid=parentOf[fid]; if(gid && persons[gid]) gf=givenOnly(persons[gid].name); else if(persons[fid].father) gf=givenOnly(persons[fid].father); }
  else if(q.father) father=givenOnly(q.father);
  const own=givenOnly(q.name)||q.name||'';
  return own+(father?' '+relOf(q)+' '+father+(gf?' בן '+gf:''):'');
}
function motherPerson(p){ return (p && p.mother_id && persons[p.mother_id]) ? persons[p.mother_id] : null; }
function motherText(p){ return ((p&&p.mother)||'').toString().trim(); }
function motherKey(p){ const m=motherPerson(p); if(m) return 'id:'+m.id; const t=motherText(p); return t ? 't:'+norm(givenOnly(t)) : null; }
function motherHtml(p){
  const m=motherPerson(p);
  if(m){ const hs=houseShort(m._house); return plink(m.id, lineageName(m.id))+(hs?' <span class="years">· מבית אב: '+esc(hs)+'</span>':''); }
  const t=motherText(p);
  if(t){ const hs=houseShort(p.mother_house); return esc(t)+(hs?' <span class="years">· מבית אב: '+esc(hs)+'</span>':''); }
  return '<span class="years">לא ידוע במקורות</span>';
}
function motherShort(p){ const m=motherPerson(p); if(m) return givenOnly(m.name); const t=motherText(p); return t?givenOnly(t):''; }

const PC_W=150, PC_H=76, PC_GAP=14;
let _parRun=0;
function closeParents(){ _parRun++; const m=document.getElementById('parModal'); if(m) m.classList.remove('open'); }
function pcCard(spec, cls){
  const d=document.createElement('div');
  d.className='pc '+cls+(spec.self?' self':'')+(spec.ghost?' ghost':'');
  if(spec.id && persons[spec.id]){
    const q=persons[spec.id], yr=(displayYears(spec.id,q)||'').replace(/^\(|\)$/g,'');
    d.innerHTML='<div class="pc-role">'+esc(spec.role||'')+'</div><div class="pc-n">'+esc(displayName(q))+'</div>'+
      (yr?'<div class="pc-y">'+esc(yr)+'</div>':'')+'<div class="pc-h">'+esc(houseShort(q._house)+(q.uid?' · ID '+q.uid:''))+'</div>';
    d.title='לחיצה — פתיחת הכרטיס'; d.onclick=()=>{ closeParents(); openPerson(spec.id); };
  } else {
    d.innerHTML='<div class="pc-role">'+esc(spec.role||'')+'</div><div class="pc-n">'+esc(spec.label||'')+'</div>'+(spec.sub?'<div class="pc-h">'+esc(spec.sub)+'</div>':'');
  }
  return d;
}
function showParents(id){
  const X=persons[id]; if(!X) return;
  const run=++_parRun;
  const modal=document.getElementById('parModal'), stage=document.getElementById('parStage'), status=document.getElementById('parStatus');
  document.getElementById('parTitle').textContent='ההורים והאחים של '+displayName(X);
  stage.innerHTML=''; stage.style.zoom=1; modal.classList.add('open');
  const fid=parentOf[id], F=(fid&&persons[fid])?persons[fid]:null;
  const M=motherPerson(X), mtxt=M?'':motherText(X), mk=motherKey(X);
  /* who is who */
  let full=[], halfF=[], halfM=[];
  if(F){
    const kids=(childMap[fid]||[]).slice().sort(byBirthIds), by={};
    kids.forEach(c=>{
      const k=motherKey(persons[c]);
      if(k===mk) full.push(c);
      else (by[k||'?']=by[k||'?']||{ids:[],label:''}).ids.push(c);
    });
    if(!full.includes(id)) full.push(id);
    Object.keys(by).forEach(k=>{ const g=by[k], p0=persons[g.ids[0]];
      g.label = k==='?' ? 'אם לא ידועה' : 'מאם אחרת: '+motherShort(p0); halfF.push(g); });
  } else full=[id];
  if(M){
    const by={};
    Object.values(persons).forEach(q=>{
      if(q.id===id || q.mother_id!==M.id) return;
      if(F && parentOf[q.id]===fid) return;                         // already a full sibling
      if(!F && !parentOf[q.id]){ if(!full.includes(q.id)) full.push(q.id); return; }
      const k=parentOf[q.id]||'?'; (by[k]=by[k]||{ids:[],label:''}).ids.push(q.id);
    });
    Object.keys(by).forEach(k=>{ const g=by[k]; g.label = k==='?' ? 'אב לא ידוע' : 'מאב אחר: '+givenOnly(persons[k].name); g.ids.sort(byBirthIds); halfM.push(g); });
  }
  /* geometry (physical px: mother on the left, father on the right) */
  const GG=28, PAD=24;
  const rowW=n=>n*PC_W+Math.max(0,n-1)*PC_GAP;
  const grpW=gs=>gs.reduce((s,g)=>s+rowW(g.ids.length),0)+Math.max(0,gs.length-1)*GG;
  const w0=rowW(full.length), wB=grpW(halfF), wC=grpW(halfM), hasHalf=halfF.length||halfM.length;
  let dx=PC_W/2+30;
  if(hasHalf) dx=Math.max(dx, w0/2+PC_W/2+30, (wB+wC)/4+20);
  const minX=Math.min(-dx-PC_W/2, -w0/2, -dx-wC/2, dx-wB/2), maxX=Math.max(dx+PC_W/2, w0/2, dx+wB/2, -dx+wC/2);
  const off=PAD-minX, W=maxX-minX+2*PAD;
  const y1=PAD+4, y2=y1+PC_H+84, y3=y2+PC_H+92, Hh=(hasHalf?y3+PC_H:y2+PC_H)+PAD;
  stage.style.width=W+'px'; stage.style.height=Hh+'px';
  const NS='http://www.w3.org/2000/svg';
  const svg=document.createElementNS(NS,'svg'); svg.setAttribute('width',W); svg.setAttribute('height',Hh); svg.setAttribute('class','par-svg'); stage.appendChild(svg);
  const COL={A:'#2e7d6b',B:'#c2722a',C:'#7a4f9e'};
  const paths=[];
  function mkPath(d,color,delayGroup){ const p=document.createElementNS(NS,'path'); p.setAttribute('d',d); p.setAttribute('fill','none'); p.setAttribute('stroke',color);
    p.setAttribute('stroke-width','3'); p.setAttribute('stroke-linecap','round'); p.setAttribute('stroke-linejoin','round'); p.setAttribute('pathLength','1');
    p.style.strokeDasharray='1'; p.style.strokeDashoffset='1'; svg.appendChild(p); return p; }
  function place(el,cx,y){ el.style.left=(off+cx-PC_W/2)+'px'; el.style.top=y+'px'; stage.appendChild(el); return el; }
  /* cards */
  const xm=-dx, xf=dx;
  const fCard=place(F?pcCard({id:fid,role:'האב'},'pcA'):pcCard({ghost:true,role:'האב',label:'האב אינו ידוע'},'pcA'), xf, y1);
  const mSpec = M ? {id:M.id,role:'האם'} : (mtxt ? {ghost:true,role:'האם',label:mtxt,sub:houseShort(X.mother_house)||'אינה רשומה בעץ'} : {ghost:true,role:'האם',label:'האם אינה ידועה'});
  const mCard=place(pcCard(mSpec,'pcA'), xm, y1);
  const sibCards=full.map((cid,i)=>place(pcCard({id:cid,role:cid===id?'האדם שנבחר':'אח/ות',self:cid===id},'pcA'), -w0/2+PC_W/2+i*(PC_W+PC_GAP), y2));
  const mid=(xm+xf)/2;
  const pMar=mkPath('M '+(off+xm+PC_W/2)+' '+(y1+PC_H/2)+' L '+(off+xf-PC_W/2)+' '+(y1+PC_H/2), COL.A);
  const busA=y2-34; let dA='M '+(off+mid)+' '+(y1+PC_H/2)+' L '+(off+mid)+' '+busA;
  const xs=full.map((_,i)=>-w0/2+PC_W/2+i*(PC_W+PC_GAP));
  dA+=' M '+(off+Math.min(...xs))+' '+busA+' L '+(off+Math.max(...xs))+' '+busA; xs.forEach(x=>{ dA+=' M '+(off+x)+' '+busA+' L '+(off+x)+' '+y2; });
  const pDropA=mkPath(dA,COL.A);
  function buildGroups(gs, cx, parentY, color, cls){
    if(!gs.length) return null;
    const tot=grpW(gs); let x0=cx-tot/2; const cards=[], labels=[]; const bus=y3-40;
    let d='M '+(off+cx)+' '+parentY+' L '+(off+cx)+' '+bus;
    gs.forEach(g=>{
      const w=rowW(g.ids.length), cs=[];
      g.ids.forEach((cid,i)=>{ const x=x0+PC_W/2+i*(PC_W+PC_GAP); cs.push(x); cards.push(place(pcCard({id:cid,role:'אח/ות למחצה'},cls),x,y3)); });
      d+=' M '+(off+Math.min(...cs))+' '+bus+' L '+(off+Math.max(...cs))+' '+bus; cs.forEach(x=>{ d+=' M '+(off+x)+' '+bus+' L '+(off+x)+' '+y3; });
      const lb=document.createElement('div'); lb.className='pc-gl'; lb.style.color=color; lb.textContent=g.label; lb.style.left=(off+x0)+'px'; lb.style.top=(y3-30)+'px'; lb.style.width=w+'px';
      stage.appendChild(lb); labels.push(lb); x0+=w+GG;
    });
    return {path:mkPath(d,color), cards, labels};
  }
  const gB=buildGroups(halfF, xf, y1+PC_H, COL.B, 'pcB');
  const gC=buildGroups(halfM, xm, y1+PC_H, COL.C, 'pcC');
  /* fit to the window width (phones) */
  const body=document.getElementById('parBody'); const z=Math.min(1,(body.clientWidth-8)/W); stage.style.zoom=z>0?z:1;
  /* animation */
  const RM=window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const sleep=ms=>new Promise(r=>setTimeout(r,RM?0:ms));
  const alive=()=>run===_parRun;
  const hide=els=>els.forEach(e=>{ if(e){ e.style.opacity='0'; } });
  hide([fCard,mCard,...sibCards]); paths.push(pMar,pDropA);
  if(gB){ hide(gB.cards); hide(gB.labels); } if(gC){ hide(gC.cards); hide(gC.labels); }
  const fadeIn=(el,from,ms)=>{ el.style.opacity='1'; if(!RM) el.animate([{opacity:0,transform:from},{opacity:1,transform:'none'}],{duration:ms,easing:'cubic-bezier(.2,.8,.2,1)'}); };
  const draw=(p,ms)=>{ p.style.strokeDashoffset='0'; if(!RM) p.animate([{strokeDashoffset:1},{strokeDashoffset:0}],{duration:ms,easing:'ease-in-out'}); };
  async function play(){
    status.textContent='מאתר את כרטיס האב…'; await sleep(250); if(!alive()) return;
    fadeIn(fCard,'translateX(260px) scale(.9)',800); await sleep(900); if(!alive()) return;
    status.textContent='מאתר את כרטיס האם…'; await sleep(150); if(!alive()) return;
    fadeIn(mCard,'translateX(-260px) scale(.9)',800); await sleep(950); if(!alive()) return;
    status.textContent='מצמיד את ההורים זה לזה…'; draw(pMar,550); await sleep(650); if(!alive()) return;
    status.textContent='משרטט את ילדיהם…'; draw(pDropA,700); await sleep(600); if(!alive()) return;
    for(const c of sibCards){ fadeIn(c,'translateY(-24px)',450); await sleep(160); if(!alive()) return; }
    if(gB||gC){
      await sleep(350); if(!alive()) return;
      status.textContent='אחים למחצה — מתחת לאב או לאם, בצבע אחר';
      for(const g of [gB,gC]){ if(!g) continue; draw(g.path,700); await sleep(550); if(!alive()) return;
        g.labels.forEach(l=>fadeIn(l,'translateY(-10px)',400));
        for(const c of g.cards){ fadeIn(c,'translateY(-24px)',450); await sleep(150); if(!alive()) return; } }
    }
    status.textContent=(M||mtxt?'':'האם אינה ידועה במקורות — האחים מוצגים לפי האב בלבד. ')+'לחיצה על כרטיס פותחת אותו.';
  }
  document.getElementById('parReplay').onclick=()=>showParents(id);
  play();
}
document.getElementById('parClose').onclick=closeParents;
document.getElementById('parModal').addEventListener('click',e=>{ if(e.target.id==='parModal') closeParents(); });
