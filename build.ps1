# Builds one upload package per game and portal:
#   dist\<game>\<portal>\index.html   and   dist\<game>\<game>-<portal>.zip
# Each package is the game's index.html with the PORTAL build flag set.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$utf8 = New-Object Text.UTF8Encoding $false

# Car Jam keeps its generated level list in a separate file; merge it into index.html first.
$carSrc = [IO.File]::ReadAllText("$root\car-jam\index.src.html")
$levels = (Get-Content "$root\car-jam\tools\levels.txt" -Raw).Trim()
if (-not $carSrc.Contains('/*LEVELS*/')) { throw 'LEVELS marker not found in car-jam\index.src.html' }
[IO.File]::WriteAllText("$root\car-jam\index.html", $carSrc.Replace('/*LEVELS*/', $levels), $utf8)

$flag = "const PORTAL = 'gamemonetize';"
foreach ($game in 'tap-arcade', 'boba-sort', 'car-jam', 'tile-trio', 'one-line') {
    $src = [IO.File]::ReadAllText("$root\$game\index.html")
    if (-not $src.Contains($flag)) { throw "PORTAL flag not found in $game\index.html" }
    foreach ($portal in 'gamemonetize', 'crazygames', 'none') {
        $stage = "$root\dist\$game\$portal"
        New-Item -ItemType Directory -Force $stage | Out-Null
        [IO.File]::WriteAllText("$stage\index.html", $src.Replace($flag, "const PORTAL = '$portal';"), $utf8)
        $zip = "$root\dist\$game\$game-$portal.zip"
        Compress-Archive -Path "$stage\index.html" -DestinationPath $zip -Force
        "{0,-11} {1,-13} {2,6} bytes" -f $game, $portal, (Get-Item $zip).Length
    }
}
