# -*- coding: utf-8 -*-
"""Tile Trio: bo giai, bo sinh man va hang du tru man.
  python tools/tiletrio.py verify        giai lai moi man trong levels/ va content-queue/, khong giai duoc hoac sai so ghi -> thoat 1
  python tools/tiletrio.py fill [giay]   sinh man moi, chi giu man bo giai xac nhan giai duoc, cho den khi hang du tru du QUEUE_TARGET
  python tools/tiletrio.py take N        chuyen N man tu hang du tru vao levels/tile-trio.json (N chia het cho 20: moi trang chon man co 20 o)
Man viet thanh chuoi, moi quan 4 ky tu: x, y (he 36, don vi nua o), tang z, loai (he 36): '0000' + '2001' + ...
Quan a de len quan b khi a o tang cao hon va hai o vuong 2x2 chong nhau; chi quan khong bi de moi lay duoc. Khay chua 7 quan, du 3 quan cung loai thi bien mat.
Giai duoc = bo giai (duyet theo chieu sau, co nho trang thai) don sach ban ma khay khong bao gio day.
Do kho ("hard", 0-100) = ty le thua cua mot nguoi choi chi nhin truoc mat (giong botPick trong game): uu tien quan trung voi khay, roi den loai
dang lo ra nhieu nhat, khong tinh truoc. Man nao cung can so luot = so quan nen so luot khong noi len do kho."""
import json
import random
import sys
import time
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ROOT / "levels" / "tile-trio.json"
QUEUE = ROOT / "content-queue" / "tile-trio.json"
TRAY, KINDS = 7, 14
QUEUE_MIN, QUEUE_TARGET = 30, 40
NEW_SHAPES = ((6, 7, 4), (6, 7, 5), (5, 6, 5))   # (rong, cao, so tang) cua man moi: noi tiep chang cuoi cua 100 man dau
NEW_KINDS = (11, 12, 13, 14)
PER_BAND = 8                        # moi khoang 10 diem do kho giu toi da 8 man de hang du tru du muc
NODE_CAP = 200000
SIMS = 40
B36 = "0123456789abcdefghijklmnopqrstuvwxyz"


def load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def save(path, rows):
    path.parent.mkdir(exist_ok=True)
    path.write_text("[\n" + ",\n".join(json.dumps(r) for r in rows) + "\n]\n", encoding="utf-8", newline="\n")


def rng(seed):
    """Xorshift 32 bit, giong het ham rng trong game de man sinh ra o day va trong game la mot."""
    s = [(seed & 0xFFFFFFFF) or 1]

    def nxt():
        x = s[0]
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        s[0] = x
        return x / 4294967296
    return nxt


def covers(a, b):
    return a[2] > b[2] and abs(a[0] - b[0]) < 2 and abs(a[1] - b[1]) < 2


def make(seed, w, h, layers, kinds):
    """Dung man tu hat giong (ban chep ham makeLevel cu cua game): xep quan thanh thap, roi phat loai theo dung thu tu mot nguoi choi
    co the don ban (moi lan 3 quan dang lay duoc), nen man nao cung co loi giai. -> chuoi man."""
    r = rng(seed)
    holes = 0.12 + 0.18 * r()
    tiles = []
    for z in range(layers):
        lw, lh = w - z, h - z
        if lw < 1 or lh < 1:
            break
        for j in range(lh):
            for i in range(lw):
                if z > 0 and r() < holes:
                    continue
                tiles.append([i * 2 + z, j * 2 + z, z, -1])
    while len(tiles) % 3:
        free = [t for t in tiles if not any(covers(o, t) for o in tiles)]
        tiles.remove(free[int(r() * len(free))])
    left, k = set(range(len(tiles))), int(r() * kinds)
    while left:
        for _ in range(3):
            free = [i for i in sorted(left) if not any(covers(tiles[o], tiles[i]) for o in left)]
            pick = free[int(r() * len(free))]
            tiles[pick][3] = k % kinds
            left.discard(pick)
        k += 1 + int(r() * 2)
    return "".join(B36[x] + B36[y] + str(z) + B36[kind] for x, y, z, kind in tiles)


def parse(board):
    """-> danh sach (x, y, z, loai). None neu man khong hop le."""
    if not board or len(board) % 4 or any(c not in B36 for c in board):
        return None
    tiles = [(B36.index(board[i]), B36.index(board[i + 1]), B36.index(board[i + 2]), B36.index(board[i + 3])) for i in range(0, len(board), 4)]
    kinds = [t[3] for t in tiles]
    if len(tiles) % 3 or max(kinds) >= KINDS or any(kinds.count(k) % 3 for k in set(kinds)):
        return None
    if len({t[:3] for t in tiles}) != len(tiles):
        return None
    return tiles


class Board:
    """Ban dang choi: quan nao con, quan nao dang lay duoc, khay dang giu gi."""

    def __init__(self, tiles):
        n = len(tiles)
        self.kind = [t[3] for t in tiles]
        self.under = [[b for b in range(n) if covers(tiles[a], tiles[b])] for a in range(n)]
        self.blocked0 = [sum(1 for a in range(n) if covers(tiles[a], tiles[b])) for b in range(n)]
        self.reset()

    def reset(self):
        self.blocked = self.blocked0[:]
        self.free = [i for i, b in enumerate(self.blocked) if not b]
        self.cnt = [0] * KINDS
        self.held = 0
        self.left = len(self.kind)
        self.mask = 0

    def pick(self, i):
        """Lay quan i (dang lay duoc). -> cac quan vua duoc mo ra, de hoan tac."""
        self.free.remove(i)
        opened = []
        for b in self.under[i]:
            self.blocked[b] -= 1
            if not self.blocked[b]:
                opened.append(b)
        self.free += opened
        k = self.kind[i]
        self.cnt[k] = (self.cnt[k] + 1) % 3
        self.held += 1 if self.cnt[k] else -2
        self.left -= 1
        self.mask |= 1 << i
        return opened

    def unpick(self, i, opened):
        for b in opened:
            self.free.remove(b)
        for b in self.under[i]:
            self.blocked[b] += 1
        self.free.append(i)
        k = self.kind[i]
        self.held -= 1 if self.cnt[k] else -2
        self.cnt[k] = (self.cnt[k] + 2) % 3
        self.left += 1
        self.mask &= ~(1 << i)


def solve(board, budget=NODE_CAP):
    """-> so trang thai da duyet neu don sach duoc ban, None neu khong giai duoc / man sai / vuot budget."""
    tiles = parse(board)
    if not tiles:
        return None
    b, seen, nodes = Board(tiles), set(), 0

    def dfs():
        nonlocal nodes
        if not b.left:
            return True
        nodes += 1
        if nodes > budget:
            return False
        # quan lam du bo ba thi lay ngay: khay nhe di, ban chi mo them, khong bao gio thiet
        todo = [i for i in b.free if b.cnt[b.kind[i]] == 2][:1]
        if not todo:
            if b.held >= TRAY - 1:
                return False
            key = (b.mask, tuple(b.cnt))
            if key in seen:
                return False
            seen.add(key)
            same = [0] * KINDS
            for i in b.free:
                same[b.kind[i]] += 1
            todo = sorted(b.free, key=lambda i: -(b.cnt[b.kind[i]] * 10 + same[b.kind[i]]))
        for i in todo:
            opened = b.pick(i)
            if dfs():
                return True
            b.unpick(i, opened)
            if nodes > budget:
                return False
        return False

    return nodes if dfs() else None


def hardness(board, sims=SIMS):
    """Ty le thua (0-100) cua nguoi choi chi nhin truoc mat qua sims van; hat giong lay tu chinh man nen chay lai ra dung con so cu."""
    b, r, lost = Board(parse(board)), rng(zlib.crc32(board.encode("ascii"))), 0
    for _ in range(sims):
        b.reset()
        while b.left and b.held < TRAY:
            same = [0] * KINDS
            for i in b.free:
                same[b.kind[i]] += 1
            score = [b.cnt[b.kind[i]] * 10 + same[b.kind[i]] for i in b.free]
            best = max(score)
            pool = [i for i, s in zip(b.free, score) if s == best]
            b.pick(pool[int(r() * len(pool))])
        lost += b.left > 0 or b.held >= TRAY
    return round(100 * lost / sims)


def random_board(rnd):
    w, h, layers = rnd.choice(NEW_SHAPES)
    return make(rnd.randrange(1, 1 << 32), w, h, layers, rnd.choice(NEW_KINDS))


def verify():
    bad = []
    for path in (LEVELS, QUEUE):
        rows = load(path)
        for i, row in enumerate(rows, 1):
            tiles = parse(row["board"])
            if not tiles or solve(row["board"]) is None:
                bad.append(f"{path.name} man {i}: KHONG GIAI DUOC")
            elif row["tiles"] != len(tiles) or row["hard"] != hardness(row["board"]):
                bad.append(f"{path.name} man {i}: so quan hoac do kho ghi sai")
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
        per[r["hard"] // 10] = per.get(r["hard"] // 10, 0) + 1
    added = tried = 0
    deadline = time.time() + seconds
    while len(queue) < QUEUE_TARGET and time.time() < deadline:
        board = random_board(rnd)
        tried += 1
        if board in known or solve(board) is None:
            continue
        known.add(board)
        hard = hardness(board)
        if per.get(hard // 10, 0) >= PER_BAND:
            continue
        per[hard // 10] = per.get(hard // 10, 0) + 1
        queue.append({"board": board, "tiles": len(board) // 4, "hard": hard})
        added += 1
    queue.sort(key=lambda r: (r["hard"], r["tiles"]))
    save(QUEUE, queue)
    return added, tried


def paced(rows):
    """Xep do kho tang dan, cu 4 man kho dan thi chen 1 man de de nguoi choi nghi."""
    rows = sorted(rows, key=lambda r: (r["hard"], r["tiles"]))
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
