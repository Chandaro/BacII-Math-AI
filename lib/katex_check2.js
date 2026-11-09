const fs=require('fs'),vm=require('vm');const ctx={window:{},document:undefined,console};ctx.self=ctx.window;ctx.globalThis=ctx;vm.createContext(ctx);vm.runInContext(fs.readFileSync('dataset/preview_assets/katex.min.js','utf8'),ctx);const katex=ctx.katex||ctx.window.katex;
const L=fs.readFileSync(process.argv[2],'utf8').trim().split('\n');let n=0,bad=[];
for(const l of L){const r=JSON.parse(l);for(const s of [r.problem_km,r.solution_km]){const re=/\$\$([\s\S]+?)\$\$|\$([^$]+?)\$/g;let m;while((m=re.exec(s))){n++;try{katex.renderToString(m[1]||m[2],{throwOnError:true,strict:false,displayMode:true})}catch(e){bad.push([r.id,(m[1]||m[2]).slice(0,90),e.message.slice(0,70)])}}}}
console.log('fragments',n,'bad',bad.length);bad.slice(0,10).forEach(b=>console.log(b.join(' | ')));
