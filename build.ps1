# Builds index.html from the template + data, and also writes public/index.html
# (the Cloudflare Pages output directory).
# Usage:  powershell -ExecutionPolicy Bypass -File build.ps1
$dir = $PSScriptRoot
$enc = New-Object System.Text.UTF8Encoding($false)   # UTF-8, no BOM
$json    = [System.IO.File]::ReadAllText("$dir\master_v2.json", [System.Text.Encoding]::UTF8)
$stories = [System.IO.File]::ReadAllText("$dir\stories.json",  [System.Text.Encoding]::UTF8)
$modern  = [System.IO.File]::ReadAllText("$dir\integrate.json", [System.Text.Encoding]::UTF8)
$html    = [System.IO.File]::ReadAllText("$dir\genealogy_template.html", [System.Text.Encoding]::UTF8)
$out = $html.Replace('/*__DATA__*/null', $json)
$out = $out.Replace('/*__STORIES__*/{}', $stories)
$out = $out.Replace('/*__MODERN__*/{"modern":[],"overlap":[]}', $modern)
if ($out.Contains('/*__DATA__*/null') -or $out.Contains('/*__STORIES__*/{}') -or $out.Contains('/*__MODERN__*/{"modern":[],"overlap":[]}')) {
  Write-Error "Placeholder not replaced - check template markers."
  exit 1
}
[System.IO.File]::WriteAllText("$dir\index.html", $out, $enc)
New-Item -ItemType Directory -Force -Path "$dir\public" | Out-Null
[System.IO.File]::WriteAllText("$dir\public\index.html", $out, $enc)
$len = $out.Length
Write-Host "Built index.html + public/index.html ($len bytes)"
