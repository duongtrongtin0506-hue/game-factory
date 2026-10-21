# Xưởng Tool – nhà máy Net24 (Agent 3)

Giao hàng cho **tools.snoutsmith.com**. Luật: `net24-he-thong/13-Ban-hang-so/KHUON-NHA-MAY.md`.

| Thư mục / tệp | Việc |
|---|---|
| `NGHIEN-CUU/` | Kết quả nghiên cứu thứ Hai (`HOC-TOP-*.md`) và R&D từng sản phẩm |
| `KHUNG/` | Khung đã đạt + `san_xuat.py` (1 món/ngày) + `keo_mien_phi.py` (hàng miễn phí hợp pháp) |
| `KIEM/` | Bộ kiểm: `kiem_tat_ca.py` chạy Cửa 0 + Cửa 1 trên mọi món trong `HANG/` |
| `HANG/<YYYYMMDD>-<ten>/` | Từng sản phẩm = đúng hồ sơ nộp (BAN-GIAO.md, LEADER.md, LICENSES.md, gói bán, CUA0.json, CUA1.json) |
| `tools/chung/` | Công cụ chung chép vào từng kho, ghim phiên bản (`VERSION`): ai, bao, giay_phep, nghien_cuu, cua0, cua1, nop |
| `.github/workflows/` | `nghien-cuu` (T2), `san-xuat` (ngày), `keo-mien-phi` (ngày, tới 31/10), `kiem` (mỗi push), `nop` (sau kiem xanh) |

Secrets: `N24_AI_KEY` (khóa AI chung) hoặc `GEMINI_API_KEY`, `DISCORD_WEBHOOK`, `NET24_PUSH_TOKEN` (đẩy hồ sơ sang net24-he-thong). Thiếu khóa AI thì nghiên cứu vẫn lấy số liệu thật, Cửa 1 đóng (không nộp hàng chưa chấm).
