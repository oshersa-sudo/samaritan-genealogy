# -*- coding: utf-8 -*-
# 2026-11-09 — owner's request:
#   (1) where a father has children by different mothers, the tree lays the children out grouped by mother
#       (all the children of the first mother, then of the second …), each group by age;
#   (2) everywhere else, the card header carries the child's number among the father's children, by age («ילד 2»).
#       (not where the children are separated by mother — there the mother's name is shown instead).
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
T = io.open('genealogy_template.html', encoding='utf-8').read()
if 'orderKids' in T:
    print('already patched'); sys.exit()


def rep(old, new, count=1):
    global T
    assert T.count(old) == count, (T.count(old), old[:80])
    T = T.replace(old, new)


rep("function motherShort(p){", """// children of one father, in tree order: by age; when the mothers differ — grouped by mother (the order of the father's wives, else by the eldest child of each)
function orderKids(fid, ids){
  const kids=ids.slice().sort(byBirthIds);
  if(!fid || !persons[fid] || persons[fid].sex==='F' || kids.length<2) return kids;     // (a woman registered as the parent IS the mother)
  const key={}; kids.forEach(c=>{ key[c]=momKey2(persons[c]); });
  if(new Set(kids.map(c=>key[c]).filter(Boolean)).size<2) return kids;
  const sps=persons[fid].spouses||[];
  function wifeIndex(c){
    const p=persons[c], mid=p.mother_id;
    for(let i=0;i<sps.length;i++){
      if(mid && spouseTargetId(sps[i])===mid) return i;
      const t=motherText(p);
      if(!mid && t){
        const sn=norm(givenOnly(sps[i].name||'')), tn=norm(givenOnly(t));
        if(sn && sn===tn) return i;
        if(/^אשה/.test(t) && /ראשונ/.test(t) && /^אשה/.test(sps[i].name||'') && /ראשונ/.test(sps[i].name||'')) return i;
        if(/^אשה/.test(t) && /שניי/.test(t) && /שניי/.test(sps[i].name||'')) return i;
      }
    }
    return -1;
  }
  const groups=[], idx=new Map();
  kids.forEach(c=>{ const k=key[c]||'?'; if(!idx.has(k)){ idx.set(k,groups.length); groups.push({k,ids:[],w:wifeIndex(c)}); } groups[idx.get(k)].ids.push(c); });
  const useWives=groups.every(g=>g.k==='?'||g.w>=0);
  groups.forEach(g=>{ g.b=Math.min(...g.ids.map(birthSortKey)); });
  groups.sort((a,b)=>{ if(a.k==='?') return 1; if(b.k==='?') return -1;          // the mother of the eldest child first; equal/unknown ages -> the order of the wives
    const unk=a.b>=99999 || b.b>=99999;                                            // an unknown age cannot order two mothers — the wives' order does
    return (unk && useWives) ? (a.w-b.w) : ((a.b-b.b) || (useWives ? (a.w-b.w) : 0)); });
  return [].concat(...groups.map(g=>g.ids));
}
// the child's number among the father's children, by age (not shown where the children are split by mother — the mother's name is shown instead)
function kidOrdinal(id){
  const f=parentOf[id]; if(!f || !persons[f] || halfMomInfo(id)) return null;
  const sibs=(childMap[f]||[]).filter(c=>persons[c]); if(sibs.length<2) return null;
  const ord=sibs.slice().sort(byBirthIds), n=ord.indexOf(id)+1; if(!n) return null;
  const exact=sibs.every(c=>birthSortKey(c)<99999);
  return {n, exact, text:'ילד '+(exact?'':'≈')+n, full:'הילד ה-'+n+' מתוך '+sibs.length+' ילדי האב, לפי הגילאים'+(exact?'':' (לחלק מהאחים אין שנת לידה — הסדר משוער)')};
}
function motherShort(p){""")
rep("  return (childMap[id]||[]).slice().sort(byBirthIds);\n}\nfunction uChildren(id)", "  return orderKids(id, childMap[id]||[]);\n}\nfunction uChildren(id)")
rep("    (childMap[id]||[]).slice().sort(byBirthIds).forEach(c=>rec(c,depth+1));", "    orderKids(id, childMap[id]||[]).forEach(c=>rec(c,depth+1));")
rep("""    '<div class="nb-gen">דור '+gen+'</div>'+""", """    '<div class="nb-gen"'+(ko?' title="'+esc(ko.full)+'"':'')+'>דור '+gen+(ko?' · '+ko.text:'')+'</div>'+""")
rep("  const gen=genOf(id);\n  const story=", "  const gen=genOf(id), ko=kidOrdinal(id);\n  const story=")
io.open('genealogy_template.html', 'w', encoding='utf-8').write(T)
# the exported picture uses the same order and the same number
J = io.open('image_share_feature.js', encoding='utf-8').read()
a = "const ks=(d+1<maxGen)?(childMap[id]||[]).slice().sort(byBirthIds).filter(c=>!seen.has(c)&&persons[c]):[];"
assert J.count(a) == 1
J = J.replace(a, "const ks=(d+1<maxGen)?orderKids(id, childMap[id]||[]).filter(c=>!seen.has(c)&&persons[c]):[];")
io.open('image_share_feature.js', 'w', encoding='utf-8').write(J)
T = io.open('genealogy_template.html', encoding='utf-8').read()
assert T.count(a) == 1
T = T.replace(a, "const ks=(d+1<maxGen)?orderKids(id, childMap[id]||[]).filter(c=>!seen.has(c)&&persons[c]):[];")
rep("    { const hm=halfMomInfo(id); if(hm){ c.save();", "    { const ko=kidOrdinal(id); if(ko){ c.save(); c.font='9px \"Segoe UI\",\"Arial Hebrew\",Arial,sans-serif'; c.fillStyle='#8a8478'; c.textAlign='left'; c.fillText(ko.text,x+4,y+11); c.restore(); } }\n    { const hm=halfMomInfo(id); if(hm){ c.save();")
io.open('genealogy_template.html', 'w', encoding='utf-8').write(T)
print('patched')
