"""从当前汇总稿建立编辑副本，统一真实数据并裁取授权的原始图像。"""
from pathlib import Path
from lxml import etree as E
from PIL import Image
import zipfile,json,csv,copy,posixpath
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[1]
OUT=ROOT.parent
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
PN=NS['p']; AN=NS['a']; RN=NS['r']
inv=json.loads((ROOT/'.build/input_inventory.json').read_text(encoding='utf-8'))
w=inv['workbooks']['阻力工作簿']['sheets']; g=inv['workbooks']['重量工作簿']['sheets']
def val(sh,cell):return w[sh][cell]['value']
DATA={'DWT':val('新船换算','B5'),'k':val('新船换算','B9'),'LOA':177.496604,'Lpp':169.721013,'B':28.418402,'D':14.406551,'T_performance':val('新船换算','B10'),'lightship':8310.700160893894,'points':751,'stations':31,'branches':32,'max_half_breadth':14.209201}
DATA['curve']=[{'V':val('新船换算',f'A{r}'),'RT':val('新船换算',f'E{r}')/1000,'PE':val('新船换算',f'F{r}')} for r in range(14,20)]
DATA['engines']=[{'label':label,'model':val('推进与主机',f'{c}5'),'MCR':val('推进与主机',f'{c}6'),'rpm':val('推进与主机',f'{c}7'),'CSR':val('推进与主机',f'{c}9'),'CSRrpm':val('推进与主机',f'{c}10'),'speed':val('推进与主机',f'{c}21')} for c,label in [('D','A'),('E','B')]]
(ROOT/'source/data.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')
with (ROOT/'source/curve_data.csv').open('w',encoding='utf-8-sig',newline='') as f:
 cw=csv.DictWriter(f,fieldnames=['V','RT','PE']);cw.writeheader();cw.writerows(DATA['curve'])

# 编辑对象仍为当前汇总稿，保留其页面及继承的模板，仅清除本次需要替换的页内内容。
with zipfile.ZipFile(inv['selected']) as z:parts={n:z.read(n) for n in z.namelist()}
pr=E.fromstring(parts['ppt/presentation.xml']);lst=pr.find('p:sldIdLst',NS);old=list(lst)
rels=E.fromstring(parts['ppt/_rels/presentation.xml.rels']);rmap={r.get('Id'):r.get('Target') for r in rels}
order=[7,3,6,2,4,8,0,5]
for n in list(lst):lst.remove(n)
for i in order:lst.append(old[i])
pr.find('p:sldSz',NS).set('cx','12192000');pr.find('p:sldSz',NS).set('cy','6858000')
parts['ppt/presentation.xml']=E.tostring(pr,xml_declaration=True,encoding='UTF-8',standalone=True)
selected=[]
for i in order:
 sn=posixpath.normpath(posixpath.join('ppt',rmap[old[i].get('{'+RN+'}id')])).lstrip('/')
 selected.append(sn)
 s=E.fromstring(parts[sn]);tree=s.find('p:cSld/p:spTree',NS)
 for el in list(tree):
  if E.QName(el).localname not in ['nvGrpSpPr','grpSpPr']:tree.remove(el)
 parts[sn]=E.tostring(s,xml_declaration=True,encoding='UTF-8',standalone=True)
 # 删除旧备注及图片关系，避免把旧的占位技术图留在编辑副本中。
 rn=posixpath.join(posixpath.dirname(sn),'_rels',posixpath.basename(sn)+'.rels')
 rr=E.fromstring(parts[rn])
 for rel in list(rr):
  if not rel.get('Type').endswith('/slideLayout'):rr.remove(rel)
 parts[rn]=E.tostring(rr,xml_declaration=True,encoding='UTF-8',standalone=True)
for rel in list(rels):
 if rel.get('Type').endswith('/slide') and rel.get('Id') not in [old[i].get('{'+RN+'}id') for i in order]:rels.remove(rel)
parts['ppt/_rels/presentation.xml.rels']=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
# 将上一轮为对照图片移动的两条封面灰线恢复到原模板坐标。
with zipfile.ZipFile(OUT/'ppt模板.pptx') as z:
 template={n:z.read(n) for n in z.namelist()}
 original_lines=[]
 for n,b in template.items():
  if n.startswith('ppt/slideLayouts/') and n.endswith('.xml'):
   x=E.fromstring(b)
   for sh in x.xpath('.//p:sp|.//p:cxnSp',namespaces=NS):
    off=sh.find('.//a:xfrm/a:off',NS);ext=sh.find('.//a:xfrm/a:ext',NS)
    if off is not None and ext is not None and int(ext.get('cx'))>7000000 and int(ext.get('cy'))<50000:
     original_lines.append(int(off.get('y')))
for n,b in list(parts.items()):
 if n.startswith('ppt/slideLayouts/') and n.endswith('.xml'):
  x=E.fromstring(b)
  for sh in x.xpath('.//p:sp|.//p:cxnSp',namespaces=NS):
   off=sh.find('.//a:xfrm/a:off',NS);ext=sh.find('.//a:xfrm/a:ext',NS)
   if off is not None and ext is not None and int(ext.get('cx'))>7000000 and int(ext.get('cy'))<50000:
    y=int(off.get('y'));nearest=min(original_lines,key=lambda v:abs(v-y));off.set('y',str(nearest))
  parts[n]=E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
def write_pruned(target,parts):
 reachable=set();pending=['']
 while pending:
  part=pending.pop()
  if part in reachable:continue
  reachable.add(part)
  rp=posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels') if part else '_rels/.rels'
  if rp not in parts:continue
  reachable.add(rp)
  for r in E.fromstring(parts[rp]):
   if r.get('TargetMode')=='External':continue
   pending.append(posixpath.normpath(posixpath.join(posixpath.dirname(part),r.get('Target'))).lstrip('/'))
 result={n:b for n,b in parts.items() if n in reachable or n=='[Content_Types].xml'}
 ct=E.fromstring(result['[Content_Types].xml'])
 for el in list(ct):
  if el.get('PartName') and el.get('PartName').lstrip('/') not in result:ct.remove(el)
 result['[Content_Types].xml']=E.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True)
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in result.items():z.writestr(n,b)
write_pruned(ROOT/'.build/edit_base.pptx',parts)

# 只裁切白色边缘及既有图文布局，不改变实际几何线条或补造技术内容。
src=PROJECT/'outputs/B组_首次汇报综合材料_v0.3_20261101/图像'
crops={
 'model.png':('01_组员三维曲面预览.png',(80,210,1935,690)),
 'lines.png':('02_组员型线图全图.png',(20,30,5870,2160)),
 'section.png':('04_典型横剖面.png',(0,70,900,1030)),
}
cropmeta=[]
for dst,(name,bbox) in crops.items():
 im=Image.open(src/name);im.crop(bbox).save(ROOT/'assets'/dst)
 cropmeta.append({'output':dst,'source':str(src/name),'source_size':im.size,'crop':bbox})
(ROOT/'source/crop_manifest.json').write_text(json.dumps(cropmeta,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selected_slide_order':[i+1 for i in order],'data':DATA,'template_lines':original_lines,'crops':cropmeta},ensure_ascii=False,indent=2))
