# Xưởng Game → play.snoutsmith.com
Tôi là xưởng Game của nhà máy Net24. MÁY làm hàng, tôi (Claude) chỉ dựng và sửa script.

## Việc của tôi
- Script: `chay.py`. Chạy: `node ../../khung/gen.js <id>; python ../../khung/build.py <id>; python ../../khung/test.py <id>; python ../../khung/giao.py` (Task Scheduler máy nhà, 01:00 mỗi đêm).
- Dây chuyền: nghiên cứu (net24-he-thong/13-Ban-hang-so/HOC-TOP/game.md) → làm → Cửa 0 (máy kiểm) → Cửa 1 (AI chấm 4 vai ≥ 80) → đóng gói → đẩy vào net24-he-thong/BAN-GIAO/YYYYMMDD-game-<ten>/ → 1 dòng Discord.
- Chuẩn ngành: net24-he-thong/13-Ban-hang-so/KHUON-NHA-MAY.md mục 4 – Game (HTML5) (CHỈ đọc mục này khi cần).
- Chỉ tiêu: ≥ 10 game gốc trước 10/11/2026 (đã có 5), sau đó +3/tuần. Công suất script: 1 biến thể/game gốc mỗi đêm (lên 3 khi qua cửa ổn 3 đêm).
- AI: dùng AI chung (POST https://coinnew24.com/wp-json/n24/v1/ai), cầu chì ≤ 40 lượt/đêm.

## Đang có
- Mã game nằm sẵn ở gốc kho (KHÔNG di chuyển): `../../khung/` (khung Drop & Merge: gen.js, build.py, test.py, giao.py), `../../web/`, `../../tools/`, `../../levels/`. Bộ nhớ cũ của dự án game: `BO-NHO-GAME.md` (chỉ đọc mục cần).

## Khi nào mở Claude (khung này)
1. Dựng script lần đầu. 2. Script lỗi 2 lần. 3. Hàng bị trả lại (đọc NGHIEM-THU.md) → sửa script/khuôn.
KHÔNG làm tay từng sản phẩm. KHÔNG đọc cả kho, cả hiến chương. Xong việc: commit + push, ghi 3 dòng (món · lịch · token) vào NHAT-KY.md, đóng phiên.

## Nhật ký
NHAT-KY.md (ngày · số món ra · qua cửa · nộp · bị trả · lỗi)
