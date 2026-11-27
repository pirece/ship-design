"""把 PowerPoint 重新序列化的浮点缓存还原为 Excel 十五位精度。"""
from pathlib import Path
from lxml import etree as E
import zipfile,json
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'source/data.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(root/'.build/tuned.pptx') as z:parts={n:z.read(n) for n in z.namelist()}
n='ppt/charts/chart1.xml';x=E.fromstring(parts[n]);ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
for i,s in enumerate(x.xpath('.//c:ser',namespaces=ns)):
 key=['RT','PE'][i]
 for pt in s.xpath('c:val/c:numLit/c:pt',namespaces=ns):
  idx=int(pt.get('idx'));v=pt.find('c:v',ns);expected=data['curve'][idx][key]
  assert abs(float(v.text)-expected)<1e-9
  v.text=format(expected,'.15g')
parts[n]=E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
with zipfile.ZipFile(root/'.build/normalized.pptx','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in parts.items():z.writestr(n,b)
print('十二个曲线值均已与原工作簿快照交叉核对。')
