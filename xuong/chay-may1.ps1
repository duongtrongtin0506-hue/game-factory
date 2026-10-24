# Xưởng chạy trên MÁY 1 (máy nhà dự phòng khi máy 2 ngủ) – Task Scheduler "Net24\Xuong<Ten>" gọi:
#   powershell -NoProfile -ExecutionPolicy Bypass -File chay-may1.ps1 <xuong> [so-mon]
# Dùng bản clone RIÊNG Documents\Net24-xuong (không đụng kho các phiên Claude đang sửa), bản dựng nặng ở %USERPROFILE%\Net24-lam.
param([string]$Xuong = "mau", [string]$SoMon = "1")
$ErrorActionPreference = "Continue"
$GF = Split-Path -Parent $PSScriptRoot
$env:NET24 = Join-Path $env:USERPROFILE "Documents\Net24-xuong"
$env:N24_LAM = Join-Path $env:USERPROFILE "Net24-lam"
$env:PYTHONIOENCODING = "utf-8"
$log = Join-Path $env:N24_LAM "chay-may1.log"
New-Item -ItemType Directory -Force $env:N24_LAM | Out-Null
"$(Get-Date -Format 'yyyy-MM-dd HH:mm') bat dau $Xuong" | Out-File -Append -Encoding utf8 $log
git -C $GF pull -q --rebase 2>&1 | Out-File -Append -Encoding utf8 $log
git -C $env:NET24 pull -q --rebase 2>&1 | Out-File -Append -Encoding utf8 $log
python (Join-Path $PSScriptRoot "dieu-toc.py") $Xuong $SoMon 2>&1 | Out-File -Append -Encoding utf8 $log
# đồng bộ nhật ký xưởng (NHAT-KY-chay.txt, chay_v2.da-nop.json) về game-factory
git -C $GF add "xuong/$Xuong" 2>&1 | Out-Null
git -C $GF commit -qm "nhat ky xuong $Xuong (may 1)" 2>&1 | Out-Null
git -C $GF push -q 2>&1 | Out-File -Append -Encoding utf8 $log
"$(Get-Date -Format 'yyyy-MM-dd HH:mm') xong $Xuong" | Out-File -Append -Encoding utf8 $log
