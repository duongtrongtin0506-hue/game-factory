# ③ GAME – bộ nhớ

**Kế hoạch hiện hành = KE-HOACH-V3.md. Bỏ mọi 'chờ X ngày' và mọi chia giai đoạn cũ.**
**Ngôn ngữ thiết kế xuyên suốt = THIET-KE.md (khoảng trắng – nhịp điệu – 1 điểm nhấn). Mọi giao diện mới hay sửa lại đều theo tệp đó, không hỏi lại.**

Phạm vi: chỉ game. Không YouTube, không bot.
Thư mục dự án: `C:\Users\Administrator\Desktop\GAME\web` (khung chat có thể mở ở thư mục khác; mọi việc game làm ở đây).
Trả lời tiếng Việt, ngắn gọn, tự làm; chỉ hỏi khi cần tài khoản, mật khẩu, tiền. Đầu việc ghi "mức: nhẹ/nặng".

## CHẾ ĐỘ TỰ CHẠY

- Tự làm, không hỏi xin phép, không nhắc lại, không giảng giải, không đưa chủ lệnh để chạy.
- **Làm liên tục (chủ dặn 13/10): mỗi lượt làm hết việc này sang việc kế trong `VIEC.md`, KHÔNG dừng để chờ chủ gõ "làm tiếp". Chỉ dừng khi: (a) bí thật sự và cần chủ điền tài khoản, mật khẩu, khóa hoặc quyết định tiền; (b) mọi việc còn lại đều chờ chủ (ghi ở đầu `HUONG-DAN-CHU.md`). Việc bị chặn thì bỏ qua, làm việc khác trước, không đứng chờ.**
- Lệnh viết kiểu PowerShell: nối bằng `;`, không dùng `&&`.
- Thiếu tài khoản / trang nền tảng (itch.io…): bỏ qua, ghi ⚪, không báo 🔴.
- Việc chỉ chủ làm được: gom vào `HUONG-DAN-CHU.md`, nhắc 1 lần/ngày trong Discord #game, không chờ chủ.
- Trả lời chủ 1 dòng.
- Vẫn phải hỏi: tài khoản, mật khẩu, tiền.

VIỆC TIẾP THEO: làm `VIEC.md` từ trên xuống (ưu tiên theo mục 4 của kế hoạch). Mỗi lượt: `git pull` → đọc `TRANG-THAI.md` (🔴 thì sửa trước) → làm việc đầu danh sách chưa xong → tích xong, commit + push sau mỗi việc → cuối lượt thêm 1 dòng vào cuối `TRANG-THAI.md` dưới `## Nhật ký lượt` dạng `- DD/MM HH:MM 🎮 Xong … · Gói chờ nộp N · Việc còn N` (giữ 30 dòng mới nhất; `bao-discord.yml` gửi dòng cuối vào Discord #game). Routine đám mây (Sonnet, 08:00/14:00/20:00 giờ VN) bỏ qua việc có nhãn `[nặng]`; khung chat trên máy làm cả `[nặng]`.

Tệp V3: `KE-HOACH-V3.md` (kế hoạch nguyên văn) · `HIEN-TRANG.md` (cái đã có) · `VIEC.md` (hàng việc) · `CONG.md` (cổng) · `XU-HUONG.md` + `Y-TUONG.md` (thứ hai) · `NHAT-KY-CAI-TIEN.md` (chủ nhật) · `CHI-SO.md` · `VAN-HANH.md` · `ASSETS.md` · `THU-NGHIEM.md` · `phat-hanh/<cổng>/<game>/` (gói nộp).

Trên đám mây (routine, Linux): dùng bash; `pip install -r tools/requirements.txt; python -m playwright install --with-deps chromium` trước khi chạy `tools/run_daily.py --no-publish` hay `tools/smoke_test.py`; không có `.env` và không có trình duyệt đăng nhập cổng nào, nên việc nộp cổng/chép số ghi vào `HUONG-DAN-CHU.md`; không tự gọi Discord (đã có `bao-discord.yml`).

## Danh sách game

| Tên | Thư mục | Số màn | Cổng đã nộp | Ngày nộp | Trạng thái duyệt |
|---|---|---|---|---|---|
| Tap Arcade | `web/tap-arcade` | 45 (Journey) | GameMonetize (bản 5 trò) · CrazyGames | 09/10 · 11/10 | chờ duyệt (xem lần cuối 09/10) · bị từ chối 11/10 |
| Boba Sort | `web/boba-sort` | 120 | CrazyGames | 11/10 | bị từ chối 11/10 |
| Car Jam Escape | `web/car-jam` | 120 (+40 dự trữ) | CrazyGames (bản 1) | 11/10 | bị từ chối 11/10; bản giao diện mới có gói, chờ chủ nộp |
| Tile Trio | `web/tile-trio` | 120 | CrazyGames | 11/10 | bị từ chối 11/10 |
| One Line Fill | `web/one-line` | 120 | chưa nộp | - | có gói + ảnh bìa, video; chờ chủ nộp |
| Merge Harvest | `web/merge-harvest` | vô tận (gộp + idle, 10 bậc) | chưa nộp | - | bản thử 13/10 đạt, đang làm game đủ; mẫu tham chiếu ngôn ngữ thiết kế |

GameDistribution: đăng ký tài khoản 09/10, chờ thư. itch.io: có khóa, chưa có trang game. Chi tiết: `THEO-DOI.md`.

Kho GitHub: game-factory (`duongtrongtin0506-hue/game-factory`, riêng tư, nhánh `main`; không dùng tài khoản iCloud `77nrw8z5hk-sys`) · Discord: Máy chủ của net24 #game · healthchecks: check "Game"

## Đã có (chi tiết: `HIEN-TRANG.md`)

- Cả 5 game đọc màn từ `levels/`; 4 game xếp hình có bộ giải + hàng dự trữ ≥ 30; Tap Arcade chỉ kiểm định dạng.
- `web/ads.js`: một lớp quảng cáo cho các cổng (gamemonetize, gamedistribution, crazygames, none); `tools/build.py` dán vào từng game; quảng cáo thưởng không bị giữ lại, midgame cách nhau ≥ 60 giây; `tools/test_ads.js` thử với SDK giả, chưa thử với SDK thật.
- `daily` 06:00 đạt ✅ 3 ngày liền trên Actions (11–13/10). Mỗi thứ hai `run_daily` chuyển 20 màn/game vào Car Jam, Boba Sort, Tile Trio, One Line Fill (hỏng kiểm thử thì trả lại). Car Jam (13/10): 7 cảnh thế giới, hết cảnh thì lặp lại; 120 màn; đã vào `TAKE_GAMES` nên thứ hai cũng tự thêm 20 màn.
- `run_daily` giữ nguyên phần `## Nhật ký lượt` ở cuối `TRANG-THAI.md`.
- 13/10: cả 5 game cũ đã đổi giao diện theo `THIET-KE.md` (Car Jam, Boba Sort, Tile Trio nền giấy; One Line Fill, Tap Arcade nền đêm); ảnh bìa mới ở `assets-goc/<game>/`; `tools/build.py` ghi 15 gói `phat-hanh/<cổng>/<game>/` (zip + `mo-ta.md`, lấy mô tả từ mục `store` trong specs). Sửa giao diện game: sửa `index.src.html` rồi `python tools/build.py`; soát hình bằng `python tools/chup.py <game> "?" "?level=3"` (ảnh ra `_build/anh/`).
- Chưa có: game nào lên sóng, số liệu, bản Roblox, khóa Roblox.

## Chờ chủ (xem đầu `HUONG-DAN-CHU.md`)

- Cài Claude GitHub App cho kho game-factory (routine đám mây chưa tạo được: lỗi repo_access_denied; tạo lại bằng skill schedule, cron `0 1,7,13 * * *`, Sonnet).
- Nộp Car Jam + One Line Fill lên CrazyGames; lấy GameId GameMonetize cho 4 game; xem kết quả duyệt Tap Arcade; thư kích hoạt GameDistribution.

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
| `THIET-KE.md`, `thiet-ke/` | Ngôn ngữ thiết kế (token màu, bo góc, font, luật) và bản gốc chủ gửi |
| `tools/build.py` | Ghép `/*LEVELS*/` + `/*ADS*/` rồi đóng gói `dist/<game>/<cổng>/` + zip (cổng: gamemonetize, crazygames, gamedistribution, none); mã game ở từng cổng lấy từ `specs/<game>.json` mục `portal_ids` |
| `tools/quay.py` | `python tools/quay.py <game>`: ảnh bìa mọi cỡ + 2 video từ `?demo=` của game → `assets-goc/<game>/` (ảnh có trong git, video không) và `dist/<game>/assets` |
| `tools/test_ads.js` | Thử `web/ads.js` với SDK giả của từng cổng (`node tools/test_ads.js`); `run_daily` chạy trước kiểm thử trình duyệt |
| `tools/smoke_test.py` | Playwright cỡ điện thoại dọc + ngang + máy tính, bắt lỗi console, đo thời gian tải trên máy yếu mạng chậm (giới hạn 5 giây), gọi `?selftest=1` của từng game |
| `tools/run_daily.py` | Trọn quy trình ngày; ghi `TRANG-THAI.md`, `metrics/history.json`; `tools/notify.py` báo Discord + healthchecks |
| `.github/workflows/daily.yml` | 06:00 giờ VN mỗi ngày |
| `.github/workflows/weekly-selftest.yml` | Chủ nhật 20:00 giờ VN, không đăng, gửi báo cáo tuần; cũng chạy khi sửa `tools/` hoặc workflow |
| `THEO-DOI.md` / `NGHIEN-CUU.md` / `HUONG-DAN-CHU.md` | Trạng thái nộp duyệt / nghiên cứu có nguồn / việc chủ phải bấm |

Chạy thử trên máy: launch config `game-web` (`.claude/launch.json`), cổng 8931, đường dẫn `/web/<game>/`; dùng `?level=N`, `?play=`, `?demo=`, `?selftest=1`.
`git` ở `C:\Program Files\Git\cmd` (thêm vào PATH từng lệnh). Khóa đã có ở GitHub Secrets: `DISCORD_WEBHOOK`, `HC_PING`, `BUTLER_API_KEY`, `ITCH_USER`. Chưa có: Roblox.

## Quy tắc

- Mỗi lượt "làm tiếp": đọc tệp này → làm `VIEC.md` theo thứ tự ưu tiên → commit + push sau mỗi việc. Đổi hướng lớn (bỏ cổng, lên tầng 3, tiêu tiền) thì đề xuất kèm số liệu cho chủ duyệt, ghi Nhật ký quyết định.
- Báo chủ 1 dòng: vừa xong gì, gói chờ nộp, việc còn.
- Game mới: mỗi game một cơ chế khác, lấy từ `Y-TUONG.md`, qua bản thử 1 ngày trước khi làm đủ; chỉ học cơ chế, không chép tên, hình, nhân vật, nhạc.
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
- 2026-10-12 – Màn mới vào game mỗi thứ hai, 20 màn/game (không phải mỗi ngày); cổng web vẫn gom theo tháng – trang chọn màn chia 20 ô nên phải thêm trọn trang; 20 màn/ngày thì tệp game phình nhanh mà chưa có người chơi.
- 2026-10-13 – Chủ dặn: khung chat chủ động làm liên tục hàng việc, không dừng chờ câu "làm tiếp"; chỉ hỏi khi cần tài khoản, mật khẩu, tiền – chủ không muốn phải nhắc.
- 2026-10-13 – Chủ chọn ngôn ngữ thiết kế xuyên suốt (`THIET-KE.md`): nền giấy ấm/đêm, card trắng bo 16, nút pill, 1 màu nhấn, headline serif mảnh – game cũ bị chê chất lượng chung; game mới theo từ đầu, game cũ đổi dần.
- 2026-10-13 – Chuyển sang KE-HOACH-V3: bỏ chia giai đoạn và các mốc chờ ngày, làm theo hàng việc VIEC.md; cho làm game mới song song (mục tiêu 2 game/tuần) và nộp nhiều cổng; routine đám mây 3 lượt/ngày – chủ dự án yêu cầu, để không phụ thuộc 1 cổng hay 1 game.
