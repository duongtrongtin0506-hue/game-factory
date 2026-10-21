"""Run CỬA 0 (and CỬA 1 when it has not passed yet) on every product in HANG/. Exit 1 if any product is red."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
bad = 0
for item in sorted((ROOT / "HANG").glob("*")):
    if not item.is_dir() or (item / ".da-nop").exists():
        continue
    meta = {}
    if (item / "meta.json").exists():
        meta = json.loads((item / "meta.json").read_text(encoding="utf-8"))
    args = [sys.executable, str(ROOT / "tools/chung/cua0.py"), str(item)]
    if meta.get("web"):
        args += ["--web", meta["web"]]
    if meta.get("epub"):
        args += ["--epub", meta["epub"]]
    if meta.get("free"):
        args += ["--free"]
    r0 = subprocess.run(args)
    if r0.returncode:
        bad += 1
        continue
    c1 = item / "CUA1.json"
    if not (c1.exists() and json.loads(c1.read_text(encoding="utf-8")).get("pass")):
        subprocess.run([sys.executable, str(ROOT / "tools/chung/cua1.py"), str(item)] + (["--free"] if meta.get("free") else []))
print("kiem xong, do:", bad)
sys.exit(1 if bad else 0)
