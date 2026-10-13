# -*- coding: utf-8 -*-
"""Lan chay hang ngay (GitHub Actions daily.yml, hoac chay tay): python tools/run_daily.py [--no-publish] [--weekly]
  1. kiem lai moi man bang bo giai   1b. thu hai: chuyen 20 man tu hang du tru vao game (TAKE_GAMES)   2. bo sung hang du tru man
  3. build   4. kiem lop quang cao + ban web tren dien thoai va may tinh
  5. dang len cac nen tang co khoa (thieu khoa thi bo qua nen tang do)   6. ghi TRANG-THAI.md + metrics/history.json
  7. Discord 1 dong + diem danh healthchecks
Buoc nao hong thi dung, KHONG dang, man vua chuyen duoc tra ve hang du tru, bao Discord @here kem cach sua. --weekly gui them bao cao tuan (chu nhat)."""
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import bobasort
import build
import carjam
import notify
import oneline
import taparcade
import tiletrio

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / "metrics" / "history.json"
VN = timezone(timedelta(hours=7))
# Game tu them man: man hinh chon man cua 3 game nay tu dai theo so man. Car Jam chua vao: man 101+ can canh the gioi thu 6.
TAKE_GAMES = (("Car Jam Escape", carjam), ("Boba Sort", bobasort), ("Tile Trio", tiletrio), ("One Line Fill", oneline))
LOG_MARK = "## Nhật ký lượt"   # tu dong nay tro xuong trong TRANG-THAI.md la cua routine, run_daily khong ghi de
TAKE_COUNT, TAKE_WEEKDAY = 20, 0   # 20 man = 1 trang chon man; 0 = thu hai
FIX = {
    "them man": "chay python tools/<game>.py verify; hang du tru phai con du 20 man",
    "kiem man": "chay python tools/carjam.py verify, tools/bobasort.py verify, tools/tiletrio.py verify va tools/oneline.py verify, xoa man sai khoi levels/ hoac content-queue/",
    "bo sung hang du tru": "chay python tools/carjam.py fill 300 (hoac tools/bobasort.py, tools/tiletrio.py, tools/oneline.py fill 300) tren may roi commit content-queue/",
    "build": "xem dau /*LEVELS*/ va /*ADS*/ trong web/<game>/index.src.html, dau /*PORTAL*/ va /*GAME_ID*/ trong web/ads.js",
    "kiem ban web": "chay node tools/test_ads.js va python tools/smoke_test.py tren may, sua loi duoc neu ten",
    "dang": "kiem khoa nen tang trong GitHub Secrets (con han khong), chay lai workflow",
}


def step_verify():
    problems = carjam.verify() + bobasort.verify() + tiletrio.verify() + oneline.verify() + taparcade.verify()
    if problems:
        raise RuntimeError("; ".join(problems[:3]))


def step_take(history, today):
    """Moi tuan 1 lan (thu hai, hoac lan chay dau tien sau do neu thu hai hong): chuyen TAKE_COUNT man moi game tu hang du tru vao game.
    -> (so man da chuyen, ban luu cac tep da doi de tra lai neu buoc sau hong)."""
    recent = any(r.get("took") and (today - date.fromisoformat(r["date"])).days < 7 for r in history)
    due = today.weekday() == TAKE_WEEKDAY or any(r.get("take_failed") for r in history[-6:])
    if recent or not due:
        return 0, {}
    backup, took = {}, 0
    for _, tool in TAKE_GAMES:
        if len(tool.load(tool.QUEUE)) < TAKE_COUNT:
            continue
        for path in (tool.LEVELS, tool.QUEUE):
            backup[path] = path.read_text(encoding="utf-8")
        took += len(tool.take(TAKE_COUNT))
    return took, backup


def step_fill():
    for name, tool in (("Car Jam", carjam), ("Boba Sort", bobasort), ("Tile Trio", tiletrio), ("One Line Fill", oneline)):
        if len(tool.load(tool.QUEUE)) < tool.QUEUE_TARGET:
            tool.fill(90)
        if tool is carjam:   # moi ngay doi vai man de thanh man kho, den khi nua hang du tru tu HARD_MOVES buoc
            carjam.harden(40)
        left = len(tool.load(tool.QUEUE))
        if left < tool.QUEUE_MIN:
            raise RuntimeError(f"hang du tru {name} chi con {left} man (can {tool.QUEUE_MIN})")


def step_test():
    if shutil.which("node"):   # lop quang cao chung, thu voi SDK gia cua tung cong
        ads = subprocess.run(["node", str(ROOT / "tools" / "test_ads.js")], capture_output=True, timeout=60)
        if ads.returncode:
            raise RuntimeError(ads.stdout.decode("utf-8", "replace").strip()[:400] or "tools/test_ads.js hong")
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
    done["Roblox"] = "bo qua (chua co ban Roblox; lam khi co game thang)"
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
    history = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
    took, backup = 0, {}

    def step_take_now():
        nonlocal took, backup
        took, backup = step_take(history, now.date())

    steps = [("kiem man", step_verify), ("bo sung hang du tru", step_fill), ("build", lambda: (build.build(), build.release())), ("kiem ban web", step_test)]
    if publish:
        steps.insert(1, ("them man", step_take_now))
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
    if failed and failed != "dang" and backup:   # man moi chua qua kiem thu: tra lai nhu cu, tuan nay thu lai o lan chay sau
        for path, text in backup.items():
            path.write_text(text, encoding="utf-8", newline="\n")
        build.build()
        build.release()
        took = -1

    row = {"date": now.date().isoformat(), "ok": not failed, "levels": len(carjam.load(carjam.LEVELS)),
           "queue": len(carjam.load(carjam.QUEUE)), "games_tested": 0 if failed else len(build.GAMES)}
    if took > 0 or any(r.get("took") for r in history if r["date"] == row["date"]):   # lan chay lai trong ngay khong lam mat dau da chuyen man
        row["took"] = took if took > 0 else next(r["took"] for r in history if r["date"] == row["date"] and r.get("took"))
    elif took < 0:
        row["take_failed"] = True
    history = [r for r in history if r["date"] != row["date"]]
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
        f"- One Line Fill: {len(oneline.load(oneline.LEVELS))} màn trong game, {len(oneline.load(oneline.QUEUE))} màn dự trữ đã kiểm (cần ≥ {oneline.QUEUE_MIN})",
        f"- Tap Arcade: {len(taparcade.load(taparcade.LEVELS))} chặng Journey đã kiểm (trò phản xạ, không có hàng dự trữ)",
        f"- Kiểm bản web cỡ điện thoại: {row['games_tested']}/{len(build.GAMES)} game đạt",
        "- Thêm màn tuần này: " + (f"đã chuyển {row['took']} màn từ hàng dự trữ vào game" if row.get("took") else "màn mới hỏng kiểm thử, đã trả lại" if took < 0 else "không phải hôm nay (mỗi thứ hai 20 màn mỗi game: Car Jam, Boba Sort, Tile Trio, One Line Fill)"),
        "- Đăng: " + ("; ".join(f"{k}: {v}" for k, v in published.items()) or "không đăng lần này"),
        "- Lượt chơi, thời gian chơi, doanh thu: chưa có, chưa game nào lên sóng", "",
        "| Khóa | Có | Hết hạn |", "|---|---|---|", *keys, "",
    ]
    status_path = ROOT / "TRANG-THAI.md"   # giu nguyen nhat ky luot (routine ghi moi luot 1 dong o cuoi tep)
    old_status = status_path.read_text(encoding="utf-8") if status_path.exists() else ""
    log = old_status[old_status.index(LOG_MARK):].rstrip("\n") if LOG_MARK in old_status else LOG_MARK + "\n"
    status_path.write_text("\n".join(status) + "\n" + log + "\n", encoding="utf-8", newline="\n")

    if failed:
        notify.discord(f"🔴 game-factory hỏng ở bước '{failed}': {detail[:250]} | Sửa: {FIX[failed]}", alert=True)
        notify.ping(failed=True)
    else:
        skipped = [f"{k}: {v.split('⚪ ')[1] if '⚪' in v else v}" for k, v in published.items() if "bo qua" in v and k != "Roblox"]
        todo = len(re.findall(r"^- \[ \]", (ROOT / "HUONG-DAN-CHU.md").read_text(encoding="utf-8"), re.M))
        notify.discord(f"✅ game-factory {now:%d/%m}: {row['games_tested']} game qua kiểm thử, Car Jam {row['levels']} màn + {row['queue']} dự trữ"
                       + (f" | +{took} màn mới vào game" if took > 0 else "")
                       + (f" | ⚪ {'; '.join(skipped)}" if skipped else "")
                       + (f" | 📌 chờ chủ: {todo} mục trong HUONG-DAN-CHU.md" if todo and publish else "")
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
