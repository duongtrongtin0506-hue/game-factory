# -*- coding: utf-8 -*-
"""Car Jam Escape: bo giai, bo sinh man va hang du tru man.
  python tools/carjam.py verify        giai lai moi man trong levels/ va content-queue/, sai so buoc hoac khong giai duoc -> thoat 1
  python tools/carjam.py fill [giay]   sinh man moi, chi giu man bo giai xac nhan giai duoc, cho den khi hang du tru du QUEUE_TARGET
  python tools/carjam.py take N        chuyen N man tu hang du tru vao levels/car-jam.json (ban cap nhat thang)
Ban co 6x6 viet thanh 36 ky tu theo hang: '.' la o trong, moi chu cai la 1 xe, 'A' la xe do phai ra o hang EXIT_ROW.
Do kho = so buoc it nhat (1 buoc = keo 1 xe di bao nhieu o cung duoc), tim bang duyet theo chieu rong nen la con so chinh xac."""
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ROOT / "levels" / "car-jam.json"
QUEUE = ROOT / "content-queue" / "car-jam.json"
N, EXIT_ROW = 6, 2
QUEUE_MIN, QUEUE_TARGET = 30, 40
MIN_MOVES, PER_MOVES = 8, 6   # man moi phai can it nhat 8 buoc; moi muc do kho giu toi da 6 man de hang du tru khong toan man de
STATE_CAP = 60000


def load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def save(path, rows):
    path.parent.mkdir(exist_ok=True)
    path.write_text("[\n" + ",\n".join(json.dumps(r) for r in rows) + "\n]\n", encoding="utf-8", newline="\n")


def parse(board):
    """-> danh sach xe (hang, cot, dai, nam ngang), xe 'A' dung dau. None neu ban co khong hop le."""
    if len(board) != N * N:
        return None
    cells = {}
    for i, ch in enumerate(board):
        if ch != ".":
            cells.setdefault(ch, []).append(divmod(i, N))
    cars = []
    for ch in sorted(cells):
        c = cells[ch]
        horiz, vert = len({r for r, _ in c}) == 1, len({k for _, k in c}) == 1
        line = [k for _, k in c] if horiz else [r for r, _ in c]
        if len(c) not in (2, 3) or not (horiz or vert) or line != list(range(line[0], line[0] + len(c))):
            return None
        cars.append((c[0][0], c[0][1], len(c), horiz))
    if "A" not in cells or sorted(cells) != [chr(65 + i) for i in range(len(cars))]:
        return None
    if not cars[0][3] or cars[0][0] != EXIT_ROW or any(h and r == EXIT_ROW for r, _, _, h in cars[1:]):
        return None
    return cars


def solve(board):
    """-> (so buoc it nhat, so trang thai da duyet), hoac None neu khong giai duoc / ban co sai."""
    cars = parse(board)
    if not cars:
        return None
    fixed = [r if h else c for r, c, _, h in cars]
    start = tuple(c if h else r for r, c, _, h in cars)
    seen, frontier, depth = {start}, [start], 0
    while frontier:
        nxt = []
        for pos in frontier:
            if pos[0] + cars[0][2] == N:
                return depth, len(seen)
            occ = set()
            for i, (_, _, ln, h) in enumerate(cars):
                for k in range(ln):
                    occ.add(fixed[i] * N + pos[i] + k if h else (pos[i] + k) * N + fixed[i])
            for i, (_, _, ln, h) in enumerate(cars):
                for d in (-1, 1):
                    p = pos[i] + d
                    while 0 <= p and p + ln <= N:
                        cell = p if d < 0 else p + ln - 1
                        if (fixed[i] * N + cell if h else cell * N + fixed[i]) in occ:
                            break
                        new = pos[:i] + (p,) + pos[i + 1:]
                        if new not in seen:
                            seen.add(new)
                            nxt.append(new)
                        p += d
        frontier, depth = nxt, depth + 1
        if len(seen) > STATE_CAP:
            return None
    return None


def random_board(rnd):
    grid, count = ["."] * (N * N), 0

    def place(row, col, ln, horiz):
        nonlocal count
        cells = [(row, col + k) if horiz else (row + k, col) for k in range(ln)]
        if any(r >= N or c >= N or grid[r * N + c] != "." for r, c in cells):
            return
        for r, c in cells:
            grid[r * N + c] = chr(65 + count)
        count += 1

    place(EXIT_ROW, rnd.randrange(3), 2, True)
    want = 6 + rnd.randrange(8)
    for _ in range(200):
        if count >= want:
            break
        horiz, ln, row, col = rnd.random() < 0.5, 2 if rnd.random() < 0.72 else 3, rnd.randrange(N), rnd.randrange(N)
        if not (horiz and row == EXIT_ROW):
            place(row, col, ln, horiz)
    return "".join(grid)


def verify():
    bad = []
    for path in (LEVELS, QUEUE):
        rows = load(path)
        for i, row in enumerate(rows, 1):
            got = solve(row["board"])
            if not got or got[0] != row["moves"]:
                bad.append(f"{path.name} man {i}: ghi {row['moves']} buoc, bo giai ra {got[0] if got else 'KHONG GIAI DUOC'}")
        boards = [r["board"] for r in rows]
        if len(set(boards)) != len(boards):
            bad.append(f"{path.name}: co man trung nhau")
    if set(r["board"] for r in load(LEVELS)) & set(r["board"] for r in load(QUEUE)):
        bad.append("hang du tru co man da nam trong game")
    return bad


def fill(seconds=60, rnd=None):
    """Sinh man cho den khi hang du tru du QUEUE_TARGET hoac het gio. -> (so man them, so ban co da thu)."""
    rnd = rnd or random.Random()
    queue = load(QUEUE)
    known = {r["board"] for r in load(LEVELS)} | {r["board"] for r in queue}
    per = {}
    for r in queue:
        per[r["moves"]] = per.get(r["moves"], 0) + 1
    added = tried = 0
    deadline = time.time() + seconds
    while len(queue) < QUEUE_TARGET and time.time() < deadline:
        board = random_board(rnd)
        tried += 1
        if board in known:
            continue
        known.add(board)
        got = solve(board)
        if not got or got[0] < MIN_MOVES or per.get(got[0], 0) >= PER_MOVES:
            continue
        per[got[0]] = per.get(got[0], 0) + 1
        queue.append({"board": board, "moves": got[0], "states": got[1]})
        added += 1
    queue.sort(key=lambda r: (r["moves"], r["states"]))
    save(QUEUE, queue)
    return added, tried


def paced(rows):
    """Xep do kho tang dan, cu 4 man kho dan thi chen 1 man de de nguoi choi nghi."""
    rows = sorted(rows, key=lambda r: (r["moves"], r.get("states", 0)))
    easy, hard, out = rows[:len(rows) // 5], rows[len(rows) // 5:], []
    for i, r in enumerate(hard, 1):
        out.append(r)
        if i % 4 == 0 and easy:
            out.append(easy.pop(0))
    return out + easy


def take(count):
    queue = load(QUEUE)
    if len(queue) - count < 0:
        sys.exit(f"Hang du tru chi con {len(queue)} man.")
    step = len(queue) / count   # lay rai deu theo do kho de phan con lai van du muc
    picked = [queue[int(i * step)] for i in range(count)]
    save(QUEUE, [r for r in queue if r not in picked])
    save(LEVELS, load(LEVELS) + [{"board": r["board"], "moves": r["moves"]} for r in paced(picked)])
    return picked


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if cmd == "verify":
        problems = verify()
        print("\n".join(problems) or f"dat: {len(load(LEVELS))} man trong game, {len(load(QUEUE))} man du tru")
        sys.exit(1 if problems else 0)
    elif cmd == "fill":
        added, tried = fill(float(sys.argv[2]) if len(sys.argv) > 2 else 60)
        print(f"them {added} man (thu {tried} ban co), hang du tru: {len(load(QUEUE))}")
    elif cmd == "take":
        print(f"da chuyen {len(take(int(sys.argv[2])))} man vao game; nho them canh cho the gioi moi roi build lai")
