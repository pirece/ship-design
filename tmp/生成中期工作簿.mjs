import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const out='outputs/B组_成员一_中期_v0.2_20261031';
await fs.mkdir('tmp/表格检查',{recursive:true});
const calc=JSON.parse(await fs.readFile('tmp/计算结果.json','utf8'));
const put=(s,c,v)=>s.getRange(c).values=[[v]];
const fx=(s,c,v)=>s.getRange(c).formulas=[[v]];
function table(s,range){s.getRange(range).format={font:{name:'Microsoft YaHei',size:11},rowHeight:25,verticalAlignment:'center'};s.showGridLines=false;}
function header(s,range){s.getRange(range).format={fill:'#D9E2F3',font:{bold:true,color:'#000000'},wrapText:true,rowHeight:32};}
function fresh(w,name,cols='A1:F45'){const s=w.worksheets.add(name);table(s,cols);s.getRange('A:A').format.columnWidth=31;s.getRange('B:E').format.columnWidth=19;s.getRange('F:F').format.columnWidth=72;s.getRange('B4:E40').setNumberFormat('0.000');return s;}
async function finish(w,file,renders){
 w.recalculate();
 console.log(file,(await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!',options:{useRegex:true,maxResults:40},maxChars:3000})).ndjson);
 for(const [s,r] of renders){const b=await w.render({sheetName:s,range:r,scale:1.3});await fs.writeFile(`tmp/表格检查/${s}.png`,new Uint8Array(await b.arrayBuffer()));}
 await (await SpreadsheetFile.exportXlsx(w)).save(`${out}/${file}`);
}

const w=await SpreadsheetFile.importXlsx(await FileBlob.load('0003_阻力估算模板.xlsx'));
const ship=w.worksheets.getItem('ship'), h=w.worksheets.getItem('HoltropMennen');
const m=fresh(w,'对应航速母型');
m.getRange('A1:I38').copyFrom(h.getRange('A1:I38'),'all');
const n=fresh(w,'新船换算');
const p=fresh(w,'推进与主机');
const e=fresh(w,'EEDI与续航');
const cost=fresh(w,'建造成本待补');
put(ship,'A31','资料来源：课程Holtrop方法第1—2页；DWT为船型名义称谓。');
put(ship,'A32','9.83 m状态总排水量41442.3 t，不能与名义35000 t载重混为一体。');
put(ship,'A33','以下公式沿用课程参数；新船模型实测值返回后另版复算。');
// 补齐课程模板所有低速分量，并修正C15高区分支的错误引用。
function holtrop(s){
 for(const c of ['B','C','D','E','F','G']){
  const forms={7:`${c}6*0.5144`,8:`${c}7/SQRT($C$4*ship!$C$5)`,9:`${c}7*ship!$C$5/$C$3`,10:`0.075/(LOG10(${c}9)-2)^2`,11:`0.5*$C$2*${c}7^2*${c}10*ship!$C$18`,12:'0.93+0.487118*(1+0.011*ship!$C$24)*(ship!$C$7/ship!$C$5)^1.06806*(ship!$C$8/ship!$C$5)^0.46106*(ship!$C$5/ship!$C$6)^0.121563*ship!$C$29^0.36486*(1-ship!$C$15)^(-0.60247)',13:'1.4',14:`0.5*$C$2*${c}7^2*ship!$C$19*${c}13*${c}10`,15:'IF(1/ship!$C$25<0.11,0.229577*(1/ship!$C$25)^0.33333,IF(1/ship!$C$25<0.25,1/ship!$C$25,0.5-0.0625/ship!$C$25))',16:`2223105*${c}15^3.78613*ship!$C$26^1.07961*(90-ship!$C$13)^(-1.37565)`,17:'0.56*ship!$C$22^1.5/(ship!$C$7*ship!$C$8*(0.31*SQRT(ship!$C$22)+ship!$C$9-ship!$C$23))',18:`EXP(-1.89*SQRT(${c}17))`,19:'1-0.8*ship!$C$21/(ship!$C$7*ship!$C$8*ship!$C$16)',20:'IF(ship!$C$15<0.8,8.07981*ship!$C$15-13.8673*ship!$C$15^2+6.984388*ship!$C$15^3,1.73014-0.7067*ship!$C$15)',21:`0.0140407*ship!$C$27-1.75254*ship!$C$29^(-1/3)-4.79323/ship!$C$25-${c}20`,22:'-0.9',23:'IF(ship!$C$29<512,-1.69385,IF(ship!$C$29>1726.91,0,-1.69385+(ship!$C$29^(1/3)-8)/2.36))',24:`0.4*${c}23*EXP(-0.034*${c}8^(-3.29))`,25:'IF(ship!$C$25<12,1.446*ship!$C$15-0.03*ship!$C$25,1.446*ship!$C$15-0.36)',26:`$C$2*$C$4*ship!$C$11*${c}16*${c}18*${c}19*EXP(${c}21*${c}8^${c}22+${c}24*COS(${c}25/${c}8^2))`,27:'0.56*SQRT(ship!$C$22)/(ship!$C$9-ship!$C$23)',28:`${c}7/SQRT($C$4*(ship!$C$9-ship!$C$23-0.25*SQRT(ship!$C$22))+0.15*${c}7^2)`,29:`0.11*EXP(-3*${c}27^(-2))*${c}28^3*ship!$C$22^1.5*$C$2*$C$4/(1+${c}28^2)`,30:`${c}7/SQRT(2*$C$4*ship!$C$21/(ship!$C$7*(1+ship!$C$17)))`,31:`IF(${c}30<5,0.2*(1-0.2*${c}30),0)`,32:`0.5*$C$2*${c}7^2*ship!$C$21*${c}31`,33:'MIN(ship!$C$9/ship!$C$5,0.04)',34:`0.006*(ship!$C$5+100)^(-0.16)-0.00205+0.003*SQRT(ship!$C$5/7.5)*ship!$C$14^4*${c}18*(0.04-${c}33)`,35:`0.5*$C$2*${c}7^2*ship!$C$20*${c}34`,36:`${c}11*${c}12+${c}14+${c}26+${c}29+${c}32+${c}35`,37:`${c}36*${c}7/1000`,38:`${c}37*1.34102209`,39:`${c}37/0.7355`};
  for(const [r,f] of Object.entries(forms))fx(s,`${c}${r}`,'='+f);
 }
 put(s,'A38','P_E 英制hp');put(s,'A39','P_E 公制PS');
 s.getRange('B6:G39').setNumberFormat('0.0000');s.getRange('B9:G9').setNumberFormat('0.000E+00');
 s.getRange('B10:G10').setNumberFormat('0.0000000');s.getRange('B24:G24').setNumberFormat('0.000E+00');s.getRange('B34:G34').setNumberFormat('0.0000000');
 s.getRange('A:A').format.columnWidth=21;s.getRange('B:G').format.columnWidth=17;
 put(s,'A41','第38行保留模板英制hp；DMAU应使用第39行公制PS。');
 put(s,'A42','C15分支修正为L³/∇，本船处于小于512分支，修正不改变本船数值。');
 put(s,'A43','适用本次Fn<0.4；本表不是通用高速Holtrop程序。');
}
holtrop(h);holtrop(m);m.getRange('I1:I39').clear({applyTo:'contents'});
put(n,'A2','新船性能参考吃水下的相似换算');
n.getRange('A4:C11').values=[['输入与比例','数值','单位'],['目标载重量',33500,'t'],['母型满载总排水量',43517.7,'t'],['母型空船重量',8650,'t'],['质量比例 r',null,'—'],['长度比例 k',null,'—'],['新船性能参考吃水',null,'m'],['新船满载参考吃水',null,'m']];
fx(n,'B8','=B5/(B6-B7)');fx(n,'B9','=B8^(1/3)');fx(n,'B10','=ship!C8*B9');fx(n,'B11','=10.27*B9');
n.getRange('A13:G13').values=[['新船航速 kn','母型对应航速 kn','母型阻力 N','母型有效功率 kW','新船阻力 N','新船有效功率 kW','新船有效功率 PS']];
for(let i=0;i<6;i++){
 const r=i+14,c='BCDEFG'[i];put(n,`A${r}`,i+11);fx(n,`B${r}`,`=A${r}/SQRT($B$9)`);fx(m,`${c}6`,`='新船换算'!B${r}`);
 fx(n,`C${r}`,`='对应航速母型'!${c}36`);fx(n,`D${r}`,`='对应航速母型'!${c}37`);fx(n,`E${r}`,`=C${r}*$B$8`);fx(n,`F${r}`,`=D${r}*$B$8^(7/6)`);fx(n,`G${r}`,`=F${r}/0.7355`);
}
header(n,'A4:C4');header(n,'A13:G13');n.getRange('A13:G19').format.columnWidth=22;n.getRange('A13:G13').format.rowHeight=45;n.getRange('B14:G19').setNumberFormat('0.000');
put(n,'A22','依据：v0.1几何相似比例，课程流程第8步。');put(n,'A23','在相同Fn下比较，不能将两船同为14 kn时的功率直接乘r^(7/6)。');
put(n,'A24','满载10.134 m及压载工况：待新模型静水力和船型参数，不由本表替代。');
put(n,'A25','14 kn附近估算，不含风浪、污底及附加海况裕量。');
const ch=n.charts.add('line',[n.getRange('A13:A19'),n.getRange('F13:F19')]);ch.setPosition('A28','G42');ch.title='新船有效功率曲线';ch.hasLegend=false;ch.xAxis={axisType:'textAxis',textStyle:{typeface:'Microsoft YaHei',fontSize:11}};ch.yAxis={numberFormatCode:'0',numberFormatSourceLinked:false,textStyle:{typeface:'Microsoft YaHei',fontSize:11}};

const 运行=[];
for(const dir of ['01_parent_corrected','02_new_initial','03_new_G45_L1_CSR','04_new_S40_L1_CSR']){
 const raw=await fs.readFile(`${out}/计算依据/DMAU/${dir}/DMAU_中文结果.txt`,'utf8');
 const block=raw.slice(raw.indexOf('(4)'),raw.indexOf('(5)'));
 const get=re=>Number(block.match(re)[1]);
 运行.push({dir,D:get(/D =\s+([\d.]+)/),pd:get(/P\/D=\s+([\d.]+) no/),pdc:get(/P\/D=\s+([\d.]+) T/),ae:get(/AE\/A0=\s+([\d.]+)/),eta:get(/ETP=\s+([\d.]+)/),ets:get(/ETS=\s+([\d.]+)/),v:get(/VS=\s+([\d.]+) kn/),power:get(/BHP=\s+([\d.]+) kw/),rpm:get(/RPM=\s+([\d.]+)/)});
}
await fs.writeFile('tmp/DMAU摘要.json',JSON.stringify(运行,null,2));
put(p,'A2','推进因子与主机候选比较');
p.getRange('A4:E4').values=[['参数','母型修正复算','新船相似初选','新船候选A','新船候选B']];header(p,'A4:E4');
const rows={5:['主机型号','6S42MC','尚未选型','5G45ME-C9.7','6S40ME-C9.5'],6:['MCR kW',6480,null,6950,6810],7:['MCR转速 rpm',136,null,111,146],8:['CSR比例',.9,.9,.9,.9],9:['本次输入功率 kW',5832,运行[1].power,6255,6129],10:['本次输入转速 rpm',131.4,运行[1].rpm,107.17,140.96],11:['伴流分数 w',.3563,.3563,.3563,.3563],12:['推力减额 t',.2194,.2194,.2194,.2194],13:['相对旋转效率',1,1,1,1],14:['轴系效率',.99,.99,.99,.99],15:['桨径 m',...运行.map(x=>x.D)],16:['盘面比',...运行.map(x=>x.ae)],17:['螺距比 未修正',...运行.map(x=>x.pd)],18:['螺距比 厚度修正',...运行.map(x=>x.pdc)],19:['敞水效率',...运行.map(x=>x.eta)],20:['船后推进效率 不含轴系',...运行.map(x=>x.ets)],21:['DMAU估算航速 kn',...运行.map(x=>x.v)],22:['75%负荷SFOC g/kWh',null,null,163,170],23:['100%负荷SFOC g/kWh',177,null,169.5,176.5],24:['Tier II主机干重 t',null,null,165,126],25:['最小机长 mm',null,null,5200,5342]};
for(const[r,a]of Object.entries(rows))p.getRange(`A${r}:E${r}`).values=[a];
for(const c of ['B','C','D','E']){fx(p,`${c}26`,`=${c}19*${c}14*(1-${c}12)/(1-${c}11)`);fx(p,`${c}27`,`=IF(${c}21>=14,"本次估算达到14 kn","本次估算未达到")`);}
put(p,'A26','含轴系总推进效率');put(p,'A27','本次航速校核');
p.getRange('B5:E5').format.rowHeight=32;p.getRange('B:E').format.columnWidth=23;p.getRange('B27:E27').format.wrapText=true;p.getRange('A27:E27').format.rowHeight=40;
put(p,'F5','型号与参数：厂家2026手册第32、33、104、106页。');
put(p,'F6','候选A供中期布置与能效比较；未最终定型。');
put(p,'F9','功率为90%MCR；CSR转速按螺旋桨立方律初估。');
put(p,'F11','w=0.5CB−0.05，t=0.27CB；输入定宽舍入至4位小数。');
put(p,'F15','Dmax、轴高按母型缩尺；实际尾部净空尚待成员二、三核对。');
put(p,'F21','软件数值为本版快照，修改船型、主机、推进因子必须重跑DMAU。');
put(p,'F22','油耗为L1、低负荷EGB、Tier II、LCV=42700 kJ/kg参考值。');
put(p,'F24','干重不含全套机电与基础；不能在空船粗估上重复叠加。');
p.getRange('A30:D30').values=[['课程净空下限','系数','候选A下限 m','实测值 m']];header(p,'A30:D30');
for(let i=0;i<4;i++){put(p,`A${31+i}`,'abcd'[i]);put(p,`B${31+i}`,[.12,.20,.14,.04][i]);fx(p,`C${31+i}`,`=B${31+i}*$D$15`);p.getRange(`D${31+i}`).format.fill='#FFF2CC';}
put(p,'F31','仅按课程引用计算数值；实测值与现行CCS条款核对后才可判通过。');

put(e,'A2','EEDI与续航分阶段计算');
e.getRange('A4:D4').values=[['参数','数值','单位','状态或依据']];header(e,'A4:D4');e.getRange('D:D').format.columnWidth=63;
const erows={5:['目标载重量',33500,'t','指导书；最终以夏季载重线核定值为准'],6:['参考线系数a',961.79,'—','IMO散货船参考线'],7:['参考线指数c',.477,'—','IMO散货船参考线'],8:['EEDI参考线',null,'gCO2/(t·nm)','可计算'],9:['课程20%削减限值',null,'gCO2/(t·nm)','保留课程示例口径'],10:['第三阶段30%削减限值',null,'gCO2/(t·nm)','2025起适用阶段；合同和交付日期另核'],12:['候选A MCR',null,'kW','厂家L1点；未作降额优化'],13:['EEDI主机功率',null,'kW','75%MCR'],14:['目录75%负荷SFOC',null,'g/kWh','柴油基准LCV=42700；非本船认证值'],15:['柴油CF',3.206,'tCO2/t燃油','IMO MEPC.364(79)'],16:['附机功率公式值',null,'kW','无轴带机且MCR<10000时0.05MCR'],17:['满载75%MCR对应Vref',null,'kn','待成员三满载船型与功率航速闭合'],18:['认证主机SFOC',null,'g/kWh','待实际燃料与证书工况'],19:['认证辅机SFOC',null,'g/kWh','待辅机选型及电力负荷'],20:['认证主机CF',null,'—','待实际燃料'],21:['认证辅机CF',null,'—','待实际燃料'],22:['含主辅机EEDI待补值',null,'gCO2/(t·nm)','常规单机无PTO/PTI；修正因子需逐项核对'],24:['课程简化情景航速',14,'kn','仅为假定，不是满载Vref'],25:['候选A主机简化情景',null,'gCO2/(t·nm)','只含主机，使用目录柴油SFOC'],26:['目录75%油耗容差',.06,'—','2026手册第8页；65%至84.99%负荷为6%'],27:['候选A容差情景',null,'gCO2/(t·nm)','不得作为正式达到EEDI'],28:['情景相对第三阶段限值',null,'—','不能据此出具合规结论'],30:['要求续航力',16000,'nm','指导书'],31:['估算航速',14,'kn','保守使用设计目标'],32:['连续航行时间',null,'h','不含港停'],33:['候选A CSR',null,'kW','90%MCR'],34:['90%负荷油耗插值',null,'g/kWh','75%与100%目录点线性插值；非厂家保证值'],35:['柴油基准主机耗油',null,'t','不含辅机、锅炉、储备及不可用油'],36:['HFO低热值情景',40200,'kJ/kg','仅作热值换算情景'],37:['HFO主机耗油情景',null,'t','LCV换算；待本船燃料数据替换'],38:['CSR油耗容差情景',.05,'—','2026手册第8页；85%至100%为5%'],39:['含5%油耗容差HFO量',null,'t','仍不是总燃油舱容量或全船燃油重量']};
for(const[r,a]of Object.entries(erows))e.getRange(`A${r}:D${r}`).values=[a];
const ef={8:'B6*B5^(-B7)',9:'B8*(1-20%)',10:'B8*(1-30%)',12:"'推进与主机'!D6",13:'0.75*B12',14:"'推进与主机'!D22",16:'IF(B12<10000,0.05*B12,0.025*B12+250)',22:'IF(COUNT(B17:B21)<5,"待补数据",(B13*B18*B20+B16*B19*B21)/(B5*B17))',25:'B13*B14*B15/(B5*B24)',27:'B25*(1+B26)',28:'B25/B10-1',32:'B30/B31',33:"'推进与主机'!D9",34:"'推进与主机'!D22+(0.9-0.75)/(1-0.75)*('推进与主机'!D23-'推进与主机'!D22)",35:'B32*B33*B34/1000000',37:'B35*42700/B36',39:'B37*(1+B38)'};
for(const[r,f]of Object.entries(ef))fx(e,`B${r}`,'='+f);
e.getRange('B17:B21').format.fill='#FFF2CC';for(const r of [26,28,38])e.getRange(`B${r}`).setNumberFormat('0.0%');
put(e,'A42','参考：MEPC.364(79)、MEPC.410(84)、MARPOL附则VI参考线与削减阶段。');
put(e,'A43','母型课程示例仅用于教学：6480×75%×211×1.05×3.206/(35000×14)。');fx(e,'B44','=6480*0.75*211*1.05*3.206/(35000*14)');put(e,'A44','母型示例复算');
put(e,'A45','流程原文结果7.44为算术笔误，按所列参数复算为7.044910；超限结论不变。');
put(e,'A46','https://wwwcdn.imo.org/localresources/en/OurWork/Environment/Documents/annex/RESOLUTION%20MEPC.364(79).pdf');

put(cost,'A2','建造成本估算待补表');
put(cost,'A3','缺少材料量、设备报价和工时；本版不提供虚构总造价。');
cost.getRange('A5:F5').values=[['成本项目','数量','单位','单价 元/单位','金额 元','数据提供及口径']];header(cost,'A5:F5');
const cr=[['钢材采购',null,'t',null,null,'净钢重、利用率、钢级、含税运价'],['主机及附属系统',1,'套',null,null,'候选A厂家报价，注明供货范围'],['主柴油发电机',3,'套',null,null,'指导书规定数量；待型号及报价'],['应急发电机',1,'套',null,null,'待容量与报价'],['组合锅炉',1,'套',null,null,'指导书配置；待规格及报价'],['甲板起重机',4,'台',null,null,'30 t起重量不是设备自重；待型号及报价'],['舱口盖系统',5,'舱套',null,null,'按5货舱规划；待实际数量和供货边界'],['轴桨舵系统',1,'船套',null,null,'待最终尺寸及报价'],['其他舾装电气管系',null,'批',null,null,'待清单；避免与设备附属系统重复'],['建造人工',null,'工时',null,null,'待建造工时及单位人工成本'],['设计检验试验',null,'项',null,null,'待合同或课程成本依据'],['船厂制造间接费',null,'项',null,null,'待计费基数与口径']];cost.getRange('A6:F17').values=cr;
for(let r=6;r<=17;r++)fx(cost,`E${r}`,`=IF(COUNT(B${r},D${r})<2,"待补",B${r}*D${r})`);
put(cost,'A19','建造成本合计');fx(cost,'E19','=IF(COUNT(E6:E17)<12,"待补完整成本",SUM(E6:E17))');
cost.getRange('B6:B17').format.fill='#FFF2CC';cost.getRange('D6:D17').format.fill='#FFF2CC';cost.getRange('E6:E19').setNumberFormat('#,##0');
put(cost,'A22','币种、含税口径、报价日期、运费和预备费须统一；价格来源写在F列。');
put(cost,'A23','船舶销售合同价含利润等因素，不能直接称为本船建造成本。');

// 独立Python计算逐点核对Excel有意义的输出。
w.recalculate();
for(let i=0;i<6;i++){const c='BCDEFG'[i];const a=h.getRange(`${c}37`).values[0][0];const b=n.getRange(`F${i+14}`).values[0][0];if(Math.abs(a-calc.母型[i].pe)>1e-6||Math.abs(b-calc.新船[i].pe)>1e-6)throw new Error(`阻力计算不一致 ${c}: ${a} ${b}`);}
await finish(w,'02_阻力快速性与总体校核.xlsx',[['ship','A1:E29'],['HoltropMennen','A6:G39'],['对应航速母型','A6:G39'],['新船换算','A2:G25'],['推进与主机','A4:E34'],['EEDI与续航','A4:D39'],['建造成本待补','A2:F23']]);

const ww=await SpreadsheetFile.importXlsx(await FileBlob.load('重量重心和浮态调整.xlsx'));
const wt=ww.worksheets.getItem('Weight'),fl=ww.worksheets.getItem('Floating'),b=ww.worksheets.getItem('Sheet1');
const dist=ww.worksheets.add('母型分区缩放');table(dist,'A1:J28');dist.getRange('A:J').format.columnWidth=18;
put(dist,'A2','母型纵向重量分区的几何缩放');
dist.getRange('A4:J4').values=[['分区','母型重量 t','母型XG距AP m','母型ZG m','新船重量 t','新船XG距AP m','新船ZG m','新船纵向矩 t·m','新船垂向矩 t·m','新船YG m']];header(dist,'A4:J4');dist.getRange('A4:J4').format.rowHeight=48;
const dr=[['STERN 艉部',269,2.17],['ER1 机舱1',555,17.94],['ER2 机舱2',400,15.4],['HOLD5 五货舱区',885,40.3],['BHD2 舱壁2',201,53.4],['HOLD4 四货舱区',1035,68.5],['BHD3 舱壁3',222,82.23],['HOLD3 三货舱区',1026,96.76],['BHD4 舱壁4',222,111.03],['HOLD2 二货舱区',1021,125.8],['BHD5 舱壁5',201,139.83],['HOLD1 一货舱区',717,152.6],['FORE 艏部',360,170],['SUPER 上层建筑',700,18.4],['PIPE 管系',200,75],['MIS 杂项',386,86],['ADD 附加',250,86]];
for(let i=0;i<dr.length;i++){const rr=i+5;dist.getRange(`A${rr}:D${rr}`).values=[[...dr[i],10.2]];fx(dist,`E${rr}`,`=B${rr}*Sheet1!$C$8`);fx(dist,`F${rr}`,`=C${rr}*Sheet1!$C$9`);fx(dist,`G${rr}`,`=D${rr}*Sheet1!$C$9`);fx(dist,`H${rr}`,`=E${rr}*F${rr}`);fx(dist,`I${rr}`,`=E${rr}*G${rr}`);put(dist,`J${rr}`,0);}
put(dist,'A22','合计或加权重心');for(const c of ['B','E','H','I'])fx(dist,`${c}22`,`=SUM(${c}5:${c}21)`);fx(dist,'C22','=SUMPRODUCT(B5:B21,C5:C21)/B22');fx(dist,'D22','=SUMPRODUCT(B5:B21,D5:D21)/B22');fx(dist,'F22','=H22/E22');fx(dist,'G22','=I22/E22');put(dist,'J22',0);dist.getRange('B5:J22').setNumberFormat('0.000');
put(dist,'A24','来源：母型装载手册PDF第333页，逐项照录重量及坐标；全部原始ZG均为10.2 m。');
put(dist,'A25','这些是空船纵向重量分布区，不是货物载荷，也不是钢料、机电、舾装的独立估算。');
put(dist,'A26','分区缩放沿用v0.1假设；保留原表坐标舍入引起的加权重心差异。');
put(dist,'A27','实际设备不会全部按体积比缩放；本表用于复核与后续替换，不能证明独立重量闭合。');
table(b,'A1:F46');b.getRange('A:A').format.columnWidth=34;b.getRange('B:E').format.columnWidth=19;b.getRange('F:F').format.columnWidth=65;
put(b,'A2','空船粗估基准与分项待补');b.getRange('A4:D4').values=[['参数','母型','新船','单位']];header(b,'A4:D4');
const br={5:['满载参考排水量',43517.7,null,'t'],6:['空船重量',8650,null,'t'],7:['载重量',null,33500,'t'],8:['质量比例',null,null,'—'],9:['线性比例',null,null,'—'],10:['垂线间长',172,null,'m'],11:['XG距AP',79.3,null,'m'],12:['ZG距BL',10.2,null,'m'],13:['YG',0,null,'m'],14:['XG距舯',null,null,'m'],15:['性能参考吃水',9.83,null,'m'],16:['满载参考吃水',10.27,null,'m'],17:['水密度',1.025,null,'t/m³'],18:['型深',14.6,null,'m'],19:['型宽',28.8,null,'m']};for(const[r,a]of Object.entries(br))b.getRange(`A${r}:D${r}`).values=[a];
fx(b,'B7','=B5-B6');fx(b,'C8','=C7/B7');fx(b,'C9','=C8^(1/3)');fx(b,'C5','=B5*C8');fx(b,'C6','=B6*C8');for(const r of [10,11,12,13,15,16,18,19])fx(b,`C${r}`,`=B${r}*$C$9`);fx(b,'B14','=B11-B10/2');fx(b,'C14','=C11-C10/2');fx(b,'C17','=B17');
put(b,'F5','母型装载手册PDF第42页T=10.27 m行。');put(b,'F6','空船重量与重心：手册第100、333页。');put(b,'F8','v0.1假设：载重量系数不变，几何相似。');put(b,'F14','AP为纵向零点，向艏为正；距舯负数表示舯后。');
b.getRange('B5:C19').setNumberFormat('0.000000');
b.getRange('A22:F22').values=[['独立空船重量分项','重量 t','XG距AP m','ZG距BL m','YG m','缺项及来源']];header(b,'A22:F22');
const bw=[['船体钢料及结构',null,null,null,null,'待结构重量估算或母型钢重系数'],['主机和机电设备',null,null,null,null,'待全套设备清单与布置重心'],['舾装及货物装卸设备',null,null,null,null,'待4台30t吊机实际自重、舱盖等清单'],['重量裕量',null,null,null,null,'待课程采用比例及作用基数']];b.getRange('A23:F26').values=bw;b.getRange('B23:E26').format.fill='#FFF2CC';put(b,'A28','独立分项汇总');fx(b,'B28','=IF(COUNT(B23:B26)<4,"待补分项",SUM(B23:B26))');for(const c of ['C','D','E'])fx(b,`${c}28`,`=IF(COUNT(B23:B26,${c}23:${c}26)<8,"待补分项",SUMPRODUCT(B23:B26,${c}23:${c}26)/SUM(B23:B26))`);
put(b,'A30','候选A主机干重');put(b,'B30',165);put(b,'F30','厂家2026手册第104页；未加入总重，避免重复。');
put(b,'A32','Weight表本版使用C6粗估空船重；独立分项完整后才替换。');put(b,'A33','载荷栏为空表示未知；确实未装载的项目应由工况制定人填0。');put(b,'A34','模板G列填写正的舯后距离，H列以负号计纵向矩。');
// 重量模板只计各分类小计，不将小计和明细重复相加。
fx(wt,'B4','=Sheet1!C6');fx(wt,'C4','=Sheet1!C12');fx(wt,'E4','=MAX(Sheet1!C14,0)');fx(wt,'G4','=MAX(-Sheet1!C14,0)');fx(wt,'I4','=Sheet1!C13');
const leaf=[4,6,7,8,9,10,12,13,14,15,17,18,19,20,22,23,24,25,26,27,29,30,31,32,33];
for(const r of leaf){fx(wt,`D${r}`,`=IF(B${r}="","",IF(B${r}=0,0,IF(C${r}="","",B${r}*C${r})))`);fx(wt,`F${r}`,`=IF(B${r}="","",IF(B${r}=0,0,IF(COUNT(E${r},G${r})<2,"",B${r}*E${r})))`);fx(wt,`H${r}`,`=IF(B${r}="","",IF(B${r}=0,0,IF(COUNT(E${r},G${r})<2,"",-B${r}*G${r})))`);fx(wt,`J${r}`,`=IF(B${r}="","",IF(B${r}=0,0,IF(I${r}="","",B${r}*I${r})))`);}
for(const[r,start,end]of[[5,6,10],[11,12,15],[16,17,20],[21,22,25],[28,29,33]]){
 for(const c of ['B','D','F','H','J'])fx(wt,`${c}${r}`,`=IF(COUNT(${c}${start}:${c}${end})<${end-start+1},"",SUM(${c}${start}:${c}${end}))`);
 for(const[c,mat]of[['C','D'],['E','F'],['G','H'],['I','J']])fx(wt,`${c}${r}`,`=IF(OR(B${r}="",${mat}${r}=""),"",IF(B${r}=0,0,${c==='G'?'-':''}${mat}${r}/B${r}))`);
}
for(const c of ['B','D','F','H','J']){const a=[4,5,11,16,21,26,27,28].map(r=>`${c}${r}`).join(',');fx(wt,`${c}34`,`=IF(COUNT(${a})<8,"待补工况",SUM(${a}))`);}
for(const[c,mat]of[['C','D'],['E','F'],['G','H'],['I','J']])fx(wt,`${c}34`,`=IF(COUNT(B34,${mat}34)<2,"待补工况",${c==='G'?'-':''}${mat}34/B34)`);
put(wt,'A17','滑油分项1');put(wt,'A18','滑油分项2');put(wt,'A19','滑油分项3');put(wt,'A20','滑油分项4');put(wt,'A24','其他淡水1');put(wt,'A25','其他淡水2');put(wt,'A33','其他压载水');
wt.getRange('B4:J34').setNumberFormat('0.000');wt.getRange('B:J').format.columnWidth=15;wt.getRange('A:A').format.columnWidth=26;
for(const r of leaf.filter(x=>x!==4))for(const c of ['B','C','E','G','I'])wt.getRange(`${c}${r}`).format.fill='#FFF2CC';
wt.getRange('B3:J3').values=[['t','m','t·m','m','t·m','m','t·m','m','t·m']];put(wt,'A36','空船行为几何粗估；其他项目须按一个明确工况填入，不自动均分33500 t。');put(wt,'A37','G列为舯后距离正值，H列为负纵向矩；不存在的载荷须明确填0。');
table(fl,'A1:G25');fl.getRange('B:B').format.columnWidth=26;fl.getRange('D:D').format.columnWidth=32;fl.getRange('E:E').format.columnWidth=19;fl.getRange('G:G').format.columnWidth=68;
const ff={3:'IF(ISNUMBER(Weight!B34),Weight!B34,"待补工况")',5:'IF(COUNT(Weight!B34,Weight!F34,Weight!H34)<3,"待补工况",(Weight!F34+Weight!H34)/Weight!B34)',8:'IF(COUNT(E3,E5,E6,E7)<4,"待补静水力",E3*(E5-E6)/(100*E7))',10:'IF(COUNT(E8,E9)<2,"待补静水力",E8*(Sheet1!C10/2-E9)/Sheet1!C10)',11:'IF(COUNT(E8,E9)<2,"待补静水力",-E8*(Sheet1!C10/2+E9)/Sheet1!C10)',12:'IF(COUNT(E4,E10)<2,"待补静水力",E4+E10)',13:'IF(COUNT(E4,E11)<2,"待补静水力",E4+E11)',14:'IF(ISNUMBER(Weight!C34),Weight!C34,"待补工况")',16:'IF(COUNT(E14,E15)<2,"待补静水力",E15-E14)',18:'IF(COUNT(E16,E17)<2,"待补自由液面",E16-E17)'};
for(const[r,f]of Object.entries(ff))fx(fl,`E${r}`,'='+f);for(const r of [2,4,6,7,9,15,17,19])fl.getRange(`E${r}`).format.fill='#FFF2CC';
put(fl,'G2','排水体积由模型提供；型体积与外板修正后体积不能混用。');put(fl,'G4','重量对应的平浮参考吃水，由静水力反求。');put(fl,'G7','MTC单位t·m/cm，勿漏纵倾值换算中的100。');put(fl,'G8','纵倾定义dF−dA，正值为首倾；所有纵坐标向艏为正。');put(fl,'G9','XF距舯，需对应同一吃水状态。');put(fl,'G17','由成员四提供自由液面矩合计/排水量。');put(fl,'G19','横摇经验式系数尚未指定，本版不虚填。');put(fl,'A22','近似小纵倾校核表；完整稳性须以成员四的软件工况计算为准。');
await finish(ww,'03_重量重心与浮态待补.xlsx',[['Weight','A1:J37'],['Floating','A1:E22'],['Sheet1','A4:F30'],['母型分区缩放','A2:J27']]);
console.log('工作簿已导出');
