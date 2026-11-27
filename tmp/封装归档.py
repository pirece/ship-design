from pathlib import Path
import csv
import hashlib
import shutil
import zipfile

# 将核验后的报告预览、计算依据和文件校验值封装成可移交归档。
根 = Path.cwd()
输出 = 根 / 'outputs/B组_成员一_中期_v0.2_20261031'
shutil.copy2(根 / 'tmp/中期报告检查.pdf', 输出 / '01_成员一中期设计计算报告.pdf')
说明 = 输出 / '00_阅读说明.txt'
说明.write_text(说明.read_text(encoding='utf-8') + '\n附：同名PDF为Word原生导出的12页阅读版；继续编辑请使用DOCX。\n', encoding='utf-8')
核验 = 输出 / '计算依据/核验记录.txt'
核验.write_text(核验.read_text(encoding='utf-8-sig') + '\n最终视觉检查：报告12页逐页检查完成，公式、表格与页脚无截断；功率曲线预览正常。\n最终数据检查：两本工作簿无Excel错误单元格，正式EEDI、总成本与装载工况仍按缺项保留待补。\n', encoding='utf-8-sig')
for 名称 in ['归档与最终核验.py', '封装归档.py']:
    shutil.copy2(根 / 'tmp' / 名称, 输出 / '计算依据/重算脚本' / 名称)
清单 = 输出 / '文件清单_SHA256.csv'
文件 = sorted(p for p in 输出.rglob('*') if p.is_file() and p != 清单)
with 清单.open('w', encoding='utf-8-sig', newline='') as 流:
    表 = csv.writer(流)
    表.writerow(['相对路径', '字节数', 'SHA256'])
    for 路径 in 文件:
        表.writerow([路径.relative_to(输出).as_posix(), 路径.stat().st_size, hashlib.sha256(路径.read_bytes()).hexdigest()])
压缩路径 = 输出.parent / (输出.name + '.zip')
with zipfile.ZipFile(压缩路径, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as 包:
    for 路径 in sorted(输出.rglob('*')):
        if 路径.is_file():
            包.write(路径, 路径.relative_to(输出.parent).as_posix())
with zipfile.ZipFile(压缩路径) as 包:
    assert 包.testzip() is None, 'ZIP完整性检查失败'
    assert len(包.namelist()) == len(文件) + 1
print(f'已归档 {len(文件)} 个文件及校验清单；ZIP完整性检查通过。')
print(f'{压缩路径}，{压缩路径.stat().st_size / 1024 / 1024:.2f} MB')
