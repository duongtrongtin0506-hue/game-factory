# Sổ tay vận hành xưởng game (đủ để người khác tiếp quản)

Cập nhật 13/10/2026. Đọc kèm: `CLAUDE.md` (bộ nhớ + quy tắc), `KE-HOACH-V3.md` (kế hoạch), `VIEC.md` (hàng việc), `HUONG-DAN-CHU.md` (việc phải bấm tay).

## 1. Xưởng gồm gì

- Kho GitHub riêng tư `duongtrongtin0506-hue/game-factory`, nhánh `main`. Mọi mã, màn chơi, tài liệu ở đây, định dạng mở (HTML, JSON, Markdown, Python). Không có máy chủ, không có cơ sở dữ liệu.
- 6 game HTML5, mỗi game 1 tệp canvas không phụ thuộc thư viện: nguồn `web/<game>/index.src.html`, màn `levels/<game>.json`, thông số + mô tả cửa hàng `specs/<game>.json`.
- Dây chuyền: `tools/<game>.py` (bộ giải, sinh màn, hàng dự trữ) → `tools/build.py` (ghép màn + lớp quảng cáo `web/ads.js`, ra `dist/` và gói nộp `phat-hanh/`) → `tools/smoke_test.py` (Playwright) → `tools/run_daily.py` (trọn quy trình, ghi `TRANG-THAI.md`, báo Discord).
- Hình: tất cả vẽ bằng mã; ảnh bìa và video sinh bằng `tools/quay.py` (xem `ASSETS.md`).

## 2. Chạy trên máy mới (Windows, macOS, Linux)

1. Cài Python 3.13, Node (chỉ để chạy `tools/test_ads.js`), git; muốn quay video thì thêm ffmpeg.
2. `git clone` kho; `pip install -r tools/requirements.txt`; `python -m playwright install chromium`.
3. Kiểm tra: `python tools/run_daily.py --no-publish` phải in `✅ đạt`.
4. Xem game: `python -m http.server 8931` ở gốc kho rồi mở `http://localhost:8931/web/<game>/` (tham số thử: `?level=N`, `?selftest=1`, `?demo=cover&w=&h=`).
5. Sửa game: sửa `index.src.html` → `python tools/build.py` → `python tools/smoke_test.py` → `python tools/chup.py <game> "?" "?level=3"` để soát hình → commit.

## 3. Lịch tự động

| Việc | Ở đâu | Khi nào (giờ VN) | Hỏng thì |
|---|---|---|---|
| Kiểm màn, bổ sung dự trữ, build, kiểm trình duyệt, đẩy itch.io, ghi trạng thái | `.github/workflows/daily.yml` | 06:00 mỗi ngày | Discord #game báo 🔴 kèm bước lỗi và cách sửa (`FIX` trong `tools/run_daily.py`); healthchecks báo nếu không chạy |
| Thêm 20 màn/game từ hàng dự trữ | trong `daily`, thứ hai | thứ hai | kiểm thử hỏng thì tự trả lại, hôm sau làm bù |
| Chạy thử không đăng + báo cáo tuần | `weekly-selftest.yml` | chủ nhật 20:00, và mỗi lần sửa `tools/` | như trên |
| Gửi dòng cuối `TRANG-THAI.md` vào Discord | `bao-discord.yml` | mỗi lần `TRANG-THAI.md` đổi trên `main` | xem tab Actions |
| Làm hàng việc `VIEC.md` | routine Claude trên đám mây (Sonnet) | 08:00, 14:00, 20:00 | CHƯA CHẠY: chờ cài Claude GitHub App cho kho (đầu `HUONG-DAN-CHU.md`) |
| Việc `[nặng]`, việc cần trình duyệt | khung chat Claude trên máy 2 | khi chủ mở | - |

## 4. Khóa và tài khoản (không ghi giá trị vào tệp nào)

| Tên | Dùng cho | Nằm ở | Hết hạn |
|---|---|---|---|
| `DISCORD_WEBHOOK` | báo #game | GitHub Secrets | không |
| `HC_PING` | healthchecks.io, check "Game" | GitHub Secrets | không |
| `BUTLER_API_KEY`, `ITCH_USER` | đẩy itch.io | GitHub Secrets | không |
| `ROBLOX_API_KEY` | đăng place Roblox | CHƯA CÓ | - |
| Tài khoản cổng (CrazyGames, GameMonetize, GameDistribution, itch.io) | nộp game, xem số | chủ dự án đăng nhập trong Chrome máy 2 | - |

Ngày hết hạn ghi ở `specs/expiry.json`; `run_daily` cảnh báo trước 14 ngày. Chạy trên máy cần khóa thì tạo `.env` theo `.env.example` (đã nằm trong `.gitignore`).

## 5. Phương án B

| Thành phần | Nếu mất | Làm gì |
|---|---|---|
| Một cổng (khóa tài khoản, đổi chính sách) | mất nguồn thu ở cổng đó | game đã đóng gói cho cổng khác trong `phat-hanh/`; thêm cổng mới = thêm 1 nhánh trong `web/ads.js` + 1 dòng `RELEASE` trong `tools/build.py` (xem `CONG.md`) |
| GitHub (kho hoặc Actions) | mất lịch tự động | kho là git thường: đẩy sang GitLab/Codeberg; `tools/run_daily.py` chạy được bằng cron hoặc Task Scheduler trên máy bất kỳ; nên giữ thêm 1 bản sao kho trên máy 2 (`git pull` hằng tuần) |
| Phút Actions miễn phí (2.000/tháng, dùng chung) | `daily` không chạy | mỗi lần chạy ~3–5 phút; hết phút thì chạy `run_daily.py` trên máy 2 |
| Claude (routine, khung chat) | không ai làm `VIEC.md` | xưởng vẫn tự kiểm và tự thêm màn bằng Actions; việc mới cần người hoặc công cụ khác đọc `CLAUDE.md` + `VIEC.md` |
| Discord webhook | không có báo cáo | trạng thái vẫn ở `TRANG-THAI.md`; tạo webhook mới, đổi secret |
| Máy 2 | mất chỗ nộp cổng bằng trình duyệt | nộp từ máy bất kỳ: gói ở `phat-hanh/`, ảnh ở `assets-goc/` (video phải quay lại bằng `tools/quay.py`, cần ffmpeg) |
| Khóa AI vẽ hình | không ảnh hưởng | hiện không dùng AI vẽ; mọi hình vẽ bằng mã |

## 6. Chuyển nhượng / cấp phép trong 48 giờ

1. Chuyển quyền kho GitHub (Settings → Transfer) hoặc gửi bản `git bundle`.
2. Giao tài khoản cổng theo điều khoản từng cổng, hoặc người nhận tự nộp lại từ `phat-hanh/`.
3. Tài liệu kèm: tệp này, `HIEN-TRANG.md`, `THEO-DOI.md` (số liệu), `CHI-SO.md` (doanh thu, chi phí), `ASSETS.md` (giấy phép), `CONG.md`.
4. Người nhận thay các secret ở mục 4; không có bí mật nào nằm trong mã.

## 7. Điểm hỏng đơn lẻ đang có

- Chỉ chủ dự án nộp được lên cổng (không cổng nào đang dùng có API tải bản).
- Chưa có số liệu người chơi thật: mọi đánh giá chất lượng là tự đo bằng bot và Playwright.
- `web/ads.js` mới thử với SDK giả (trừ GameMonetize đã qua Verify bản cũ).
