// 以当前汇总稿的编辑副本为基础，更新八页原生内容并保留模板。
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';
const ROOT=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const D=JSON.parse(await fs.readFile(path.join(ROOT,'source/data.json'),'utf8'));
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(ROOT,'.build/edit_base.pptx')));
const C={red:'#CA1420',navy:'#20364D',blue:'#266CA7',teal:'#227F7D',orange:'#AA651F',gray:'#566575',light:'#EDF2F6',border:'#CCD6DF',white:'#FFFFFF',ink:'#273647'};
const F='Microsoft YaHei';
let slide,seq=0;
const manifest=[];
function box(name,x,y,w,h,fill=C.white,stroke=C.border,r=7){return slide.shapes.add({geometry:r?'roundRect':'rect',name,position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,style:'solid',width:stroke==='none'?0:1},...(r?{borderRadius:r}:{})});}
function txt(name,text,x,y,w,h,size=24,color=C.ink,bold=false,align='left'){
 const s=box(name,x,y,w,h,'none','none',0);s.text=String(text);s.text.style={typeface:F,fontSize:size,bold,color,alignment:align,verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:0};return s;
}
function line(name,x1,y1,x2,y2,color=C.navy,width=2,dash=false,arrow=false,both=false){
 const x=Math.min(x1,x2),y=Math.min(y1,y2),w=Math.max(Math.abs(x2-x1),.05),h=Math.max(Math.abs(y2-y1),.05);
 slide.shapes.add({geometry:'custom',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:color,width,style:dash?'dash':'solid'},customPaths:[{width:w,height:h,commands:[{moveTo:{x:x1-x,y:y1-y}},{lineTo:{x:x2-x,y:y2-y}}]}]});
 function tip(a,b,c,d){const ang=Math.atan2(d-b,c-a),len=8;poly(name+'_箭头',[[c,d],[c-len*Math.cos(ang)-4*Math.sin(ang),d-len*Math.sin(ang)+4*Math.cos(ang)],[c-len*Math.cos(ang)+4*Math.sin(ang),d-len*Math.sin(ang)-4*Math.cos(ang)]],color,color,0,true);}
 if(arrow)tip(x1,y1,x2,y2);if(both)tip(x2,y2,x1,y1);
}
function poly(name,pts,color=C.navy,fill='none',width=2,closed=false){
 const xs=pts.map(a=>a[0]),ys=pts.map(a=>a[1]),x=Math.min(...xs),y=Math.min(...ys),w=Math.max(...xs)-x||.05,h=Math.max(...ys)-y||.05;
 const commands=[{moveTo:{x:pts[0][0]-x,y:pts[0][1]-y}},...pts.slice(1).map(a=>({lineTo:{x:a[0]-x,y:a[1]-y}})),...(closed?[{close:{}}]:[])];
 slide.shapes.add({geometry:'custom',name,position:{left:x,top:y,width:w,height:h},fill,line:{fill:color,width,style:'solid'},customPaths:[{width:w,height:h,commands}]});
}
function dot(name,x,y,r,color){slide.shapes.add({geometry:'ellipse',name,position:{left:x-r,top:y-r,width:r*2,height:r*2},fill:color,line:{fill:color,width:0}});}
async function pic(file,x,y,w,h,name){const b=await fs.readFile(path.join(ROOT,'assets',file));slide.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',alt:name,position:{left:x,top:y,width:w,height:h},fit:'contain'});}
function title(text){txt('页面标题',text,112.9,4.58,1010,62.83,42.6667,C.white,true);}
function note(text){slide.speakerNotes.text=text;}
function header(n,t){slide=p.slides.items[n-1];seq=n;title(t);}
function band(text,y=578,h=44,size=24){box('阶段结论',54,y,1172,h,C.light,'none');txt('阶段结论文本',text,72,y+4,1136,h-8,size,C.navy,true,'center');}
function label(t,x,y,w,color=C.teal){box('状态_'+t,x,y,w,28,color,'none',4);txt('状态文字_'+t,t,x,y,w,28,18,C.white,true,'center');}
function icon(kind,x,y,s=64,color=C.navy){
 const L=(a,b,c,d)=>line('图标_'+kind,x+a*s,y+b*s,x+c*s,y+d*s,color,2);
 if(kind==='图纸'){box('图纸轮廓',x,y,s*.85,s,'none',color,0);for(let i=1;i<=3;i++)L(.15,i*.22,.7,i*.22);L(.45,0,.45,1);}
 else if(kind==='舱室'){box('舱室图标',x,y,s,s*.7,'none',color,0);for(let i=1;i<4;i++)L(i*.25,0,i*.25,.7);L(0,.35,1,.35);}
 else if(kind==='文档'){poly('文件图标',[[x,y],[x+s*.65,y],[x+s*.88,y+s*.25],[x+s*.88,y+s],[x,y+s]],color,'none',2,true);L(.15,.4,.7,.4);L(.15,.58,.7,.58);L(.15,.76,.55,.76);}
 else if(kind==='模型'){poly('模型图标',[[x,y+s*.25],[x+s*.7,y],[x+s,y+s*.3],[x+s*.3,y+s*.6],[x,y+s*.25]],color,'none',2);poly('模型侧面',[[x,y+s*.25],[x,y+s*.65],[x+s*.3,y+s],[x+s,y+s*.7],[x+s,y+s*.3]],color);L(.3,.6,.3,1);}
 else if(kind==='重量'){L(.5,0,.5,.9);L(.1,.28,.9,.28);L(.1,.28,.1,.65);L(.9,.28,.9,.65);L(.0,.65,.2,.65);L(.8,.65,1,.65);L(.25,.9,.75,.9);}
 else if(kind==='性能'){L(0,0,0,.85);L(0,.85,1,.85);poly('趋势图标',[[x+s*.05,y+s*.7],[x+s*.35,y+s*.57],[x+s*.65,y+s*.3],[x+s*.94,y+s*.06]],color);}
 else if(kind==='推进'){dot('桨毂',x+s/2,y+s/2,s*.1,color);for(let a=0;a<3;a++){const t=a*2*Math.PI/3;poly('桨叶',[[x+s*.5,y+s*.5],[x+s*.5+s*.45*Math.cos(t),y+s*.5+s*.45*Math.sin(t)],[x+s*.5+s*.33*Math.cos(t+.65),y+s*.5+s*.33*Math.sin(t+.65)]],color,'none',2,true);}}
 else{box('接口图标',x,y,s,s*.7,'none',color,0);L(.2,.2,.8,.2);L(.2,.45,.65,.45);}
}
function shipOutline(x,y,w,h){poly('船体示意非成果',[[x,y+h*.25],[x+w*.8,y+h*.25],[x+w,y],[x+w*.91,y+h*.8],[x+w*.15,y+h*.8],[x,y+h*.25]],C.blue,'none',2);line('水线示意',x-5,y+h*.61,x+w+8,y+h*.61,C.border,1);}
function miniCurve(x,y,w,h){const xx=v=>x+(v-11)/5*w,yy=r=>y+h-(r-200)/550*h;for(let i=1;i<D.curve.length;i++)line('实际阻力缩略线',xx(D.curve[i-1].V),yy(D.curve[i-1].RT),xx(D.curve[i].V),yy(D.curve[i].RT),C.blue,2.4);line('缩略横轴',x,y+h,x+w,y+h,C.gray,1);line('缩略纵轴',x,y,x,y+h,C.gray,1);}

// 第一页：模板构图及学校元素全部继承。
slide=p.slides.items[0];
txt('课程名称','船舶设计Ⅱ课程设计',210,191,860,50,36,C.navy,true,'center');
txt('封面主标题','第一次汇报',200,247,880,82,66,C.red,true,'center');
txt('封面设计对象',`B组｜33,500 DWT 灵便型散货船母型改造设计`,180,368,920,46,29,C.navy,true,'center');
txt('封面汇报人','汇报人：董昱彤（组长）',200,451,880,44,32,C.navy,true,'center');
txt('封面组员','组员：林森崎｜王弘毅｜孟也然',200,505,880,38,27,C.navy,false,'center');
txt('封面日期','2026 年 11 月',200,567,880,38,26,C.gray,false,'center');
note('建议用时15秒。B组以35000 DWT母型建立33500 t目标船初步方案。本次汇报聚焦已有的总体设计和型线建模成果，以及下一阶段的专业协同。来源：课程设计指导书§1、完善任务规划。封面学校元素继承ppt模板.pptx。');

// 第二页：合并任务与路线，不增加单独的任务页。
header(2,'设计任务与总体设计路线');
box('母型方案',54,103,355,159);box('改造方法',463,103,354,159,C.light);box('目标方案',871,103,355,159);
txt('母型标题','35000 DWT 母型船',72,114,320,38,32,C.navy,true,'center');
txt('母型依据','课程提供参考母型',72,154,320,29,22,C.gray,false,'center');shipOutline(100,198,255,42);
txt('方法标题','母型改造法',480,114,320,38,32,C.navy,true,'center');
txt('缩放说明','几何相似 / 参数调整',480,157,320,29,23,C.gray,false,'center');
txt('比例值',`k = ${D.k.toFixed(6)}`,480,202,320,40,34,C.red,true,'center');
txt('目标标题',`${D.DWT} t 目标船`,889,114,319,38,32,C.navy,true,'center');
txt('目标依据','B组设计任务',889,154,319,29,22,C.gray,false,'center');shipOutline(919,198,255,42);
line('母型至改造',415,182,453,182,C.navy,3,false,true);line('改造至目标',823,182,861,182,C.navy,3,false,true);
const metrics=[[`${D.DWT} t`,'目标载重量'],['14 kn','设计服务航速'],['16000 n mile','续航力'],['5 个','货舱'],['4 × 30 t','起重机 / SWL']];
metrics.forEach(([v,t],i)=>{const x=54+i*238;box('任务指标_'+t,x,283,220,100,C.white);txt('指标数值_'+t,v,x+8,294,204,44,i===2?30:36,C.red,true,'center');txt('指标名称_'+t,t,x+8,343,204,27,23,C.navy,false,'center');});
txt('船型要求','钢质、单机单桨、尾机型双壳散货船',55,399,760,31,24,C.navy);
txt('航区铺位','国际无限航区　　25 人铺位',790,399,436,31,23,C.navy,false,'right');
txt('任务性质','以上为课程任务要求；30 t 为起重机安全工作负荷。两端船体线稿仅示意改造逻辑。',55,438,1170,27,18,C.gray);
const steps=[['主尺度','图纸'],['型线 / 模型','模型'],['静水力','性能'],['总布置 / 舱容','舱室'],['重量浮力','重量'],['稳性','性能'],['快速性 / 推进','推进'],['能效与成本','文档']];
steps.forEach(([t,k],i)=>{const x=54+i*149;box('路线_'+t,x,492,129,91,i<2?'#E7EFF6':C.white);icon(k,x+51,502,27,C.navy);txt('路线文字_'+t,t.includes(' / ')?t.split(' / ').join('\n'):t,x+4,532,121,48,t.includes(' / ')?19:23,C.navy,true,'center');if(i<7)line('路线箭头_'+i,x+132,536,x+145,536,C.navy,1.8,false,true);});
txt('路线总结','以母型改造为起点，通过多专业迭代形成完整设计方案',54,596,1172,32,26,C.navy,true,'center');
note('建议用时40秒。依据课程指导书§1.1、§2.1、§2.2、§2.10、§2.12、§2.13。缩尺比来源：02_阻力快速性与总体校核.xlsx，新船换算!B9。服务航速约14 kn的课程条件为设计吃水、CSR=90%MCR、清洁船底和平静开阔深海。路线模块颜色只区分本次叙述重点，不代表完成比例。');

// 第三页：上下两条协作线与统一接口。
header(3,'成员分工与协同关系');
const people=[
 [54,109,'董昱彤（组长）','总体设计',['统筹协调、主尺度、重量重心','阻力与快速性、EEDI / 成本框架','设计报告与 PPT 汇总'],'文档'],
 [744,109,'林森崎','总布置设计',['总布置图、主要舱室与设备布置','技术规格书','文档标准化'],'舱室'],
 [54,349,'王弘毅','型线设计',['船体型线、三维船体建模','主要舱室建模、型线图','静水力计算书及数据接口'],'模型'],
 [744,349,'孟也然','性能计算',['舱容图、舱容计算','装载工况、完整稳性','舱容与稳性计算书'],'性能']];
for(const [x,y,name,role,items,kind]of people){box('成员_'+name,x,y,482,204);txt('姓名_'+name,name,x+20,y+12,300,42,33,C.navy,true);txt('职责_'+name,role,x+20,y+56,330,31,25,C.red,true);items.forEach((t,i)=>txt('职责细项_'+i,t,x+20,y+98+i*30,439,29,23,C.ink));icon(kind,x+398,y+24,52,C.gray);}
txt('上协作说明','总体参数\n布置可行性',547,150,186,70,23,C.navy,true,'center');line('总体布置协作',550,237,730,237,C.blue,2.6,false,true,true);
txt('下协作说明','几何模型\n静水力 / 舱容 / 稳性',540,393,200,72,21,C.navy,true,'center');line('型线性能协作',550,477,730,477,C.blue,2.6,false,true,true);
band('统一接口：主尺度｜吃水｜排水量｜重心｜舱室边界｜模型版本',578,47,26);
note('建议用时30秒。四人组职责依据课程指导书表1-2。董昱彤负责总体与统筹，林森崎负责总布置及文档标准化，王弘毅负责型线建模与静水力接口，孟也然负责舱容装载和完整稳性。箭头为双向交换数据，不是单向任务交接。');

// 第四页：已形成的成果与尚未汇总的成果分开表达。
header(4,'当前总体进展');
const blocks=[
 [54,109,'总体设计与快速性初估','已形成阶段结果',['主尺度、几何相似重量初值','阻力曲线与两个主机候选'],C.teal],
 [658,109,'型线设计与三维建模','文件已形成 / 点集已核查',['三维曲面、二维型线已形成','751 点 / 31 站位 / 32 分支组'],C.teal],
 [54,339,'总布置与技术规格书','组员成果待并入统一汇总',['待并入当前版本总布置图','核对主要舱室与设备信息'],C.orange],
 [658,339,'舱容与稳性','组员成果待并入统一汇总',['待并入舱容与装载工况','完整稳性尚无可展示结论'],C.orange]];
for(const [x,y,t,status,items,color]of blocks){box('进展_'+t,x,y,568,204);txt('进展标题_'+t,t,x+20,y+12,530,40,32,C.navy,true);label(status,x+20,y+60,status.length>15?300:265,color);items.forEach((v,i)=>txt('进展说明_'+i,v,x+20,y+108+i*34,405,31,23,C.ink));}
miniCurve(473,221,120,64);await pic('model.png',1080,231,126,62,'真实三维预览缩略图');icon('舱室',480,454,65,C.gray);icon('性能',1084,454,65,C.gray);
band('当前阶段重点：由“分别完成”转向“相互验证”',567,43,29);
txt('进展限定','建立统一设计状态；点集传递核查尚不能替代曲面、静水力与稳性验证。',54,605,1172,25,19,C.gray,false,'center');
note('建议用时30秒。来源：01_首次汇报综合分析.docx、02_供GPT读取的完整文本.txt及成员一中期报告。当前资料提供总体和型线两条证据链。未发现同一方案版本可直接并入的林森崎总布置、孟也然舱容/稳性最终成果，因此保留待汇总，不使用旧方案概念稿。右上模型为01_组员三维曲面预览.png裁切。');

// 第五页：所有曲线点直接来源于 Excel 的最终公式缓存值。
header(5,'阶段成果①：总体设计与快速性初估');
box('主尺度面板',54,107,337,447);
txt('主尺度标题','主尺度初始方案',72,118,300,40,32,C.navy,true);
for(const [i,k,lab]of [[0,'Lpp','Lpp'],[1,'B','B'],[2,'D','D']]){txt('尺度符号_'+k,lab,77,173+i*64,61,40,27,C.gray,true);txt('尺度值_'+k,`${D[k].toFixed(3)} m`,145,169+i*64,223,47,36,C.navy,true);line('尺度分隔_'+k,76,220+i*64,368,220+i*64,C.border,1);}
txt('设计载重量',`DWT = ${D.DWT} t`,77,371,292,45,32,C.red,true);
txt('主尺度状态','母型改造法初始方案',77,422,292,31,24,C.navy,true);
txt('重量状态','空船重量为几何相似初估\n独立重量与浮力待闭合',77,471,292,62,22,C.gray);
box('图表白底',420,101,806,308,C.white,'none',0);
txt('曲线工况',`性能参考吃水 T = ${D.T_performance.toFixed(6)} m`,420,103,806,34,26,C.navy,true);
const gx=484,gy=173,gw=660,gh=151;
txt('RT轴标题','RT / kN',420,139,130,26,19,C.blue,true);txt('PE轴标题','PE / kW',1103,139,123,26,19,C.red,true,'right');
for(let i=0;i<5;i++){const y=gy+gh-i*gh/4;line('图表网格_'+i,gx,y,gx+gw,y,'#DBE1E6',1);txt('RT刻度_'+i,String(i*200),427,y-12,47,25,18,C.gray,false,'right');txt('PE刻度_'+i,String(i*1500),1154,y-12,70,25,18,C.gray);}
line('左纵轴',gx,gy,gx,gy+gh,C.gray,1);line('右纵轴',gx+gw,gy,gx+gw,gy+gh,C.gray,1);line('横轴',gx,gy+gh,gx+gw,gy+gh,C.gray,1);
const XX=v=>gx+(v-11)/5*gw,YY=(v,max)=>gy+gh-v/max*gh;
line('14kn参考线',XX(14),gy,XX(14),gy+gh,C.gray,1.5,true);
for(const row of D.curve){txt('航速刻度_'+row.V,String(row.V),XX(row.V)-18,gy+gh+4,36,26,18,C.gray,false,'center');}
txt('横轴标题','V / kn',1106,348,82,24,18,C.gray,false,'right');
for(const [key,color,max]of [['RT',C.blue,800],['PE',C.red,6000]]){for(let i=1;i<D.curve.length;i++)line('曲线_'+key+'_'+i,XX(D.curve[i-1].V),YY(D.curve[i-1][key],max),XX(D.curve[i].V),YY(D.curve[i][key],max),color,3);for(const row of D.curve)dot('数据点_'+key+'_'+row.V,XX(row.V),YY(row[key],max),3.6,color);}
line('图例RT',681,152,712,152,C.blue,3);txt('图例RT文字','RT',720,139,55,26,19,C.blue,true);line('图例PE',791,152,822,152,C.red,3);txt('图例PE文字','PE',830,139,55,26,19,C.red,true);
const at14=D.curve.find(v=>v.V===14);
txt('14kn关键结果',`14 kn：RT ${at14.RT.toFixed(3)} kN　　PE ${at14.PE.toFixed(3)} kW`,420,370,806,33,26,C.navy,true);
for(const [i,e]of D.engines.entries()){const x=420+i*411;box('主机候选_'+e.label,x,418,395,136);txt('候选型号_'+e.label,`${e.label}　${e.model}`,x+15,426,369,38,31,C.navy,true);txt('候选MCR_'+e.label,`MCR ${e.MCR} kW / ${e.rpm} rpm`,x+15,468,369,27,23,C.ink);txt('候选CSR_'+e.label,`CSR ≈ ${e.CSR} kW　航速 ≈ ${e.speed.toFixed(2)} kn`,x+15,509,369,29,22,C.ink);}
txt('计算边界','当前为性能参考状态下的阶段结果，用于方案比较；满载状态待静水力与重量闭合后重新计算。',54,565,1172,29,19,C.gray);
box('主机待定条',54,596,1172,34,C.light,'none');txt('主机待定结论','主机尚未定型　后续结合最终船型、桨径净空、EEDI 及总布置综合确定',66,598,1148,29,23,C.navy,true,'center');
note('建议用时55秒。曲线数据：02_阻力快速性与总体校核.xlsx，新船换算!A14:A19、E14:E19（N转kN）、F14:F19（kW），参考吃水B10。图中曲线为原生可编辑折线与标记，六个点均来自工作簿。主机候选：推进与主机!D5:E10、D21:E21。候选A CSR转速107.17 rpm；B为140.96 rpm。DMAU航速只对应本版性能参考状态，不等同于33500 t满载最终航速或EEDI Vref。主尺度：综合材料及重量工作簿，保留三位小数。');

// 第六页：真实图像以独立图片插入，所有新增说明和数据均为原生文本。
header(6,'阶段成果②：型线设计与三维建模');
txt('真实模型标题','真实三维曲面预览',54,106,568,40,32,C.navy,true);
await pic('model.png',54,151,568,147,'组员三维曲面预览原图裁切');
txt('模型说明','组内曲面数据预览，非 MAXSURF 截图',54,306,568,26,19,C.gray);
txt('模型外形特点','艉部收缩　　丰满中体　　球鼻艏',54,339,568,29,23,C.navy);
txt('型线标题','真实二维型线图',658,106,568,40,32,C.navy,true);
await pic('lines.png',658,150,568,206,'组员型线图含横剖纵剖半宽及型值表');
txt('型线图注','横剖线、纵剖线、半宽水线与型值表',658,360,568,26,19,C.gray);
await pic('section.png',54,388,180,192,'典型横剖面真实图艉至舯裁切');
txt('横剖面标题','典型横剖面',280,390,334,39,32,C.navy,true);
txt('横剖面说明','基于真实型值点\n按站位 / 分支绘制\n不添加假设插值点',280,436,334,88,23,C.ink);
txt('横剖面口径','图中虚线沿用原图参考水线\n不作为满载核定结论',280,533,334,48,18,C.gray);
const counts=[[D.points,'型值采样点'],[D.stations,'不同站位'],[D.branches,'站位 / 分支组']];
counts.forEach(([n,l],i)=>{const x=658+i*195;box('点集统计_'+l,x,404,178,101,C.light,'none');txt('统计数值_'+l,n,x,410,178,51,44,C.navy,true,'center');txt('统计名称_'+l,l,x+4,468,170,27,21,C.gray,false,'center');});
txt('点集结果','CSV / Markers / 三维 DXF 点集一致性已核查',658,518,568,29,22,C.teal,true);
txt('半宽核查','最大半宽 × 2 = 28.418402 m，与当前型宽一致',658,559,568,28,21,C.navy);
box('模型边界条',54,590,1172,43,C.light,'none');
txt('模型边界说明','当前证明的是型值数据在不同文件之间的传递一致；曲面公平性、接缝、水密性\n及与当前 MSD 切剖的一致性仍待进一步验证。',70,589,1138,46,19,C.navy);
note('建议用时50秒。图片来自B组_首次汇报综合材料_v0.3_20261101/图像：01_组员三维曲面预览.png、02_组员型线图全图.png、04_典型横剖面.png。模型图裁取完整船体主体，型线图裁去外围说明区，横剖面裁取艉至舯完整子图，均等比例放置。原横剖面灰虚线为性能参考吃水、红点线为缩放满载参考吃水，仅保留原图背景参照。核查为751点、31站位、32分支，CSV/Markers同序差0、DXF排序差约4.996e-13。此为数据传递检查，不能代替曲面公平、水密及MSD重新切剖验证。来源：综合分析及型线、建模补充说明。');

// 第七页：三组设计接口，每列明确已有、缺口、行动。
header(7,'存在的困难与解决措施');
const interfaces=[
 {x:54,t:'船型模型 ↔ 静水力',have:['型值点集一致，模型 / 型线已形成'],gap:['曲面公平、接缝与水密待验证','缺同版本切剖与正式静水力输出'],action:['冻结唯一 MSD 版本','检查曲面、统一站位重新切剖','输出静水力，确定工况吃水浮态'],kind:'模型'},
 {x:452,t:'重量 ↔ 浮力 ↔ 舱容',have:[`空船重量初值约 ${D.lightship.toFixed(1)} t`],gap:['相似初值，独立重量分项待闭合','载重量含货物及油水、人员备品'],action:['总布置 / 舱容 → 实际载荷与重心','更新重量表，与静水力交叉校核','迭代浮态、装载工况与完整稳性'],kind:'重量'},
 {x:850,t:'快速性 ↔ 推进 ↔ 总布置',have:['参考状态阻力、两个主机候选'],gap:['满载状态未统一，主机 / 桨未定型','尾部净空及 EEDI / 续航输入待补'],action:['最终船型与静水力 → 重算阻力','DMAU 更新推进，测量尾部净空','结合总布置，闭合 EEDI 与续航'],kind:'推进'}];
for(const q of interfaces){box('接口模块_'+q.t,q.x,108,376,436);txt('接口标题',q.t,q.x+15,120,346,44,q.x===850?27:29,C.navy,true);line('接口分隔线',q.x+16,174,q.x+360,174,C.border,1);label('当前已有',q.x+16,187,92,C.teal);q.have.forEach((t,i)=>txt('当前已有文本',t,q.x+16,223+i*28,344,29,22,C.ink));label('当前问题',q.x+16,270,92,C.orange);q.gap.forEach((t,i)=>txt('当前缺口文本',t,q.x+16,306+i*31,344,29,22,C.ink));label('下一步措施',q.x+16,388,110,C.blue);q.action.forEach((t,i)=>txt('接口措施文本',t,q.x+16,426+i*31,344,29,22,C.ink));}
txt('工况协调','各工况吃水、重量重心和舱室边界，必须绑定同一模型版本。',54,550,1172,30,24,C.gray,false,'center');
const btxt=['统一模型与设计状态','各专业成果相互验证','形成一套闭环设计方案'];
btxt.forEach((t,i)=>{const x=54+i*403;box('闭环节点_'+i,x,586,366,39,C.light,'none');txt('闭环文字_'+i,t,x+8,590,350,30,25,C.navy,true,'center');if(i<2)line('闭环箭头_'+i,x+373,606,x+395,606,C.navy,2,false,true);});
note('建议用时45秒。来源：首次汇报综合分析、成员一报告、重量重心与浮态待补.xlsx。空船8310.7 t为几何相似初值，并非结构/机电/舾装独立重量估算。尾部桨径5.2298 m仅为母型缩尺参考，未证明真实净空。工况应区分性能9.699753 m、缩放满载参考10.133923 m、组员满载正浮副本约10.120 m和10300WL缩放采样水线10.163526 m。本页不把这些不同口径数字并列作已核定吃水。');

// 第八页：计划周期及可检查的里程碑。
header(8,'11.02—12.04 进展规划');
txt('计划性质','计划周期与阶段里程碑',54,102,1172,34,26,C.gray);
const plans=[
 {date:'11.02—11.09',t:'统一\n设计基准',tasks:['冻结主尺度与缩尺比','坐标、单位、版本统一','定义性能、满载及压载','明确专业输入及接口'],m:'M1  唯一统一的设计输入表'},
 {date:'11.10—11.18',t:'模型与布置\n交叉验证',tasks:['曲面检查与重新切剖','总布置初步方案','并入舱室和设备信息','同版本静水力输出'],m:'M2  船型与布置基本一致'},
 {date:'11.19—11.27',t:'重量—浮力\n性能闭环',tasks:['舱容计算与装载工况','重量重心与排水量闭合','完整稳性计算','重算阻力和推进方案'],m:'M3  第一轮完整设计状态'},
 {date:'11.28—12.04',t:'方案收敛\n成果整理',tasks:['主机、桨与设备迭代','完善 EEDI 与续航','整理设计文件与图纸','完成第二次汇报材料'],m:'M4  汇总相互校核的阶段方案'}];
plans.forEach((q,i)=>{const x=54+i*299;box('计划阶段_'+i,x,162,275,386);box('阶段日期底',x,162,275,52,C.navy,'none',0);txt('阶段日期_'+i,q.date,x+8,170,259,35,29,C.white,true,'center');txt('阶段标题_'+i,q.t,x+15,228,245,80,32,C.navy,true,'center');q.tasks.forEach((t,j)=>txt('计划任务_'+j,t,x+15,315+j*43,245,35,23,C.ink));box('里程碑底',x,505,275,43,C.light,'none',0);txt('里程碑_'+i,q.m,x+8,509,259,34,19,C.navy,true,'center');if(i<3)line('阶段箭头_'+i,x+279,355,x+294,355,C.navy,2,false,true);});
box('12月4日目标底',54,570,1172,58,C.light,'none');
txt('12月4日目标','12 月 4 日前：形成同一船型、同一工况\n相互校核的第一轮完整设计方案',74,569,1132,60,25,C.navy,true,'center');
note('建议用时35秒。时间计划依据PPT完善任务规划第8页要求。四个日期区间均是后续计划，不是当前完成比例。12月4日为第一轮完整方案阶段节点，不代表最终定型。M2在模型检查和船型布置基本一致后，才能作为后续舱容、稳性、快速性计算基础。');

await (await PresentationFile.exportPptx(p)).save(path.join(ROOT,'.build/raw.pptx'));
console.log('已完成八页原生内容更新，等待实际 PowerPoint 渲染检查。');
