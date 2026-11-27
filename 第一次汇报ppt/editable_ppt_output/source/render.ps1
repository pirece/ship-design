param([string]$InputPptx, [string]$OutputDirectory)
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$app=New-Object -ComObject PowerPoint.Application
$deck=$null
try {
    $deck=$app.Presentations.Open($InputPptx,-1,0,0)
    $deck.Export($OutputDirectory,'PNG',1672,941)
    $findings=[System.Collections.Generic.List[object]]::new()
    function Test-ShapeText($shape, $slideNumber) {
            if ($shape.Type -eq 6) {
                foreach ($child in $shape.GroupItems) { Test-ShapeText $child $slideNumber }
            }
            if ($shape.HasTextFrame -and $shape.TextFrame.HasText) {
                $tr=$shape.TextFrame2.TextRange
                if ($shape.Rotation -eq 0 -and ($tr.BoundWidth -gt $shape.Width+1.5 -or $tr.BoundHeight -gt $shape.Height+1.5)) {
                    $findings.Add(@{slide=$slideNumber;name=$shape.Name;text=$tr.Text;width=$shape.Width;boundWidth=$tr.BoundWidth;height=$shape.Height;boundHeight=$tr.BoundHeight})
                }
            }
    }
    foreach ($slide in $deck.Slides) {
        foreach ($shape in $slide.Shapes) { Test-ShapeText $shape $slide.SlideIndex }
    }
    ConvertTo-Json -InputObject @($findings) -Depth 5 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'text_fit.json') -Encoding utf8
    Write-Output ('已实际渲染 '+$deck.Slides.Count+' 页；待复核文本框 '+$findings.Count+' 个')
} finally {
    if ($null -ne $deck) {$deck.Close()}
    $app.Quit()
}
