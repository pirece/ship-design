"""保留原生编辑树，设置精确画幅、整理对象，并输出单页与汇总候选文件。"""
from pathlib import Path
from lxml import etree as E
import zipfile,json,copy,re,posixpath
ROOT=Path(__file__).resolve().parents[1]
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
PN=NS['p'];AN=NS['a'];RN=NS['r'];REL='http://schemas.openxmlformats.org/package/2006/relationships'
scenes=json.loads((ROOT/'source/scenes.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(ROOT/'.build/all_raw.pptx') as z:parts={n:z.read(n) for n in z.namelist()}
def xml(n):return E.fromstring(parts[n])
def save(n,r):parts[n]=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
p=xml('ppt/presentation.xml');sz=p.find('p:sldSz',NS);sz.set('cy',str(round(int(sz.get('cx'))*941/1672)));save('ppt/presentation.xml',p)
# 调整封面原生分隔线，匹配参考图纵坐标；沿用原模板底纹。
for i,scene in enumerate(scenes,1):
 sn=f'ppt/slides/slide{i}.xml';r=xml(sn)
 # 清除复制产生的空占位符，不保留隐藏的旧标题。
 tree=r.find('p:cSld/p:spTree',NS)
 for sh in list(tree):
  if sh.tag==f'{{{PN}}}sp' and not sh.xpath('.//a:t[text()]',namespaces=NS) and sh.find('p:nvSpPr/p:nvPr/p:ph',NS) is not None:tree.remove(sh)
 # 明确为中文指定字体，避免跨机依赖主题字体。
 for rp in r.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr',namespaces=NS):
  if rp.find('a:latin',NS) is not None and rp.find('a:latin',NS).get('typeface')=='Microsoft YaHei':
   ea=rp.find('a:ea',NS)
   if ea is None:ea=E.SubElement(rp,f'{{{AN}}}ea')
   ea.set('typeface','Microsoft YaHei')
 # 技术变量使用原生上下标；保留原图 T、E 的大写形式。
 for run in list(r.xpath('.//a:r',namespaces=NS)):
  t=run.find('a:t',NS)
  if t is None or not any(c in (t.text or '') for c in 'ₜₑₚ'):continue
  parent=run.getparent();idx=parent.index(run);pieces=re.split('([ₜₑₚ]+)',t.text)
  for piece in pieces:
   if not piece:continue
   nr=copy.deepcopy(run);nt=nr.find('a:t',NS);nt.text=piece.translate(str.maketrans({'ₜ':'T','ₑ':'E','ₚ':'p'}))
   if piece[0] in 'ₜₑₚ':
    rp=nr.find('a:rPr',NS)
    if rp is None:rp=E.Element(f'{{{AN}}}rPr');nr.insert(0,rp)
    rp.set('baseline','-25000');rp.set('sz',str(round(int(rp.get('sz','1100'))*.75)))
   parent.insert(idx,nr);idx+=1
  parent.remove(run)
 # 将连续的图标/编号/表格单元格与对应文字组成可取消组合的小组。
 def bounds(sh):
  tr=sh.find('p:spPr/a:xfrm',NS)
  if tr is None:return None
  off=tr.find('a:off',NS);ext=tr.find('a:ext',NS)
  return tuple(int(v) for v in [off.get('x'),off.get('y'),ext.get('cx'),ext.get('cy')])
 maxid=max(int(v) for v in r.xpath('.//p:cNvPr/@id',namespaces=NS))
 nodes=list(tree);j=0
 while j<len(nodes)-1:
  a,b=nodes[j],nodes[j+1];j+=1
  if a.tag!=f'{{{PN}}}sp' or b.tag!=f'{{{PN}}}sp':continue
  if a.xpath('.//a:t[text()]',namespaces=NS) or not b.xpath('.//a:t[text()]',namespaces=NS):continue
  if a.find('p:spPr/a:solidFill',NS) is None and a.find('p:spPr/a:gradFill',NS) is None:continue
  ba,bb=bounds(a),bounds(b)
  if ba is None or bb is None:continue
  ax,ay,aw,ah=ba;bx,by,bw,bh=bb
  if aw>3650000 or ah>750000 or abs(ay-by)>250000 or bx<ax-250000 or bx>ax+aw+300000:continue
  x=min(ax,bx);y=min(ay,by);w=max(ax+aw,bx+bw)-x;h=max(ay+ah,by+bh)-y
  grp=E.Element(f'{{{PN}}}grpSp');nv=E.SubElement(grp,f'{{{PN}}}nvGrpSpPr');maxid+=1
  label=''.join(b.xpath('.//a:t/text()',namespaces=NS))[:35]
  E.SubElement(nv,f'{{{PN}}}cNvPr',id=str(maxid),name='组合_'+label);E.SubElement(nv,f'{{{PN}}}cNvGrpSpPr');E.SubElement(nv,f'{{{PN}}}nvPr')
  gp=E.SubElement(grp,f'{{{PN}}}grpSpPr');tr=E.SubElement(gp,f'{{{AN}}}xfrm')
  for tag,attrs in [('off',{'x':x,'y':y}),('ext',{'cx':w,'cy':h}),('chOff',{'x':x,'y':y}),('chExt',{'cx':w,'cy':h})]:E.SubElement(tr,f'{{{AN}}}'+tag,**{k:str(v) for k,v in attrs.items()})
  index=tree.index(a);tree.remove(a);tree.remove(b);grp.append(a);grp.append(b);tree.insert(index,grp);j+=1
 save(sn,r)
 if scene['key']=='cover':
  rels=xml(f'ppt/slides/_rels/slide{i}.xml.rels')
  target=next(z.get('Target') for z in rels if z.get('Type').endswith('/slideLayout'))
  layoutname=posixpath.normpath(posixpath.join('ppt/slides',target)).lstrip('/');layout=xml(layoutname)
  for sh in layout.xpath('.//p:sp|.//p:cxnSp',namespaces=NS):
   off=sh.find('.//a:xfrm/a:off',NS);ext=sh.find('.//a:xfrm/a:ext',NS)
   if off is not None and ext is not None and int(ext.get('cx'))>7000000 and int(ext.get('cy'))<50000:
    y=int(off.get('y'))/int(sz.get('cx'))*1672
    if 225<y<245:off.set('y',str(round(194/1672*int(sz.get('cx')))))
    if 461<y<481:off.set('y',str(round(452/1672*int(sz.get('cx')))))
  save(layoutname,layout)

def write(path,data):
 # 按 OPC 关系递归保留实际可达资源，清除无引用页面及其备注。
 reachable=set();pending=['']
 while pending:
  part=pending.pop()
  if part in reachable:continue
  reachable.add(part)
  relpath=posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels') if part else '_rels/.rels'
  if relpath not in data:continue
  reachable.add(relpath)
  for rel in E.fromstring(data[relpath]):
   if rel.get('TargetMode')=='External':continue
   target=posixpath.normpath(posixpath.join(posixpath.dirname(part),rel.get('Target'))).lstrip('/')
   if target not in data:raise ValueError('缺失关系目标：'+target)
   pending.append(target)
 data={n:b for n,b in data.items() if n in reachable or n=='[Content_Types].xml'}
 ct=E.fromstring(data['[Content_Types].xml'])
 for el in list(ct):
  if el.get('PartName') and el.get('PartName').lstrip('/') not in data:ct.remove(el)
 data['[Content_Types].xml']=E.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True)
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in data.items():z.writestr(n,b)
write(ROOT/'.build/combined_candidate.pptx',parts)
slideids=p.find('p:sldIdLst',NS)
for i,scene in enumerate(scenes):
 d=parts.copy();pr=E.fromstring(d['ppt/presentation.xml']);lst=pr.find('p:sldIdLst',NS)
 for j,el in reversed(list(enumerate(list(lst)))):
  if j!=i:lst.remove(el)
 d['ppt/presentation.xml']=E.tostring(pr,xml_declaration=True,encoding='UTF-8',standalone=True)
 # 只交付选定页面的关系入口，完整资源仍保持自包含。
 rel=E.fromstring(d['ppt/_rels/presentation.xml.rels']);keepid=lst[0].get(f'{{{RN}}}id')
 for el in list(rel):
  if el.get('Type').endswith('/slide') and el.get('Id')!=keepid:rel.remove(el)
 d['ppt/_rels/presentation.xml.rels']=E.tostring(rel,xml_declaration=True,encoding='UTF-8',standalone=True)
 # 去掉其余页面 XML，避免将非本页内容作为隐藏编辑页保留。
 ct=E.fromstring(d['[Content_Types].xml'])
 for j in range(1,len(scenes)+1):
  if j==i+1:continue
  for name in [f'ppt/slides/slide{j}.xml',f'ppt/slides/_rels/slide{j}.xml.rels']:
   d.pop(name,None)
  for el in list(ct):
   if el.get('PartName')==f'/ppt/slides/slide{j}.xml':ct.remove(el)
 d['[Content_Types].xml']=E.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True)
 write(ROOT/'.build'/(Path(scene['source']).stem+'_candidate.pptx'),d)
print('已生成精确比例候选文件：1 个汇总与 9 个单页')
