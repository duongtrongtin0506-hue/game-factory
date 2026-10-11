# -*- coding: utf-8 -*-
"""One Line Fill: bo giai, bo sinh man va hang du tru man.
  python tools/oneline.py verify        giai lai moi man trong levels/ va content-queue/, khong giai duoc hoac sai so ghi -> thoat 1
  python tools/oneline.py fill [giay]   sinh man moi, chi giu man bo giai xac nhan giai duoc, cho den khi hang du tru du QUEUE_TARGET
  python tools/oneline.py take N        chuyen N man tu hang du tru vao levels/one-line.json (N chia het cho 20: moi trang chon man co 20 o)
Man viet thanh chuoi: rong, cao, cot va hang cua o xuat phat (moi thu 1 chu so), roi duong di mau bang cac chu R L D U: '3300RDDLU...'.
Cac o duong di mau di qua chinh la ban choi; nguoi choi phai ve mot net tu o xuat phat qua het moi o. Duong di mau la loi giai game dung de goi y.
Giai duoc = bo giai (duyet theo chieu sau, khong nhin duong di mau) tu tim ra mot net di het ban.
Do kho ("hard", 0-100) = ty le thua cua nguoi choi chi nhin truoc mat: di tiep sang o con it loi ra nhat, bang nhau thi chon dai, khong quay lui."""
import json
import random
import sys
import time
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ROOT / "levels" / "one-line.json"
QUEUE = ROOT / "content-queue" / "one-line.json"
QUEUE_MIN, QUEUE_TARGET = 30, 40
NEW_W, NEW_H, NEW_LEN = 6, 7, (30, 41)   # man moi noi tiep chang cuoi cua 100 man dau: ban 6x7, net dai 30-41 o
PER_BAND = 8                              # moi khoang 10 diem do kho giu toi da 8 man de hang du tru du muc
NODE_CAP = 200000
SIMS = 200
DIRS = {"R": (1, 0), "L": (-1, 0), "D": (0, 1), "U": (0, -1)}
STEP = ((1, 0), (-1, 0), (0, 1), (0, -1))


def load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def save(path, rows):
    path.parent.mkdir(exist_ok=True)
    path.write_text("[\n" + ",\n".join(json.dumps(r) for r in rows) + "\n]\n", encoding="utf-8", newline="\n")


def rng(seed):
    """Xorshift 32 bit, giong het ham rng trong game."""
    s = [(seed & 0xFFFFFFFF) or 1]

    def nxt():
        x = s[0]
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        s[0] = x
        return x / 4294967296
    return nxt


def walk(seed, w, h, length):
    """Mot lan di ngau nhien khong cat chinh minh (ban chep vong trong cua ham makeLevel cu). -> chuoi man, None neu ket truoc khi du dai."""
    r = rng(seed)
    c, q = int(r() * w), int(r() * h)
    used, path = {(c, q)}, [(c, q)]

    def is_open(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in used

    def exits(x, y):
        return sum(is_open(x + dx, y + dy) for dx, dy in STEP)

    while len(path) < length:
        opts = [d for d in STEP if is_open(c + d[0], q + d[1])]
        if not opts:
            return None
        opts.sort(key=lambda d: exits(c + d[0], q + d[1]))   # phan lon di sat cac o it loi ra de hinh gon, doi khi di lang thang
        d = opts[0] if r() < 0.7 else opts[int(r() * len(opts))]
        c, q = c + d[0], q + d[1]
        used.add((c, q))
        path.append((c, q))
    letter = {v: k for k, v in DIRS.items()}
    return f"{w}{h}{path[0][0]}{path[0][1]}" + "".join(letter[(b[0] - a[0], b[1] - a[1])] for a, b in zip(path, path[1:]))


def parse(board):
    """-> (rong, cao, duong di mau). None neu man khong hop le (ra ngoai ban, di lai o cu, ky tu la)."""
    if len(board) < 6 or not board[:4].isdigit() or any(ch not in DIRS for ch in board[4:]):
        return None
    w, h, x, y = (int(ch) for ch in board[:4])
    path = [(x, y)]
    for ch in board[4:]:
        x, y = x + DIRS[ch][0], y + DIRS[ch][1]
        path.append((x, y))
    if any(not (0 <= px < w and 0 <= py < h) for px, py in path) or len(set(path)) != len(path):
        return None
    return w, h, path


def shape(board):
    """Hinh ban + o xuat phat, khong tinh duong di mau va vi tri tren luoi: hai man cung shape la mot cau do."""
    _, _, path = parse(board)
    mx, my = min(p[0] for p in path), min(p[1] for p in path)
    return (path[0][0] - mx, path[0][1] - my), frozenset((x - mx, y - my) for x, y in path)


def solve(board, budget=NODE_CAP):
    """-> so nut da duyet neu tim ra mot net di het ban tu o xuat phat, None neu khong co / man sai / vuot budget."""
    got = parse(board)
    if not got:
        return None
    cells, start = set(got[2]), got[2][0]
    left = cells - {start}
    nodes = 0

    def around(x, y):
        return [(x + dx, y + dy) for dx, dy in STEP if (x + dx, y + dy) in left]

    def dfs(x, y):
        nonlocal nodes
        if not left:
            return True
        nodes += 1
        if nodes > budget:
            return False
        ends = 0   # o chi con 1 duong vao phai la o cuoi cung: co 2 o nhu vay, hoac 1 o khong con duong vao, thi nhanh nay hong
        for cx, cy in left:
            ways = len(around(cx, cy)) + (abs(cx - x) + abs(cy - y) == 1)
            if ways == 0 or (ways == 1 and (ends := ends + 1) > 1):
                return False
        for nx, ny in sorted(around(x, y), key=lambda p: len(around(*p))):
            left.discard((nx, ny))
            if dfs(nx, ny):
                return True
            left.add((nx, ny))
            if nodes > budget:
                return False
        return False

    return nodes if dfs(*start) else None


def hardness(board, sims=SIMS):
    """Ty le thua (0-100) cua nguoi choi chi nhin truoc mat qua sims van; hat giong lay tu chuoi man nen chay lai ra dung con so cu."""
    _, _, path = parse(board)
    cells, r, lost = set(path), rng(zlib.crc32(board.encode("ascii"))), 0
    for _ in range(sims):
        left = cells - {path[0]}
        x, y = path[0]
        while left:
            opts = [(x + dx, y + dy) for dx, dy in STEP if (x + dx, y + dy) in left]
            if not opts:
                break
            ways = [sum((ox + dx, oy + dy) in left for dx, dy in STEP) for ox, oy in opts]
            pool = [o for o, n in zip(opts, ways) if n == min(ways)]
            x, y = pool[int(r() * len(pool))]
            left.discard((x, y))
        lost += bool(left)
    return round(100 * lost / sims)


def row_for(board):
    return {"board": board, "cells": len(board) - 3, "hard": hardness(board)}


def random_board(rnd):
    return walk(rnd.randrange(1, 1 << 32), NEW_W, NEW_H, rnd.randint(*NEW_LEN))


def verify():
    bad = []
    for path in (LEVELS, QUEUE):
        rows = load(path)
        for i, row in enumerate(rows, 1):
            if not parse(row["board"]) or solve(row["board"]) is None:
                bad.append(f"{path.name} man {i}: KHONG GIAI DUOC")
            elif row != row_for(row["board"]):
                bad.append(f"{path.name} man {i}: so o hoac do kho ghi sai")
    shapes = [shape(r["board"]) for r in load(LEVELS) + load(QUEUE) if parse(r["board"])]
    if len(set(shapes)) != len(shapes):
        bad.append("co man trung nhau (cung hinh ban va o xuat phat)")
    if len(load(LEVELS)) % 20:
        bad.append(f"{LEVELS.name}: so man phai chia het cho 20")
    return bad


def fill(seconds=60, rnd=None):
    """Sinh man cho den khi hang du tru du QUEUE_TARGET hoac het gio. -> (so man them, so man da thu)."""
    rnd = rnd or random.Random()
    queue = load(QUEUE)
    known = {shape(r["board"]) for r in load(LEVELS) + queue}
    per = {}
    for r in queue:
        per[r["hard"] // 10] = per.get(r["hard"] // 10, 0) + 1
    added = tried = 0
    deadline = time.time() + seconds
    while len(queue) < QUEUE_TARGET and time.time() < deadline:
        board = random_board(rnd)
        tried += 1
        if not board or shape(board) in known or solve(board) is None:
            continue
        known.add(shape(board))
        row = row_for(board)
        if per.get(row["hard"] // 10, 0) >= PER_BAND:
            continue
        per[row["hard"] // 10] = per.get(row["hard"] // 10, 0) + 1
        queue.append(row)
        added += 1
    queue.sort(key=lambda r: (r["hard"], r["cells"]))
    save(QUEUE, queue)
    return added, tried


def paced(rows):
    """Xep do kho tang dan, cu 4 man kho dan thi chen 1 man de de nguoi choi nghi."""
    rows = sorted(rows, key=lambda r: (r["hard"], r["cells"]))
    easy, hard, out = rows[:len(rows) // 5], rows[len(rows) // 5:], []
    for i, r in enumerate(hard, 1):
        out.append(r)
        if i % 4 == 0 and easy:
            out.append(easy.pop(0))
    return out + easy


def take(count):
    queue = load(QUEUE)
    if count % 20 or len(queue) - count < 0:
        sys.exit(f"Can so man chia het cho 20 va khong qua {len(queue)} man dang co trong hang du tru.")
    step = len(queue) / count   # lay rai deu theo do kho de phan con lai van du muc
    picked = [queue[int(i * step)] for i in range(count)]
    save(QUEUE, [r for r in queue if r not in picked])
    save(LEVELS, load(LEVELS) + paced(picked))
    return picked


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if cmd == "verify":
        problems = verify()
        print("\n".join(problems) or f"dat: {len(load(LEVELS))} man trong game, {len(load(QUEUE))} man du tru")
        sys.exit(1 if problems else 0)
    elif cmd == "fill":
        added, tried = fill(float(sys.argv[2]) if len(sys.argv) > 2 else 60)
        print(f"them {added} man (thu {tried} man), hang du tru: {len(load(QUEUE))}")
    elif cmd == "take":
        print(f"da chuyen {len(take(int(sys.argv[2])))} man vao game; nho build lai")
