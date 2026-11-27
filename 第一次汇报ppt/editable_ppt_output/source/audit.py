"""核验实际 PPTX 的原生对象、文字覆盖及素材来源，制作逐页对照图。"""
from pathlib import Path
from collections import Counter
from lxml import etree as E
from PIL import Image, ImageChops
import json,zipfile,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
scenes=json.loads((ROOT/'source/scenes.json').read_text(encoding='utf-8'))
PPT=ROOT/'pptx/combined_editable.pptx'
norm=lambda s:s.translate(str.maketrans({'ₜ':'T','ₑ':'E','ₚ':'p'})).replace('\r','\n')
def content(sh):
 ps=[]
 for p in sh.findall('p:txBody/a:p',NS):
  chunks=[]
  for ch in p:
   if ch.tag.endswith('}br'):chunks.append('\n')
   else:chunks.extend(ch.xpath('.//a:t/text()',namespaces=NS))
  ps.append(''.join(chunks))
 return '\n'.join(ps)
report={'render_application':'Microsoft PowerPoint COM','source_size':[1672,941],'slides':[],'native_text_missing':[],'native_text_extra':[]}
with zipfile.ZipFile(PPT) as z:
 p=E.fromstring(z.read('ppt/presentation.xml'));sz=p.find('p:sldSz',NS);report['page_size_emu']={k:int(v) for k,v in sz.attrib.items() if k in ['cx','cy']}
 originals={hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'source/reference_images').glob('*.png')}
 report['embedded_full_reference_images']=[n for n in z.namelist() if '/media/' in n and hashlib.sha256(z.read(n)).hexdigest() in originals]
 for i,scene in enumerate(scenes,1):
  r=E.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
  shapes=r.findall('.//p:sp',NS);actual=Counter(content(s) for s in shapes if content(s))
  expected=Counter(norm(e['text']) for e in scene['elements'] if e['kind']=='text')
  missing=list((expected-actual).elements());extra=list((actual-expected).elements())
  report['native_text_missing']+=missing;report['native_text_extra']+=extra
  report['slides'].append({'index':i,'source':scene['source'],'native_shapes':len(shapes),'native_textboxes':sum(bool(content(s)) for s in shapes),'native_groups':len(r.findall('.//p:grpSp',NS)),'independent_images':len(r.findall('.//p:pic',NS)),'text_exact_match':not missing and not extra})
  stem=Path(scene['source']).stem
  ref=Image.open(ROOT/'source/reference_images'/scene['source']).convert('RGB')
  render=Image.open(ROOT/'previews'/f'幻灯片{i}.PNG').convert('RGB')
  if render.size!=ref.size:raise ValueError('渲染尺寸不匹配')
  render.save(ROOT/'previews'/(stem+'.png'))
  pair=Image.new('RGB',(3344,941),'white');pair.paste(ref,(0,0));pair.paste(render,(1672,0));pair.save(ROOT/'comparisons'/(stem+'_并排.png'))
  Image.blend(ref,render,.5).save(ROOT/'comparisons'/(stem+'_叠加.png'))
  solo=ROOT/'.build/single_renders'/(stem+'.png')
  if solo.exists():
   d=ImageChops.difference(render,Image.open(solo).convert('RGB'));report['slides'][-1]['single_combined_render_identical']=d.getbbox() is None
report['totals']={k:sum(s[k] for s in report['slides']) for k in ['native_shapes','native_textboxes','native_groups','independent_images']}
report['all_expected_text_native']=not report['native_text_missing'] and not report['native_text_extra']
report['delivered_files']=[{'file':'pptx/'+f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted((ROOT/'pptx').glob('*.pptx'))]
(ROOT/'acceptance_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
thumbs=[]
for i,scene in enumerate(scenes,1):
 im=Image.open(ROOT/'previews'/(Path(scene['source']).stem+'.png')).convert('RGB');im.thumbnail((557,314));thumbs.append(im)
overview=Image.new('RGB',(1671,942),'white')
for i,im in enumerate(thumbs):overview.paste(im,((i%3)*557,(i//3)*314))
overview.save(ROOT/'previews/总览.png')
print(json.dumps(report,ensure_ascii=False,indent=2))
if not report['all_expected_text_native']:raise ValueError('原生文本覆盖核对未通过')
