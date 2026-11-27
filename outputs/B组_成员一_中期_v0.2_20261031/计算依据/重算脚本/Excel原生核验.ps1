$ErrorActionPreference = 'Stop'
$taskRoot = (Get-Location).Path
$taskOutput = Join-Path $taskRoot 'outputs/B组_成员一_中期_v0.2_20261031'
$records = [System.Collections.Generic.List[string]]::new()
$excelCheck = New-Object -ComObject Excel.Application
$excelCheck.Visible = $false
$excelCheck.DisplayAlerts = $false
try {
    $resistance = $excelCheck.Workbooks.Open((Join-Path $taskOutput '02_阻力快速性与总体校核.xlsx'))
    $excelCheck.CalculateFullRebuild()
    $newHull = $resistance.Worksheets.Item('新船换算')
    $basePower = $newHull.Range('F17').Value2
    if ([Math]::Abs($basePower - 3449.5047886509865) -gt 0.000001) { throw '新船14节功率与独立计算不符' }
    $newHull.Range('B5').Value2 = 33000
    $excelCheck.CalculateFullRebuild()
    if ([Math]::Abs($newHull.Range('F17').Value2 - $basePower) -lt 0.001) { throw '载重量修改未联动' }
    $newHull.Range('B5').Value2 = 33500
    $eedi = $resistance.Worksheets.Item('EEDI与续航')
    $eedi.Range('B17').Value2 = 14
    $excelCheck.CalculateFullRebuild()
    if ($eedi.Range('B22').Value2 -ne '待补数据') { throw '补一个输入后掩盖了其余EEDI缺项' }
    $eedi.Range('B17').ClearContents() | Out-Null
    $costCheck = $resistance.Worksheets.Item('建造成本待补')
    $costCheck.Range('D7').Value2 = 1000000
    $excelCheck.CalculateFullRebuild()
    if ($costCheck.Range('E19').Value2 -ne '待补完整成本') { throw '成本缺项被误计为0' }
    $costCheck.Range('D7').ClearContents() | Out-Null
    $excelCheck.CalculateFullRebuild()
    $records.Add(('新船14节有效功率核对 {0:F9} kW；33000 t输入联动，已恢复33500 t；EEDI和成本缺项门槛通过。' -f $newHull.Range('F17').Value2))
    $resistance.Save()
    $resistance.Close($false)

    $weight = $excelCheck.Workbooks.Open((Join-Path $taskOutput '03_重量重心与浮态待补.xlsx'))
    $weightSheet = $weight.Worksheets.Item('Weight')
    $restoreFormula = $weightSheet.Range('B6:J33').Formula
    $leafRows = @(6,7,8,9,10,12,13,14,15,17,18,19,20,22,23,24,25,26,27,29,30,31,32,33)
    foreach ($r in $leafRows) { $weightSheet.Range(('B{0}' -f $r)).Value2 = 0 }
    $excelCheck.CalculateFullRebuild()
    if ([Math]::Abs($weightSheet.Range('B34').Value2 - 8310.700160893894) -gt 0.000001) { throw '显式零载荷汇总不正确' }
    $weightSheet.Range('B6').Value2 = 1000
    $weightSheet.Range('C6').Value2 = 2
    $weightSheet.Range('E6').Value2 = 5
    $weightSheet.Range('G6').Value2 = 0
    $weightSheet.Range('I6').Value2 = 0
    $excelCheck.CalculateFullRebuild()
    if ([Math]::Abs($weightSheet.Range('B34').Value2 - 9310.700160893894) -gt 0.000001) { throw '重量小计重复累计或未累计' }
    $records.Add(('工况测试：加入1000 t测试载荷后总重 {0:F6} t，已验证不重复计小计。' -f $weightSheet.Range('B34').Value2))
    $weightSheet.Range('B7').ClearContents() | Out-Null
    $excelCheck.CalculateFullRebuild()
    if ($weightSheet.Range('B34').Value2 -ne '待补工况') { throw '未知载荷被误当作0' }
    $weightSheet.Range('B6:J33').Formula = $restoreFormula
    $excelCheck.CalculateFullRebuild()
    if ($weightSheet.Range('B34').Value2 -ne '待补工况') { throw '测试后工况未恢复' }
    $records.Add('未知载荷与显式0区分通过；测试输入已全部恢复。')
    $weight.Save()
    $weight.Close($false)
} finally {
    $excelCheck.Quit()
}
$records | Set-Content -LiteralPath (Join-Path $taskRoot 'tmp/Excel核验记录.txt') -Encoding utf8
$records
