"""只读核验当前演示文稿、课程资料及工作簿缓存值。"""
from pathlib import Path
import os,json,zipfile,hashlib
from lxml import etree as E
from openpyxl import load_workbook
ROOT=Path(r'C:\Users\董昱彤\Desktop\船舶设计')
OUT=ROOT/'第一次汇报ppt/完善制作资料'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
decks=[];inputs=[]
for base,dirs,files in os.walk(ROOT):
 dirs[:]=[d for d in dirs if d not in ['.build','node_modules','tmp','完善制作资料']]
 for name in files:
  p=Path(base)/name
  if p.suffix.lower()=='.pptx':
   with zipfile.ZipFile(p) as z:
    r=E.fromstring(z.read('ppt/presentation.xml'));n=len(r.findall('p:sldIdLst/p:sldId',NS))
   decks.append({'file':str(p),'slide_count':n,'mtime':p.stat().st_mtime})
sources={
 '课程指导书':ROOT/'《船舶设计Ⅱ》_课程设计指导书_20261016.docx',
 '综合分析':ROOT/'outputs/B组_首次汇报综合材料_v0.3_20261101/01_首次汇报综合分析.docx',
 '完整文本':ROOT/'outputs/B组_首次汇报综合材料_v0.3_20261101/02_供GPT读取的完整文本.txt',
 '中期报告':ROOT/'outputs/B组_成员一_中期_v0.2_20261031/01_成员一中期设计计算报告.docx',
 '阻力工作簿':ROOT/'outputs/B组_成员一_中期_v0.2_20261031/02_阻力快速性与总体校核.xlsx',
 '重量工作簿':ROOT/'outputs/B组_成员一_中期_v0.2_20261031/03_重量重心与浮态待补.xlsx',
 '型线补充':ROOT/'outputs/B组_首次汇报综合材料_v0.3_20261101/型线图补充说明.txt',
 '建模补充':ROOT/'outputs/B组_首次汇报综合材料_v0.3_20261101/三维建模补充说明.txt',
 '模板':ROOT/'第一次汇报ppt/ppt模板.pptx'}
for key,p in sources.items():
 assert p.is_file(),str(p)
 inputs.append({'name':key,'file':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 if p.suffix=='.docx':
  with zipfile.ZipFile(p) as z:r=E.fromstring(z.read('word/document.xml'))
  text='\n'.join(''.join(q.xpath('.//w:t/text()',namespaces=NS)) for q in r.xpath('//w:p',namespaces=NS))
  (OUT/'.build'/f'{key}.txt').write_text(text,encoding='utf-8')
snapshots={}
for key in ['阻力工作簿','重量工作簿']:
 p=sources[key];vf=load_workbook(p,data_only=False,read_only=True);vv=load_workbook(p,data_only=True,read_only=True);sheets={}
 lines=[]
 for sh in vf:
  lines.append('\n工作表：'+sh.title);cells={}
  for row in sh:
   rowparts=[]
   for c in row:
    if c.value is None:continue
    value=vv[sh.title][c.coordinate].value
    cells[c.coordinate]={'formula':c.value if c.data_type=='f' else None,'value':value}
    rowparts.append(f'{c.coordinate}={value}' + (' [公式]' if c.data_type=='f' else ''))
   if rowparts:lines.append(' | '.join(rowparts))
  sheets[sh.title]=cells
 snapshots[key]={'file':str(p),'sheets':sheets}
 (OUT/'.build'/f'{key}_单元格.txt').write_text('\n'.join(lines),encoding='utf-8')
eight=sorted([d for d in decks if d['slide_count']==8],key=lambda d:d['mtime'],reverse=True)
selected=eight[0]['file'] if eight else str(ROOT/'第一次汇报ppt/editable_ppt_output/pptx/combined_editable.pptx')
inventory={'inputs':inputs,'presentation_candidates':decks,'eight_page_found':bool(eight),'selected':selected,'workbooks':snapshots}
(OUT/'.build/input_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print(json.dumps({'inputs':inputs,'presentation_candidates':decks,'eight_page_found':bool(eight),'selected':selected},ensure_ascii=False,indent=2))
