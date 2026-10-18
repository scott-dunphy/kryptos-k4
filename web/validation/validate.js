const fs=require('fs'); const s=fs.readFileSync(require('path').join(__dirname,'..','kryptos_sun_study.html'),'utf8');
class V{constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z}clone(){return new V(this.x,this.y,this.z)}addScaledVector(v,t){this.x+=v.x*t;this.y+=v.y*t;this.z+=v.z*t;return this}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this}negate(){this.x=-this.x;this.y=-this.y;this.z=-this.z;return this}length(){return Math.hypot(this.x,this.y,this.z)}normalize(){const l=this.length();this.x/=l;this.y/=l;this.z/=l;return this}
 applyAxisAngle(ax,a){const c=Math.cos(a),sn=Math.sin(a);const x=this.x*c+this.z*sn, z=-this.x*sn+this.z*c;this.x=x;this.z=z;return this}}
global.THREE={Vector3:V}; globalThis.UI={bulge:"1",layout:process.env.LAYOUT||"justify"}; global.document={getElementById:id=>({value:UI[id]})};
const grab=n=>{const i=s.indexOf("function "+n+"(");let d=0,j=s.indexOf("{",i);for(let k=j;k<s.length;k++){if(s[k]=="{")d++;if(s[k]=="}"){d--;if(!d)return s.slice(i,k+1)}}};
const pre=s.slice(s.indexOf("const LEFT="),s.indexOf("const P={};"));
eval("var $=id=>document.getElementById(id);var measured={};"+pre+"var P={};for(const k in DIMS)P[k]=DIMS[k].v;"+
 ["apertures","arcs","faceTheta","facePoint","faceUV","hitFace","hitCyl","inDisk","solar"].map(grab).join("\n")+
 "var rotY=th=>Math.PI-th*Math.PI/180; function sunLocal(az,el,h){const er=el*Math.PI/180,ar=az*Math.PI/180;return new V(Math.cos(er)*Math.sin(ar),Math.sin(er),-Math.cos(er)*Math.cos(ar)).applyAxisAngle(null,-rotY(h));}"+
 "globalThis.M={P,DIMS,apertures,facePoint,hitFace,hitCyl,solar,sunLocal};");

// observed band (row -> [lo,hi] column index, as read from the mirrored photo); null = no band in that row
const OBS={1:[11,17],2:[14,20],3:[14,20],4:[14,22],5:[15,25],6:[15,23],9:[14,26],11:[15,26],12:[20,29],15:[12,25],21:[22,30],22:[22,32],24:[27,30],25:[24,30],26:[22,30],27:[24,30]};
function blocker(o,S,p){ if(hitCyl(p.treeX,p.treeZ,p.treeR,p.treeH,o,S,1e-5)<Infinity)return "tree";
  for(const f of ["cipher","tableau"]) if(hitFace(f,o,S,p,1e-5)<Infinity)return f; return null;}
function predict(p,S){const out={}; for(const a of apertures(p,UI.layout)){ if(a.face!=="cipher")continue;
  const b=blocker(facePoint("cipher",a.u,a.v,p),S,p); (out[a.row]=out[a.row]||[]).push(b);} return out;}
function score(pred){ // fraction of observed band cells predicted tree-shadowed + fraction of non-band cells predicted not tree-shadowed, per observed row
  let tp=0,fn=0,tn=0,fp=0; for(const r in OBS){const [lo,hi]=OBS[r]; pred[r].forEach((b,i)=>{const inb=i>=lo&&i<=hi, sh=b==="tree"; if(inb&&sh)tp++; else if(inb)fn++; else if(sh)fp++; else tn++;});}
  return {tp,fn,fp,tn,recall:tp/(tp+fn),spec:tn/(tn+fp)};}
function show(pred,rows){for(const r of rows){const line=pred[r].map(b=>b==="tree"?"#":b==="cipher"?"c":b==="tableau"?"t":".").join(""); const o=OBS[r]?` obs ${OBS[r]}`:""; console.log(String(r).padStart(2),line,o);}}
const sun=solar("1999-10-27",14+23/60,-4); console.log("sun az %s el %s",sun.az.toFixed(1),sun.el.toFixed(1));
const S=sunLocal(sun.az,sun.el,M.P.heading); const pred=predict(M.P,S);
console.log("model at defaults (heading 140): # = tree shadow, c/t = own/other panel blocks the sun, . = lit"); show(pred,[...Array(28).keys()]);
console.log("score", JSON.stringify(score(pred)));
// how well can ANY heading / time offset explain it, holding geometry at defaults? (diagnostic, not a fit to keep)
let best=null; for(let h=100;h<=180;h+=2) for(let dm=-60;dm<=60;dm+=10){const sn=solar("1999-10-27",14+23/60+dm/60,-4); const sc=score(predict(M.P,sunLocal(sn.az,sn.el,h))); const f=sc.recall+sc.spec; if(!best||f>best.f)best={h,dm,f,sc};}
console.log("best heading/time over grid:", JSON.stringify(best));
