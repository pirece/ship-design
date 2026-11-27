"""核验交付包、数据及输入文件，生成逐页记录与素材清单。"""
from pathlib import Path
from lxml import etree as E
from PIL import Image,ImageChops,ImageStat
from pypdf import PdfReader
import zipfile,json,hashlib,csv,re
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT.parent;PROJECT=OUT.parent
BASE=PROJECT/'outputs/B组_首次汇报综合材料_v0.3_20261101'
MID=PROJECT/'outputs/B组_成员一_中期_v0.2_20261031'
PPT=OUT/'船舶设计II_B组_第一次汇报_完善版.pptx';PDF=PPT.with_suffix('.pdf')
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
inv=json.loads((ROOT/'.build/input_inventory.json').read_text(encoding='utf-8'))
D=json.loads((ROOT/'source/data.json').read_text(encoding='utf-8'))
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
preserved=[]
for item in inv['inputs']:
 assert sha(item['file'])==item['sha256'],item['file']
 preserved.append(item['file'])
with zipfile.ZipFile(PPT) as z:
 slides=[E.fromstring(z.read(f'ppt/slides/slide{i}.xml')) for i in range(1,9)]
 texts=['\n'.join(x.xpath('.//a:t/text()',namespaces=NS)) for x in slides]
 assert len(E.fromstring(z.read('ppt/presentation.xml')).find('p:sldIdLst',NS))==8
 for t in ['33500','0.986750']:assert t in texts[1]
 for t in ['33500','169.721','28.418','14.407','478.991','3449.505','主机尚未定型']:assert t in texts[4]
 for t in ['751','31','32','28.418402','仍待进一步验证']:assert t in texts[5]
 assert '组员成果待并入统一汇总' in texts[3]
 assert '第一轮完整设计方案' in texts[7]
 chart=E.fromstring(z.read('ppt/charts/chart1.xml'))
 errors=[]
 for i,s in enumerate(chart.xpath('.//c:ser',namespaces=NS)):
  key=['RT','PE'][i]
  vv=s.xpath('c:val/c:numRef/c:numCache/c:pt/c:v/text()',namespaces=NS)
  assert len(vv)==6
  for value,row in zip(vv,D['curve']):
   error=abs(float(value)-row[key]);errors.append(error);assert error<1e-9
 assert any(n.endswith('.xlsx') and n.startswith('ppt/embeddings/') for n in z.namelist())
 native=sum(len(x.xpath('.//p:sp',namespaces=NS)) for x in slides)
 textcount=sum(len(x.xpath('.//p:sp[p:txBody/a:p/a:r/a:t]',namespaces=NS)) for x in slides)
 pictures=sum(len(x.xpath('.//p:pic',namespaces=NS)) for x in slides)
 titlechecks=[]
 for i,x in enumerate(slides[1:],2):
  sh=x.xpath('.//p:sp[p:nvSpPr/p:cNvPr[@name="页面标题"]]',namespaces=NS)[0]
  off=sh.find('p:spPr/a:xfrm/a:off',NS);size=sh.xpath('.//a:rPr/@sz',namespaces=NS)
  titlechecks.append({'slide':i,'x':int(off.get('x')),'y':int(off.get('y')),'font_sizes':size})
  assert abs(int(off.get('x'))/9525-112.9)<.02
  assert abs(int(off.get('y'))/9525-4.58)<.02
  assert all(int(v)==3200 for v in size)
 assert pictures==4
reader=PdfReader(PDF);assert len(reader.pages)==8
assert len(list((OUT/'rendered_slides').glob('*.PNG')))==8
fits=json.loads((OUT/'rendered_slides/text_fit.json').read_text(encoding='utf-8-sig'));assert not fits
template=Image.open(OUT/'editable_ppt_output/.build/template/幻灯片2.PNG').convert('RGB')
comparisons=[]
for i in range(2,9):
 im=Image.open(OUT/f'rendered_slides/幻灯片{i}.PNG').convert('RGB')
 areas={}
 for label,bounds in [('校徽',(0,0,140,94)),('右上装饰',(1420,0,1672,94)),('页脚',(0,831,1672,941))]:
  delta=ImageStat.Stat(ImageChops.difference(im.crop(bounds),template.crop(bounds)))
  areas[label]=round(sum(delta.mean)/3,6)
 comparisons.append({'slide':i,'mean_absolute_rgb_difference':areas})
audit={'slides':8,'pdf_pages':8,'native_shapes':native,'native_text_objects':textcount,'native_charts':1,'independent_real_images':pictures,'max_chart_source_error':max(errors),'unchanged_inputs':preserved,'template_title_checks':titlechecks,'template_render_comparisons':comparisons,'pptx_sha256':sha(PPT),'pdf_sha256':sha(PDF),'text_overflow_count':0}
(ROOT/'.build/delivery_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')

rows=[]
def asset(slide,typ,file,loc,use,status='已核对并使用'):
 rows.append({'slide':slide,'asset_type':typ,'source_file':str(file),'source_location_or_sheet':loc,'used_for':use,'status':status})
for i in range(1,9):asset(i,'模板',OUT/'ppt模板.pptx','封面母版/版式' if i==1 else '内容页母版/版式','学校标识、顶部标题栏、右上装饰、底部线稿')
guide=PROJECT/'《船舶设计Ⅱ》_课程设计指导书_20261016.docx'
asset(1,'课程任务',guide,'§1.1','组别、目标载重量与成员姓名')
asset(2,'任务指标',guide,'§1.1、§2.1、§2.2、§2.10、§2.12、§2.13','母型、33500t、14kn、16000海里、5货舱、4台SWL30t、25铺位')
asset(2,'计算数据',MID/'02_阻力快速性与总体校核.xlsx','新船换算!B5、B9','目标载重量与线性缩尺比')
asset(2,'原生示意线稿',ROOT/'source/build.mjs','shipOutline','表达母型改造路线','非实船照片；非成果几何')
asset(3,'成员分工',guide,'表1-2','四人组职责与协作接口')
asset(4,'阶段状态',BASE/'01_首次汇报综合分析.docx','阶段成果及当前证据边界','总体/型线已形成阶段成果；总布置/舱容稳性待汇总')
asset(4,'真实模型缩略图',BASE/'图像/01_组员三维曲面预览.png','裁切(80,210,1935,690)','三维模型阶段成果')
asset(4,'真实数据缩略曲线',MID/'02_阻力快速性与总体校核.xlsx','新船换算!A14:A19、E14:E19','总体快速性阶段成果')
asset(4,'待并入成果',BASE/'02_供GPT读取的完整文本.txt','成果边界说明','总布置、舱容、完整稳性状态','未并入当前统一汇总；只保留原生图标')
asset(5,'主尺度数据',BASE/'01_首次汇报综合分析.docx','当前统一主尺度','Lpp、B、D；均为阶段方案')
asset(5,'原生双纵轴图表',MID/'02_阻力快速性与总体校核.xlsx','新船换算!B10、A14:A19、E14:E19、F14:F19','性能参考吃水、6点阻力和有效功率；E列N转kN')
asset(5,'主机候选数据',MID/'02_阻力快速性与总体校核.xlsx','推进与主机!D5:E10、D21:E21','两个候选的型号、MCR/CSR及估算航速')
asset(5,'结果边界',MID/'01_成员一中期设计计算报告.docx','快速性、推进方案和待补事项','参考状态与满载结论区分；主机尚未定型')
asset(6,'真实模型图片',BASE/'图像/01_组员三维曲面预览.png','裁切(80,210,1935,690)','完整船体主体；等比例放置','曲面数据预览；非MAXSURF截图')
asset(6,'真实型线图片',BASE/'图像/02_组员型线图全图.png','裁切(20,30,5870,2160)','型值表、横剖、纵剖和半宽水线整体布局')
asset(6,'真实横剖面图片',BASE/'图像/04_典型横剖面.png','裁切(0,70,900,1030)，艉至舯子图','真实型值折线；不添加插值点')
asset(6,'点集一致性数据',BASE/'02_供GPT读取的完整文本.txt','751点、31站位、32分支组及最大半宽核查','跨文件数据传递一致性','不代表公平、水密或MSD切剖验证通过')
asset(6,'证据边界',BASE/'型线图补充说明.txt','全文','限制型线与当前MSD一致性的结论')
asset(6,'证据边界',BASE/'三维建模补充说明.txt','全文','限制曲面公平、接缝、水密性结论')
asset(7,'重量初值及缺项',MID/'03_重量重心与浮态待补.xlsx','Sheet1!C6、B23:E28；母型分区缩放!E22；Weight载荷待补区域','8310.7t几何相似初估及独立重量待闭合')
asset(7,'跨专业待办',MID/'01_成员一中期设计计算报告.docx','后续接口及数据边界','模型/静水力、重量/浮力/舱容、快速性/推进/GA三接口')
asset(8,'计划',OUT/'船舶设计II_B组_第一次汇报_PPT完善任务规划.md','Slide 8','四个计划周期、M1—M4及12月4日阶段目标','未来计划；非当前完成比例')
with (OUT/'asset_manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)

curve='\n'.join(f"| {x['V']} | {x['RT']:.3f} | {x['PE']:.3f} |" for x in D['curve'])
record=f'''# B组第一次汇报 PPT 完善记录

## 交付与修改基础

- 输出：`船舶设计II_B组_第一次汇报_完善版.pptx`、同名 PDF、`rendered_slides/` 中 8 张实际 PowerPoint 渲染 PNG、本文和 `asset_manifest.csv`。
- 本地没有找到已合并的 8 页版本。实际编辑对象是 `editable_ppt_output/pptx/combined_editable.pptx`，原稿为 9 页。按本次规划合并单独任务页，采用原页序 **8、4、7、3、5、9、1、6** 对应新的 1—8 页；原第2页的有效任务内容并入新第2页。
- 保留原稿的页面及模板继承关系，替换获准修改的中部内容，未从空白演示文稿新建。模板为 `ppt模板.pptx`。
- 画幅恢复为模板的 13⅓ × 7½ 英寸（16:9）。内容页标题统一回到模板位置，字号 32 pt。上一轮为复刻参考图移动的封面两条灰线已恢复到原模板坐标。
- 输入文件保持原样。本次对输入清单内的 {len(preserved)} 个文件做了 SHA-256 复核，均与编辑前一致。

## 逐页修改

| 页 | 标题 | 修改与证据边界 |
|---|---|---|
| 1 | 封面 | 保留校徽、背景建筑和模板构图，更新课程、组别、汇报人、组员及日期，不添加船舶照片。 |
| 2 | 设计任务与总体设计路线 | 合并任务与路线。母型—改造—目标船采用明确标注的原生示意轮廓；五项任务指标来自指导书。保留8步设计主线，注明SWL不是设备自重。 |
| 3 | 成员分工与协同关系 | 按指导书纠正职责。上部总体—总布置、下部型线—性能分别双向协作，统一六项接口。 |
| 4 | 当前总体进展 | 总体和型线两条工作线标为阶段成果；总布置、舱容与稳性标为“组员成果待并入统一汇总”。移除未核验的GA、舱容及GZ示意结果。 |
| 5 | 阶段成果① | 使用统一主尺度和原工作簿公式最终缓存值，生成原生双纵轴图表，蓝RT、红PE，标注14kn。以数据卡展示两台主机候选，移除发动机占位图。明确性能参考吃水和主机未定型。 |
| 6 | 阶段成果② | 置换为真实三维曲面图、二维型线图及横剖面图；展示751/31/32与半宽核查。保留完整的模型验证限定。 |
| 7 | 困难与解决措施 | 组织为三个专业接口，每个接口区分已有依据、当前缺口及下一步措施。未使用假舱容、假稳性或假尾部净空图。 |
| 8 | 进展规划 | 四段时间对应M1—M4，明确是未来计划，未使用完成百分比。12月4日目标为第一轮完整设计方案，不称最终定型。 |

## 数据核对

曲线来源：`{MID / '02_阻力快速性与总体校核.xlsx'}`，工作表“新船换算”A14:A19、E14:E19、F14:F19。E列单位由N换为kN。所有原始读取值保存在 `完善制作资料/source/data.json` 和 `curve_data.csv`，原工作簿未修改、未补填空白。

| V / kn | RT / kN | PE / kW |
|---:|---:|---:|
{curve}

- 当前计算吃水只使用 **9.699753 m**。曲线数据与规划/中期报告的三位小数结果一致，未发现本次展示值差异。
- Lpp 169.721 m、B 28.418 m、D 14.407 m统一保留三位小数；目标载重量33500t是课程要求。
- A：5G45ME-C9.7，MCR 6950kW/111rpm，CSR 6255kW/107.17rpm，阶段航速14.42kn。
- B：6S40ME-C9.5，MCR 6810kW/146rpm，CSR 6129kW/140.96rpm，阶段航速14.44kn。
- 两主机数据来自“推进与主机”D、E列。本版为保持主画面简洁，把CSR转速保留在第5页演讲者备注。
- 8310.7t为空船几何相似初值，不是独立结构、机电及舾装重量闭合结果。
- 751点、31站位、32分支组和最大半宽14.209201m来自综合材料；CSV/Markers同序差0，DXF排序点集差约4.996×10⁻¹³，仅证明数据传递一致。

第5页图表包含两个原生数据系列和一个内嵌Excel数据快照，可在PowerPoint“编辑数据”中修改。快照保留Excel支持的15位有效数字，与源值最大绝对差为 {max(errors):.3g}，三位小数展示值完全相同。快照不包含原阻力工作簿全部公式，也不会随外部工作簿自动更新；原公式和文件完整保留。14kn竖虚线及图下结论为独立注释，修改数据后须同步更新。

## 真实图片处理与占位图替换

三张主图均来自 `{BASE / '图像'}`，裁切记录见 `完善制作资料/source/crop_manifest.json`：

1. `01_组员三维曲面预览.png`：裁取完整船体主体，等比例显示；这是曲面数据预览，非MAXSURF截图。另用于第4页缩略图。
2. `02_组员型线图全图.png`：保留型值表、横剖、纵剖和半宽水线的整体布局，裁去下方外围图纸说明。原图细节在源文件中保留。
3. `04_典型横剖面.png`：使用原图“艉部至舯部”完整子图，不重绘、不平滑、不添加插值点。虚线沿用原图参考水线，图注说明其不构成满载核定结论。

旧稿中的技术占位船照、船体、型线、横剖、GA、GZ、发动机及尾部示意均已从编辑页移除。本次没有生成AI技术图片。简单船体轮廓、文档/舱室/性能图标仅表示任务或专业类别，不承载已完成结果。模型、CAD、横剖面为独立图片，可移动、缩放、裁剪或替换，其内部曲面和线条不是PowerPoint几何对象。

## 未闭合、未展示的事项

- 当前统一版本的总布置图、技术规格书、舱容图及完整稳性结果，尚未并入本次材料。没有用旧方案概念稿代替。
- 曲面公平性、接缝、水密性、当前MSD重新切剖与二维型线对照、同版本正式静水力输出仍待验证。
- 独立空船重量、载荷重心、舱容装载及重量—浮力闭合仍待完成，未核定最终满载吃水。
- 10.133923m（缩放满载参考）、约10.120m（组员条件匹配副本）、10.163526m（缩放采样水线）含义不同；不作为本版快速性工况，也不混作最终满载吃水。
- 主机/桨最终选择、实际尾部净空、正式EEDI、续航完整输入及成本仍未闭合。本版不显示EEDI达标、最终造价、净空通过或主机定型结论。
- 本次必须使用的三张真实图片和计算工作簿均已找到，没有因核心素材缺失而使用虚构替代图。缺少的是可以并入同一设计状态的其他专业成果。

## 渲染与文件验收

- 实际通过Microsoft PowerPoint打开、渲染8页并导出PDF。PDF共8页，经Poppler再次渲染并逐页查看。
- 已完成“生成—实际渲染—修正—再渲染”闭环，修正计划页长标题、文本越界、信息条触及页脚、图表轴标题位置等问题。
- 最终文本边界检查为0项溢出；版面、包结构、标题位置、字体和原生图表缓存/内嵌工作簿校验通过。
- 页内共有 {native} 个原生形状，其中 {textcount} 个含可编辑文本；另有1个原生图表及4处独立真实图片（3张主图和1处模型缩略复用）。不存在整页截图替代内容。
- 在测试副本中修改图表系列名、调整尺寸、保存并重新打开成功，未更改交付文件。
- 模板校徽、右上装饰与页脚进行区域对照，数据详见 `完善制作资料/.build/delivery_audit.json`；上、下模板内容未用新增遮罩覆盖。
- 输入、图像裁切、数据快照、源代码和验证记录保存在 `完善制作资料/`。
- 页面演讲者备注包含来源和时间建议：15、40、30、30、55、50、45、35秒，合计300秒。实际讲述时长仍取决于语速。

PPTX SHA-256：`{sha(PPT)}`  
PDF SHA-256：`{sha(PDF)}`
'''
(OUT/'PPT完善记录.md').write_text(record,encoding='utf-8')
print(json.dumps({'native_shapes':native,'text_objects':textcount,'pictures':pictures,'chart_error':max(errors),'template_comparisons':comparisons,'unchanged_input_count':len(preserved),'manifest_rows':len(rows)},ensure_ascii=False,indent=2))
