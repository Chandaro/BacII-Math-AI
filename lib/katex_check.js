const katex=require(require('path').join(__dirname,'..','dataset','preview_assets','katex.min.js')),fs=require('fs');
const lines=fs.readFileSync(process.argv[2],'utf8').trim().split('\n');
let n=0,bad=[],badRows=new Set();
function t(id,s){n++;try{katex.renderToString(s,{throwOnError:true,strict:false,displayMode:true})}catch(e){bad.push([id,s.slice(0,100),e.message.slice(0,90)]);badRows.add(id)}}
for(const l of lines){const r=JSON.parse(l);
 for(const f of ['problem_km','solution_km']){const x=r[f];const re=/\$\$([\s\S]+?)\$\$|\$([^$]+?)\$/g;let m;while((m=re.exec(x)))t(r.id,m[1]||m[2]);}
 t(r.id,r.answer_latex);
 for(const d of r.diagrams) if(d.type!=='graph'&&d.type!=='figure'&&d.latex&&!d.latex.includes('tikzpicture')) t(r.id,d.latex);}
fs.writeFileSync(process.argv[3],[...badRows].join('\n'));
console.log('fragments',n,'bad',bad.length,'rows',badRows.size);const c={};for(const b of bad){const k=b[2].replace(/ at position.*/,"").slice(0,70);(c[k]=c[k]||[]).push(b[1])}for(const k in c)console.log(c[k].length,k,"|",c[k][0]);
