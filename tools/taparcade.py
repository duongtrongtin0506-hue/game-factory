# -*- coding: utf-8 -*-
"""Tap Arcade: kiem cac chang Journey trong levels/tap-arcade.json:  python tools/taparcade.py verify
Chang viet thanh chuoi '<tro>:<diem 1 sao>,<diem 2 sao>,<diem 3 sao>', vi du 'balloon:8,13,19'. Choi mot luot tro do, dat moc diem nao duoc sao do.
Day la tro phan xa, khong co loi giai de bo giai tim; chi kiem duoc: tro co that, ba moc diem tang dan, cung mot tro thi chang sau khong de hon chang truoc,
so chang chia het cho 15 (moi trang chon chang co 15 o), va 9 chang dau dung thu tu 9 tro (qua chang i la mo tro i o muc Arcade)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ROOT / "levels" / "tap-arcade.json"
GAMES = ["balloon", "mole", "number", "stroop", "memory", "math", "odd", "simon", "catch"]   # dung thu tu mang GAMES trong game


def load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def parse(board):
    """-> (tro, [3 moc diem]). None neu chang khong hop le."""
    game, _, rest = board.partition(":")
    goals = rest.split(",")
    if game not in GAMES or len(goals) != 3 or not all(g.isdigit() for g in goals):
        return None
    goals = [int(g) for g in goals]
    return (game, goals) if 0 < goals[0] < goals[1] < goals[2] else None


def verify():
    bad, last = [], {}
    rows = load(LEVELS)
    for i, row in enumerate(rows, 1):
        got = parse(row["board"])
        if not got:
            bad.append(f"{LEVELS.name} chang {i}: sai dinh dang hoac moc diem khong tang dan")
            continue
        game, goals = got
        if i <= len(GAMES) and game != GAMES[i - 1]:
            bad.append(f"{LEVELS.name} chang {i}: 9 chang dau phai theo thu tu 9 tro")
        if goals[0] < last.get(game, 0):
            bad.append(f"{LEVELS.name} chang {i}: de hon chang truoc cua tro {game}")
        last[game] = goals[0]
    if not rows or len(rows) % 15:
        bad.append(f"{LEVELS.name}: so chang phai chia het cho 15")
    return bad


if __name__ == "__main__":
    problems = verify()
    print("\n".join(problems) or f"dat: {len(load(LEVELS))} chang")
    sys.exit(1 if problems else 0)
