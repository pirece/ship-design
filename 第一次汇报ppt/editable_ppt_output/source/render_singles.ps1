$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$output=Join-Path $root '.build\single_renders'
New-Item -ItemType Directory -Force -Path $output | Out-Null
$scenes=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'scenes.json') -Raw | ConvertFrom-Json
$app=New-Object -ComObject PowerPoint.Application
$records=@()
try {
    foreach ($scene in $scenes) {
        $stem=[IO.Path]::GetFileNameWithoutExtension($scene.source)
        $deck=$app.Presentations.Open((Join-Path $root ('pptx\'+$stem+'_editable.pptx')),-1,0,0)
        try {
            if ($deck.Slides.Count -ne 1) {throw '单页文件页数不正确'}
            $deck.Slides.Item(1).Export((Join-Path $output ($stem+'.png')),'PNG',1672,941)
            $ungrouped=$false
            foreach ($shape in $deck.Slides.Item(1).Shapes) {
                if ($shape.Type -eq 6) {
                    # 在未保存的检查副本上实际取消一个组合，验证内部对象仍可访问。
                    $parts=$shape.Ungroup()
                    $ungrouped=($parts.Count -gt 1)
                    break
                }
            }
            $deck.Saved=-1
            $records+=@{file=$stem+'_editable.pptx';opened=$true;slideCount=1;rendered=$true;ungroupChecked=$ungrouped}
        } finally {$deck.Close()}
    }
} finally {$app.Quit()}
ConvertTo-Json -InputObject $records -Depth 5 | Set-Content -LiteralPath (Join-Path $root 'single_file_checks.json') -Encoding utf8
Write-Output '九个单页文件均已在 PowerPoint 打开并实际渲染'
