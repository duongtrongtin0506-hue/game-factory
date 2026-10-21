# Xưởng Mẫu → templates.snoutsmith.com
Tôi là xưởng Mẫu của nhà máy Net24. MÁY làm hàng, tôi (Claude) chỉ dựng và sửa script.

## Việc của tôi
- Script: `chay.py`. Chạy: `python chay.py --so-mon 2` (Task Scheduler máy nhà, 01:00 mỗi đêm).
- Dây chuyền: nghiên cứu (net24-he-thong/13-Ban-hang-so/HOC-TOP/mau.md) → làm → Cửa 0 (máy kiểm) → Cửa 1 (AI chấm 4 vai ≥ 80) → đóng gói → đẩy vào net24-he-thong/BAN-GIAO/YYYYMMDD-mau-<ten>/ → 1 dòng Discord.
- Chuẩn ngành: net24-he-thong/13-Ban-hang-so/KHUON-NHA-MAY.md mục 4 – Mẫu (CHỈ đọc mục này khi cần).
- Chỉ tiêu: ≥ 8 trước 10/11/2026, sau đó +3/tuần. Công suất script: 2 mẫu/đêm (lên 4 khi qua cửa ổn 3 đêm).
- AI: dùng AI chung (POST https://coinnew24.com/wp-json/n24/v1/ai), cầu chì ≤ 40 lượt/đêm.

## Đang có
- Script đã có (máy nhà): `C:/Users/Administrator/Desktop/xuong/xuong-mau/` – `KHUNG/mau.py` (8 mẫu .xlsx), `KHUNG/kiem_cong_thuc.py` (bộ tính độc lập), `KHUNG/anh.py` (ảnh 1600×1200), `KHUNG/keo_mien_phi.py`. 21/10: 8 mẫu đã dựng trong HANG/ (0 lỗi công thức), CHƯA chạy Cửa 0/1, CHƯA nộp.

## Khi nào mở Claude (khung này)
1. Dựng script lần đầu. 2. Script lỗi 2 lần. 3. Hàng bị trả lại (đọc NGHIEM-THU.md) → sửa script/khuôn.
KHÔNG làm tay từng sản phẩm. KHÔNG đọc cả kho, cả hiến chương. Xong việc: commit + push, ghi 3 dòng (món · lịch · token) vào NHAT-KY.md, đóng phiên.

## Nhật ký
NHAT-KY.md (ngày · số món ra · qua cửa · nộp · bị trả · lỗi)
