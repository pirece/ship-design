from pathlib import Path
import json
from docx import Document
from pypdf import PdfReader
import openpyxl

根目录 = Path.cwd()
输出 = 根目录 / 'tmp' / '资料提取'
输出.mkdir(parents=True, exist_ok=True)
for 路径 in 根目录.rglob('*'):
    if not 路径.is_file() or 'tmp' in 路径.parts or 路径.name.startswith('~$'):
        continue
    if 路径.suffix.lower() == '.docx':
        文档 = Document(路径)
        段落 = [段.text for 段 in 文档.paragraphs]
        for 编号, 表 in enumerate(文档.tables, 1):
            段落.append(f'\n表格 {编号}')
            段落.extend(' | '.join(格.text for 格 in 行.cells) for 行 in 表.rows)
        (输出 / (路径.stem + '.txt')).write_text('\n'.join(段落), encoding='utf-8')
    elif 路径.suffix.lower() == '.pdf':
        阅读器 = PdfReader(路径)
        内容 = '\n'.join(f'\n===== PDF页 {序号} =====\n{页.extract_text()}' for 序号, 页 in enumerate(阅读器.pages, 1))
        (输出 / (路径.stem + '.txt')).write_text(内容, encoding='utf-8')
    elif 路径.suffix.lower() == '.xlsx':
        工作簿 = openpyxl.load_workbook(路径, data_only=False)
        缓存 = openpyxl.load_workbook(路径, data_only=True)
        内容 = []
        for 表 in 工作簿:
            内容.append(f'工作表 {表.title} 范围 {表.max_row}行 {表.max_column}列 合并 {表.merged_cells}')
            for 行 in 表:
                项 = []
                for 格 in 行:
                    if 格.value is not None:
                        值 = f'{格.coordinate}={格.value}'
                        if 格.data_type == 'f':
                            值 += f' [缓存={缓存[表.title][格.coordinate].value}]'
                        项.append(值)
                if 项:
                    内容.append(' | '.join(项))
        (输出 / (路径.stem + '.txt')).write_text('\n'.join(内容), encoding='utf-8')
print('提取完成：', 输出)
