# -*- coding: utf-8 -*-
"""Lan chay hang ngay (GitHub Actions daily.yml, hoac chay tay): python tools/run_daily.py [--no-publish] [--weekly]
  1. kiem lai moi man bang bo giai   2. bo sung hang du tru man   3. build   4. kiem ban web tren man hinh dien thoai
  5. dang len cac nen tang co khoa (thieu khoa thi bo qua nen tang do)   6. ghi TRANG-THAI.md + metrics/history.json
  7. Discord 1 dong + diem danh healthchecks
Buoc nao hong thi dung, KHONG dang, bao Discord @here kem cach sua. --weekly gui them bao cao tuan (chu nhat)."""
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import bobasort
import build
import carjam
import notify
import tiletrio

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / "metrics" / "history.json"
VN = timezone(timedelta(hours=7))
FIX = {
    "kiem man": "chay python tools/carjam.py verify, tools/bobasort.py verify va tools/tiletrio.py verify, xoa man sai khoi levels/ hoac content-queue/",
    "bo sung hang du tru": "chay python tools/carjam.py fill 300 (hoac tools/bobasort.py, tools/tiletrio.py fill 300) tren may roi commit content-queue/",
    "build": "xem dau PORTAL va /*LEVELS*/ trong web/<game>/index.html",
    "kiem ban web": "chay python tools/smoke_test.py tren may, sua loi console cua game duoc neu ten",
    "dang": "kiem khoa nen tang trong GitHub Secrets (con han khong), chay lai workflow",
}


def step_verify():
    problems = carjam.verify() + bobasort.verify() + tiletrio.verify()
    if problems:
        raise RuntimeError("; ".join(problems[:3]))


def step_fill():
    for name, tool in (("Car Jam", carjam), ("Boba Sort", bobasort), ("Tile Trio", tiletrio)):
        if len(tool.load(tool.QUEUE)) < tool.QUEUE_TARGET:
            tool.fill(90)
        left = len(tool.load(tool.QUEUE))
        if left < tool.QUEUE_MIN:
            raise RuntimeError(f"hang du tru {name} chi con {left} man (can {tool.QUEUE_MIN})")


def step_test():
    out = subprocess.run([sys.executable, str(ROOT / "tools" / "smoke_test.py")], capture_output=True, timeout=420)
    text = out.stdout.decode("utf-8", "replace").strip()
    if out.returncode:
        bad = [line for line in text.splitlines() if "LOI" in line]
        raise RuntimeError("; ".join(bad)[:400] or out.stderr.decode("utf-8", "replace")[-300:])
    return len(text.splitlines())


def step_publish():
    """-> {nen tang: ket qua}. Cong web (GameMonetize, CrazyGames...) nop tay moi thang, khong nam o day."""
    done = {}
    key, user = notify.env("BUTLER_API_KEY"), notify.env("ITCH_USER")
    if not (key and user):
        done["itch.io"] = "bo qua (chua co BUTLER_API_KEY / ITCH_USER)"
    elif not shutil.which("butler"):
        done["itch.io"] = "bo qua (may nay khong co butler)"
    else:
        pushed, missing = 0, []
        for spec in (ROOT / "specs" / f"{g}.json" for g in build.GAMES):
            slug = json.loads(spec.read_text(encoding="utf-8")).get("itch")
            if slug:
                out = subprocess.run(["butler", "push", str(ROOT / "dist" / spec.stem / "none"), f"{user}/{slug}:html5"],
                                     capture_output=True, timeout=180, env=dict(os.environ, BUTLER_API_KEY=key))
                if out.returncode:  # butler ghi ly do o cuoi (sai khoa, chua co trang game...): dua vao bao cao de biet sua gi
                    text = (out.stdout + out.stderr).decode("utf-8", "replace").strip()
                    if "invalid game" in text.lower():  # chu chua tao trang game: viec cua chu, khong phai loi
                        missing.append(slug)
                        continue
                    raise RuntimeError(f"itch.io {slug}: {' | '.join(text.splitlines()[-3:])}")
                pushed += 1
        done["itch.io"] = f"da day {pushed} game"
        if missing:
            done["itch.io"] += f"; ⚪ bo qua (chua co trang: {', '.join(missing)})"
    done["Roblox"] = "bo qua (chua co ban Roblox; cho so lieu 14 ngay de chon game)"
    return done


def key_lines(today):
    """Tinh trang tung khoa: co/thieu va ngay het han ghi trong specs/expiry.json. -> (cac dong, cac canh bao sap het han)."""
    lines, warn = [], []
    for name, expires in json.loads((ROOT / "specs" / "expiry.json").read_text(encoding="utf-8")).items():
        have = "co" if notify.env(name) else "THIEU"
        if expires:
            left = (date.fromisoformat(expires) - today).days
            if left < 14:
                warn.append(f"{name} con {left} ngay")
        lines.append(f"| {name} | {have} | {expires or 'khong co han'} |")
    return lines, warn


def main():
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    publish, weekly = "--no-publish" not in sys.argv, "--weekly" in sys.argv
    now = datetime.now(VN)
    steps = [("kiem man", step_verify), ("bo sung hang du tru", step_fill), ("build", build.build), ("kiem ban web", step_test)]
    if publish:
        steps.append(("dang", step_publish))
    failed, detail, published = None, "", {}
    for name, func in steps:
        try:
            result = func()
            if name == "dang":
                published = result
        except Exception as e:  # chay khong nguoi trong: ghi lai roi bao, khong de chet im lang
            failed, detail = name, f"{type(e).__name__}: {str(e)[:300]}"
            break

    row = {"date": now.date().isoformat(), "ok": not failed, "levels": len(carjam.load(carjam.LEVELS)),
           "queue": len(carjam.load(carjam.QUEUE)), "games_tested": 0 if failed else len(build.GAMES)}
    history = [r for r in (json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []) if r["date"] != row["date"]]
    history = (history + [row])[-120:]
    HISTORY.parent.mkdir(exist_ok=True)
    HISTORY.write_text("[\n" + ",\n".join(json.dumps(r) for r in history) + "\n]\n", encoding="utf-8", newline="\n")

    keys, warn = key_lines(now.date())
    status = [
        "# Trạng thái game-factory", "",
        f"- Lần chạy cuối: {now:%Y-%m-%d %H:%M} (giờ VN), {'chạy thử, không đăng' if not publish else 'chạy hằng ngày'}",
        f"- Kết quả: {'🔴 HỎNG ở bước ' + failed + ': ' + detail if failed else '✅ đạt'}",
        f"- Car Jam Escape: {row['levels']} màn trong game, {row['queue']} màn dự trữ đã kiểm (cần ≥ {carjam.QUEUE_MIN})",
        f"- Boba Sort: {len(bobasort.load(bobasort.LEVELS))} màn trong game, {len(bobasort.load(bobasort.QUEUE))} màn dự trữ đã kiểm (cần ≥ {bobasort.QUEUE_MIN})",
        f"- Tile Trio: {len(tiletrio.load(tiletrio.LEVELS))} màn trong game, {len(tiletrio.load(tiletrio.QUEUE))} màn dự trữ đã kiểm (cần ≥ {tiletrio.QUEUE_MIN})",
        f"- Kiểm bản web cỡ điện thoại: {row['games_tested']}/{len(build.GAMES)} game đạt",
        "- Đăng: " + ("; ".join(f"{k}: {v}" for k, v in published.items()) or "không đăng lần này"),
        "- Lượt chơi, thời gian chơi, doanh thu: chưa có, chưa game nào lên sóng", "",
        "| Khóa | Có | Hết hạn |", "|---|---|---|", *keys, "",
    ]
    (ROOT / "TRANG-THAI.md").write_text("\n".join(status), encoding="utf-8", newline="\n")

    if failed:
        notify.discord(f"🔴 game-factory hỏng ở bước '{failed}': {detail[:250]} | Sửa: {FIX[failed]}", alert=True)
        notify.ping(failed=True)
    else:
        notify.discord(f"✅ game-factory {now:%d/%m}: {row['games_tested']} game qua kiểm thử, Car Jam {row['levels']} màn + {row['queue']} dự trữ"
                       + (f" | ⚠️ khóa sắp hết hạn: {', '.join(warn)}" if warn else ""))
        notify.ping()
    if weekly:
        old = next((r for r in reversed(history) if r["date"] <= (now.date() - timedelta(days=7)).isoformat()), None)
        runs = [r for r in history if r["date"] > (now.date() - timedelta(days=7)).isoformat()]
        notify.discord(
            f"📊 game-factory tuần đến {now:%d/%m}: {sum(r['ok'] for r in runs)}/{len(runs)} lần chạy đạt; "
            f"màn dự trữ {row['queue']}" + (f" (tuần trước {old['queue']})" if old else " (chưa có số tuần trước)")
            + "; lượt chơi và doanh thu: chưa có vì chưa game nào được duyệt. "
            "Đề xuất: xem THEO-DOI.md, việc gần tiền nhất là đưa một game qua vòng duyệt.")
    print(status[3])
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
