"""按参考图像素坐标建立元素清单、裁切素材及原生图标轮廓。"""
from pathlib import Path
import json, re, cv2, numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'source'/'reference_images'
ASSETS=ROOT/'assets'
ASSETS.mkdir(exist_ok=True)
SOURCES={
 'task':'船舶设计任务信息图幻灯片.png',
 'route':'船舶总体设计流程与任务概览.png',
 'team':'上海交大风格B组成员分工图.png',
 'progress':'船舶设计项目总体进展 infographics.png',
 'results':'船舶总体设计与快速性初估.png',
 'model':'型线设计与三维建模阶段成果.png',
 'issues':'船舶设计困难与解决措施闭环分析.png',
 'plan':'大学船舶设计进展规划时间轴.png',
 'cover':'上海交通大学船舶设计课程汇报封面.png'}
images={k:Image.open(INPUT/v).convert('RGB') for k,v in SOURCES.items()}
manifest=[]; scenes=[]; elements=[]; current=''
NAVY='#183B60'; RED='#B70910'; BLUE='#176CAF'; TEAL='#008C94'; ORANGE='#D65A00'; GREEN='#378C59'; INK='#243B56'
def add(kind,**kw):
 e={'kind':kind,**kw}; elements.append(e); return e
def shape(x,y,w,h,fill='#FFFFFF',stroke='none',sw=1,r=0,name='框体',geom=None):
 return add('shape',x=x,y=y,w=w,h=h,fill=fill,stroke=stroke,sw=sw,r=r,name=name,geom=geom or ('roundRect' if r else 'rect'))
def text(s,x,y,w,h,size=24,color=INK,bold=False,align='left',name=None):
 return add('text',text=s,x=x,y=y,w=w,h=h,size=size,color=color,bold=bold,align=align,name=name or '文字_'+s.replace('\n','_')[:36])
def line(x1,y1,x2,y2,color=NAVY,sw=1.5,dash=False,arrow=False):
 return add('line',x=x1,y=y1,x2=x2,y2=y2,color=color,sw=sw,dash=dash,arrow=arrow,name='连线')
def poly(points,color=NAVY,sw=1.5,fill='none',closed=False,name='自由曲线'):
 return add('path',points=points,color=color,sw=sw,fill=fill,closed=closed,name=name)
def circle(x,y,d,fill,stroke='none',sw=1):return shape(x,y,d,d,fill,stroke,sw,geom='ellipse',name='圆形')
def number(n,x,y,color=BLUE,d=57):
 circle(x,y,d,f'linear(45deg, {color} 0%, {color} 100%)','#FFFFFF',1);text(str(n),x,y-1,d,d,36 if d>45 else 24,'#FFFFFF',True,'center','编号_'+str(n))
def bullet(s,x,y,w,size=23,color=BLUE,h=35,bold=False):
 shape(x,y+9,14,14,color);text(s,x+36,y,w-36,h,size,INK,bold)
def panel(x,y,w,h,title=None,color=RED,bar='#FBE3E4',th=48):
 shape(x,y,w,h,'#FFFFFF/87','#D7DBDF',1.2,16,'模块_'+(title or '背景'))
 if title:
  shape(x+1,y+1,w-2,th,f'linear(0deg, {bar} 0%, #FFFFFF/20 100%)',r=9,name='标题栏_'+title)
  text(title,x+18,y+4,w-32,th-6,30,color,True)
def crop(key,box,name,x=None,y=None,w=None,h=None,kind='原图裁切',diff='保留原图局部；内部细节为栅格图像'):
 im=images[key].crop(box); path=ASSETS/(name+'.png');im.save(path)
 x=box[0] if x is None else x;y=box[1] if y is None else y
 w=box[2]-box[0] if w is None else w;h=box[3]-box[1] if h is None else h
 add('image',file=path.name,x=x,y=y,w=w,h=h,name='插画_'+name)
 manifest.append({'name':name,'source':SOURCES[key],'region':box,'slide':SOURCES[current],'method':kind,'path':'assets/'+path.name,'prompt':None,'tool':'Pillow 精确裁切','known_difference':diff})
def icon(key,box,name,color=None,mode='dark',x=None,y=None,w=None,h=None):
 # 将单色图标的有意义闭合轮廓转成原生自由曲线，不逐像素建形。
 a=np.array(images[key].crop(box));r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 if mode=='white': mask=((r>215)&(g>215)&(b>215)).astype('uint8')*255
 elif mode=='red':mask=((r.astype(int)>g.astype(int)+45)&(r.astype(int)>b.astype(int)+35)&(g<170)).astype('uint8')*255
 elif mode=='blue':mask=((b.astype(int)>r.astype(int)+20)&(g<180)&(r<150)).astype('uint8')*255
 elif mode=='gray':mask=((r<195)&(g<195)&(b<195)).astype('uint8')*255
 elif mode=='green':mask=((g.astype(int)>r.astype(int)+14)&(g.astype(int)>b.astype(int)+5)&(r<170)).astype('uint8')*255
 else:mask=((r<175)&(g<180)&(b<205)).astype('uint8')*255
 cnts,hier=cv2.findContours(mask,cv2.RETR_EXTERNAL if mode=='gray' else cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
 paths=[]
 for c in cnts:
  if cv2.contourArea(c)<2:continue
  c=cv2.approxPolyDP(c,0.48,True).reshape(-1,2)
  if len(c)>2:paths.append(c.tolist())
 x=box[0] if x is None else x;y=box[1] if y is None else y
 w=box[2]-box[0] if w is None else w;h=box[3]-box[1] if h is None else h
 add('icon',x=x,y=y,w=w,h=h,vw=box[2]-box[0],vh=box[3]-box[1],paths=paths,fill=color or NAVY,name='图标_'+name)
def title(s,size=56):text(s,160,9,1450,78,size,'#FFFFFF',True,name='标题_'+s)
def begin(key):
 global elements,current
 elements=[];current=key
def finish():scenes.append({'source':SOURCES[current],'key':current,'elements':elements})

# 封面：沿用模板版式的校徽、校名及校门底纹。
begin('cover')
text('船舶设计Ⅱ课程设计',400,204,872,56,35,'#44546A',False,'center')
text('第一次汇报',350,265,972,104,88,'#C8161E',True,'center')
text('B组 | 33,500 DWT散货船母型改造设计',300,377,1072,60,37,'#44546A',False,'center')
text('汇报人：董昱彤（组长）',365,604,942,76,53,'#44546A',True,'center')
text('组员：林森崎 | 王弘毅 | 孟也然',350,691,972,55,35,'#44546A',False,'center')
text('2026年11月',550,804,572,48,30,'#44546A',False,'center')
finish()

# 本组设计任务。
begin('task');title('1. 本组设计任务')
panel(44,141,750,478,'设计背景')
bullet('以课程提供的母型船为基础，开展目标船型的方案设计',73,205,699,24,RED,38,True)
bullet('在满足任务书要求的前提下，完成总体布置、主要性能计算、',73,247,712,24,RED,38,True)
text('型线优化以及关键设计说明等工作。',113,282,645,39,24)
crop('task',(66,332,773,572),'母型船海上照片')
text('图 1  母型船示意图',180,578,480,35,22,INK,False,'center')
panel(44,628,750,242,'本组任务（B组）')
shape(66,687,707,165,'#FBE6E6',r=12)
text('以母型船为基准，按照课程设计指导书中B组的要求，',113,705,642,40,26)
text('完成满足特定任务需求的目标船型设计，并在经济性、',113,750,642,40,26)
text('适航性、操纵性等方面进行综合分析与评估。',113,795,642,40,26)
panel(820,142,820,335,'设计目标')
for cx,label,desc,box,n in [(965,'满足任务需求','在母型船基础上实现\n目标功能与性能要求',(934,242,998,298),'增长'),(1230,'综合性能优化','兼顾经济性、适航性、\n操纵性等多方面指标',(1198,239,1265,301),'齿轮'),(1494,'完成设计成果','形成完整、规范的\n设计报告与图纸',(1460,240,1526,301),'书本')]:
 circle(cx-56,213,112,RED);icon('task',box,n,'#FFFFFF','white')
 text(label,cx-126,334,252,42,28,'#080808',True,'center');text(desc,cx-132,380,264,73,23,INK,False,'center')
for x in [1075,1340]:text('+',x-5,229,62,72,77,'#F6CBCB',True,'center')
panel(820,508,820,334,'主要设计要求（摘自指导书）')
req=['船型在母型船基础上进行尺度与型线的合理调整；','满足货运任务需求及相关规范要求；','进行必要的性能计算与方案论证；','完成总体布置、主要结构与设备选型等设计内容；','提交设计说明书、主要图纸及相关计算书。']
for i,s in enumerate(req):
 number(i+1,844,577+i*51,RED,38);text(s,895,581+i*51,665,36,20)
icon('task',(1310,580,1604,665),'船舶侧视轮廓','#9BA0A4',mode='gray')
icon('task',(1310,705,1605,773),'船舶俯视轮廓','#A4A9AC',mode='gray')
for x in [1338,1368,1398,1428,1458,1488,1518]:shape(x,714,26,51,'#C2C5C7','#B6BABC',.5,name='俯视图_舱口')
shape(1321,726,12,27,'#E5E7E8',name='俯视图_艉部舱室')
line(1315,665,1615,665,'#7B858D',1,True);line(1315,704,1615,704,'#7B858D',1,True)
line(1315,662,1315,775,'#7B858D',1,True);line(1600,662,1600,775,'#7B858D',1,True)
text('L',1430,671,58,30,18,'#111111',False,'center');line(1611,707,1611,769,'#111111',1)
text('B',1615,724,22,28,18,'#111111')
finish()

# 设计路线。
begin('route');title('设计任务与总体设计路线')
for x,w,label,c in [(65,486,'35000 DWT母型船',RED),(626,421,'母型改造法',NAVY),(1120,486,'33500 t目标船',RED)]:
 shape(x,141,w,238,'#FFFFFF/85',c,1.2,16);text(label,x+8,151,w-16,58,36,c,True,'center')
crop('route',(89,202,533,311),'路线_母型船')
crop('route',(1144,202,1589,311),'路线_目标船')
for x,label,w in [(128,'参考母型',364),(652,'线性缩尺比 k = 0.986750',370),(1179,'B组设计任务',367)]:
 shape(x,322,w,41,'#DEE2E8/80',r=13);text(label,x,322,w,41,26,NAVY,False,'center')
icon('route',(644,224,800,286),'灰色船舶','#7D8794');icon('route',(880,228,1027,286),'红色船舶','#BD3036','red')
for x,y,w,h in [(565,226,49,56),(808,245,63,34),(1059,226,49,56)]:shape(x,y,w,h,'linear(0deg, #FBE2E4 0%, #C80918 100%)',geom='rightArrow',name='箭头_母型改造')
cards=[(65,'33500 t','目标载重量',(165,426,254,504),'载重量',RED),(378,'14 kn','设计服务航速',(476,430,574,500),'航速',NAVY),(692,'16000 n mile','续航力',(799,429,875,504),'地球',NAVY),(1006,'5个货舱','货舱数量',(1101,438,1202,502),'货舱',NAVY),(1320,'4×30 t起重机','甲板起货设备',(1425,426,1518,505),'起重机',NAVY)]
for x,a,b,box,n,c in cards:
 shape(x,410,290,201,'#FFFFFF/80','#CDDCE9',1.3,18);icon('route',box,n,c,'red' if c==RED else 'dark');text(a,x+4,508,282,54,37,RED,True,'center');text(b,x+4,559,282,43,26,NAVY,False,'center')
line(65,654,725,654,NAVY,.8);line(948,654,1608,654,NAVY,.8);text('总体设计主线',724,630,224,47,29,INK,True,'center')
stages=[(65,177,'主尺度',(93,700,140,748),'三角尺'),(288,190,'型线/模型',(304,700,362,749),'型线'),(524,176,'静水力',(549,703,602,747),'波浪'),(740,194,'总布置/舱容',(754,700,807,747),'总布置'),(974,180,'重量浮力',(989,698,1048,751),'天平'),(1199,167,'稳性',(1229,700,1290,749),'稳性'),(1412,196,'快速性/推进',(1430,697,1479,749),'推进')]
for i,(x,w,s,box,n) in enumerate(stages):
 shape(x,685,w,77,'#FCEEF0' if i%2==0 else '#EAF0F5','#EABCC0' if i%2==0 else '#C7D6E4',1.4,10);icon('route',box,n,NAVY);text(s,x+77,704,w-80,41,21,NAVY,True)
 if i<6:shape(x+w+8,712,33,24,'#8A99A6',geom='rightArrow')
shape(1258,782,350,61,'#FFFFFF/50','#BCC3C8',1,10)
text('船型：钢质、单机单桨、尾机型双壳散货船\n航区：国际无限航区',1278,787,325,51,17)
finish()

# 成员分工。
begin('team');title('成员分工',58)
members=[(56,150,726,276,RED,1,'董昱彤（组长）',['总体方案与设计组织','船型主尺度确定与性能目标分解','船体型线设计（与林森崎协作）','汇报材料整理与统筹']), (889,150,735,277,BLUE,2,'林森崎',['船体型线设计（与董昱彤协作）','船体几何参数计算与图纸绘制','船舶静水力性能计算','相关软件建模与数据处理']), (56,557,726,281,BLUE,3,'王弘毅',['船舶阻力性能分析','推进系统初步匹配','功率预估与经济性分析','相关仿真计算与结果整理']), (889,558,735,279,RED,4,'孟也然',['船舶重量与重心计算','舱室布置方案设计','装载工况与稳性初步分析','相关图纸绘制与规范校核'])]
for x,y,w,h,c,n,person,items in members:
 shape(x,y,w,h,'#FFFFFF/80',c,1.2,18);number(n,x+(84 if n==4 else 20),y+11,c,56);text(person,x+(159 if n==4 else 99),y+13,w-150,61,36,NAVY if c==BLUE else c,True)
 for j,s in enumerate(items):
  e=bullet(s,x+(49 if n==4 else 32),y+88+j*43,500,24,NAVY if c==BLUE else c,42)
  elements[-1]['color']='#111111'
crop('team',(482,221,763,400),'分工_船体模型');crop('team',(1325,216,1604,400),'分工_彩色模型',diff='原始彩色模型及色标原样保留，色标内极小数值无法辨读')
crop('team',(1273,589,1607,797),'分工_舱室工程图',diff='工程图中的细小编号不可辨读，保留原始证据')
# 左下曲线数据按图上像素跟踪，轴值按参考图原样抄录。
shape(412,579,351,250,'#FFFFFF');chartx,charty,cw,ch=482,594,247,174
for y,label in [(594,'500'),(635,'400'),(678,'300'),(722,'100')]:line(chartx,y,chartx+cw,y,'#C9C9C9',.8);text(label,433,y-12,39,25,15,'#111111',False,'right')
for x,label in [(482,'0'),(544,'5'),(605,'10'),(667,'15'),(729,'20')]:line(x,594,x,768,'#CCCCCC',.8);text(label,x-20,773,40,28,15,'#111111',False,'center')
line(482,594,482,768,'#111111',1.5);line(482,768,729,768,'#111111',1.5)
poly([(482,767),(513,762),(544,754),(575,742),(605,732),(636,718),(667,701),(698,677),(725,643)],BLUE,2.5)
poly([(482,767),(513,760),(544,749),(575,737),(605,726),(636,709),(667,687),(698,655),(725,613)],RED,2.5)
line(499,615,529,615,BLUE,2.5);line(499,639,529,639,RED,2.5);text('母型船',538,602,110,28,17,'#111111');text('目标船型',538,627,115,28,17,'#111111')
text('总阻力 (kN)',409,621,31,133,17,'#111111')['rotation']=270;text('航速 (kn)',528,800,170,27,18,'#111111',False,'center')
for pts,c in [([(627,427),(627,448),(640,462),(700,462)],RED), ([(1042,427),(1042,450),(1030,462),(968,462)],BLUE), ([(627,556),(627,534),(639,523),(700,523)],NAVY), ([(1042,556),(1042,535),(1030,523),(968,523)],RED)]:
 poly(pts,c,1.6);circle(pts[0][0]-5,pts[0][1]-5,10,c)
# 中央四段圆环，原生弧带自由曲线。
def ring(cx,cy,r,th,start,end,c):
 a=np.linspace(np.deg2rad(start),np.deg2rad(end),45)
 pts=[(cx+r*np.cos(t),cy+r*np.sin(t)) for t in a]+[(cx+(r-th)*np.cos(t),cy+(r-th)*np.sin(t)) for t in a[::-1]]
 poly(pts,'none',0,c,True,'环形分区')
for a,c in [(-88,BLUE),(2,RED),(92,NAVY),(182,'#C72226')]:ring(833,498,140,24,a,a+85,c)
circle(727,391,212,'#FFFFFF','#E0E0E0',1.5);icon('team',(788,409,879,477),'团队',NAVY)
text('B组',744,478,180,67,55,NAVY,True,'center');text('(4人)',750,539,169,52,39,NAVY,True,'center')
finish()

# 当前总体进展。
begin('progress');title('4. 当前总体进展')
progress=[(41,129,784,338,BLUE,1,'总体设计（成员一：董昱彤）',['主尺度方案确定','空船重量重心初值','阻力/快速性初算','主机候选方案比较','建立EEDI与成本计算框架']), (841,129,794,338,BLUE,2,'型线与三维建模（成员三：王弘毅）',['完成三维船体曲面模型','完成二维型线图','751个型值采样点整理','文件一致性核查','绘制典型横剖面分析图']), (41,496,784,336,ORANGE,3,'总布置与设备（成员二：林森崎）',['总布置方案设计','主要舱室与设备布置','技术规格书编制','机舱布置与系统设计','文档标准化']), (841,496,794,336,ORANGE,4,'舱容与稳性（成员四：孟也然）',['货舱与舱容计算','装载工况制定','完整稳性计算','舱容图与稳性曲线','与总体方案的匹配校核'])]
for x,y,w,h,c,n,s,items in progress:
 panel(x,y,w,h);shape(x+1,y+1,w-2,65,'#E7F0FB' if c==BLUE else '#FFF2E4',r=13);number(n,x+(166 if n==4 else 13),y+7,c,54);text(s,x+(236 if n==4 else 82),y+13,w-93,43,26,NAVY if c==BLUE else RED,True)
 px=520 if n==3 else 1434 if n==4 else x+w-238;pw=185 if n>2 else 224
 shape(px,y+16,pw,42,TEAL if c==BLUE else '#E87409',r=23)
 if n<3:poly([(px+14,y+37),(px+21,y+44),(px+35,y+28)],'#FFFFFF',3)
 else:
  circle(px+12,y+25,21,'none','#FFFFFF',1.8);line(px+23,y+29,px+23,y+36,'#FFFFFF',1.6);line(px+23,y+36,px+29,y+39,'#FFFFFF',1.6)
 text('已完成可核验结果' if c==BLUE else '组员成果待并入',px+47,y+20,pw-50,32,20 if n<3 else 18,'#FFFFFF',True)
 bx=x+52 if n==2 else x+21 if n!=4 else x+120;by=y+85
 shape(bx,by,265 if n!=2 else 345,229,'#F0F5FB' if c==BLUE else '#FFF8EF',r=12)
 for j,ss in enumerate(items):bullet(ss,bx+24+(62 if n==2 and j==3 else 85 if n==2 and j==4 else 0),by+12+j*43,360,21,c,36)
crop('progress',(334,246,698,337),'进展_侧视图');crop('progress',(335,349,615,419),'进展_俯视图')
line(349,236,692,236,NAVY,1);line(349,232,349,247,NAVY);line(692,231,692,247,NAVY);text('Lₚₚ = 169.721 m',411,203,250,31,19,NAVY,False,'center')
line(701,256,701,332,NAVY,1);text('D = 14.407 m',710,277,117,29,19,NAVY)
line(622,354,622,417,NAVY,1);text('B = 28.418 m',626,370,166,30,19,NAVY)
crop('progress',(1189,203,1614,320),'进展_蓝色船体');crop('progress',(1250,320,1605,453),'进展_型线工程图',diff='原图内的小号工程编号不可辨读，保留图像')
crop('progress',(359,579,785,797),'进展_总布置工程图',diff='原图工程细节和极小编号保留为图像')
crop('progress',(1259,578,1606,706),'进展_舱容模型')
# 稳性曲线按参考图像素保留折线位置，文字可编辑。
for xx in range(1407,1615,35):line(xx,663,xx,773,'#D7D7D7',.6)
for yy in [675,699,723,747,773]:line(1407,yy,1614,yy,'#D7D7D7',.6)
poly([(1408,770),(1425,743),(1443,721),(1463,697),(1483,681),(1495,678),(1513,683),(1532,694),(1554,713),(1575,734),(1595,754),(1613,770)],'#9D9D9D',1.2)
for j,s in enumerate(['0','10','20','30','40','50','60']):text(s,1394+j*34.3,774,25,19,10,'#999999',False,'center')
for yy,s in [(666,'2.0'),(690,'1.5'),(714,'1.0'),(738,'0.5'),(764,'0.0')]:text(s,1375,yy,25,17,10,'#999999',False,'right')
text('GZ (m)',1363,701,17,57,11,'#999999')['rotation']=270;text('Heel Angle (°)',1443,795,150,21,11,'#999999',False,'center')
for a,c in [(-88,'#82C0EC'),(2,'#F4AF60'),(92,'#F9CF9C'),(182,'#65ADE0')]:
 ring(836,486,163,22,a,a+85,c)
 t=np.deg2rad(a+88);px=836+152*np.cos(t);py=486+152*np.sin(t)
 tx=-np.sin(t);ty=np.cos(t);nx=np.cos(t);ny=np.sin(t)
 poly([(px+tx*12,py+ty*12),(px-tx*9+nx*16,py-ty*9+ny*16),(px-tx*9-nx*16,py-ty*9-ny*16)],'none',0,c,True,'圆环箭头')
circle(697,347,278,'#FFFFFF');icon('progress',(805,358,870,409),'中央船舶',NAVY)
text('当前阶段重点',725,416,224,40,26,NAVY,True,'center');text('由 “分别完成”\n转向 “相互验证”',710,458,250,87,32,RED,True,'center')
line(811,553,860,553,NAVY,1);text('建立统一的设计状态\n形成闭环设计方案',738,566,196,50,18,NAVY,False,'center')
stages=['主尺度方案','型线/模型','静水力','总布置/舱容','重量浮力','稳性','快速性/推进','能效与成本']
for i,s in enumerate(stages):
 x=45+i*177;shape(x,854,168,41,'#D9E6F2' if i<7 else '#F9DFC4',geom='chevron');text(s,x+10,858,142,31,19,NAVY if i<7 else ORANGE,False,'center')
finish()

# 主尺度、阻力与推进比选。
begin('results');title('5. 阶段成果①：总体设计与快速性初估')
panel(44,116,743,743,'5.1 主尺度方案（母型改造法初始方案）')
crop('results',(67,226,653,346),'成果_船侧视图');crop('results',(61,375,640,479),'成果_船俯视图')
line(113,213,662,213,NAVY,1.3);line(113,206,113,250,NAVY,.7);line(662,206,662,274,NAVY,.7)
text('Lₚₚ = 169.721 m',276,176,266,36,21,NAVY,False,'center');line(668,240,668,342,NAVY,1.3);text('D = 14.407 m',674,274,110,35,19,NAVY)
line(647,378,647,479,NAVY,1.3);text('B = 28.418 m',657,415,128,34,19,NAVY)
headers=['参数','母型\n(35000 DWT)','新船初始方案\n(33500 DWT)','单位']
rows=[['总长 LOA','179.880','177.4966','m'],['垂线间长 Lpp','172.000','169.7210','m'],['型宽 B','28.800','28.4184','m'],['型深 D','14.600','14.4066','m'],['满载参考吃水','10.270','10.1339','m'],['性能参考吃水','9.830','9.6998','m'],['目标载重量 DWT','34867.7（对应状态）','33500','t'],['空船重量（初估）','8650','8310.7','t'],['满载参考排水量','43517.7','41810.7','t']]
def table(x,y,widths,headers,rows,rh=30,hh=52,size=19):
 x0=x
 for i,w in enumerate(widths):
  shape(x0,y,w,hh,'#C51A21','#FFFFFF',.7);text(headers[i],x0+8,y+1,w-16,hh-2,size,'#FFFFFF',True,'left' if i==0 else 'center');x0+=w
 for j,row in enumerate(rows):
  x0=x
  for i,w in enumerate(widths):
   shape(x0,y+hh+j*rh,w,rh,'#EAF0F6' if j%2==0 else '#FFFFFF/70','#D5DFE7',.4);text(row[i],x0+8,y+hh+j*rh,w-16,rh,size,NAVY,False,'left' if i==0 else 'center');x0+=w
table(61,500,[178,210,230,93],headers,rows,30.5,52,19)
panel(806,116,833,442,'5.2 阻力与快速性计算结果（性能参考吃水 9.699753 m）')
# 坐标网格、轴标与曲线均为原生对象；非标注点按原图位置追踪。
for j in range(7):
 y=440-j*37.5;line(900,y,1253,y,'#DFE5ED',.8);text(['0','200','400','600','800','1,000','1,200'][j],839,y-13,49,27,17,NAVY,False,'right')
for j in range(6):
 x=900+j*70.4;line(x,215,x,440,'#DFE5ED',.8);text(str(j+11),x-21,444,42,29,17,NAVY,False,'center')
line(900,214,900,440,'#73859D',1.2);line(900,440,1253,440,'#73859D',1.2);line(1253,214,1253,440,'#73859D',1.2)
for j,s in enumerate(['0','2,000','4,000','6,000','8,000']):text(s,1267,428-j*56,56,27,16,NAVY)
text('总阻力 Rₜ (kN)',812,278,35,137,19,NAVY)['rotation']=270;text('有效功率 Pₑ (kW)',1320,263,33,148,18,NAVY)['rotation']=270
text('航速 V (kn)',1016,467,180,29,19,NAVY,False,'center')
bluepts=[(900,422),(965,411),(1030,397),(1104,377),(1178,353),(1253,328)]
redpts=[(900,415),(965,401),(1030,381),(1104,353),(1178,319),(1253,276)]
poly(bluepts,BLUE,2.3);poly(redpts,'#D21A22',2.3)
for x,y in bluepts:circle(x-4.5,y-4.5,9,BLUE)
for x,y in redpts:shape(x-4.5,y-4.5,9,9,'#C51C22')
line(1104,378,1104,440,NAVY,1,True);line(938,190,973,190,BLUE,2.2);circle(951,186,8,BLUE);text('总阻力 Rₜ',978,174,115,29,17,NAVY)
line(1089,190,1123,190,RED,2.2);shape(1102,186,8,8,RED);text('有效功率 Pₑ',1129,174,135,29,17,NAVY)
shape(1062,226,149,78,'#F3F8FE',NAVY,.8,5);text('14 kn\nRₜ=478.991 kN\nPₑ=3449.505 kW',1076,229,138,72,18,NAVY);line(1105,304,1105,340,RED,1.5,arrow=True)
shape(1364,170,260,317,'#E5F0FF',r=12);text('14 kn 典型结果',1378,173,235,39,24,NAVY,True)
metrics=[('总阻力 Rₜ','478.991 kN',(1390,226,1434,262),'小船'),('有效功率 Pₑ','3449.505 kW',(1386,285,1439,332),'螺旋桨'),('计算吃水','9.699753 m',(1384,356,1440,392),'波浪'),('对应航速','14 kn',(1384,424,1441,466),'速度表')]
for j,(a,b,box,n) in enumerate(metrics):
  y=214+j*66.5;shape(1376,y,236,59,'#FFFFFF',r=8);icon('results',box,n,BLUE if j==2 else NAVY,'blue' if j==2 else 'dark');text(a,1454,y+3,152,28,19,NAVY);text(b,1453,y+28,158,29,23,NAVY,True)
text('注：以上结果基于性能参考吃水 9.699753 m，用于阶段方案评价，\n    不等同于 33500 t 满载状态的最终航速与功率，待静水力结果返回后复算。',824,499,798,55,19,NAVY)
panel(806,569,833,290,'5.3 推进方案初步比选')
for x,c,lab,model,pow,rpm,v in [(823,BLUE,'候选方案 A','5G45ME-C9.7','6950 kW','111 rpm','≈ 14.42 kn'),(1224,TEAL,'候选方案 B','6S40ME-C9.5','6810 kW','146 rpm','≈ 14.44 kn')]:
 shape(x,625,383 if x==823 else 400,161,'#EAF3FF' if c==BLUE else '#E9F7F8','#C3DCEC',1,12);shape(x,625,163,36,c,r=18);text(lab,x+20,624,150,37,24,'#FFFFFF',True)
 text(model,x+172,660,220,36,23,c,True)
 for j,s in enumerate(['额定功率：'+pow,'额定转速：'+rpm,'CSR 估算航速：'+v]):
  bullet(s,x+163,700+j*27,232,17,c,28);elements[-1]['x']-=17;elements[-1]['w']+=17;elements[-2]['w']=9;elements[-2]['h']=9
crop('results',(844,666,975,781),'主机A');crop('results',(1246,667,1383,782),'主机B')
shape(823,793,802,60,'#FDEEF0',r=10);icon('results',(830,794,888,848),'方案比选靶标',RED,'red')
text('两套主机方案在相同桨径上限条件下均可满足 14 kn 阶段性目标，\n主机尚未定型，需结合最终船型、尾部净空、EEDI 及总体布置进一步确定。',902,795,717,57,20,NAVY)
finish()

# 型线与三维建模。
begin('model');title('6. 阶段成果②：型线设计与三维建模')
panel(43,116,896,410,'6.1 三维船体模型');panel(953,116,683,410,'6.2 二维型线图成果')
# 原船体含三处背景内标注，裁成一个独立船体素材，文字区域在提取时不进入主体可见区域。
crop('model',(53,166,925,520),'三维船体模型_原始局部',diff='提取时将叠加标注区域设为透明；船体像素未生成或修复，三个标注另建为原生对象')
for pts in [[(60,371),(113,371),(126,311),(122,371),(176,371),(176,434),(60,434)],[(314,436),(366,436),(408,383),(378,436),(430,436),(430,500),(314,500)],[(827,426),(934,426),(934,489),(827,489),(827,465),(790,454),(827,456)]]:
 poly(pts,NAVY,1.2,'#E4F1FD',True,'原生标注框')
for x,y in [(126,310),(408,383),(790,454)]:circle(x-5,y-5,10,'#A9D9F5',BLUE,.6)
for s,x,y,w in [('艉部收缩\n线型顺畅',67,374,103),('丰满中体\n型线光顺',321,438,102),('球鼻艏\n改善兴波',833,429,96)]:text(s,x,y,w,57,20,NAVY,True,'center')
crop('model',(965,172,1615,483),'二维型线图',diff='工程图内部的极小表格和站位标号原图模糊，未虚构或转写，作为原始图像保留')
text('图  组员已校验的型线图（横剖线、纵剖线、半宽水线图等）',985,488,625,31,18,NAVY,False,'center')
panel(43,539,896,304,'6.3 典型横剖面型线');panel(953,537,683,315,'6.4 型值数据与文件一致性核查')
sections=[(86,'ST 2','(艉部)',(87,668,219,787)),(262,'ST 6','(前中部)',(263,668,396,787)),(438,'ST 10','(中部)',(440,668,571,787)),(614,'ST 16','(后中部)',(618,668,748,787)),(789,'ST 20.25','(艏部/球鼻艏)',(794,668,926,787))]
for x,s,cap,b in sections:
 shape(x,595,132,31,'#1766A9',r=5);text(s,x,596,132,29,19,'#FFFFFF',True,'center');text(cap,x-18,627,168,29,18,NAVY,False,'center');crop('model',b,'横剖面_'+s.replace(' ','_'))
 for j,v in enumerate(['-15','-10','-5','0','5','10','15']):text(v,x-8+j*22,790,25,18,9,NAVY,False,'center')
 for yy,v in [(663,'15'),(692,'10'),(722,'5'),(752,'0.5'),(780,'0')]:text(v,x-27,yy,22,18,10,NAVY,False,'right')
 text('Y (m)',x+33,811,65,21,11,NAVY,False,'center');text('Z (m)',x-38,707,18,54,11,NAVY)['rotation']=270
for x,w,n,s in [(970,148,'751','型值采样点'),(1126,147,'31','不同站位'),(1281,147,'32','站位/分支组')]:
 shape(x,589,w,80,'#E4F0FD',r=8);text(n,x,588,w,53,40,'#145486',True,'center');text(s,x,636,w,29,18,NAVY,True,'center')
shape(1437,589,185,80,'#E4F0FD',r=8);circle(1449,612,28,TEAL);poly([(1456,626),(1461,631),(1470,620)],'#FFFFFF',2.5);text('CSV / Markers /\n三维 DXF 点集\n已完成一致性核查',1488,595,132,68,16,NAVY)
table(970,678,[205,447],['校核项目','结果'],[
 ['型值点与站位','751点，31个不同站位，32个站位分支组'],['分支分布','主船体736点；球鼻艏12点；上舱部3点'],['纵坐标范围','-3.157600 ～ 171.842526 m'],['半宽与高度范围','Y：0 ～ 14.209201 m；Z：0 ～ 14.899926 m'],['最大半宽核对','2 × 14.209201 = 28.418402 m（与型宽一致）']],27,28,17)
shape(43,856,1282,47,'#E5F0FC',geom='chevron');circle(64,862,38,BLUE);text('!',64,861,38,39,29,'#FFFFFF',True,'center');text('当前证明是型值数据在不同文件间的传递一致，曲面公平性、接缝、水密性及与当前MSD切剖的一致性仍待进一步验证。',116,862,1196,35,20,NAVY,True)
finish()

# 困难与措施闭环。
begin('issues');title('7. 存在的困难与解决措施')
issue_rows=[
 (117,237,BLUE,'船型模型与静水力的闭合',['型值数据已基本一致\n（751点，31站位）','三维模型文件已整理','已有型线图初步成果'],['曲面公平性、接缝、水密性尚未验证','与当前MSD重新切剖的型线对照尚未完成','缺少同版本模型的静水力正式输出','当前难以确定满载浮态与排水量的闭合关系'],['冻结唯一的MSD版本，进行曲面检查\n（接缝、公平性、法向等）','统一坐标系与单位重新切剖生成型线，\n与现有型线图逐站对照','当前同版本静水力报告，得到排水量、LCB、\nLCF、MTC、KM等参数','在此基础上确定各工况吃水与浮态']),
 (371,244,ORANGE,'重量—浮力—舱容的统一',['空船重量初估 8310.7 t','已完成17个分区复核','建立了重量表模板','货舱布置与装载方案\n框架已确定'],['空船重量仍为几何相似初值，未进行独立\n结构/设备重量校核','舱容和实际装载工况尚未完成','33500 t为载重量，包含货物、油水、人员\n和备品，尚不能直接等同为货物重量','缺少与静水力的相互验证，无法形成完整\n重量—浮力闭合'],['完善总布置与舱容计算，给出各舱装载方案\n与实际载荷及重心','在组内统一工况下，建立完整的重量重心表','将重量结果与静水力排水量进行对照与迭代','明确各工况下的平均吃水、LCB、LCF 等参数']),
 (633,219,BLUE,'快速性—推进—总布置的匹配',['已完成母型阻力复算','新船14 kn阻力初算','主机两方案初步比选\n（≈14.42 / 14.44 kn）','桨径上限约 5.2298 m'],['当前阻力结果基于性能参考吃水，尚未在\n统一满载状态下复算','主机与桨的最终选型尚未定型','尾部净空、机舱布置与设备选型尚未统一','EEDI 和续航力计算仍十部分关键输入'],['在确定最终船型和满载吃水后，重新计算阻力','结合尾部型线和总布置，校核桨径、尾部净空','根据阻力与航速需求，确定主机/桨最终方案','完善 EEDI、续航力等计算，形成可行的推进\n与能效方案'])]
for idx,(y,h,c,heading,left,mid,right) in enumerate(issue_rows):
 panel(41,y,613,h);shape(42,y+1,611,52,'#DDEBFA' if c==BLUE else '#FCEBD5',r=14);number(idx+1,42,y-2,c,58);text(heading,114,y+6,535,43,28,'#114D80' if c==BLUE else '#C14B00',True)
 shape(403,y+60,246,h-69,'#F0F7FF' if c==BLUE else '#FFF8EF',r=11)
 ly=y+(58 if idx==2 else 58 if idx==1 else 72)
 for s in left:bullet(s,420,ly,226,19,c,53 if '\n' in s else 34);ly+=57 if '\n' in s else 33
 panel(699,y,400,h);shape(700,y+1,398,45,'#FBE2E4',r=12);text('主要问题与原因',719,y+5,363,37,22,RED,True)
 ly=y+58
 for s in mid:
  bullet(s,719,ly,381,19,c if idx else RED,56 if '\n' in s else 37);elements[-1]['x']-=8;elements[-1]['w']+=8;ly+=(46 if idx==0 else (51 if '\n' in s else 31))
 panel(1168,y,468,h);shape(1169,y+1,466,38,'#D4EFEE' if idx==0 else '#FBEBD6' if idx==1 else '#DEEBFA',r=12);text('解决思路与措施',1189,y+2,429,36,22,TEAL if idx==0 else c,True)
 ly=y+43
 for s in right:bullet(s,1192,ly,432,19,TEAL if idx==0 else c,57 if '\n' in s else 35);ly+=54 if '\n' in s else 34
 for x in [663,1125]:shape(x,y+98,34,55,'#F5CBCD' if idx==0 else '#F8DBC1' if idx==1 else '#CCE0F3',geom='chevron',name='箭头_问题到措施')
crop('issues',(49,180,396,347),'困难_蓝色船体');crop('issues',(51,432,394,606),'困难_货舱船体');crop('issues',(72,695,367,844),'困难_尾部螺旋桨')
shape(90,861,1224,55,'#F1F7FF','#BEDCF6',1.4,28);icon('issues',(114,863,174,915),'核心靶标',RED,'red');text('核心思路：',187,867,173,42,29,RED,True)
for s,x,w in [('统一模型与设计状态',359,260),('各专业成果相互验证',675,260),('形成一套闭环的设计方案',998,302)]:text(s,x,869,w,39,25,NAVY,True)
line(615,889,642,889,BLUE,2,arrow=True);line(935,889,962,889,BLUE,2,arrow=True)
finish()

# 进度规划。
begin('plan');title('8. 11月2日—12月4日 进度规划')
line(40,153,1635,153,BLUE,2.5,arrow=True)
phases=[(40,374,BLUE,'11.02 — 11.09','统一设计基准',['梳理并冻结主要设计输入','• 主尺度与缩放参数\n• 坐标系与单位体系\n• 性能/满载/压载工况定义','统一数据表与文件版本管理','明确各专业接口与传递格式'],'形成唯一统一的设计输入表\n（主尺度、吃水、排水量、重心）'),(419,405,ORANGE,'11.10 — 11.18','模型与布置交叉验证',['完成三维模型曲面检查\n（接缝、公平性、水密性等）','与型线图重新切剖对照','总布置方案初步完成\n（货舱布置、机舱布置、主要设备）','输出同版本静水力参数\n（排水量、LCB、LCF、MTC、KM 等）'],'船型—布置基本一致\n模型可用于性能与舱容计算'),(830,409,GREEN,'11.19 — 11.27','重量—浮力—性能闭环',['完成主要舱容计算与装载工况制定','更新重量重心并与静水力闭合','开展完整稳性计算','基于最终船型重算阻力与推进\n（主机/桨选型、尾部净空校核）','开展 EEDI、续航力等进一步计算'],'形成第一轮完整设计状态\n（型线、布置、舱容、重量、稳性、快速性）'),(1247,389,RED,'11.28 — 12.04','方案收敛与成果整理',['各专业成果迭代完善与相互校核','确定主机、桨与主要设备方案','完善 EEDI、续航力和成本估算','编制设计报告、技术规格书\n及各类计算书与图纸','完成第二次汇报材料'],'12月4日：完成第二次汇报材料\n进入方案定型阶段')]
for i,(x,w,c,date,heading,items,mile) in enumerate(phases):
 text(date,x,115,w,35,24,NAVY,True,'center');circle(x+w/2-7,146,14,'#EAF3FA',c,2)
 shape(x,166,w,70,'#D6E8FA' if i==0 else '#FCE7CF' if i==1 else '#D9EDDF' if i==2 else '#FAD9DB',geom='chevron');number(i+1,x+12,169,c,61);text(heading,x+93,182,w-102,47,28,NAVY if i==0 else c,True)
 panel(x,236,w,392);ly=251
 for j,s in enumerate(items):
  if i==0 and j==1:text(s,x+50,284,w-58,99,20,NAVY);ly=396;continue
  bullet(s,x+19,ly,w-26,21,c,64 if '\n' in s else 41);ly+=72 if '\n' in s else 44
 shape(x+10,498,w-20,121,'#EFF7FF' if i==0 else '#FFF3E7' if i==1 else '#EFF9F3' if i==2 else '#FFF1F2',r=12)
 icon('plan',[(57,504,96,550),(450,503,490,551),(855,503,896,552),(1275,503,1318,550)][i],'里程碑旗帜'+str(i),c,'blue' if i==0 else 'red' if i in [1,3] else 'green')
 text('里程碑 M'+str(i+1),x+65,505,w-76,40,26,c,True);text(mile,x+13,549,w-26,63,21,NAVY,False,'center')
panel(40,640,1047,232);shape(40,640,272,42,'#276AA7',r=21);text('整体进度示意',64,642,240,36,25,'#FFFFFF',True)
dates=[(356,'11.02'),(502,'11.09'),(680,'11.18'),(862,'11.27'),(1052,'12.04')]
line(278,705,1053,705,'#4782B4',1.4)
for x,s in dates:
 text(s,x-37,673,74,29,17,NAVY,False,'center');circle(x-5,700,10,'#5792C7');line(x,711,x,862,'#8AA7C8',1,True)
for j,(s,x1,x2,x3,c) in enumerate([('总体设计（董昱彤）',356,613,955,'#369DE1'),('总布置与设备（林森崎）',521,914,975,'#E78A3C'),('型线与三维建模（王弘毅）',492,818,968,'#49A06A'),('舱容与稳性（孟也然）',592,932,1000,'#DC5F62')]):
 y=713+j*36;line(278,y+36,1053,y+36,'#DEE6EF',.8);text(s,63,y+1,215,32,20,NAVY);shape(x1,y+7,x3-x1,22,c+'/25',r=4);shape(x1,y+7,x2-x1,22,c,r=4)
panel(1110,641,526,231);shape(1118,645,243,50,'#2B6FAA',r=25);icon('plan',(1128,648,1176,695),'最终目标', '#FFFFFF','white');text('最终目标',1198,651,150,39,27,'#FFFFFF',True)
for j,s in enumerate(['一套统一船型、统一工况、相互校核的\n完整设计方案','满足 33500 t 载重量、14 kn 航速、\n16000 n mile 续航等任务要求','提交完整的设计文件并完成第二次汇报']):
 yy=[708,766,828][j];shape(1128,yy+3,22,22,'#3899DD',r=3);poly([(1132,yy+14),(1138,yy+20),(1147,yy+8)],'#FFFFFF',2.3);text(s,1164,yy,459,59 if j<2 else 35,21,NAVY)
crop('plan',(1464,713,1622,833),'规划_船舶线稿')
finish()

# 针对实际渲染后发现的问题进行局部修正，保留原图模块坐标。
for scene in scenes:
 es=scene['elements'];key=scene['key']
 if key=='task':
  for e in es:
   if e['kind']=='text' and e['text'] in req:e['size']=19
  for e in list(es):
   if e['kind']=='text' and e['text']=='+':
    es.remove(e);es.append({'kind':'shape','x':e['x']+5,'y':251,'w':44,'h':44,'fill':'#F6CBCB','stroke':'none','sw':0,'r':0,'name':'图形_加号','geom':'mathPlus'})
  for e in es:
   if e['kind']=='text' and e['text'].startswith(('以母型船为基准','完成满足特定','适航性、操纵性')):
    e['emphasis']=[{'text':s,'color':RED,'bold':True} for s in ['B组','目标船型设计','经济性、','适航性、操纵性'] if s in e['text']]
 if key=='results':
  for e in es:
   if e['kind']=='text' and e['text'].startswith('两套主机方案'):
    e['emphasis']=[{'text':s,'color':RED,'bold':True} for s in ['可满足 14 kn 阶段性目标','主机尚未定型']]
   if e['kind']=='text' and e['text'].startswith('D ='):e['size']=16.5;e['w']=113
   if e['kind']=='text' and e['text'].startswith('14 kn\n'):e['size']=16.5;e['x']=1074;e['w']=136
 if key=='route':
  for e in es:
   if e['kind']=='text' and e['text'] in ['总布置/舱容','快速性/推进']:e['size']=19.5
   if e['kind']=='text' and e['text'].startswith('船型：'):e['size']=16.5
 if key=='issues':
  for e in es:
   if e['kind']=='text' and e['text'].startswith(('当前难以确定','33500 t为载重量','空船重量初估','主机两方案初步比选')):e['size']=18
   if e['kind']=='text' and e['text'].startswith('主机两方案初步比选'):e['w']=198;e['x']=450
 if key=='plan':
  p=ASSETS/'规划_船舶线稿.png';im=Image.open(p).convert('RGBA');arr=np.array(im);rgb=arr[:,:,:3].astype(int)
  # 灰色船舶线稿与叠在其左上方的蓝色正文按色相分离，避免把文字烘焙进图片。
  keep=(rgb.max(axis=2)-rgb.min(axis=2)<18)&(rgb.min(axis=2)>135)&(rgb.min(axis=2)<249)
  arr[:,:,3]=np.where(keep,255,0).astype('uint8');Image.fromarray(arr).save(p)
  for m in manifest:
   if m['name']=='规划_船舶线稿':m['method']='原图裁切及灰度主体提取，排除蓝色正文';m['alpha_verified']=True;m['known_difference']='极浅背景转为透明；少量接近正文颜色的线稿边缘可能减弱'
  for e in es:
   if e['kind']=='text' and e['text'].startswith(('输出同版本静水力参数','形成第一轮完整设计状态')):e['size']=19
   if e['kind']=='text' and e['text'] in ['总布置与设备（林森崎）','型线与三维建模（王弘毅）']:e['size']=18;e['w']=234
  # 船舶线稿是独立素材，置于本模块正文下方以保留完整可读文本。
  im=next(e for e in es if e['kind']=='image' and e['file']=='规划_船舶线稿.png');es.remove(im)
  idx=next(i for i,e in enumerate(es) if e['kind']=='text' and e['text'].startswith('一套统一船型'))
  es.insert(idx-2,im)
 if key=='model':
  p=ASSETS/'三维船体模型_原始局部.png';im=Image.open(p).convert('RGBA');a=Image.new('L',im.size,255);d=ImageDraw.Draw(a)
  # 完整排除原图标注的文本框及箭头区域，再由幻灯片中的原生形状填入。
  for pts in [[(59,370),(112,370),(128,308),(125,370),(177,370),(177,435),(59,435)],[(313,435),(365,435),(410,381),(380,435),(431,435),(431,501),(313,501)],[(826,425),(936,425),(936,490),(826,490),(826,467),(788,456),(788,452),(826,454)]]:
   d.polygon([(x-53,y-166) for x,y in pts],fill=0)
  im.putalpha(a);im.save(p)
  for m in manifest:
   if m['name']=='三维船体模型_原始局部':m['method']='原图裁切与标注区域透明排除';m['tool']='Pillow 精确裁切及 Alpha 遮罩；未调用生成模型';m['alpha_verified']=True
 if key=='progress':
  for e in es:
   if e['kind']=='text' and e['text'].startswith('D ='):e['size']=17;e['w']=117
   if e['kind']=='text' and e['text'].startswith('B ='):e['size']=18
   if e['kind']=='text' and e['text'].startswith('由 “分别完成”'):e['x']=697;e['w']=278;e['size']=30
  # 透明度较低的工程图背景与圆环不能遮住外围参数和任务文本。
  texts=[e for e in es if e['kind']=='text'];es[:]=[e for e in es if e['kind']!='text']+texts
  p=ASSETS/'进展_舱容模型.png';im=Image.open(p).convert('RGBA');a=Image.new('L',im.size,255);ImageDraw.Draw(a).rectangle((1399-1259,650-578,347,128),fill=0);im.putalpha(a);im.save(p)
  for m in manifest:
   if m['name']=='进展_舱容模型':m['method']='原图裁切并排除相邻图表区域';m['alpha_verified']=True
 # 尺度线的双向箭头按照参考图端点补齐。
 if key in ['results','progress']:
  dims=[(113,213,662,213),(668,240,668,342),(647,378,647,479)] if key=='results' else [(349,236,692,236),(701,256,701,332),(622,354,622,417)]
  for x1,y1,x2,y2 in dims:
   for x,y,tx,ty in [(x1,y1,x2-x1,y2-y1),(x2,y2,x1-x2,y1-y2)]:
    norm=(tx*tx+ty*ty)**.5;tx/=norm;ty/=norm
    pts=[(x,y),(x+tx*6-ty*2.5,y+ty*6+tx*2.5),(x+tx*6+ty*2.5,y+ty*6-tx*2.5)]
    es.append({'kind':'path','points':pts,'color':'none','sw':0,'fill':NAVY,'closed':True,'name':'尺寸线箭头'})

# 与 Windows 资源管理器一致的文件名自然排序。
import ctypes, functools
cmp=ctypes.windll.shlwapi.StrCmpLogicalW
cmp.argtypes=[ctypes.c_wchar_p,ctypes.c_wchar_p];cmp.restype=ctypes.c_int
scenes.sort(key=functools.cmp_to_key(lambda a,b:cmp(a['source'],b['source'])))
(ROOT/'source'/'scenes.json').write_text(json.dumps(scenes,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'asset_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('页面',len(scenes),'元素',sum(len(s['elements']) for s in scenes),'素材',len(manifest))
