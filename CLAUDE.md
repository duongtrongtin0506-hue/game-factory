# ③ GAME – bộ nhớ

Phạm vi: chỉ game. Không YouTube, không bot.
Thư mục dự án: `C:\Users\Administrator\Desktop\GAME\web` (khung chat có thể mở ở thư mục khác; mọi việc game làm ở đây).
Trả lời tiếng Việt, ngắn gọn, tự làm; chỉ hỏi khi cần tài khoản, mật khẩu, tiền. Đầu việc ghi "mức: nhẹ/nặng".

## CHẾ ĐỘ TỰ CHẠY

- Tự làm, không hỏi xin phép, không nhắc lại, không giảng giải, không đưa chủ lệnh để chạy.
- Lệnh viết kiểu PowerShell: nối bằng `;`, không dùng `&&`.
- Thiếu tài khoản / trang nền tảng (itch.io…): bỏ qua, ghi ⚪, không báo 🔴.
- Việc chỉ chủ làm được: gom vào `HUONG-DAN-CHU.md`, nhắc 1 lần/ngày trong Discord #game, không chờ chủ.
- Trả lời chủ tối đa 3 dòng.
- Vẫn phải hỏi: tài khoản, mật khẩu, tiền.

GIAI ĐOẠN HIỆN TẠI: 2 (chuẩn hóa)
VIỆC TIẾP THEO: Đo chuẩn giai đoạn 2 trong `tools/smoke_test.py`: thời gian tải < 5 giây, thêm cỡ máy tính (1280x720) bên cạnh điện thoại; ghi kết quả từng game vào `THEO-DOI.md`. Đạt cả 5 game thì gộp `chuan-hoa` vào `main` và chuyển sang giai đoạn 3.

## Danh sách game

| Tên | Thư mục | Số màn | Cổng đã nộp | Ngày nộp | Trạng thái duyệt |
|---|---|---|---|---|---|
| Tap Arcade | `web/tap-arcade` | 45 (Journey) | GameMonetize (bản 5 trò) · CrazyGames | 09/10 · 11/10 | chờ duyệt (xem lần cuối 09/10) · bị từ chối 11/10 |
| Boba Sort | `web/boba-sort` | 100 | CrazyGames | 11/10 | bị từ chối 11/10 |
| Car Jam Escape | `web/car-jam` | 100 (+40 dự trữ) | CrazyGames (bản 1) | 11/10 | bị từ chối 11/10; bản 2 chưa nộp, chờ chủ chơi thử |
| Tile Trio | `web/tile-trio` | 100 | CrazyGames | 11/10 | bị từ chối 11/10 |
| One Line Fill | `web/one-line` | 100 | chưa nộp | - | chưa có ảnh bìa, video |

GameDistribution: đăng ký tài khoản 09/10, chờ thư. itch.io: có khóa, chưa có trang game. Chi tiết: `THEO-DOI.md`.

Kho GitHub: game-factory (`duongtrongtin0506-hue/game-factory`, riêng tư, nhánh `main`; không dùng tài khoản iCloud `77nrw8z5hk-sys`) · Discord: Máy chủ của net24 #game · healthchecks: check "Game"

## Tiến độ theo giai đoạn

- 0 Dọn + GitHub: XONG (kho có mã, `.gitignore` chặn khóa, quét khóa sạch 12/10).
- 1 Kiểm kê: XONG, `THEO-DOI.md` đủ 5 game (kiểm thử mới ở cỡ điện thoại dọc + ngang, chưa có cỡ máy tính riêng).
- 2 Chuẩn hóa: ĐANG LÀM. Có: `levels/car-jam.json`; Boba Sort (12/10, nhánh `chuan-hoa`: `tools/bobasort.py`, `levels/boba-sort.json` giữ nguyên 100 màn cũ, 40 màn dự trữ, `run_daily` kiểm cả hai); Tile Trio (12/10, cùng nhánh: `tools/tiletrio.py`, `levels/tile-trio.json` giữ nguyên 100 màn cũ, 40 màn dự trữ; quy trình ngày chạy trọn trên máy đạt với cả 3 game). One Line Fill (12/10, cùng nhánh: `tools/oneline.py`, `levels/one-line.json` giữ 99 màn cũ, màn 27 trùng màn 26 nên thay bằng màn mới cùng cỡ, 40 màn dự trữ). Tap Arcade (12/10: 45 chặng Journey ở `levels/tap-arcade.json`, `tools/taparcade.py` chỉ kiểm định dạng vì là trò phản xạ, không có hàng dự trữ). Cả 5 game giờ đọc màn từ `levels/`. Lớp quảng cáo chung `web/ads.js` (12/10): một nguồn cho 4 cổng (gamemonetize, gamedistribution, crazygames, none), `tools/build.py` dán vào từng game; quảng cáo thưởng không bị giữ lại, midgame cách nhau ≥ 60 giây; `tools/test_ads.js` thử với SDK giả, chưa thử với SDK thật của cổng nào. Thiếu: đo tải < 5 giây, kiểm thử cỡ máy tính.
- 3 Máy tự thêm màn: làm trước một phần (Car Jam: bộ giải, hàng chờ, `daily.yml`, `weekly-selftest.yml`, Discord, healthchecks). Chưa có trang itch.io thì `daily` bỏ qua bước đăng, ghi ⚪ (sửa 12/10, chưa chạy thật trên Actions).
- 4 Đo 14 ngày: chưa bắt đầu, chưa game nào lên sóng.
- 5 Roblox: chưa làm, chưa có khóa.

## Chờ chủ (xem `HUONG-DAN-CHU.md`)

- Chơi thử Car Jam bản 2 → rồi mới tạo bài nộp CrazyGames mới (bài bị từ chối không tải bản mới được).
- Tạo trang itch.io `car-jam-escape`, nhắn "xong trang itch" → chạy lại `daily` → chủ tích "played in the browser" → đặt `itch` cho 4 game còn lại.
- Đăng nhập GameMonetize xem kết quả duyệt Tap Arcade.

## Sơ đồ

| Đường dẫn | Nội dung |
|---|---|
| `web/<game>/index.html` | Bản đã ghép màn (do `tools/build.py` tạo, không sửa tay): 5 game, mỗi game một tệp canvas (`pop-the-balloon` là bản thử, không đăng) |
| `web/<game>/index.src.html` (cả 5 game) | Nguồn game (sửa ở đây); `tools/build.py` ghép màn vào thành `index.html` |
| `levels/<game>.json` | Màn đang ở trong game (cả 5 game) |
| `content-queue/<game>.json` | Màn dự trữ đã qua bộ giải, luôn giữ ≥ 30 |
| `specs/<game>.json` | Thông số dùng chung web/Roblox; `specs/expiry.json` ghi ngày hết hạn từng khóa |
| `tools/carjam.py` | Bộ giải BFS, bộ sinh màn, hàng dự trữ (`verify`, `fill`, `take N`) |
| `tools/bobasort.py` | Bộ giải A* (số bước ít nhất), bản chép bộ giải trong game, bộ sinh màn, hàng dự trữ (cùng lệnh; `take N` phải chia hết cho 20) |
| `tools/tiletrio.py` | Bộ giải duyệt theo chiều sâu, bộ sinh màn theo hạt giống (bản chép `makeLevel` cũ của game), hàng dự trữ (cùng lệnh). Độ khó `hard` 0–100 = tỉ lệ thua của người chơi chỉ nhìn trước mắt; 60 màn cuối đang ở mức 30–100, trung bình ~65 (khó, cân nhắc khi nâng chất lượng) |
| `tools/oneline.py` | Bộ giải duyệt theo chiều sâu (không nhìn đường đi mẫu), bộ sinh màn theo hạt giống (bản chép `makeLevel` cũ), hàng dự trữ (cùng lệnh). `hard` 0–100 = tỉ lệ thua của người chơi luôn đi sang ô ít lối ra nhất; trùng màn xét theo hình bàn + ô xuất phát |
| `web/ads.js` | Lớp quảng cáo chung: `showAd('midgame'/'rewarded', done)`, `gameplay(on)`, `happy()`, biến `adPlaying`; game có thể khai `onPortalReady()` |
| `tools/build.py` | Ghép `/*LEVELS*/` + `/*ADS*/` rồi đóng gói `dist/<game>/<cổng>/` + zip (cổng: gamemonetize, crazygames, gamedistribution, none); mã game ở từng cổng lấy từ `specs/<game>.json` mục `portal_ids` |
| `tools/test_ads.js` | Thử `web/ads.js` với SDK giả của từng cổng (`node tools/test_ads.js`); `run_daily` chạy trước kiểm thử trình duyệt |
| `tools/smoke_test.py` | Playwright cỡ điện thoại dọc + ngang, bắt lỗi console, đối chiếu bộ giải trong game |
| `tools/run_daily.py` | Trọn quy trình ngày; ghi `TRANG-THAI.md`, `metrics/history.json`; `tools/notify.py` báo Discord + healthchecks |
| `.github/workflows/daily.yml` | 06:00 giờ VN mỗi ngày |
| `.github/workflows/weekly-selftest.yml` | Chủ nhật 20:00 giờ VN, không đăng, gửi báo cáo tuần; cũng chạy khi sửa `tools/` hoặc workflow |
| `THEO-DOI.md` / `NGHIEN-CUU.md` / `HUONG-DAN-CHU.md` | Trạng thái nộp duyệt / nghiên cứu có nguồn / việc chủ phải bấm |

Chạy thử trên máy: launch config `game-web`, cổng 8931, đường dẫn `/web/<game>/`; dùng `?level=N`, `?play=`, `?demo=`, `?selftest=1`.
`git` ở `C:\Program Files\Git\cmd` (thêm vào PATH từng lệnh). Khóa đã có ở GitHub Secrets: `DISCORD_WEBHOOK`, `HC_PING`, `BUTLER_API_KEY`, `ITCH_USER`. Chưa có: Roblox.

## Quy tắc

- Mỗi lượt "làm tiếp": đọc tệp này → làm đúng VIỆC TIẾP THEO → cập nhật VIỆC TIẾP THEO → commit + push. Không nhảy giai đoạn; đổi hướng thì hỏi chủ, ghi Nhật ký quyết định.
- Mở phiên 3 dòng: giai đoạn mấy, vừa làm gì, làm tiếp gì / cần chủ gì.
- Không làm game thứ 6 khi chưa có số liệu 14 ngày của 5 game hiện có.
- Không sửa hay nộp lại bản đang chờ duyệt; sửa ở nhánh riêng.
- Mọi màn mới phải được bộ giải xác nhận giải được và đo độ khó; khoảng 5 màn chèn 1 màn dễ.
- Không cờ bạc, không hộp quà may rủi, không link ra ngoài, không thu dữ liệu cá nhân.
- Không ghi mật khẩu hay khóa vào tệp. Khóa ở GitHub Secrets hoặc `.env` (mẫu: `.env.example`).
- Discord chỉ gửi #game; không gửi #youtube, #trade, #dang-tiktok.
- Phút GitHub Actions miễn phí (2.000/tháng) dùng chung cho mọi kho riêng tư của tài khoản.

## Nhật ký quyết định

- 2026-10-09 – Bỏ Unity/AdMob, chuyển sang game HTML5 nộp cổng web – tài khoản AdMob bị khóa, chi phí 0.
- 2026-10-10 – Mỗi lần làm kỹ một game nhiều màn, không reskin hàng loạt – reskin là lý do bị khóa trước đây.
- 2026-10-11 – Không nộp lại bản cũ lên CrazyGames; làm Car Jam bản 2 trước – cả 4 game bị chê chất lượng chung.
- 2026-10-11 – Màn mới sinh bằng thuật toán + bộ giải, không dùng Gemini – không cần khóa, không hết lượt, chắc chắn giải được.
- 2026-10-12 – Dọn giai đoạn 0 chỉ áp dụng cho thư mục game; không xóa CLAUDE.md và không dời tệp trong `Videos\noi-dung-video` – thư mục đó là dự án khác đang chạy theo lịch, dời tệp sẽ làm hỏng nó.
