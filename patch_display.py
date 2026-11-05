# -*- coding: utf-8 -*-
# One-off patch of genealogy_template.html (2026-11-06, owner request):
#  * Hijri years -> approximate Gregorian everywhere (marked with ≈)
#  * age: at death (death - birth) or, when no death is known, the current age (computed on every load)
#  * zodiac sign for people with an exact birth date
#  * under every name, in parentheses:  «name בן/בת father בן grandfather»
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
P = 'genealogy_template.html'
s = io.open(P, encoding='utf-8', newline='').read().replace('\r\n', '\n')


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)


# ---------------------------------------------------------------- css
rep(".node-box{position:absolute; width:124px; height:56px;", ".node-box{position:absolute; width:124px; height:70px;")
rep("border:1.5px solid var(--line); border-radius:9px; padding:3px 6px; cursor:pointer;", "border:1.5px solid var(--line); border-radius:9px; padding:15px 6px 3px; cursor:pointer;")
rep("  .node-box .nb-name{font-size:13px; font-weight:700; line-height:1.15; margin-top:7px; color:var(--ink)}", "  .node-box .nb-name{font-size:13px; font-weight:700; line-height:1.15; margin-top:0; color:var(--ink)}")
rep("const NODE_W=124, NODE_H=56, COL_W=150, ROW_H=120,", "const NODE_W=124, NODE_H=70, COL_W=150, ROW_H=126,")

# ---------------------------------------------------------------- year helpers
rep("function gregApprox(y){ const n=numYear(y); return n? (n+584) : null; }",
    "function hij2greg(h){ const n=numYear(h); return n? Math.round(n*0.970229+621.574) : null; }   // Hijri -> Gregorian, ±1\n"
    "function gregApprox(y){ return hij2greg(y); }")
rep("""  const bs=b!=null?b:'', ds=d!=null?d:'';
  return '('+bs+(d!=null||b!=null?'–':'')+ds+')';
}""", """  const bs=b!=null?'≈'+hij2greg(b):'', ds=d!=null?'≈'+hij2greg(d):'';     // Hijri census years shown as approximate Gregorian
  return '('+bs+'–'+ds+')';
}""")

helpers = r'''
/* ---------- age, zodiac and the «name בן father בן grandfather» line ---------- */
function parseYearPart(t){ const m=(t||'').toString().match(/\d{3,4}/); return m?parseInt(m[0]):null; }
function lifeData(id){
  const p=persons[id]; if(!p) return null;
  const parts=(gregOf(id)||'').split('–');
  let by=parseYearPart(parts[0]), dy=parseYearPart(parts[1]), bA=false, dA=false;
  if(by==null){ const n=numYear(p.byear); if(n!=null) by=n; }
  if(dy==null){ const n=numYear(p.dyear); if(n!=null) dy=n; }
  if(by==null && numYear(p.birth)!=null){ by=hij2greg(p.birth); bA=true; }
  if(dy==null && numYear(p.death)!=null){ dy=hij2greg(p.death); dA=true; }
  let bm=null, bd=null;
  if(p.bmonth && p.bday && !p.bamb){ bm=+p.bmonth; bd=+p.bday; }
  else if(p.bdate){
    const t=(''+p.bdate).trim(); let m=t.match(/^(\d{1,2})[.\/-](\d{1,2})[.\/-](\d{4})$/);
    if(m){ bd=+m[1]; bm=+m[2]; if(bm>12 && bd<=12){ const x=bm; bm=bd; bd=x; } }
    else { m=t.match(/^(\d{4})[.\/-](\d{1,2})[.\/-](\d{1,2})$/); if(m){ bm=+m[2]; bd=+m[3]; } }
  }
  if(bm && (bm<1||bm>12||bd<1||bd>31)){ bm=null; bd=null; }
  return {by,dy,bA,dA,bm,bd};
}
function ageInfo(id){
  const L=lifeData(id); if(!L||L.by==null) return null;
  if(L.dy!=null){ const a=L.dy-L.by; return (a>=0&&a<=125)?{n:a,kind:'death',approx:L.bA||L.dA}:null; }
  const now=new Date(); let a=now.getFullYear()-L.by;       // recomputed every time the app is opened / re-rendered
  const exact=!!(L.bm&&L.bd&&!L.bA);
  if(exact && ((now.getMonth()+1)<L.bm || ((now.getMonth()+1)===L.bm && now.getDate()<L.bd))) a--;
  if(a<0||a>110) return null;                                // no death date but implausibly old: presumably deceased
  return {n:a,kind:'now',approx:!exact};
}
const ZOD_START=[[1,20,'דלי','♒'],[2,19,'דגים','♓'],[3,21,'טלה','♈'],[4,20,'שור','♉'],[5,21,'תאומים','♊'],[6,21,'סרטן','♋'],
                 [7,23,'אריה','♌'],[8,23,'בתולה','♍'],[9,23,'מאזניים','♎'],[10,23,'עקרב','♏'],[11,22,'קשת','♐'],[12,22,'גדי','♑']];
function zodiacOf(id){
  const L=lifeData(id); if(!L||!L.bm||!L.bd||L.bA) return null;
  let z=['גדי','♑'];
  ZOD_START.forEach(r=>{ if(L.bm>r[0] || (L.bm===r[0] && L.bd>=r[1])) z=[r[2],r[3]]; });
  return {name:z[0],sym:z[1]};
}
function ageText(a){ return a? ('גיל '+(a.approx?'≈':'')+a.n+(a.kind==='now'?' כיום':' בפטירה')) : ''; }
function metaLine(id){
  const a=ageInfo(id), z=zodiacOf(id), out=[];
  if(a) out.push(a.kind==='now' ? ('גיל '+(a.approx?'≈':'')+a.n+' כיום') : ('גיל '+(a.approx?'≈':'')+a.n));
  if(z) out.push(z.sym+' '+z.name);
  return out.join(' · ');
}
function givenOnly(n){
  n=(n||'').replace(/\s*[\(（].*$/,'').replace(/\s*=\s*.*$/,'').replace(/[\[\]]/g,'').trim();
  return (n.split(/\s+/)[0]||'');
}
function chainLine(p){
  if(!p) return '';
  const fid=parentOf[p.id];
  let father='', gf='';
  if(fid && persons[fid]){ father=givenOnly(persons[fid].name); const gid=parentOf[fid]; if(gid && persons[gid]) gf=givenOnly(persons[gid].name); else if(persons[fid].father) gf=givenOnly(persons[fid].father); }
  else if(p.father){ father=givenOnly(p.father); }
  if(!father) return '';
  const own=givenOnly(p.name)||'(ללא שם)';
  return '('+own+' '+(p.sex==='F'?'בת':'בן')+' '+father+(gf?' בן '+gf:'')+')';
}
'''
rep("function fatherNameOf(p){", helpers + "function fatherNameOf(p){")

# ---------------------------------------------------------------- tree card
rep("  const ys=displayYears(id,p);\n  const sexMark=", "  const ys0=displayYears(id,p), ai0=ageInfo(id), ys=ys0+(ai0? (ys0?' · ':'')+(ai0.kind==='now'?'גיל '+(ai0.approx?'≈':'')+ai0.n+' כיום':'גיל '+(ai0.approx?'≈':'')+ai0.n):'');\n  const sexMark=")

# ---------------------------------------------------------------- panel
rep("  pSub.textContent=p._house.replace(/^[א-ת]\\.\\s*/,'')+' · '+p._family;",
    "  { const chn=chainLine(p); pSub.innerHTML=(chn?'<div>'+esc(chn)+'</div>':'')+esc(p._house.replace(/^[א-ת]\\.\\s*/,'')+' · '+p._family); }")
rep("  // modern registry details (exact birth date, occupation, birthplace)",
    "  { const ai=ageInfo(id), zz=zodiacOf(id), bits=[];\n"
    "    if(ai) bits.push(ai.kind==='now' ? 'גיל כיום: '+(ai.approx?'≈':'')+ai.n+(ai.approx?' <span class=\"years\">(לפי שנת לידה בלבד)</span>':'') : 'גיל בפטירה: '+(ai.approx?'≈':'')+ai.n);\n"
    "    if(zz) bits.push('מזל: '+zz.sym+' '+zz.name);\n"
    "    if(bits.length) html+=field('גיל ומזל', bits.join(' · ')); }\n"
    "  // modern registry details (exact birth date, occupation, birthplace)")

# ---------------------------------------------------------------- management table: Hijri-only dates shown as approximate Gregorian (display only; export/edit untouched)
rep("function mgmtRowHTML(p){", "function mgShow(p,k){ let v=mgGet(p,k); if((v===''||v==null) && (k==='birth'||k==='death')){ const h=(k==='birth')?p.birth:p.death; const g=hij2greg(h); if(g) v='≈'+g; } return v; }\nfunction mgmtRowHTML(p){")
rep("  MGMT_FIELDS.forEach(f=>{ h+='<td>'+esc(mgGet(p,f.k))+'</td>'; });\n  h+='<td class=\"acts\">'+",
    "  MGMT_FIELDS.forEach(f=>{ h+='<td>'+esc(mgShow(p,f.k))+'</td>'; });\n  h+='<td class=\"acts\">'+")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('patched')
