from pathlib import Path
import json, shutil, hashlib, csv, zipfile
from datetime import datetime
from pypdf import PdfReader
import openpyxl

根=Path.cwd()
输出=根/'outputs/B组_成员一_中期_v0.2_20261031'
依据=输出/'计算依据'
原件=依据/'课程原件'
原件.mkdir(exist_ok=True)
来源=[根/'《船舶设计Ⅱ》_课程设计指导书_20261016.docx',根/'0002_Holtrop阻力估算方法介绍.pdf',根/'0003_阻力估算模板.xlsx',根/'0004_流程.docx',根/'重量重心和浮态调整.xlsx',根/'船舶设计Ⅱ_第五讲_性能计算_20261012.pdf']
来源.extend((根/'0000DMAU软件2026/0000DMAU软件').iterdir())
来源.append(next((根/'B组_33500DWT_第一步初算_v0.1_20261026').rglob('DC081210,101,001JS装载手册(初步)-A_20230206.pdf')))
来源.extend([p for p in (根/'B组_33500DWT_第一步初算_v0.1_20261026').rglob('*') if p.is_file() and p.name.startswith(('01_第一步主尺度','02_第一步结果与计算说明.md','03_Codex协作交接.md','04_统一参数'))])
for p in 来源:
    目的=原件/p.name
    shutil.copy2(p,目的)
    assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(目的.read_bytes()).digest()

for p in (依据/'外部资料').glob('*.pdf'):
    assert len(PdfReader(p).pages)>0,p

计算=json.loads((根/'tmp/计算结果.json').read_text(encoding='utf-8'))
软件=json.loads((根/'tmp/DMAU摘要.json').read_text(encoding='utf-8'))
阻力=openpyxl.load_workbook(输出/'02_阻力快速性与总体校核.xlsx',data_only=True)
重量=openpyxl.load_workbook(输出/'03_重量重心与浮态待补.xlsx',data_only=True)
for w in [阻力,重量]:
    for s in w:
        for row in s:
            for c in row:
                assert c.data_type!='e',(s.title,c.coordinate,c.value)
assert 阻力['EEDI与续航']['B22'].value=='待补数据'
assert 阻力['建造成本待补']['E19'].value=='待补完整成本'
assert 重量['Weight']['B34'].value=='待补工况'
assert abs(重量['母型分区缩放']['B22'].value-8650)<1e-8
assert abs(阻力['新船换算']['F17'].value-计算['新船'][3]['pe'])<1e-7

快照={'版本':'v0.2','日期':'2026-10-31','范围':'中期可完成任务，缺少项按用户指示跳过并列明','角色':'成员一 总体设计组长','方法':'沿用v0.1几何相似，独立重量未完成','母型与新船阻力':计算,'DMAU软件结果':软件,'空船粗估':{'LW_t':重量['Sheet1']['C6'].value,'XG_AP_m':重量['Sheet1']['C11'].value,'ZG_BL_m':重量['Sheet1']['C12'].value,'XG_舯_m':重量['Sheet1']['C14'].value,'分区加权XG_AP_m':重量['母型分区缩放']['F22'].value},'EEDI':{a:阻力['EEDI与续航'][a].value for a in ['B8','B9','B10','B25','B27','B44']},'未完成':['独立钢料机电舾装重量','实际装载浮态与完整稳性','FORAN或Maxsurf新船模型校核','实际桨叶净空','满载75%MCR航速与正式EEDI','最终主辅机桨定型','建造成本总价','终版报告与PPT']}
(输出/'04_统一参数与结果快照.json').write_text(json.dumps(快照,ensure_ascii=False,indent=2),encoding='utf-8')
说明='''B组33500吨散货船成员一中期成果 v0.2
日期：2026年10月31日

阅读顺序
1. 01_成员一中期设计计算报告.docx：12页，中期结果、计算推导、修正依据、缺项及后续安排。
2. 02_阻力快速性与总体校核.xlsx：保留课程ship与HoltropMennen模板，补齐母型阻力；新增对应航速、新船换算、DMAU主机比较、EEDI续航和成本待补表。
3. 03_重量重心与浮态待补.xlsx：填入现阶段空船粗估及力矩，补全汇总和浮态公式，新增母型17分区缩放；黄色格为后续数据输入。
4. 04_统一参数与结果快照.json：本版机器可读静态快照，修改Excel后不会自动更新。
5. 05_后续任务与数据交接.txt：可直接发给组员的数据清单与执行顺序。本次没有代发消息。

本版结果边界
新船9.699753 m性能参考吃水下14 kn时PE约3449.505 kW；这不是33500 t满载航速证明。
空船8310.700 t为几何缩放初值，17个分区仍是同一缩放假设，不代表独立结构和设备估算。
候选A与B的DMAU航速为14.42、14.44 kn；它们仍需尾部净空、完整性能和EEDI联合校核。
本船EEDI参考线6.677807，第三阶段限值4.674465。正式EEDI输入不足；简化情景不能作合规证书。
建造成本未给出虚构总价。

公式与原始文件问题修正
公制马力与英制马力区分；DMAU输入采用1 PS=0.7355 kW。
附带原始dmau.ipt存在定宽错位，会读出材料系数91.2及t=0.2100；正式输入已按8F9.4重写。
流程中的相似转速比应按保持J不变推导为r^(-1/6)，详细见报告第6页。
流程的母型EEDI算式复算为7.044910，原写7.44为算术笔误；超限结论不变。

修改与重算
Excel公式可以联动，但DMAU输出是外部程序的静态结果。更新主尺度、型线、主机、桨径或推进因子后必须重跑DMAU。
原始课程文件未改动。下一轮另存v0.3，先更新输入和模型，后重算Excel与DMAU，再同步报告和JSON。
不得把黄色空格直接填0来消除“待补”；只有确定不存在的载荷才能填0。
各DMAU目录保存IPT、OUT、UTF-8中文结果及运行日志；输出数据以对应工况为准。

核验
Holtrop母型11 kn复现课程校核值；逐点独立计算对照；两工作簿经桌面Excel重算与输入扰动测试。
报告采用Word原生公式，已按实际Word分页渲染检查。模板渲染工具因系统无LibreOffice不可用，改用已安装Word原生PDF导出及PDFium逐页检查。
计算依据/含课程原件、厂家和IMO文件、软件输入输出、脚本与核验记录。文件清单_SHA256.csv用于追溯。
'''
(输出/'00_阅读说明.txt').write_text(说明,encoding='utf-8')
交接='''成员一后续任务与组员数据交接

成员二 总布置
提交总布置DWG、主要设备型号/数量/自重/三向重心、主机与机舱位置、桨轴高与尾部净空a/b/c/d。起重机30 t为起重量，不是自重。

成员三 型线及静水力
提交最终FORAN/Maxsurf模型与版本；在性能参考9.699753 m、满载参考10.133923 m和压载状态导出TF、TA、LWL、总排水量、型排水体积、CB、CP、CM、CWP、湿表面积、LCB、LCF、KM、MTC。
阻力额外需要去流段长、进流半角、球鼻艏截面积和形心、艉封板浸水面积、附体面积及尾部几何。
注明系数参考长度、外板修正、坐标原点、纵倾正号和软件版本。

成员四 舱容与稳性
提交各舱装载率—舱容—三向重心—自由液面矩表、货物积载因数和密度、满载出港/到港及压载工况、完整稳性计算书。
油水数量与重心必须来自同一装载工况；确认16000 nm所需燃油能否装下。

组长补充
取得独立钢料结构重量、机电舾装清单，完成重量裕量依据；取得主辅机对应负荷SFOC、燃料及排放配置；取得材料量、工时、设备和人工单价。
按满载75%MCR曲线确定Vref，检查能效及最低推进功率，不以较浅吃水CSR航速代替。

执行顺序
一、冻结模型及独立重量，复核载重量、舱容、允许吃水。
二、跑新模型各工况Holtrop，与海军系数法估算比较。
三、联合选SMCR/转速/桨径，重跑DMAU并实测净空。
四、完成燃油与EEDI闭合，有问题则回到前序优化。
五、补齐造价，汇总最终报告、技术规格书、成员贡献与PPT。

更新纪律
沿用AP向艏为正，ZG距BL；报告和公式必须说明不同坐标换算。
接收新结果时记录来源、日期、软件、版本与单位。保留v0.2原件，另存v0.3。
每次按“输入—计算表—DMAU—报告—参数快照—校验清单”顺序同步更新。
'''
(输出/'05_后续任务与数据交接.txt').write_text(交接,encoding='utf-8')
网址='''外部来源核对日期 2026-10-31
厂家2026主机手册页面
https://www.everllence.com/marine/products/planning-tools-and-downloads/marine-engine-programme
厂家2026手册PDF
https://www.everllence.com/docs/default-source/marine-documents/everllence-marine-engine-programme-2026.pdf?sfvrsn=88c90321_24
IMO现行导则索引
https://www.imo.org/en/ourwork/environment/pages/index-of-mepc-resolutions-and-guidelines-related-to-marpol-annex-vi.aspx
MEPC.364(79)
https://wwwcdn.imo.org/localresources/en/OurWork/Environment/Documents/annex/RESOLUTION%20MEPC.364(79).pdf
MEPC.410(84)
https://wwwcdn.imo.org/localresources/en/OurWork/Environment/Documents/Annex%2012.pdf
MEPC.324(75)
https://wwwcdn.imo.org/localresources/en/OurWork/Environment/Documents/Air%20pollution/MEPC.324(75).pdf
'''
(依据/'外部资料/来源网址.txt').write_text(网址,encoding='utf-8')
脚本=依据/'重算脚本'
脚本.mkdir(exist_ok=True)
for name in ['计算与软件输入.py','生成中期工作簿.mjs','生成中期报告.py','Excel原生核验.ps1','报告排版核验.ps1']:
    shutil.copy2(根/'tmp'/name,脚本/name)
shutil.copy2(根/'tmp/Excel核验记录.txt',依据/'核验记录.txt')
(脚本/'使用说明.txt').write_text('这些脚本记录本次计算实现。默认在原工作区根目录运行，依赖Codex提供的Python、Node和artifact-tool以及本机Word、Excel。迁移到另一电脑应先设置运行路径和依赖，不可直接把目录当独立安装软件。数学计算可独立查阅计算与软件输入.py。DMAU各工况目录可独立运行：输入00341700，使用默认文件名选N，中文输出选Y。生成脚本中的软件输出为本版快照；变更输入须先更新并重跑软件。',encoding='utf-8')
for p in 输出.glob('*.inspect.ndjson'):
    shutil.move(str(p),str(依据/p.name))

print('归档文件已准备，等待最终页面检查后生成SHA-256和ZIP。')
