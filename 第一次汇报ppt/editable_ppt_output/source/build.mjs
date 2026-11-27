// 使用 Artifact Tool 生成原生文本、框体、线条和自由曲线，继承原模板。
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';
const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.dirname(dir);
const scenes=JSON.parse(await fs.readFile(path.join(dir,'scenes.json'),'utf8'));
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(root,'source','template.pptx')));
const originals=[...p.slides.items];
const k=1280/1672;
const pos=e=>({left:e.x*k,top:e.y*k,width:e.w*k,height:e.h*k,...(e.rotation?{rotation:e.rotation}:{})});
const ln=(fill,width=1)=>({style:'solid',fill,width:width*k});
const slides=[];
for(const scene of scenes){
 const slide=originals[scene.key==='cover'?0:1].duplicate();
 for(const sh of slide.shapes.items) sh.text='';
 for(const e of scene.elements){
  if(e.kind==='shape'){
   slide.shapes.add({geometry:e.geom,name:e.name,position:pos(e),fill:e.fill,line:ln(e.stroke,e.sw),...(e.r?{borderRadius:e.r*k}:{})});
  }else if(e.kind==='text'){
   const s=slide.shapes.add({geometry:'textbox',name:e.name,position:pos(e),fill:'none',line:ln('none',0)});
   s.text=e.text;s.text.style={typeface:'Microsoft YaHei',fontSize:e.size*k,bold:e.bold,color:e.color,alignment:e.align,verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:0};
   for(const em of e.emphasis||[]){const range=s.text.get(em.text);range.bold=em.bold;range.fill=em.color;}
  }else if(e.kind==='image'){
   const b=await fs.readFile(path.join(root,'assets',e.file));
   slide.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',alt:e.name,position:pos(e),fit:'contain'});
  }else if(e.kind==='line'){
   const x=Math.min(e.x,e.x2),y=Math.min(e.y,e.y2),w=Math.max(Math.abs(e.x2-e.x),.05),h=Math.max(Math.abs(e.y2-e.y),.05);
   const commands=[{moveTo:{x:(e.x-x)*k,y:(e.y-y)*k}},{lineTo:{x:(e.x2-x)*k,y:(e.y2-y)*k}}];
   slide.shapes.add({geometry:'custom',name:e.name,position:{left:x*k,top:y*k,width:w*k,height:h*k},fill:'none',line:{...ln(e.color,e.sw),style:e.dash?'dash':'solid'},customPaths:[{width:w*k,height:h*k,commands}]});
   if(e.arrow){const dx=e.x2-e.x,dy=e.y2-e.y,L=Math.hypot(dx,dy),ux=dx/L,uy=dy/L,a=10,b=5;const pts=[[e.x2,e.y2],[e.x2-ux*a-uy*b,e.y2-uy*a+ux*b],[e.x2-ux*a+uy*b,e.y2-uy*a-ux*b]];addPath(slide,pts,'none',0,e.color,true,'箭头端点');}
  }else if(e.kind==='path')addPath(slide,e.points,e.color,e.sw,e.fill,e.closed,e.name);
  else if(e.kind==='icon'){
   const commands=[];
   for(const pts of e.paths){commands.push({moveTo:{x:pts[0][0],y:pts[0][1]}});for(const pt of pts.slice(1))commands.push({lineTo:{x:pt[0],y:pt[1]}});commands.push({close:{}});}
   if(commands.length)slide.shapes.add({geometry:'custom',name:e.name,position:pos(e),fill:e.fill,line:ln('none',0),customPaths:[{width:e.vw,height:e.vh,commands}]});
  }
 }
 slides.push(slide);
 console.log('已生成',scene.source,scene.elements.length);
}
function addPath(slide,pts,color,sw,fill,closed,name){
 const xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]);const x=Math.min(...xs),y=Math.min(...ys),w=Math.max(...xs)-x||.05,h=Math.max(...ys)-y||.05;
 const commands=[{moveTo:{x:(pts[0][0]-x)*k,y:(pts[0][1]-y)*k}},...pts.slice(1).map(a=>({lineTo:{x:(a[0]-x)*k,y:(a[1]-y)*k}})),...(closed?[{close:{}}]:[])];
 slide.shapes.add({geometry:'custom',name,position:{left:x*k,top:y*k,width:w*k,height:h*k},fill,line:ln(color,sw),customPaths:[{width:w*k,height:h*k,commands}]});
}
const current=await p.inspect({kind:'slide',maxChars:30000});
const records=current.records||current.ndjson.split('\n').filter(Boolean).map(x=>JSON.parse(x));
const indices=slides.map(s=>p.slides.items.indexOf(s));
// 复制接口可能返回新包装对象，按实际原始标识定位。
const order=slides.map(s=>{const idx=p.slides.items.findIndex(v=>v.id===s.id);return records.find(r=>r.kind==='slide'&&r.slideIndex===idx).id;});
p.slides.keep(order);
p.slides.reorder(order);
await (await PresentationFile.exportPptx(p)).save(path.join(root,'.build','all_raw.pptx'));
console.log('汇总原生稿已写入');
