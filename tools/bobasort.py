# -*- coding: utf-8 -*-
"""Boba Sort: bo giai, bo sinh man va hang du tru man.
  python tools/bobasort.py verify        giai lai moi man trong levels/ va content-queue/, sai so buoc hoac khong giai duoc -> thoat 1
  python tools/bobasort.py fill [giay]   sinh man moi, chi giu man bo giai xac nhan giai duoc, cho den khi hang du tru du QUEUE_TARGET
  python tools/bobasort.py take N        chuyen N man tu hang du tru vao levels/boba-sort.json (N chia het cho 20: moi trang chon man co 20 o)
Man viet thanh chuoi cac coc cach nhau bang '|', moi coc doc tu day len mieng, moi chu so la 1 mau, coc trong la doan rong: '2001|0021|1221||'.
Do kho = so buoc it nhat (1 buoc = chuyen 1 vien), tim bang A* voi uoc luong khong bao gio vuot qua so buoc that nen la con so chinh xac.
Game con co bo giai rieng (duyet theo chieu sau, gioi han GAME_BUDGET nut) de goi y va tinh sao; game_moves() la ban chep y het bo giai do,
man nao no khong giai noi thi khong duoc vao game."""
import heapq
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ROOT / "levels" / "boba-sort.json"
QUEUE = ROOT / "content-queue" / "boba-sort.json"
CAP, SPARE, MAX_COLOURS = 4, 2, 8   # 4 vien moi coc, 2 coc trong, game co 8 mau
QUEUE_MIN, QUEUE_TARGET = 30, 40
NEW_COLOURS = (7, 8)                # man moi noi tiep man 100 nen dung so mau cua chang cuoi
PER_MOVES = 6                       # moi muc do kho giu toi da 6 man de hang du tru du muc
STATE_CAP = 400000
GAME_BUDGET = 40000


def load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def save(path, rows):
    path.parent.mkdir(exist_ok=True)
    path.write_text("[\n" + ",\n".join(json.dumps(r) for r in rows) + "\n]\n", encoding="utf-8", newline="\n")


def parse(board):
    """-> danh sach coc (chuoi chu so, day truoc). None neu man khong hop le."""
    tubes = board.split("|")
    balls = "".join(tubes)
    n = len(tubes) - SPARE
    if not balls.isdigit() or not 2 <= n <= MAX_COLOURS or any(len(t) > CAP for t in tubes):
        return None
    if any(balls.count(str(c)) != CAP for c in range(n)) or len(balls) != n * CAP:
        return None
    if any(len(t) == CAP and len(set(t)) == 1 for t in tubes):   # khong coc nao xong san
        return None
    return tubes


def must_move(tubes):
    """So vien chac chan phai chuyen it nhat 1 lan: vien nam tren mau khac, va cac cum day cung mau nam o coc khong phai coc dich."""
    need, runs = 0, {}
    for t in tubes:
        if t:
            base = len(t) - len(t.lstrip(t[0]))
            need += len(t) - base
            runs.setdefault(t[0], []).append(base)
    return need + sum(sum(r) - max(r) for r in runs.values())


def moves_from(tubes):
    """Cac nuoc di dang xet: bo nuoc do vien cua coc mot mau sang coc trong, va chi thu 1 coc trong (cac coc trong nhu nhau)."""
    for a, src in enumerate(tubes):
        if not src:
            continue
        top, plain = src[-1], len(set(src)) == 1
        if plain and len(src) == CAP:
            continue
        used_empty = False
        for b, dst in enumerate(tubes):
            if a == b or len(dst) >= CAP:
                continue
            if dst:
                if dst[-1] == top:
                    yield a, b, 0
            elif not used_empty and not plain:
                used_empty = True
                yield a, b, 1


def solve(board):
    """-> (so buoc it nhat, so trang thai da duyet), hoac None neu khong giai duoc / man sai / vuot STATE_CAP."""
    tubes = parse(board)
    if not tubes:
        return None
    start = tuple(sorted(tubes))
    best = {start: 0}
    heap = [(must_move(start), 0, start)]
    while heap:
        f, neg, state = heapq.heappop(heap)
        g = -neg
        if best[state] < g:
            continue
        if f == g:
            return g, len(best)
        for a, b, _ in moves_from(state):
            nxt = list(state)
            nxt[b] += nxt[a][-1]
            nxt[a] = nxt[a][:-1]
            nxt = tuple(sorted(nxt))
            if best.get(nxt, 1 << 30) > g + 1:
                best[nxt] = g + 1
                heapq.heappush(heap, (g + 1 + must_move(nxt), -g - 1, nxt))
        if len(best) > STATE_CAP:
            return None
    return None


def game_moves(board, budget=GAME_BUDGET):
    """Ban chep bo giai trong game (web/boba-sort/index.src.html, ham solve). -> so buoc loi giai cua no, hoac None neu het budget."""
    t = [list(x) for x in board.split("|")]
    seen, path, nodes = set(), [], 0

    def done():
        return all(not x or (len(x) == CAP and len(set(x)) == 1) for x in t)

    def dfs():
        nonlocal nodes
        if done():
            return True
        nodes += 1
        if nodes > budget:
            return False
        key = "|".join(sorted(",".join(x) for x in t))
        if key in seen:
            return False
        seen.add(key)
        for a, b, _ in sorted(moves_from(["".join(x) for x in t]), key=lambda m: m[2]):
            t[b].append(t[a].pop())
            path.append((a, b))
            if dfs():
                return True
            path.pop()
            t[a].append(t[b].pop())
            if nodes > budget:
                return False
        return False

    limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(limit, budget + 1000))
    try:
        return len(path) if dfs() else None
    finally:
        sys.setrecursionlimit(limit)


def random_board(rnd):
    n = rnd.choice(NEW_COLOURS)
    balls = [str(c) for c in range(n) for _ in range(CAP)]
    rnd.shuffle(balls)
    return "|".join(["".join(balls[i * CAP:i * CAP + CAP]) for i in range(n)] + [""] * SPARE)


def verify():
    bad = []
    for path in (LEVELS, QUEUE):
        rows = load(path)
        for i, row in enumerate(rows, 1):
            got = solve(row["board"])
            if not got or got[0] != row["moves"]:
                bad.append(f"{path.name} man {i}: ghi {row['moves']} buoc, bo giai ra {got[0] if got else 'KHONG GIAI DUOC'}")
            elif game_moves(row["board"]) is None:
                bad.append(f"{path.name} man {i}: bo giai trong game khong giai noi")
        boards = [r["board"] for r in rows]
        if len(set(boards)) != len(boards):
            bad.append(f"{path.name}: co man trung nhau")
    if len(load(LEVELS)) % 20:
        bad.append(f"{LEVELS.name}: so man phai chia het cho 20")
    if set(r["board"] for r in load(LEVELS)) & set(r["board"] for r in load(QUEUE)):
        bad.append("hang du tru co man da nam trong game")
    return bad


def fill(seconds=60, rnd=None):
    """Sinh man cho den khi hang du tru du QUEUE_TARGET hoac het gio. -> (so man them, so man da thu)."""
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
        if board in known or not parse(board):
            continue
        known.add(board)
        got = solve(board)
        if not got or per.get(got[0], 0) >= PER_MOVES or game_moves(board) is None:
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
    if count % 20 or len(queue) - count < 0:
        sys.exit(f"Can so man chia het cho 20 va khong qua {len(queue)} man dang co trong hang du tru.")
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
        print(f"them {added} man (thu {tried} man), hang du tru: {len(load(QUEUE))}")
    elif cmd == "take":
        print(f"da chuyen {len(take(int(sys.argv[2])))} man vao game; nho build lai")
