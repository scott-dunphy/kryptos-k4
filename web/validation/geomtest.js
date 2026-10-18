const fs=require('fs'); const s=fs.readFileSync(require('path').join(__dirname,'..','kryptos_sun_study.html'),'utf8');
class V{constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z}clone(){return new V(this.x,this.y,this.z)}addScaledVector(v,t){this.x+=v.x*t;this.y+=v.y*t;this.z+=v.z*t;return this}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this}negate(){this.x=-this.x;this.y=-this.y;this.z=-this.z;return this}length(){return Math.hypot(this.x,this.y,this.z)}normalize(){const l=this.length();this.x/=l;this.y/=l;this.z/=l;return this}}
global.THREE={Vector3:V}; global.document={getElementById:id=>({value:id==="bulge"?"1":"justify"})};
const grab=n=>{const i=s.indexOf("function "+n+"(");let d=0,j=s.indexOf("{",i);for(let k=j;k<s.length;k++){if(s[k]=="{")d++;if(s[k]=="}"){d--;if(!d)return s.slice(i,k+1)}}};
const DIMSsrc=s.slice(s.indexOf("const SRC={"),s.indexOf("const P={};"));
eval("var $=id=>document.getElementById(id);"+DIMSsrc+"var P={};for(const k in DIMS)P[k]=DIMS[k].v;"+["arcs","faceTheta","facePoint","faceUV","hitFace","hitCyl","inDisk","traceOut","sunReaches"].map(grab).join("\n")+
`
// 1. round trip
let err=0; for(const f of ["cipher","tableau"]) for(let u=0.05;u<1;u+=0.1){const q=facePoint(f,u,0.5,P); const uv=faceUV(f,q,P); err=Math.max(err,Math.abs(uv.u-u));}
console.log("uv round-trip max error", err.toExponential(2));
// 2. light from behind-left through cipher middle, travelling toward +x,-z... sun in front-left high
const o=facePoint("cipher",0.75,0.5,P); const S=new V(-0.5,0.6,0.62).normalize(); const D=S.clone().negate();
console.log("cipher u=.75: sun reaches", sunReaches(o,S,P,1e-5), "lands", JSON.stringify(traceOut(o,D,P,1e-5,0).surf), traceOut(o,D,P,1e-5,0).face||"");
// 3. a sun direction straight from the tableau side through cipher toward -x: aim ray through the tree
const o2=new V(-2.5,0.5,0); const toTree=new V(P.treeX-o2.x,0,P.treeZ-o2.z).normalize();
console.log("ray aimed at tree blocked:", !sunReaches(o2,toTree,P,1e-5));
// 4. tableau point, sun from front high: light passes into the tableau pocket (behind) -> ground expected
const o3=facePoint("tableau",0.5,0.3,P); const S3=new V(0,0.7,0.71).normalize();
const r3=traceOut(o3,S3.clone().negate(),P,1e-5,0); console.log("tableau u=.5 from front:", sunReaches(o3,S3,P,1e-5), r3.surf, r3.pt&&[r3.pt.x.toFixed(2),r3.pt.y.toFixed(2),r3.pt.z.toFixed(2)].join(","));
// 5. cipher point lit from behind (sun at -z): light goes to +z (front) and down; bubbling pool at (-1.52,0.6)?
const o4=facePoint("cipher",0.5,0.1,P); const S4=new V(0,0.5,-0.87).normalize(); const r4=traceOut(o4,S4.clone().negate(),P,1e-5,0);
console.log("cipher low, sun behind:", sunReaches(o4,S4,P,1e-5), r4.surf);
`);
// arc checks: endpoints, junction, arc length, faceUV round trip already covered
eval(["arcs","faceTheta","facePoint"].map(grab).join("\n")+`
const j1=facePoint("cipher",1,0,P), j2=facePoint("tableau",0,0,P), e1=facePoint("cipher",0,0,P), e2=facePoint("tableau",1,0,P);
let len=0,prev=facePoint("cipher",0,0,P); for(let i=1;i<=1000;i++){const q=facePoint("cipher",i/1000,0,P); len+=Math.hypot(q.x-prev.x,q.z-prev.z); prev=q;}
console.log("junction", j1.x.toFixed(4), j1.z.toFixed(4), j2.x.toFixed(4), j2.z.toFixed(4), "| ends x", e1.x.toFixed(2), e2.x.toFixed(2), "| cipher arc length", len.toFixed(3), "| mid z", facePoint("cipher",0.5,0,P).z.toFixed(2), facePoint("tableau",0.5,0,P).z.toFixed(2));`);
