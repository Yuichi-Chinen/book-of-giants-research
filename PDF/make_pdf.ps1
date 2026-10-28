# 調査報告 PDF を生成する（目次ページ番号のため2回印刷）
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$html = Join-Path $here "巨人の書_マニ教_調査報告-print.html"
$pdf  = Join-Path $here "巨人の書_マニ教_調査報告.pdf"
$json = Join-Path $here "pages.json"
$url  = "file:///" + $html.Replace([char]92, [char]47)

function Print-Pdf {
    if (Test-Path $pdf) { Remove-Item $pdf }
    Start-Process -FilePath $edge -Wait -ArgumentList @(
        "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        "--virtual-time-budget=15000", "--print-to-pdf=`"$pdf`"", "`"$url`"")
}

python (Join-Path $here "build.py")
Print-Pdf
python (Join-Path $here "pages.py") $pdf $json
python (Join-Path $here "build.py") $json
Print-Pdf
Remove-Item $json
Write-Host "done: $pdf"
