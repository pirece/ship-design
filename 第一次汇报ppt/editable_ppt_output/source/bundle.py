"""打包交付内容，排除草稿、临时检查目录和依赖联接。"""
from pathlib import Path
import os,zipfile,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
target=ROOT.parent/'editable_ppt_完整交付包.zip'
report=json.loads((ROOT/'acceptance_report.json').read_text(encoding='utf-8'))
report['delivered_files']=[{'file':'pptx/'+f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted((ROOT/'pptx').glob('*.pptx'))]
(ROOT/'acceptance_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
v=ROOT/'validation';v.mkdir(exist_ok=True)
for f in (ROOT/'.build/receipts_release_verified').glob('*.json'):shutil.copy2(f,v/f.name)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for base,dirs,files in os.walk(ROOT):
  dirs[:]=[d for d in dirs if d not in ['.build','node_modules','__pycache__','.codex-finalizer']]
  for name in files:
   f=Path(base)/name
   if name=='probe.mjs' or (f.parent.name=='previews' and name.startswith('幻灯片')):continue
   z.write(f,Path('editable_ppt_output')/f.relative_to(ROOT))
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 assert len([n for n in z.namelist() if '/pptx/' in n and n.endswith('.pptx')])==10
 print('压缩包校验通过',len(z.namelist()),'个文件')
print(target,target.stat().st_size)
