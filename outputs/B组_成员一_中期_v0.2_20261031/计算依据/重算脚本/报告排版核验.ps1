$ErrorActionPreference = 'Stop'
$taskPath = (Get-Location).Path
$reportPath = Join-Path $taskPath 'outputs/B组_成员一_中期_v0.2_20261031/01_成员一中期设计计算报告.docx'
$reportApp = New-Object -ComObject Word.Application
$reportApp.Visible = $false
try {
    $reportDoc = $reportApp.Documents.Open($reportPath)
    $reportDoc.Fields.Update() | Out-Null
    $reportDoc.ExportAsFixedFormat((Join-Path $taskPath 'tmp/中期报告检查.pdf'),17)
    $reportDoc.Save()
    $reportDoc.Close(0)
} finally { $reportApp.Quit() }
& 'C:/Users/董昱彤/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -c "import pypdfium2 as p; from pathlib import Path; d=p.PdfDocument('tmp/中期报告检查.pdf'); o=Path('tmp/报告页面'); o.mkdir(exist_ok=True); [d[i].render(scale=1.5).to_pil().save(str(o/f'page-{i+1}.png')) for i in range(len(d))]; print('已渲染',len(d),'页')"
