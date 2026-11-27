param([string]$OutputName=('pptx_rebuilt_'+(Get-Date -Format 'yyyyMMdd_HHmmss')))
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$node='C:\Users\董昱彤\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
$modules='C:\Users\董昱彤\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
$python='C:\Program Files\Python313\python.exe'
$env:PYTHONIOENCODING='utf-8'
New-Item -ItemType Directory -Force -Path (Join-Path $root '.build') | Out-Null
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'node_modules'))) {
    New-Item -ItemType Junction -Path (Join-Path $PSScriptRoot 'node_modules') -Target $modules | Out-Null
}
& $python (Join-Path $PSScriptRoot 'prepare.py')
if ($LASTEXITCODE -ne 0) {throw '素材与元素清单生成失败'}
& $node (Join-Path $PSScriptRoot 'build.mjs')
if ($LASTEXITCODE -ne 0) {throw '原生幻灯片生成失败'}
& $python (Join-Path $PSScriptRoot 'package.py')
if ($LASTEXITCODE -ne 0) {throw '文件打包失败'}
& $node (Join-Path $PSScriptRoot 'finalize.mjs') $OutputName
if ($LASTEXITCODE -ne 0) {throw '文件验证失败'}
& (Join-Path $PSScriptRoot 'render.ps1') -InputPptx (Join-Path $root ($OutputName+'\combined_editable.pptx')) -OutputDirectory (Join-Path $root ($OutputName+'\previews'))
Write-Output ('重新生成完成：'+(Join-Path $root $OutputName))
