from pathlib import Path
import csv, hashlib, shutil, zipfile
根=Path.cwd();出=根/'outputs/B组_首次汇报综合材料_v0.3_20261101';源=根/'outputs/33500DWT_图纸模型表格_20261101'
for p in (出/'原始成果').rglob('*'):
    if p.is_file():
        原=源/p.relative_to(出/'原始成果') if p.name!='组员原说明.md' else 源/'先读我_文件说明.md'
        assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(原.read_bytes()).digest(),p
说明='''B组首次汇报综合材料 v0.3  2026年11月1日

优先阅读01_首次汇报综合分析.docx：10页，含5张图像、数据表、结论边界和文件索引。
02_供GPT读取的完整文本.txt与Word正文对应；图像请同时上传Word或图像目录。
三维建模补充说明.txt、型线图补充说明.txt分别汇集两部分的补充分析。
本次不涉及PPT版式设计。原几何、MSD、DWG和DXF均未修改。

本次实际核验
751个型值点、31个站位；CSV与Markers坐标一致；CSV与三维DXF点集差小于1e-8 m。
型值点与母型按k缩放一致；最大半宽与组内型宽一致。
二维DXF结构审查错误0、修复0；这不代表曲线或工程图审查全部通过。
IGES读取7个曲面目录项；本轮未对MSD作原生曲面公平性、静水力或重新切剖验证。
原始成果拷贝逐文件SHA256对比通过。Word原生导出后10页逐页视觉检查通过。
当前系统无LibreOffice，沿用已诊断的Word原生PDF导出和PDFium页面检查流程；页面图及检查PDF保存在工作区tmp，不作为设计成果。

数据使用注意
原满载参考10.133923 m与提交说明的约10.120 m满载副本分开使用。
131.266 t为母型排水口径差的缩放假设，不是核定钢板重量。
CSV折线图不是MSD重新切剖，不可由点文件的吻合推断曲面拟合合格。
前期性能估算仍有原工况限制；旧方案表格未纳入新方案计算依据。
归档包中的工作簿都是原件副本，本轮没有修改或重新计算这些工作簿。

后续GPT分析建议
先读取Word或纯文本，再结合5张原始分辨率图像；引用数值时保留对应状态与单位。
不要将“提交说明”“前期估算”“待核验”改写为“本轮已验证”。不把预览图冒充软件截图。
模型和CAD文件供工程软件进一步核查，不要求GPT直接解析其几何。
'''
(出/'00_先读我.txt').write_text(说明,encoding='utf-8')
证据=出/'核查数据';shutil.copy2(根/'tmp/首次汇报核查.py',证据/'本轮数据核查脚本.py')
(证据/'脚本运行说明.txt').write_text('核查脚本记录本轮方法，默认从原工作区运行；需要Python及numpy、matplotlib、ezdxf。附加库安装在工作区tmp/analysislibs，运行器使用Codex依赖目录。移动归档后应先调整源码中的输入输出路径。报告和原始几何不依赖脚本即可查阅。',encoding='utf-8')
文件=sorted(p for p in 出.rglob('*') if p.is_file() and p.name!='文件清单_SHA256.csv')
with (出/'文件清单_SHA256.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['相对路径','字节数','SHA256'])
    for p in 文件:w.writerow([p.relative_to(出).as_posix(),p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest()])
压缩=出.parent/(出.name+'.zip')
with zipfile.ZipFile(压缩,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(出.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(出.parent).as_posix())
with zipfile.ZipFile(压缩) as z:assert z.testzip() is None
print(f'原件对比通过；{len(文件)}项文件及SHA256清单；压缩包{压缩.stat().st_size/1024/1024:.2f}MB；ZIP完整性通过。')
