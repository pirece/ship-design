param([string]$InputPptx,[string]$OutputPptx)
$ErrorActionPreference='Stop'
$app=New-Object -ComObject PowerPoint.Application
$deck=$null
try {
    $deck=$app.Presentations.Open($InputPptx,0,0,0)
    $slide=$deck.Slides.Item(5)
    $frame=$slide.Shapes.Item('图表_性能参考状态阻力与有效功率')
    $chart=$frame.Chart
    # PowerPoint 在首次打开时会重排图表，明确其实际绘图区和各原生标题位置。
    $chart.ChartTitle.Left=0
    $chart.ChartTitle.Top=0
    $chart.Legend.Left=350
    $chart.Legend.Top=26
    $chart.PlotArea.InsideLeft=48
    $chart.PlotArea.InsideTop=54
    $chart.PlotArea.InsideWidth=495
    $chart.PlotArea.InsideHeight=100
    $rt=$chart.Axes(2,1).AxisTitle
    $rt.Orientation=0
    $rt.Left=0
    $rt.Top=29
    $pe=$chart.Axes(2,2).AxisTitle
    $pe.Orientation=0
    $pe.Left=531
    $pe.Top=29
    $vx=$chart.Axes(1,1).AxisTitle
    $vx.Orientation=0
    $vx.Left=270
    $vx.Top=166
    # 注释虚线使用最终绘图区坐标，避免偏离 14 kn 的实际数据点。
    $ref=$slide.Shapes.Item('14kn参考线')
    $ref.Left=$frame.Left+$chart.PlotArea.InsideLeft+$chart.PlotArea.InsideWidth*3/5+3.75
    $ref.Top=$frame.Top+$chart.PlotArea.InsideTop+3
    $ref.Height=$chart.PlotArea.InsideHeight-3
    $chart.Refresh()
    $deck.SaveAs($OutputPptx,24)
    Write-Output ('图表实际绘图区：'+$chart.PlotArea.InsideLeft+','+$chart.PlotArea.InsideTop+','+$chart.PlotArea.InsideWidth+','+$chart.PlotArea.InsideHeight)
} finally {
    if ($null -ne $deck) {$deck.Close()}
    $app.Quit()
}
