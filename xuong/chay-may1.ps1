# CHI DUNG KHI MAY BAN (may nha) HONG. Viec nang chay tren MAY BAN; may Surface khong chay xuong (chu trang 24/10).
# Xuong chay tren MAY 1 – Task Scheduler "Net24\Xuong<Ten>" gọi:
#   powershell -NoProfile -ExecutionPolicy Bypass -File chay-may1.ps1 <xuong> [so-mon]
# Dùng bản clone RIÊNG Documents\Net24-xuong (không đụng kho các phiên Claude đang sửa), bản dựng nặng ở %USERPROFILE%\Net24-lam.
param([string]$Xuong = "mau", [string]$SoMon = "1")
$ErrorActionPreference = "Continue"
$GF = Split-Path -Parent $PSScriptRoot
$env:NET24 = Join-Path $env:USERPROFILE "Documents\Net24-xuong"
$env:N24_LAM = Join-Path $env:USERPROFILE "Net24-lam"
$env:PYTHONIOENCODING = "utf-8"
$env:N24_CPU_MAX = "101"  # may 1: CPU luon 99-100% vi cac phien khac -> khong bo luot, chay uu tien thap (BelowNormal) de khong tranh CPU
$log = Join-Path $env:N24_LAM "chay-may1.log"
New-Item -ItemType Directory -Force $env:N24_LAM | Out-Null
"$(Get-Date -Format 'yyyy-MM-dd HH:mm') bat dau $Xuong" | Out-File -Append -Encoding utf8 $log
git -C $GF pull -q --rebase 2>&1 | Out-File -Append -Encoding utf8 $log
git -C $env:NET24 pull -q --rebase 2>&1 | Out-File -Append -Encoding utf8 $log
$out = Join-Path $env:N24_LAM "dieu-toc-$Xuong.out"
$p = Start-Process python -ArgumentList "`"$(Join-Path $PSScriptRoot 'dieu-toc.py')`" $Xuong $SoMon" -NoNewWindow -PassThru -RedirectStandardOutput $out -RedirectStandardError "$out.err"
try { $p.PriorityClass = "BelowNormal" } catch {}
$p.WaitForExit()
Get-Content $out, "$out.err" -ErrorAction SilentlyContinue | Out-File -Append -Encoding utf8 $log
# dong bo nhật ký xưởng (NHAT-KY-chay.txt, chay_v2.da-nop.json) về game-factory
git -C $GF add "xuong/$Xuong" 2>&1 | Out-Null
git -C $GF commit -qm "nhat ky xuong $Xuong (may 1)" 2>&1 | Out-Null
git -C $GF push -q 2>&1 | Out-File -Append -Encoding utf8 $log
"$(Get-Date -Format 'yyyy-MM-dd HH:mm') xong $Xuong" | Out-File -Append -Encoding utf8 $log
