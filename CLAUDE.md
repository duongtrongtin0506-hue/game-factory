# game-factory

Kho GitHub riêng tư: `duongtrongtin0506-hue/game-factory` (nhánh `main`). Không dùng tài khoản iCloud `77nrw8z5hk-sys`.
Thư mục trên máy: `C:\Users\Administrator\Desktop\GAME\web`.
Trả lời tiếng Việt, ngắn gọn, tự làm; chỉ hỏi khi cần tài khoản, mật khẩu, tiền. Đầu việc ghi "mức: nhẹ/nặng".

## Mục tiêu

Game HTML5 nhỏ nhiều màn, đăng lên cổng game chia doanh thu quảng cáo; sau đó một bản Roblox của game có số liệu tốt nhất.
Mục tiêu gần: đồng doanh thu đầu tiên. Chủ dự án không trả trước cho bên thứ ba nào.

## Sơ đồ

| Đường dẫn | Nội dung |
|---|---|
| `web/<game>/index.html` | 5 game, mỗi game một tệp canvas: tap-arcade, boba-sort, car-jam, tile-trio, one-line (`pop-the-balloon` là bản thử, không đăng) |
| `web/car-jam/index.src.html` | Nguồn Car Jam; `tools/build.py` ghép màn vào thành `index.html` |
| `levels/car-jam.json` | Màn Car Jam đang ở trong game (bàn cờ + số bước ít nhất) |
| `content-queue/car-jam.json` | Màn dự trữ đã qua bộ giải, luôn giữ ≥ 30 |
| `specs/<game>.json` | Thông số dùng chung web/Roblox; `specs/expiry.json` ghi ngày hết hạn từng khóa |
| `tools/carjam.py` | Bộ giải BFS, bộ sinh màn, hàng dự trữ (`verify`, `fill`, `take N`) |
| `tools/build.py` | Đóng gói `dist/<game>/<cổng>/` + zip (cổng: gamemonetize, crazygames, none) |
| `tools/smoke_test.py` | Playwright cỡ điện thoại dọc + ngang, bắt lỗi console, đối chiếu bộ giải trong game |
| `tools/run_daily.py` | Trọn quy trình ngày; ghi `TRANG-THAI.md`, `metrics/history.json`; `tools/notify.py` báo Discord + healthchecks |
| `.github/workflows/daily.yml` | 06:00 giờ VN mỗi ngày |
| `.github/workflows/weekly-selftest.yml` | Chủ nhật 20:00 giờ VN, không đăng, gửi báo cáo tuần; cũng chạy khi sửa `tools/` hoặc workflow |
| `THEO-DOI.md` / `NGHIEN-CUU.md` / `HUONG-DAN-CHU.md` | Trạng thái nộp duyệt / nghiên cứu có nguồn / việc chủ phải bấm |

Quảng cáo: mỗi game tự chứa lớp quảng cáo, chọn cổng bằng hằng `PORTAL`; `tools/build.py` đổi hằng này. Chưa tách thành `ads.js` chung.
Chạy thử trên máy: phục vụ thư mục qua `http://127.0.0.1` (launch config `game-web`, cổng 8931, đường dẫn `/web/<game>/`) để dùng `?level=N`, `?play=`, `?demo=`, `?selftest=1`.
Màn mới sinh bằng thuật toán + bộ giải, không cần Gemini nên không cần khóa và không hết lượt.

## Quy tắc

- Không làm game thứ 6 khi chưa có số liệu 14 ngày của 5 game hiện có.
- Không sửa hay nộp lại bản đang chờ duyệt; sửa ở nhánh riêng.
- Mọi màn mới phải được bộ giải xác nhận giải được và đo số bước; khoảng 5 màn chèn 1 màn dễ.
- Không cờ bạc, không hộp quà may rủi, không link ra ngoài, không thu dữ liệu cá nhân.
- Không ghi mật khẩu hay khóa vào tệp. Khóa ở GitHub Secrets hoặc `.env` (mẫu: `.env.example`).
- Phút GitHub Actions miễn phí (2.000/tháng) dùng chung cho mọi kho riêng tư của tài khoản.

## Trạng thái (2026-10-11)

- Chưa game nào lên sóng. CrazyGames từ chối cả 4 game vì chất lượng (2026-10-11). Tap Arcade chờ duyệt ở GameMonetize từ 2026-10-09, chưa xem lại. GameDistribution chờ thư.
- Car Jam Escape bản 2 đã gộp vào `main`, chưa nộp lại: chờ chủ chơi thử.
- Quy trình ngày chạy đạt trên máy (5/5 game qua kiểm thử, 100 màn + 40 dự trữ). Trên GitHub Actions: xem `TRANG-THAI.md`.
- Chưa có khóa nào: Discord, healthchecks, itch.io, Roblox đều đang bị bỏ qua.

## Việc dở

1. Chờ chủ: xem `HUONG-DAN-CHU.md` (chơi thử Car Jam 2, đăng nhập GameMonetize, webhook #game, healthchecks, itch.io).
2. Sau khi chủ chơi thử: tạo bài nộp CrazyGames mới cho Car Jam 2 (bài cũ không tải bản mới được).
3. Bộ giải trong `tools/` cho Boba Sort, Tile Trio, One Line Fill (màn của ba game này đang sinh trong game theo hạt giống) và tách màn ra `levels/`.
4. Car Jam: `take 20` mới chỉ thêm màn; game cần cảnh cho thế giới thứ 6 và sửa chữ "ALL 100 LEVELS" trước bản cập nhật tháng. Chỉ nộp khi bản hiện tại đã được duyệt.
5. Đường itch.io trong `run_daily.py` chưa chạy thật (chưa có tài khoản); workflow chưa cài butler.
6. `roblox/` (Luau + Rojo) chưa làm: chờ số liệu 14 ngày để chọn game.
7. Tách lớp quảng cáo thành `web/ads.js` chung; thêm SDK GameDistribution khi tài khoản được duyệt.
8. Nghiên cứu còn thiếu: xem các mục "chưa xác minh" trong `NGHIEN-CUU.md`.
9. Đo lượt chơi, thời gian chơi, màn bị bỏ nhiều nhất, doanh thu: chưa có nguồn số liệu cho đến khi có game lên sóng.
