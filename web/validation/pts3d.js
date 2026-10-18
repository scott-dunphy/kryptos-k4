// print local 3-D positions of chosen apertures from the page model, for both spacing modes
const fs=require('fs'); eval(fs.readFileSync(require('path').join(__dirname,'validate.js'),'utf8').split("// observed band")[0]);
const want=JSON.parse(process.argv[2]);
for(const mode of ["justify","pitch"]){UI.layout=mode; const aps=M.apertures(M.P,mode);
  console.log(mode, JSON.stringify(want.map(([r,i])=>{const a=aps.find(a=>a.face==="cipher"&&a.row===r&&a.i===i); const q=M.facePoint("cipher",a.u,a.v,M.P); return [a.ch,+q.x.toFixed(4),+q.y.toFixed(4),+q.z.toFixed(4)];})));}
