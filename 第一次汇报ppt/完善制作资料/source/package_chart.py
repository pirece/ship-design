"""将精确绘图转换为带双纵轴的原生 PowerPoint 图表，并设置中文字体。"""
from pathlib import Path
from lxml import etree as E
import zipfile,json
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'source/data.json').read_text(encoding='utf-8'))
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main';C='http://schemas.openxmlformats.org/drawingml/2006/chart';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';REL='http://schemas.openxmlformats.org/package/2006/relationships'
N={'p':P,'a':A,'c':C,'r':R}
with zipfile.ZipFile(ROOT/'.build/raw.pptx') as z:parts={n:z.read(n) for n in z.namelist()}
def child(parent,tag,**attrs):
 ns,name=tag.split(':');el=E.SubElement(parent,'{'+N[ns]+'}'+name,**{k:str(v) for k,v in attrs.items()});return el
def cv(parent,tag,value):return child(parent,'c:'+tag,val=value)
def fill(parent,color):child(child(parent,'a:solidFill'),'a:srgbClr',val=color)
def stroke(parent,color,width=9525):
 ln=child(parent,'a:ln',w=width);fill(ln,color);child(ln,'a:prstDash',val='solid')
def textstyle(parent,size=1350,color='566575',bold=False):
 tx=child(parent,'c:txPr');child(tx,'a:bodyPr');child(tx,'a:lstStyle');para=child(tx,'a:p');pp=child(para,'a:pPr');rp=child(pp,'a:defRPr',sz=size,b=int(bold));fill(rp,color);child(rp,'a:latin',typeface='Microsoft YaHei');child(rp,'a:ea',typeface='Microsoft YaHei');child(para,'a:endParaRPr',lang='zh-CN');return tx
def layout(parent,x,y,w,h,target=None):
 la=child(parent,'c:layout');m=child(la,'c:manualLayout')
 if target:cv(m,'layoutTarget',target)
 for k in ['xMode','yMode','wMode','hMode']:cv(m,k,'factor')
 for k,v in [('x',x),('y',y),('w',w),('h',h)]:cv(m,k,v)
def title(parent,text,size,color,coords):
 t=child(parent,'c:title');tx=child(t,'c:tx');rich=child(tx,'c:rich');child(rich,'a:bodyPr',wrap='none');child(rich,'a:lstStyle');pp=child(rich,'a:p');pr=child(pp,'a:pPr',algn='l');rp=child(pr,'a:defRPr',sz=size,b=1);fill(rp,color);child(rp,'a:latin',typeface='Microsoft YaHei');child(rp,'a:ea',typeface='Microsoft YaHei');run=child(pp,'a:r');rr=child(run,'a:rPr',sz=size,b=1);fill(rr,color);child(rr,'a:latin',typeface='Microsoft YaHei');child(rr,'a:ea',typeface='Microsoft YaHei');child(run,'a:t').text=text;layout(t,*coords);cv(t,'overlay',1);return t
chart=E.Element('{'+C+'}chartSpace',nsmap={'c':C,'a':A,'r':R});cv(chart,'date1904',0);cv(chart,'lang','zh-CN');cv(chart,'roundedCorners',0)
ch=child(chart,'c:chart');title(ch,f"性能参考吃水 T = {D['T_performance']:.6f} m",1950,'20364D',(0,.0,1,.13));cv(ch,'autoTitleDeleted',0)
plot=child(ch,'c:plotArea');layout(plot,64/806,72/265,660/806,151/265,'inner')
for idx,key,color,maxval,axis in [(0,'RT','266CA7',800,(10,11)),(1,'PE','CA1420',6000,(20,21))]:
 lc=child(plot,'c:lineChart');cv(lc,'grouping','standard');cv(lc,'varyColors',0);ser=child(lc,'c:ser');cv(ser,'idx',idx);cv(ser,'order',idx);child(child(ser,'c:tx'),'c:v').text=key
 sp=child(ser,'c:spPr');stroke(sp,color,28575)
 mk=child(ser,'c:marker');cv(mk,'symbol','circle');cv(mk,'size',6);ms=child(mk,'c:spPr');fill(ms,color);stroke(ms,color)
 cats=child(child(ser,'c:cat'),'c:numLit');child(cats,'c:formatCode').text='0';cv(cats,'ptCount',6)
 values=child(child(ser,'c:val'),'c:numLit');child(values,'c:formatCode').text='0.000';cv(values,'ptCount',6)
 for i,row in enumerate(D['curve']):
  # 内嵌 Excel 数据遵循其十五位有效数字精度；原始双精度值完整保存在 data.json。
  child(child(cats,'c:pt',idx=i),'c:v').text=str(row['V']);child(child(values,'c:pt',idx=i),'c:v').text=format(row[key],'.15g')
 cv(ser,'smooth',0);cv(lc,'marker',1);cv(lc,'smooth',0);cv(lc,'axId',axis[0]);cv(lc,'axId',axis[1])
for aid,vid,secondary,maxval,unit in [(10,11,False,800,200),(20,21,True,6000,1500)]:
 ax=child(plot,'c:catAx');cv(ax,'axId',aid);sc=child(ax,'c:scaling');cv(sc,'orientation','minMax');cv(ax,'delete',int(secondary));cv(ax,'axPos','b');child(ax,'c:numFmt',formatCode='0',sourceLinked=0);cv(ax,'majorTickMark','none');cv(ax,'minorTickMark','none');cv(ax,'tickLblPos','nextTo');sp=child(ax,'c:spPr');stroke(sp,'566575');textstyle(ax);cv(ax,'crossAx',vid);cv(ax,'crosses','autoZero');cv(ax,'auto',1);cv(ax,'lblAlgn','ctr');cv(ax,'lblOffset',100)
 if not secondary:title(ax,'V / kn',1350,'566575',(.86,.92,.12,.075))
 ax=child(plot,'c:valAx');cv(ax,'axId',vid);sc=child(ax,'c:scaling');cv(sc,'orientation','minMax');cv(sc,'max',maxval);cv(sc,'min',0);cv(ax,'delete',0);cv(ax,'axPos','r' if secondary else 'l')
 if not secondary:
  grid=child(ax,'c:majorGridlines');sp=child(grid,'c:spPr');stroke(sp,'DBE1E6')
 title(ax,'PE / kW' if secondary else 'RT / kN',1425,'CA1420' if secondary else '266CA7',(.84,.13,.16,.1) if secondary else (0,.13,.16,.1))
 child(ax,'c:numFmt',formatCode='0',sourceLinked=0);cv(ax,'majorTickMark','none');cv(ax,'minorTickMark','none');cv(ax,'tickLblPos','nextTo');sp=child(ax,'c:spPr');stroke(sp,'566575');textstyle(ax);cv(ax,'crossAx',aid);cv(ax,'crosses','max' if secondary else 'autoZero');cv(ax,'crossBetween','midCat');cv(ax,'majorUnit',unit)
sp=child(plot,'c:spPr');fill(sp,'FFFFFF');child(child(sp,'a:ln'),'a:noFill')
legend=child(ch,'c:legend');cv(legend,'legendPos','t');layout(legend,.31,.13,.3,.1);cv(legend,'overlay',1);textstyle(legend,1425,'20364D',True)
cv(ch,'plotVisOnly',1);cv(ch,'dispBlanksAs','gap');cv(ch,'showDLblsOverMax',0)
sp=child(chart,'c:spPr');fill(sp,'FFFFFF');child(child(sp,'a:ln'),'a:noFill');textstyle(chart)
parts['ppt/charts/chart1.xml']=E.tostring(chart,xml_declaration=True,encoding='UTF-8',standalone=True)

# 删除原先用于精准布局的图表线条，换入单个原生数据图表；14 kn 注释仍为独立可编辑虚线。
sn='ppt/slides/slide5.xml';s=E.fromstring(parts[sn]);tree=s.find('p:cSld/p:spTree',N)
exact={'曲线工况','RT轴标题','PE轴标题','左纵轴','右纵轴','横轴','横轴标题','图例RT','图例PE','图例RT文字','图例PE文字'}
prefix=('图表网格_','RT刻度_','PE刻度_','航速刻度_','曲线_','数据点_')
insert=None
for el in list(tree):
 names=el.xpath('.//p:cNvPr/@name',namespaces=N);name=names[0] if names else ''
 if name=='曲线工况':insert=tree.index(el)
 if name in exact or name.startswith(prefix):tree.remove(el)
frame=E.Element('{'+P+'}graphicFrame');nv=child(frame,'p:nvGraphicFramePr');mid=max(int(x) for x in tree.xpath('.//p:cNvPr/@id',namespaces=N))+1;child(nv,'p:cNvPr',id=mid,name='图表_性能参考状态阻力与有效功率');child(nv,'p:cNvGraphicFramePr');child(nv,'p:nvPr');xf=child(frame,'p:xfrm');child(xf,'a:off',x=420*9525,y=101*9525);child(xf,'a:ext',cx=806*9525,cy=265*9525);gd=child(child(frame,'a:graphic'),'a:graphicData',uri=C);cc=child(gd,'c:chart');cc.set('{'+R+'}id','rIdNativeChart');tree.insert(insert,frame)
parts[sn]=E.tostring(s,xml_declaration=True,encoding='UTF-8',standalone=True)
rn='ppt/slides/_rels/slide5.xml.rels';rels=E.fromstring(parts[rn]);E.SubElement(rels,'{'+REL+'}Relationship',Id='rIdNativeChart',Type=R+'/chart',Target='../charts/chart1.xml');parts[rn]=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
ct=E.fromstring(parts['[Content_Types].xml']);E.SubElement(ct,'{http://schemas.openxmlformats.org/package/2006/content-types}Override',PartName='/ppt/charts/chart1.xml',ContentType='application/vnd.openxmlformats-officedocument.drawingml.chart+xml');parts['[Content_Types].xml']=E.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True)
for n,b in list(parts.items()):
 if n.startswith('ppt/slides/') and n.endswith('.xml'):
  x=E.fromstring(b)
  for pr in x.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr',namespaces=N):
   f=pr.find('a:latin',N)
   if f is not None and f.get('typeface')=='Microsoft YaHei':
    ea=pr.find('a:ea',N)
    if ea is None:ea=child(pr,'a:ea')
    ea.set('typeface','Microsoft YaHei')
  parts[n]=E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
with zipfile.ZipFile(ROOT/'.build/candidate.pptx','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in parts.items():z.writestr(n,b)
print('双纵轴原生图表已绑定六组真实数据，准备生成内嵌数据工作簿。')
