const { chromium } = require('playwright');
const fs=require('fs');const http=require('http');const path=require('path');
const ROOT=__dirname;
const mime={'.html':'text/html','.js':'text/javascript','.otf':'font/otf'};
const srv=http.createServer((q,r)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);r.end();return}r.writeHead(200,{'Content-Type':mime[path.extname(f)]||'application/octet-stream'});r.end(d)})});
const [,,mode,a,b,out,step]=process.argv; // mode: stills "t1,t2" outdir | range f0 f1 outdir
srv.listen(0,async()=>{
 const port=srv.address().port;
 const br=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
 const p=await br.newPage({viewport:{width:1080,height:1920}});
 p.on('console',m=>{if(m.type()==='error')console.log('PAGE:',m.text())});p.on('pageerror',e=>console.log('ERR:',e.message));
 await p.goto(`http://localhost:${port}/scene.html`);await p.waitForFunction('window.ready===true',null,{timeout:120000});
 await p.evaluate(()=>document.fonts.ready);
 const words=JSON.parse(fs.readFileSync(ROOT+'/../audio/words.json')).words;
 await p.evaluate(w=>window.setWords(w),words);
 fs.mkdirSync(out||a,{recursive:true});
 const shot=async(t,file)=>{await p.evaluate(t=>window.renderAt(t),t);await p.screenshot({path:file,type:'jpeg',quality:94});};
 if(mode==='stills'){for(const t of a.split(',').map(Number)){const s=Date.now();await shot(t,`${b}/s_${t.toFixed(2)}.jpg`);console.log(t,Date.now()-s,'ms')}}
 else {const f0=+a,f1=+b,fps=+(step||30);for(let f=f0;f<f1;f++){await shot(f/fps,`${out}/f_${String(f).padStart(5,'0')}.jpg`);if(f%30==0)console.log('frame',f,new Date().toISOString())}}
 await br.close();srv.close();
});
